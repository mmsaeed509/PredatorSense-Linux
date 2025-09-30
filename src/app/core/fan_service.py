import shutil
import subprocess
from typing import Optional, Tuple

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from .linuwu_service import _attr_path


LINUWU_BIN = "linuwu-sense"


class FanService(QObject):
    """Controls fan speeds and reads current RPM values via sensors.

    Speeds API expects percentage 0..100 per README:
      0   -> Auto
      1   -> Minimum (not recommended)
      100 -> Max
    Custom values like 50/70 are allowed.
    """

    rpmUpdated = pyqtSignal(int, int)  # cpu_rpm, gpu_rpm

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._poll)
        self._timer.setInterval(1000)  # 1s

    # Lifecycle
    def start(self):
        if not self._timer.isActive():
            self._timer.start()

    def stop(self):
        if self._timer.isActive():
            self._timer.stop()

    # Control methods
    def set_auto(self):
        self._set_speeds(0, 0)

    def set_max(self):
        self._set_speeds(100, 100)

    def set_custom(self, cpu_percent: int, gpu_percent: int):
        c = max(0, min(100, int(cpu_percent)))
        g = max(0, min(100, int(gpu_percent)))
        self._set_speeds(c, g)

    # Internals
    def _set_speeds(self, cpu: int, gpu: int):
        # Try sysfs write via tee (supports Predator and Nitro via _attr_path)
        path = _attr_path("fan_speed")
        if path:
            cmd = f"echo {cpu},{gpu} | tee {path}"
            if self._run_shell(cmd):
                return True
        # Fallback to linuwu-sense binary if available
        if shutil.which(LINUWU_BIN):
            return self._run([LINUWU_BIN, "--fan-speed", str(cpu), str(gpu)])
        return False

    def _run(self, args) -> bool:
        try:
            subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    def _run_shell(self, cmd: str) -> bool:
        try:
            subprocess.run(["sh", "-c", cmd], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    def _poll(self):
        vals = self._read_rpm_from_sensors()
        if vals is not None:
            cpu, gpu = vals
            self.rpmUpdated.emit(cpu, gpu)

    def _read_rpm_from_sensors(self) -> Optional[Tuple[int, int]]:
        """Parse `sensors -j` for acer-isa-0ace fan1_input/fan2_input."""
        try:
            out = subprocess.check_output(["sensors", "-j"], text=True, timeout=1.5)
        except Exception:
            return None
        try:
            import json
            data = json.loads(out)
        except Exception:
            return None
        cpu = gpu = None
        # Walk dict to find the acer-isa-0ace section and pick fan1_input, fan2_input
        stack = [data]
        while stack:
            obj = stack.pop()
            if isinstance(obj, dict):
                for k, v in obj.items():
                    lk = str(k).lower()
                    if lk.startswith("acer-isa-0ace") and isinstance(v, (dict, list)):
                        stack.append(v)
                    else:
                        if isinstance(v, (dict, list)):
                            stack.append(v)
                        else:
                            # leaf: ignore
                            pass
            elif isinstance(obj, list):
                stack.extend(obj)
        # Simpler targeted search
        def find_key(d, key):
            if isinstance(d, dict):
                if key in d and isinstance(d[key], (int, float)):
                    return int(d[key])
                for v in d.values():
                    res = find_key(v, key)
                    if res is not None:
                        return res
            elif isinstance(d, list):
                for v in d:
                    res = find_key(v, key)
                    if res is not None:
                        return res
            return None
        cpu = find_key(data, "fan1_input")
        gpu = find_key(data, "fan2_input")
        if cpu is None and gpu is None:
            return None
        return int(cpu or 0), int(gpu or 0)
