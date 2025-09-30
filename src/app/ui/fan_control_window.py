from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush, QRegion, QPolygon, QPen, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QButtonGroup
from app.utils.ui_utils import FanDial, ModeButton
from app.core import CoreController
from config import DEFAULT_FONT_FAMILY


class FanControlWindow(QWidget):
    """
    PredatorSense-style panel dedicated for Fan Control.
    Shows:
    - Header: "Fan speed"
    - Mode buttons: Auto (selected), Max, Custom (disabled for now)
    - Two big RPM readouts: CPU, GPU
    """

    def __init__(self, parent=None, controller: CoreController = None):
        super().__init__(parent)
        self.controller = controller
        # Position and size identical to InternalWindow
        self.setGeometry(300, 100, 1100, 600)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.polygon = self._create_mask()

        self._build_ui()

    # Panel mask (same shape as InternalWindow for consistency)
    def _create_mask(self):
        points = [
            QPoint(1080, 0),
            QPoint(1100, 20),
            QPoint(1100, 580),
            QPoint(1080, 600),
            QPoint(20, 600),
            QPoint(0, 580),
            QPoint(0, 560),
            QPoint(20, 540),
            QPoint(20, 60),
            QPoint(0, 40),
            QPoint(0, 20),
            QPoint(20, 0),
        ]
        polygon = QPolygon(points)
        self.setMask(QRegion(polygon))
        return polygon

    def _build_ui(self):
        font_title = QFont(DEFAULT_FONT_FAMILY, 12)
        font_label = QFont(DEFAULT_FONT_FAMILY, 10)

        wrapper = QWidget(self)
        wrapper.setAttribute(Qt.WA_TranslucentBackground)
        wrapper.setGeometry(30, 20, self.width() - 60, self.height() - 40)

        vbox = QVBoxLayout(wrapper)
        vbox.setContentsMargins(20, 16, 20, 16)
        vbox.setSpacing(18)

        # Header
        header = QLabel("Fan speed")
        header.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        header.setFont(font_title)
        header.setStyleSheet("color: #9aa0a6;")
        vbox.addWidget(header)

        # Mode selector row
        mode_row = QHBoxLayout()
        mode_row.setSpacing(18)

        # Custom predator-style mode buttons
        self.btn_auto = ModeButton("Auto", subglyph="A")
        self.btn_max = ModeButton("Max")
        self.btn_custom = ModeButton("Custom")
        self.btn_auto.setChecked(True)
        self.btn_custom.setEnabled(False)

        # Exclusive behavior
        def select(btn: ModeButton):
            self.btn_auto.setChecked(btn is self.btn_auto)
            self.btn_max.setChecked(btn is self.btn_max)
            self.btn_custom.setChecked(btn is self.btn_custom)

        self.btn_auto.clicked.connect(lambda: select(self.btn_auto))
        self.btn_max.clicked.connect(lambda: select(self.btn_max))
        self.btn_custom.clicked.connect(lambda: select(self.btn_custom))

        mode_row.addStretch(1)
        mode_row.addWidget(self.btn_auto)
        mode_row.addSpacing(12)
        mode_row.addWidget(self.btn_max)
        mode_row.addSpacing(12)
        mode_row.addWidget(self.btn_custom)
        mode_row.addStretch(1)
        vbox.addLayout(mode_row)

        # Animated RPM dials
        rpm_row = QHBoxLayout()
        rpm_row.setSpacing(80)

        self.cpu_dial = FanDial("CPU")
        self.gpu_dial = FanDial("GPU")
        self.cpu_dial.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gpu_dial.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        rpm_row.addWidget(self.cpu_dial, 1)
        rpm_row.addWidget(self.gpu_dial, 1)

        vbox.addLayout(rpm_row, 1)

    def setRpm(self, cpu_rpm: int, gpu_rpm: int):
        self.cpu_dial.setRpm(int(cpu_rpm))
        self.gpu_dial.setRpm(int(gpu_rpm))

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
