import random
from PyQt5.QtCore import QObject, QTimer, pyqtSignal


class MetricsService(QObject):
    """Simple metrics generator (stub). Replace with real sensors later."""

    metricsUpdated = pyqtSignal(int, int, int)  # cpu, gpu, system

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._timer.setInterval(1000)  # 1s
        self._cpu = 60
        self._gpu = 55
        self._sys = 45

    def start(self):
        if not self._timer.isActive():
            self._timer.start()

    def stop(self):
        if self._timer.isActive():
            self._timer.stop()

    def _update(self):
        # small random walk for demo
        self._cpu = max(30, min(95, self._cpu + random.randint(-2, 3)))
        self._gpu = max(30, min(95, self._gpu + random.randint(-2, 2)))
        self._sys = max(25, min(85, self._sys + random.randint(-1, 2)))
        self.metricsUpdated.emit(self._cpu, self._gpu, self._sys)
