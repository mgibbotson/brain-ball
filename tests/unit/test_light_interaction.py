"""Unit tests for light interaction logic."""

import pytest
from client.app.light_interaction import LightInteraction
from client.app.light_state import LightState
from client.app.display_content import DisplayContent


def test_light_interaction_initialization():
    """Test that LightInteraction can be initialized with hardware."""
    from client.lib.photoresistor.mock import PhotoresistorMock
    from client.lib.lcd.mock import LCDMock
    
    photo = PhotoresistorMock()
    lcd = LCDMock()
    
    interaction = LightInteraction(photoresistor=photo, lcd=lcd)
    
    assert interaction.photoresistor is photo
    assert interaction.lcd is lcd


def test_light_interaction_update_light_state():
    """Test that update_light_state() reads from photoresistor."""
    from client.lib.photoresistor.mock import PhotoresistorMock
    from client.lib.lcd.mock import LCDMock
    
    photo = PhotoresistorMock()
    photo.set_light_value(50000)
    lcd = LCDMock()
    
    interaction = LightInteraction(photoresistor=photo, lcd=lcd)
    state = interaction.update_light_state()
    
    assert isinstance(state, LightState)
    assert state.value == 50000


def test_light_interaction_generate_display_content():
    """Test that generate_display_content() creates content from light state."""
    from client.lib.photoresistor.mock import PhotoresistorMock
    from client.lib.lcd.mock import LCDMock
    
    photo = PhotoresistorMock()
    lcd = LCDMock()
    
    interaction = LightInteraction(photoresistor=photo, lcd=lcd)
    
    # Dark state
    dark_state = LightState(value=1000, normalized=0.1, is_dark=True)
    dark_content = interaction.generate_display_content(dark_state)
    
    assert isinstance(dark_content, DisplayContent)
    assert dark_content.mode == "dark"
    
    # Light state
    light_state = LightState(value=60000, normalized=0.9, is_light=True)
    light_content = interaction.generate_display_content(light_state)
    
    assert isinstance(light_content, DisplayContent)
    assert light_content.mode == "light"


def test_light_interaction_update_display():
    """Test that update_display() updates LCD with content."""
    from client.lib.photoresistor.mock import PhotoresistorMock
    from client.lib.lcd.mock import LCDMock
    
    photo = PhotoresistorMock()
    photo.set_light_value(50000)
    lcd = LCDMock()
    lcd.initialize()
    
    interaction = LightInteraction(photoresistor=photo, lcd=lcd)
    interaction.update_display()
    
    # LCD should have been called with DisplayContent
    assert lcd.last_content is not None
    assert isinstance(lcd.last_content, DisplayContent)
