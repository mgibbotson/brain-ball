# Quickstart Guide: Interactive Kids Device - Crawl Phase

**Date**: 2026-01-07  
**Phase**: Crawl (MVP)

## Prerequisites

- Raspberry Pi Zero W with Raspberry Pi OS installed
- Python 3.11 or higher
- Hardware components:
  - Photoresistor with 10kΩ resistor (voltage divider circuit)
  - Adafruit 2.8" TFT LCD Display (Product 6178)
  - Jumper wires for connections

## Installation

### 1. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev python3-venv
sudo apt-get install -y libgpiod-dev  # For GPIO access
```

### 2. Enable SPI Interface

```bash
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable
```

### 3. Create Virtual Environment

```bash
cd /path/to/brain-ball
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `adafruit-circuitpython-ili9341`
- `adafruit-blinka`
- `gpiozero`
- `pytest` (for testing)

## Hardware Setup

### Photoresistor Connection

1. Connect photoresistor to 3.3V pin
2. Connect other leg to GPIO pin (e.g., GPIO26) via 10kΩ resistor to ground
3. This creates a voltage divider circuit

### LCD Display Connection

Connect LCD to Raspberry Pi via SPI (matches `src/lib/lcd/hardware.py`):
- VCC → 3.3V (Pin 1)
- GND → GND (Pin 6)
- SCK → GPIO 11 (Physical 23)
- MOSI → GPIO 10 (Physical 19)
- TFTCS (CS) → GPIO 22 (Physical 15)
- RST → GPIO 27 (Physical 13)
- DC → GPIO 17 (Physical 11)
- Backlight → GPIO 13 (Physical 33), optional

*Note: To use different pins, edit pin assignments in `src/lib/lcd/hardware.py`.*

## Running the Application

### On Device (Raspberry Pi)

```bash
python src/app/main.py --backend device
```

### On Desktop (Prototyping)

```bash
python src/app/main.py --backend desktop
```

## Testing Individual Devices

### Test Photoresistor

```bash
python src/playground/photoresistor_playground.py
```

This interactive playground allows you to:
- Read light values in real-time
- Test different light conditions
- Verify hardware connections

### Test LCD Display

```bash
python src/playground/lcd_playground.py
```

This interactive playground allows you to:
- Display test patterns
- Test different colors and text
- Verify display functionality

## Running Tests

### Unit Tests (with mocks)

```bash
pytest tests/unit/
```

### Integration Tests (requires hardware)

```bash
pytest tests/integration/
```

## Troubleshooting

### Photoresistor not reading values
- Check voltage divider circuit connections
- Verify GPIO pin number matches code
- Test with multimeter to confirm voltage changes

### LCD display not showing content
- Verify SPI is enabled (`lsmod | grep spi`)
- Check all SPI connections
- Verify pin assignments match code
- Test with `src/playground/lcd_playground.py`

### Permission errors
- Add user to `gpio` group: `sudo usermod -a -G gpio $USER`
- Log out and back in for group changes to take effect

## Next Steps

Once crawl phase is working:
- **Walk Phase**: Add audio feedback (speaker) in response to light changes
- **Run Phase**: Add additional sensors (microphone, IMU) and complex interactions
