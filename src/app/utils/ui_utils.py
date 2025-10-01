from PyQt5.QtCore import QPoint, Qt, pyqtProperty, QTimer, QElapsedTimer, pyqtSignal
from PyQt5.QtGui import QPolygon, QRegion, QPainter, QColor, QPen, QFont
from PyQt5.QtWidgets import QWidget
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
        self._timer.setInterval(15)  # smooth animation
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
        # Spin model parameters
        self._rpm_max = 7000  # used to normalize rotational speed
        self._deg_per_sec_max = 720.0  # deg/sec at max RPM (2 rev/sec)
        self._deg_per_sec_min = 60.0   # deg/sec minimum for smooth continuous rotation
        self._spin_rpm = float(self._target_rpm)  # smoothed rpm for rotation
        self._font_value = QFont(DEFAULT_FONT_FAMILY, 26, QFont.DemiBold)
        self._font_unit = QFont(DEFAULT_FONT_FAMILY, 10)
        self._font_title = QFont(DEFAULT_FONT_FAMILY, 10)
        self.setMinimumSize(180, 180)

        # Value animation timer
        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(16)  # ~60fps
        self._tick_timer.timeout.connect(self._on_tick)
        self._tick_timer.start()
        # High-resolution time delta
        self._clock = QElapsedTimer()
        self._clock.start()

    # API
    def setRpm(self, rpm: int):
        self._target_rpm = max(0, int(rpm))

    def setTitle(self, title: str):
        self._title = title
        self.update()

    # Animation step
    def _on_tick(self):
        # compute dt in seconds (time-based animation prevents stutter)
        elapsed_ms = self._clock.elapsed()
        self._clock.restart()
        dt = max(0.001, min(0.1, float(elapsed_ms) / 1000.0))  # Cap dt to prevent large jumps
        
        # animate numeric value toward target smoothly
        if self._rpm != self._target_rpm:
            delta = self._target_rpm - self._rpm
            # faster convergence for big deltas, slower for small changes
            step = max(1, int(abs(delta) * 0.15))
            self._rpm += step if delta > 0 else -step
        
        # smooth spin RPM toward target using gentler time-based lerp
        blend = max(0.0, min(1.0, dt * 2.0))  # ~500ms time constant for smoother transitions
        self._spin_rpm = (1.0 - blend) * self._spin_rpm + blend * float(self._target_rpm)
        
        # Always rotate at minimum speed for continuous motion, even at 0 RPM
        if self._spin_rpm > 0:
            # rotation speed proportional to smoothed RPM (normalized)
            rpm_norm = max(0.0, min(1.0, self._spin_rpm / float(self._rpm_max)))
            deg_per_sec = self._deg_per_sec_min + (self._deg_per_sec_max - self._deg_per_sec_min) * rpm_norm
        else:
            # Even at 0 RPM, maintain minimum rotation for visual continuity
            deg_per_sec = self._deg_per_sec_min * 0.3  # Slow but continuous rotation
        
        self._spin_angle = (self._spin_angle + deg_per_sec * dt) % 360.0
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
        painter.setRenderHint(QPainter.Antialiasing)

        # Rotating blades (segments) around the rim (outside area)
        blades = 30
        # Shorter blades and inclined a bit
        blade_len = max(5, int((outer_r - inner_r) * 0.85))
        tilt = 14.0  # degrees of inclination
        blade_pen = QPen(QColor(110, 110, 110), 5)
        blade_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(blade_pen)
        from math import cos, sin, radians
        for i in range(blades):
            a = (self._spin_angle + i * (360.0 / blades))
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
    - Checked: cyan border, cyan icon and caption
    - Disabled: dimmed
    - Normal: gray icon/caption
    Emits clicked() on mouse release inside.
    """

    clicked = pyqtSignal()

    def __init__(self, caption: str, subglyph: str = "", parent=None):
        super().__init__(parent)
        self._caption = caption
        self._subglyph = subglyph  # e.g., "A" for Auto, or "" for Max
        self._checked = False
        self.setMinimumSize(140, 92)
        self._font_caption = QFont(DEFAULT_FONT_FAMILY, 11)
        self._font_sub = QFont(DEFAULT_FONT_FAMILY, 14, QFont.DemiBold)
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

    def setSubglyph(self, text: str):
        self._subglyph = text
        self.update()

    # Interaction
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self.rect().contains(e.pos()):
            self.clicked.emit()
        super().mouseReleaseEvent(e)

    # Painting helpers
    def _panelPolygon(self):
        w, h = self.width(), self.height()
        top = 10
        bot = h - 10
        left = 10
        right = w - 10
        notch = 18
        pts = [
            QPoint(left + notch, top),
            QPoint(right - notch, top),
            QPoint(right, top + notch),
            QPoint(right, bot - notch),
            QPoint(right - notch, bot),
            QPoint(left + notch, bot),
            QPoint(left, bot - notch),
            QPoint(left, top + notch),
        ]
        return QPolygon(pts)

    def _drawFanGlyph(self, p: QPainter, cx: int, cy: int, size: int, color: QColor):
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(color, 2))
        # ring
        p.drawEllipse(cx - size//3, cy - size//3, 2*size//3, 2*size//3)
        # small blades around
        blades = 10
        radius = size * 0.55
        from math import cos, sin, radians
        for i in range(blades):
            a = radians(i * (360.0 / blades))
            x1 = cx + int(radius * cos(a))
            y1 = cy + int(radius * sin(a))
            x2 = cx + int((radius - size * 0.25) * cos(a))
            y2 = cy + int((radius - size * 0.25) * sin(a))
            p.drawLine(x1, y1, x2, y2)
        p.restore()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        poly = self._panelPolygon()

        # base panel
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(26, 26, 26))
        p.drawPolygon(poly)

        # border
        if self.isEnabled() and self._checked:
            border = QPen(QColor("#00B0C8"), 2)
        else:
            border = QPen(QColor(42, 42, 42), 2)
        p.setPen(border)
        p.setBrush(Qt.NoBrush)
        p.drawPolygon(poly)

        # icon + glyph
        cx, cy = self.width()//2, int(self.height()*0.42)
        icon_color = QColor("#00B0C8") if (self.isEnabled() and self._checked) else QColor(100, 100, 100)
        if not self.isEnabled():
            icon_color = QColor(70, 70, 70)
        self._drawFanGlyph(p, cx - 10, cy, 36, icon_color)
        if self._subglyph:
            p.setPen(icon_color)
            p.setFont(self._font_sub)
            p.drawText(cx + 4, cy + 6, self._subglyph)

        # caption under
        p.setFont(self._font_caption)
        if not self.isEnabled():
            p.setPen(QColor(120, 120, 120))
        elif self._checked:
            p.setPen(QColor("#00B0C8"))
        else:
            p.setPen(QColor(150, 150, 150))
        tw = p.fontMetrics().width(self._caption)
        p.drawText(self.width()//2 - tw//2, self.height() - 14, self._caption)