#!/usr/bin/env python3
"""Test script to verify metrics collection."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app.core.metrics_service import MetricsService
from PyQt5.QtCore import QCoreApplication
import time

def test_metrics():
    app = QCoreApplication(sys.argv)
    
    metrics = MetricsService()
    
    def print_metrics(cpu_temp, gpu_temp, sys_temp):
        print(f"Temperatures - CPU: {cpu_temp}°C, GPU: {gpu_temp}°C, System: {sys_temp}°C")
    
    def print_cpu_metrics(cpu_metrics):
        print(f"CPU: {cpu_metrics.name}")
        print(f"  Fan: {cpu_metrics.fan_speed} RPM")
        print(f"  Freq: {cpu_metrics.frequency} MHz")
        print(f"  Voltage: {cpu_metrics.voltage} V")
        print(f"  Usage: {cpu_metrics.usage}%")
        print(f"  Temp Range: {cpu_metrics.min_temp}°C - {cpu_metrics.max_temp}°C")
    
    def print_gpu_metrics(gpu_metrics):
        print(f"GPU: {gpu_metrics.name}")
        print(f"  Fan: {gpu_metrics.fan_speed} RPM")
        print(f"  Core Clock: {gpu_metrics.core_clock} MHz")
        print(f"  Usage: {gpu_metrics.usage}%")
        print(f"  Temp Range: {gpu_metrics.min_temp}°C - {gpu_metrics.max_temp}°C")
    
    def print_system_metrics(system_metrics):
        print(f"System:")
        print(f"  RAM: {system_metrics.ram_usage_gb}GB / {system_metrics.ram_total_gb}GB ({system_metrics.ram_usage_percent}%)")
        print(f"  RAM Freq: {system_metrics.ram_frequency} MHz")
        print(f"  Ethernet: ↓{system_metrics.ethernet_download} Kbps ↑{system_metrics.ethernet_upload} Kbps")
        print(f"  WiFi: ↓{system_metrics.wifi_download} Kbps ↑{system_metrics.wifi_upload} Kbps")
        print(f"  Temp Range: {system_metrics.min_temp}°C - {system_metrics.max_temp}°C")
    
    # Connect signals
    metrics.metricsUpdated.connect(print_metrics)
    metrics.cpuMetricsUpdated.connect(print_cpu_metrics)
    metrics.gpuMetricsUpdated.connect(print_gpu_metrics)
    metrics.systemMetricsUpdated.connect(print_system_metrics)
    
    # Start metrics collection
    metrics.start()
    
    print("Collecting metrics for 10 seconds...")
    print("=" * 50)
    
    # Run for 10 seconds
    from PyQt5.QtCore import QTimer
    timer = QTimer()
    timer.timeout.connect(app.quit)
    timer.start(10000)  # 10 seconds
    
    app.exec_()

if __name__ == "__main__":
    test_metrics()