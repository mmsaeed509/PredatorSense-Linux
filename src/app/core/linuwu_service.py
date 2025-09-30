import os
import subprocess
from typing import Optional

# Support both Predator and Nitro paths
PREDATOR_SENSE_PATH = "/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/predator_sense"
NITRO_SENSE_PATH = "/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/nitro_sense"

_SENSE_BASE_CACHE: Optional[str] = None


def _sense_base() -> Optional[str]:
    global _SENSE_BASE_CACHE
    if _SENSE_BASE_CACHE is not None:
        return _SENSE_BASE_CACHE
    if os.path.exists(PREDATOR_SENSE_PATH):
        _SENSE_BASE_CACHE = PREDATOR_SENSE_PATH
    elif os.path.exists(NITRO_SENSE_PATH):
        _SENSE_BASE_CACHE = NITRO_SENSE_PATH
    else:
        _SENSE_BASE_CACHE = None
    return _SENSE_BASE_CACHE


def _attr_path(attr: str) -> Optional[str]:
    base = _sense_base()
    return os.path.join(base, attr) if base else None


def _read_int(path: Optional[str]) -> Optional[int]:
    if not path:
        return None
    try:
        with open(path, "r") as f:
            val = f.read().strip()
        return int(val)
    except Exception:
        try:
            out = subprocess.check_output(["cat", path], text=True, timeout=1.0)
            return int(out.strip())
        except Exception:
            return None


def _run_cmd(args: list) -> bool:
    try:
        res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2.0)
        return res.returncode == 0
    except Exception:
        return False


# Boot animation & sound

def get_boot_animation_enabled() -> Optional[bool]:
    v = _read_int(_attr_path("boot_animation_sound"))
    return None if v is None else (v == 1)


def set_boot_animation_enabled(enabled: bool) -> bool:
    # Prefer CLI; fallback to writing sysfs using tee
    if enabled:
        if _run_cmd(["linuwu-sense", "--boot-animation"]):
            return True
    else:
        if _run_cmd(["linuwu-sense", "--no-boot-animation"]):
            return True
    # Fallback
    val = "1" if enabled else "0"
    path = _attr_path("boot_animation_sound")
    if not path:
        return False
    return _run_cmd(["bash", "-lc", f"echo {val} | tee {path}"])


# LCD override

def get_lcd_override_enabled() -> Optional[bool]:
    v = _read_int(_attr_path("lcd_override"))
    return None if v is None else (v == 1)


def set_lcd_override_enabled(enabled: bool) -> bool:
    if enabled:
        if _run_cmd(["linuwu-sense", "--lcd-override"]):
            return True
    else:
        if _run_cmd(["linuwu-sense", "--no-lcd-override"]):
            return True
    val = "1" if enabled else "0"
    path = _attr_path("lcd_override")
    if not path:
        return False
    return _run_cmd(["bash", "-lc", f"echo {val} | tee {path}"])


# Backlight timeout (30s)

def get_backlight_timeout_enabled() -> Optional[bool]:
    v = _read_int(_attr_path("backlight_timeout"))
    return None if v is None else (v == 1)


def set_backlight_timeout_enabled(enabled: bool) -> bool:
    if enabled:
        if _run_cmd(["linuwu-sense", "--backlight-timeout"]):
            return True
    else:
        if _run_cmd(["linuwu-sense", "--no-backlight-timeout"]):
            return True
    val = "1" if enabled else "0"
    path = _attr_path("backlight_timeout")
    if not path:
        return False
    return _run_cmd(["bash", "-lc", f"echo {val} | tee {path}"])


# Battery calibration
def get_battery_calibration_status() -> Optional[bool]:
    v = _read_int(_attr_path("battery_calibration"))
    return None if v is None else (v == 1)


def set_battery_calibration(enabled: bool) -> bool:
    if enabled:
        if _run_cmd(["linuwu-sense", "--battery-calibration"]):
            return True
    else:
        if _run_cmd(["linuwu-sense", "--stop-battery-calibration"]):
            return True
    val = "1" if enabled else "0"
    path = _attr_path("battery_calibration")
    if not path:
        return False
    return _run_cmd(["bash", "-lc", f"echo {val} | tee {path}"])


# Battery limiter
def get_battery_limiter_status() -> Optional[bool]:
    v = _read_int(_attr_path("battery_limiter"))
    return None if v is None else (v == 1)


def set_battery_limiter(enabled: bool) -> bool:
    if enabled:
        if _run_cmd(["linuwu-sense", "--battery-limiter"]):
            return True
    else:
        if _run_cmd(["linuwu-sense", "--no-battery-limiter"]):
            return True
    val = "1" if enabled else "0"
    path = _attr_path("battery_limiter")
    if not path:
        return False
    return _run_cmd(["bash", "-lc", f"echo {val} | tee {path}"])


# USB charging
def get_usb_charging_threshold() -> Optional[int]:
    """Get current USB charging threshold (0, 10, 20, or 30)"""
    return _read_int(_attr_path("usb_charging"))


def set_usb_charging_threshold(value: int) -> bool:
    """Set USB charging threshold. Valid values: 0, 10, 20, 30"""
    if value not in (0, 10, 20, 30):
        return False

    if _run_cmd(["linuwu-sense", "--usb-charging", str(value)]):
        return True

    path = _attr_path("usb_charging")
    if not path:
        return False
    return _run_cmd(["bash", "-lc", f"echo {value} | tee {path}"])
