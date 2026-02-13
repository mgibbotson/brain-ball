"""Hardware implementation of LCDInterface for Adafruit TFT displays.

Supports:
- ILI9341: 320x240 rectangular (e.g. 2.8" TFT)
- GC9A01A: 240x240 round (Adafruit 1.28" Round TFT with EYESPI - Product 6178)
"""

import math
import os
from src.lib.lcd.interface import LCDInterface
from src.lib import HardwareError
from src.app.display_content import DisplayContent


class LCDHardware(LCDInterface):
    """Hardware implementation for Adafruit SPI TFT (ILI9341 or GC9A01A)."""

    DEFAULT_CS_PIN = None
    DEFAULT_DC_PIN = None
    DEFAULT_RST_PIN = None

    def __init__(self):
        """Initialize hardware LCD display."""
        try:
            import board
            import busio
            from digitalio import DigitalInOut
        except (ImportError, NotImplementedError) as e:
            raise HardwareError(
                f"Adafruit libraries not available - not running on Raspberry Pi: {e}"
            )

        self._initialized = False
        self._display = None
        self._width = 320
        self._height = 240

        # Pins: TFTCS=GPIO22/D22, RST=GPIO27/D27, DC=GPIO17/D17; SCK=23, MOSI=19
        self.DEFAULT_CS_PIN = board.D22
        self.DEFAULT_DC_PIN = board.D17
        self.DEFAULT_RST_PIN = board.D27

        display_type = (os.environ.get("DISPLAY_TYPE") or "ili9341").strip().lower()
        rotation = int(os.environ.get("LCD_ROTATION", "0"))
        if rotation not in (0, 90, 180, 270):
            rotation = 0

        try:
            spi = busio.SPI(clock=board.SCLK, MOSI=board.MOSI)
            cs = DigitalInOut(self.DEFAULT_CS_PIN)
            dc = DigitalInOut(self.DEFAULT_DC_PIN)
            rst = DigitalInOut(self.DEFAULT_RST_PIN)

            if display_type == "gc9a01a":
                from adafruit_rgb_display import gc9a01a
                self._width, self._height = 240, 240
                self._display = gc9a01a.GC9A01A(
                    spi, dc=dc, cs=cs, rst=rst, width=240, height=240, rotation=rotation
                )
            else:
                from adafruit_rgb_display import ili9341
                self._width, self._height = 320, 240
                self._display = ili9341.ILI9341(
                    spi, cs=cs, dc=dc, rst=rst, width=320, height=240, rotation=rotation
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
            elif content.mode == "imu" and content.text:
                self._render_imu_arrow(content)
            elif getattr(content, "level", None) is not None:
                self._render_level_bar(content)
            elif content.text:
                pass  # Text would need font library
            
        except Exception as e:
            raise HardwareError(f"Failed to update LCD: {e}")
    
    def is_available(self) -> bool:
        """Check if hardware LCD is available."""
        return self._initialized and self._display is not None
    
    def _rgb_to_565(self, rgb: tuple) -> int:
        """Convert RGB tuple to 16-bit RGB565 format."""
        r, g, b = rgb
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

    def _render_imu_arrow(self, content: DisplayContent) -> None:
        """Render an arrow on the LCD for IMU mode (direction from content.text)."""
        try:
            parts = content.text.split(",")
            if len(parts) != 3:
                return
            angle_deg = float(parts[0])
            dir_x = float(parts[1])
            dir_y = float(parts[2])
            if abs(dir_x) < 1e-6 and abs(dir_y) < 1e-6:
                dir_x, dir_y = 1.0, 0.0
                angle_deg = 0.0
        except (ValueError, TypeError):
            return
        try:
            W, H = self._width, self._height
            cx, cy = W // 2, H // 2
            arrow_color = self._rgb_to_565(content.color)
            arrow_length = int(0.4 * min(W, H))
            thick = 4
            end_x = cx + dir_x * arrow_length
            end_y = cy - dir_y * arrow_length
            end_x = max(0, min(W - 1, int(end_x)))
            end_y = max(0, min(H - 1, int(end_y)))

            steps = max(1, arrow_length // 2)
            for i in range(steps + 1):
                t = i / steps
                x = int(cx + t * (end_x - cx))
                y = int(cy + t * (end_y - cy))
                x0 = max(0, x - thick // 2)
                y0 = max(0, y - thick // 2)
                w = min(thick, W - x0)
                h = min(thick, H - y0)
                if w > 0 and h > 0:
                    self._display.fill_rectangle(x0, y0, w, h, arrow_color)

            angle_rad = math.radians(angle_deg)
            head_size = min(16, arrow_length // 4)
            base_x = end_x - math.cos(angle_rad) * head_size
            base_y = end_y + math.sin(angle_rad) * head_size
            perp = angle_rad + math.pi / 2
            half = head_size * 0.6
            p1_x = base_x + math.cos(perp) * half
            p1_y = base_y - math.sin(perp) * half
            p2_x = base_x - math.cos(perp) * half
            p2_y = base_y + math.sin(perp) * half
            tip = (end_x, end_y)
            b1 = (int(p1_x), int(p1_y))
            b2 = (int(p2_x), int(p2_y))
            ys = sorted({tip[1], b1[1], b2[1]})
            y_min, y_max = max(0, min(ys)), min(H - 1, max(ys))
            for y in range(y_min, y_max + 1):
                xs = []
                for (ax, ay), (bx, by) in [(tip, b1), (tip, b2), (b1, b2)]:
                    if ay == by:
                        if ay == y:
                            xs.extend([ax, bx])
                    else:
                        t = (y - ay) / (by - ay) if by != ay else 0
                        if 0 <= t <= 1:
                            xs.append(ax + t * (bx - ax))
                if len(xs) >= 2:
                    x_min = max(0, int(min(xs)))
                    x_max = min(W - 1, int(max(xs)))
                    if x_max >= x_min:
                        self._display.fill_rectangle(x_min, y, x_max - x_min + 1, 1, arrow_color)
        except Exception as e:
            raise HardwareError(f"Failed to render IMU arrow: {e}")

    def _scaled_image_rect(self, image_width: int, image_height: int):
        """Return (start_x, start_y, scaled_w, scaled_h) so image fills 80% of screen."""
        max_w = int(0.8 * self._width)
        max_h = int(0.8 * self._height)
        scale = max(1, min(max_w // image_width, max_h // image_height))
        scaled_w = image_width * scale
        scaled_h = image_height * scale
        start_x = (self._width - scaled_w) // 2
        start_y = (self._height - scaled_h) // 2
        return start_x, start_y, scaled_w, scaled_h

    def _render_level_bar(self, content: DisplayContent) -> None:
        """Render a horizontal level/amplitude bar (0–1)."""
        level = getattr(content, "level", 0.0) or 0.0
        level = max(0.0, min(1.0, level))
        W, H = self._width, self._height
        bar_width = int(W * 0.8)
        bar_height = max(4, H // 20)
        bar_x = (W - bar_width) // 2
        bar_y = H - bar_height - (H // 10)
        bg_color = self._rgb_to_565((60, 60, 60))
        fill_color = self._rgb_to_565(content.color)
        self._display.fill_rectangle(bar_x, bar_y, bar_width, bar_height, bg_color)
        fill_width = int(bar_width * level)
        if fill_width > 0:
            self._display.fill_rectangle(bar_x, bar_y, fill_width, bar_height, fill_color)

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
            display_width = self._width
            display_height = self._height
            start_x, start_y, scaled_w, scaled_h = self._scaled_image_rect(image_width, image_height)
            scale = scaled_w // image_width

            # Use fill_rectangle per source pixel (one rect per block) instead of pixel-by-pixel
            for y, row in enumerate(image_data):
                for x, pixel in enumerate(row):
                    pixel_color = self._rgb_to_565(pixel)
                    bx = start_x + x * scale
                    by = start_y + y * scale
                    self._display.fill_rectangle(bx, by, scale, scale, pixel_color)
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
            image_start_x, image_start_y, scaled_w, scaled_h = self._scaled_image_rect(image_width, image_height)
            # Position text below the scaled image
            text_y = image_start_y + scaled_h + 20
            text_x = image_start_x + scaled_w // 2
            # Text rendering on LCD would require a font library; currently a no-op
            pass
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
            display_width = self._width
            display_height = self._height
            image_start_x, image_start_y, scaled_w, scaled_h = self._scaled_image_rect(image_width, image_height)
            text_spacing = 20
            text_height = 30
            indicator_spacing = 25
            text_y = image_start_y + scaled_h + text_spacing
            indicator_y = text_y + text_height + indicator_spacing
            indicator_x = image_start_x + scaled_w // 2
            
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