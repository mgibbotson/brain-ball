"""Hardware implementation of PhotoresistorInterface for Raspberry Pi."""

# Lazy import - only import when actually needed (on Raspberry Pi)

from client.lib.photoresistor.interface import PhotoresistorInterface
from client.lib import HardwareError


class PhotoresistorHardware(PhotoresistorInterface):
    """Hardware implementation for photoresistor on Raspberry Pi."""
    
    # Default GPIO pin for photoresistor (adjust based on hardware setup)
    DEFAULT_PHOTO_PIN = 0  # MCP3008 channel 0
    DEFAULT_THRESHOLD = 50000  # Light threshold value
    
    def __init__(self, pin: int = None):
        """
        Initialize hardware photoresistor.
        
        Parameters:
            pin: MCP3008 channel number (0-7), defaults to 0
        """
        # Lazy import - only import when actually instantiating on Raspberry Pi
        try:
            from gpiozero import MCP3008
        except ImportError as e:
            raise HardwareError(f"gpiozero not available - not running on Raspberry Pi: {e}")
        
        self._pin = pin or self.DEFAULT_PHOTO_PIN
        
        try:
            # Initialize MCP3008 ADC for photoresistor
            # Photoresistor is connected via voltage divider
            self._adc = MCP3008(channel=self._pin)
        except Exception as e:
            raise HardwareError(f"Failed to initialize photoresistor: {e}")
    
    def read_light_value(self) -> int:
        """Read the current light level from hardware."""
        try:
            # MCP3008 returns 0.0-1.0, convert to 0-65535 range
            raw_value = self._adc.value
            light_value = int(raw_value * 65535)
            return light_value
        except Exception as e:
            raise HardwareError(f"Failed to read photoresistor: {e}")
    
    def is_available(self) -> bool:
        """Check if hardware photoresistor is available."""
        try:
            # Try to read a value to verify hardware is responsive
            _ = self.read_light_value()
            return True
        except HardwareError:
            return False
