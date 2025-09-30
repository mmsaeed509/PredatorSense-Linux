import os
import subprocess
from typing import Optional, List, Tuple
from PyQt5.QtCore import QObject, pyqtSignal
from .linuwu_service import _attr_path, _read_int, _run_cmd

class LightingService(QObject):
    """Controls keyboard RGB lighting via linuwu-sense module."""
    
    modeChanged = pyqtSignal(int)  # Current mode
    zoneColorsChanged = pyqtSignal(list)  # [zone1_rgb, zone2_rgb, zone3_rgb, zone4_rgb]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._base_path = os.path.join(_attr_path(""), "four_zoned_kb")

    def set_per_zone_colors(self, colors: List[str], brightness: int = 100) -> bool:
        """Set individual RGB colors for each zone.
        colors: List of 4 hex RGB values without # (e.g. ['ff0000', '00ff00', ...])
        """
        if len(colors) != 4 or not all(len(c) == 6 for c in colors):
            return False
            
        value = f"{','.join(colors)},{brightness}"
        path = os.path.join(self._base_path, "per_zone_mode")
        return _run_cmd(["bash", "-lc", f"echo {value} | tee {path}"])

    def set_effect_mode(self, mode: int, speed: int = 5, brightness: int = 100, 
                       direction: int = 1, rgb: Tuple[int, int, int] = (0, 0, 255)) -> bool:
        """Set keyboard effect mode with parameters."""
        if not (0 <= mode <= 7 and 0 <= speed <= 9 and 0 <= brightness <= 100 
                and direction in (1, 2) and all(0 <= x <= 255 for x in rgb)):
            return False
            
        value = f"{mode},{speed},{brightness},{direction},{rgb[0]},{rgb[1]},{rgb[2]}"
        path = os.path.join(self._base_path, "four_zone_mode")
        return _run_cmd(["bash", "-lc", f"echo {value} | tee {path}"])

    def get_current_colors(self) -> Optional[List[str]]:
        """Get current per-zone colors. Returns list of 4 hex RGB values or None."""
        try:
            path = os.path.join(self._base_path, "per_zone_mode")
            with open(path) as f:
                value = f.read().strip()
            parts = value.split(",")
            if len(parts) >= 4:
                return parts[:4]
        except Exception:
            pass
        return None
