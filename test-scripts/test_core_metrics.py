#!/usr/bin/env python3
"""Test script to verify per-core CPU metrics collection."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.core.metrics_service import MetricsService
from PyQt5.QtCore import QCoreApplication
import time

def test_core_metrics():
    app = QCoreApplication(sys.argv)
    
    metrics = MetricsService()
    
    def print_cpu_details(cpu_metrics):
        print(f"\n=== CPU Details ===")
        print(f"CPU: {cpu_metrics.name}")
        print(f"Overall Frequency: {cpu_metrics.frequency} MHz")
        print(f"Core Count: {cpu_metrics.core_count}")
        print(f"Usage: {cpu_metrics.usage}%")
        print(f"Temperature: {cpu_metrics.temperature}°C")
        
        print(f"\n--- Per-Core Frequencies ---")
        for i, freq in enumerate(cpu_metrics.core_frequencies):
            print(f"Core #{i+1}: {freq} MHz")
        
        print(f"\n--- Per-Core Temperatures ---")
        for i, temp in enumerate(cpu_metrics.core_temperatures):
            print(f"Core #{i+1}: {temp}°C")
        
        print("=" * 50)
    
    # Connect signals
    metrics.cpuMetricsUpdated.connect(print_cpu_details)
    
    # Start metrics collection
    metrics.start()
    
    print("Collecting per-core CPU metrics for 10 seconds...")
    print("=" * 50)
    
    # Run for 10 seconds
    from PyQt5.QtCore import QTimer
    timer = QTimer()
    timer.timeout.connect(app.quit)
    timer.start(10000)  # 10 seconds
    
    app.exec_()

if __name__ == "__main__":
    test_core_metrics()