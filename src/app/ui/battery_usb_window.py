from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush, QRegion, QPolygon, QPen, QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTabWidget, QPushButton, QButtonGroup)
from app.core import CoreController
from config import DEFAULT_FONT_FAMILY

class BatteryUSBWindow(QWidget):
    def __init__(self, parent=None, controller: CoreController = None):
        super().__init__(parent)
        self.controller = controller
        self.setGeometry(300, 100, 1100, 600)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.polygon = self._create_mask()
        self._build_ui()

    def _create_mask(self):
        points = [
            QPoint(1080, 0), QPoint(1100, 20),
            QPoint(1100, 580), QPoint(1080, 600),
            QPoint(20, 600), QPoint(0, 580),
            QPoint(0, 560), QPoint(20, 540),
            QPoint(20, 60), QPoint(0, 40),
            QPoint(0, 20), QPoint(20, 0),
        ]
        polygon = QPolygon(points)
        self.setMask(QRegion(polygon))
        return polygon

    def _build_ui(self):
        wrapper = QWidget(self)
        wrapper.setAttribute(Qt.WA_TranslucentBackground)
        wrapper.setGeometry(30, 20, self.width() - 60, self.height() - 40)

        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(20)

        # Tab widget with custom style
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #1a1a1a;
                color: #9aa0a6;
                border: 1px solid #2a2a2a;
                padding: 8px 25px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #0e2c31;
                color: #00B0C8;
                border: 1px solid #00B0C8;
            }
            QTabBar::tab:hover:!selected {
                border-color: #00B0C8;
            }
        """)

        # Battery Calibration Tab
        calib_tab = QWidget()
        calib_layout = QVBoxLayout(calib_tab)
        calib_layout.setAlignment(Qt.AlignCenter)

        # Warning label
        warning = QLabel(
            "⚠️ Battery Calibration Process:\n\n"
            "This will calibrate your battery to provide more accurate readings.\n"
            "The process involves:\n"
            "1. Charging to 100%\n"
            "2. Draining to 0%\n"
            "3. Recharging to 100%\n\n"
            "⚡ DO NOT unplug AC power during calibration!"
        )
        warning.setStyleSheet("color: #e0e0e0; font-size: 14px;")
        warning.setAlignment(Qt.AlignCenter)
        calib_layout.addWidget(warning)
        calib_layout.addSpacing(20)

        # Status label
        self.calib_status = QLabel("Calibration Status: Not Running")
        self.calib_status.setStyleSheet("color: #9aa0a6; font-size: 14px;")
        self.calib_status.setAlignment(Qt.AlignCenter)
        calib_layout.addWidget(self.calib_status)
        calib_layout.addSpacing(20)

        # Control buttons
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Calibration")
        self.stop_btn = QPushButton("Stop Calibration")
        
        for btn in (self.start_btn, self.stop_btn):
            btn.setStyleSheet("""
                QPushButton {
                    background: #1a1a1a;
                    color: #e0e0e0;
                    border: 1px solid #2a2a2a;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    border-color: #00B0C8;
                }
                QPushButton:pressed {
                    background: #0e2c31;
                }
                QPushButton:disabled {
                    color: #666666;
                    border-color: #2a2a2a;
                }
            """)
            
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        calib_layout.addLayout(btn_layout)
        calib_layout.addStretch()

        # Battery Limiter Tab
        limiter_tab = QWidget()
        limiter_layout = QVBoxLayout(limiter_tab)
        limiter_layout.setAlignment(Qt.AlignCenter)

        # Info label
        info = QLabel(
            "󰂁 Battery Charging Limiter\n\n"
            "Limits battery charging to 80% capacity.\n"
            "This helps preserve battery health when the laptop\n"
            "is primarily used while plugged into AC power.\n\n"
            "Enable this feature if you mostly use your laptop\n"
            "connected to a power adapter."
        )
        info.setStyleSheet("color: #e0e0e0; font-size: 14px;")
        info.setAlignment(Qt.AlignCenter)
        limiter_layout.addWidget(info)
        limiter_layout.addSpacing(20)

        # Status label
        self.limiter_status = QLabel("Limiter Status: Disabled")
        self.limiter_status.setStyleSheet("color: #9aa0a6; font-size: 14px;")
        self.limiter_status.setAlignment(Qt.AlignCenter)
        limiter_layout.addWidget(self.limiter_status)
        limiter_layout.addSpacing(20)

        # Toggle button
        self.limiter_btn = QPushButton("Enable Limiter")
        self.limiter_btn.setStyleSheet("""
            QPushButton {
                background: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 150px;
            }
            QPushButton:hover {
                border-color: #00B0C8;
            }
            QPushButton:pressed {
                background: #0e2c31;
            }
            QPushButton:checked {
                background: #0e2c31;
                border-color: #00B0C8;
                color: #00B0C8;
            }
        """)
        self.limiter_btn.setCheckable(True)
        limiter_layout.addWidget(self.limiter_btn, alignment=Qt.AlignCenter)
        limiter_layout.addStretch()

        # USB Charging Tab
        usb_tab = QWidget()
        usb_layout = QVBoxLayout(usb_tab)
        usb_layout.setAlignment(Qt.AlignCenter)

        # Info label
        info = QLabel(
            "⚡ USB Power When Laptop is Off\n\n"
            "Allow USB ports to provide power for charging devices\n"
            "even when your laptop is turned off.\n\n"
            "You can set a battery threshold to automatically stop\n"
            "USB charging to preserve battery life."
        )
        info.setStyleSheet("color: #e0e0e0; font-size: 14px;")
        info.setAlignment(Qt.AlignCenter)
        usb_layout.addWidget(info)
        usb_layout.addSpacing(20)

        # Status label
        self.usb_status = QLabel("USB Charging: Disabled")
        self.usb_status.setStyleSheet("color: #9aa0a6; font-size: 14px;")
        self.usb_status.setAlignment(Qt.AlignCenter)
        usb_layout.addWidget(self.usb_status)
        usb_layout.addSpacing(20)

        # Mode buttons
        btn_layout = QHBoxLayout()
        self.usb_group = QButtonGroup()
        self.usb_group.setExclusive(True)

        for value in (0, 10, 20, 30):
            label = "Disabled" if value == 0 else f"Until {value}%"
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("value", value)  # Store threshold value
            btn.setStyleSheet("""
                QPushButton {
                    background: #1a1a1a;
                    color: #e0e0e0;
                    border: 1px solid #2a2a2a;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 14px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    border-color: #00B0C8;
                }
                QPushButton:pressed {
                    background: #0e2c31;
                }
                QPushButton:checked {
                    background: #0e2c31;
                    border-color: #00B0C8;
                    color: #00B0C8;
                }
            """)
            self.usb_group.addButton(btn)
            btn_layout.addWidget(btn)

        usb_layout.addLayout(btn_layout)
        usb_layout.addStretch()

        # Add tabs
        self.tabs.addTab(calib_tab, "Battery Calibration 󰂃")
        self.tabs.addTab(limiter_tab, "Battery Limiter 󰂁")
        self.tabs.addTab(usb_tab, "USB Charging ⚡")
        layout.addWidget(self.tabs)

        # Wire up controls
        if self.controller:
            self.start_btn.clicked.connect(self._start_calibration)
            self.stop_btn.clicked.connect(self._stop_calibration)
            self.controller.battery.calibrationStateChanged.connect(self._on_calib_state)
            self.limiter_btn.clicked.connect(self._toggle_limiter)
            self.controller.battery.limiterStateChanged.connect(self._on_limiter_state)
            self.usb_group.buttonClicked.connect(self._on_usb_button)
            self.controller.battery.usbChargingChanged.connect(self._on_usb_state)

    def _start_calibration(self):
        if self.controller:
            if self.controller.battery.start_calibration():
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
            
    def _stop_calibration(self):
        if self.controller:
            if self.controller.battery.stop_calibration():
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)

    def _toggle_limiter(self):
        if self.controller:
            enabled = self.limiter_btn.isChecked()
            if not self.controller.battery.set_limiter(enabled):
                # Revert button state if failed
                self.limiter_btn.setChecked(not enabled)

    def _on_calib_state(self, is_calibrating: bool):
        self.start_btn.setEnabled(not is_calibrating)
        self.stop_btn.setEnabled(is_calibrating)
        status = "Running" if is_calibrating else "Not Running"
        color = "#00B0C8" if is_calibrating else "#9aa0a6"
        self.calib_status.setText(f"Calibration Status: {status}")
        self.calib_status.setStyleSheet(f"color: {color}; font-size: 14px;")

    def _on_limiter_state(self, is_limited: bool):
        self.limiter_btn.setChecked(is_limited)
        status = "Enabled" if is_limited else "Disabled"
        color = "#00B0C8" if is_limited else "#9aa0a6"
        self.limiter_status.setText(f"Limiter Status: {status}")
        self.limiter_status.setStyleSheet(f"color: {color}; font-size: 14px;")
        self.limiter_btn.setText("Disable Limiter" if is_limited else "Enable Limiter")

    def _on_usb_button(self, button: QPushButton):
        if self.controller:
            value = button.property("value")
            if not self.controller.battery.set_usb_charging(value):
                # Reset selection on failure
                button.setChecked(False)

    def _on_usb_state(self, threshold: int):
        # Update button states
        for btn in self.usb_group.buttons():
            btn.setChecked(btn.property("value") == threshold)
        
        # Update status text
        if threshold == 0:
            status = "Disabled"
            color = "#9aa0a6"
        else:
            status = f"Active until {threshold}%"
            color = "#00B0C8"
        
        self.usb_status.setText(f"USB Charging: {status}")
        self.usb_status.setStyleSheet(f"color: {color}; font-size: 14px;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Panel fill
        painter.setBrush(QBrush(QColor("#121212")))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(self.polygon)

        # Cyan border
        pen = QPen(QColor("#00B0C8"), 3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPolygon(self.polygon)
