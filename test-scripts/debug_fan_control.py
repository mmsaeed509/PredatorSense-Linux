#!/usr/bin/env python3
"""
Debug script to investigate why Fan Control tab doesn't spin continuously in main app.
"""

import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from app.ui.main_window import CustomShapeWindow
from app.core import CoreController

class DebugFanControl(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Debug Fan Control - Main App vs Test")
        self.setGeometry(100, 100, 1400, 800)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Debug: Fan Control Animation Issue Investigation")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00B0C8; margin: 10px;")
        layout.addWidget(title)
        
        # Create the actual main window
        self.main_window = CustomShapeWindow()
        layout.addWidget(self.main_window)
        
        # Debug info
        self.debug_label = QLabel("Debug Info: Monitoring fan service...")
        self.debug_label.setStyleSheet("color: #ffffff; background: #1a1a1a; padding: 10px; font-family: monospace;")
        layout.addWidget(self.debug_label)
        
        # Control buttons
        controls_layout = QVBoxLayout()
        
        self.btn_check_service = QPushButton("Check Fan Service Status")
        self.btn_force_rpm = QPushButton("Force RPM Update (1500, 1300)")
        self.btn_start_service = QPushButton("Start Fan Service")
        self.btn_goto_fan_tab = QPushButton("Go to Fan Control Tab")
        
        # Connect buttons
        self.btn_check_service.clicked.connect(self.check_fan_service)
        self.btn_force_rpm.clicked.connect(self.force_rpm_update)
        self.btn_start_service.clicked.connect(self.start_fan_service)
        self.btn_goto_fan_tab.clicked.connect(self.goto_fan_tab)
        
        # Style buttons
        for btn in [self.btn_check_service, self.btn_force_rpm, self.btn_start_service, self.btn_goto_fan_tab]:
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
            """)
        
        controls_layout.addWidget(self.btn_check_service)
        controls_layout.addWidget(self.btn_force_rpm)
        controls_layout.addWidget(self.btn_start_service)
        controls_layout.addWidget(self.btn_goto_fan_tab)
        
        layout.addLayout(controls_layout)
        
        # Monitor timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.monitor_fan_service)
        self.monitor_timer.start(2000)  # Check every 2 seconds
        
        # Style the window
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
            }
        """)
        
        # Initial check
        self.check_fan_service()
    
    def check_fan_service(self):
        """Check the status of the fan service."""
        try:
            controller = self.main_window.controller
            fan_service = controller.fans
            
            debug_info = []
            debug_info.append(f"Fan Service Active: {fan_service._timer.isActive()}")
            debug_info.append(f"Timer Interval: {fan_service._timer.interval()}ms")
            debug_info.append(f"Poll Failures: {fan_service._poll_failures}")
            debug_info.append(f"Last RPM Values: {fan_service._last_rpm_values}")
            
            # Check if fan window exists
            if hasattr(self.main_window, 'fan_window') and self.main_window.fan_window:
                debug_info.append("Fan Window: EXISTS")
                fan_window = self.main_window.fan_window
                
                # Check fan dial states
                if hasattr(fan_window, 'cpu_dial'):
                    cpu_dial = fan_window.cpu_dial
                    debug_info.append(f"CPU Dial RPM: {cpu_dial._rpm}")
                    debug_info.append(f"CPU Dial Target: {cpu_dial._target_rpm}")
                    debug_info.append(f"CPU Dial Timer Active: {cpu_dial._tick_timer.isActive()}")
                    debug_info.append(f"CPU Dial Spin Angle: {cpu_dial._spin_angle:.1f}°")
                
                if hasattr(fan_window, 'gpu_dial'):
                    gpu_dial = fan_window.gpu_dial
                    debug_info.append(f"GPU Dial RPM: {gpu_dial._rpm}")
                    debug_info.append(f"GPU Dial Target: {gpu_dial._target_rpm}")
                    debug_info.append(f"GPU Dial Timer Active: {gpu_dial._tick_timer.isActive()}")
                    debug_info.append(f"GPU Dial Spin Angle: {gpu_dial._spin_angle:.1f}°")
            else:
                debug_info.append("Fan Window: NOT CREATED YET")
            
            self.debug_label.setText("\n".join(debug_info))
            
        except Exception as e:
            self.debug_label.setText(f"Error checking fan service: {e}")
    
    def force_rpm_update(self):
        """Force an RPM update to test the connection."""
        try:
            controller = self.main_window.controller
            
            # Emit a test RPM update
            controller.fans.rpmUpdated.emit(1500, 1300)
            
            self.debug_label.setText(self.debug_label.text() + f"\n[{time.strftime('%H:%M:%S')}] Forced RPM update: CPU=1500, GPU=1300")
            
        except Exception as e:
            self.debug_label.setText(self.debug_label.text() + f"\nError forcing RPM update: {e}")
    
    def start_fan_service(self):
        """Start the fan service."""
        try:
            controller = self.main_window.controller
            controller.fans.start()
            
            self.debug_label.setText(self.debug_label.text() + f"\n[{time.strftime('%H:%M:%S')}] Fan service started")
            
        except Exception as e:
            self.debug_label.setText(self.debug_label.text() + f"\nError starting fan service: {e}")
    
    def goto_fan_tab(self):
        """Navigate to Fan Control tab."""
        try:
            # Simulate clicking Fan Control button
            self.main_window.onMenuSelected("Fan Control")
            
            self.debug_label.setText(self.debug_label.text() + f"\n[{time.strftime('%H:%M:%S')}] Navigated to Fan Control tab")
            
        except Exception as e:
            self.debug_label.setText(self.debug_label.text() + f"\nError navigating to Fan Control: {e}")
    
    def monitor_fan_service(self):
        """Continuously monitor fan service status."""
        try:
            controller = self.main_window.controller
            fan_service = controller.fans
            
            # Check if anything changed
            current_status = f"Timer: {fan_service._timer.isActive()}, RPM: {fan_service._last_rpm_values}"
            
            if hasattr(self, '_last_status') and self._last_status != current_status:
                self.debug_label.setText(self.debug_label.text() + f"\n[{time.strftime('%H:%M:%S')}] Status changed: {current_status}")
            
            self._last_status = current_status
            
        except Exception as e:
            pass  # Ignore monitoring errors

def main():
    app = QApplication(sys.argv)
    
    debug_window = DebugFanControl()
    debug_window.show()
    
    print("🔍 Debug Fan Control Started")
    print("Instructions:")
    print("1. Click 'Check Fan Service Status' to see current state")
    print("2. Click 'Go to Fan Control Tab' to navigate to the tab")
    print("3. Click 'Force RPM Update' to test if connection works")
    print("4. Watch the debug info for changes")
    print("5. Compare fan animation behavior with test scripts")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())