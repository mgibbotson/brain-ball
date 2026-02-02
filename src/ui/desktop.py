"""Desktop UI backend using Pygame for prototyping."""

import math
try:
    import pygame
except ImportError:
    pygame = None

from src.ui.interface import UIInterface
from src.ui import UIError
from src.app.display_content import DisplayContent


class UIDesktop(UIInterface):
    """Desktop UI implementation using Pygame for prototyping."""
    
    # Display dimensions matching typical LCD (320x240 scaled up)
    DISPLAY_WIDTH = 640
    DISPLAY_HEIGHT = 480
    
    # Circular display parameters (matching ILI9341 circular viewport)
    # Use the smaller dimension to ensure circle fits
    CIRCLE_RADIUS = min(DISPLAY_WIDTH, DISPLAY_HEIGHT) // 2 - 20  # Leave some margin
    CIRCLE_CENTER_X = DISPLAY_WIDTH // 2
    CIRCLE_CENTER_Y = DISPLAY_HEIGHT // 2
    
    def __init__(self):
        """Initialize desktop UI backend."""
        self._initialized = False
        self._screen = None
        self._clock = None
        self._circle_surface = None
    
    def initialize(self) -> None:
        """Initialize Pygame display."""
        if pygame is None:
            raise UIError("Pygame not available - install with: pip install pygame")
        
        try:
            pygame.init()
            self._screen = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
            pygame.display.set_caption("Interactive Kids Device - Desktop Prototype")
            self._clock = pygame.time.Clock()
            
            # Create circular surface for rendering content
            self._circle_surface = pygame.Surface((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT), pygame.SRCALPHA)
            
            self._initialized = True
        except Exception as e:
            raise UIError(f"Failed to initialize Pygame: {e}")
    
    def render(self, content: DisplayContent) -> None:
        """Render content to Pygame display with circular viewport."""
        if not self._initialized:
            raise UIError("UI not initialized")
        if content is None:
            raise ValueError("content cannot be None")
        if not isinstance(content, DisplayContent):
            raise ValueError("content must be DisplayContent instance")
        
        try:
            # Fill screen background (outside circle will be visible)
            self._screen.fill((64, 64, 64))  # Dark gray background for outside circle
            
            # Clear circular surface (transparent)
            self._circle_surface.fill((0, 0, 0, 0))
            
            # Fill circular area with background color
            bg_color = content.background_color
            pygame.draw.circle(self._circle_surface, bg_color,
                             (self.CIRCLE_CENTER_X, self.CIRCLE_CENTER_Y),
                             self.CIRCLE_RADIUS)
            
            # Render content to circular surface
            # Check for image data using getattr for backward compatibility
            image_data = getattr(content, 'image_data', None)
            image_width = getattr(content, 'image_width', None)
            image_height = getattr(content, 'image_height', None)
            
            if image_data and image_width and image_height:
                # Render pixel art image
                self._render_pixel_art(content, surface=self._circle_surface)
                # Render status indicator below the image if present
                status_indicator = getattr(content, 'status_indicator', None)
                if status_indicator:
                    self._render_status_indicator(status_indicator, surface=self._circle_surface)
            elif content.mode == "imu" and content.text:
                self._render_arrow(content, surface=self._circle_surface)
            elif content.text:
                # Render text if provided
                font = pygame.font.Font(None, 36)
                text_color = content.color
                text_surface = font.render(content.text, True, text_color)
                text_rect = text_surface.get_rect(center=(self.CIRCLE_CENTER_X, self.CIRCLE_CENTER_Y))
                self._circle_surface.blit(text_surface, text_rect)
            else:
                # Render mode indicator
                font = pygame.font.Font(None, 48)
                mode_text = content.mode.upper()
                text_color = content.color
                text_surface = font.render(mode_text, True, text_color)
                text_rect = text_surface.get_rect(center=(self.CIRCLE_CENTER_X, self.CIRCLE_CENTER_Y))
                self._circle_surface.blit(text_surface, text_rect)
            
            # Create a mask to clip content to circle using pygame.mask
            # Create a temporary surface with white circle for mask
            mask_surface = pygame.Surface((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
            mask_surface.fill((0, 0, 0))  # Black background
            pygame.draw.circle(mask_surface, (255, 255, 255),
                             (self.CIRCLE_CENTER_X, self.CIRCLE_CENTER_Y),
                             self.CIRCLE_RADIUS)
            
            # Create mask from surface
            circle_mask = pygame.mask.from_surface(mask_surface)
            
            # Apply mask to circle_surface: set alpha to 0 outside circle
            # Only process pixels in bounding box around circle for efficiency
            bbox_left = max(0, self.CIRCLE_CENTER_X - self.CIRCLE_RADIUS - 5)
            bbox_right = min(self.DISPLAY_WIDTH, self.CIRCLE_CENTER_X + self.CIRCLE_RADIUS + 5)
            bbox_top = max(0, self.CIRCLE_CENTER_Y - self.CIRCLE_RADIUS - 5)
            bbox_bottom = min(self.DISPLAY_HEIGHT, self.CIRCLE_CENTER_Y + self.CIRCLE_RADIUS + 5)
            
            for x in range(bbox_left, bbox_right):
                for y in range(bbox_top, bbox_bottom):
                    if not circle_mask.get_at((x, y)):
                        # Outside circle - make transparent
                        r, g, b, a = self._circle_surface.get_at((x, y))
                        self._circle_surface.set_at((x, y), (r, g, b, 0))
            
            # Blit circular surface to main screen
            self._screen.blit(self._circle_surface, (0, 0))
            
            # Draw black circle border to show display boundary
            pygame.draw.circle(self._screen, (0, 0, 0),
                             (self.CIRCLE_CENTER_X, self.CIRCLE_CENTER_Y),
                             self.CIRCLE_RADIUS, width=3)
            
            pygame.display.flip()
        except Exception as e:
            raise UIError(f"Failed to render content: {e}")
    
    def _render_arrow(self, content: DisplayContent, surface=None) -> None:
        """Render an arrow pointing in the acceleration direction."""
        if surface is None:
            surface = self._screen
        
        # Parse direction info from text: "angle,dir_x,dir_y"
        try:
            parts = content.text.split(',')
            angle_deg = float(parts[0])
            dir_x = float(parts[1])
            dir_y = float(parts[2])
        except (ValueError, IndexError):
            # Fallback if parsing fails
            return
        
        center_x = self.CIRCLE_CENTER_X
        center_y = self.CIRCLE_CENTER_Y
        # Scale arrow length to fit within circle (leave some margin)
        arrow_length = self.CIRCLE_RADIUS * 0.6  # 60% of radius
        
        # Calculate arrow endpoint
        # Note: Pygame's y-axis is inverted (0 at top), so negate dir_y
        end_x = center_x + dir_x * arrow_length
        end_y = center_y - dir_y * arrow_length  # Invert y for screen coordinates
        
        # Draw arrow line
        arrow_color = content.color
        pygame.draw.line(surface, arrow_color, (center_x, center_y), (end_x, end_y), 4)
        
        # Draw arrowhead (triangle)
        arrowhead_size = 20
        angle_rad = math.radians(angle_deg)
        
        # Arrowhead points (perpendicular to arrow direction)
        perp_angle = angle_rad + math.pi / 2
        arrowhead_base_x = end_x - math.cos(angle_rad) * arrowhead_size
        arrowhead_base_y = end_y + math.sin(angle_rad) * arrowhead_size  # Invert y
        
        # Calculate two points for arrowhead triangle
        arrowhead_point1_x = arrowhead_base_x + math.cos(perp_angle) * 10
        arrowhead_point1_y = arrowhead_base_y - math.sin(perp_angle) * 10  # Invert y
        arrowhead_point2_x = arrowhead_base_x - math.cos(perp_angle) * 10
        arrowhead_point2_y = arrowhead_base_y + math.sin(perp_angle) * 10  # Invert y
        
        # Draw arrowhead triangle
        arrowhead_points = [
            (end_x, end_y),
            (arrowhead_point1_x, arrowhead_point1_y),
            (arrowhead_point2_x, arrowhead_point2_y)
        ]
        pygame.draw.polygon(surface, arrow_color, arrowhead_points)
    
    def _render_pixel_art(self, content: DisplayContent, surface=None) -> None:
        """Render pixel art image on the surface."""
        if surface is None:
            surface = self._screen
        
        if not content.image_data or not content.image_width or not content.image_height:
            return
        
        try:
            # Scale factor for pixel art (make it bigger for visibility)
            scale = 8  # 16x16 becomes 128x128
            
            # Calculate position to center the scaled image
            scaled_width = content.image_width * scale
            scaled_height = content.image_height * scale
            start_x = self.CIRCLE_CENTER_X - scaled_width // 2
            start_y = self.CIRCLE_CENTER_Y - scaled_height // 2
            
            # Draw each pixel scaled up
            for y, row in enumerate(content.image_data):
                for x, pixel in enumerate(row):
                    # Draw a scaled rectangle for each pixel
                    rect_x = start_x + (x * scale)
                    rect_y = start_y + (y * scale)
                    pygame.draw.rect(
                        surface,
                        pixel,
                        (rect_x, rect_y, scale, scale)
                    )
        except Exception as e:
            # If rendering fails, just log and continue
            pass
    
    def _render_status_indicator(self, status: str, surface=None) -> None:
        """Render a small status indicator icon below the main image.
        
        Args:
            status: Status type ("listening" or "thinking")
            surface: Pygame surface to render on (defaults to screen)
        """
        if surface is None:
            surface = self._screen
        
        if status not in ("listening", "thinking"):
            return
        
        try:
            # Position indicator below the main image
            # Main image is centered, so indicator goes below it
            # Image is 16x16 scaled by 8 = 128x128 pixels
            indicator_y = self.CIRCLE_CENTER_Y + (16 * 8) // 2 + 15  # Below 16x16 image scaled by 8
            indicator_x = self.CIRCLE_CENTER_X
            
            # Draw a small dot/icon based on status
            if status == "listening":
                # Gray dot for listening
                color = (128, 128, 128)
                # Draw a small circle
                pygame.draw.circle(surface, color, (indicator_x, indicator_y), 5)
            elif status == "thinking":
                # Orange/yellow dot for thinking
                color = (255, 200, 0)
                # Draw a small circle
                pygame.draw.circle(surface, color, (indicator_x, indicator_y), 5)
        except Exception as e:
            pass  # Don't crash UI if indicator rendering fails
    
    def update(self) -> None:
        """Update Pygame display and handle events."""
        if not self._initialized:
            return
        
        try:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
            
            self._clock.tick(60)  # Limit to 60 FPS
        except Exception:
            pass  # Ignore errors during cleanup
    
    def cleanup(self) -> None:
        """Clean up Pygame resources."""
        if self._initialized:
            try:
                pygame.quit()
            except Exception:
                pass  # Ignore errors during cleanup
            self._initialized = False
