"""Microphone hardware abstraction library."""

from src.lib.microphone.interface import MicrophoneInterface
from src.lib.microphone.hardware import MicrophoneHardware
from src.lib.microphone.mock import MicrophoneMock

__all__ = ["MicrophoneInterface", "MicrophoneHardware", "MicrophoneMock"]
