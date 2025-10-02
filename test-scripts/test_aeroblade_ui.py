#!/usr/bin/env python3
"""
Test script to verify the AeroBlade UI updates
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from app.ui.fan_control_window import FanControlWindow
from app.core import CoreController

def main():
    # Set attributes before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Create a mock controller for testing
    controller = CoreController(None)
    
    # Create the fan control window
    fan_window = FanControlWindow(controller=controller)
    fan_window.show()
    
    # Set some test RPM values to see the animation
    fan_window.setRpm(1200, 1000)
    
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())