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
            if content.mode == "imu" and content.text:
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
