#!/usr/bin/env python3
"""
Isolated test to check if FanDial works correctly when created with initial RPM.
"""

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from app.utils.ui_utils import FanDial

class IsolatedFanDialTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Isolated FanDial Test - Check Initial RPM")
        self.setGeometry(100, 100, 800, 400)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Isolated FanDial Test - Should Start Spinning Immediately")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00B0C8; margin: 10px;")
        layout.addWidget(title)
        
        # Fan dials with different initial values
        fan_layout = QHBoxLayout()
        
        # Test 1: FanDial with 0 RPM (should still spin slowly)
        zero_container = QVBoxLayout()
        zero_label = QLabel("Initial RPM: 0")
        zero_label.setAlignment(Qt.AlignCenter)
        zero_label.setStyleSheet("color: #ffffff; font-size: 14px;")
        
        self.zero_fan = FanDial("Zero", 0)
        self.zero_fan.setStyleSheet("background-color: #1a1a1a;")
        
        zero_container.addWidget(zero_label)
        zero_container.addWidget(self.zero_fan)
        
        # Test 2: FanDial with 1200 RPM (should spin faster)
        rpm_container = QVBoxLayout()
        rpm_label = QLabel("Initial RPM: 1200")
        rpm_label.setAlignment(Qt.AlignCenter)
        rpm_label.setStyleSheet("color: #ffffff; font-size: 14px;")
        
        self.rpm_fan = FanDial("RPM", 1200)
        self.rpm_fan.setStyleSheet("background-color: #1a1a1a;")
        
        rpm_container.addWidget(rpm_label)
        rpm_container.addWidget(self.rpm_fan)
        
        # Test 3: FanDial created with 0, then set to 1500
        set_container = QVBoxLayout()
        set_label = QLabel("Set to 1500 after creation")
        set_label.setAlignment(Qt.AlignCenter)
        set_label.setStyleSheet("color: #ffffff; font-size: 14px;")
        
        self.set_fan = FanDial("Set", 0)
        self.set_fan.setStyleSheet("background-color: #1a1a1a;")
        # Set RPM after creation
        self.set_fan.setRpm(1500)
        
        set_container.addWidget(set_label)
        set_container.addWidget(self.set_fan)
        
        fan_layout.addLayout(zero_container)
        fan_layout.addLayout(rpm_container)
        fan_layout.addLayout(set_container)
        layout.addLayout(fan_layout)
        
        # Status info
        self.status_label = QLabel("Monitoring fan states...")
        self.status_label.setStyleSheet("color: #9aa0a6; background: #1a1a1a; padding: 10px; font-family: monospace;")
        layout.addWidget(self.status_label)
        
        # Monitor timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_status)
        self.monitor_timer.start(1000)  # Update every second
        
        # Style the window
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
            }
        """)
        
        # Initial status
        self.update_status()
    
    def update_status(self):
        """Update status information."""
        try:
            status_lines = []
            
            # Zero RPM fan
            status_lines.append(f"Zero Fan - RPM: {self.zero_fan._rpm}, Target: {self.zero_fan._target_rpm}, Timer: {self.zero_fan._tick_timer.isActive()}, Angle: {self.zero_fan._spin_angle:.1f}°")
            
            # 1200 RPM fan
            status_lines.append(f"RPM Fan - RPM: {self.rpm_fan._rpm}, Target: {self.rpm_fan._target_rpm}, Timer: {self.rpm_fan._tick_timer.isActive()}, Angle: {self.rpm_fan._spin_angle:.1f}°")
            
            # Set RPM fan
            status_lines.append(f"Set Fan - RPM: {self.set_fan._rpm}, Target: {self.set_fan._target_rpm}, Timer: {self.set_fan._tick_timer.isActive()}, Angle: {self.set_fan._spin_angle:.1f}°")
            
            self.status_label.setText("\n".join(status_lines))
            
        except Exception as e:
            self.status_label.setText(f"Error: {e}")

def main():
    app = QApplication(sys.argv)
    
    test_window = IsolatedFanDialTest()
    test_window.show()
    
    print("🔍 Isolated FanDial Test Started")
    print("Expected behavior:")
    print("  - All fans should be spinning continuously")
    print("  - Zero fan should spin slowly (minimum speed)")
    print("  - RPM fan should spin faster (based on 1200 RPM)")
    print("  - Set fan should spin fastest (based on 1500 RPM)")
    print("  - All timers should be active")
    print("  - Angles should be continuously changing")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())