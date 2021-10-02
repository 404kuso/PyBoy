from enum import IntEnum
from .utils import get_bit, set_bits, set_bit

Fast = 1
Medium = 3
Slow = 5
Fastest = 0x00
Slowest = 0x0F

class BattleStyle(IntEnum):
    Set = 0b1000000
    Shift = 0b0000000
    def __str__(self) -> str:
        return self.name

class Settings:
    def __init__(self, val) -> None:
        self.value = val
    @property
    def speed(self):
        return get_bit(self.value, 4)
    @speed.setter
    def speed(self, speed):
        if speed > Fastest:
            raise Exception("nah you tweakin! Max speed is 0x0F")
        self.value = set_bits(self.value, speed)
    @property
    def battle_style(self) -> BattleStyle:
        return BattleStyle(self.value & 0b1000000)
    @battle_style.setter
    def battle_style(self, value):
        self.value = set_bit(self.value, 6, getattr(value.value, value))
    @property
    def battle_animation(self) -> bool:
        """True = On, False = Off"""
        return not bool(self.value & 0b10000000)
    @battle_animation.setter
    def battle_animation(self, value):
        self.value = set_bit(self.value, 7, int(not value))


def game_settings(self, value: Settings) -> Settings:
    """The game settings
    
    Parameters
    ----------
    value: `Settings`
        The new settings to be used
    
    Returns
    -------
    `Settings`
        The current settinigs
    
    """
    if value:
        self.pyboy.set_memory_value(0xD355, value.value)
    return Settings(self.pyboy.get_memory_value(0xD355))
def badges(pyboy, value=None):
    """Badges (Binary Switches)"""
    if value:
        pyboy.set_memory_value(0xD356, value)
    return pyboy.get_memory_value(0xD356)
def text_delay(pyboy, value=None):
    """If bit0 = 0, delay is limited to 1 frame between each letter. 
    If bit1 = 0, no delay during text printing. Overrides previous setting."""
    if value:
        pyboy.set_memory_value(0xD358, value)
    return pyboy.get_memory_value(0xD358)
def player_id(pyboy, value=None):
    if value:
        raise NotImplementedError()
    return int(str(pyboy.get_memory_value(0xD359) * 256) +  str(pyboy.get_memory_value(0xD35A)))
def audio_track(pyboy, value=None):
    if value:
        pyboy.set_memory_value(0xD35B, value)
    return pyboy.get_memory_value(0xD35B)
def map_palette(pyboy, value=None):
    """usallly 0; if 6, flash is required"""
    if value:
        pyboy.set_memory_value(0xD35D, value)
    return pyboy.get_memory_value(0xD35D)
