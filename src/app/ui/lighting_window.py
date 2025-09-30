from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush, QRegion, QPolygon, QPen
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QSlider, QPushButton, QColorDialog)
from app.core import CoreController
from config import DEFAULT_FONT_FAMILY

class LightingWindow(QWidget):
    def __init__(self, parent=None, controller: CoreController = None):
        super().__init__(parent)
        self.controller = controller
        self.setGeometry(300, 100, 1100, 600)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.polygon = self._create_mask()
        self._zone_colors = ['#4287f5'] * 4  # Default blue
        self._current_mode = 0
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

        # Profile selector
        profile_row = QHBoxLayout()
        profile_label = QLabel("Lighting Profile")
        profile_label.setStyleSheet("color: #9aa0a6;")
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(["Default", "Static", "Breathing", "Neon", "Wave", 
                                   "Shifting", "Zoom", "Meteor", "Twinkling"])
        self.profile_combo.setStyleSheet("""
            QComboBox {
                background: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QComboBox:hover { border-color: #00B0C8; }
        """)
        profile_row.addWidget(profile_label)
        profile_row.addWidget(self.profile_combo)
        profile_row.addStretch()
        layout.addLayout(profile_row)

        # Controls section
        controls = QHBoxLayout()
        
        # Left side: Speed & Brightness
        sliders = QVBoxLayout()
        sliders.setSpacing(15)
        
        # Speed slider
        speed_layout = QVBoxLayout()
        speed_label = QLabel("Speed")
        speed_label.setStyleSheet("color: #9aa0a6;")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(0, 9)
        self.speed_slider.setValue(5)
        self.speed_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
            }
            QSlider::handle:horizontal {
                background: #00B0C8;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
        """)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_slider)
        sliders.addLayout(speed_layout)
        
        # Brightness slider
        brightness_layout = QVBoxLayout()
        brightness_label = QLabel("Brightness")
        brightness_label.setStyleSheet("color: #9aa0a6;")
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(100)
        self.brightness_slider.setStyleSheet(self.speed_slider.styleSheet())
        brightness_layout.addWidget(brightness_label)
        brightness_layout.addWidget(self.brightness_slider)
        sliders.addLayout(brightness_layout)
        
        controls.addLayout(sliders)
        controls.addStretch()

        # Right side: Zone color pickers
        zones = QHBoxLayout()
        zones.setSpacing(15)
        
        self.zone_buttons = []
        for i in range(4):
            zone = QVBoxLayout()
            label = QLabel(f"Zone {i+1}")
            label.setStyleSheet("color: #9aa0a6;")
            label.setAlignment(Qt.AlignCenter)
            
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.clicked.connect(lambda x, idx=i: self._pick_zone_color(idx))
            self._update_zone_button(btn, self._zone_colors[i])
            self.zone_buttons.append(btn)
            
            zone.addWidget(label)
            zone.addWidget(btn, alignment=Qt.AlignCenter)
            zones.addLayout(zone)
            
        controls.addLayout(zones)
        layout.addLayout(controls)
        
        # Direction buttons (when applicable)
        self.direction_row = QHBoxLayout()
        self.left_btn = QPushButton("← Left")
        self.right_btn = QPushButton("Right →")
        for btn in (self.left_btn, self.right_btn):
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background: #1a1a1a;
                    color: #e0e0e0;
                    border: 1px solid #2a2a2a;
                    border-radius: 6px;
                    padding: 8px 16px;
                }
                QPushButton:checked {
                    background: #0e2c31;
                    border-color: #00B0C8;
                    color: #00B0C8;
                }
            """)
        self.left_btn.setChecked(True)
        self.direction_row.addStretch()
        self.direction_row.addWidget(self.left_btn)
        self.direction_row.addWidget(self.right_btn)
        self.direction_row.addStretch()
        layout.addLayout(self.direction_row)
        
        # Apply button
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background: #00B0C8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #00859b;
            }
        """)
        layout.addWidget(self.apply_btn, alignment=Qt.AlignCenter)
        layout.addStretch()

        # Wire up events
        self.profile_combo.currentIndexChanged.connect(self._on_profile_changed)
        self.apply_btn.clicked.connect(self._apply_settings)
        self.left_btn.clicked.connect(lambda: self.right_btn.setChecked(False))
        self.right_btn.clicked.connect(lambda: self.left_btn.setChecked(False))

    def _pick_zone_color(self, zone: int):
        color = QColorDialog.getColor(QColor(self._zone_colors[zone]))
        if color.isValid():
            self._zone_colors[zone] = color.name()
            self._update_zone_button(self.zone_buttons[zone], color.name())

    def _update_zone_button(self, btn: QPushButton, color: str):
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                border: 2px solid #2a2a2a;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                border-color: #00B0C8;
            }}
        """)

    def _on_profile_changed(self, index: int):
        # Show/hide direction controls based on mode
        self._current_mode = index
        show_direction = index in (3, 4)  # Wave & Shifting modes
        self.left_btn.setVisible(show_direction)
        self.right_btn.setVisible(show_direction)

    def _apply_settings(self):
        if not self.controller:
            return
            
        if self._current_mode == 0:  # Static per-zone
            colors = [c.lstrip('#') for c in self._zone_colors]
            brightness = self.brightness_slider.value()
            self.controller.lighting.set_per_zone_colors(colors, brightness)
        else:
            # Convert mode index to linuwu mode
            mode = self._current_mode - 1  # Adjust for our UI vs linuwu modes
            speed = self.speed_slider.value()
            brightness = self.brightness_slider.value()
            direction = 2 if self.right_btn.isChecked() else 1
            # Use first zone color for effect color
            color = QColor(self._zone_colors[0])
            self.controller.lighting.set_effect_mode(
                mode, speed, brightness, direction,
                (color.red(), color.green(), color.blue())
            )

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
