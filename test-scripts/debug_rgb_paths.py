#!/usr/bin/env python3
"""
Debug script to check RGB keyboard paths
"""
import os
import sys

def check_path(path, description):
    exists = os.path.exists(path)
    print(f"{description}: {path}")
    print(f"  Exists: {exists}")
    if exists and os.path.isdir(path):
        try:
            contents = os.listdir(path)
            print(f"  Contents: {contents}")
        except PermissionError:
            print("  Contents: Permission denied")
    print()

def main():
    print("=== RGB Keyboard Path Debug ===\n")
    
    # Base linuwu-sense path
    base_path = "/sys/module/linuwu_sense"
    check_path(base_path, "Base linuwu-sense module")
    
    # Driver path
    driver_path = "/sys/module/linuwu_sense/drivers/platform:acer-wmi"
    check_path(driver_path, "Driver path")
    
    # Acer WMI path
    wmi_path = "/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi"
    check_path(wmi_path, "Acer WMI path")
    
    # RGB keyboard path
    rgb_path = "/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/four_zoned_kb"
    check_path(rgb_path, "RGB Keyboard path")
    
    # Predator sense path
    predator_path = "/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/predator_sense"
    check_path(predator_path, "Predator Sense path")
    
    # Nitro sense path
    nitro_path = "/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/nitro_sense"
    check_path(nitro_path, "Nitro Sense path")
    
    # Check for RGB control files if RGB path exists
    if os.path.exists(rgb_path):
        print("=== RGB Control Files ===")
        per_zone = os.path.join(rgb_path, "per_zone_mode")
        four_zone = os.path.join(rgb_path, "four_zone_mode")
        
        check_path(per_zone, "Per-zone mode file")
        check_path(four_zone, "Four-zone mode file")
    
    # Test linuwu-sense command
    print("=== Command Test ===")
    try:
        import subprocess
        result = subprocess.run(["which", "linuwu-sense"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"linuwu-sense command found at: {result.stdout.strip()}")
            
            # Test status command
            status_result = subprocess.run(["linuwu-sense", "--status"], 
                                         capture_output=True, text=True, timeout=5)
            print(f"Status command return code: {status_result.returncode}")
            if status_result.stdout:
                print(f"Status output: {status_result.stdout[:200]}...")
        else:
            print("linuwu-sense command not found")
    except Exception as e:
        print(f"Error testing command: {e}")

if __name__ == "__main__":
    main()