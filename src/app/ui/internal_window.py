from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush, QRegion, QPolygon, QPen, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame, QSizePolicy, QStackedWidget
from app.utils.ui_utils import CircularGauge
from app.core import CoreController, LightingProfile, OverclockLevel, Tab
from app.core.models import TemperatureUnit
from config import DEFAULT_FONT_FAMILY


class InternalWindow(QWidget):
    def __init__(self, parent=None, controller: CoreController = None):
        super().__init__(parent)
        self.controller = controller
        self._temp_unit = TemperatureUnit.CELSIUS
        # Position and size similar to the reference screenshot
        self.setGeometry(300, 100, 1100, 600)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.polygon = self.createCustomMask()

        # Content layout on top of the painted polygon
        self._buildContent()
        self._wireController()

    def createCustomMask(self):
        # Angled-corners panel
        points = [
            QPoint(1080, 0),   # Top center, 1
            QPoint(1100, 20),  # Top right, 2
            QPoint(1100, 580), # Middle right, 3
            QPoint(1080, 600), # Bottom right, 4
            QPoint(20, 600),   # Bottom center, 5
            QPoint(0, 580),    # Bottom left, 6
            QPoint(0, 560),    # Middle left, 7
            QPoint(20, 540),   # Top left, 8
            QPoint(20, 60),    # Bottom center, 9
            QPoint(0, 40),     # Bottom left, 10
            QPoint(0, 20),     # Middle left, 11
            QPoint(20, 0)      # Top left, 12
        ]
        polygon = QPolygon(points)
        self.setMask(QRegion(polygon))
        return polygon

    def _buildContent(self):
        font_title = QFont(DEFAULT_FONT_FAMILY, 12)
        font_label = QFont(DEFAULT_FONT_FAMILY, 10)

        wrapper = QWidget(self)
        wrapper.setAttribute(Qt.WA_TranslucentBackground)
        wrapper.setGeometry(30, 20, self.width() - 60, self.height() - 40)

        # Use stacked widget to switch between home and coming soon views
        self.stacked_widget = QStackedWidget(wrapper)
        self.stacked_widget.setGeometry(0, 0, wrapper.width(), wrapper.height())
        self.stacked_widget.setAttribute(Qt.WA_TranslucentBackground)
        
        # Home content (index 0)
        home_widget = QWidget()
        home_widget.setAttribute(Qt.WA_TranslucentBackground)
        vbox = QVBoxLayout(home_widget)
        vbox.setContentsMargins(20, 16, 20, 16)
        vbox.setSpacing(18)

        # Header: Temperature (dynamic unit)
        self.header = QLabel("Temperature (°C)")
        self.header.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.header.setFont(font_title)
        self.header.setStyleSheet("color: #9aa0a6;")
        vbox.addWidget(self.header)

        # Gauges row
        gauges_row = QHBoxLayout()
        gauges_row.setSpacing(40)

        self.cpu_g = CircularGauge("CPU"    , 60, circle_scale=0.65, pen_width=12)
        self.gpu_g = CircularGauge("GPU"    , 55, circle_scale=0.65, pen_width=12)
        self.sys_g = CircularGauge("System" , 45, circle_scale=0.65, pen_width=12)
        for g in (self.cpu_g, self.gpu_g, self.sys_g):
            g.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        gauges_row.addWidget(self.cpu_g)
        gauges_row.addWidget(self.gpu_g)
        gauges_row.addWidget(self.sys_g)
        vbox.addLayout(gauges_row)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #2a2a2a;")
        vbox.addWidget(sep)

        # Bottom controls: Lighting Profile and GPU Overclocking
        bottom = QHBoxLayout()
        bottom.setSpacing(80)

        # Lighting Profile
        lp_box = QVBoxLayout()
        lp_label = QLabel("Lighting Profile")
        lp_label.setFont(font_label)
        lp_label.setStyleSheet("color: #9aa0a6;")
        self.lp_combo = QComboBox()
        self.lp_combo.setFont(QFont(DEFAULT_FONT_FAMILY, 10))
        self.lp_combo.addItems(["Default", "Breathing", "Wave", "Ripple"]) 
        self.lp_combo.setStyleSheet(
            """
            QComboBox { background: #1A1A1A; color: #e0e0e0; padding: 6px 10px; border: 1px solid #2b2b2b; border-radius: 6px; }
            QComboBox::drop-down { width: 18px; }
            QComboBox:hover { border-color: #00B0C8; }
            QComboBox QAbstractItemView { background: #1A1A1A; color: #e0e0e0; selection-background-color: #0e2c31; selection-color: #e6feff; border: 1px solid #2b2b2b; }
            """
        )
        lp_box.addWidget(lp_label)
        lp_box.addWidget(self.lp_combo)

        # GPU Overclocking
        oc_box = QVBoxLayout()
        oc_label = QLabel("GPU Overclocking")
        oc_label.setFont(font_label)
        oc_label.setStyleSheet("color: #9aa0a6;")
        self.oc_combo = QComboBox()
        self.oc_combo.setFont(QFont(DEFAULT_FONT_FAMILY, 10))
        self.oc_combo.addItems(["Normal", "Fast", "Extreme"]) 
        self.oc_combo.setStyleSheet(
            """
            QComboBox { background: #1A1A1A; color: #e0e0e0; padding: 6px 10px; border: 1px solid #2b2b2b; border-radius: 6px; }
            QComboBox::drop-down { width: 18px; }
            QComboBox:hover { border-color: #00B0C8; }
            QComboBox QAbstractItemView { background: #1A1A1A; color: #e0e0e0; selection-background-color: #0e2c31; selection-color: #e6feff; border: 1px solid #2b2b2b; }
            """
        )
        oc_box.addWidget(oc_label)
        oc_box.addWidget(self.oc_combo)

        bottom.addLayout(lp_box, 1)
        bottom.addLayout(oc_box, 1)
        vbox.addLayout(bottom)
        
        self.stacked_widget.addWidget(home_widget)
        
        # Coming Soon content (index 1) for Game and Apps Sync
        coming_soon_widget = self._buildComingSoonContent()
        self.stacked_widget.addWidget(coming_soon_widget)
        
        # Show home by default
        self.stacked_widget.setCurrentIndex(0)
    
    def _buildComingSoonContent(self):
        """Build the coming soon view for Game and Apps Sync"""
        widget = QWidget()
        widget.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)
        
        # Icon/Emoji
        icon_label = QLabel("🎮")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 80px; background: transparent; border: none;")
        layout.addWidget(icon_label)
        
        # Title
        title = QLabel("Game and Apps Sync")
        title.setFont(QFont(DEFAULT_FONT_FAMILY, 24, QFont.Bold))
        title.setStyleSheet("color: #00B0C8; background: transparent; border: none;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Coming Soon message
        coming_soon = QLabel("Coming Soon")
        coming_soon.setFont(QFont(DEFAULT_FONT_FAMILY, 18, QFont.Bold))
        coming_soon.setStyleSheet("color: #ffffff; background: transparent; border: none;")
        coming_soon.setAlignment(Qt.AlignCenter)
        layout.addWidget(coming_soon)
        
        # Description
        description = QLabel(
            "Automatic profile switching based on\n"
            "running applications and games.\n\n"
            "This feature will be implemented in a future update."
        )
        description.setFont(QFont(DEFAULT_FONT_FAMILY, 12))
        description.setStyleSheet("color: #acacac; background: transparent; border: none;")
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        return widget

    def _wireController(self):
        if not self.controller:
            return
        # metrics -> gauges
        def _emit_values(cpu_c, gpu_c, sys_c):
            if self._temp_unit == TemperatureUnit.FAHRENHEIT:
                c2f = lambda c: int(round(c * 9 / 5 + 32))
                self.cpu_g.setValueAnimated(c2f(cpu_c))
                self.gpu_g.setValueAnimated(c2f(gpu_c))
                self.sys_g.setValueAnimated(c2f(sys_c))
            else:
                self.cpu_g.setValueAnimated(cpu_c)
                self.gpu_g.setValueAnimated(gpu_c)
                self.sys_g.setValueAnimated(sys_c)

        self.controller.metrics.metricsUpdated.connect(_emit_values)

        # initialize combos from controller
        # Lighting
        lp_to_index = {
            LightingProfile.DEFAULT: 0,
            LightingProfile.BREATHING: 1,
            LightingProfile.WAVE: 2,
            LightingProfile.RIPPLE: 3,
        }
        oc_to_index = {
            OverclockLevel.NORMAL: 0,
            OverclockLevel.FAST: 1,
            OverclockLevel.EXTREME: 2,
        }
        try:
            self.lp_combo.setCurrentIndex(lp_to_index[self.controller.lighting])
            self.oc_combo.setCurrentIndex(oc_to_index[self.controller.overclock])
        except Exception:
            pass

        # UI -> controller
        self.lp_combo.currentIndexChanged.connect(self._onLightingChanged)
        self.oc_combo.currentIndexChanged.connect(self._onOverclockChanged)

        # Initialize and react to temperature unit
        try:
            self._applyTempUnit(self.controller.temperature_unit)
        except Exception:
            self._applyTempUnit(TemperatureUnit.CELSIUS)
        self.controller.temperatureUnitChanged.connect(self._applyTempUnit)
        
        # React to tab changes to show appropriate content
        self.controller.tabChanged.connect(self._onTabChanged)
    
    def _onTabChanged(self, tab: Tab):
        """Switch content based on current tab"""
        if tab == Tab.GAME_APP_SYNC:
            self.stacked_widget.setCurrentIndex(1)  # Show coming soon
        elif tab == Tab.HOME:
            self.stacked_widget.setCurrentIndex(0)  # Show home content

    def _onLightingChanged(self, idx: int):
        if not self.controller:
            return
        mapping = [LightingProfile.DEFAULT, LightingProfile.BREATHING, LightingProfile.WAVE, LightingProfile.RIPPLE]
        if 0 <= idx < len(mapping):
            self.controller.set_lighting(mapping[idx])

    def _onOverclockChanged(self, idx: int):
        if not self.controller:
            return
        mapping = [OverclockLevel.NORMAL, OverclockLevel.FAST, OverclockLevel.EXTREME]
        if 0 <= idx < len(mapping):
            self.controller.set_overclock(mapping[idx])

    def _applyTempUnit(self, unit: TemperatureUnit):
        self._temp_unit = unit
        if unit == TemperatureUnit.FAHRENHEIT:
            self.header.setText("Temperature (°F)")
            for g in (self.cpu_g, self.gpu_g, self.sys_g):
                g.setRange(0, 212)
        else:
            self.header.setText("Temperature (°C)")
            for g in (self.cpu_g, self.gpu_g, self.sys_g):
                g.setRange(0, 100)

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
