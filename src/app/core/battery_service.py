from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from . import linuwu_service as lw

class BatteryService(QObject):
    """Manages battery calibration and charging states."""
    
    calibrationStateChanged = pyqtSignal(bool)  # is_calibrating
    limiterStateChanged = pyqtSignal(bool)  # Add new signal

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._poll)
        self._timer.setInterval(2000)  # 2s polling

    def start(self):
        if not self._timer.isActive():
            self._timer.start()
            self._poll()  # Initial poll

    def stop(self):
        if self._timer.isActive():
            self._timer.stop()

    def start_calibration(self) -> bool:
        return lw.set_battery_calibration(True)

    def stop_calibration(self) -> bool:
        return lw.set_battery_calibration(False)

    def set_limiter(self, enabled: bool) -> bool:
        return lw.set_battery_limiter(enabled)

    def _poll(self):
        try:
            is_calibrating = bool(lw.get_battery_calibration_status())
            self.calibrationStateChanged.emit(is_calibrating)
            
            is_limited = bool(lw.get_battery_limiter_status())
            self.limiterStateChanged.emit(is_limited)
        except Exception as e:
            print(f"Battery poll error: {e}")
