"""
Lightweight performance monitoring for the PredatorSense application.
"""
import time
import psutil
from typing import Dict, Optional
from PyQt5.QtCore import QObject, QTimer, pyqtSignal


class PerformanceMonitor(QObject):
    """Lightweight performance monitor to track app resource usage."""
    
    performanceUpdated = pyqtSignal(dict)  # Emits performance stats
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_stats)
        self._timer.setInterval(10000)  # Update every 10 seconds
        
        self._process = None
        self._start_time = time.time()
        self._enabled = False
        
        try:
            self._process = psutil.Process()
        except:
            pass
    
    def enable(self):
        """Enable performance monitoring."""
        self._enabled = True
        if not self._timer.isActive():
            self._timer.start()
    
    def disable(self):
        """Disable performance monitoring."""
        self._enabled = False
        if self._timer.isActive():
            self._timer.stop()
    
    def _update_stats(self):
        """Update performance statistics."""
        if not self._enabled or not self._process:
            return
        
        try:
            stats = {
                'cpu_percent': round(self._process.cpu_percent(), 1),
                'memory_mb': round(self._process.memory_info().rss / 1024 / 1024, 1),
                'memory_percent': round(self._process.memory_percent(), 1),
                'uptime_minutes': round((time.time() - self._start_time) / 60, 1),
                'num_threads': self._process.num_threads(),
            }
            
            # Add system-wide stats for context
            stats['system_cpu'] = round(psutil.cpu_percent(interval=None), 1)
            stats['system_memory'] = round(psutil.virtual_memory().percent, 1)
            
            self.performanceUpdated.emit(stats)
            
            # Auto-disable if memory usage gets too high (>500MB)
            if stats['memory_mb'] > 500:
                print(f"Warning: High memory usage detected: {stats['memory_mb']}MB")
                
        except Exception as e:
            print(f"Performance monitoring error: {e}")
    
    def get_current_stats(self) -> Optional[Dict]:
        """Get current performance stats synchronously."""
        if not self._process:
            return None
        
        try:
            return {
                'cpu_percent': round(self._process.cpu_percent(), 1),
                'memory_mb': round(self._process.memory_info().rss / 1024 / 1024, 1),
                'memory_percent': round(self._process.memory_percent(), 1),
                'uptime_minutes': round((time.time() - self._start_time) / 60, 1),
                'num_threads': self._process.num_threads(),
            }
        except:
            return None


# Global performance monitor instance
perf_monitor = PerformanceMonitor()