#!/usr/bin/env python3
"""
Test script to verify the RGB Lighting UI
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from app.ui.lighting_window import LightingWindow
from app.core import CoreController

def main():
    # Set attributes before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Create controller
    controller = CoreController(None)
    
    # Create the lighting window
    lighting_window = LightingWindow(controller=controller)
    lighting_window.show()
    
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())