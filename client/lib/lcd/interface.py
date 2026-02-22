"""Abstract interface for LCD display hardware."""

from abc import ABC, abstractmethod
from client.lib import HardwareError


class LCDInterface(ABC):
    """Abstract base class for LCD display hardware."""
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the LCD display hardware.
        
        Raises:
            HardwareError: If display cannot be initialized
            IOError: If communication with hardware fails
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """
        Clear the entire display.
        
        Raises:
            HardwareError: If display is not initialized or hardware failure occurs
        """
        pass
    
    @abstractmethod
    def update_display(self, content) -> None:
        """
        Update the display with new content.
        
        Parameters:
            content: DisplayContent object to display
            
        Raises:
            HardwareError: If display is not initialized or hardware failure occurs
            ValueError: If content is invalid
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the LCD display hardware is available and responsive.
        
        Returns:
            bool: True if hardware is available, False otherwise
        """
        pass
