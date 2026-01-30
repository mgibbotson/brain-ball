"""UI backends for desktop and device deployment."""

from src.lib import HardwareError


class UIError(Exception):
    """Base exception for UI-related errors."""
    pass
