#####################################
#                                   #
#  @author      : 00xWolf           #
#    GitHub    : @mmsaeed509       #
#    Developer : Mahmoud Mohamed   #
#  﫥  Copyright : Exodia OS         #
#                                   #
#####################################

import os
import json
import yaml
from typing import Any, Optional


def read_text_file(path: str, encoding: str = "utf-8") -> Optional[str]:
    """
    Read a text file and return its contents as a string. Returns None if a file is not found or error.
    """
    try:
        with open(path, "r", encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"[file_utils] Error reading {path}: {e}")
        return None


def write_text_file(path: str, content: str, encoding: str = "utf-8") -> bool:
    """
    Write a string to a text file. Returns True on success, False on error.
    """
    try:
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"[file_utils] Error writing {path}: {e}")
        return False


def read_json_file(path: str, encoding: str = "utf-8") -> Optional[Any]:
    """
    Read a JSON file and return the parsed object. Returns None on error.
    """
    try:
        with open(path, "r", encoding=encoding) as f:
            return json.load(f)
    except Exception as e:
        print(f"[file_utils] Error reading JSON {path}: {e}")
        return None


def write_json_file(path: str, data: Any, encoding: str = "utf-8", indent: int = 2) -> bool:
    """
    Write an object to a JSON file. Returns True on success, False on error.
    """
    try:
        with open(path, "w", encoding=encoding) as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception as e:
        print(f"[file_utils] Error writing JSON {path}: {e}")
        return False


def read_yaml_file(path: str, encoding: str = "utf-8") -> Optional[Any]:
    """
    Read a YAML file and return the parsed object. Returns None on error.
    """
    try:
        with open(path, "r", encoding=encoding) as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[file_utils] Error reading YAML {path}: {e}")
        return None


def write_yaml_file(path: str, data: Any, encoding: str = "utf-8") -> bool:
    """
    Write an object to a YAML file. Returns True on success, False on error.
    """
    try:
        with open(path, "w", encoding=encoding) as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        return True
    except Exception as e:
        print(f"[file_utils] Error writing YAML {path}: {e}")
        return False


def ensure_dir_exists(path: str) -> None:
    """
    Ensure that a directory exists. Create it if it does not.
    """
    os.makedirs(path, exist_ok=True)
