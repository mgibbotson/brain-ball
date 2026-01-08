# Data Model: Interactive Kids Device - Crawl Phase

**Date**: 2026-01-07  
**Phase**: Crawl (MVP)

## Entities

### LightState

Represents the current light level detected by the photoresistor.

**Fields**:
- `value` (int): Raw ADC reading from photoresistor (0-65535 or device-specific range)
- `normalized` (float): Normalized value between 0.0 and 1.0
- `is_dark` (bool): True if light level is below dark threshold
- `is_light` (bool): True if light level is above light threshold
- `timestamp` (float): Unix timestamp when reading was taken

**Validation Rules**:
- `value` must be non-negative integer
- `normalized` must be between 0.0 and 1.0 inclusive
- `is_dark` and `is_light` are mutually exclusive (cannot both be True)
- `timestamp` must be positive

**State Transitions**:
- Initial state: `is_dark=False`, `is_light=False` (unknown/initializing)
- When `value` < dark_threshold: `is_dark=True`, `is_light=False`
- When `value` > light_threshold: `is_dark=False`, `is_light=True`
- Threshold values are configurable but default to device-specific ranges

### DisplayContent

Represents the visual feedback shown on the LCD screen.

**Fields**:
- `mode` (str): Display mode - "dark", "light", or "transitioning"
- `text` (str, optional): Text to display (if any)
- `color` (tuple): RGB color tuple (r, g, b) where each value is 0-255
- `background_color` (tuple): RGB background color tuple (r, g, b)
- `update_required` (bool): True if display needs to be refreshed

**Validation Rules**:
- `mode` must be one of: "dark", "light", "transitioning"
- `color` and `background_color` must be tuples of 3 integers, each 0-255
- `text` is optional and may be None or empty string

**State Transitions**:
- When `LightState.is_dark` becomes True: `mode="dark"`, update colors/text accordingly
- When `LightState.is_light` becomes True: `mode="light"`, update colors/text accordingly
- During state change: `mode="transitioning"` (optional, for smooth transitions)

## Relationships

- **LightState → DisplayContent**: One-to-one relationship. Each `LightState` determines the `DisplayContent` to show. When `LightState` changes, `DisplayContent` is updated accordingly.

## Data Flow

1. Photoresistor hardware reads analog value → `LightState.value`
2. `LightState.value` is normalized and thresholds are checked → `LightState.is_dark` / `LightState.is_light`
3. `LightState` changes trigger `DisplayContent` update
4. `DisplayContent` is rendered to LCD display hardware

## Persistence

**None required for crawl phase**. All state is in-memory and ephemeral. No data needs to persist between application runs.

## Future Phases (Not in Crawl)

- **Walk Phase**: May add audio state, interaction history
- **Run Phase**: May add IMU data, multi-sensor fusion, game state
