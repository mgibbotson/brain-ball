"""UI backends for desktop and device deployment."""

from client.lib import HardwareError


class UIError(Exception):
    """Base exception for UI-related errors."""
    pass
