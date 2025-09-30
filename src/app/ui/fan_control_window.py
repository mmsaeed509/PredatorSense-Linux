from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush, QRegion, QPolygon, QPen, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QButtonGroup
from app.utils.ui_utils import FanDial, ModeButton
from app.utils.config_utils import config_manager
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
        
        # Initialize mode tracking
        self._current_mode = None
        
        self._build_ui()
        self._load_saved_mode()

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
        
        # Map mode names to buttons for easier access
        self._mode_buttons = {
            'auto': self.btn_auto,
            'max': self.btn_max,
            'custom': self.btn_custom
        }

        # Connect button signals
        self.btn_auto.clicked.connect(lambda: self._on_mode_selected('auto'))
        self.btn_max.clicked.connect(lambda: self._on_mode_selected('max'))
        self.btn_custom.clicked.connect(lambda: self._on_mode_selected('custom'))

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
        
    def _on_mode_selected(self, mode: str):
        """Handle mode selection and update UI and settings."""
        if mode not in self._mode_buttons:
            return
            
        # Update button states
        for name, button in self._mode_buttons.items():
            button.setChecked(name == mode)
            
        # Save the selected mode
        self._current_mode = mode
        config_manager.set('fan_mode', mode)
        
        # TODO: Apply the fan mode to the system
        # This would involve calling the appropriate controller method
        # For example: self.controller.set_fan_mode(mode)
    
    def _load_saved_mode(self):
        """Load the saved fan mode from config and update UI."""
        saved_mode = config_manager.get('fan_mode', 'auto')
        self._on_mode_selected(saved_mode)
        
    def get_current_mode(self) -> str:
        """Get the currently selected fan mode."""
        return self._current_mode or 'auto'

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
