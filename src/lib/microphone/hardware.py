"""Hardware implementation of MicrophoneInterface."""

import platform
from src.lib.microphone.interface import MicrophoneInterface
from src.lib import HardwareError


class MicrophoneHardware(MicrophoneInterface):
    """Hardware implementation for microphone (desktop or I2S device)."""
    
    # Audio format constants
    SAMPLE_RATE = 16000  # 16kHz for Vosk
    CHANNELS = 1  # Mono
    CHUNK_SIZE = 4000  # Audio chunk size in frames
    SAMPLE_WIDTH = 2  # 16-bit (2 bytes per sample)
    
    def __init__(self):
        """Initialize hardware microphone."""
        # Lazy import - only import when actually instantiating
        try:
            import pyaudio
        except ImportError as e:
            raise HardwareError(f"pyaudio not available: {e}")
        
        self._pyaudio = pyaudio
        self._audio = None
        self._stream = None
        self._initialized = False
        self._is_raspberry_pi = platform.machine() in ('armv7l', 'armv6l', 'aarch64')
    
    def initialize(self) -> None:
        """Initialize the microphone hardware."""
        if self._initialized:
            return
        
        try:
            self._audio = self._pyaudio.PyAudio()
            
            # Try to open a test stream to verify microphone is available
            # We'll open the actual stream when recording
            self._initialized = True
        except Exception as e:
            raise HardwareError(f"Failed to initialize microphone: {e}")
    
    def record_audio(self, duration_seconds: float) -> bytes:
        """
        Record audio from the microphone.
        
        Parameters:
            duration_seconds: Duration to record in seconds
            
        Returns:
            bytes: Raw audio data (PCM format, 16-bit, mono, 16kHz)
        """
        if not self._initialized:
            raise HardwareError("Microphone not initialized")
        
        if duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")
        
        try:
            # Open audio stream
            stream = self._audio.open(
                format=self._pyaudio.paInt16,
                channels=self.CHANNELS,
                rate=self.SAMPLE_RATE,
                input=True,
                frames_per_buffer=self.CHUNK_SIZE
            )
            
            # Calculate number of frames to read
            frames_to_read = int(self.SAMPLE_RATE * duration_seconds)
            audio_data = b''
            
            # Read audio data
            for _ in range(0, frames_to_read, self.CHUNK_SIZE):
                chunk = stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                audio_data += chunk
            
            stream.stop_stream()
            stream.close()
            
            return audio_data
            
        except Exception as e:
            raise HardwareError(f"Failed to record audio: {e}")
    
    def is_available(self) -> bool:
        """Check if hardware microphone is available."""
        if not self._initialized:
            try:
                self.initialize()
            except HardwareError:
                return False
        
        try:
            # Try to open a test stream to verify microphone is available
            test_stream = self._audio.open(
                format=self._pyaudio.paInt16,
                channels=self.CHANNELS,
                rate=self.SAMPLE_RATE,
                input=True,
                frames_per_buffer=1024
            )
            test_stream.stop_stream()
            test_stream.close()
            return True
        except Exception:
            return False
    
    def __del__(self):
        """Cleanup audio resources."""
        if self._audio:
            try:
                self._audio.terminate()
            except Exception:
                pass
