import json
import random
import subprocess
from typing import Tuple, Optional

from PyQt5.QtCore import QObject, QTimer, pyqtSignal


class MetricsService(QObject):
    """Temperature metrics provider.

    Tries, in order per tick:
    1) psutil.sensors_temperatures()
    2) `sensors -j` JSON output
    3) fallback random walk
    """

    metricsUpdated = pyqtSignal(int, int, int)  # cpu, gpu, system (in °C)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._timer.setInterval(1000)  # 1s
        # last knowns for smoothness
        self._cpu = 60
        self._gpu = 55
        self._sys = 45

    def start(self):
        if not self._timer.isActive():
            self._timer.start()

    def stop(self):
        if self._timer.isActive():
            self._timer.stop()

    # --- Providers ---
    def _read_psutil(self) -> Optional[Tuple[int, int, int]]:
        try:
            import psutil  # type: ignore
        except Exception:
            return None
        try:
            temps = psutil.sensors_temperatures(fahrenheit=False)
            if not temps:
                return None

            cpu = None
            # Prefer coretemp package value
            for key, entries in temps.items():
                if key.lower().startswith("coretemp"):
                    # pick 'Package id 0' if exists, else max of entries
                    pkg = None
                    max_core = None
                    for e in entries:
                        label = (e.label or "").lower()
                        if "package id" in label:
                            pkg = int(e.current)
                        if "core" in label:
                            v = int(e.current)
                            max_core = v if max_core is None else max(max_core, v)
                    cpu = pkg if pkg is not None else (max_core if max_core is not None else None)
                    break

            # GPU (best-effort from psutil)
            gpu = None
            for key, entries in temps.items():
                lk = key.lower()
                if "amdgpu" in lk or "nvidia" in lk:
                    for e in entries:
                        if e.current is not None:
                            gpu = int(e.current)
                            break
                if gpu is not None:
                    break

            # System: try pch or acpitz or any other meaningful source
            system = None
            for pref in ("pch", "acpitz", "iwlwifi", "acer", "nvme"):
                for key, entries in temps.items():
                    if pref in key.lower():
                        for e in entries:
                            if e.current is not None:
                                system = int(e.current)
                                break
                    if system is not None:
                        break
                if system is not None:
                    break

            # fill fallbacks from what's available
            if cpu is None:
                # Scan any source
                for entries in temps.values():
                    for e in entries:
                        if e.current is not None:
                            cpu = int(e.current)
                            break
                    if cpu is not None:
                        break

            if gpu is None and cpu is not None:
                gpu = max(0, cpu - 5)
            if system is None and cpu is not None:
                system = max(0, cpu - 10)

            if cpu is None or gpu is None or system is None:
                return None
            return int(cpu), int(gpu), int(system)
        except Exception:
            return None

    def _read_sensors_json(self) -> Optional[Tuple[int, int, int]]:
        try:
            out = subprocess.check_output(["sensors", "-j"], text=True, timeout=1.5)
            data = json.loads(out)
        except Exception:
            return None

        def pick_temp(obj, keys):
            # walk dict to find any temp*_input under known device keys
            for k in list(obj.keys()):
                low = k.lower()
                if any(p in low for p in keys):
                    # search nested for xxx_input values
                    stack = [obj[k]]
                    while stack:
                        cur = stack.pop()
                        if isinstance(cur, dict):
                            for kk, vv in cur.items():
                                if isinstance(vv, (dict, list)):
                                    stack.append(vv)
                                else:
                                    if isinstance(kk, str) and kk.endswith("_input") and isinstance(vv, (int, float)):
                                        return int(round(vv))
                        elif isinstance(cur, list):
                            stack.extend(cur)
            return None

        # Prefer explicit acer-isa-0ace mapping if present
        cpu = gpu = system = None
        try:
            for dev_name, dev_val in data.items():
                if dev_name.lower().startswith("acer-isa-0ace") and isinstance(dev_val, dict):
                    # find temp1_input/temp2_input/temp3_input
                    def find_input(dct, key):
                        v = dct.get(key)
                        if isinstance(v, (int, float)):
                            return int(round(v))
                        return None
                    # Some versions nest under another level; flatten one level
                    flat = {}
                    stack = [dev_val]
                    while stack:
                        cur = stack.pop()
                        if isinstance(cur, dict):
                            flat.update(cur)
                            for vv in cur.values():
                                if isinstance(vv, dict):
                                    stack.append(vv)
                    c = find_input(flat, "temp1_input")
                    g = find_input(flat, "temp2_input")
                    s = find_input(flat, "temp3_input")
                    if c is not None:
                        cpu = c
                    if g is not None:
                        gpu = g
                    if s is not None:
                        system = s
                    break
        except Exception:
            pass

        # If anything is missing, fall back to generic picks
        if cpu is None:
            cpu = pick_temp(data, ["coretemp", "package id", "cpu"]) or pick_temp(data, ["acer"]) 
        if gpu is None:
            gpu = pick_temp(data, ["amdgpu", "nvidia"]) or (cpu - 5 if cpu is not None else None)
        if system is None:
            system = pick_temp(data, ["pch", "acpitz", "acer"]) or (cpu - 10 if cpu is not None else None)

        if cpu is None or gpu is None or system is None:
            return None
        return int(cpu), int(gpu), int(system)

    # --- Tick ---
    def _update(self):
        # Prefer sensors -j so we can honor acer-isa-0ace temp1/2/3 mapping
        vals = self._read_sensors_json()
        if vals is None:
            vals = self._read_psutil()

        if vals is None:
            # fallback: small random walk
            self._cpu = max(30, min(95, self._cpu + random.randint(-2, 3)))
            self._gpu = max(30, min(95, self._gpu + random.randint(-2, 2)))
            self._sys = max(25, min(85, self._sys + random.randint(-1, 2)))
        else:
            self._cpu, self._gpu, self._sys = vals

        self.metricsUpdated.emit(int(self._cpu), int(self._gpu), int(self._sys))
