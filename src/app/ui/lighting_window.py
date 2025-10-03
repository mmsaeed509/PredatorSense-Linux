"""
RGB Keyboard Lighting Control Window - Clean & Modern Design
Supports Static (per-zone) and Dynamic (four-zone) modes
"""
from PyQt5.QtCore import Qt, QPoint, QTimer, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QBrush, QRegion, QPolygon, QPen, QFont, QLinearGradient, QImage, QPixmap
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                          QTabWidget, QSlider, QComboBox, QColorDialog, QGridLayout,
                          QFrame, QSizePolicy, QSpacerItem, QDialog, QLineEdit, QSpinBox)
from app.core import CoreController
from config import DEFAULT_FONT_FAMILY

class ColorSVPicker(QWidget):
    """Saturation/Value color picker widget"""
    colorChanged = pyqtSignal(float, float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hue = 0.0
        self.saturation = 1.0
        self.value = 1.0
        self.setMouseTracking(True)
    
    def set_hue(self, hue):
        self.hue = hue
        self.update()
    
    def set_color(self, s, v):
        self.saturation = s
        self.value = v
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw SV gradient
        for y in range(self.height()):
            for x in range(self.width()):
                s = x / self.width()
                v = 1.0 - (y / self.height())
                
                color = QColor()
                color.setHsvF(self.hue, s, v)
                painter.setPen(color)
                painter.drawPoint(x, y)
        
        # Draw cursor
        cursor_x = int(self.saturation * self.width())
        cursor_y = int((1.0 - self.value) * self.height())
        
        painter.setPen(QPen(QColor("#000000"), 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(cursor_x - 6, cursor_y - 6, 12, 12)
        
        painter.setPen(QPen(QColor("#ffffff"), 2))
        painter.drawEllipse(cursor_x - 6, cursor_y - 6, 12, 12)
    
    def mousePressEvent(self, event):
        self._update_from_mouse(event.pos())
    
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self._update_from_mouse(event.pos())
    
    def _update_from_mouse(self, pos):
        self.saturation = max(0.0, min(1.0, pos.x() / self.width()))
        self.value = max(0.0, min(1.0, 1.0 - (pos.y() / self.height())))
        self.update()
        self.colorChanged.emit(self.saturation, self.value)


class HueSlider(QWidget):
    """Vertical hue slider widget"""
    hueChanged = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hue = 0.0
        self.setMouseTracking(True)
    
    def set_hue(self, hue):
        self.hue = hue
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw hue gradient
        for y in range(self.height()):
            hue = y / self.height()
            color = QColor()
            color.setHsvF(hue, 1.0, 1.0)
            
            painter.setPen(color)
            painter.drawLine(0, y, self.width(), y)
        
        # Draw cursor
        cursor_y = int(self.hue * self.height())
        
        # Draw triangle cursor
        points = [
            QPoint(0, cursor_y),
            QPoint(15, cursor_y - 8),
            QPoint(15, cursor_y + 8)
        ]
        
        painter.setPen(QPen(QColor("#000000"), 2))
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawPolygon(QPolygon(points))
    
    def mousePressEvent(self, event):
        self._update_from_mouse(event.pos())
    
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self._update_from_mouse(event.pos())
    
    def _update_from_mouse(self, pos):
        self.hue = max(0.0, min(1.0, pos.y() / self.height()))
        self.update()
        self.hueChanged.emit(self.hue)


class SimpleColorButton(QPushButton):
    """Simple, clean color picker button"""
    
    def __init__(self, color="#4287f5", size=50, parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(size, size)
        self.clicked.connect(self._pick_color)
        self._update_style()
    
    def _update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                border: 2px solid #2a2a2a;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                border-color: #00B0C8;
                border-width: 3px;
            }}
            QPushButton:pressed {{
                border-color: #00d4e8;
            }}
        """)
    
    def _pick_color(self):
        color = QColorDialog.getColor(QColor(self._color), self, "Choose Color")
        if color.isValid():
            self._color = color.name()
            self._update_style()
    
    def get_color(self) -> str:
        return self._color
    
    def set_color(self, color: str):
        self._color = color
        self._update_style()


class PresetColorButton(QPushButton):
    """Preset color button for quick selection"""
    
    def __init__(self, color, name, parent=None):
        super().__init__(parent)
        self._color = color
        self._name = name
        self.setFixedSize(35, 35)
        self.setToolTip(name)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 1px solid #404040;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                border-color: #00B0C8;
                border-width: 2px;
            }}
        """)
    
    def get_color(self):
        return self._color


class PredatorStaticTab(QWidget):
    """Exact replica of PredatorSense Static lighting interface"""
    
    def __init__(self, controller: CoreController, parent=None):
        super().__init__(parent)
        self.controller = controller
        
        # Read current colors from system
        try:
            zone1, zone2, zone3, zone4, brightness = self.controller.lighting_service.get_current_zone_colors()
            self._zone_colors = [f"#{zone1}", f"#{zone2}", f"#{zone3}", f"#{zone4}"]
            self._brightness = brightness
        except Exception as e:
            print(f"Error reading current colors: {e}")
            self._brightness = 100
            self._zone_colors = ["#00ffff", "#ff00ff", "#00ffff", "#ff00ff"]  # Default cyan/purple
        
        self._keyboard_widget = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Brightness control (moved to top right)
        brightness_section = QHBoxLayout()
        brightness_section.addStretch()
        
        brightness_label = QLabel("Brightness:")
        brightness_label.setFont(QFont(DEFAULT_FONT_FAMILY, 12, QFont.Bold))
        brightness_label.setStyleSheet("color: #00B0C8;")
        brightness_section.addWidget(brightness_label)
        
        self._brightness_slider = QSlider(Qt.Horizontal)
        self._brightness_slider.setRange(0, 100)
        self._brightness_slider.setValue(self._brightness)
        self._brightness_slider.setFixedWidth(200)
        self._brightness_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #333333, stop:1 #00B0C8);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 2px solid #00B0C8;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #00B0C8;
            }
            QSlider::sub-page:horizontal {
                background: #00B0C8;
                border-radius: 4px;
            }
        """)
        self._brightness_slider.valueChanged.connect(self._brightness_changed)
        brightness_section.addWidget(self._brightness_slider)
        
        self._brightness_value = QLabel(f"{self._brightness}%")
        self._brightness_value.setStyleSheet("color: #00B0C8; font-weight: bold; font-size: 14px; min-width: 50px;")
        self._brightness_value.setAlignment(Qt.AlignCenter)
        brightness_section.addWidget(self._brightness_value)
        
        layout.addLayout(brightness_section)
        
        # Keyboard visualization
        keyboard_frame = QFrame()
        keyboard_frame.setMinimumHeight(230)
        keyboard_frame.setStyleSheet("""
            QFrame {
                background: #121212;
                border: 2px solid #121212;
                border-radius: 10px;
            }
        """)
        
        # Create keyboard layout
        keyboard_layout = QVBoxLayout(keyboard_frame)
        keyboard_layout.setContentsMargins(10, 10, 10, 10)
        
        # Keyboard visual representation
        self._keyboard_widget = self._create_keyboard_visual()
        keyboard_layout.addWidget(self._keyboard_widget, 1)  # Stretch to fill
        
        layout.addWidget(keyboard_frame, 1)  # Give it more space
        
        # Zone labels under the keyboard box
        zone_labels_section = QHBoxLayout()
        zone_labels_section.setSpacing(0)
        zone_labels_section.setContentsMargins(0, 5, 0, 5)
                
        for i in range(4):
            zone_label_container = QVBoxLayout()
            zone_label_container.setSpacing(2)
            zone_label_container.setAlignment(Qt.AlignCenter)
            
            # Zone number
            zone_num = QLabel(f"Zone {i+1}")
            zone_num.setAlignment(Qt.AlignCenter)
            zone_num.setStyleSheet("color: #00B0C8; font-size: 10px; font-weight: bold;")
            zone_label_container.addWidget(zone_num)
            
            zone_labels_section.addLayout(zone_label_container, 1)
        
        layout.addLayout(zone_labels_section)
        
        # Zone color controls
        zones_section = QHBoxLayout()
        zones_section.setSpacing(40)
        zones_section.setContentsMargins(30, 10, 30, 10)
        
        self._zone_color_buttons = []
        
        for i in range(4):
            zone_container = QVBoxLayout()
            zone_container.setSpacing(8)
            zone_container.setAlignment(Qt.AlignCenter)
            
            # Color picker button
            color_btn = SimpleColorButton(self._zone_colors[i], 50)
            color_btn.clicked.connect(lambda checked, zone=i, btn=color_btn: self._zone_color_picked(zone, btn))
            zone_container.addWidget(color_btn)
            
            self._zone_color_buttons.append(color_btn)
            zones_section.addLayout(zone_container)
        
        layout.addLayout(zones_section)
        layout.addStretch()
    
    def _create_keyboard_visual(self):
        """Create a realistic full-sized keyboard with 4 zones matching the screenshot"""
        keyboard_widget = QWidget()
        keyboard_widget.setMinimumSize(800, 200)  # Set minimum size
        
        # Use a custom paint event to draw the keyboard
        def paint_keyboard(event):
            painter = QPainter(keyboard_widget)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Black background
            painter.fillRect(0, 0, keyboard_widget.width(), keyboard_widget.height(), QColor("#121212"))
            
            # Calculate scaling based on available space with better margins
            margin = 10
            available_width = keyboard_widget.width() - (margin * 2)
            available_height = keyboard_widget.height() - (margin * 2)
            
            # Keyboard dimensions in units (22.5 units wide for full keyboard, 6.5 units tall)
            keyboard_width_units = 22.5
            keyboard_height_units = 8
            
            # Calculate unit size to fit available space
            unit_from_width = available_width / keyboard_width_units
            unit_from_height = available_height / keyboard_height_units
            unit = min(unit_from_width, unit_from_height)  # Use smaller to fit both dimensions
            
            # Ensure minimum unit size for visibility
            unit = max(unit, 8)
            
            gap = unit * 0.12  # Slightly smaller gap for better fit
            
            # Center the keyboard
            keyboard_actual_width = keyboard_width_units * unit
            keyboard_actual_height = keyboard_height_units * unit
            start_x = (keyboard_widget.width() - keyboard_actual_width) / 2
            start_y = (keyboard_widget.height() - keyboard_actual_height) / 2
            
            # Define keyboard layout with proper key sizes
            # Format: (x_offset, y_offset, width_units, height_units, zone)
            keys = []
            
            # Row 0: Function keys + extras
            row0_y = 0
            # Esc
            keys.append((0, row0_y, 1, 1, 0))
            # F1-F4 (zone 0)
            for i in range(1, 5):
                keys.append((i + 0.6, row0_y, 1, 1, 0))
            # F5-F8 (zone 1)
            for i in range(5, 9):
                keys.append((i + 0.8, row0_y, 1, 1, 1))
            # F9-F12 (zone 2)
            for i in range(9, 13):
                keys.append((i + 1, row0_y, 1, 1, 2))
            # Print, Scroll, Pause (zone 3)
            for i in range(13, 16):
                keys.append((i + 1.5, row0_y, 1, 1, 3))

            # Print, Scroll, Pause (zone 3)
            for i in range(16, 20):
                keys.append((i + 2, row0_y, 1, 1, 3))
            
            # Row 1: Number row
            row1_y = 1.8
            # ` to 5 (zone 0)
            for i in range(5):
                keys.append((i, row1_y, 1, 1, 0))
            # 6-7 (zone 1)
            for i in range(5, 9):
                keys.append((i, row1_y, 1, 1, 1))
            # 8-0 (zone 2)
            for i in range(9, 11):
                keys.append((i, row1_y, 1, 1, 2))
            # -=Backspace (zone 2)
            keys.append((11, row1_y, 1, 1, 2))
            keys.append((12, row1_y, 2, 1, 2))  # Backspace (2 units)
            # Ins, Home, PgUp (zone 3)
            keys.append((14.5, row1_y, 1, 1, 3))
            keys.append((15.5, row1_y, 1, 1, 3))
            keys.append((16.5, row1_y, 1, 1, 3))
            # Numpad (zone 3)
            keys.append((18, row1_y, 1, 1, 3))
            keys.append((19, row1_y, 1, 1, 3))
            keys.append((20, row1_y, 1, 1, 3))
            keys.append((21, row1_y, 1, 1, 3))
            
            # Row 2: QWERTY row
            row2_y = 2.8
            # Tab (zone 0)
            keys.append((0, row2_y, 1.5, 1, 0))
            # Q-T (zone 0)
            for i in range(1, 5):
                keys.append((i + 0.5, row2_y, 1, 1, 0))
            # Y-U (zone 1)
            for i in range(5, 9):
                keys.append((i + 0.5, row2_y, 1, 1, 1))
            # I-P (zone 2)
            for i in range(9, 11):
                keys.append((i + 0.5, row2_y, 1, 1, 2))
            # []\ (zone 2)
            keys.append((11.5, row2_y, 1, 1, 2))
            keys.append((12.5, row2_y, 1.5, 1, 2))
            # Del, End, PgDn (zone 3)
            keys.append((14.5, row2_y, 1, 1, 3))
            keys.append((15.5, row2_y, 1, 1, 3))
            keys.append((16.5, row2_y, 1, 1, 3))
            # Numpad (zone 3)
            keys.append((18, row2_y, 1, 1, 3))
            keys.append((19, row2_y, 1, 1, 3))
            keys.append((20, row2_y, 1, 1, 3))
            keys.append((21, row2_y, 1, 2, 3))  # + (2 units tall)
            
            # Row 3: ASDF row
            row3_y = 3.8
            # Caps (zone 0)
            keys.append((0, row3_y, 1.75, 1, 0))
            # A-G (zone 0)
            for i in range(1, 5):
                keys.append((i + 0.75, row3_y, 1, 1, 0))
            # H-J (zone 1)
            for i in range(5, 9):
                keys.append((i + 0.75, row3_y, 1, 1, 1))
            # K-; (zone 2)
            for i in range(9, 11):
                keys.append((i + 0.75, row3_y, 1, 1, 2))
            # '" (zone 2)
            keys.append((11.75, row3_y, 1, 1, 2))
            # Enter (zone 2)
            keys.append((12.75, row3_y, 1.2, 1, 2))
            # Numpad (zone 3)
            keys.append((18, row3_y, 1, 1, 3))
            keys.append((19, row3_y, 1, 1, 3))
            keys.append((20, row3_y, 1, 1, 3))
            
            # Row 4: ZXCV row
            row4_y = 4.8
            # LShift (zone 0)
            keys.append((0, row4_y, 2.25, 1, 0))
            # Z-V (zone 0)
            for i in range(2, 5):
                keys.append((i + 0.25, row4_y, 1, 1, 0))
            # B-N (zone 1)
            for i in range(5, 9):
                keys.append((i + 0.25, row4_y, 1, 1, 1))
            # M-/ (zone 2)
            for i in range(9, 11):
                keys.append((i + 0.25, row4_y, 1, 1, 2))
            # RShift (zone 2)
            keys.append((11.25, row4_y, 2.75, 1, 2))
            # Up arrow (zone 3)
            keys.append((15.5, row4_y, 1, 1, 3))
            # Numpad (zone 3)
            keys.append((18, row4_y, 1, 1, 3))
            keys.append((19, row4_y, 1, 1, 3))
            keys.append((20, row4_y, 1, 1, 3))
            keys.append((21, row4_y, 1, 2, 3))  # Enter (2 units tall)
            
            # Row 5: Bottom row
            row5_y = 5.8
            # Ctrl, Fn, Win, Alt (zone 0)
            keys.append((0, row5_y, 1.25, 1, 0))
            keys.append((1.25, row5_y, 1.25, 1, 0))
            keys.append((2.5, row5_y, 1.25, 1, 0))
            keys.append((3.75, row5_y, 1.25, 1, 0))
            # Spacebar (zone 1)
            keys.append((5, row5_y, 5.25, 1, 1))
            # AltGr, Menu, Ctrl (zone 2)
            keys.append((10.25, row5_y, 1.25, 1, 2))
            keys.append((11.5, row5_y, 1.25, 1, 2))
            keys.append((12.75, row5_y, 1.25, 1, 2))
            # Left, Down, Right arrows (zone 3)
            keys.append((14.5, row5_y, 1, 1, 3))
            keys.append((15.5, row5_y, 1, 1, 3))
            keys.append((16.5, row5_y, 1, 1, 3))
            # Numpad (zone 3)
            keys.append((18, row5_y, 2, 1, 3))  # 0 (2 units wide)
            keys.append((20, row5_y, 1, 1, 3))
            
            # Draw all keys
            for key_data in keys:
                x_units, y_units, w_units, h_units, zone = key_data
                
                x = start_x + x_units * (unit + gap)
                y = start_y + y_units * (unit + gap)
                w = w_units * unit + (w_units - 1) * gap
                h = h_units * unit + (h_units - 1) * gap
                
                # Get zone color
                zone_color = self._zone_colors[zone]
                
                # Draw key with black fill and colored border
                painter.setBrush(QBrush(QColor("#000000")))
                painter.setPen(QPen(QColor(zone_color), 2))
                painter.drawRoundedRect(int(x), int(y), int(w), int(h), 3, 3)
        
        keyboard_widget.paintEvent = paint_keyboard
        return keyboard_widget
    
    def _brightness_changed(self, value):
        self._brightness = value
        self._brightness_value.setText(f"{value}%")
        # Apply brightness change immediately
        self._apply_current_settings()
    
    def _zone_color_picked(self, zone_index, button):
        """Handle zone color picker change"""
        color = button.get_color()
        self._zone_colors[zone_index] = color
        # Trigger repaint of keyboard visual
        if self._keyboard_widget:
            self._keyboard_widget.update()
        # Apply color change immediately
        self._apply_current_settings()
    
    def _apply_current_settings(self):
        """Apply current zone colors and brightness"""
        try:
            # Convert colors to hex format
            hex_colors = []
            for color in self._zone_colors:
                if color.startswith('#'):
                    hex_colors.append(color[1:])
                else:
                    hex_colors.append(color)
            
            success = self.controller.lighting_service.set_per_zone_colors(
                hex_colors[0], hex_colors[1], hex_colors[2], hex_colors[3], 
                self._brightness
            )
            
            if success:
                print(f"Applied PredatorSense static lighting: zones={hex_colors}, brightness={self._brightness}")
                
                # Save settings for next time
                self.controller.settings.set_static_settings(
                    hex_colors[0], hex_colors[1], hex_colors[2], hex_colors[3],
                    self._brightness
                )
            
        except Exception as e:
            print(f"Error applying lighting: {e}")


class CleanDynamicTab(QWidget):
    """PredatorSense-style dynamic lighting control"""
    
    def __init__(self, controller: CoreController, parent=None):
        super().__init__(parent)
        self.controller = controller
        
        # Load saved settings
        saved_settings = self.controller.settings.get_dynamic_settings()
        self._current_color = saved_settings.get('color', '#00ffff')
        self._current_effect = saved_settings.get('effect', 4)
        self._speed = saved_settings.get('speed', 5)
        self._brightness = saved_settings.get('brightness', 100)
        self._direction = saved_settings.get('direction', 2)  # 2 = left to right (default)
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Brightness control at top (like Static tab)
        brightness_section = QHBoxLayout()
        brightness_section.addStretch()
        
        brightness_label = QLabel("Brightness:")
        brightness_label.setFont(QFont(DEFAULT_FONT_FAMILY, 12, QFont.Bold))
        brightness_label.setStyleSheet("color: #00B0C8;")
        brightness_section.addWidget(brightness_label)
        
        self._brightness_slider = QSlider(Qt.Horizontal)
        self._brightness_slider.setRange(0, 100)
        self._brightness_slider.setValue(self._brightness)
        self._brightness_slider.setFixedWidth(200)
        self._brightness_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #333333, stop:1 #00B0C8);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 2px solid #00B0C8;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #00B0C8;
            }
            QSlider::sub-page:horizontal {
                background: #00B0C8;
                border-radius: 4px;
            }
        """)
        self._brightness_slider.valueChanged.connect(self._brightness_changed)
        brightness_section.addWidget(self._brightness_slider)
        
        self._brightness_value = QLabel(f"{self._brightness}%")
        self._brightness_value.setStyleSheet("color: #00B0C8; font-weight: bold; font-size: 14px; min-width: 50px;")
        self._brightness_value.setAlignment(Qt.AlignCenter)
        brightness_section.addWidget(self._brightness_value)
        
        layout.addLayout(brightness_section)
        
        # Main content layout
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        
        # Light Effects section
        effects_frame = QFrame()
        effects_frame.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 1px solid #1A1A1A;
                border-radius: 8px;
            }
        """)
        effects_layout = QVBoxLayout(effects_frame)
        effects_layout.setContentsMargins(15, 15, 15, 15)
        effects_layout.setSpacing(10)
        
        effects_title = QLabel("Light Effects")
        effects_title.setFont(QFont(DEFAULT_FONT_FAMILY, 13, QFont.Bold))
        effects_title.setStyleSheet("color: #00B0C8;")
        effects_layout.addWidget(effects_title)
        
        # Effect buttons in 2 columns
        effects_grid = QGridLayout()
        effects_grid.setSpacing(8)
        
        effects = [
            (1, "Breathing"),
            (4, "Shifting"),
            (3, "Wave"),
            (2, "Neon"),
            (5, "Zoom"),
        ]
        
        self._effect_buttons = {}
        for i, (mode_id, name) in enumerate(effects):
            row = i // 3
            col = i % 3
            
            btn = QPushButton(name)
            btn.setFixedSize(120, 25)
            btn.setCheckable(True)
            btn.setStyleSheet(self._effect_button_style())
            btn.clicked.connect(lambda checked, m=mode_id: self._select_effect(m))
            
            effects_grid.addWidget(btn, row, col)
            self._effect_buttons[mode_id] = btn
        
        # Set saved/default selection
        if self._current_effect in self._effect_buttons:
            self._effect_buttons[self._current_effect].setChecked(True)
        else:
            self._effect_buttons[4].setChecked(True)  # Fallback to Shifting
        
        effects_layout.addLayout(effects_grid)
        content_layout.addWidget(effects_frame)
        
        # Speed and Direction row
        controls_row = QHBoxLayout()
        controls_row.setSpacing(15)
        
        # Speed section
        speed_frame = QFrame()
        speed_frame.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 1px solid #1A1A1A;
                border-radius: 8px;
            }
        """)
        speed_layout = QVBoxLayout(speed_frame)
        speed_layout.setContentsMargins(15, 10, 15, 10)
        speed_layout.setSpacing(8)
        
        speed_title = QLabel("Speed")
        speed_title.setFont(QFont(DEFAULT_FONT_FAMILY, 12, QFont.Bold))
        speed_title.setStyleSheet("color: #00B0C8;")
        speed_layout.addWidget(speed_title)
        
        self._speed_slider = QSlider(Qt.Horizontal)
        self._speed_slider.setRange(1, 9)
        self._speed_slider.setValue(self._speed)
        self._speed_slider.setStyleSheet(self._slider_style())
        self._speed_slider.valueChanged.connect(self._speed_changed)
        speed_layout.addWidget(self._speed_slider)
        
        controls_row.addWidget(speed_frame, 1)
        
        # Direction section
        direction_frame = QFrame()
        direction_frame.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 1px solid #1A1A1A;
                border-radius: 8px;
            }
        """)
        direction_layout = QVBoxLayout(direction_frame)
        direction_layout.setContentsMargins(15, 10, 15, 10)
        direction_layout.setSpacing(8)
        
        direction_title = QLabel("Direction")
        direction_title.setFont(QFont(DEFAULT_FONT_FAMILY, 12, QFont.Bold))
        direction_title.setStyleSheet("color: #00B0C8;")
        direction_layout.addWidget(direction_title)
        
        # Direction buttons
        direction_buttons_layout = QHBoxLayout()
        direction_buttons_layout.setSpacing(10)
        
        self._left_btn = QPushButton("→")
        self._left_btn.setFixedSize(50, 30)
        self._left_btn.setCheckable(True)
        self._left_btn.setStyleSheet(self._direction_button_style())
        self._left_btn.clicked.connect(lambda checked: self._set_direction(1) if checked else None)  # 1 = right to left
        
        self._right_btn = QPushButton("←")
        self._right_btn.setFixedSize(50, 30)
        self._right_btn.setCheckable(True)
        self._right_btn.setStyleSheet(self._direction_button_style())
        self._right_btn.clicked.connect(lambda checked: self._set_direction(2) if checked else None)  # 2 = left to right
        
        # Set saved direction
        if self._direction == 1:  # right to left (←)
            self._left_btn.setChecked(True)
        else:  # 2 = left to right (→)
            self._right_btn.setChecked(True)
        
        direction_buttons_layout.addWidget(self._left_btn)
        direction_buttons_layout.addWidget(self._right_btn)
        direction_buttons_layout.addStretch()
        
        direction_layout.addLayout(direction_buttons_layout)
        controls_row.addWidget(direction_frame, 1)
        
        content_layout.addLayout(controls_row)
        
        # Color sections
        self._color_sections_widget = QWidget()
        color_sections_layout = QVBoxLayout(self._color_sections_widget)
        color_sections_layout.setContentsMargins(0, 0, 0, 0)
        color_sections_layout.setSpacing(15)
        
        # Basic colors
        basic_colors_frame = QFrame()
        basic_colors_frame.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 1px solid #1A1A1A;
                border-radius: 8px;
            }
        """)
        basic_colors_layout = QVBoxLayout(basic_colors_frame)
        basic_colors_layout.setContentsMargins(15, 10, 15, 10)
        basic_colors_layout.setSpacing(8)
        
        basic_title = QLabel("Basic colors")
        basic_title.setFont(QFont(DEFAULT_FONT_FAMILY, 11, QFont.Bold))
        basic_title.setStyleSheet("color: #00B0C8;")
        basic_colors_layout.addWidget(basic_title)
        
        # Basic color buttons
        basic_colors_grid = QHBoxLayout()
        basic_colors_grid.setSpacing(5)
        
        basic_colors = [
                        "#00ffff", "#ff0000", "#ff8000", 
                        "#ffff00", "#00ff00", "#0000ff", 
                        "#ff00ff", "#8000ff", "#ffffff"
                        ]
        
        self._basic_color_buttons = []
        for color in basic_colors:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    border: 2px solid #404040;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    border-color: #00B0C8;
                }}
            """)
            btn.clicked.connect(lambda checked, c=color: self._select_color(c))
            basic_colors_grid.addWidget(btn)
            self._basic_color_buttons.append(btn)
        
        # More color button (on the right side)
        more_color_btn = QPushButton("     More colors")
        more_color_btn.setFixedSize(100, 30)
        more_color_btn.setStyleSheet("""
            QPushButton {
                background: #2a2a2a;
                color: #ffffff;
                border: 1px solid #00B0C8;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #3a3a3a;
                border-color: #00d4e8;
            }
        """)
        more_color_btn.clicked.connect(self._open_color_dialog)
        basic_colors_grid.addWidget(more_color_btn)
        
        basic_colors_grid.addStretch()
        basic_colors_layout.addLayout(basic_colors_grid)
        
        color_sections_layout.addWidget(basic_colors_frame)
        
        content_layout.addWidget(self._color_sections_widget)
        content_layout.addStretch()
        
        layout.addLayout(content_layout)
        
        # Update color sections visibility based on current effect
        self._update_color_sections_visibility()
    
    def _effect_button_style(self):
        return """
            QPushButton {
                background: #2a2a2a;
                color: #888888;
                border: 1px solid #404040;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #3a3a3a;
                color: #ffffff;
            }
            QPushButton:checked {
                background: #00B0C8;
                color: #000000;
                border-color: #00B0C8;
                font-weight: bold;
            }
        """
    
    def _direction_button_style(self):
        return """
            QPushButton {
                background: #2a2a2a;
                color: #888888;
                border: 1px solid #404040;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #3a3a3a;
                color: #ffffff;
                border-color: #00B0C8;
            }
            QPushButton:checked {
                background: #00B0C8;
                color: #000000;
                border-color: #00B0C8;
            }
        """
    
    def _slider_style(self):
        return """
            QSlider::groove:horizontal {
                height: 6px;
                background: #333333;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00B0C8;
                border: 2px solid #00B0C8;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #00d4e8;
                border-color: #00d4e8;
            }
            QSlider::sub-page:horizontal {
                background: #00B0C8;
                border-radius: 3px;
            }
        """
    
    def _select_effect(self, mode_id):
        # Uncheck other buttons
        for btn in self._effect_buttons.values():
            btn.setChecked(False)
        
        # Check selected button
        self._effect_buttons[mode_id].setChecked(True)
        self._current_effect = mode_id
        
        # Update color sections visibility
        self._update_color_sections_visibility()
        
        # Auto-apply effect
        self._apply_effect()
    
    def _update_color_sections_visibility(self):
        """Hide color sections for Wave and Neon effects"""
        # Wave=3, Neon=2 don't use colors
        if self._current_effect in [2, 3]:
            self._color_sections_widget.setVisible(False)
        else:
            self._color_sections_widget.setVisible(True)
    
    def _select_color(self, color):
        self._current_color = color
        # Auto-apply
        self._apply_effect()
    
    def _open_color_dialog(self):
        color = QColorDialog.getColor(QColor(self._current_color), self, "Choose Color")
        if color.isValid():
            self._select_color(color.name())
    
    def _set_direction(self, direction):
        self._direction = direction
        # Block signals to prevent recursive calls
        self._left_btn.blockSignals(True)
        self._right_btn.blockSignals(True)
        # Uncheck both
        self._left_btn.setChecked(False)
        self._right_btn.setChecked(False)
        # Check selected (1 = right to left, 2 = left to right)
        if direction == 1:  # right to left (←)
            self._left_btn.setChecked(True)
        else:  # 2 = left to right (→)
            self._right_btn.setChecked(True)
        # Unblock signals
        self._left_btn.blockSignals(False)
        self._right_btn.blockSignals(False)
        # Auto-apply
        self._apply_effect()
    
    def _speed_changed(self, value):
        self._speed = value
        # Auto-apply
        self._apply_effect()
    
    def _brightness_changed(self, value):
        self._brightness = value
        self._brightness_value.setText(f"{value}%")
        # Auto-apply
        self._apply_effect()
    
    def _apply_effect(self):
        """Apply the selected dynamic effect"""
        try:
            # Convert color to RGB
            color = self._current_color
            if color.startswith('#'):
                color = color[1:]
            
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            success = self.controller.lighting_service.set_four_zone_mode(
                self._current_effect, self._speed, self._brightness, 
                self._direction, r, g, b
            )
            
            if success:
                print(f"Applied dynamic effect: mode={self._current_effect}, speed={self._speed}, "
                      f"brightness={self._brightness}, direction={self._direction}, rgb=({r},{g},{b})")
                
                # Save settings for next time
                self.controller.settings.set_dynamic_settings(
                    self._current_effect, self._speed, self._brightness,
                    self._direction, self._current_color
                )
                
        except Exception as e:
            print(f"Error applying dynamic effect: {e}")


class LightingWindow(QWidget):
    """Main RGB Keyboard Lighting Control Window"""
    
    def __init__(self, parent=None, controller: CoreController = None):
        super().__init__(parent)
        self.controller = controller
        # Position and size identical to other windows
        self.setGeometry(300, 100, 1100, 600)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.polygon = self._create_mask()
        self._build_ui()
    
    def _create_mask(self):
        """Create the same mask as other windows for consistency"""
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
        wrapper = QWidget(self)
        wrapper.setAttribute(Qt.WA_TranslucentBackground)
        wrapper.setGeometry(30, 20, self.width() - 60, self.height() - 40)
        
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("RGB Keyboard Lighting")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont(DEFAULT_FONT_FAMILY, 16, QFont.Bold))
        header.setStyleSheet("color: #00B0C8; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Check if lighting is available
        if not self.controller.lighting_service.is_available():
            # Show unavailable message
            unavailable_label = QLabel("RGB Lighting is not available on this system.\n"
                                     "Please ensure the linuwu-sense driver is installed and loaded.")
            unavailable_label.setAlignment(Qt.AlignCenter)
            unavailable_label.setStyleSheet("color: #ff6b6b; font-size: 14px; margin: 50px;")
            layout.addWidget(unavailable_label)
            layout.addStretch()
            return
        
        # Tab widget for Static/Dynamic modes
        self._tab_widget = QTabWidget()
        self._tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #2a2a2a;
                color: #cfcfcf;
                border: none;
                padding: 12px 30px;
                margin-right: 4px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00B0C8, stop:1 #008a9c);
                color: #000000;
            }
            QTabBar::tab:hover:!selected {
                background: #3a3a3a;
                color: #ffffff;
            }
        """)
        
        # Add tabs
        self._static_tab = PredatorStaticTab(self.controller)
        self._dynamic_tab = CleanDynamicTab(self.controller)
        
        self._tab_widget.addTab(self._static_tab, "Static")
        self._tab_widget.addTab(self._dynamic_tab, "Dynamic")
        
        layout.addWidget(self._tab_widget)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Panel fill - dark background
        painter.setBrush(QBrush(QColor("#121212")))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(self.polygon)
        
        # Cyan border
        pen = QPen(QColor("#00B0C8"), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPolygon(self.polygon)