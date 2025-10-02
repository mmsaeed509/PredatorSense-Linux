#!/usr/bin/env python3
"""
Test to verify fan animation spins at fixed speed regardless of RPM values.
"""

import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from app.utils.ui_utils import FanDial

class FixedSpeedAnimationTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fixed Speed Animation Test - Constant Spinning")
        self.setGeometry(100, 100, 1000, 500)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Fixed Speed Animation Test - Should Spin at Constant Speed")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00B0C8; margin: 10px;")
        layout.addWidget(title)
        
        # Fan dials with different RPM values
        fan_layout = QHBoxLayout()
        
        # Fan 1: 0 RPM
        fan1_container = QVBoxLayout()
        fan1_label = QLabel("0 RPM\n(Should still spin at fixed speed)")
        fan1_label.setAlignment(Qt.AlignCenter)
        fan1_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        
        self.fan1 = FanDial("0 RPM", 0)
        self.fan1.setStyleSheet("background-color: #1a1a1a;")
        
        fan1_container.addWidget(fan1_label)
        fan1_container.addWidget(self.fan1)
        
        # Fan 2: 2000 RPM
        fan2_container = QVBoxLayout()
        fan2_label = QLabel("2000 RPM\n(Should spin at same fixed speed)")
        fan2_label.setAlignment(Qt.AlignCenter)
        fan2_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        
        self.fan2 = FanDial("2000 RPM", 2000)
        self.fan2.setStyleSheet("background-color: #1a1a1a;")
        
        fan2_container.addWidget(fan2_label)
        fan2_container.addWidget(self.fan2)
        
        # Fan 3: 5000 RPM
        fan3_container = QVBoxLayout()
        fan3_label = QLabel("5000 RPM\n(Should spin at same fixed speed)")
        fan3_label.setAlignment(Qt.AlignCenter)
        fan3_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        
        self.fan3 = FanDial("5000 RPM", 5000)
        self.fan3.setStyleSheet("background-color: #1a1a1a;")
        
        fan3_container.addWidget(fan3_label)
        fan3_container.addWidget(self.fan3)
        
        fan_layout.addLayout(fan1_container)
        fan_layout.addLayout(fan2_container)
        fan_layout.addLayout(fan3_container)
        layout.addLayout(fan_layout)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.btn_set_zero = QPushButton("Set All to 0 RPM")
        self.btn_set_high = QPushButton("Set All to 4000 RPM")
        self.btn_set_random = QPushButton("Set Random RPM")
        
        self.btn_set_zero.clicked.connect(self.set_all_zero)
        self.btn_set_high.clicked.connect(self.set_all_high)
        self.btn_set_random.clicked.connect(self.set_random_rpm)
        
        for btn in [self.btn_set_zero, self.btn_set_high, self.btn_set_random]:
            btn.setStyleSheet("""
                QPushButton {
                    background: #1a1a1a;
                    color: #cfcfcf;
                    border: 1px solid #2a2a2a;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    border-color: #00B0C8;
                }
            """)
        
        controls_layout.addWidget(self.btn_set_zero)
        controls_layout.addWidget(self.btn_set_high)
        controls_layout.addWidget(self.btn_set_random)
        layout.addLayout(controls_layout)
        
        # Status
        status = QLabel("✅ All fans should spin at the SAME FIXED SPEED regardless of RPM values\n🎯 Animation speed is now independent of actual fan RPM")
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("color: #9aa0a6; margin: 10px;")
        layout.addWidget(status)
        
        # Monitor angles to verify fixed speed
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.monitor_angles)
        self.monitor_timer.start(1000)  # Check every second
        
        self.prev_angles = [0, 0, 0]
        
        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
            }
        """)
    
    def set_all_zero(self):
        """Set all fans to 0 RPM - should still spin at fixed speed."""
        self.fan1.setRpm(0)
        self.fan2.setRpm(0)
        self.fan3.setRpm(0)
        print("Set all fans to 0 RPM - should still spin at fixed speed")
    
    def set_all_high(self):
        """Set all fans to high RPM - should spin at same fixed speed."""
        self.fan1.setRpm(4000)
        self.fan2.setRpm(4000)
        self.fan3.setRpm(4000)
        print("Set all fans to 4000 RPM - should spin at same fixed speed")
    
    def set_random_rpm(self):
        """Set random RPM values - should all spin at same fixed speed."""
        import random
        rpm1 = random.randint(0, 5000)
        rpm2 = random.randint(0, 5000)
        rpm3 = random.randint(0, 5000)
        
        self.fan1.setRpm(rpm1)
        self.fan2.setRpm(rpm2)
        self.fan3.setRpm(rpm3)
        print(f"Set random RPM: {rpm1}, {rpm2}, {rpm3} - should all spin at same fixed speed")
    
    def monitor_angles(self):
        """Monitor fan angles to verify they're all rotating at the same speed."""
        try:
            angles = [
                self.fan1._spin_angle,
                self.fan2._spin_angle,
                self.fan3._spin_angle
            ]
            
            # Calculate angle changes (should be approximately the same for all fans)
            angle_changes = []
            for i, (current, prev) in enumerate(zip(angles, self.prev_angles)):
                change = (current - prev) % 360
                angle_changes.append(change)
            
            # Check if all fans are rotating at similar speeds
            if len(set(self.prev_angles)) > 1:  # Not first measurement
                avg_change = sum(angle_changes) / len(angle_changes)
                max_diff = max(abs(change - avg_change) for change in angle_changes)
                
                if max_diff < 5:  # Within 5 degrees tolerance
                    print(f"✅ All fans rotating at consistent speed: {avg_change:.1f}°/sec")
                else:
                    print(f"⚠️ Speed variation detected: changes={angle_changes}")
            
            self.prev_angles = angles
            
        except Exception as e:
            print(f"Monitor error: {e}")

def main():
    app = QApplication(sys.argv)
    
    test_window = FixedSpeedAnimationTest()
    test_window.show()
    
    print("🚀 Fixed Speed Animation Test Started")
    print("Expected behavior:")
    print("  ✅ All fans should spin at the same constant speed")
    print("  ✅ Speed should NOT change when RPM values change")
    print("  ✅ Animation should be smooth and continuous")
    print("  ✅ Even 0 RPM fans should spin at fixed speed")
    print("\nUse buttons to test different RPM values.")
    print("All fans should maintain the same visual spinning speed.")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())