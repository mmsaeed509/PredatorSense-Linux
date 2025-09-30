from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush, QRegion, QPolygon, QPen
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from app.utils.ui_utils import CircularGauge, ModeButton
from app.core import CoreController, OverclockLevel
from config import DEFAULT_FONT_FAMILY

class OverclockingWindow(QWidget):
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

        # Not implemented message
        title = QLabel("GPU Overclocking")
        title.setStyleSheet("color: #9aa0a6; font-size: 24px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        warning = QLabel("⚠️ Feature Not Available")
        warning.setStyleSheet("color: #e74c3c; font-size: 20px; font-weight: bold;")
        warning.setAlignment(Qt.AlignCenter)
        layout.addWidget(warning)

        message = QLabel(
            "GPU Overclocking is currently not implemented in the Linuwu-Sense module.\n\n"
            "This feature requires kernel-level support to safely adjust GPU clock speeds.\n"
            "The feature may be added in future updates to the Linuwu-Sense module."
        )
        message.setStyleSheet("color: #9aa0a6; font-size: 14px;")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        layout.addWidget(message)

        layout.addStretch()

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
        self.loading_label.setStyleSheet("color: #9aa0a6; font-size: 14px;")
        self.loading_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.loading_label)
        layout.addStretch()

        # Wire up controller
        if self.controller:
            # Mode buttons
            self.btn_normal.clicked.connect(lambda: self._set_mode(OverclockLevel.NORMAL))
            self.btn_fast.clicked.connect(lambda: self._set_mode(OverclockLevel.FAST))
            self.btn_extreme.clicked.connect(lambda: self._set_mode(OverclockLevel.EXTREME))
            # Update UI when mode changes
            self.controller.overclockChanged.connect(self._on_mode_changed)
            # Set initial mode
            self._on_mode_changed(self.controller.overclock)

    def _set_mode(self, mode: OverclockLevel):
        if self.controller:
            self.controller.set_overclock(mode)

    def _on_mode_changed(self, mode: OverclockLevel):
        # Update button states
        self.btn_normal.setChecked(mode == OverclockLevel.NORMAL)
        self.btn_fast.setChecked(mode == OverclockLevel.FAST)
        self.btn_extreme.setChecked(mode == OverclockLevel.EXTREME)
        
        # Update clock speed based on mode
        if mode == OverclockLevel.NORMAL:
            self.clock_gauge.setValueAnimated(1770)
            self.loading_label.setText("Loading 26%")
        elif mode == OverclockLevel.FAST:
            self.clock_gauge.setValueAnimated(1900)
            self.loading_label.setText("Loading 48%") 
        else:  # EXTREME
            self.clock_gauge.setValueAnimated(2070)
            self.loading_label.setText("Loading 96%")

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
