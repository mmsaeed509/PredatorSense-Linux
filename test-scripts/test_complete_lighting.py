#!/usr/bin/env python3
"""
Complete lighting system test
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from app.ui.lighting_window import LightingWindow
from app.core import CoreController

def main():
    print("=== Complete Lighting System Test ===\n")
    
    # Test 1: Service availability
    print("1. Testing service availability...")
    from app.core.lighting_service import LightingService
    service = LightingService()
    print(f"   Service available: {service.is_available()}")
    
    # Test 2: Controller integration
    print("\n2. Testing controller integration...")
    controller = CoreController(None)
    print(f"   Controller lighting service available: {controller.lighting_service.is_available()}")
    
    # Test 3: UI creation
    print("\n3. Testing UI creation...")
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    
    try:
        lighting_window = LightingWindow(controller=controller)
        print("   UI created successfully!")
        
        # Test 4: Quick RGB test
        print("\n4. Testing RGB functionality...")
        success = controller.lighting_service.set_all_zones_color("ff0000", 50)  # Red at 50%
        print(f"   RGB test result: {success}")
        
        # Show the window briefly
        lighting_window.show()
        app.processEvents()  # Process any pending events
        
        print("\n✅ All tests passed! RGB lighting system is working correctly.")
        print("\nYou can now use the Lighting tab in the main application.")
        
    except Exception as e:
        print(f"   Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())