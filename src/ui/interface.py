"""Abstract interface for UI backends."""

from abc import ABC, abstractmethod
from src.ui import UIError


class UIInterface(ABC):
    """Abstract base class for UI backends (desktop and device)."""
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the UI backend.
        
        Raises:
            UIError: If UI cannot be initialized
        """
        pass
    
    @abstractmethod
    def render(self, content) -> None:
        """
        Render content to the display.
        
        Parameters:
            content: DisplayContent object to render
            
        Raises:
            UIError: If rendering fails
            ValueError: If content is invalid
        """
        pass
    
    @abstractmethod
    def update(self) -> None:
        """
        Update the display (for event loop-based backends like Pygame).
        Should be called regularly in main loop.
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up UI resources.
        Must be safe to call multiple times.
        """
        pass
