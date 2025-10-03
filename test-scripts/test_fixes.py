#!/usr/bin/env python3
"""
Test script to verify the fixes: Direction, Sudo, and Persistence
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
    
    # Check settings file
    settings_file = controller.settings.config_path
    print("Settings Persistence Test")
    print("=" * 60)
    print(f"Settings file: {settings_file}")
    print(f"Settings file exists: {settings_file.exists()}")
    
    if settings_file.exists():
        print("\nCurrent saved settings:")
        with open(settings_file, 'r') as f:
            print(f.read())
    else:
        print("\nNo settings file yet (will be created on first use)")
    
    print("\n" + "=" * 60)
    print("Testing Fixes:")
    print("=" * 60)
    
    print("\n1. Direction Fix:")
    print("   - Click ← button")
    print("   - Verify it stays selected")
    print("   - Click → button")
    print("   - Verify it switches properly")
    print("   - No flickering or toggling")
    
    print("\n2. Persistence Fix:")
    print("   - Select Zoom effect")
    print("   - Change speed, direction, color")
    print("   - Close application")
    print("   - Reopen application")
    print("   - Verify Zoom is still selected")
    print("   - Verify all settings restored")
    
    print("\n3. Sudo Fix:")
    print("   - Make changes")
    print("   - Should NOT ask for password")
    print("   - Uses linuwu-sense CLI properly")
    
    print("\n" + "=" * 60)
    
    # Create and show lighting window
    window = LightingWindow(controller=controller)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
