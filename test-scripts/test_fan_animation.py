#!/usr/bin/env python3
"""
Test script to verify fan animation improvements.
"""

import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt, QTimer
from app.utils.ui_utils import FanDial

class FanAnimationTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fan Animation Test - Continuous Spinning")
        self.setGeometry(100, 100, 800, 400)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Fan Animation Test - Should Spin Continuously")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00B0C8; margin: 10px;")
        layout.addWidget(title)
        
        # Fan dials
        fan_layout = QHBoxLayout()
        
        # CPU Fan
        cpu_container = QVBoxLayout()
        cpu_label = QLabel("CPU Fan")
        cpu_label.setAlignment(Qt.AlignCenter)
        cpu_label.setStyleSheet("color: #ffffff; font-size: 14px;")
        
        self.cpu_fan = FanDial("CPU", 0)
        self.cpu_fan.setStyleSheet("background-color: #1a1a1a;")
        
        cpu_container.addWidget(cpu_label)
        cpu_container.addWidget(self.cpu_fan)
        
        # GPU Fan
        gpu_container = QVBoxLayout()
        gpu_label = QLabel("GPU Fan")
        gpu_label.setAlignment(Qt.AlignCenter)
        gpu_label.setStyleSheet("color: #ffffff; font-size: 14px;")
        
        self.gpu_fan = FanDial("GPU", 0)
        self.gpu_fan.setStyleSheet("background-color: #1a1a1a;")
        
        gpu_container.addWidget(gpu_label)
        gpu_container.addWidget(self.gpu_fan)
        
        fan_layout.addLayout(cpu_container)
        fan_layout.addLayout(gpu_container)
        layout.addLayout(fan_layout)
        
        # Controls
        controls_layout = QVBoxLayout()
        
        # CPU RPM Slider
        cpu_slider_layout = QHBoxLayout()
        cpu_slider_label = QLabel("CPU RPM:")
        cpu_slider_label.setStyleSheet("color: #ffffff;")
        self.cpu_slider = QSlider(Qt.Horizontal)
        self.cpu_slider.setRange(0, 5000)
        self.cpu_slider.setValue(0)
        self.cpu_slider.valueChanged.connect(self.update_cpu_rpm)
        self.cpu_value_label = QLabel("0")
        self.cpu_value_label.setStyleSheet("color: #00B0C8; font-weight: bold;")
        
        cpu_slider_layout.addWidget(cpu_slider_label)
        cpu_slider_layout.addWidget(self.cpu_slider)
        cpu_slider_layout.addWidget(self.cpu_value_label)
        
        # GPU RPM Slider
        gpu_slider_layout = QHBoxLayout()
        gpu_slider_label = QLabel("GPU RPM:")
        gpu_slider_label.setStyleSheet("color: #ffffff;")
        self.gpu_slider = QSlider(Qt.Horizontal)
        self.gpu_slider.setRange(0, 5000)
        self.gpu_slider.setValue(0)
        self.gpu_slider.valueChanged.connect(self.update_gpu_rpm)
        self.gpu_value_label = QLabel("0")
        self.gpu_value_label.setStyleSheet("color: #00B0C8; font-weight: bold;")
        
        gpu_slider_layout.addWidget(gpu_slider_label)
        gpu_slider_layout.addWidget(self.gpu_slider)
        gpu_slider_layout.addWidget(self.gpu_value_label)
        
        controls_layout.addLayout(cpu_slider_layout)
        controls_layout.addLayout(gpu_slider_layout)
        layout.addLayout(controls_layout)
        
        # Status
        status = QLabel("✅ Fans should spin continuously even at 0 RPM\n🎯 Animation should be smooth without start/stop behavior")
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("color: #9aa0a6; margin: 10px;")
        layout.addWidget(status)
        
        # Auto-test timer
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self.auto_test)
        self.test_timer.start(3000)  # Change RPM every 3 seconds
        self.test_step = 0
        
        # Style the window
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00B0C8;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #007d8e;
                border-radius: 3px;
            }
        """)
    
    def update_cpu_rpm(self, value):
        self.cpu_fan.setRpm(value)
        self.cpu_value_label.setText(str(value))
    
    def update_gpu_rpm(self, value):
        self.gpu_fan.setRpm(value)
        self.gpu_value_label.setText(str(value))
    
    def auto_test(self):
        """Automatically test different RPM values."""
        test_values = [0, 1000, 2500, 4000, 0, 1500, 3000, 0]
        
        if self.test_step < len(test_values):
            rpm = test_values[self.test_step]
            self.cpu_slider.setValue(rpm)
            self.gpu_slider.setValue(rpm + 200)  # Slightly different for GPU
            print(f"Auto-test step {self.test_step + 1}: CPU={rpm}, GPU={rpm + 200}")
            self.test_step += 1
        else:
            self.test_step = 0  # Loop the test

def main():
    app = QApplication(sys.argv)
    
    test_window = FanAnimationTest()
    test_window.show()
    
    print("🚀 Fan Animation Test Started")
    print("Expected behavior:")
    print("  ✅ Fans should spin continuously, even at 0 RPM")
    print("  ✅ No start/stop stuttering behavior")
    print("  ✅ Smooth animation at all RPM levels")
    print("  ✅ Immediate response to RPM changes")
    print("\nUse the sliders to test different RPM values manually.")
    print("Auto-test will cycle through different values every 3 seconds.")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exi