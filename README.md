# Interactive Kids Device - Brain Ball

An interactive embedded device application where children interact with sensors and receive visual/audio feedback.

## Crawl Phase (MVP)

The current implementation focuses on the **crawl phase** - the absolute minimum viable feature:
- Single sensor: Photoresistor (light sensor)
- Single output: LCD display
- Simple interaction: Child covers/exposes photoresistor, device responds with visual feedback

## Hardware

- Raspberry Pi Zero W
- Photoresistor (with 10kΩ resistor for voltage divider circuit)
- Adafruit 2.8" TFT LCD Display (Product 6178 - ILI9341)

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
- SPI interface enabled (`sudo raspi-config` → Interface Options → SPI → Enable)

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
   
   The `-e` flag installs the package in "editable" mode, allowing Python to find the `src` module.

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

**Note**: Use `python -m src.app.main` instead of `python src/app/main.py` to ensure Python can find the `src` module. Alternatively, use the `brain-ball` command after installing with `pip install -e .`.

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

## Future Phases

- **Walk Phase**: Add audio feedback (speaker)
- **Run Phase**: Add additional sensors (microphone, IMU) and complex interactions
