#!/usr/bin/env python3
"""
Test RGB commands directly
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.core.lighting_service import LightingService

def main():
    print("=== Testing RGB Commands ===\n")
    
    service = LightingService()
    
    if not service.is_available():
        print("RGB lighting not available!")
        return
    
    print("RGB lighting is available!")
    
    # Test static lighting - set all zones to blue
    print("\n1. Testing static lighting (all zones blue)...")
    success = service.set_all_zones_color("4287f5", 100)
    print(f"Static lighting result: {success}")
    
    # Wait a moment
    import time
    time.sleep(2)
    
    # Test dynamic lighting - breathing effect
    print("\n2. Testing dynamic lighting (breathing purple)...")
    success = service.set_breathing_effect(128, 0, 255, 4, 100, 1)
    print(f"Dynamic lighting result: {success}")
    
    # Wait a moment
    time.sleep(2)
    
    # Test another dynamic effect - wave
    print("\n3. Testing wave effect (green)...")
    success = service.set_wave_effect(0, 255, 0, 5, 100, 1)
    print(f"Wave effect result: {success}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()