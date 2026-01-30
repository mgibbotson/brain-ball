"""Hardware implementation of LCDInterface for Adafruit ILI9341."""

# Lazy import - only import when actually needed (on Raspberry Pi)

from src.lib.lcd.interface import LCDInterface
from src.lib import HardwareError
from src.app.display_content import DisplayContent


class LCDHardware(LCDInterface):
    """Hardware implementation for Adafruit ILI9341 LCD display."""
    
    # Default SPI pins for Raspberry Pi Zero W (set in __init__)
    DEFAULT_CS_PIN = None  # Set dynamically in __init__
    DEFAULT_DC_PIN = None  # Set dynamically in __init__
    DEFAULT_RST_PIN = None  # Set dynamically in __init__
    
    def __init__(self):
        """Initialize hardware LCD display."""
        # Lazy import - only import when actually instantiating on Raspberry Pi
        try:
            import board
            import busio
            from adafruit_rgb_display import ili9341
            from digitalio import DigitalInOut
        except (ImportError, NotImplementedError) as e:
            raise HardwareError(
                f"Adafruit libraries not available - not running on Raspberry Pi: {e}"
            )
        
        self._initialized = False
        self._display = None
        self._board = board
        self._busio = busio
        self._ili9341 = ili9341
        self._DigitalInOut = DigitalInOut
        
        # Set pin constants dynamically (board module now available)
        self.DEFAULT_CS_PIN = board.D8
        self.DEFAULT_DC_PIN = board.D24
        self.DEFAULT_RST_PIN = board.D25
        
        try:
            # Initialize SPI bus
            spi = busio.SPI(clock=board.SCLK, MOSI=board.MOSI)
            
            # Initialize display pins
            cs = DigitalInOut(self.DEFAULT_CS_PIN)
            dc = DigitalInOut(self.DEFAULT_DC_PIN)
            rst = DigitalInOut(self.DEFAULT_RST_PIN)
            
            # Initialize ILI9341 display
            self._display = ili9341.ILI9341(
                spi, cs=cs, dc=dc, rst=rst, width=320, height=240
            )
        except Exception as e:
            raise HardwareError(f"Failed to initialize LCD: {e}")
    
    def initialize(self) -> None:
        """Initialize the LCD display hardware."""
        if self._display is None:
            raise HardwareError("LCD display not initialized")
        self._initialized = True
    
    def clear(self) -> None:
        """Clear the entire display."""
        if not self._initialized:
            raise HardwareError("LCD not initialized")
        try:
            self._display.fill(0x000000)  # Fill with black
        except Exception as e:
            raise HardwareError(f"Failed to clear LCD: {e}")
    
    def update_display(self, content: DisplayContent) -> None:
        """Update the display with new content."""
        if not self._initialized:
            raise HardwareError("LCD not initialized")
        if content is None:
            raise ValueError("content cannot be None")
        if not isinstance(content, DisplayContent):
            raise ValueError("content must be DisplayContent instance")
        
        try:
            # Convert RGB tuple to 16-bit color (RGB565)
            bg_color = self._rgb_to_565(content.background_color)
            
            # Fill background
            self._display.fill(bg_color)
            
            # Render text if provided
            if content.text:
                # Simple text rendering (would need font library for production)
                # For now, just display the mode
                pass
            
        except Exception as e:
            raise HardwareError(f"Failed to update LCD: {e}")
    
    def is_available(self) -> bool:
        """Check if hardware LCD is available."""
        return self._initialized and self._display is not None
    
    def _rgb_to_565(self, rgb: tuple) -> int:
        """Convert RGB tuple to 16-bit RGB565 format."""
        r, g, b = rgb
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
