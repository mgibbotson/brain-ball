# Implementation Plan: Interactive Kids Device - Crawl Phase

**Branch**: `001-interactive-kids-device` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-interactive-kids-device/spec.md`

## Summary

Build a simple interactive embedded device application where children interact with a photoresistor and receive visual feedback on an LCD display. This is the crawl phase - the absolute minimum viable feature using a single sensor (photoresistor) and single output (LCD display). The application will be built in Python with modular hardware abstraction libraries, a UI library that supports both desktop prototyping and device deployment, and interactive playgrounds for independent device testing.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: 
- `adafruit-circuitpython-ili9341` (LCD display)
- `adafruit-blinka` (CircuitPython compatibility on Raspberry Pi)
- `RPi.GPIO` or `gpiozero` (GPIO control)
- `spidev` or `adafruit-circuitpython-busdevice` (SPI/I2C communication)
- `pytest` (testing framework)
- `pytest-mock` (mocking for hardware abstraction)

**Storage**: N/A (no persistent data storage required for crawl phase)  
**Testing**: pytest with hardware mocks, interactive playgrounds for device testing  
**Target Platform**: Raspberry Pi Zero W (Linux ARM), Desktop (Linux/macOS/Windows for prototyping)  
**Project Type**: Single embedded application  
**Performance Goals**: Display updates within 1 second of light level change detection  
**Constraints**: 
- Raspberry Pi Zero W resource limitations (512MB RAM, single core)
- Must operate without network connectivity
- Must handle sensor failures gracefully
- Desktop prototyping must match device behavior

**Scale/Scope**: 
- Single user interaction (one child at a time)
- Single sensor input (photoresistor)
- Single output (LCD display)
- Crawl phase only - minimal feature set

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Crawl-Walk-Run (NON-NEGOTIABLE)
✅ **PASS**: This plan implements the crawl phase only - single sensor (photoresistor), single interaction, single response (LCD display). No additional features planned.

### II. Simplicity First
✅ **PASS**: Using standard Python libraries and well-established hardware abstraction patterns. No custom frameworks or over-engineering.

### III. Modular Architecture
✅ **PASS**: Each hardware device will have its own library module with clear interfaces. Hardware abstraction enables testing without physical hardware.

### IV. Clear and Readable Code
✅ **PASS**: Python's readability, small focused functions, descriptive naming conventions.

### V. Hardware Abstraction Layer
✅ **PASS**: All hardware interactions will go through abstraction interfaces. Mock implementations will be provided for desktop testing and unit tests.

**Gate Status**: ✅ ALL GATES PASS

## Project Structure

### Documentation (this feature)

```text
specs/001-interactive-kids-device/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── lib/
│   ├── __init__.py
│   ├── photoresistor/
│   │   ├── __init__.py
│   │   ├── interface.py          # Abstract interface
│   │   ├── hardware.py            # Raspberry Pi implementation
│   │   └── mock.py                # Mock for testing
│   ├── lcd/
│   │   ├── __init__.py
│   │   ├── interface.py           # Abstract interface
│   │   ├── hardware.py            # Adafruit ILI9341 implementation
│   │   └── mock.py                # Mock for testing
│   ├── microphone/                # Future: Walk phase
│   ├── speaker/                    # Future: Walk phase
│   └── imu/                       # Future: Run phase
├── ui/
│   ├── __init__.py
│   ├── interface.py               # Abstract UI interface
│   ├── desktop.py                 # Desktop backend (Pygame/Tkinter)
│   └── device.py                  # Device backend (LCD display)
├── app/
│   ├── __init__.py
│   ├── main.py                    # Main application loop
│   └── light_interaction.py       # Crawl phase interaction logic
└── playground/
    ├── __init__.py
    ├── photoresistor_playground.py    # Interactive testing for photoresistor
    └── lcd_playground.py              # Interactive testing for LCD

tests/
├── unit/
│   ├── test_photoresistor.py
│   ├── test_lcd.py
│   └── test_light_interaction.py
├── integration/
│   └── test_hardware_integration.py
└── playground/
    └── test_playground_examples.py
```

**Structure Decision**: Single project structure with modular libraries. Each hardware device gets its own library module with interface, hardware implementation, and mock. UI library supports both desktop (for prototyping) and device (for deployment) backends. Interactive playgrounds allow independent device testing without the full application.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - all constitution principles are satisfied.
