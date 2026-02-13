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
- Adafruit 2.8" TFT LCD Display (Product 6178 - ILI9341)
- Microphone (USB microphone for desktop, I2S microphone for device)

### Hardware Connections

**Photoresistor:**
- Connect photoresistor to 3.3V pin
- Connect other leg to GPIO pin (e.g., MCP3008 channel 0) via 10kΩ resistor to ground
- This creates a voltage divider circuit

**LCD Display:**
- Connect via SPI:
  - VCC → 5V
  - GND → GND
  - CS → GPIO 8 (CE0)
  - RST → GPIO 25
  - DC → GPIO 24
  - MOSI → GPIO 10 (MOSI)
  - SCK → GPIO 11 (SCLK)
  - LED → 3.3V (backlight)

*Note: Pin assignments may vary - check LCD product documentation*

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
   
   The `-e` flag installs the package in "editable" mode, allowing Python to find the `src` module.

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
python -m src.app.main --backend device
# Or: brain-ball --backend device
```

**On Desktop (Prototyping)**:
```bash
python -m src.app.main --backend desktop
# Or: brain-ball --backend desktop
```

**Voice Features** (requires Vosk model):
```bash
# Speech-to-text only mode (test recognition)
python -m src.app.main --backend desktop --test mic

# Full pipeline: speech-to-text → image display
python -m src.app.main --backend desktop --test farm

# Cycle through 10 animal images (screen test)
python -m src.app.main --backend desktop --test screen
```

**Note**: Use `python -m src.app.main` instead of `python src/app/main.py` to ensure Python can find the `src` module. Alternatively, use the `brain-ball` command after installing with `pip install -e .`.

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

## Project Structure

```
src/
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
