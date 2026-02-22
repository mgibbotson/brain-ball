# Interactive Kids Device - Brain Ball

An interactive embedded device application where children interact with sensors and receive visual/audio feedback.

## Features

### Current Implementation

**Crawl Phase (MVP)**:
- Single sensor: Photoresistor (light sensor)
- Single output: LCD display
- Simple interaction: Child covers/exposes photoresistor, device responds with visual feedback

**Voice-Activated Image Display**:
- Microphone input with offline speech recognition (Vosk)
- Voice-to-image matching using semantic vector embeddings
- Stardew Valley-style 16x16 pixel art sprites
- Two test modes:
  - `--test mic`: Speech-to-text only (for testing recognition)
  - `--test farm`: Full pipeline (speech-to-text → image display)
  - `--test screen`: Cycles through 10 animal images (no mic)

## Hardware

- Raspberry Pi Zero W
- Photoresistor (with 10kΩ resistor for voltage divider circuit)
- SPI TFT display: **ILI9341** (320x240) or **Adafruit 1.28" 240x240 Round TFT - GC9A01A** (EYESPI). For the round display set `DISPLAY_TYPE=gc9a01a`.
- Microphone (USB microphone for desktop, I2S microphone for device)

### Hardware Connections

**Photoresistor:**
- Connect photoresistor to 3.3V pin
- Connect other leg to GPIO pin (e.g., MCP3008 channel 0) via 10kΩ resistor to ground
- This creates a voltage divider circuit

**LCD Display:**
- Connect via SPI (matches default in software):
  - VCC → 3.3V (Pin 1)
  - GND → GND (Pin 6)
  - SCK → GPIO 11 / Physical 23
  - MOSI → GPIO 10 / Physical 19
  - MISO → GPIO 9 / Physical 21 (optional for display)
  - TFTCS (CS) → GPIO 22 / Physical 15
  - RST → GPIO 27 / Physical 13
  - DC → GPIO 17 / Physical 11
  - Backlight (BL) → GPIO 13 / Physical 33 (optional)

For the **1.28" 240x240 Round TFT (GC9A01A, EYESPI)** use the same SPI pins; set before running:
`export DISPLAY_TYPE=gc9a01a`

*Pin assignments are in `client/lib/lcd/hardware.py`; adjust there if your wiring differs.*

**IMU (SparkFun 9DoF ICM-20948, Qwiic):**
- GND → GND
- VIN (V+) → 5V
- DA (SDA) → Physical 3 (GPIO 2 / SDA1)
- CL (SCL) → Physical 5 (GPIO 3 / SCL1)

Enable **I2C**: `sudo raspi-config` → Interface Options → I2C → Yes, then reboot. Use `--test imu` with `--backend device` to run the IMU arrow on the LCD.

## Setup

### Prerequisites

- Raspberry Pi Zero W with Raspberry Pi OS installed
- **Python 3.11 or higher** (required)
- Hardware components connected (see hardware connections above)
- **SPI enabled** (required for LCD): run `sudo raspi-config` → **Interface Options** → **SPI** → **Yes**, then **reboot**. After reboot, `ls /dev/spidev*` should show `/dev/spidev0.0` and `/dev/spidev0.1`.

**For macOS users (voice features)**:
- PortAudio library (required for `pyaudio`):
  ```bash
  brew install portaudio
  ```

### Installation

1. Clone this repository
2. **Create a virtual environment with Python 3.11 or higher:**
   
   **If you have pyenv or multiple Python versions:**
   ```bash
   # Check available Python versions
   python3.11 --version  # Should show 3.11.x or higher
   
   # Create venv with Python 3.11
   python3.11 -m venv venv
   source venv/bin/activate
   ```
   
   **Or if your default python3 is 3.11+:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   **Verify you're using the correct Python version:**
   ```bash
   python --version  # Should show 3.11.x or higher
   ```

3. Install dependencies and install the package:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```
   
   **Note for macOS users**: If `pyaudio` installation fails, ensure PortAudio is installed first (see Prerequisites above).
   
   The `-e` flag installs the package in "editable" mode, allowing Python to find the `client` module.

   **Raspberry Pi: low disk space**  
   If `pip install -r requirements.txt` fails with `OSError: [Errno 28] No space left on device` (e.g. when downloading scipy), either free space or use the minimal device requirements (no voice→image farm mode on device):

   ```bash
   # Option A: Free space, then install full requirements
   pip cache purge
   df -h /                    # check free space (aim for ~500MB+ free)
   sudo journalctl --vacuum-size=50M   # shrink logs
   # Remove other unused software if needed, then:
   pip install -r requirements.txt
   pip install -e .
   ```

   ```bash
   # Option B: Minimal install (no sentence-transformers/scipy) – screen test, mic, light/IMU only
   pip install -r requirements-device.txt
   pip install -e .
   ```

   With Option B you can run `--backend device`, `--test screen`, `--test mic`, and light/IMU; farm mode (voice→image) requires the full `requirements.txt`.

4. **Download Stardew Valley sprites** (required for farm mode):
   ```bash
   python scripts/download_sprites.py
   ```
   
   This attempts to download farm animal sprites from public repositories. If automatic download fails, you can:
   - Extract sprites from your Stardew Valley game files (if you own the game)
   - Manually place 16x16 PNG files in `sprites/FarmAnimals/` with filenames: `cow.png`, `pig.png`, `chicken.png`, `sheep.png`, `horse.png`, `duck.png`, `goat.png`
   
   **Note**: Stardew Valley sprites are copyrighted by ConcernedApe. Ensure you have rights to use them for your project.

5. **Download Vosk speech recognition model** (required for voice features):
   ```bash
   python scripts/download_vosk_model.py
   ```
   
   This downloads the lightweight `vosk-model-small-en-us-0.15` model (suitable for Raspberry Pi Zero W) to the `vosk-model/` directory.
   
   **Alternative**: If the scripts don't work, manually download from [Vosk Models](https://alphacephei.com/vosk/models) and extract to `vosk-model/` directory.

**Sprite Assets**: The application expects Stardew Valley sprite PNG files (16x16 pixels) in the `sprites/FarmAnimals/` directory. You can:
- Extract sprites from Stardew Valley game files (if you own the game)
- Use sprite extraction tools or modding resources
- The application will automatically resize sprites to 16x16 if needed

### Running the Application

**On Device (Raspberry Pi)**:
```bash
python -m client.app.main --backend device
# Or: brain-ball --backend device
```

**On Desktop (Prototyping)**:
```bash
python -m client.app.main --backend desktop
# Or: brain-ball --backend desktop
```

**Backend API (text-to-animal)**: To offload text-to-animal to the backend, set the backend base URL and run the client. When the backend is unreachable, the client shows "Backend unavailable" and a random animal (FR-011).
```bash
export BRAIN_BALL_API_URL=http://<host-ip>:8080   # e.g. http://192.168.1.100:8080
python -m client.app.main --backend desktop --test farm
```
See `specs/003-backend-monorepo/quickstart.md` for same-LAN setup.

**Voice Features** (requires Vosk model):
```bash
# Speech-to-text only mode (test recognition)
python -m client.app.main --backend desktop --test mic

# Full pipeline: speech-to-text → image display
python -m client.app.main --backend desktop --test farm

# Cycle through 10 animal images (screen test)
python -m client.app.main --backend desktop --test screen
```

**Note**: Use `python -m client.app.main` instead of `python client/app/main.py` to ensure Python can find the `client` module. Alternatively, use the `brain-ball` command after installing with `pip install -e .`.

### Raspberry Pi: LCD / SPI errors

If you see **`/dev/spidev0.0 does not exist`** or **`Falling back from lgpio`** / **`failed to import spidev`**:

1. **Enable SPI and reboot**  
   `sudo raspi-config` → **Interface Options** → **SPI** → **Yes** → Finish → **Reboot**.  
   After reboot: `ls /dev/spidev*` should list `spidev0.0` and `spidev0.1`.

2. **Install SPI/Pin packages in your venv** (so Blinka/gpiozero can use the display):
   ```bash
   pip install spidev lgpio
   ```
   If you used `requirements-device.txt`, these are already included; re-run `pip install -r requirements-device.txt` to be sure.

### Display changes but shows nothing meaningful

If the backlight or something changes but you don’t see a clear image:

1. **Run the LCD test script** (on the Pi) to cycle solid red, green, blue, white and draw a simple pattern:
   ```bash
   python scripts/test_lcd.py
   ```
   If you see solid colors and a rectangle/border, wiring and SPI are fine; try rotation (below). If you see nothing, double-check wiring and SPI.

2. **Use the correct display type** – For the **Adafruit 1.28" 240x240 Round TFT (GC9A01A)** set `DISPLAY_TYPE=gc9a01a` before running (same pins; driver and size differ from ILI9341).

3. **Try rotation** – Many boards are mounted 180° or 90°. Set before running:
   ```bash
   export LCD_ROTATION=180
   python scripts/test_lcd.py
   # or
   python -m client.app.main --backend device --test screen
   ```
   Use `0`, `90`, `180`, or `270` until the image is right-side up.

4. **Colors wrong (e.g. red/blue swapped)** – The driver uses RGB; some panels expect BGR. If needed, we can add a BGR option to the LCD hardware.

## Project Structure

```
client/
├── lib/           # Hardware abstraction libraries
├── ui/            # UI backends (desktop + device)
├── app/           # Application logic
└── playground/    # Interactive testing tools

tests/
├── unit/          # Unit tests
├── integration/   # Integration tests
└── playground/    # Playground examples
```

## Development

See `specs/001-interactive-kids-device/quickstart.md` for detailed setup instructions.

## Voice Features

The voice-activated image display feature uses:
- **Vosk**: Offline speech recognition (no internet required)
- **Sentence Transformers**: Semantic word-to-image matching using vector embeddings
- **Pixel Art**: Stardew Valley-style 16x16 sprites for farm animals

### Supported Animals

The system recognizes words and sounds for:
- Cow (words: "cow", "cattle", "bovine", "moo", "mooing")
- Pig (words: "pig", "swine", "hog", "oink", "oinking", "snort")
- Chicken (words: "chicken", "hen", "rooster", "cluck", "clucking", "bawk")
- Sheep (words: "sheep", "lamb", "ewe", "ram", "baa", "baaing", "bleat")
- Horse (words: "horse", "pony", "mare", "stallion", "neigh", "whinny")

The system uses semantic matching, so saying "moo" will display a cow, "oink" will display a pig, etc.

## Future Phases

- **Walk Phase**: Add audio feedback (speaker)
- **Run Phase**: Additional sensors and complex interactions
