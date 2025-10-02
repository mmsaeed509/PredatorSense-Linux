#!/usr/bin/env python3
"""
Test script to verify the final keyboard layout with labels under the box
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
    
    print("Final Keyboard Layout Test")
    print("=" * 60)
    print("Layout improvements:")
    print("✓ Keyboard fills the height and width properly")
    print("✓ Better scaling with minimum size constraints")
    print("✓ Zone labels (Zone 1-4, Left/Center-Left/etc.) under the box")
    print("✓ Color picker buttons below the labels")
    print("✓ Clean, organized layout")
    print("=" * 60)
    print("\nThe keyboard should now:")
    print("- Fill the black frame completely")
    print("- Show zone labels underneath")
    print("- Have color pickers at the bottom")
    print("- Be properly sized and centered")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
