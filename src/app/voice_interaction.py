"""Voice interaction logic for microphone and speech recognition."""

import logging
import json
import os
from typing import Optional
from src.lib.microphone.interface import MicrophoneInterface
from src.lib.lcd.interface import LCDInterface
from src.app.display_content import DisplayContent

logger = logging.getLogger(__name__)

# Vosk model path (user should download and place model here)
DEFAULT_VOSK_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "vosk-model")


class VoiceInteraction:
    """Manages voice recognition and image display based on speech input."""
    
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
        
        # Initialize Vosk recognizer
        self._recognizer = None
        self._rec = None
        self._initialized = False
        
        # Current recognized word
        self.current_word = None
        
        # Last recognized image (to keep displaying)
        self.last_image_key = None
        self.last_image_data = None
        
        # Status tracking
        self.status = "listening"  # "listening", "processing", "recognized"
    
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
    
    def recognize_word(self) -> Optional[str]:
        """
        Recognize a word from microphone input.
        
        Returns:
            str: Recognized word, or None if no speech detected
            
        Raises:
            RuntimeError: If Vosk is not initialized
            HardwareError: If microphone fails
        """
        if not self._initialized:
            self._initialize_vosk()
        
        try:
            # Set status to listening
            self.status = "listening"
            
            # Record audio (2 second chunks for better recognition)
            audio_data = self.microphone.record_audio(2.0)
            expected_size = 16000 * 2 * 2  # 16kHz * 2 seconds * 2 bytes per sample
            logger.debug(f"Recorded {len(audio_data)} bytes of audio (expected ~{expected_size})")
            
            if len(audio_data) < expected_size * 0.5:
                logger.warning(f"Audio data seems too short: {len(audio_data)} bytes")
                self.status = "listening"
                return None
            
            # Set status to processing
            self.status = "processing"
            logger.debug("Processing audio with Vosk...")
            
            # Process with Vosk
            if self._rec.AcceptWaveform(audio_data):
                # Final result
                result = json.loads(self._rec.Result())
                text = result.get("text", "").strip()
                logger.info(f"Vosk final result: '{text}'")
                if text:
                    # Extract first word
                    words = text.split()
                    if words:
                        word = words[0].lower()
                        self.current_word = word
                        self.status = "recognized"
                        logger.info(f"✓ Recognized word: {word}")
                        # Update last image when we recognize a new word
                        if self.enable_images:
                            image_key = self.find_closest_image(word)
                            if image_key:
                                try:
                                    from src.app.pixel_art import get_pixel_art_image
                                    self.last_image_data = get_pixel_art_image(image_key)
                                    self.last_image_key = image_key
                                except Exception as e:
                                    logger.warning(f"Failed to load image for {image_key}: {e}")
                        return word
            else:
                # Partial result
                result = json.loads(self._rec.PartialResult())
                text = result.get("partial", "").strip()
                if text:
                    logger.info(f"Vosk partial result: '{text}'")
                    words = text.split()
                    if words:
                        word = words[0].lower()
                        self.current_word = word
                        self.status = "recognized"
                        logger.info(f"Partial recognition: {word}")
                        # Update last image when we recognize a new word
                        if self.enable_images:
                            image_key = self.find_closest_image(word)
                            if image_key:
                                try:
                                    from src.app.pixel_art import get_pixel_art_image
                                    self.last_image_data = get_pixel_art_image(image_key)
                                    self.last_image_key = image_key
                                except Exception as e:
                                    logger.warning(f"Failed to load image for {image_key}: {e}")
                        return word
            
            # No words recognized
            self.current_word = None
            self.status = "listening"
            logger.debug("No speech detected in audio chunk")
            return None
            
        except Exception as e:
            logger.error(f"Failed to recognize word: {e}", exc_info=True)
            self.status = "listening"
            return None
    
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
            # No word recognized - show last image with status indicator if available
            if self.enable_images and self.last_image_data:
                # Determine status indicator
                status_indicator = None
                display_text = None
                if hasattr(self, 'status'):
                    if self.status == "processing":
                        status_indicator = "thinking"  # Orange/yellow indicator
                        display_text = "Thinking..."
                    else:
                        status_indicator = "listening"  # Gray indicator
                        display_text = "Listening..."
                
                return DisplayContent(
                    mode="voice",
                    color=(255, 255, 255),
                    background_color=(0, 0, 0),
                    text=display_text,  # Show status text below image
                    image_data=self.last_image_data,
                    image_width=16,
                    image_height=16,
                    status_indicator=status_indicator
                )
            
            # No image to show - show status text
            status_text = "Listening..."
            status_color = (128, 128, 128)  # Gray text
            
            if hasattr(self, 'status'):
                if self.status == "processing":
                    status_text = "Thinking..."
                    status_color = (255, 200, 0)  # Orange/yellow for processing
                else:
                    status_text = "Listening..."
                    status_color = (128, 128, 128)  # Gray for listening
            
            return DisplayContent(
                mode="voice",
                color=status_color,
                background_color=(32, 32, 32),  # Dark background
                text=status_text
            )
        
        if show_image:
            # Find closest image
            image_key = self.find_closest_image(word)
            if image_key:
                # Get image data from pixel_art module
                try:
                    from src.app.pixel_art import get_pixel_art_image
                    image_data = get_pixel_art_image(image_key)
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
                            status_indicator=None  # No indicator when word is recognized
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
