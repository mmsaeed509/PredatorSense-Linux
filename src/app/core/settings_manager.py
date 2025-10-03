"""
Settings Manager for PredatorSense Linux
Handles saving and loading user preferences
"""
import json
import os
from pathlib import Path


class SettingsManager:
    """Manages application settings persistence"""
    
    def __init__(self):
        # Use XDG config directory or fallback to ~/.config
        config_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config/linuwu-sense'))
        self.config_path = Path(config_dir) / 'predatorsense-linux' / 'settings.json'
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._settings = self._load_settings()
    
    def _load_settings(self) -> dict:
        """Load settings from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
        return {}
    
    def _save_settings(self):
        """Save settings to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key: str, default=None):
        """Get a setting value"""
        return self._settings.get(key, default)
    
    def set(self, key: str, value):
        """Set a setting value"""
        self._settings[key] = value
        self._save_settings()
    
    def get_dynamic_settings(self) -> dict:
        """Get dynamic lighting settings"""
        return self._settings.get('dynamic_lighting', {
            'effect': 4,  # Shifting
            'speed': 5,
            'brightness': 100,
            'direction': 2,  # 2 = left to right (→)
            'color': '#00ffff'
        })
    
    def set_dynamic_settings(self, effect: int, speed: int, brightness: int, 
                            direction: int, color: str):
        """Save dynamic lighting settings"""
        self._settings['dynamic_lighting'] = {
            'effect': effect,
            'speed': speed,
            'brightness': brightness,
            'direction': direction,
            'color': color
        }
        self._save_settings()
    
    def get_static_settings(self) -> dict:
        """Get static lighting settings"""
        return self._settings.get('static_lighting', {
            'zone1': '00ffff',
            'zone2': 'ff00ff',
            'zone3': '00ffff',
            'zone4': 'ff00ff',
            'brightness': 100
        })
    
    def set_static_settings(self, zone1: str, zone2: str, zone3: str, 
                           zone4: str, brightness: int):
        """Save static lighting settings"""
        self._settings['static_lighting'] = {
            'zone1': zone1,
            'zone2': zone2,
            'zone3': zone3,
            'zone4': zone4,
            'brightness': brightness
        }
        self._save_settings()
