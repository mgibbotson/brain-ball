"""Microphone hardware abstraction library."""

from client.lib.microphone.interface import MicrophoneInterface
from client.lib.microphone.hardware import MicrophoneHardware
from client.lib.microphone.mock import MicrophoneMock

__all__ = ["MicrophoneInterface", "MicrophoneHardware", "MicrophoneMock"]
