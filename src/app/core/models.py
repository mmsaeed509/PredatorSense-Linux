from enum import Enum, auto


class Tab(Enum):
    HOME = auto()
    LIGHTING = auto()
    OVERCLOCKING = auto()
    FAN_CONTROL = auto()
    MONITORING = auto()
    GAME_SYNC = auto()
    APP_CENTER = auto()


class LightingProfile(Enum):
    DEFAULT = "Default"
    BREATHING = "Breathing"
    WAVE = "Wave"
    RIPPLE = "Ripple"


class OverclockLevel(Enum):
    NORMAL = "Normal"
    FAST = "Fast"
    EXTREME = "Extreme"


class TemperatureUnit(Enum):
    CELSIUS = "C"
    FAHRENHEIT = "F"
