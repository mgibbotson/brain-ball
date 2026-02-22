"""LightState entity representing photoresistor readings."""

import time


class LightState:
    """Represents the current light level detected by the photoresistor."""
    
    def __init__(
        self,
        value: int,
        normalized: float,
        is_dark: bool = False,
        is_light: bool = False,
        timestamp: float = None
    ):
        """
        Initialize LightState.
        
        Parameters:
            value: Raw ADC reading from photoresistor (0-65535)
            normalized: Normalized value between 0.0 and 1.0
            is_dark: True if light level is below dark threshold
            is_light: True if light level is above light threshold
            timestamp: Unix timestamp when reading was taken
            
        Raises:
            ValueError: If validation fails
        """
        # Validation
        if value < 0:
            raise ValueError("value must be non-negative")
        if not 0.0 <= normalized <= 1.0:
            raise ValueError("normalized must be between 0.0 and 1.0")
        if is_dark and is_light:
            raise ValueError("is_dark and is_light cannot both be True")
        if timestamp is not None and timestamp <= 0:
            raise ValueError("timestamp must be positive")
        
        self.value = value
        self.normalized = normalized
        self.is_dark = is_dark
        self.is_light = is_light
        self.timestamp = timestamp if timestamp is not None else time.time()
