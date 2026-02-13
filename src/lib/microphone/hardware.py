"""Hardware implementation of MicrophoneInterface."""

import os
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
        self._is_raspberry_pi = platform.machine() in ("armv7l", "armv6l", "aarch64")
        self._device_env = os.environ.get("MIC_INPUT_DEVICE", "").strip() or None
    
    def _get_input_device_index(self):
        """Return input device index from MIC_INPUT_DEVICE, or None for default."""
        if not self._device_env or not self._audio:
            return None
        try:
            return int(self._device_env)
        except ValueError:
            pass
        # Match by device name (e.g. ALSA plughw:CARD=sndrpigooglevoi,0)
        for i in range(self._audio.get_device_count()):
            info = self._audio.get_device_info_by_index(i)
            if info.get("maxInputChannels", 0) > 0 and self._device_env in info.get("name", ""):
                return i
        return None

    def initialize(self) -> None:
        """Initialize the microphone hardware."""
        if self._initialized:
            return

        try:
            self._audio = self._pyaudio.PyAudio()
            self._initialized = True
        except Exception as e:
            raise HardwareError(f"Failed to initialize microphone: {e}")
    
    def start_continuous_stream(self) -> None:
        """Open and keep the input stream open for continuous reading (e.g. mic level meter)."""
        if not self._initialized:
            raise HardwareError("Microphone not initialized")
        if self._stream is not None:
            return
        kwargs = dict(
            format=self._pyaudio.paInt16,
            channels=self.CHANNELS,
            rate=self.SAMPLE_RATE,
            input=True,
            frames_per_buffer=self.CHUNK_SIZE,
        )
        idx = self._get_input_device_index()
        if idx is not None:
            kwargs["input_device_index"] = idx
        try:
            self._stream = self._audio.open(**kwargs)
        except Exception as e:
            raise HardwareError(f"Failed to start microphone stream: {e}")

    def read_chunk(self, num_frames: int) -> bytes:
        """
        Read a chunk from the continuous stream (call start_continuous_stream first).
        Returns num_frames * 2 bytes (16-bit mono).
        """
        if not self._initialized:
            raise HardwareError("Microphone not initialized")
        if self._stream is None:
            self.start_continuous_stream()
        try:
            data = b""
            to_read = num_frames
            while to_read > 0:
                n = min(to_read, self.CHUNK_SIZE)
                chunk = self._stream.read(n, exception_on_overflow=False)
                data += chunk
                to_read -= n
            return data
        except Exception as e:
            raise HardwareError(f"Failed to read from microphone: {e}")

    def stop_continuous_stream(self) -> None:
        """Close the continuous stream if open."""
        if self._stream is None:
            return
        try:
            self._stream.stop_stream()
            self._stream.close()
        except Exception:
            pass
        self._stream = None

    def record_audio(self, duration_seconds: float) -> bytes:
        """
        Record audio from the microphone.
        Opens and closes a new stream each call; for continuous reading use
        start_continuous_stream/read_chunk/stop_continuous_stream instead.
        """
        if not self._initialized:
            raise HardwareError("Microphone not initialized")
        if duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")
        kwargs = dict(
            format=self._pyaudio.paInt16,
            channels=self.CHANNELS,
            rate=self.SAMPLE_RATE,
            input=True,
            frames_per_buffer=self.CHUNK_SIZE,
        )
        idx = self._get_input_device_index()
        if idx is not None:
            kwargs["input_device_index"] = idx
        try:
            stream = self._audio.open(**kwargs)
            frames_to_read = int(self.SAMPLE_RATE * duration_seconds)
            audio_data = b""
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
        
        kwargs = dict(
            format=self._pyaudio.paInt16,
            channels=self.CHANNELS,
            rate=self.SAMPLE_RATE,
            input=True,
            frames_per_buffer=1024,
        )
        idx = self._get_input_device_index()
        if idx is not None:
            kwargs["input_device_index"] = idx
        try:
            test_stream = self._audio.open(**kwargs)
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
