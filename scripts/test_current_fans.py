#!/usr/bin/env python3
"""Test current fan speed detection."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.core.metrics_service import MetricsService
from PyQt5.QtCore import QCoreApplication
import subprocess
import json

def test_current_sensors():
    """Test current sensors output."""
    print("=== Current sensors output ===")
    try:
        result = subprocess.run(['sensors'], capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'fan' in line.lower() or 'acer-isa' in line.lower():
                    print(line)
    except Exception as e:
        print(f"Error: {e}")

def test_current_metrics():
    """Test current metrics detection."""
    app = QCoreApplication(sys.argv)
    
    metrics = MetricsService()
    
    def print_metrics(cpu_metrics):
        print(f"CPU Fan: {cpu_metrics.fan_speed} RPM")
    
    def print_gpu_metrics(gpu_metrics):
        print(f"GPU Fan: {gpu_metrics.fan_speed} RPM")
    
    # Connect signals
    metrics.cpuMetricsUpdated.connect(print_metrics)
    metrics.gpuMetricsUpdated.connect(print_gpu_metrics)
    
    # Start metrics collection
    metrics.start()
    
    print("\n=== Current Fan Speed Detection ===")
    
    # Run for 3 seconds
    from PyQt5.QtCore import QTimer
    timer = QTimer()
    timer.timeout.connect(app.quit)
    timer.start(3000)
    
    app.exec_()

if __name__ == "__main__":
    test_current_sensors()
    test_current_metrics()