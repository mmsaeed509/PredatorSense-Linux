from PyQt5.QtCore import QObject, pyqtSignal
from .models import Tab, LightingProfile, OverclockLevel, TemperatureUnit
from .metrics_service import MetricsService
from .fan_service import FanService
from .battery_service import BatteryService
from .lighting_service import LightingService


class CoreController(QObject):
    """App core state and services coordinator."""

    tabChanged = pyqtSignal(object)  # Tab
    lightingChanged = pyqtSignal(object)  # LightingProfile
    overclockChanged = pyqtSignal(object)  # OverclockLevel
    temperatureUnitChanged = pyqtSignal(object)  # TemperatureUnit

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tab = Tab.HOME
        self._lighting = LightingProfile.DEFAULT
        self._overclock = OverclockLevel.NORMAL
        self._temp_unit = TemperatureUnit.CELSIUS
        self.metrics = MetricsService(self)
        self.fans = FanService(self)
        self.battery = BatteryService(self)
        self.lighting_service = LightingService()

    # Lifecycle
    def start(self):
        self.metrics.start()
        try:
            self.fans.start()
        except Exception:
            pass
        try:
            self.battery.start()
        except Exception:
            pass
        # Lighting service doesn't need explicit start/stop

    def stop(self):
        self.metrics.stop()
        try:
            self.fans.stop()
        except Exception:
            pass
        try:
            self.battery.stop()
        except Exception:
            pass

    # State setters
    def set_tab(self, tab: Tab):
        if tab != self._tab:
            self._tab = tab
            self.tabChanged.emit(tab)

    def set_lighting(self, profile: LightingProfile):
        if profile != self._lighting:
            self._lighting = profile
            self.lightingChanged.emit(profile)

    def set_overclock(self, level: OverclockLevel):
        if level != self._overclock:
            self._overclock = level
            self.overclockChanged.emit(level)

    def set_temperature_unit(self, unit: TemperatureUnit):
        if unit != self._temp_unit:
            self._temp_unit = unit
            self.temperatureUnitChanged.emit(unit)

    # Getters
    @property
    def tab(self) -> Tab:
        return self._tab

    @property
    def lighting(self) -> LightingProfile:
        return self._lighting

    @property
    def overclock(self) -> OverclockLevel:
        return self._overclock

    @property
    def temperature_unit(self) -> TemperatureUnit:
        return self._temp_unit
