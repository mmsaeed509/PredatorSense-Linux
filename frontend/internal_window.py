# frontend/internal_window.py

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush, QRegion, QPolygon, QPen  # Corrected import for QPolygon
from PyQt5.QtWidgets import QWidget

class InternalWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set the geometry (position and size) of the internal window
        # self.setGeometry(x, y, width, height)
        self.setGeometry(300, 100, 1100, 600)
        self.setAttribute(Qt.WA_TranslucentBackground)  # Make the background transparent
        self.polygon = self.createCustomMask()  # Store the polygon used for the mask

    def createCustomMask(self):
        # Define points for an 8-sided polygon
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
        mask = QRegion(polygon)
        self.setMask(mask)  # Apply the mask to make the window non-rectangular
        return polygon  # Return the polygon for use in the paint event

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the custom shape with a color fill
        painter.setBrush(QBrush(QColor("#121212")))  # Use a custom background color
        painter.drawPolygon(self.polygon)  # Draw the filled polygon

        # Draw the border with the specified color
        pen = QPen(QColor("#00B0C8"), 3)  # Create a pen with the desired color and border width
        painter.setPen(pen)
        painter.drawPolygon(self.polygon)  # Draw the polygon border
