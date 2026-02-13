"""Main application loop for interactive kids device."""

import argparse
import logging
import sys
import time
import os
import importlib.util
from pathlib import Path
from src.lib.photoresistor.hardware import PhotoresistorHardware
from src.lib.photoresistor.mock import PhotoresistorMock
from src.lib.imu.mock import IMUMock
from src.lib.imu.hardware import IMUHardware
from src.lib.lcd.hardware import LCDHardware
from src.lib.lcd.mock import LCDMock
from src.lib.microphone.hardware import MicrophoneHardware
from src.lib.microphone.mock import RandomWalkMicrophone
from src.ui.desktop import UIDesktop
from src.ui.device import UIDevice
from src.app.light_interaction import LightInteraction
from src.app.imu_interaction import IMUInteraction
from src.app.mic_level_interaction import MicLevelInteraction
from src.app.voice_interaction import VoiceInteraction
from src.app.image_embeddings import create_farm_animal_embeddings
from src.app.display_content import DisplayContent
from src.app.pixel_art import get_pixel_art_image
from src.lib import HardwareError
from src.ui import UIError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# Required animal types for farm mode (sprites organized in subdirectories)
REQUIRED_ANIMAL_TYPES = [
    "cow",
    "pig",
    "chicken",
    "sheep",
    "horse",
    "duck",
    "goat",
    "dog",
    "cat",
]

# Animals to cycle through in --test screen (10 images)
SCREEN_TEST_ANIMALS = [
    "cow", "pig", "chicken", "sheep", "horse",
    "duck", "goat", "dog", "cat", "rabbit",
]
SCREEN_CYCLE_SECONDS = 2.0


def check_vosk_model() -> bool:
    """Check if Vosk model exists.
    
    Returns:
        True if model exists, False otherwise.
    """
    model_file = PROJECT_ROOT / "vosk-model" / "am" / "final.mdl"
    return model_file.exists()


def check_sprites() -> bool:
    """Check if all required animal types have sprites.
    
    Returns:
        True if all animal types have at least one sprite, False otherwise.
    """
    sprites_dir = PROJECT_ROOT / "sprites" / "Animals"
    if not sprites_dir.exists():
        return False
    
    # Check if each animal type has at least one PNG file
    for animal_type in REQUIRED_ANIMAL_TYPES:
        animal_dir = sprites_dir / animal_type
        if not animal_dir.exists() or not list(animal_dir.glob("*.png")):
            return False
    
    return True


def ensure_vosk_model() -> bool:
    """Ensure Vosk model is downloaded, downloading if necessary.
    
    Returns:
        True if model is available, False if download failed.
    """
    if check_vosk_model():
        return True
    
    logger.info("Vosk model not found. Downloading...")
    try:
        # Dynamically import download function
        script_path = PROJECT_ROOT / "scripts" / "download_vosk_model.py"
        spec = importlib.util.spec_from_file_location("download_vosk_model", script_path)
        if spec is None or spec.loader is None:
            raise ImportError("Could not load download_vosk_model module")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        success = module.download_vosk_model(PROJECT_ROOT)
        if success:
            logger.info("Vosk model downloaded successfully")
            return True
        else:
            logger.error("Failed to download Vosk model")
            return False
    except Exception as e:
        logger.error(f"Error downloading Vosk model: {e}")
        logger.info("Please run: python scripts/download_vosk_model.py")
        return False


def ensure_sprites() -> bool:
    """Ensure sprites are downloaded, downloading if necessary.
    
    Returns:
        True if all sprites are available, False if download failed.
    """
    return ensure_sprites_with_progress(project_root=PROJECT_ROOT, ui=None)


def ensure_sprites_with_progress(project_root: Path = None, ui=None) -> bool:
    """Ensure sprites are downloaded, downloading if necessary, with UI progress updates.
    
    Args:
        project_root: Path to project root. If None, uses PROJECT_ROOT.
        ui: Optional UI instance for progress updates (desktop backend only).
    
    Returns:
        True if all sprites are available, False if download failed.
    """
    if project_root is None:
        project_root = PROJECT_ROOT
    
    if check_sprites():
        return True
    
    logger.info("Sprites not found. Downloading...")
    try:
        # Dynamically import download function
        script_path = project_root / "scripts" / "download_sprites.py"
        spec = importlib.util.spec_from_file_location("download_sprites", script_path)
        if spec is None or spec.loader is None:
            raise ImportError("Could not load download_sprites module")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Create a progress callback for UI updates
        def progress_callback(animal_type: str, filename: str, status: str):
            """Callback for download progress updates."""
            logger.info(f"Downloading {animal_type}/{filename}... {status}")
            if ui is not None:
                try:
                    # Update UI with current download status
                    progress_text = f"Downloading\n{animal_type}..."
                    if status == "success":
                        progress_text = f"Downloaded\n{animal_type}"
                    elif status == "failed":
                        progress_text = f"Failed\n{animal_type}"
                    
                    loading_content = DisplayContent(
                        mode="voice",
                        color=(255, 200, 0) if status != "success" else (0, 255, 0),
                        background_color=(32, 32, 32),
                        text=progress_text
                    )
                    ui.render(loading_content)
                    ui.update()
                except Exception:
                    pass  # Don't fail if UI update fails
        
        # Use verbose=True to get better error messages in logs
        success = module.download_sprites(project_root, verbose=True, progress_callback=progress_callback if ui else None)
        
        if success:
            logger.info("All sprites are present")
            if ui is not None:
                try:
                    loading_content = DisplayContent(
                        mode="voice",
                        color=(0, 255, 0),  # Green text
                        background_color=(32, 32, 32),
                        text="Sprites\nready!"
                    )
                    ui.render(loading_content)
                    ui.update()
                    time.sleep(1)  # Show success message briefly
                except Exception:
                    pass
            return True
        else:
            # Check how many animal types we actually have sprites for
            sprites_dir = project_root / "sprites" / "Animals"
            existing_count = sum(
                1 for animal_type in REQUIRED_ANIMAL_TYPES
                if (sprites_dir / animal_type).exists() and list((sprites_dir / animal_type).glob("*.png")))
            if existing_count == 0:
                logger.warning("No sprites found. Farm mode will not work.")
                logger.info("Sprites will be downloaded automatically. Run: python scripts/download_sprites.py for manual download")
            else:
                logger.warning(f"Only {existing_count}/{len(REQUIRED_ANIMAL_TYPES)} animal types have sprites. Farm mode may not work correctly.")
                logger.info("Run: python scripts/download_sprites.py to download missing sprites")
            return False
    except Exception as e:
        logger.error(f"Error downloading sprites: {e}", exc_info=True)
        logger.info("You can manually download sprites by running: python scripts/download_sprites.py")
        return False


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
    parser.add_argument(
        "--test",
        choices=["imu", "mic", "farm", "button", "screen"],
        default="imu",
        help="Test mode: select component to test (IMU, mic, farm, button, or screen to cycle 10 animal images)"
    )
    args = parser.parse_args()
    
    test_mode = args.test.lower() if args.test else None
    logger.info(f"Starting Interactive Kids Device - Backend: {args.backend}" + 
                (f", Test Mode: {args.test}" if args.test else ""))
    
    # Create hardware instances
    try:
        sensor_type, sensor, lcd, ui = create_hardware(args.backend)
    except Exception as e:
        logger.error(f"Failed to create hardware: {e}")
        sys.exit(1)
    
    # Override sensor type if test mode is specified
    if test_mode:
        if test_mode == "imu":
            sensor_type = "imu"
            if args.backend == "desktop":
                sensor = IMUMock()
            else:
                try:
                    sensor = IMUHardware()
                    sensor.initialize()
                    logger.info("Using ICM-20948 IMU hardware")
                except Exception as e:
                    logger.warning("IMU hardware init failed (%s), using mock", e)
                    sensor = IMUMock()
        elif test_mode == "mic" or test_mode == "farm":
            sensor_type = test_mode
            logger.info(f"Microphone test mode: {test_mode}")
            if os.environ.get("MIC_RANDOM_WALK", "").lower() in ("1", "true", "yes"):
                sensor = RandomWalkMicrophone()
                sensor.initialize()
                logger.info("Using random-walk mic input (MIC_RANDOM_WALK)")
            else:
                try:
                    sensor = MicrophoneHardware()
                    sensor.initialize()
                except Exception as e:
                    logger.error(f"Failed to initialize microphone: {e}")
                    sensor = None
        elif test_mode == "button":
            sensor_type = "button"
            logger.info("Button test mode - not yet implemented")
            # TODO: Create button mock/hardware
            sensor = None
        elif test_mode == "screen":
            sensor_type = "screen"
            logger.info("Screen test mode - cycling through 10 animal images")
            sensor = None
    
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
    
    # Show initial loading screen
    if args.backend == "desktop":
        loading_content = DisplayContent(
            mode="voice",
            color=(255, 255, 255),
            background_color=(32, 32, 32),
            text="Loading..."
        )
        ui.render(loading_content)
        ui.update()  # Process events to show the screen
    
    # Check and download required resources for voice modes (farm needs Vosk; mic test does not)
    if sensor_type == "farm":
        if not check_vosk_model():
            if args.backend == "desktop":
                loading_content = DisplayContent(
                    mode="voice",
                    color=(255, 200, 0),  # Orange text
                    background_color=(32, 32, 32),
                    text="Downloading\nspeech model..."
                )
                ui.render(loading_content)
                ui.update()
            
            if not ensure_vosk_model():
                logger.error("Vosk model is required for voice features")
                logger.info("Please run: python scripts/download_vosk_model.py")
                sys.exit(1)
        # Check sprites for farm mode
        if sensor_type == "farm":
            if not check_sprites():
                if args.backend == "desktop":
                    loading_content = DisplayContent(
                        mode="voice",
                        color=(255, 200, 0),  # Orange text
                        background_color=(32, 32, 32),
                        text="Downloading\nsprites..."
                    )
                    ui.render(loading_content)
                    ui.update()
                
                # Download sprites with progress updates
                logger.info("Starting sprite download...")
                if not ensure_sprites_with_progress(project_root=PROJECT_ROOT, ui=ui if args.backend == "desktop" else None):
                    logger.warning("Some sprites may be missing. Farm mode may not work correctly.")
                    logger.info("Please run: python scripts/download_sprites.py")
                    # Continue anyway - some sprites might still work
    
    # Check sprites for screen test (no voice/mic required)
    if sensor_type == "screen":
        if not check_sprites():
            if args.backend == "desktop":
                loading_content = DisplayContent(
                    mode="voice",
                    color=(255, 200, 0),
                    background_color=(32, 32, 32),
                    text="Downloading\nsprites..."
                )
                ui.render(loading_content)
                ui.update()
            logger.info("Starting sprite download...")
            if not ensure_sprites_with_progress(project_root=PROJECT_ROOT, ui=ui if args.backend == "desktop" else None):
                logger.warning("Some sprites may be missing. Screen test may not show all animals.")
                logger.info("Please run: python scripts/download_sprites.py")
    
    # Initialize microphone if in mic/farm mode
    if sensor_type == "mic" or sensor_type == "farm":
        if sensor is not None:
            try:
                sensor.initialize()
            except HardwareError as e:
                logger.warning(f"Microphone initialization failed: {e}")
                # Continue without microphone if it fails
    
    # Create interaction logic based on sensor type
    interaction = None
    try:
        if sensor_type == "imu":
            interaction = IMUInteraction(imu=sensor)
        elif sensor_type == "mic":
            # Mic test: amplitude/level only, no Vosk
            interaction = MicLevelInteraction(microphone=sensor)
            logger.info("Mic test mode: showing voice intensity (no speech-to-text)")
        elif sensor_type == "farm":
            # Show loading screen for farm mode (embedding model takes time to load)
            if args.backend == "desktop":
                loading_content = DisplayContent(
                    mode="voice",
                    color=(255, 255, 0),  # Yellow text
                    background_color=(32, 32, 32),
                    text="Loading AI model..."
                )
                ui.render(loading_content)
                ui.update()
                logger.info("Loading embedding model (this may take a moment)...")
            image_embeddings = None
            try:
                image_embeddings = create_farm_animal_embeddings()
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to create image embeddings: {e}")
                logger.info("Continuing with text-only mode")
            interaction = VoiceInteraction(
                microphone=sensor,
                lcd=lcd,
                image_embeddings=image_embeddings,
                enable_images=True,
            )
            try:
                interaction.start_continuous_recognition()
                logger.info("Continuous voice recognition started")
            except Exception as e:
                logger.error(f"Failed to start continuous recognition: {e}")
                logger.info("Falling back to per-call recognition")
        elif sensor_type == "button":
            logger.warning("Button interaction not yet implemented")
            # TODO: Create button interaction
        else:
            # Default to photoresistor/light interaction
            interaction = LightInteraction(photoresistor=sensor, lcd=lcd)
    except Exception as e:
        logger.error(f"Failed to create interaction: {e}")
        ui.cleanup()
        sys.exit(1)
    
    # Main loop
    logger.info("Starting main loop...")
    running = True
    screen_index = 0
    last_screen_switch = time.monotonic()
    
    try:
        while running:
            # Update UI (handle events for desktop backend)
            ui.update()
            
            # Update display based on sensor
            try:
                if sensor_type == "screen":
                    # Cycle through 10 animal images every SCREEN_CYCLE_SECONDS
                    now = time.monotonic()
                    if now - last_screen_switch >= SCREEN_CYCLE_SECONDS:
                        last_screen_switch = now
                        screen_index = (screen_index + 1) % len(SCREEN_TEST_ANIMALS)
                    animal_key = SCREEN_TEST_ANIMALS[screen_index]
                    image_data = get_pixel_art_image(animal_key)
                    if image_data is not None:
                        content = DisplayContent(
                            mode="voice",
                            color=(255, 255, 255),
                            background_color=(32, 32, 32),
                            text=animal_key,
                            image_data=image_data,
                            image_width=16,
                            image_height=16,
                        )
                    else:
                        content = DisplayContent(
                            mode="voice",
                            color=(255, 200, 0),
                            background_color=(32, 32, 32),
                            text=animal_key or "?",
                        )
                    lcd.update_display(content)
                    if args.backend == "desktop":
                        ui.render(content)
                    time.sleep(0.1)
                    continue
                if interaction is None:
                    logger.warning("No interaction logic available - skipping update")
                    time.sleep(0.1)
                    continue
                    
                if sensor_type == "imu":
                    # IMU interaction
                    accel = interaction.update_acceleration()
                    content = interaction.generate_display_content(accel)
                    lcd.update_display(content)
                    ui.render(content)
                    logger.debug(f"Display: accel=({accel[0]:.2f}, {accel[1]:.2f}, {accel[2]:.2f})")
                elif sensor_type == "mic":
                    # Mic test: level from background thread, no blocking
                    content = interaction.generate_display_content()
                    lcd.update_display(content)
                    ui.render(content)  # required for device LCD and for fallback desktop window
                    time.sleep(0.02)  # ~50 FPS; level updates in background
                elif sensor_type == "farm":
                    word = interaction.recognize_word()
                    content = interaction.generate_display_content(word)
                    if word:
                        logger.debug(f"Display: word={word}, mode={content.mode}")
                    lcd.update_display(content)
                    if args.backend == "desktop":
                        ui.render(content)
                        ui.update()
                    time.sleep(0.05)
                elif sensor_type == "button":
                    # Button interaction (not yet implemented)
                    logger.debug("Button test mode - not yet implemented")
                    time.sleep(0.1)
                    continue
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

            # Delay: mic has its own short sleep for low latency; others use 0.1s
            if sensor_type != "mic":
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
            if interaction and hasattr(interaction, 'stop_continuous_recognition'):
                interaction.stop_continuous_recognition()
            if interaction and hasattr(interaction, 'stop'):
                interaction.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        try:
            ui.cleanup()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        
        logger.info("Application stopped")


if __name__ == "__main__":
    main()
