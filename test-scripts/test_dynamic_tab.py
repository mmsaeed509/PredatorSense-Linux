#!/usr/bin/env python3
"""
Test script to verify the PredatorSense-style Dynamic tab
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
    
    print("PredatorSense Dynamic Tab Test")
    print("=" * 60)
    print("Features:")
    print("✓ Light Effects section (Breathing, Shifting, Wave, Neon, Zoom)")
    print("✓ Speed slider")
    print("✓ Direction buttons (← →)")
    print("✓ Brightness slider (vertical, on right)")
    print("✓ Basic colors palette")
    print("✓ More color... button")
    print("✓ Color sections hidden for Wave and Neon effects")
    print("✓ Auto-apply on changes")
    print("=" * 60)
    print("\nTest the Dynamic tab:")
    print("1. Click different effects")
    print("2. Notice Wave and Neon hide color sections")
    print("3. Adjust speed and direction")
    print("4. Select colors from basic palette")
    print("5. Use 'More color...' for custom colors")
    print("6. Adjust brightness with vertical slider")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
