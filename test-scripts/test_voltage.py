#!/usr/bin/env python3
"""Test voltage detection from sensors."""

import subprocess
import json

def test_voltage_sensors():
    """Test what voltage sensors are available."""
    print("=== Available Voltage Sensors ===")
    
    try:
        # Test regular sensors output
        result = subprocess.run(['sensors'], capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ['in0:', 'in1:', 'in2:', 'in3:', 'voltage', 'vcore', 'vdd']):
                    print(f"Text: {line}")
    except Exception as e:
        print(f"Error with sensors: {e}")
    
    print("\n=== JSON Voltage Sensors ===")
    try:
        # Test JSON sensors output
        result = subprocess.run(['sensors', '-j'], capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            
            for device_name, device_data in data.items():
                if isinstance(device_data, dict):
                    print(f"\nDevice: {device_name}")
                    for sensor_name, sensor_data in device_data.items():
                        if isinstance(sensor_data, dict):
                            # Look for voltage-related sensors
                            if any(keyword in sensor_name.lower() for keyword in ['in', 'voltage', 'vcore', 'vdd']):
                                print(f"  {sensor_name}: {sensor_data}")
    except Exception as e:
        print(f"Error with sensors -j: {e}")

if __name__ == "__main__":
    test_voltage_sensors()