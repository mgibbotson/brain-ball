"""Hardware abstraction libraries for embedded devices."""

# Base error types
class HardwareError(Exception):
    """Base exception for hardware-related errors."""
    pass


class UIError(Exception):
    """Base exception for UI-related errors."""
    pass
