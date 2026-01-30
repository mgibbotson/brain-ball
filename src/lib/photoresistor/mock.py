"""Mock implementation of PhotoresistorInterface for testing."""

from src.lib.photoresistor.interface import PhotoresistorInterface
from src.lib import HardwareError


class PhotoresistorMock(PhotoresistorInterface):
    """Mock photoresistor implementation for testing and desktop prototyping."""
    
    def __init__(self, initial_value: int = 32768):
        """Initialize mock photoresistor with optional initial light value."""
        self._light_value = initial_value
        self._error = False
        self._available = True
    
    def read_light_value(self) -> int:
        """Read the current light level (mock)."""
        if self._error:
            raise HardwareError("Mock photoresistor error")
        if not self._available:
            raise HardwareError("Mock photoresistor not available")
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
