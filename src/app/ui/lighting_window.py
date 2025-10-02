"""
RGB Keyboard Lighting Control Window - Clean & Modern Design
Supports Static (per-zone) and Dynamic (four-zone) modes
"""
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QPainter, QColor, QBrush, QRegion, QPolygon, QPen, QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                          QTabWidget, QSlider, QComboBox, QColorDialog, QGridLayout,
                          QFrame, QSizePolicy, QSpacerItem)
from app.core import CoreController
from config import DEFAULT_FONT_FAMILY


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
            
        except Exception as e:
            print(f"Error applying lighting: {e}")


class CleanDynamicTab(QWidget):
    """Clean, simple dynamic lighting control"""
    
    def __init__(self, controller: CoreController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._current_color = "#4287f5"
        self._current_effect = 1  # Breathing
        self._speed = 4
        self._brightness = 100
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(30)
        
        # Effect selection
        effect_section = QFrame()
        effect_section.setStyleSheet("QFrame { background: transparent; }")
        effect_layout = QVBoxLayout(effect_section)
        effect_layout.setSpacing(20)
        
        effect_title = QLabel("Choose Effect")
        effect_title.setFont(QFont(DEFAULT_FONT_FAMILY, 16, QFont.Bold))
        effect_title.setStyleSheet("color: #ffffff;")
        effect_title.setAlignment(Qt.AlignCenter)
        effect_layout.addWidget(effect_title)
        
        # Effect buttons grid
        effects_grid = QGridLayout()
        effects_grid.setSpacing(12)
        
        effects = [
            (1, "💨 Breathing", "#4287f5"),
            (2, "💡 Neon", "#00ff00"),
            (3, "🌊 Wave", "#00ffff"),
            (4, "🌈 Shifting", "#ff8000"),
            (6, "☄️ Meteor", "#ff0000"),
            (7, "✨ Twinkling", "#ffffff")
        ]
        
        self._effect_buttons = {}
        for i, (mode_id, name, color) in enumerate(effects):
            row = i // 3
            col = i % 3
            
            btn = QPushButton(name)
            btn.setFixedSize(140, 50)
            btn.setCheckable(True)
            btn.setStyleSheet(self._effect_button_style(color))
            btn.clicked.connect(lambda checked, m=mode_id, c=color: self._select_effect(m, c))
            
            effects_grid.addWidget(btn, row, col)
            self._effect_buttons[mode_id] = btn
        
        # Set default selection
        self._effect_buttons[1].setChecked(True)
        
        effects_container = QWidget()
        effects_container.setLayout(effects_grid)
        effect_layout.addWidget(effects_container, 0, Qt.AlignCenter)
        
        layout.addWidget(effect_section)
        
        # Color selection
        color_section = QFrame()
        color_section.setStyleSheet("QFrame { background: transparent; }")
        color_layout = QVBoxLayout(color_section)
        color_layout.setSpacing(20)
        
        color_title = QLabel("Effect Color")
        color_title.setFont(QFont(DEFAULT_FONT_FAMILY, 14, QFont.Bold))
        color_title.setStyleSheet("color: #cfcfcf;")
        color_title.setAlignment(Qt.AlignCenter)
        color_layout.addWidget(color_title)
        
        # Color picker
        color_picker_layout = QHBoxLayout()
        color_picker_layout.addStretch()
        self._color_btn = SimpleColorButton(self._current_color, 60)
        self._color_btn.clicked.connect(self._color_changed)
        color_picker_layout.addWidget(self._color_btn)
        color_picker_layout.addStretch()
        color_layout.addLayout(color_picker_layout)
        
        layout.addWidget(color_section)
        
        # Speed and brightness controls
        controls_section = QFrame()
        controls_section.setStyleSheet("QFrame { background: transparent; }")
        controls_layout = QVBoxLayout(controls_section)
        controls_layout.setSpacing(25)
        
        # Speed control
        speed_layout = QVBoxLayout()
        speed_layout.setSpacing(10)
        
        speed_title = QLabel("Effect Speed")
        speed_title.setFont(QFont(DEFAULT_FONT_FAMILY, 14, QFont.Bold))
        speed_title.setStyleSheet("color: #cfcfcf;")
        speed_title.setAlignment(Qt.AlignCenter)
        speed_layout.addWidget(speed_title)
        
        speed_slider_layout = QHBoxLayout()
        speed_slider_layout.setSpacing(15)
        
        slow_label = QLabel("Slow")
        slow_label.setStyleSheet("color: #888888; font-size: 12px;")
        speed_slider_layout.addWidget(slow_label)
        
        self._speed_slider = QSlider(Qt.Horizontal)
        self._speed_slider.setRange(1, 9)
        self._speed_slider.setValue(self._speed)
        self._speed_slider.setStyleSheet(self._clean_slider_style())
        self._speed_slider.valueChanged.connect(self._speed_changed)
        speed_slider_layout.addWidget(self._speed_slider)
        
        fast_label = QLabel("Fast")
        fast_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        speed_slider_layout.addWidget(fast_label)
        
        self._speed_value = QLabel(f"{self._speed}")
        self._speed_value.setStyleSheet("color: #00B0C8; font-weight: bold; font-size: 14px; min-width: 30px;")
        self._speed_value.setAlignment(Qt.AlignCenter)
        speed_slider_layout.addWidget(self._speed_value)
        
        speed_layout.addLayout(speed_slider_layout)
        controls_layout.addLayout(speed_layout)
        
        # Brightness control
        brightness_layout = QVBoxLayout()
        brightness_layout.setSpacing(10)
        
        brightness_title = QLabel("Brightness")
        brightness_title.setFont(QFont(DEFAULT_FONT_FAMILY, 14, QFont.Bold))
        brightness_title.setStyleSheet("color: #cfcfcf;")
        brightness_title.setAlignment(Qt.AlignCenter)
        brightness_layout.addWidget(brightness_title)
        
        brightness_slider_layout = QHBoxLayout()
        brightness_slider_layout.setSpacing(15)
        
        dim_label = QLabel("Dim")
        dim_label.setStyleSheet("color: #888888; font-size: 12px;")
        brightness_slider_layout.addWidget(dim_label)
        
        self._brightness_slider = QSlider(Qt.Horizontal)
        self._brightness_slider.setRange(10, 100)
        self._brightness_slider.setValue(self._brightness)
        self._brightness_slider.setStyleSheet(self._clean_slider_style())
        self._brightness_slider.valueChanged.connect(self._brightness_changed)
        brightness_slider_layout.addWidget(self._brightness_slider)
        
        bright_label = QLabel("Bright")
        bright_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        brightness_slider_layout.addWidget(bright_label)
        
        self._brightness_value = QLabel(f"{self._brightness}%")
        self._brightness_value.setStyleSheet("color: #00B0C8; font-weight: bold; font-size: 14px; min-width: 50px;")
        self._brightness_value.setAlignment(Qt.AlignCenter)
        brightness_slider_layout.addWidget(self._brightness_value)
        
        brightness_layout.addLayout(brightness_slider_layout)
        controls_layout.addLayout(brightness_layout)
        
        layout.addWidget(controls_section)
        
        # Apply button
        apply_btn = QPushButton("🎆 Apply Effect")
        apply_btn.setStyleSheet(self._apply_button_style())
        apply_btn.clicked.connect(self._apply_effect)
        layout.addWidget(apply_btn)
        
        layout.addStretch()
    
    def _effect_button_style(self, color):
        return f"""
            QPushButton {{
                background: #2a2a2a;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 10px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #3a3a3a;
                border-color: {color};
            }}
            QPushButton:checked {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}40, stop:1 {color}20);
                border-color: {color};
                color: #ffffff;
            }}
        """
    
    def _clean_slider_style(self):
        return """
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
        """
    
    def _apply_button_style(self):
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00B0C8, stop:1 #00d4e8);
                color: #000000;
                border: none;
                border-radius: 12px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4e8, stop:1 #00f0ff);
            }
            QPushButton:pressed {
                background: #008a9c;
            }
        """
    
    def _select_effect(self, mode_id, color):
        # Uncheck other buttons
        for btn in self._effect_buttons.values():
            btn.setChecked(False)
        
        # Check selected button
        self._effect_buttons[mode_id].setChecked(True)
        self._current_effect = mode_id
        
        # Update color to match effect
        self._current_color = color
        self._color_btn.set_color(color)
    
    def _color_changed(self):
        self._current_color = self._color_btn.get_color()
    
    def _speed_changed(self, value):
        self._speed = value
        self._speed_value.setText(str(value))
    
    def _brightness_changed(self, value):
        self._brightness = value
        self._brightness_value.setText(f"{value}%")
    
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
                self._current_effect, self._speed, self._brightness, 1, r, g, b
            )
            
            if success:
                print(f"Applied dynamic effect: mode={self._current_effect}, speed={self._speed}, "
                      f"brightness={self._brightness}, rgb=({r},{g},{b})")
            else:
                print("Failed to apply dynamic effect")
                
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