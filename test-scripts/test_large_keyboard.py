#!/usr/bin/env python3
"""
Test script to verify the larger keyboard layout
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
    
    print("Large Keyboard Layout Test")
    print("=" * 60)
    print("The keyboard should now:")
    print("✓ Fill the container/frame properly")
    print("✓ Scale dynamically based on available space")
    print("✓ Be much larger and easier to see")
    print("✓ Maintain proper proportions")
    print("✓ Show combined keys with colored borders")
    print("=" * 60)
    print("\nThe keyboard scales to fit the black frame.")
    print("Keys are larger and more visible!")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
