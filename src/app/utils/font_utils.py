import os

from PyQt5.QtGui import QFontDatabase, QFont
from config import FONTS_DIR, DEFAULT_FONT_FAMILY


def loadPredatorFont():
    # Load the font from the Fonts directory using config values
    font_path = os.path.join(FONTS_DIR, f'{DEFAULT_FONT_FAMILY}.otf')
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id == -1:
        print(f"Failed to load font: {font_path}")
        return None
    else:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        return QFont(font_family, 30, QFont.Bold)