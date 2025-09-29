#####################################
#                                   #
#  @author      : 00xWolf           #
#    GitHub    : @mmsaeed509       #
#    Developer : Mahmoud Mohamed   #
#  﫥  Copyright : Exodia OS         #
#                                   #
#####################################

"""
Centralized configuration for Exodia Assistant.
All global constants, paths, and environment settings should be defined here.
"""

import os
from typing import Final

# App Info #
APP_NAME: Final[str]    = "PredatorSense Linux"
APP_VERSION: Final[str] = "1.0"
APP_RELEASE: Final[str] = "1"
APP_AUTHOR: Final[str]  = "Mahmoud Mohammed,  @mmsaeed509"
APP_URL: Final[str]     = "https://github.com/mmsaeed509/PredatorSense-Linux"
APP_LICENSE: Final[str] = "MIT License"

# Paths #
BASE_DIR: Final[str]   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR: Final[str] = os.path.join(BASE_DIR, "assets")
FONTS_DIR: Final[str]  = os.path.join(ASSETS_DIR, "fonts")
ICONS_DIR: Final[str]  = os.path.join(ASSETS_DIR, "icons")
IMGS_DIR: Final[str]   = os.path.join(ASSETS_DIR, "imgs")

USER_CONFIG_DIR: Final[str]     = os.path.expanduser("~/.config/linuwu-sense")
ROLES_PROFILES_DIR: Final[str]  = os.path.join(USER_CONFIG_DIR, "saved_profiles")

# Font #
DEFAULT_FONT_FAMILY: Final[str] = "Squares-Bold"

# WM_CLASS #
WM_CLASS: Final[str]   = "PredatorSense Linux"
WM_CLASS_2: Final[str] = "PredatorSense-Linux"

# Environment #
DEBUG: Final[bool] = bool(os.environ.get("PredatorSense_DEBUG", False))
