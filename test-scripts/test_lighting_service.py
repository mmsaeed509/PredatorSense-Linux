#!/usr/bin/env python3
"""
Test script to debug the lighting service
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.core.lighting_service import LightingService

def main():
    print("=== Lighting Service Debug ===\n")
    
    service = LightingService()
    
    print(f"RGB keyboard available: {service.is_available()}")
    
    # Test the path detection
    from app.core.lighting_service import RGB_KB_BASE_PATH, _rgb_attr_path
    
    print(f"RGB base path: {RGB_KB_BASE_PATH}")
    print(f"RGB base path exists: {os.path.exists(RGB_KB_BASE_PATH)}")
    
    per_zone_path = _rgb_attr_path("per_zone_mode")
    four_zone_path = _rgb_attr_path("four_zone_mode")
    
    print(f"Per-zone path: {per_zone_path}")
    print(f"Per-zone exists: {os.path.exists(per_zone_path)}")
    
    print(f"Four-zone path: {four_zone_path}")
    print(f"Four-zone exists: {os.path.exists(four_zone_path)}")
    
    # Test preset colors
    presets = service.get_preset_colors()
    print(f"\nPreset colors: {len(presets)} available")
    for name, hex_color in presets[:3]:  # Show first 3
        print(f"  {name}: #{hex_color}")
    
    # Test effect modes
    effects = service.get_effect_modes()
    print(f"\nEffect modes: {len(effects)} available")
    for mode_id, name in effects[:3]:  # Show first 3
        print(f"  {mode_id}: {name}")

if __name__ == "__main__":
    main()