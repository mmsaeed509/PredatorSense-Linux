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
        keyboard_frame.setFixedHeight(200)
        keyboard_frame.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 2px solid #00B0C8;
                border-radius: 10px;
            }
        """)
        
        # Create keyboard layout
        keyboard_layout = QVBoxLayout(keyboard_frame)
        keyboard_layout.setContentsMargins(20, 20, 20, 20)
        
        # Keyboard visual representation
        self._keyboard_widget = self._create_keyboard_visual()
        keyboard_layout.addWidget(self._keyboard_widget)
        
        layout.addWidget(keyboard_frame)
        
        # Zone controls
        zones_section = QHBoxLayout()
        zones_section.setSpacing(30)
        zones_section.setContentsMargins(50, 20, 50, 20)
        
        self._zone_buttons = []
        for i in range(4):
            zone_container = QVBoxLayout()
            zone_container.setSpacing(10)
            zone_container.setAlignment(Qt.AlignCenter)
            
            # Zone label
            zone_label = QLabel(f"Zone {i+1}")
            zone_label.setAlignment(Qt.AlignCenter)
            zone_label.setStyleSheet("color: #888888; font-size: 12px;")
            zone_container.addWidget(zone_label)
            
            # Zone controls
            zone_controls = QHBoxLayout()
            zone_controls.setSpacing(10)
            zone_controls.setAlignment(Qt.AlignCenter)
            
            # Cyan color button
            cyan_btn = QPushButton()
            cyan_btn.setFixedSize(40, 25)
            cyan_btn.setStyleSheet("""
                QPushButton {
                    background: #00ffff;
                    border: 2px solid #404040;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    border-color: #ffffff;
                }
            """)
            cyan_btn.clicked.connect(lambda checked, zone=i: self._set_zone_color(zone, "#00ffff"))
            zone_controls.addWidget(cyan_btn)
            
            # Purple color button  
            purple_btn = QPushButton()
            purple_btn.setFixedSize(40, 25)
            purple_btn.setStyleSheet("""
                QPushButton {
                    background: #ff00ff;
                    border: 2px solid #404040;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    border-color: #ffffff;
                }
            """)
            purple_btn.clicked.connect(lambda checked, zone=i: self._set_zone_color(zone, "#ff00ff"))
            zone_controls.addWidget(purple_btn)
            
            zone_container.addLayout(zone_controls)
            
            # Store buttons for later reference
            self._zone_buttons.append((cyan_btn, purple_btn))
            
            zones_section.addLayout(zone_container)
        
        layout.addLayout(zones_section)
        layout.addStretch()
    
    def _create_keyboard_visual(self):
        """Create a visual representation of the keyboard"""
        keyboard_widget = QWidget()
        keyboard_widget.setFixedHeight(120)
        
        # Use a custom paint event to draw the keyboard
        def paint_keyboard(event):
            painter = QPainter(keyboard_widget)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw keyboard outline
            painter.setPen(QPen(QColor("#404040"), 2))
            painter.setBrush(QBrush(QColor("#2a2a2a")))
            painter.drawRoundedRect(10, 10, keyboard_widget.width()-20, keyboard_widget.height()-20, 8, 8)
            
            # Draw keys with zone colors
            key_width = 12
            key_height = 12
            key_spacing = 2
            
            # Zone 1 (WASD area) - Top left
            painter.setBrush(QBrush(QColor(self._zone_colors[0])))
            for row in range(3):
                for col in range(8):
                    x = 20 + col * (key_width + key_spacing)
                    y = 20 + row * (key_height + key_spacing)
                    painter.drawRoundedRect(x, y, key_width, key_height, 2, 2)
            
            # Zone 2 (Arrow keys area) - Top right  
            painter.setBrush(QBrush(QColor(self._zone_colors[1])))
            for row in range(3):
                for col in range(8):
                    x = 200 + col * (key_width + key_spacing)
                    y = 20 + row * (key_height + key_spacing)
                    painter.drawRoundedRect(x, y, key_width, key_height, 2, 2)
            
            # Zone 3 (Numpad area) - Bottom right
            painter.setBrush(QBrush(QColor(self._zone_colors[2])))
            for row in range(2):
                for col in range(6):
                    x = 220 + col * (key_width + key_spacing)
                    y = 70 + row * (key_height + key_spacing)
                    painter.drawRoundedRect(x, y, key_width, key_height, 2, 2)
            
            # Zone 4 (Function keys) - Bottom left
            painter.setBrush(QBrush(QColor(self._zone_colors[3])))
            for row in range(2):
                for col in range(6):
                    x = 20 + col * (key_width + key_spacing)
                    y = 70 + row * (key_height + key_spacing)
                    painter.drawRoundedRect(x, y, key_width, key_height, 2, 2)
        
        keyboard_widget.paintEvent = paint_keyboard
        return keyboard_widget
    
    def _brightness_changed(self, value):
        self._brightness = value
        self._brightness_value.setText(f"{value}%")
        # Apply brightness change immediately
        self._apply_current_settings()
    
    def _set_zone_color(self, zone_index, color):
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