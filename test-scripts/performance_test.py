#!/usr/bin/env python3
"""
Performance test script for PredatorSense application.
Tests startup time, memory usage, and responsiveness.
"""

import sys
import time
import subprocess
import psutil
from typing import Dict, List


def measure_startup_time() -> float:
    """Measure application startup time."""
    print("Testing startup time...")
    
    start_time = time.time()
    
    # Start the application
    process = subprocess.Popen([
        sys.executable, "src/main.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for the process to fully start (window appears)
    time.sleep(3)
    
    startup_time = time.time() - start_time
    
    # Terminate the process
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
    
    return startup_time


def measure_memory_usage() -> Dict[str, float]:
    """Measure memory usage over time."""
    print("Testing memory usage...")
    
    # Start the application
    process = subprocess.Popen([
        sys.executable, "src/main.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    memory_samples = []
    
    try:
        # Wait for startup
        time.sleep(2)
        
        # Get process handle
        app_process = psutil.Process(process.pid)
        
        # Sample memory usage over 30 seconds
        for i in range(10):
            try:
                memory_info = app_process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                memory_samples.append(memory_mb)
                time.sleep(3)
            except psutil.NoSuchProcess:
                break
    
    finally:
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    
    if memory_samples:
        return {
            'initial_mb': memory_samples[0],
            'peak_mb': max(memory_samples),
            'average_mb': sum(memory_samples) / len(memory_samples),
            'final_mb': memory_samples[-1],
            'growth_mb': memory_samples[-1] - memory_samples[0]
        }
    else:
        return {'error': 'Could not measure memory usage'}


def test_cpu_usage() -> Dict[str, float]:
    """Test CPU usage during normal operation."""
    print("Testing CPU usage...")
    
    # Start the application
    process = subprocess.Popen([
        sys.executable, "src/main.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    cpu_samples = []
    
    try:
        # Wait for startup
        time.sleep(2)
        
        # Get process handle
        app_process = psutil.Process(process.pid)
        
        # Sample CPU usage
        for i in range(10):
            try:
                cpu_percent = app_process.cpu_percent(interval=1)
                cpu_samples.append(cpu_percent)
            except psutil.NoSuchProcess:
                break
    
    finally:
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    
    if cpu_samples:
        return {
            'average_cpu': sum(cpu_samples) / len(cpu_samples),
            'peak_cpu': max(cpu_samples),
            'idle_cpu': min(cpu_samples)
        }
    else:
        return {'error': 'Could not measure CPU usage'}


def run_performance_tests():
    """Run all performance tests and display results."""
    print("🚀 PredatorSense Performance Test Suite")
    print("=" * 50)
    
    # Test 1: Startup Time
    try:
        startup_time = measure_startup_time()
        print(f"✅ Startup Time: {startup_time:.2f} seconds")
        
        if startup_time < 3.0:
            print("   🟢 Excellent startup performance")
        elif startup_time < 5.0:
            print("   🟡 Good startup performance")
        else:
            print("   🔴 Slow startup - needs optimization")
    except Exception as e:
        print(f"❌ Startup test failed: {e}")
    
    print()
    
    # Test 2: Memory Usage
    try:
        memory_stats = measure_memory_usage()
        if 'error' not in memory_stats:
            print(f"✅ Memory Usage:")
            print(f"   Initial: {memory_stats['initial_mb']:.1f} MB")
            print(f"   Peak: {memory_stats['peak_mb']:.1f} MB")
            print(f"   Average: {memory_stats['average_mb']:.1f} MB")
            print(f"   Growth: {memory_stats['growth_mb']:.1f} MB")
            
            if memory_stats['peak_mb'] < 150:
                print("   🟢 Excellent memory efficiency")
            elif memory_stats['peak_mb'] < 250:
                print("   🟡 Good memory usage")
            else:
                print("   🔴 High memory usage - needs optimization")
                
            if memory_stats['growth_mb'] < 10:
                print("   🟢 No significant memory leaks detected")
            else:
                print("   🟡 Potential memory growth detected")
        else:
            print(f"❌ Memory test failed: {memory_stats['error']}")
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
    
    print()
    
    # Test 3: CPU Usage
    try:
        cpu_stats = test_cpu_usage()
        if 'error' not in cpu_stats:
            print(f"✅ CPU Usage:")
            print(f"   Average: {cpu_stats['average_cpu']:.1f}%")
            print(f"   Peak: {cpu_stats['peak_cpu']:.1f}%")
            print(f"   Idle: {cpu_stats['idle_cpu']:.1f}%")
            
            if cpu_stats['average_cpu'] < 5:
                print("   🟢 Excellent CPU efficiency")
            elif cpu_stats['average_cpu'] < 15:
                print("   🟡 Good CPU usage")
            else:
                print("   🔴 High CPU usage - needs optimization")
        else:
            print(f"❌ CPU test failed: {cpu_stats['error']}")
    except Exception as e:
        print(f"❌ CPU test failed: {e}")
    
    print()
    print("=" * 50)
    print("🏁 Performance testing complete!")
    
    # Performance recommendations
    print("\n💡 Performance Tips:")
    print("- Close unused applications before running PredatorSense")
    print("- Ensure adequate system RAM (8GB+ recommended)")
    print("- Use SSD storage for better I/O performance")
    print("- Keep system drivers updated")


if __name__ == "__main__":
    # Check if psutil is available
    try:
        import psutil
    except ImportError:
        print("❌ psutil not available. Install with: pip install psutil")
        sys.exit(1)
    
    run_performance_tests()