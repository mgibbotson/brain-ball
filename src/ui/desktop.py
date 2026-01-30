"""Desktop UI backend using Pygame for prototyping."""

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
    
    def __init__(self):
        """Initialize desktop UI backend."""
        self._initialized = False
        self._screen = None
        self._clock = None
    
    def initialize(self) -> None:
        """Initialize Pygame display."""
        if pygame is None:
            raise UIError("Pygame not available - install with: pip install pygame")
        
        try:
            pygame.init()
            self._screen = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
            pygame.display.set_caption("Interactive Kids Device - Desktop Prototype")
            self._clock = pygame.time.Clock()
            self._initialized = True
        except Exception as e:
            raise UIError(f"Failed to initialize Pygame: {e}")
    
    def render(self, content: DisplayContent) -> None:
        """Render content to Pygame display."""
        if not self._initialized:
            raise UIError("UI not initialized")
        if content is None:
            raise ValueError("content cannot be None")
        if not isinstance(content, DisplayContent):
            raise ValueError("content must be DisplayContent instance")
        
        try:
            # Fill background
            bg_color = content.background_color
            self._screen.fill(bg_color)
            
            # Handle IMU mode - draw arrow
            if content.mode == "imu" and content.text:
                self._render_arrow(content)
            elif content.text:
                # Render text if provided
                font = pygame.font.Font(None, 36)
                text_color = content.color
                text_surface = font.render(content.text, True, text_color)
                text_rect = text_surface.get_rect(center=(self.DISPLAY_WIDTH // 2, self.DISPLAY_HEIGHT // 2))
                self._screen.blit(text_surface, text_rect)
            else:
                # Render mode indicator
                font = pygame.font.Font(None, 48)
                mode_text = content.mode.upper()
                text_color = content.color
                text_surface = font.render(mode_text, True, text_color)
                text_rect = text_surface.get_rect(center=(self.DISPLAY_WIDTH // 2, self.DISPLAY_HEIGHT // 2))
                self._screen.blit(text_surface, text_rect)
            
            pygame.display.flip()
        except Exception as e:
            raise UIError(f"Failed to render content: {e}")
    
    def _render_arrow(self, content: DisplayContent) -> None:
        """Render an arrow pointing in the acceleration direction."""
        # Parse direction info from text: "angle,dir_x,dir_y"
        try:
            parts = content.text.split(',')
            angle_deg = float(parts[0])
            dir_x = float(parts[1])
            dir_y = float(parts[2])
        except (ValueError, IndexError):
            # Fallback if parsing fails
            return
        
        center_x = self.DISPLAY_WIDTH // 2
        center_y = self.DISPLAY_HEIGHT // 2
        arrow_length = 150  # Length of arrow in pixels
        
        # Calculate arrow endpoint
        # Note: Pygame's y-axis is inverted (0 at top), so negate dir_y
        end_x = center_x + dir_x * arrow_length
        end_y = center_y - dir_y * arrow_length  # Invert y for screen coordinates
        
        # Draw arrow line
        arrow_color = content.color
        pygame.draw.line(self._screen, arrow_color, (center_x, center_y), (end_x, end_y), 4)
        
        # Draw arrowhead (triangle)
        import math
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
        pygame.draw.polygon(self._screen, arrow_color, arrowhead_points)
    
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
