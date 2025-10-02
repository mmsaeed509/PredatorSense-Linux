#!/usr/bin/env python3
"""
Test script to verify zone color reading and keyboard layout
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.core.lighting_service import LightingService

def test_read_zone_colors():
    """Test reading current zone colors from system"""
    service = LightingService()
    
    print("Testing RGB Lighting Service...")
    print(f"Is available: {service.is_available()}")
    
    if service.is_available():
        print("\nReading current zone colors...")
        zone1, zone2, zone3, zone4, brightness = service.get_current_zone_colors()
        
        print(f"Zone 1 (Left):         #{zone1}")
        print(f"Zone 2 (Center-Left):  #{zone2}")
        print(f"Zone 3 (Center-Right): #{zone3}")
        print(f"Zone 4 (Right):        #{zone4}")
        print(f"Brightness:            {brightness}%")
        
        # Test setting colors
        print("\nTesting color setting...")
        success = service.set_per_zone_colors(zone1, zone2, zone3, zone4, brightness)
        print(f"Set colors result: {success}")
    else:
        print("RGB lighting not available on this system")

if __name__ == "__main__":
    test_read_zone_colors()
