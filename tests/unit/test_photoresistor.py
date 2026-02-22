"""Unit tests for photoresistor interface."""

import pytest
from client.lib import HardwareError


def test_photoresistor_interface_abstract():
    """Test that PhotoresistorInterface is an abstract base class."""
    from client.lib.photoresistor.interface import PhotoresistorInterface
    
    # Should not be able to instantiate abstract class
    with pytest.raises(TypeError):
        PhotoresistorInterface()


def test_photoresistor_read_light_value():
    """Test that read_light_value() returns a non-negative integer."""
    from client.lib.photoresistor.mock import PhotoresistorMock
    
    photo = PhotoresistorMock()
    value = photo.read_light_value()
    
    assert isinstance(value, int)
    assert value >= 0


def test_photoresistor_is_available():
    """Test that is_available() returns boolean."""
    from client.lib.photoresistor.mock import PhotoresistorMock
    
    photo = PhotoresistorMock()
    available = photo.is_available()
    
    assert isinstance(available, bool)


def test_photoresistor_hardware_error():
    """Test that hardware errors raise HardwareError."""
    from client.lib.photoresistor.mock import PhotoresistorMock
    
    photo = PhotoresistorMock()
    photo.set_error(True)
    
    with pytest.raises(HardwareError):
        photo.read_light_value()
