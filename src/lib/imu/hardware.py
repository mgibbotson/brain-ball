"""Hardware implementation of IMUInterface for SparkFun 9DoF IMU (ICM-20948) over I2C."""

import logging
from typing import Tuple

from src.lib.imu.interface import IMUInterface
from src.lib import HardwareError

logger = logging.getLogger(__name__)

# ICM-20948 accelerometer scale: ±2g → 16384 LSB/g → m/s² = raw * (9.80665 / 16384)
ACCEL_SCALE_2G = 9.80665 / 16384.0


class IMUHardware(IMUInterface):
    """
    Hardware IMU using SparkFun 9DoF IMU Breakout - ICM-20948 (Qwiic) over I2C.

    Wiring (Raspberry Pi): DA (SDA) → Physical 3 (GPIO 2), CL (SCL) → Physical 5 (GPIO 3).
    Enable I2C: raspi-config → Interface Options → I2C → Yes, then reboot.
    """

    def __init__(self, i2c_address: int = None):
        """
        Initialize the ICM-20948 over I2C.

        Args:
            i2c_address: I2C address (default 0x69; alternate 0x68). Omit to use library default.
        """
        try:
            from qwiic_icm20948 import QwiicIcm20948
        except ImportError as e:
            raise HardwareError(
                "ICM-20948 driver not installed. Install with: pip install sparkfun-qwiic-icm20948"
            ) from e

        self._sensor = QwiicIcm20948(address=i2c_address)
        self._initialized = False
        self._accel_scale = ACCEL_SCALE_2G

    def initialize(self) -> bool:
        """
        Initialize the ICM-20948 (wake, set ±2g accel range). Call once before use.

        Returns:
            True if init succeeded, False otherwise.
        """
        if self._initialized:
            return True
        if not self._sensor.isConnected():
            raise HardwareError("ICM-20948 not connected. Check I2C wiring (SDA→GPIO2, SCL→GPIO3) and enable I2C.")
        if not self._sensor.begin():
            raise HardwareError("ICM-20948 begin() failed.")
        # Use ±2g full scale for accelerometer (matches ACCEL_SCALE_2G)
        try:
            from qwiic_icm20948 import gpm2
            self._sensor.setFullScaleRangeAccel(gpm2)
        except Exception as e:
            logger.warning("Could not set accel range to ±2g: %s", e)
        self._initialized = True
        logger.info("ICM-20948 IMU initialized")
        return True

    def read_acceleration(self) -> Tuple[float, float, float]:
        """
        Read current acceleration from the ICM-20948.

        Returns:
            (x, y, z) in m/s².

        Raises:
            HardwareError: If sensor not initialized or read fails.
        """
        if not self._initialized:
            self.initialize()
        if not self._sensor.getAgmt():
            raise HardwareError("ICM-20948 getAgmt() failed")
        ax = self._sensor.axRaw * self._accel_scale
        ay = self._sensor.ayRaw * self._accel_scale
        az = self._sensor.azRaw * self._accel_scale
        return (ax, ay, az)

    def is_available(self) -> bool:
        """Return True if the ICM-20948 is connected and initialized."""
        if not self._initialized:
            try:
                return self._sensor.isConnected()
            except Exception:
                return False
        try:
            return self._sensor.isConnected()
        except Exception:
            return False
