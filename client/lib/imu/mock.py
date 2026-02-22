"""Mock implementation of IMUInterface for testing."""

import random
import math
from typing import Tuple
from client.lib.imu.interface import IMUInterface
from client.lib import HardwareError


class IMUMock(IMUInterface):
    """Mock IMU implementation for testing and desktop prototyping."""
    
    def __init__(self, initial_x: float = 0.0, initial_y: float = 0.0, initial_z: float = 9.8):
        """
        Initialize mock IMU with optional initial acceleration values.
        
        Parameters:
            initial_x: Starting X acceleration (m/s²), defaults to 0.0
            initial_y: Starting Y acceleration (m/s²), defaults to 0.0
            initial_z: Starting Z acceleration (m/s²), defaults to 9.8 (gravity)
        """
        self._accel_x = initial_x
        self._accel_y = initial_y
        self._accel_z = initial_z
        self._error = False
        self._available = True
        
        # Random walk parameters
        self._step_size = 1.0  # How much acceleration can change per step (m/s²)
        self._min_accel = -20.0  # Minimum acceleration (m/s²)
        self._max_accel = 20.0   # Maximum acceleration (m/s²)
    
    def read_acceleration(self) -> Tuple[float, float, float]:
        """
        Read the current acceleration (mock) with random walk behavior.
        
        Each call performs a random walk step, making the acceleration values
        gradually change over time to simulate real movement.
        
        Returns:
            Tuple[float, float, float]: Acceleration vector (x, y, z) in m/s²
        """
        if self._error:
            raise HardwareError("Mock IMU error")
        if not self._available:
            raise HardwareError("Mock IMU not available")
        
        # Perform random walk step for each axis
        change_x = random.uniform(-self._step_size, self._step_size)
        change_y = random.uniform(-self._step_size, self._step_size)
        change_z = random.uniform(-self._step_size, self._step_size)
        
        # Update values
        self._accel_x = max(self._min_accel, min(self._max_accel, self._accel_x + change_x))
        self._accel_y = max(self._min_accel, min(self._max_accel, self._accel_y + change_y))
        self._accel_z = max(self._min_accel, min(self._max_accel, self._accel_z + change_z))
        
        return (self._accel_x, self._accel_y, self._accel_z)
    
    def is_available(self) -> bool:
        """Check if mock IMU is available."""
        return self._available
    
    def set_acceleration(self, x: float, y: float, z: float) -> None:
        """Set the mock acceleration values (for testing)."""
        self._accel_x = x
        self._accel_y = y
        self._accel_z = z
    
    def set_error(self, error: bool) -> None:
        """Set error state (for testing)."""
        self._error = error
    
    def set_available(self, available: bool) -> None:
        """Set availability state (for testing)."""
        self._available = available
