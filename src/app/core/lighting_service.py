"""
RGB Keyboard Lighting Service for Acer Predator/Nitro laptops
Supports both Static (per-zone) and Dynamic (four-zone) modes
"""
import os
import subprocess
from typing import Optional, Tuple, List
from PyQt5.QtCore import QObject, pyqtSignal
from .linuwu_service import _run_cmd

# RGB keyboard specific paths
RGB_KB_BASE_PATH = "/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/four_zoned_kb"

def _rgb_attr_path(attr: str) -> str:
    """Get path for RGB keyboard attribute"""
    return os.path.join(RGB_KB_BASE_PATH, attr)


class LightingService(QObject):
    """Service for controlling RGB keyboard lighting"""
    
    # Signals
    lightingChanged = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._current_mode = "static"  # "static" or "dynamic"
        
    def is_available(self) -> bool:
        """Check if RGB lighting is available on this system"""
        # Check if the RGB keyboard base path exists
        if not os.path.exists(RGB_KB_BASE_PATH):
            return False
        
        # Check for required RGB keyboard control files
        per_zone_path = _rgb_attr_path("per_zone_mode")
        four_zone_path = _rgb_attr_path("four_zone_mode")
        
        return os.path.exists(per_zone_path) or os.path.exists(four_zone_path)
    
    def get_current_mode(self) -> str:
        """Get current lighting mode (static/dynamic)"""
        return self._current_mode
    
    def set_current_mode(self, mode: str):
        """Set current lighting mode"""
        if mode in ["static", "dynamic"]:
            self._current_mode = mode
            self.lightingChanged.emit()
    
    def get_current_zone_colors(self) -> Tuple[str, str, str, str, int]:
        """
        Read current zone colors from system
        
        Returns:
            Tuple of (zone1_hex, zone2_hex, zone3_hex, zone4_hex, brightness)
        """
        try:
            path = _rgb_attr_path("per_zone_mode")
            with open(path, 'r') as f:
                data = f.read().strip()
            
            # Format: "color1,color2,color3,color4,brightness"
            parts = data.split(',')
            if len(parts) == 5:
                return (parts[0], parts[1], parts[2], parts[3], int(parts[4]))
            
        except Exception as e:
            print(f"Error reading zone colors: {e}")
        
        # Return defaults if read fails
        return ("4287f5", "4287f5", "4287f5", "4287f5", 100)
    
    # Static Mode (Per-Zone) Functions
    def set_per_zone_colors(self, zone1: str, zone2: str, zone3: str, zone4: str, brightness: int = 100) -> bool:
        """
        Set individual zone colors (Static mode)
        
        Args:
            zone1-zone4: Hex color strings (e.g., "4287f5")
            brightness: 0-100
        
        Returns:
            bool: Success status
        """
        if not (0 <= brightness <= 100):
            return False
        
        # Validate hex colors
        for color in [zone1, zone2, zone3, zone4]:
            if not self._is_valid_hex_color(color):
                return False
        
        # Try CLI first
        cmd = ["linuwu-sense", "--per-zone-mode", zone1, zone2, zone3, zone4, str(brightness)]
        if _run_cmd(cmd):
            self._current_mode = "static"
            self.lightingChanged.emit()
            return True
        
        # Fallback to direct sysfs write
        path = _rgb_attr_path("per_zone_mode")
        
        value = f"{zone1},{zone2},{zone3},{zone4},{brightness}"
        success = _run_cmd(["bash", "-lc", f"echo {value} | sudo tee {path}"])
        
        if success:
            self._current_mode = "static"
            self.lightingChanged.emit()
        
        return success
    
    def set_all_zones_color(self, color: str, brightness: int = 100) -> bool:
        """Set all zones to the same color"""
        return self.set_per_zone_colors(color, color, color, color, brightness)
    
    # Dynamic Mode (Four-Zone) Functions
    def set_four_zone_mode(self, mode: int, speed: int, brightness: int, direction: int, 
                          red: int, green: int, blue: int) -> bool:
        """
        Set four-zone animated mode (Dynamic mode)
        
        Args:
            mode: 0=Static, 1=Breathing, 2=Neon, 3=Wave, 4=Shifting, 5=Zoom, 6=Meteor, 7=Twinkling
            speed: 0-9
            brightness: 0-100
            direction: 0-2
            red, green, blue: 0-255
        
        Returns:
            bool: Success status
        """
        # Validate parameters
        if not (0 <= mode <= 7):
            return False
        if not (0 <= speed <= 9):
            return False
        if not (0 <= brightness <= 100):
            return False
        if not (0 <= direction <= 2):
            return False
        if not all(0 <= c <= 255 for c in [red, green, blue]):
            return False
        
        # Try CLI first
        cmd = ["linuwu-sense", "--four-zone-mode", str(mode), str(speed), str(brightness), 
               str(direction), str(red), str(green), str(blue)]
        if _run_cmd(cmd):
            self._current_mode = "dynamic"
            self.lightingChanged.emit()
            return True
        
        # Fallback to direct sysfs write
        path = _rgb_attr_path("four_zone_mode")
        
        value = f"{mode},{speed},{brightness},{direction},{red},{green},{blue}"
        success = _run_cmd(["bash", "-lc", f"echo {value} | sudo tee {path}"])
        
        if success:
            self._current_mode = "dynamic"
            self.lightingChanged.emit()
        
        return success
    
    # Convenience methods for common effects
    def set_breathing_effect(self, red: int, green: int, blue: int, speed: int = 4, 
                           brightness: int = 100, direction: int = 1) -> bool:
        """Set breathing effect with specified color"""
        return self.set_four_zone_mode(1, speed, brightness, direction, red, green, blue)
    
    def set_wave_effect(self, red: int, green: int, blue: int, speed: int = 4, 
                       brightness: int = 100, direction: int = 1) -> bool:
        """Set wave effect with specified color"""
        return self.set_four_zone_mode(3, speed, brightness, direction, red, green, blue)
    
    def set_neon_effect(self, red: int, green: int, blue: int, speed: int = 4, 
                       brightness: int = 100, direction: int = 1) -> bool:
        """Set neon effect with specified color"""
        return self.set_four_zone_mode(2, speed, brightness, direction, red, green, blue)
    
    def set_meteor_effect(self, red: int, green: int, blue: int, speed: int = 4, 
                         brightness: int = 100, direction: int = 1) -> bool:
        """Set meteor effect with specified color"""
        return self.set_four_zone_mode(6, speed, brightness, direction, red, green, blue)
    
    def set_twinkling_effect(self, red: int, green: int, blue: int, speed: int = 4, 
                           brightness: int = 100, direction: int = 1) -> bool:
        """Set twinkling effect with specified color"""
        return self.set_four_zone_mode(7, speed, brightness, direction, red, green, blue)
    
    # Utility methods
    def _is_valid_hex_color(self, color: str) -> bool:
        """Validate hex color string (6 characters, no # prefix)"""
        if len(color) != 6:
            return False
        try:
            int(color, 16)
            return True
        except ValueError:
            return False
    
    def rgb_to_hex(self, red: int, green: int, blue: int) -> str:
        """Convert RGB values to hex string"""
        return f"{red:02x}{green:02x}{blue:02x}"
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex string to RGB tuple"""
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        
        if len(hex_color) != 6:
            return (0, 0, 0)
        
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b)
        except ValueError:
            return (0, 0, 0)
    
    # Preset colors
    @staticmethod
    def get_preset_colors() -> List[Tuple[str, str]]:
        """Get list of preset colors (name, hex)"""
        return [
            ("Red", "ff0000"),
            ("Green", "00ff00"),
            ("Blue", "0000ff"),
            ("Cyan", "00ffff"),
            ("Magenta", "ff00ff"),
            ("Yellow", "ffff00"),
            ("Orange", "ff8000"),
            ("Purple", "8000ff"),
            ("Pink", "ff0080"),
            ("White", "ffffff"),
            ("Predator Blue", "4287f5"),
            ("Gaming Green", "33ff57"),
            ("Neon Pink", "ff33a6"),
            ("Electric Orange", "ff5733"),
        ]
    
    # Effect modes for dynamic lighting
    @staticmethod
    def get_effect_modes() -> List[Tuple[int, str]]:
        """Get list of available effect modes (id, name)"""
        return [
            (0, "Static"),
            (1, "Breathing"),
            (2, "Neon"),
            (3, "Wave"),
            (4, "Shifting"),
            (5, "Zoom"),
            (6, "Meteor"),
            (7, "Twinkling"),
        ]