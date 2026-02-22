"""Abstract interface for IMU hardware."""

from abc import ABC, abstractmethod
from typing import Tuple
from client.lib import HardwareError


class IMUInterface(ABC):
    """Abstract base class for IMU hardware."""
    
    @abstractmethod
    def read_acceleration(self) -> Tuple[float, float, float]:
        """
        Read the current acceleration from the IMU.
        
        Returns:
            Tuple[float, float, float]: Acceleration vector (x, y, z) in m/s²
            
        Raises:
            HardwareError: If sensor is unresponsive or hardware failure occurs
            IOError: If communication with hardware fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the IMU hardware is available and responsive.
        
        Returns:
            bool: True if hardware is available, False otherwise
        """
        pass
