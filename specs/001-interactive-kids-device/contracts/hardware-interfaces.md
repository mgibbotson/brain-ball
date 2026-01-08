# Hardware Interface Contracts: Interactive Kids Device - Crawl Phase

**Date**: 2026-01-07  
**Phase**: Crawl (MVP)

## Photoresistor Interface

### Interface: `PhotoresistorInterface`

Abstract base class defining the contract for photoresistor hardware.

**Methods**:

#### `read_light_value() -> int`
Reads the current light level from the photoresistor.

**Returns**: 
- `int`: Raw ADC value (0-65535 or device-specific range)

**Raises**:
- `HardwareError`: If sensor is unresponsive or hardware failure occurs
- `IOError`: If communication with hardware fails

**Contract**:
- Must return a non-negative integer
- Must raise `HardwareError` if sensor cannot be read
- Should handle transient errors gracefully (retry logic in implementation)

#### `is_available() -> bool`
Checks if the photoresistor hardware is available and responsive.

**Returns**:
- `bool`: True if hardware is available, False otherwise

**Contract**:
- Must return False if hardware is not connected or unresponsive
- Should not raise exceptions (safe to call anytime)

## LCD Display Interface

### Interface: `LCDInterface`

Abstract base class defining the contract for LCD display hardware.

**Methods**:

#### `initialize() -> None`
Initializes the LCD display hardware.

**Raises**:
- `HardwareError`: If display cannot be initialized
- `IOError`: If communication with hardware fails

**Contract**:
- Must be called before any other methods
- Must raise `HardwareError` if initialization fails
- Should be idempotent (safe to call multiple times)

#### `clear() -> None`
Clears the entire display.

**Raises**:
- `HardwareError`: If display is not initialized or hardware failure occurs

**Contract**:
- Must clear all pixels on the display
- Should complete within reasonable time (< 100ms)

#### `update_display(content: DisplayContent) -> None`
Updates the display with new content.

**Parameters**:
- `content` (DisplayContent): The content to display

**Raises**:
- `HardwareError`: If display is not initialized or hardware failure occurs
- `ValueError`: If content is invalid

**Contract**:
- Must update display within 1 second (per spec requirement SC-002)
- Must handle invalid content gracefully (raise ValueError)
- Should not block for extended periods

#### `is_available() -> bool`
Checks if the LCD display hardware is available and responsive.

**Returns**:
- `bool`: True if hardware is available, False otherwise

**Contract**:
- Must return False if hardware is not connected or unresponsive
- Should not raise exceptions (safe to call anytime)

## UI Interface

### Interface: `UIInterface`

Abstract base class defining the contract for UI backends (desktop and device).

**Methods**:

#### `initialize() -> None`
Initializes the UI backend.

**Raises**:
- `UIError`: If UI cannot be initialized

**Contract**:
- Must be called before any other methods
- Should be idempotent (safe to call multiple times)

#### `render(content: DisplayContent) -> None`
Renders content to the display.

**Parameters**:
- `content` (DisplayContent): The content to render

**Raises**:
- `UIError`: If rendering fails
- `ValueError`: If content is invalid

**Contract**:
- Must complete rendering within reasonable time
- Must handle invalid content gracefully

#### `update() -> None`
Updates the display (for event loop-based backends like Pygame).

**Contract**:
- Should process any pending UI events
- Should be called regularly in main loop

#### `cleanup() -> None`
Cleans up UI resources.

**Contract**:
- Must be safe to call multiple times
- Should release all resources

## Error Types

### `HardwareError`
Base exception for hardware-related errors.

### `UIError`
Base exception for UI-related errors.

## Mock Implementations

Both `PhotoresistorInterface` and `LCDInterface` must have mock implementations that:
- Implement the full interface contract
- Allow programmatic control for testing
- Simulate hardware behavior (delays, errors, etc.)
- Enable testing without physical hardware
