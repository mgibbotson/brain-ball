"""IMU interaction logic for displaying acceleration direction."""

import logging
import math
from typing import Tuple
from src.lib.imu.interface import IMUInterface
from src.app.display_content import DisplayContent

logger = logging.getLogger(__name__)


class IMUInteraction:
    """Manages IMU acceleration reading and display generation."""
    
    def __init__(self, imu: IMUInterface):
        """
        Initialize IMU interaction.
        
        Parameters:
            imu: IMUInterface instance
        """
        self.imu = imu
        self.current_acceleration = None
    
    def update_acceleration(self) -> Tuple[float, float, float]:
        """
        Read IMU and get current acceleration.
        
        Returns:
            Tuple[float, float, float]: Acceleration vector (x, y, z)
            
        Raises:
            HardwareError: If IMU read fails
        """
        try:
            accel = self.imu.read_acceleration()
            self.current_acceleration = accel
            logger.debug(f"Acceleration updated: x={accel[0]:.2f}, y={accel[1]:.2f}, z={accel[2]:.2f}")
            return accel
        except Exception as e:
            logger.error(f"Failed to update acceleration: {e}")
            raise
    
    def get_direction_2d(self, accel: Tuple[float, float, float]) -> Tuple[float, float]:
        """
        Convert 3D acceleration to 2D direction vector (x, y plane).
        
        Parameters:
            accel: Acceleration vector (x, y, z)
            
        Returns:
            Tuple[float, float]: Normalized 2D direction vector (x, y)
        """
        x, y, z = accel
        
        # Project onto x-y plane (ignore z/gravity for 2D arrow)
        # Normalize the 2D vector
        magnitude = math.sqrt(x * x + y * y)
        if magnitude < 0.001:  # Avoid division by zero
            return (0.0, 0.0)
        
        return (x / magnitude, y / magnitude)
    
    def generate_display_content(self, accel: Tuple[float, float, float]) -> DisplayContent:
        """
        Generate display content with arrow direction from acceleration.
        
        Parameters:
            accel: Acceleration vector (x, y, z)
            
        Returns:
            DisplayContent: Display content with arrow direction info
        """
        # Get 2D direction
        dir_x, dir_y = self.get_direction_2d(accel)
        
        # Calculate angle in degrees (0 = right, 90 = up, 180 = left, 270 = down)
        angle_rad = math.atan2(dir_y, dir_x)
        angle_deg = math.degrees(angle_rad)
        
        # Store direction info in text field (will be used by UI to draw arrow)
        direction_info = f"{angle_deg:.1f},{dir_x:.2f},{dir_y:.2f}"
        
        # Use a neutral background color
        return DisplayContent(
            mode="imu",
            color=(255, 255, 255),  # White arrow
            background_color=(32, 32, 32),  # Dark gray background
            text=direction_info  # Store angle and direction for UI
        )
    
    def update_display(self, lcd) -> None:
        """
        Update LCD display based on current acceleration.
        
        Parameters:
            lcd: LCDInterface instance to update
        """
        try:
            # Read acceleration
            accel = self.update_acceleration()
            
            # Generate display content
            content = self.generate_display_content(accel)
            
            # Update LCD display
            lcd.update_display(content)
            
            logger.info(f"Display updated: accel=({accel[0]:.2f}, {accel[1]:.2f}, {accel[2]:.2f})")
        except Exception as e:
            logger.error(f"Failed to update display: {e}")
            raise
