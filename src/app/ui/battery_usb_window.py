from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush, QRegion, QPolygon, QPen, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget
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
        calib_layout.addWidget(QLabel("Battery Calibration content coming soon..."))
        calib_layout.addStretch()

        # Battery Limiter Tab
        limiter_tab = QWidget()
        limiter_layout = QVBoxLayout(limiter_tab)
        limiter_layout.addWidget(QLabel("Battery Limiter content coming soon..."))
        limiter_layout.addStretch()

        # USB Charging Tab
        usb_tab = QWidget()
        usb_layout = QVBoxLayout(usb_tab)
        usb_layout.addWidget(QLabel("USB Charging content coming soon..."))
        usb_layout.addStretch()

        # Add tabs
        self.tabs.addTab(calib_tab, "Battery Calibration 󰂃")
        self.tabs.addTab(limiter_tab, "Battery Limiter 󰂁")
        self.tabs.addTab(usb_tab, "USB Charging ⚡")
        layout.addWidget(self.tabs)

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
