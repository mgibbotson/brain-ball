"""Light interaction logic for photoresistor and LCD display."""

import logging
from client.lib.photoresistor.interface import PhotoresistorInterface
from client.lib.lcd.interface import LCDInterface
from client.app.light_state import LightState
from client.app.display_content import DisplayContent

logger = logging.getLogger(__name__)

# Default thresholds for light detection
DARK_THRESHOLD = 20000  # Below this value = dark
LIGHT_THRESHOLD = 45000  # Above this value = light


class LightInteraction:
    """Manages interaction between photoresistor and LCD display."""
    
    def __init__(self, photoresistor: PhotoresistorInterface, lcd: LCDInterface):
        """
        Initialize light interaction.
        
        Parameters:
            photoresistor: PhotoresistorInterface instance
            lcd: LCDInterface instance
        """
        self.photoresistor = photoresistor
        self.lcd = lcd
        self.current_state = None
        self.dark_threshold = DARK_THRESHOLD
        self.light_threshold = LIGHT_THRESHOLD
    
    def update_light_state(self) -> LightState:
        """
        Read photoresistor and create LightState.
        
        Returns:
            LightState: Current light state
            
        Raises:
            HardwareError: If photoresistor read fails
        """
        try:
            raw_value = self.photoresistor.read_light_value()
            normalized = raw_value / 65535.0
            
            # Determine dark/light state
            is_dark = raw_value < self.dark_threshold
            is_light = raw_value > self.light_threshold
            
            state = LightState(
                value=raw_value,
                normalized=normalized,
                is_dark=is_dark,
                is_light=is_light
            )
            
            self.current_state = state
            logger.debug(f"Light state updated: value={raw_value}, is_dark={is_dark}, is_light={is_light}")
            
            return state
        except Exception as e:
            logger.error(f"Failed to update light state: {e}")
            raise
    
    def generate_display_content(self, state: LightState) -> DisplayContent:
        """
        Generate display content from light state.
        
        Parameters:
            state: LightState to convert
            
        Returns:
            DisplayContent: Display content for LCD
        """
        if state.is_dark:
            mode = "dark"
            color = (255, 255, 255)  # White text
            background_color = (0, 0, 0)  # Black background
            text = "DARK"
        elif state.is_light:
            mode = "light"
            color = (0, 0, 0)  # Black text
            background_color = (255, 255, 255)  # White background
            text = "LIGHT"
        else:
            mode = "transitioning"
            color = (128, 128, 128)  # Gray text
            background_color = (64, 64, 64)  # Dark gray background
            text = "TRANSITIONING"
        
        return DisplayContent(
            mode=mode,
            color=color,
            background_color=background_color,
            text=text
        )
    
    def update_display(self) -> None:
        """Update LCD display based on current light state."""
        try:
            # Read light state
            state = self.update_light_state()
            
            # Generate display content
            content = self.generate_display_content(state)
            
            # Update LCD display
            self.lcd.update_display(content)
            
            logger.info(f"Display updated: mode={content.mode}, value={state.value}")
        except Exception as e:
            logger.error(f"Failed to update display: {e}")
            # Gracefully handle errors - don't crash
            raise
