"""Main application loop for interactive kids device."""

import argparse
import logging
import sys
import time
from src.lib.photoresistor.hardware import PhotoresistorHardware
from src.lib.photoresistor.mock import PhotoresistorMock
from src.lib.imu.mock import IMUMock
from src.lib.lcd.hardware import LCDHardware
from src.lib.lcd.mock import LCDMock
from src.ui.desktop import UIDesktop
from src.ui.device import UIDevice
from src.app.light_interaction import LightInteraction
from src.app.imu_interaction import IMUInteraction
from src.lib import HardwareError
from src.ui import UIError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def create_hardware(backend: str):
    """
    Create hardware instances based on backend.
    
    Parameters:
        backend: "desktop" or "device"
        
    Returns:
        tuple: (sensor, lcd, ui) instances
        For desktop: (imu, lcd, ui) - uses IMU mock
        For device: (photoresistor, lcd, ui) - uses real hardware
    """
    if backend == "desktop":
        # Use IMU mock for desktop prototyping
        logger.info("Using IMU mock for desktop prototyping")
        imu = IMUMock()
        lcd = LCDMock()
        ui = UIDesktop()
        return ("imu", imu, lcd, ui)
    elif backend == "device":
        # Use real hardware on device
        logger.info("Using real hardware for device deployment")
        try:
            photoresistor = PhotoresistorHardware()
            lcd = LCDHardware()
            ui = UIDevice(lcd)
            return ("photoresistor", photoresistor, lcd, ui)
        except HardwareError as e:
            logger.error(f"Hardware initialization failed: {e}")
            logger.info("Falling back to mock hardware")
            photoresistor = PhotoresistorMock()
            lcd = LCDMock()
            ui = UIDesktop()
            return ("photoresistor", photoresistor, lcd, ui)
    else:
        raise ValueError(f"Unknown backend: {backend}")


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
        sensor_type, sensor, lcd, ui = create_hardware(args.backend)
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
    
    # Create interaction logic based on sensor type
    try:
        if sensor_type == "imu":
            interaction = IMUInteraction(imu=sensor)
        else:
            interaction = LightInteraction(photoresistor=sensor, lcd=lcd)
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
            
            # Update display based on sensor
            try:
                if sensor_type == "imu":
                    # IMU interaction
                    accel = interaction.update_acceleration()
                    content = interaction.generate_display_content(accel)
                    lcd.update_display(content)
                    ui.render(content)
                    logger.debug(f"Display: accel=({accel[0]:.2f}, {accel[1]:.2f}, {accel[2]:.2f})")
                else:
                    # Photoresistor interaction
                    state = interaction.update_light_state()
                    content = interaction.generate_display_content(state)
                    lcd.update_display(content)
                    if args.backend == "desktop":
                        ui.render(content)
                    logger.debug(f"Display: mode={content.mode}, value={state.value}")
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
