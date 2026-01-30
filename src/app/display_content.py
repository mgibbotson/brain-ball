"""DisplayContent entity representing visual feedback on LCD."""


class DisplayContent:
    """Represents the visual feedback shown on the LCD screen."""
    
    VALID_MODES = {"dark", "light", "transitioning", "imu"}
    
    def __init__(
        self,
        mode: str,
        color: tuple,
        background_color: tuple,
        text: str = None,
        update_required: bool = True
    ):
        """
        Initialize DisplayContent.
        
        Parameters:
            mode: Display mode - "dark", "light", or "transitioning"
            color: RGB color tuple (r, g, b) where each value is 0-255
            background_color: RGB background color tuple (r, g, b)
            text: Optional text to display
            update_required: True if display needs to be refreshed
            
        Raises:
            ValueError: If validation fails
        """
        # Validation
        if mode not in self.VALID_MODES:
            raise ValueError(f"mode must be one of {self.VALID_MODES}")
        
        if not isinstance(color, tuple) or len(color) != 3:
            raise ValueError("color must be a tuple of 3 integers")
        if not all(0 <= c <= 255 for c in color):
            raise ValueError("color values must be between 0 and 255")
        
        if not isinstance(background_color, tuple) or len(background_color) != 3:
            raise ValueError("background_color must be a tuple of 3 integers")
        if not all(0 <= c <= 255 for c in background_color):
            raise ValueError("background_color values must be between 0 and 255")
        
        self.mode = mode
        self.color = color
        self.background_color = background_color
        self.text = text
        self.update_required = update_required
