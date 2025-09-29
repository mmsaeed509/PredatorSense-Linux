from PyQt5.QtCore import QPoint, Qt, pyqtProperty, QTimer
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

    def __init__(self, title: str = "", value: int = 0, minimum: int = 0, maximum: int = 100, parent=None, circle_scale: float = 0.65, pen_width: int = 12):
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