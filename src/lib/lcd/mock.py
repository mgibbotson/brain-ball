"""Mock implementation of LCDInterface for testing."""

from src.lib.lcd.interface import LCDInterface
from src.lib import HardwareError
from src.app.display_content import DisplayContent


class LCDMock(LCDInterface):
    """Mock LCD implementation for testing and desktop prototyping."""
    
    def __init__(self):
        """Initialize mock LCD display."""
        self._initialized = False
        self._error = False
        self._available = True
        self.last_content = None
    
    def initialize(self) -> None:
        """Initialize mock LCD display."""
        if self._error:
            raise HardwareError("Mock LCD error")
        self._initialized = True
    
    def clear(self) -> None:
        """Clear the mock display."""
        if not self._initialized:
            raise HardwareError("LCD not initialized")
        if self._error:
            raise HardwareError("Mock LCD error")
        self.last_content = None
    
    def update_display(self, content: DisplayContent) -> None:
        """Update the mock display with content."""
        if not self._initialized:
            raise HardwareError("LCD not initialized")
        if self._error:
            raise HardwareError("Mock LCD error")
        if content is None:
            raise ValueError("content cannot be None")
        if not isinstance(content, DisplayContent):
            raise ValueError("content must be DisplayContent instance")
        
        self.last_content = content
    
    def is_available(self) -> bool:
        """Check if mock LCD is available."""
        return self._available and self._initialized
    
    def set_error(self, error: bool) -> None:
        """Set error state (for testing)."""
        self._error = error
    
    def set_available(self, available: bool) -> None:
        """Set availability state (for testing)."""
        self._available = available
