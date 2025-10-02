from PyQt5.QtCore import QPoint, Qt, pyqtProperty, QTimer, QElapsedTimer, pyqtSignal
from PyQt5.QtGui import QPolygon, QRegion, QPainter, QColor, QPen, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from config import DEFAULT_FONT_FAMILY


def contentButtonMask():
    """Creates a custom QRegion mask for angled buttons like PredatorSense."""
    button_points = [
        QPoint(200, 0),
        QPoint(240, 30),
        QPoint(240, 100),
        QPoint(30, 100),
        QPoint(0, 70),
        QPoint(0, 0),
    ]
    polygon = QPolygon(button_points)
    return QRegion(polygon)


class CircularGauge(QWidget):
    """
    PredatorSense-style circular gauge with animated cyan arc.
    - value: current reading (e.g., temperature)
    - min/max: range
    """

    def __init__(self, title: str = "", value: int = 0, minimum: int = 0, maximum: int = 100, parent=None, circle_scale: float = 1, pen_width: int = 9):
        super().__init__(parent)
        self._title = title
        self._value = value
        self._min = minimum
        self._max = maximum
        self._target = value
        # visual tuning
        self._scale = max(0.4, min(1.0, float(circle_scale)))
        self._pen_width = max(6, int(pen_width))
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(33)  # 30fps instead of 66fps for better performance
        self._font_title = QFont(DEFAULT_FONT_FAMILY, 10)
        self._font_value = QFont(DEFAULT_FONT_FAMILY, 24)
        self._font_unit = QFont(DEFAULT_FONT_FAMILY, 16)
        self.setMinimumSize(140, 140)

    # Animation helpers
    def setValueAnimated(self, v: int):
        v = max(self._min, min(self._max, int(v)))
        self._target = v
        if not self._timer.isActive():
            self._timer.start()

    def _tick(self):
        if self._value == self._target:
            self._timer.stop()
            return
        step = 1 if self._value < self._target else -1
        self._value += step
        self.update()

    # Property for animations (optional future use)
    def getValue(self):
        return self._value

    def setValue(self, v: int):
        self._value = max(self._min, min(self._max, int(v)))
        self.update()

    value = pyqtProperty(int, fget=getValue, fset=setValue)

    def setRange(self, minimum: int, maximum: int):
        self._min = int(minimum)
        self._max = max(self._min + 1, int(maximum))
        # clamp current value into new range
        self._value = max(self._min, min(self._max, self._value))
        self.update()

    def paintEvent(self, event):
        size = min(self.width(), self.height())
        margin = 10
        radius = int(((size // 2) - margin) * self._scale)
        cx = self.width() // 2
        cy = self.height() // 2

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background (dark ring)
        base_pen = QPen(QColor(35, 35, 35), self._pen_width)
        base_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(base_pen)
        painter.drawArc(cx - radius, cy - radius, 2 * radius, 2 * radius, 45 * 16, 270 * 16)

        # Foreground segmented cyan arc
        span_deg = int(270 * (self._value - self._min) / max(1, (self._max - self._min)))
        segment = 12  # degrees per segment
        gap = 6       # degrees gap
        deg = 0
        while deg < span_deg:
            take = min(segment, span_deg - deg)
            hue_pen = QPen(QColor("#00B0C8"), self._pen_width)
            hue_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(hue_pen)
            painter.drawArc(cx - radius, cy - radius, 2 * radius, 2 * radius, (45 + deg) * 16, take * 16)
            deg += segment + gap

        # Value text (e.g., 64°)
        painter.setPen(QColor(210, 210, 210))
        painter.setFont(self._font_value)
        text = f"{int(self._value)}°"
        tw = painter.fontMetrics().width(text)
        th = painter.fontMetrics().height()
        painter.drawText(cx - tw // 2, cy + th // 4, text)

        # Title label under
        painter.setFont(self._font_title)
        painter.setPen(QColor(172, 172, 172))
        label = self._title
        lw = painter.fontMetrics().width(label)
        painter.drawText(cx - lw // 2, cy + radius + 24, label)


def apply_cyan_glow_border(widget: QWidget, radius: int = 14, width: int = 2):
    """Apply a subtle cyan glow border using stylesheet (rounded corners)."""
    widget.setStyleSheet(
        f"""
        QWidget {{
            background-color: #121212;
            border: {width}px solid #00B0C8;
            border-radius: {radius}px;
        }}
        """
    )


class FanDial(QWidget):
    """
    PredatorSense-style fan dial with rotating blades and cyan rim.
    - setRpm(rpm): animates value towards target
    - setTitle(str): label under the dial (e.g., CPU/GPU)
    Visuals: cyan outer ring, dark inner circle, rotating blades, big numeric RPM.
    """

    def __init__(self, title: str = "", rpm: int = 0, parent=None):
        super().__init__(parent)
        self._title = title
        self._rpm = 0
        self._target_rpm = max(0, int(rpm))
        self._spin_angle = 0.0
        # Font setup
        self._font_value = QFont(DEFAULT_FONT_FAMILY, 26, QFont.DemiBold)
        self._font_unit = QFont(DEFAULT_FONT_FAMILY, 10)
        self._font_title = QFont(DEFAULT_FONT_FAMILY, 10)
        self.setMinimumSize(180, 180)

        # Fixed-speed animation timer - always spins at constant speed
        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(33)  # ~30fps
        self._tick_timer.timeout.connect(self._on_tick)
        self._tick_timer.start()  # Start immediately for continuous animation
        
        # High-resolution time delta
        self._clock = QElapsedTimer()
        self._clock.start()

    # API
    def setRpm(self, rpm: int):
        new_rpm = max(0, int(rpm))
        self._target_rpm = new_rpm

    def setTitle(self, title: str):
        if self._title != title:
            self._title = title
            self.update()

    # Animation step
    def _on_tick(self):
        # Use fixed time step for consistent animation
        dt = 0.033  # Fixed 33ms time step (30fps)
        
        # animate numeric value toward target smoothly (for display only)
        if self._rpm != self._target_rpm:
            delta = self._target_rpm - self._rpm
            # faster convergence for big deltas, slower for small changes
            step = max(1, int(abs(delta) * 0.15))
            self._rpm += step if delta > 0 else -step
        
        # FIXED SPEED ROTATION - Independent of actual RPM values
        # Always rotate at a pleasant, constant speed for visual appeal
        fixed_deg_per_sec = 120.0  # Fixed rotation speed: 120°/sec (1/3 revolution per second)
        
        # Always update angle for continuous rotation at fixed speed
        self._spin_angle = (self._spin_angle + fixed_deg_per_sec * dt) % 360.0
        
        # Always repaint for smooth continuous animation
        self.update()

    def paintEvent(self, event):
        w, h = self.width(), self.height()
        size = min(w, h)
        cx, cy = w // 2, h // 2
        # Make the overall blade ring smaller 
        # circle radius size
        outer_r = int(size * 0.40)
        # Blades inner radius size
        inner_r = int(size * 0.28)

        painter = QPainter(self)
        # Only enable antialiasing for text, not for lines (performance optimization)
        
        # Rotating blades (segments) around the rim (outside area)
        blades = 24  # Good balance between performance and visual smoothness
        # Shorter blades and inclined a bit
        blade_len = max(5, int((outer_r - inner_r) * 0.85))
        tilt = 14.0  # degrees of inclination
        blade_pen = QPen(QColor(110, 110, 110), 4)  # Slightly thinner for performance
        blade_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(blade_pen)
        
        # Pre-calculate math for performance
        from math import cos, sin, radians
        blade_step = 360.0 / blades
        for i in range(blades):
            a = (self._spin_angle + i * blade_step)
            ang_outer = radians(a)
            ang_inner = radians(a + tilt)
            x1 = cx + (outer_r - 5) * cos(ang_outer)
            y1 = cy + (outer_r - 5) * sin(ang_outer)
            x2 = cx + (outer_r - blade_len) * cos(ang_inner)
            y2 = cy + (outer_r - blade_len) * sin(ang_inner)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Inner dark circle
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(20, 20, 20))
        painter.drawEllipse(cx - inner_r, cy - inner_r, 2 * inner_r, 2 * inner_r)

        # Cyan ring INSIDE blades, hugging the inner circle
        ring_r = inner_r + 4
        ring_pen = QPen(QColor("#00B0C8"), 3)
        ring_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(ring_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(cx - ring_r, cy - ring_r, 2 * ring_r, 2 * ring_r)

        # Enable antialiasing only for text rendering
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Center text: value and unit
        painter.setPen(QColor(230, 230, 230))
        painter.setFont(self._font_value)
        text = str(int(self._rpm))
        tw = painter.fontMetrics().width(text)
        th = painter.fontMetrics().ascent()
        painter.drawText(cx - tw // 2, cy + th // 3, text)

        painter.setPen(QColor(150, 150, 150))
        painter.setFont(self._font_unit)
        unit = "RPM"
        uw = painter.fontMetrics().width(unit)
        painter.drawText(cx - uw // 2, cy + th // 3 + 18, unit)
class ModeButton(QWidget):
    """
    Custom checkable button used for Fan modes (Auto/Max/Custom) matching the screenshot style.
    Rectangular button with angled corners, text label positioned below the button.
    """

    clicked = pyqtSignal()

    def __init__(self, caption: str, parent=None):
        super().__init__(parent)
        self._caption = caption
        self._checked = False
        # Button area only (text will be below)
        self.setMinimumSize(120, 60)
        self._font_caption = QFont(DEFAULT_FONT_FAMILY, 11)
        self.setAttribute(Qt.WA_Hover)

    # API
    def setChecked(self, v: bool):
        if self._checked != bool(v):
            self._checked = bool(v)
            self.update()

    def isChecked(self) -> bool:
        return self._checked

    def setCaption(self, text: str):
        self._caption = text
        self.update()

    # Interaction
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self.rect().contains(e.pos()):
            self.clicked.emit()
        super().mouseReleaseEvent(e)

    # Painting helpers - rectangular button with angled corners like screenshot
    def _buttonPolygon(self):
        w, h = self.width(), self.height()
        corner_cut = 8  # Size of angled corners
        pts = [
            QPoint(corner_cut, 0),           # Top left after cut
            QPoint(w - corner_cut, 0),       # Top right before cut
            QPoint(w, corner_cut),           # Top right after cut
            QPoint(w, h - corner_cut),       # Bottom right before cut
            QPoint(w - corner_cut, h),       # Bottom right after cut
            QPoint(corner_cut, h),           # Bottom left before cut
            QPoint(0, h - corner_cut),       # Bottom left after cut
            QPoint(0, corner_cut),           # Top left before cut
        ]
        return QPolygon(pts)

    def _drawFanIcon(self, p: QPainter, cx: int, cy: int, size: int, color: QColor):
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        
        # Different icons based on mode matching screenshot
        if self._caption == "Auto":
            # Auto mode: Fan with "A" overlay (like screenshot)
            p.setPen(QPen(color, 2))
            # Outer ring
            ring_radius = size // 3
            p.drawEllipse(cx - ring_radius, cy - ring_radius, 2 * ring_radius, 2 * ring_radius)
            
            # Fan blades
            blades = 8
            blade_radius = size * 0.4
            from math import cos, sin, radians
            for i in range(blades):
                angle = radians(i * (360.0 / blades))
                x1 = cx + int(blade_radius * cos(angle))
                y1 = cy + int(blade_radius * sin(angle))
                x2 = cx + int((blade_radius - size * 0.15) * cos(angle))
                y2 = cy + int((blade_radius - size * 0.15) * sin(angle))
                p.drawLine(x1, y1, x2, y2)
            
            # "A" overlay in center
            p.setFont(QFont(DEFAULT_FONT_FAMILY, 14, QFont.Bold))
            p.setPen(color)
            p.drawText(cx - 5, cy + 5, "A")
            
        elif self._caption == "Max":
            # Max mode: More aggressive fan (like screenshot)
            p.setPen(QPen(color, 2))
            # Outer ring
            ring_radius = size // 3
            p.drawEllipse(cx - ring_radius, cy - ring_radius, 2 * ring_radius, 2 * ring_radius)
            
            # More blades for "max" effect
            blades = 16
            blade_radius = size * 0.42
            from math import cos, sin, radians
            for i in range(blades):
                angle = radians(i * (360.0 / blades))
                x1 = cx + int(blade_radius * cos(angle))
                y1 = cy + int(blade_radius * sin(angle))
                x2 = cx + int((blade_radius - size * 0.2) * cos(angle))
                y2 = cy + int((blade_radius - size * 0.2) * sin(angle))
                p.drawLine(x1, y1, x2, y2)
                
        elif self._caption == "Custom":
            # Custom mode: Fan with wrench overlay (like screenshot)
            p.setPen(QPen(color, 2))
            # Outer ring
            ring_radius = size // 3
            p.drawEllipse(cx - ring_radius, cy - ring_radius, 2 * ring_radius, 2 * ring_radius)
            
            # Fan blades
            blades = 8
            blade_radius = size * 0.4
            from math import cos, sin, radians
            for i in range(blades):
                angle = radians(i * (360.0 / blades))
                x1 = cx + int(blade_radius * cos(angle))
                y1 = cy + int(blade_radius * sin(angle))
                x2 = cx + int((blade_radius - size * 0.15) * cos(angle))
                y2 = cy + int((blade_radius - size * 0.15) * sin(angle))
                p.drawLine(x1, y1, x2, y2)
            
            # Wrench/tool overlay
            p.setPen(QPen(color, 3))
            # Simple wrench shape
            p.drawLine(cx - 10, cy - 6, cx + 10, cy + 6)
            p.drawLine(cx - 8, cy - 8, cx - 6, cy - 6)
            p.drawLine(cx + 6, cy + 6, cx + 8, cy + 8)
        
        p.restore()

    def paintEvent(self, event):
        p = QPainter(self)
        poly = self._buttonPolygon()

        # Button background - matching screenshot colors
        p.setPen(Qt.NoPen)
        if self.isEnabled() and self._checked:
            # Selected state: very dark background
            p.setBrush(QColor(8, 8, 8))
        else:
            # Normal state: slightly lighter dark background
            p.setBrush(QColor(15, 15, 15))
        p.drawPolygon(poly)

        # Button border - cyan for selected, gray for unselected
        if self.isEnabled() and self._checked:
            border = QPen(QColor("#00B0C8"), 2)
        else:
            border = QPen(QColor(40, 40, 40), 1)
        p.setPen(border)
        p.setBrush(Qt.NoBrush)
        p.drawPolygon(poly)

        # Icon positioning - center of button
        cx, cy = self.width() // 2, self.height() // 2
        
        # Icon color based on state
        if not self.isEnabled():
            icon_color = QColor(60, 60, 60)
        elif self._checked:
            icon_color = QColor("#00B0C8")
        else:
            icon_color = QColor(100, 100, 100)
            
        # Draw the fan icon
        self._drawFanIcon(p, cx, cy, 36, icon_color)


class ModeButtonWithLabel(QWidget):
    """
    Complete mode button widget with button and label below, matching screenshot layout.
    """
    
    clicked = pyqtSignal()
    
    def __init__(self, caption: str, parent=None):
        super().__init__(parent)
        self._caption = caption
        self._button = ModeButton(caption, self)
        self._label = QLabel(caption, self)
        
        # Setup label styling
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setFont(QFont(DEFAULT_FONT_FAMILY, 11))
        self._label.setStyleSheet("color: #9aa0a6; margin-top: 8px;")
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self._button)
        layout.addWidget(self._label)
        
        # Connect signals
        self._button.clicked.connect(self.clicked.emit)
        
        # Set size
        self.setFixedSize(120, 100)
    
    def setChecked(self, checked: bool):
        self._button.setChecked(checked)
        # Update label color based on state
        if checked:
            self._label.setStyleSheet("color: #00B0C8; margin-top: 8px; font-weight: bold;")
        else:
            self._label.setStyleSheet("color: #9aa0a6; margin-top: 8px;")
    
    def isChecked(self) -> bool:
        return self._button.isChecked()
    
    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self._button.setEnabled(enabled)
        if not enabled:
            self._label.setStyleSheet("color: #606060; margin-top: 8px;")
        elif self.isChecked():
            self._label.setStyleSheet("color: #00B0C8; margin-top: 8px; font-weight: bold;")
        else:
            self._label.setStyleSheet("color: #9aa0a6; margin-top: 8px;")