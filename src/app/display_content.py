"""DisplayContent entity representing visual feedback on LCD."""


class DisplayContent:
    """Represents the visual feedback shown on the LCD screen."""
    
    VALID_MODES = {"dark", "light", "transitioning", "imu", "voice"}
    
    def __init__(
        self,
        mode: str,
        color: tuple,
        background_color: tuple,
        text: str = None,
        update_required: bool = True,
        image_data: list = None,
        image_width: int = None,
        image_height: int = None,
        status_indicator: str = None,
        level: float = None,
    ):
        """
        Initialize DisplayContent.

        Parameters:
            mode: Display mode - "dark", "light", "transitioning", "imu", or "voice"
            color: RGB color tuple (r, g, b) where each value is 0-255
            background_color: RGB background color tuple (r, g, b)
            text: Optional text to display
            update_required: True if display needs to be refreshed
            image_data: Optional 2D array of RGB tuples [[(r, g, b), ...], ...] for pixel art
            image_width: Optional width of image in pixels
            image_height: Optional height of image in pixels
            status_indicator: Optional status indicator ("listening", "thinking", or None)
            level: Optional amplitude/level 0.0-1.0 for mic level meter (voice mode)
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
        
        # Validate image data if provided
        if image_data is not None:
            if not isinstance(image_data, list):
                raise ValueError("image_data must be a list (2D array)")
            if image_width is None or image_height is None:
                raise ValueError("image_width and image_height must be provided when image_data is set")
            if len(image_data) != image_height:
                raise ValueError(f"image_data height ({len(image_data)}) doesn't match image_height ({image_height})")
            for row in image_data:
                if not isinstance(row, list) or len(row) != image_width:
                    raise ValueError(f"image_data row width doesn't match image_width ({image_width})")
                for pixel in row:
                    if not isinstance(pixel, tuple) or len(pixel) != 3:
                        raise ValueError("image_data pixels must be RGB tuples (r, g, b)")
                    if not all(0 <= c <= 255 for c in pixel):
                        raise ValueError("image_data pixel values must be between 0 and 255")
        
        self.mode = mode
        self.color = color
        self.background_color = background_color
        self.text = text
        self.update_required = update_required
        self.image_data = image_data
        self.image_width = image_width
        self.image_height = image_height
        self.status_indicator = status_indicator
        self.level = level if level is None else max(0.0, min(1.0, float(level)))
