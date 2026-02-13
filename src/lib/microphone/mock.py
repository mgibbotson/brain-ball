"""Mock implementation of MicrophoneInterface for testing."""

import random
import struct
from src.lib.microphone.interface import MicrophoneInterface
from src.lib import HardwareError

# Match MicLevelInteraction normalization so synthetic RMS maps to 0–1 level
RMS_NORMALIZE = 8000.0


class MicrophoneMock(MicrophoneInterface):
    """Mock microphone implementation for unit testing."""
    
    # Audio format constants (matching hardware)
    SAMPLE_RATE = 16000
    CHANNELS = 1
    SAMPLE_WIDTH = 2
    
    def __init__(self):
        """Initialize mock microphone."""
        self._initialized = False
        self._available = True
        self._error = False
        self._audio_data_queue = []  # Queue of audio data to return
    
    def initialize(self) -> None:
        """Initialize the mock microphone."""
        if self._error:
            raise HardwareError("Mock microphone error")
        if not self._available:
            raise HardwareError("Mock microphone not available")
        self._initialized = True
    
    def record_audio(self, duration_seconds: float) -> bytes:
        """
        Record audio (mock) - returns queued audio data or silence.
        
        Parameters:
            duration_seconds: Duration to record in seconds
            
        Returns:
            bytes: Raw audio data (PCM format, 16-bit, mono, 16kHz)
        """
        if not self._initialized:
            raise HardwareError("Mock microphone not initialized")
        if self._error:
            raise HardwareError("Mock microphone error")
        if not self._available:
            raise HardwareError("Mock microphone not available")
        
        # Calculate number of samples
        num_samples = int(self.SAMPLE_RATE * duration_seconds)
        
        # If we have queued audio data, return it
        if self._audio_data_queue:
            audio_data = self._audio_data_queue.pop(0)
            # Pad or truncate to match requested duration
            expected_size = num_samples * self.SAMPLE_WIDTH
            if len(audio_data) < expected_size:
                # Pad with silence
                audio_data += b'\x00' * (expected_size - len(audio_data))
            elif len(audio_data) > expected_size:
                # Truncate
                audio_data = audio_data[:expected_size]
            return audio_data
        
        # Otherwise return silence
        return b'\x00' * (num_samples * self.SAMPLE_WIDTH)
    
    def is_available(self) -> bool:
        """Check if mock microphone is available."""
        return self._available and self._initialized
    
    def set_audio_data(self, audio_data: bytes) -> None:
        """
        Set audio data to return on next record_audio call (for testing).
        
        Parameters:
            audio_data: Raw audio data (PCM format, 16-bit, mono, 16kHz)
        """
        self._audio_data_queue.append(audio_data)
    
    def set_error(self, error: bool) -> None:
        """Set error state (for testing)."""
        self._error = error
    
    def set_available(self, available: bool) -> None:
        """Set availability state (for testing)."""
        self._available = available


class RandomWalkMicrophone(MicrophoneInterface):
    """Mock microphone that yields audio chunks with RMS following a random walk.
    Use when MIC_RANDOM_WALK=1 to test mic level UI on device without hardware.
    Implements continuous stream API (start_continuous_stream, read_chunk, stop_continuous_stream).
    """

    SAMPLE_RATE = 16000
    CHANNELS = 1
    CHUNK_SIZE = 4000
    SAMPLE_WIDTH = 2

    def __init__(self, step: float = 0.025, seed: int | None = None):
        self._initialized = False
        self._stream = None
        self._level = 0.5
        self._step = max(0.01, min(0.2, step))
        if seed is not None:
            random.seed(seed)

    def initialize(self) -> None:
        self._initialized = True

    def start_continuous_stream(self) -> None:
        if not self._initialized:
            raise HardwareError("Microphone not initialized")
        self._stream = True

    def read_chunk(self, num_frames: int) -> bytes:
        if not self._initialized or self._stream is None:
            raise HardwareError("Stream not started")
        # Random walk: level in [0, 1]
        self._level = max(0.0, min(1.0, self._level + random.uniform(-self._step, self._step)))
        # Produce 16-bit mono samples so RMS = level * RMS_NORMALIZE (single value => RMS = |value|)
        peak = min(32767, int(self._level * RMS_NORMALIZE))
        return struct.pack(f"<{num_frames}h", *([peak] * num_frames))

    def stop_continuous_stream(self) -> None:
        self._stream = None

    def record_audio(self, duration_seconds: float) -> bytes:
        if not self._initialized:
            raise HardwareError("Mock microphone not initialized")
        num_samples = int(self.SAMPLE_RATE * duration_seconds)
        self._level = max(0.0, min(1.0, self._level + random.uniform(-self._step, self._step)))
        peak = min(32767, int(self._level * RMS_NORMALIZE))
        return struct.pack(f"<{num_samples}h", *([peak] * num_samples))

    def is_available(self) -> bool:
        return self._initialized
