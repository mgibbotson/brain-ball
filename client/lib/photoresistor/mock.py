"""Mock implementation of PhotoresistorInterface for testing."""

import random
from client.lib.photoresistor.interface import PhotoresistorInterface
from client.lib import HardwareError


class PhotoresistorMock(PhotoresistorInterface):
    """Mock photoresistor implementation for testing and desktop prototyping."""
    
    def __init__(self, initial_value: int = 32768):
        """
        Initialize mock photoresistor with optional initial light value.
        
        Parameters:
            initial_value: Starting light value (0-65535), defaults to middle value
        """
        # Clamp initial value to valid range
        self._light_value = max(0, min(65535, initial_value))
        self._error = False
        self._available = True
        
        # Random walk parameters
        self._step_size = 8000  # How much the value can change per step
        self._min_value = 0
        self._max_value = 65535
    
    def read_light_value(self) -> int:
        """
        Read the current light level (mock) with random walk behavior.
        
        Each call performs a random walk step, making the value gradually change
        over time to simulate real light level changes.
        """
        if self._error:
            raise HardwareError("Mock photoresistor error")
        if not self._available:
            raise HardwareError("Mock photoresistor not available")
        
        # Perform random walk step
        # Move the value by a random amount within step_size
        change = random.randint(-self._step_size, self._step_size)
        new_value = self._light_value + change
        
        # Clamp to valid range
        self._light_value = max(self._min_value, min(self._max_value, new_value))
        
        return self._light_value
    
    def is_available(self) -> bool:
        """Check if mock photoresistor is available."""
        return self._available
    
    def set_light_value(self, value: int) -> None:
        """Set the mock light value (for testing)."""
        self._light_value = value
    
    def set_error(self, error: bool) -> None:
        """Set error state (for testing)."""
        self._error = error
    
    def set_available(self, available: bool) -> None:
        """Set availability state (for testing)."""
        self._available = available
