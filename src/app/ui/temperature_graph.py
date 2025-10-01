from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from PyQt5.QtWidgets import QWidget
from collections import deque


class TemperatureGraph(QWidget):
    """Simple temperature and usage graph widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.setStyleSheet("background: #1a1a1a; border: 1px solid #2a2a2a;")
        
        # Data storage (keep last 60 points for 1 minute of data)
        self.temp_data = deque(maxlen=60)
        self.usage_data = deque(maxlen=60)
        
        # Initialize with some default values
        for _ in range(60):
            self.temp_data.append(0)
            self.usage_data.append(0)
    
    def add_data_point(self, temperature: int, usage: float):
        """Add a new data point to the graph."""
        self.temp_data.append(temperature)
        self.usage_data.append(usage)
        self.update()  # Trigger repaint
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Clear background
        painter.fillRect(self.rect(), QColor("#1a1a1a"))
        
        if not self.temp_data or not self.usage_data:
            return
        
        width = self.width() - 20  # Leave margins
        height = self.height() - 20
        
        if width <= 0 or height <= 0:
            return
        
        # Calculate scales
        max_temp = max(max(self.temp_data), 100)  # At least 100°C scale
        max_usage = 100  # Usage is always 0-100%
        
        # Draw grid lines
        painter.setPen(QPen(QColor("#2a2a2a"), 1))
        for i in range(0, 101, 25):  # 0%, 25%, 50%, 75%, 100%
            y = int(10 + (height * (100 - i) / 100))
            painter.drawLine(10, y, width + 10, y)
        
        # Draw temperature line (red/orange)
        if len(self.temp_data) > 1:
            painter.setPen(QPen(QColor("#ff6b6b"), 2))
            for i in range(1, len(self.temp_data)):
                x1 = int(10 + (width * (i - 1) / (len(self.temp_data) - 1)))
                y1 = int(10 + (height * (max_temp - self.temp_data[i - 1]) / max_temp))
                x2 = int(10 + (width * i / (len(self.temp_data) - 1)))
                y2 = int(10 + (height * (max_temp - self.temp_data[i]) / max_temp))
                painter.drawLine(x1, y1, x2, y2)
        
        # Draw usage line (cyan)
        if len(self.usage_data) > 1:
            painter.setPen(QPen(QColor("#00B0C8"), 2))
            for i in range(1, len(self.usage_data)):
                x1 = int(10 + (width * (i - 1) / (len(self.usage_data) - 1)))
                y1 = int(10 + (height * (100 - self.usage_data[i - 1]) / 100))
                x2 = int(10 + (width * i / (len(self.usage_data) - 1)))
                y2 = int(10 + (height * (100 - self.usage_data[i]) / 100))
                painter.drawLine(x1, y1, x2, y2)
        
        # Draw legend
        painter.setPen(QPen(QColor("#9aa0a6"), 1))
        painter.drawText(15, height + 5, f"Temp: {self.temp_data[-1] if self.temp_data else 0}°C")
        painter.drawText(width - 80, height + 5, f"Usage: {self.usage_data[-1] if self.usage_data else 0:.1f}%")