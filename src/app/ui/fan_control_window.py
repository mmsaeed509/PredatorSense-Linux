from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush, QRegion, QPolygon, QPen, QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QSizePolicy, QButtonGroup, QSlider)
from app.utils.ui_utils import FanDial, ModeButtonWithLabel
from app.utils.config_utils import config_manager
from app.core import CoreController
from config import DEFAULT_FONT_FAMILY
import math


class CustomFanIcon(QWidget):
    """Custom fan icon widget that matches the AeroBlade design."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(32, 32)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw fan icon similar to screenshot
        cx, cy = self.width() // 2, self.height() // 2
        radius = min(self.width(), self.height()) // 3
        
        # Outer ring
        painter.setPen(QPen(QColor("#00B0C8"), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(cx - radius, cy - radius, 2 * radius, 2 * radius)
        
        # Fan blades
        blades = 8
        blade_radius = radius + 4
        for i in range(blades):
            angle = math.radians(i * (360.0 / blades))
            x1 = cx + int(blade_radius * math.cos(angle))
            y1 = cy + int(blade_radius * math.sin(angle))
            x2 = cx + int((blade_radius - 6) * math.cos(angle + math.radians(15)))
            y2 = cy + int((blade_radius - 6) * math.sin(angle + math.radians(15)))
            painter.drawLine(x1, y1, x2, y2)


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

        # Track last used values
        self._last_cpu_value = 0
        self._last_gpu_value = 0
        
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
        font_brand = QFont(DEFAULT_FONT_FAMILY, 16, QFont.Bold)

        wrapper = QWidget(self)
        wrapper.setAttribute(Qt.WA_TranslucentBackground)
        wrapper.setGeometry(30, 20, self.width() - 60, self.height() - 40)

        vbox = QVBoxLayout(wrapper)
        vbox.setContentsMargins(20, 16, 20, 16)
        vbox.setSpacing(18)

        # Top row with AeroBlade™ 3D Fan in top right
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 10)
        
        # Add stretch to push content to the right
        top_row.addStretch()
        
        # Custom fan icon widget
        fan_icon = CustomFanIcon()
        fan_icon.setFixedSize(24, 24)
        top_row.addWidget(fan_icon)
        
        # Brand text
        brand_label = QLabel("AeroBlade™ 3D Fan")
        brand_label.setFont(font_brand)
        brand_label.setStyleSheet("color: #00B0C8; margin-left: 8px;")
        top_row.addWidget(brand_label)
        
        vbox.addLayout(top_row)

        # Fan speed header (centered)
        speed_header = QLabel("Fan speed")
        speed_header.setAlignment(Qt.AlignCenter)
        speed_header.setFont(font_title)
        speed_header.setStyleSheet("color: #9aa0a6; margin-top: 20px;")
        vbox.addWidget(speed_header)

        # Mode selector row - matching screenshot layout
        mode_row = QHBoxLayout()
        mode_row.setSpacing(20)
        mode_row.setContentsMargins(40, 10, 40, 10)

        # Custom predator-style mode buttons with proper sizing
        self.btn_auto = ModeButtonWithLabel("Auto")
        self.btn_max = ModeButtonWithLabel("Max") 
        self.btn_custom = ModeButtonWithLabel("Custom")
        
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

        # Center the buttons horizontally like in screenshot
        mode_row.addStretch(1)
        mode_row.addWidget(self.btn_auto)
        mode_row.addWidget(self.btn_max)
        mode_row.addWidget(self.btn_custom)
        mode_row.addStretch(1)
        vbox.addLayout(mode_row)

        # Center container for fans and controls
        center_container = QHBoxLayout()
        center_container.setSpacing(80)

        # CPU Fan column
        cpu_column = QVBoxLayout()
        cpu_column.setAlignment(Qt.AlignCenter)
        
        self.cpu_dial = FanDial("CPU", 0)  # Start with some RPM for immediate spinning
        self.cpu_dial.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        cpu_column.addWidget(self.cpu_dial)
        
        # CPU slider container
        cpu_slider_container = QVBoxLayout()
        cpu_slider_container.setSpacing(4)
        
        # Create styled CPU label
        cpu_label = QLabel("CPU Fan:")
        cpu_label.setStyleSheet("color: #00B0C8; font-weight: bold;")
        cpu_label.setFont(font_label)
        cpu_label.setAlignment(Qt.AlignCenter)
        cpu_slider_container.addWidget(cpu_label)
        
        # CPU slider group
        cpu_slider_group = QHBoxLayout()
        cpu_slider_group.setSpacing(8)
        
        self.cpu_slider = QSlider(Qt.Horizontal)
        self._setup_slider(self.cpu_slider)
        self.cpu_auto = QPushButton("Auto")
        self._setup_auto_button(self.cpu_auto)
        
        cpu_slider_group.addWidget(self.cpu_slider)
        cpu_slider_group.addWidget(self.cpu_auto)
        
        cpu_slider_container.addLayout(cpu_slider_group)
        cpu_column.addLayout(cpu_slider_container)
        
        # GPU Fan column
        gpu_column = QVBoxLayout()
        gpu_column.setAlignment(Qt.AlignCenter)
        
        self.gpu_dial = FanDial("GPU", 0)  # Start with some RPM for immediate spinning
        self.gpu_dial.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        gpu_column.addWidget(self.gpu_dial)
        
        # GPU slider container  
        gpu_slider_container = QVBoxLayout()
        gpu_slider_container.setSpacing(4)
        
        # Create styled GPU label
        gpu_label = QLabel("GPU Fan:")
        gpu_label.setStyleSheet("color: #00B0C8; font-weight: bold;")
        gpu_label.setFont(font_label)
        gpu_label.setAlignment(Qt.AlignCenter)
        gpu_slider_container.addWidget(gpu_label)
        
        # GPU slider group
        gpu_slider_group = QHBoxLayout()
        gpu_slider_group.setSpacing(8)
        
        self.gpu_slider = QSlider(Qt.Horizontal)
        self._setup_slider(self.gpu_slider)
        self.gpu_auto = QPushButton("Auto")
        self._setup_auto_button(self.gpu_auto)
        
        gpu_slider_group.addWidget(self.gpu_slider)
        gpu_slider_group.addWidget(self.gpu_auto)
        
        gpu_slider_container.addLayout(gpu_slider_group)
        gpu_column.addLayout(gpu_slider_container)

        # Add columns to center container
        center_container.addLayout(cpu_column)
        center_container.addLayout(gpu_column)
        
        vbox.addLayout(center_container)

        # Connect signals
        self.cpu_slider.valueChanged.connect(self._on_sliders_changed)
        self.gpu_slider.valueChanged.connect(self._on_sliders_changed)
        self.cpu_auto.clicked.connect(lambda: self._on_auto_clicked('cpu'))
        self.gpu_auto.clicked.connect(lambda: self._on_auto_clicked('gpu'))

    def _setup_slider(self, slider):
        slider.setRange(0, 100)
        slider.setValue(0)
        slider.setEnabled(False)
        slider.setMinimumWidth(200)  # Set minimum width for sliders
        slider.setStyleSheet("""
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
            QSlider:disabled {
                opacity: 0.6;
            }
            QSlider::handle:horizontal:disabled {
                background: #404040;
            }
            QSlider::sub-page:horizontal:disabled {
                background: #303030;
            }
        """)

    def _setup_auto_button(self, button):
        button.setEnabled(False)
        button.setCheckable(True)  # Make button toggleable
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
            QPushButton:checked {
                background: #0e2c31;
                border: 1px solid #00B0C8;
                color: #00B0C8;
            }
        """)

    def setRpm(self, cpu_rpm: int, gpu_rpm: int):
        """Update fan RPM values - always update to ensure smooth animation."""
        cpu_rpm = int(cpu_rpm)
        gpu_rpm = int(gpu_rpm)
        
        # Always update the dials - the FanDial class handles change detection internally
        self.cpu_dial.setRpm(cpu_rpm)
        self.gpu_dial.setRpm(gpu_rpm)
        
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
        
        # Enable/disable controls based on mode
        is_custom = (mode == 'custom')
        self.cpu_auto.setEnabled(is_custom)
        self.gpu_auto.setEnabled(is_custom)
        
        if mode == 'custom':
            # Restore custom mode state
            cpu_auto = config_manager.get('cpu_fan_auto', False)
            gpu_auto = config_manager.get('gpu_fan_auto', False)
            
            # Enable sliders but respect auto state
            self.cpu_slider.setEnabled(not cpu_auto)
            self.gpu_slider.setEnabled(not gpu_auto)
            
            # Restore auto button states
            self.cpu_auto.setChecked(cpu_auto)
            self.gpu_auto.setChecked(gpu_auto)
            
            # Restore saved values
            saved_cpu = config_manager.get('last_cpu_speed', 0)
            saved_gpu = config_manager.get('last_gpu_speed', 0)
            
            # Set slider positions
            self.cpu_slider.setValue(saved_cpu)
            self.gpu_slider.setValue(saved_gpu)
            
            # Apply the fan speeds
            try:
                current_cpu = 0 if cpu_auto else saved_cpu
                current_gpu = 0 if gpu_auto else saved_gpu
                self.controller.fans.set_custom(current_cpu, current_gpu)
            except Exception as e:
                print(f"Failed to restore custom speeds: {e}")
                
        elif mode == 'auto':
            # Switch to auto mode
            try:
                self.controller.fans.set_auto()
            except Exception as e:
                print(f"Failed to set auto mode: {e}")
            
        elif mode == 'max':
            # Switch to max mode
            try:
                self.controller.fans.set_max()
            except Exception as e:
                print(f"Failed to set max mode: {e}")
                
        # Disable sliders in non-custom modes
        if not is_custom:
            self.cpu_slider.setEnabled(False)
            self.gpu_slider.setEnabled(False)
            self.cpu_auto.setChecked(False)
            self.gpu_auto.setChecked(False)
    
    def _load_saved_mode(self):
        """Load the saved fan mode and slider values from config and update UI."""
        saved_mode = config_manager.get('fan_mode', 'auto')
        
        # Load last used values
        self._last_cpu_value = config_manager.get('last_cpu_speed', 0)
        self._last_gpu_value = config_manager.get('last_gpu_speed', 0)
        
        # Load current/auto states
        cpu_auto = config_manager.get('cpu_fan_auto', False)
        gpu_auto = config_manager.get('gpu_fan_auto', False)
        
        # Set initial slider values based on auto state
        self.cpu_slider.setValue(0 if cpu_auto else self._last_cpu_value)
        self.gpu_slider.setValue(0 if gpu_auto else self._last_gpu_value)
        
        # Apply mode (this will enable/disable controls)
        self._on_mode_selected(saved_mode)
        
        # If custom mode, apply saved speeds
        if saved_mode == 'custom':
            try:
                current_cpu = 0 if cpu_auto else self._last_cpu_value
                current_gpu = 0 if gpu_auto else self._last_gpu_value
                self.controller.fans.set_custom(current_cpu, current_gpu)
            except Exception as e:
                print(f"Failed to restore custom speeds: {e}")

    def get_current_mode(self) -> str:
        """Get the currently selected fan mode."""
        return self._current_mode or 'auto'

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Panel fill - darker background to match screenshot
        painter.setBrush(QBrush(QColor("#121212")))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(self.polygon)
        # Cyan border with subtle glow effect
        pen = QPen(QColor("#00B0C8"), 2)
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
        """Handle individual fan auto button clicks."""
        if self.get_current_mode() != 'custom':
            return
            
        try:
            button = self.cpu_auto if fan == 'cpu' else self.gpu_auto
            is_auto = button.isChecked()
            slider = self.cpu_slider if fan == 'cpu' else self.gpu_slider
            
            # Don't change slider value, just update its visual state
            slider.setEnabled(not is_auto)
            
            if fan == 'cpu':
                # Store current value
                self._last_cpu_value = slider.value()
                config_manager.set('last_cpu_speed', self._last_cpu_value)
                # Apply fan speed (0 if auto, current value otherwise)
                current_cpu = 0 if is_auto else slider.value()
                self.controller.fans.set_custom(current_cpu, self.gpu_slider.value())
                config_manager.set('cpu_fan_auto', is_auto)
            else:
                # Store current value
                self._last_gpu_value = slider.value()
                config_manager.set('last_gpu_speed', self._last_gpu_value)
                # Apply fan speed (0 if auto, current value otherwise)
                current_gpu = 0 if is_auto else slider.value()
                self.controller.fans.set_custom(self.cpu_slider.value(), current_gpu)
                config_manager.set('gpu_fan_auto', is_auto)
                
        except Exception as e:
            print(f"Failed to set {fan} fan to auto: {e}")
            print(f"Failed to set {fan} fan to auto: {e}")
