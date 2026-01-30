"""Abstract interface for photoresistor hardware."""

from abc import ABC, abstractmethod
from src.lib import HardwareError


class PhotoresistorInterface(ABC):
    """Abstract base class for photoresistor hardware."""
    
    @abstractmethod
    def read_light_value(self) -> int:
        """
        Read the current light level from the photoresistor.
        
        Returns:
            int: Raw ADC value (0-65535 or device-specific range)
            
        Raises:
            HardwareError: If sensor is unresponsive or hardware failure occurs
            IOError: If communication with hardware fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the photoresistor hardware is available and responsive.
        
        Returns:
            bool: True if hardware is available, False otherwise
        """
        pass
