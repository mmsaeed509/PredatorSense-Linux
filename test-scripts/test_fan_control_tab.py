#!/usr/bin/env python3
"""
Test script to verify Fan Control tab animation works like test_fan_animation.py
"""

import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from app.ui.fan_control_window import FanControlWindow
from app.core import CoreController

class FanControlTabTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fan Control Tab Test - Continuous Spinning")
        self.setGeometry(100, 100, 1200, 700)
        
        # Create controller
        self.controller = CoreController()
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Fan Control Tab Test - Should Spin Like test_fan_animation.py")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00B0C8; margin: 10px;")
        layout.addWidget(title)
        
        # Create the actual Fan Control Window
        self.fan_control = FanControlWindow(self, controller=self.controller)
        layout.addWidget(self.fan_control)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        # Test buttons
        self.btn_test_low = QPushButton("Test Low RPM (500)")
        self.btn_test_medium = QPushButton("Test Medium RPM (2000)")
        self.btn_test_high = QPushButton("Test High RPM (4000)")
        self.btn_test_zero = QPushButton("Test Zero RPM (0)")
        
        # Connect test buttons
        self.btn_test_low.clicked.connect(lambda: self.set_test_rpm(500, 600))
        self.btn_test_medium.clicked.connect(lambda: self.set_test_rpm(2000, 2200))
        self.btn_test_high.clicked.connect(lambda: self.set_test_rpm(4000, 4200))
        self.btn_test_zero.clicked.connect(lambda: self.set_test_rpm(0, 0))
        
        # Style buttons
        for btn in [self.btn_test_low, self.btn_test_medium, self.btn_test_high, self.btn_test_zero]:
            btn.setStyleSheet("""
                QPushButton {
                    background: #1a1a1a;
                    color: #cfcfcf;
                    border: 1px solid #2a2a2a;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    border-color: #00B0C8;
                    color: #00B0C8;
                }
                QPushButton:pressed {
                    background: #0e2c31;
                }
            """)
        
        controls_layout.addWidget(self.btn_test_low)
        controls_layout.addWidget(self.btn_test_medium)
        controls_layout.addWidget(self.btn_test_high)
        controls_layout.addWidget(self.btn_test_zero)
        
        layout.addLayout(controls_layout)
        
        # Status
        status = QLabel("✅ Fans should spin continuously like in test_fan_animation.py\n🎯 Click buttons to test different RPM values")
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("color: #9aa0a6; margin: 10px;")
        layout.addWidget(status)
        
        # Auto-cycle timer for demonstration
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.auto_cycle)
        self.auto_timer.start(4000)  # Change every 4 seconds
        self.cycle_step = 0
        
        # Style the window
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
            }
        """)
        
        # Set initial RPM values to start spinning immediately
        self.set_test_rpm(1200, 1000)
    
    def set_test_rpm(self, cpu_rpm: int, gpu_rpm: int):
        """Set test RPM values for the fan dials."""
        print(f"Setting test RPM: CPU={cpu_rpm}, GPU={gpu_rpm}")
        self.fan_control.setRpm(cpu_rpm, gpu_rpm)
    
    def auto_cycle(self):
        """Automatically cycle through different RPM values."""
        test_values = [
            (0, 0),
            (800, 900),
            (2000, 2100),
            (3500, 3600),
            (1200, 1300),
            (0, 0),
            (1500, 1600)
        ]
        
        if self.cycle_step < len(test_values):
            cpu_rpm, gpu_rpm = test_values[self.cycle_step]
            self.set_test_rpm(cpu_rpm, gpu_rpm)
            print(f"Auto-cycle step {self.cycle_step + 1}: CPU={cpu_rpm}, GPU={gpu_rpm}")
            self.cycle_step += 1
        else:
            self.cycle_step = 0  # Loop the cycle

def main():
    app = QApplication(sys.argv)
    
    test_window = FanControlTabTest()
    test_window.show()
    
    print("🚀 Fan Control Tab Test Started")
    print("Expected behavior:")
    print("  ✅ Fan Control tab should work exactly like test_fan_animation.py")
    print("  ✅ Continuous spinning even at 0 RPM")
    print("  ✅ No start/stop stuttering behavior")
    print("  ✅ Smooth animation at all RPM levels")
    print("  ✅ Immediate response to RPM changes")
    print("\nUse the test buttons to manually set different RPM values.")
    print("Auto-cycle will demonstrate different values every 4 seconds.")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())