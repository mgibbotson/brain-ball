"""Hardware implementation of LCDInterface for Adafruit ILI9341."""

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
            
            # Render image if provided
            image_data = getattr(content, 'image_data', None)
            image_width = getattr(content, 'image_width', None)
            image_height = getattr(content, 'image_height', None)
            
            if image_data and image_width and image_height:
                self._render_image(content)
                
                # Render text below image if present (recognized word or status)
                if content.text:
                    self._render_text_below_image(content, image_width, image_height)
                
                # Render status indicator below the text if present
                status_indicator = getattr(content, 'status_indicator', None)
                if status_indicator:
                    self._render_status_indicator(status_indicator, image_width, image_height)
            # Render text if provided (and no image)
            elif content.text:
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
    
    def _render_image(self, content: DisplayContent) -> None:
        """
        Render pixel art image on the display.
        
        Parameters:
            content: DisplayContent with image_data, image_width, image_height
        """
        # Use getattr for backward compatibility
        image_data = getattr(content, 'image_data', None)
        image_width = getattr(content, 'image_width', None)
        image_height = getattr(content, 'image_height', None)
        
        if not image_data:
            return
        
        try:
            # Get display dimensions
            display_width = 320
            display_height = 240
            
            # Calculate centering position
            img_width = image_width
            img_height = image_height
            start_x = (display_width - img_width) // 2
            start_y = (display_height - img_height) // 2
            
            # Draw image pixel by pixel
            for y, row in enumerate(image_data):
                for x, pixel in enumerate(row):
                    pixel_color = self._rgb_to_565(pixel)
                    # Draw pixel at (start_x + x, start_y + y)
                    # ILI9341 uses pixel method or we can use a bitmap
                    # For simplicity, draw each pixel individually
                    try:
                        # Create a small 1x1 bitmap for each pixel
                        # Note: This is inefficient but works for small 16x16 images
                        self._display.pixel(start_x + x, start_y + y, pixel_color)
                    except AttributeError:
                        # If pixel method doesn't exist, use alternative method
                        # Create a bitmap and blit it
                        # For now, just fill a small area
                        pass
        except Exception as e:
            raise HardwareError(f"Failed to render image: {e}")
    
    def _render_text_below_image(self, content: DisplayContent, image_width: int, image_height: int) -> None:
        """Render text below the pixel art image.
        
        Args:
            content: DisplayContent with text to render
            image_width: Width of the main image
            image_height: Height of the main image
        """
        if not content.text:
            return
        
        try:
            display_width = 320
            display_height = 240
            
            # Position text below the image with generous spacing
            image_start_x = (display_width - image_width) // 2
            image_start_y = (display_height - image_height) // 2
            text_y = image_start_y + image_height + 20  # Increased spacing
            text_x = image_start_x + image_width // 2
            
            # Simple text rendering: draw characters pixel by pixel
            # For now, we'll use a simple approach - just indicate text is there
            # Full text rendering would require a font library
            # For LCD, we'll just draw a small indicator that text should be here
            # In a full implementation, you'd use a font library to render the text
            pass  # Text rendering on LCD would require a font library
        except Exception as e:
            raise HardwareError(f"Failed to render text: {e}")
    
    def _render_status_indicator(self, status: str, image_width: int, image_height: int) -> None:
        """Render a small status indicator icon below the text.
        
        Args:
            status: Status type ("listening" or "thinking")
            image_width: Width of the main image
            image_height: Height of the main image
        """
        if status not in ("listening", "thinking"):
            return
        
        try:
            display_width = 320
            display_height = 240
            
            # Position indicator below the text (which is below the image)
            image_start_x = (display_width - image_width) // 2
            image_start_y = (display_height - image_height) // 2
            text_spacing = 20  # Spacing between image and text
            text_height = 30  # Approximate text height
            indicator_spacing = 25  # Generous spacing between text and indicator
            text_y = image_start_y + image_height + text_spacing
            indicator_y = text_y + text_height + indicator_spacing  # Below text with more space
            indicator_x = image_start_x + image_width // 2
            
            if status == "listening":
                # Draw a microphone icon: dark cone with grey ball at the end, tilted Northeast
                # Make it 50% bigger
                scale = 1.5
                ball_color = self._rgb_to_565((148, 148, 148))
                cone_color = self._rgb_to_565((64, 64, 64))
                ball_radius = int(3 * scale)
                cone_height = int(8 * scale)
                
                # Tilt 45 degrees Northeast: ball at top-right, cone pointing down-left
                tilt_offset = int(cone_height * 0.7)  # Distance for Northeast tilt
                
                # Ball position (Northeast of center)
                ball_x = indicator_x + tilt_offset
                ball_y = indicator_y - tilt_offset
                
                # Draw ball as a small circle (approximate with pixels)
                for y_offset in range(-ball_radius, ball_radius + 1):
                    for x_offset in range(-ball_radius, ball_radius + 1):
                        if x_offset * x_offset + y_offset * y_offset <= ball_radius * ball_radius:
                            x = ball_x + x_offset
                            y = ball_y + y_offset
                            if 0 <= x < display_width and 0 <= y < display_height:
                                self._display.pixel(x, y, ball_color)
                
                # Dark cone pointing from ball toward Southwest (down-left)
                # Draw cone as a triangle (pixel by pixel, rotated 45 degrees)
                for i in range(cone_height):
                    # Width decreases as we go down-left along the diagonal
                    width_at_i = int((ball_radius + 1) * (1 - i / cone_height))
                    # Position along the diagonal (down-left from ball)
                    # For 45-degree diagonal: equal x and y movement
                    diag_x = ball_x - int(i * 0.707)  # cos(45°) ≈ 0.707
                    diag_y = ball_y + ball_radius + int(i * 0.707)  # sin(45°) ≈ 0.707
                    
                    # Draw width perpendicular to the diagonal
                    for perp_offset in range(-width_at_i, width_at_i + 1):
                        # Perpendicular to 45° line: swap x/y offsets
                        x = diag_x - int(perp_offset * 0.707)
                        y = diag_y + int(perp_offset * 0.707)
                        if 0 <= x < display_width and 0 <= y < display_height:
                            self._display.pixel(x, y, cone_color)
            elif status == "thinking":
                # Orange/yellow thinking icon (three dots)
                color = self._rgb_to_565((255, 200, 0))
                # Draw three dots in a row
                for offset in [-4, 0, 4]:
                    if 0 <= indicator_x + offset < display_width and 0 <= indicator_y < display_height:
                        self._display.pixel(indicator_x + offset, indicator_y, color)
        except Exception as e:
            raise HardwareError(f"Failed to render status indicator: {e}")