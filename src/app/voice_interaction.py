"""Voice interaction logic for microphone and speech recognition."""

import logging
import json
import os
import threading
import time
from typing import Optional
from src.lib.microphone.interface import MicrophoneInterface
from src.lib.lcd.interface import LCDInterface
from src.app.display_content import DisplayContent

logger = logging.getLogger(__name__)

# Vosk model path (user should download and place model here)
DEFAULT_VOSK_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "vosk-model")


class VoiceInteraction:
    """Manages voice recognition and image display based on speech input."""

    IMAGE_UPDATE_PERIOD = 1.0 # seconds
    
    def __init__(
        self,
        microphone: MicrophoneInterface,
        lcd: Optional[LCDInterface] = None,
        image_embeddings=None,
        enable_images: bool = True,
        vosk_model_path: str = None
    ):
        """
        Initialize voice interaction.
        
        Parameters:
            microphone: MicrophoneInterface instance
            lcd: Optional LCDInterface instance for display
            image_embeddings: Optional ImageEmbeddings instance for vector matching
            enable_images: If True, enable image display (farm mode), else text only (mic mode)
            vosk_model_path: Path to Vosk model directory (defaults to DEFAULT_VOSK_MODEL_PATH)
        """
        self.microphone = microphone
        self.lcd = lcd
        self.image_embeddings = image_embeddings
        self.enable_images = enable_images
        self.vosk_model_path = vosk_model_path or DEFAULT_VOSK_MODEL_PATH
        self.last_image_update_time = None
        
        # Initialize Vosk recognizer
        self._recognizer = None
        self._rec = None
        self._initialized = False
        
        # Thread-safe access to recognized word and image
        self._lock = threading.Lock()
        self.current_word = None
        
        # Last recognized image (to keep displaying)
        self.last_image_key = None
        self.last_image_data = None
        
        # Background thread for continuous recognition
        self._recognition_thread = None
        self._stop_recognition = threading.Event()
        self._recognition_running = False
    
    def _initialize_vosk(self):
        """Initialize Vosk speech recognition."""
        if self._initialized:
            return
        
        try:
            import vosk
        except ImportError as e:
            raise RuntimeError(f"Vosk not available: {e}. Install with: pip install vosk")
        
        if not os.path.exists(self.vosk_model_path):
            raise RuntimeError(
                f"Vosk model not found at {self.vosk_model_path}. "
                "Please download a model from https://alphacephei.com/vosk/models"
            )
        
        try:
            self._recognizer = vosk.Model(self.vosk_model_path)
            # Vosk expects 16kHz, 16-bit, mono PCM audio
            self._rec = vosk.KaldiRecognizer(self._recognizer, 16000)  # 16kHz sample rate
            self._rec.SetWords(True)  # Enable word-level recognition
            self._rec.SetPartialWords(True)  # Enable partial word recognition
            self._initialized = True
            logger.info(f"Vosk model loaded from {self.vosk_model_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Vosk: {e}")
    
    def start_continuous_recognition(self) -> None:
        """
        Start continuous recognition in a background thread.
        This will continuously record and process audio, updating current_word in real-time.
        """
        if self._recognition_running:
            logger.warning("Recognition thread already running")
            return
        
        if not self._initialized:
            self._initialize_vosk()
        
        if not self.microphone.is_available():
            raise RuntimeError("Microphone not available")
        
        self._stop_recognition.clear()
        self._recognition_running = True
        self._recognition_thread = threading.Thread(
            target=self._recognition_loop,
            daemon=True,
            name="VoiceRecognition"
        )
        self._recognition_thread.start()
        logger.info("Started continuous voice recognition thread")
    
    def stop_continuous_recognition(self) -> None:
        """Stop the continuous recognition thread."""
        if not self._recognition_running:
            return
        
        self._stop_recognition.set()
        if self._recognition_thread:
            self._recognition_thread.join(timeout=2.0)
        self._recognition_running = False
        logger.info("Stopped continuous voice recognition thread")
    
    def _recognition_loop(self) -> None:
        """Background thread loop that continuously records and processes audio."""
        try:
            import pyaudio
            
            # Open a continuous audio stream
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,  # 16kHz for Vosk
                input=True,
                frames_per_buffer=4000  # 0.25 seconds at 16kHz
            )
            
            logger.debug("Audio stream opened for continuous recognition")
            
            while not self._stop_recognition.is_set():
                try:
                    # Read a small chunk of audio (0.25 seconds)
                    audio_data = stream.read(4000, exception_on_overflow=False)
                    
                    # Process with Vosk
                    if self._rec.AcceptWaveform(audio_data):
                        # Final result
                        result = json.loads(self._rec.Result())
                        text = result.get("text", "").strip()
                        if text:
                            words = text.split()
                            if words:
                                word = words[0].lower()
                                self._update_recognized_word(word)
                    else:
                        # Check for partial result
                        partial_result = json.loads(self._rec.PartialResult())
                        partial_text = partial_result.get("partial", "").strip()
                        if partial_text:
                            words = partial_text.split()
                            if words:
                                word = words[0].lower()
                                # Only update on partial if it's different and seems stable
                                with self._lock:
                                    if word != self.current_word and len(word) >= 2:
                                        self._update_recognized_word(word)
                
                except Exception as e:
                    logger.error(f"Error in recognition loop: {e}", exc_info=True)
                    time.sleep(0.1)  # Brief pause on error
            
            # Cleanup
            stream.stop_stream()
            stream.close()
            audio.terminate()
            logger.debug("Audio stream closed")
            
        except Exception as e:
            logger.error(f"Failed to start recognition loop: {e}", exc_info=True)
            self._recognition_running = False
    
    def _update_recognized_word(self, word: str) -> None:
        """Thread-safe update of recognized word and image."""
        with self._lock:
            # Only update if it's a different word
            if word == self.current_word:
                return
            
            self.current_word = word
            logger.info(f"✓ Recognized word: {word}")
            
    
    def recognize_word(self) -> Optional[str]:
        """
        Get the currently recognized word (thread-safe).
        
        Returns:
            str: Currently recognized word, or None if no word recognized
        """
        with self._lock:
            return self.current_word
    
    def find_closest_image(self, word: str) -> Optional[str]:
        """
        Find closest image using vector distance matching.
        
        Parameters:
            word: Recognized word to match
            
        Returns:
            str: Image key of closest match, or None if no match above threshold
        """
        if not self.image_embeddings:
            return None
        
        try:
            return self.image_embeddings.find_closest_image(word)
        except Exception as e:
            logger.error(f"Failed to find closest image: {e}")
            return None
    
    def generate_display_content(
        self,
        word: Optional[str] = None,
        show_image: bool = None
    ) -> DisplayContent:
        """
        Generate display content from recognized word.
        
        Parameters:
            word: Recognized word (if None, uses current_word)
            show_image: If True, display image; if False, display text only
                      (if None, uses self.enable_images)
        
        Returns:
            DisplayContent: Display content for LCD
        """
        if word is None:
            word = self.current_word
        
        if show_image is None:
            show_image = self.enable_images
        
        if not word:
            # No word recognized - show last image with listening indicator if available
            if self.enable_images and self.last_image_data:
                # Always show listening indicator when we have an image
                return DisplayContent(
                    mode="voice",
                    color=(255, 255, 255),
                    background_color=(0, 0, 0),
                    text=None,  # No text when no new word
                    image_data=self.last_image_data,
                    image_width=16,
                    image_height=16,
                    status_indicator="listening"  # Always listening
                )
            
            # No image to show - show listening text
            return DisplayContent(
                mode="voice",
                color=(128, 128, 128),  # Gray text
                background_color=(32, 32, 32),  # Dark background
                text="Listening..."
            )
        
        if show_image:
            # Find closest image
            image_key = self.find_closest_image(word)
            if image_key:
                # Get image data from pixel_art module
                try:
                    from src.app.pixel_art import get_pixel_art_image

                    time_delta = time.time() - self.last_image_update_time if self.last_image_update_time is not None else 0

                    if (self.last_image_key is None
                    or self.last_image_key != image_key 
                    or time_delta >= self.IMAGE_UPDATE_PERIOD):
                        image_data = get_pixel_art_image(image_key)
                        self.last_image_update_time = time.time()
                    else:
                        image_data = self.last_image_data


                    if image_data:
                        # Store for later display
                        self.last_image_data = image_data
                        self.last_image_key = image_key
                        
                        # Display word text below the image
                        return DisplayContent(
                            mode="voice",
                            color=(255, 255, 255),
                            background_color=(0, 0, 0),
                            text=word.upper(),  # Show recognized word below image
                            image_data=image_data,
                            image_width=16,
                            image_height=16,
                            status_indicator="listening"  # Always listening
                        )
                except Exception as e:
                    logger.warning(f"Failed to load image for {image_key}: {e}")
            
            # Fallback: show word text if image not found
            return DisplayContent(
                mode="voice",
                color=(255, 255, 255),
                background_color=(0, 0, 0),
                text=f"{word} (no image)"
            )
        else:
            # Text-only mode (mic mode)
            return DisplayContent(
                mode="voice",
                color=(255, 255, 255),
                background_color=(0, 0, 0),
                text=word.upper()
            )
    
    def update_display(self) -> None:
        """Update LCD display based on current voice recognition."""
        if not self.lcd:
            return
        
        try:
            # Recognize word
            word = self.recognize_word()
            
            if word:
                # Generate display content
                content = self.generate_display_content(word)
                
                # Update LCD display
                self.lcd.update_display(content)
                
                logger.info(f"Display updated: word={word}, mode={content.mode}")
        except Exception as e:
            logger.error(f"Failed to update display: {e}")
            # Gracefully handle errors - don't crash
