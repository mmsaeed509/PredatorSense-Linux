import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from config import USER_CONFIG_DIR


class ConfigManager:
    def __init__(self, config_name: str = 'config.json'):
        """Initialize the config manager.
        
        Args:
            config_name: Name of the config file
        """
        self.config_path = Path(USER_CONFIG_DIR) / config_name
        self._ensure_config_dir_exists()
        self._config = self._load_config()
    
    def _ensure_config_dir_exists(self):
        """Ensure the config directory exists."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the config file.
        
        Returns:
            The loaded config as a dictionary, or an empty dict if the file doesn't exist
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
        return {}
    
    def _save_config(self):
        """Save the current config to disk."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value.
        
        Args:
            key: The config key to get
            default: Default value if key doesn't exist
            
        Returns:
            The config value or default if not found
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a config value and save to disk.
        
        Args:
            key: The config key to set
            value: The value to set
        """
        self._config[key] = value
        self._save_config()


# Global instance
config_manager = ConfigManager()
