#!/usr/bin/env python3
"""
Test script to visualize the keyboard layout
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt5.QtWidgets import QApplication
from app.core import CoreController
from app.ui.lighting_window import LightingWindow

def main():
    app = QApplication(sys.argv)
    
    # Create controller
    controller = CoreController()
    
    # Create and show lighting window
    window = LightingWindow(controller=controller)
    window.show()
    
    print("Keyboard layout test window opened")
    print("The keyboard should show:")
    print("- Full-sized 104-key layout")
    print("- Black background with colored borders")
    print("- 4 zones with different colors")
    print("- Proper key sizes (larger Enter, Shift, Spacebar, etc.)")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
