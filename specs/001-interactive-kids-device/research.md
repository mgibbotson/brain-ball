# Research: Interactive Kids Device - Crawl Phase

**Date**: 2026-01-07  
**Phase**: Crawl (MVP)

## Hardware Components

### Photoresistor
- **Decision**: Use analog-to-digital converter (ADC) via GPIO pin on Raspberry Pi Zero W
- **Rationale**: Raspberry Pi Zero W has built-in ADC capabilities. Photoresistor requires voltage divider circuit with 10kΩ resistor. Simple analog reading approach.
- **Alternatives considered**: 
  - I2C ADC breakout board (adds complexity, not needed for single sensor)
  - Digital light sensor (more expensive, less educational value)

### LCD Display (Adafruit 2.8" TFT - Product 6178)
- **Decision**: Use Adafruit CircuitPython ILI9341 library via SPI interface
- **Rationale**: Adafruit provides well-maintained Python libraries. ILI9341 is a common TFT controller with good documentation. SPI is straightforward for embedded systems.
- **Alternatives considered**:
  - I2C OLED display (smaller, simpler but less visual impact)
  - HDMI output (requires external monitor, not self-contained)

### Python Libraries for Hardware

#### GPIO Control
- **Decision**: Use `gpiozero` library
- **Rationale**: High-level, Pythonic interface. Better error handling than RPi.GPIO. Supports both GPIO and ADC operations.
- **Alternatives considered**:
  - `RPi.GPIO` (lower-level, more verbose)
  - `adafruit-blinka` (CircuitPython compatibility, but gpiozero is simpler for basic GPIO)

#### LCD Display Library
- **Decision**: Use `adafruit-circuitpython-ili9341` with `adafruit-blinka`
- **Rationale**: Official Adafruit library, well-maintained, good documentation. Works with CircuitPython ecosystem.
- **Alternatives considered**:
  - Direct SPI communication (too low-level, error-prone)
  - Custom library (reinventing the wheel)

#### Hardware Abstraction
- **Decision**: Create custom interface classes with hardware and mock implementations
- **Rationale**: Enables desktop prototyping and unit testing without hardware. Follows constitution principle V (Hardware Abstraction Layer).
- **Alternatives considered**:
  - Direct hardware calls (violates constitution, prevents testing)
  - Third-party abstraction library (adds dependency, may not fit our needs)

## UI Library Architecture

### Desktop Backend
- **Decision**: Use Pygame for desktop prototyping
- **Rationale**: Simple 2D graphics, can simulate LCD display easily. Cross-platform. Good for prototyping visual feedback.
- **Alternatives considered**:
  - Tkinter (more complex for graphics, better for forms)
  - PyQt/PySide (overkill for simple display simulation)
  - Web-based (adds complexity, requires browser)

### Device Backend
- **Decision**: Use Adafruit ILI9341 library directly
- **Rationale**: Native hardware support, optimized for embedded systems. Matches hardware choice.
- **Alternatives considered**:
  - Framebuffer approach (lower-level, more complex)
  - Custom driver (reinventing the wheel)

### UI Abstraction
- **Decision**: Create abstract UI interface with desktop and device implementations
- **Rationale**: Allows same application code to run on desktop (prototyping) and device (deployment). Follows modular architecture principle.
- **Alternatives considered**:
  - Separate applications (code duplication, maintenance burden)
  - Configuration-based switching (less explicit, harder to debug)

## Testing Strategy

### Unit Testing
- **Decision**: Use pytest with hardware mocks
- **Rationale**: Standard Python testing framework. Mocks allow testing without hardware. Fast feedback loop.
- **Alternatives considered**:
  - unittest (more verbose, less features)
  - Hardware-in-the-loop only (slow, requires hardware availability)

### Interactive Playgrounds
- **Decision**: Create standalone Python scripts that allow interactive testing of individual devices
- **Rationale**: Enables independent device testing without full application. Useful for debugging hardware issues. Follows modular architecture.
- **Alternatives considered**:
  - Full application only (harder to isolate issues)
  - Jupyter notebooks (adds dependency, less portable)

## Development Environment

### Python Version
- **Decision**: Python 3.11+
- **Rationale**: Modern Python features, good performance. Compatible with all required libraries. Raspberry Pi OS supports it.
- **Alternatives considered**:
  - Python 3.9 (older, missing some features)
  - Python 3.12+ (may have compatibility issues with some libraries)

### Dependency Management
- **Decision**: Use requirements.txt with pip
- **Rationale**: Simple, standard Python approach. Works well for single project.
- **Alternatives considered**:
  - Poetry (adds complexity for simple project)
  - Conda (overkill, adds overhead)

## Future Phases (Not Implemented in Crawl)

### Walk Phase Considerations
- Microphone: Adafruit I2S MEMS microphone (Product 3421) - will need I2S interface
- Speaker: Adafruit MAX98357 I2S amplifier (Product 3006) - will need I2S interface
- Audio libraries: `adafruit-circuitpython-audiobusio` for I2S audio

### Run Phase Considerations
- IMU: Sparkfun ICM-20948 9-DOF IMU (Qwiic) - will need I2C interface
- IMU library: `sparkfun-circuitpython-qwiic` or direct I2C communication

## Summary

All technology choices align with constitution principles:
- **Simplicity**: Using standard, well-maintained libraries
- **Modularity**: Each device is a separate library module
- **Hardware Abstraction**: Interfaces enable testing and desktop prototyping
- **Crawl-Walk-Run**: Only implementing crawl phase features

No NEEDS CLARIFICATION items remain - all technical decisions are made.
