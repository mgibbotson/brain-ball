"""Abstract interface for microphone hardware."""

from abc import ABC, abstractmethod
from client.lib import HardwareError


class MicrophoneInterface(ABC):
    """Abstract base class for microphone hardware."""
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the microphone hardware.
        
        Raises:
            HardwareError: If microphone cannot be initialized
            IOError: If communication with hardware fails
        """
        pass
    
    @abstractmethod
    def record_audio(self, duration_seconds: float) -> bytes:
        """
        Record audio from the microphone.
        
        Parameters:
            duration_seconds: Duration to record in seconds
            
        Returns:
            bytes: Raw audio data (PCM format, typically 16-bit, mono, 16kHz)
            
        Raises:
            HardwareError: If microphone is unresponsive or hardware failure occurs
            IOError: If communication with hardware fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the microphone hardware is available and responsive.
        
        Returns:
            bool: True if hardware is available, False otherwise
        """
        pass
