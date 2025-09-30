from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush, QRegion, QPolygon, QPen, QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QSizePolicy, QButtonGroup, QSlider)
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
        self.btn_custom.setEnabled(True)  # Enable custom mode button
        
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

        # Add sliders for custom control
        self.cpu_slider = QSlider(Qt.Horizontal)
        self.gpu_slider = QSlider(Qt.Horizontal)
        self._setup_slider(self.cpu_slider)
        self._setup_slider(self.gpu_slider)
        
        # Add auto revert buttons
        self.cpu_auto = QPushButton("Auto")
        self.gpu_auto = QPushButton("Auto") 
        self._setup_auto_button(self.cpu_auto)
        self._setup_auto_button(self.gpu_auto)
        
        # Add sliders to layout
        slider_box = QVBoxLayout()
        
        # Create styled labels
        cpu_label = QLabel("CPU Fan:")
        gpu_label = QLabel("GPU Fan:")
        for label in (cpu_label, gpu_label):
            label.setStyleSheet("color: #00B0C8; font-weight: bold;")
            label.setFont(font_label)
        
        cpu_row = QHBoxLayout()
        cpu_row.addWidget(cpu_label)
        cpu_row.addWidget(self.cpu_slider)
        cpu_row.addWidget(self.cpu_auto)
        
        gpu_row = QHBoxLayout()
        gpu_row.addWidget(gpu_label)
        gpu_row.addWidget(self.gpu_slider)
        gpu_row.addWidget(self.gpu_auto)
        
        slider_box.addLayout(cpu_row)
        slider_box.addLayout(gpu_row)
        
        vbox.addLayout(slider_box)
        
        # Connect signals
        self.cpu_slider.valueChanged.connect(self._on_sliders_changed)
        self.gpu_slider.valueChanged.connect(self._on_sliders_changed)
        self.cpu_auto.clicked.connect(lambda: self._on_auto_clicked('cpu'))
        self.gpu_auto.clicked.connect(lambda: self._on_auto_clicked('gpu'))

    def _setup_slider(self, slider):
        slider.setRange(0, 100)
        slider.setValue(0)
        slider.setEnabled(False)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00B0C8;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)

    def _setup_auto_button(self, button):
        button.setEnabled(False)
        button.setStyleSheet("""
            QPushButton {
                background: #1a1a1a;
                color: #cfcfcf;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                border-color: #00B0C8;
            }
        """)

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
        
        # Enable/disable sliders based on mode
        is_custom = (mode == 'custom')
        self.cpu_slider.setEnabled(is_custom)
        self.gpu_slider.setEnabled(is_custom)
        self.cpu_auto.setEnabled(is_custom)
        self.gpu_auto.setEnabled(is_custom)
        
        if not is_custom:
            # Reset sliders when leaving custom mode
            self.cpu_slider.setValue(0)
            self.gpu_slider.setValue(0)

        # TODO: Apply the fan mode to the system
        # This would involve calling the appropriate controller method
        # For example: self.controller.set_fan_mode(mode)
    
    def _load_saved_mode(self):
        """Load the saved fan mode and slider values from config and update UI."""
        saved_mode = config_manager.get('fan_mode', 'auto')
        
        # Load saved slider values
        cpu_speed = config_manager.get('cpu_fan_speed', 0)
        gpu_speed = config_manager.get('gpu_fan_speed', 0)
        
        # Set slider values
        self.cpu_slider.setValue(cpu_speed)
        self.gpu_slider.setValue(gpu_speed)
        
        # Apply mode (this will enable/disable sliders as needed)
        self._on_mode_selected(saved_mode)
        
        # If custom mode, apply saved speeds
        if saved_mode == 'custom':
            try:
                self.controller.fans.set_custom(cpu_speed, gpu_speed)
            except Exception as e:
                print(f"Failed to restore custom speeds: {e}")

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

    def _on_sliders_changed(self):
        if self.get_current_mode() == 'custom':
            try:
                cpu_value = self.cpu_slider.value()
                gpu_value = self.gpu_slider.value()
                
                # Save slider values to config
                config_manager.set('cpu_fan_speed', cpu_value)
                config_manager.set('gpu_fan_speed', gpu_value)
                
                self.controller.fans.set_custom(cpu_value, gpu_value)
            except Exception as e:
                print(f"Failed to set custom speeds: {e}")

    def _on_auto_clicked(self, fan: str):
        if fan == 'cpu':
            self.cpu_slider.setValue(0)
        else:
            self.gpu_slider.setValue(0)
