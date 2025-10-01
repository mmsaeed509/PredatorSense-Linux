#!/usr/bin/env python3
"""Test CPU voltage detection."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.core.metrics_service import MetricsService
from PyQt5.QtCore import QCoreApplication

def test_voltage_detection():
    """Test CPU voltage detection."""
    app = QCoreApplication(sys.argv)
    
    metrics = MetricsService()
    
    def print_cpu_voltage(cpu_metrics):
        print(f"CPU Voltage: {cpu_metrics.voltage} V")
        print(f"CPU Frequency: {cpu_metrics.frequency} MHz")
        print(f"CPU Usage: {cpu_metrics.usage}%")
        print("---")
    
    # Connect signals
    metrics.cpuMetricsUpdated.connect(print_cpu_voltage)
    
    # Start metrics collection
    metrics.start()
    
    print("=== CPU Voltage Detection Test ===")
    
    # Run for 5 seconds
    from PyQt5.QtCore import QTimer
    timer = QTimer()
    timer.timeout.connect(app.quit)
    timer.start(5000)
    
    app.exec_()

if __name__ == "__main__":
    test_voltage_detection()