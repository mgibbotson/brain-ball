"""Device UI backend using LCD hardware for deployment."""

from client.ui.interface import UIInterface
from client.ui import UIError
from client.lib.lcd.interface import LCDInterface
from client.app.display_content import DisplayContent


class UIDevice(UIInterface):
    """Device UI implementation using LCD hardware."""
    
    def __init__(self, lcd: LCDInterface):
        """
        Initialize device UI backend.
        
        Parameters:
            lcd: LCDInterface instance for hardware display
        """
        self._lcd = lcd
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize LCD display."""
        try:
            self._lcd.initialize()
            self._initialized = True
        except Exception as e:
            raise UIError(f"Failed to initialize LCD: {e}")
    
    def render(self, content: DisplayContent) -> None:
        """Render content to LCD display."""
        if not self._initialized:
            raise UIError("UI not initialized")
        if content is None:
            raise ValueError("content cannot be None")
        if not isinstance(content, DisplayContent):
            raise ValueError("content must be DisplayContent instance")
        
        try:
            self._lcd.update_display(content)
        except Exception as e:
            raise UIError(f"Failed to render content: {e}")
    
    def update(self) -> None:
        """Update display (no-op for device backend)."""
        # Device backend doesn't need event loop updates
        pass
    
    def cleanup(self) -> None:
        """Clean up LCD resources."""
        if self._initialized:
            try:
                self._lcd.clear()
            except Exception:
                pass  # Ignore errors during cleanup
            self._initialized = False
