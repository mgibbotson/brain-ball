"""Main application loop for interactive kids device."""

import argparse
import logging
import sys
import time
from src.lib.photoresistor.hardware import PhotoresistorHardware
from src.lib.photoresistor.mock import PhotoresistorMock
from src.lib.lcd.hardware import LCDHardware
from src.lib.lcd.mock import LCDMock
from src.ui.desktop import UIDesktop
from src.ui.device import UIDevice
from src.app.light_interaction import LightInteraction
from src.lib import HardwareError
from src.ui import UIError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_hardware(backend: str):
    """
    Create hardware instances based on backend.
    
    Parameters:
        backend: "desktop" or "device"
        
    Returns:
        tuple: (photoresistor, lcd, ui) instances
    """
    if backend == "desktop":
        # Use mocks for desktop prototyping
        logger.info("Using mock hardware for desktop prototyping")
        photoresistor = PhotoresistorMock(initial_value=32768)
        lcd = LCDMock()
        ui = UIDesktop()
    elif backend == "device":
        # Use real hardware on device
        logger.info("Using real hardware for device deployment")
        try:
            photoresistor = PhotoresistorHardware()
            lcd = LCDHardware()
            ui = UIDevice(lcd)
        except HardwareError as e:
            logger.error(f"Hardware initialization failed: {e}")
            logger.info("Falling back to mock hardware")
            photoresistor = PhotoresistorMock()
            lcd = LCDMock()
            ui = UIDesktop()
    else:
        raise ValueError(f"Unknown backend: {backend}")
    
    return photoresistor, lcd, ui


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="Interactive Kids Device - Crawl Phase")
    parser.add_argument(
        "--backend",
        choices=["desktop", "device"],
        default="desktop",
        help="UI backend to use (default: desktop)"
    )
    args = parser.parse_args()
    
    logger.info(f"Starting Interactive Kids Device - Backend: {args.backend}")
    
    # Create hardware instances
    try:
        photoresistor, lcd, ui = create_hardware(args.backend)
    except Exception as e:
        logger.error(f"Failed to create hardware: {e}")
        sys.exit(1)
    
    # Initialize UI
    try:
        ui.initialize()
    except UIError as e:
        logger.error(f"Failed to initialize UI: {e}")
        sys.exit(1)
    
    # Initialize LCD
    try:
        lcd.initialize()
    except HardwareError as e:
        logger.warning(f"LCD initialization failed: {e}")
        # Continue without LCD if it fails
    
    # Create interaction logic
    try:
        interaction = LightInteraction(photoresistor=photoresistor, lcd=lcd)
    except Exception as e:
        logger.error(f"Failed to create interaction: {e}")
        ui.cleanup()
        sys.exit(1)
    
    # Main loop
    logger.info("Starting main loop...")
    running = True
    
    try:
        while running:
            # Update UI (handle events for desktop backend)
            ui.update()
            
            # Update display based on light sensor
            try:
                interaction.update_display()
            except HardwareError as e:
                logger.warning(f"Hardware error (continuing): {e}")
                # Continue running even if hardware fails
            
            # Small delay to avoid excessive CPU usage
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        running = False
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        running = False
    finally:
        # Cleanup
        logger.info("Cleaning up...")
        try:
            ui.cleanup()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        
        logger.info("Application stopped")


if __name__ == "__main__":
    main()
