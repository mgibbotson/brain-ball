"""Mic level (amplitude) interaction – no speech-to-text, just voice intensity."""

import logging
import struct
import math
import threading
from src.lib.microphone.interface import MicrophoneInterface
from src.app.display_content import DisplayContent

logger = logging.getLogger(__name__)

# Frames per chunk in background thread (~16 ms at 16 kHz) – low latency
CHUNK_FRAMES = 256
SAMPLE_RATE = 16000
# Normalize so typical speech gives ~0.3–0.7
RMS_NORMALIZE = 8000.0


def _rms_from_raw(raw: bytes) -> float:
    if not raw or len(raw) < 2:
        return 0.0
    n = len(raw) // 2
    samples = struct.unpack_from(f"<{n}h", raw)
    rms = math.sqrt(sum(s * s for s in samples) / n) if n else 0
    return min(1.0, rms / RMS_NORMALIZE)


class MicLevelInteraction:
    """Shows microphone input level (amplitude) without speech recognition.
    Uses a background thread to read audio and compute level so the main loop
    never blocks – reduces perceived delay.
    """

    def __init__(self, microphone: MicrophoneInterface):
        self.microphone = microphone
        self._stream_started = False
        self._level = 0.0
        self._lock = threading.Lock()
        self._thread = None
        self._stop = threading.Event()

    def _reader_loop(self) -> None:
        """Background: read small chunks, compute RMS, update self._level."""
        try:
            while not self._stop.is_set():
                raw = self.microphone.read_chunk(CHUNK_FRAMES)
                level = _rms_from_raw(raw)
                with self._lock:
                    self._level = level
        except Exception as e:
            logger.debug("Mic level thread: %s", e)

    def _ensure_running(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        if getattr(self.microphone, "read_chunk", None) is None:
            return
        if getattr(self.microphone, "start_continuous_stream", None) is not None:
            self.microphone.start_continuous_stream()
            self._stream_started = True
        self._stop.clear()
        self._thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._thread.start()

    def generate_display_content(self) -> DisplayContent:
        """Return content with current level (from background thread); no blocking."""
        if getattr(self.microphone, "read_chunk", None) is not None:
            self._ensure_running()
            with self._lock:
                level = self._level
        else:
            level = 0.0
            try:
                raw = self.microphone.record_audio(0.05)
                level = _rms_from_raw(raw)
            except Exception as e:
                logger.debug("Mic level read failed: %s", e)
        return DisplayContent(
            mode="voice",
            color=(255, 255, 255),
            background_color=(32, 32, 32),
            text="Mic level",
            level=level,
        )

    def stop(self) -> None:
        """Stop background thread and continuous stream."""
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=0.5)
            self._thread = None
        if self._stream_started and getattr(self.microphone, "stop_continuous_stream", None) is not None:
            try:
                self.microphone.stop_continuous_stream()
            except Exception as e:
                logger.debug("Stop continuous stream: %s", e)
            self._stream_started = False
