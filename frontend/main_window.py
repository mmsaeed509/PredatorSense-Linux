import os
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPainter, QBrush, QPolygon, QColor, QRegion, QFont, QFontDatabase, QPixmap, QPainterPath, \
    QLinearGradient, QPen
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QApplication
from frontend.internal_window import InternalWindow

def createMask():
    # Define a polygon to set the window shape
    points = [
        # QPoint(x, y),      # Point position
        QPoint(750, 0),      # Top center, 0
        QPoint(1450, 0),     # Top right corner, 1
        QPoint(1500, 50),    # Right top-middle, a bit down, 2
        QPoint(1500, 750),   # Bottom right corner, 3
        QPoint(1450, 800),   # Bottom right-middle, 4
        QPoint(1400, 780),   # Bottom left-middle, 5
        QPoint(100, 780),    # Bottom left corner, 6
        QPoint(50, 800),     # Bottom left-middle, 7
        QPoint(0, 750),      # Bottom left corner, 8
        QPoint(0, 50),       # Left top-middle, a bit down, 9
        QPoint(50, 0)        # Top left corner, 10
    ]
    polygon = QPolygon(points)
    return QRegion(polygon)


def openSettings():
    print("Settings button clicked.")  # Placeholder for settings functionality


class CustomShapeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.internal_window = None
        self.close_button = None
        self.settings_button = None
        self.minimize_button = None
        self.predator_font = None
        self.button_font = None
        self.logo_pixmap = None
        self.initUI()

    def initUI(self):
        # Set window size
        self.setFixedSize(1500, 800)  # Adjust size as needed

        # Set window flags to remove the title bar and make it frameless
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Make the window transparent
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Load custom fonts
        self.loadPredatorFont()
        self.loadButtonFont()

        # Load logo
        self.loadLogo()

        # Define the custom shape
        self.setMask(createMask())

        # Add buttons
        self.addButtons()

        # Add the internal window shape
        self.internal_window = InternalWindow(self)
        self.internal_window.show()

    def loadPredatorFont(self):
        # Load the font from the Fonts directory
        font_path = os.path.join(os.path.dirname(__file__), '../Fonts', 'Squares-Bold.otf')
        font_id = QFontDatabase.addApplicationFont(font_path)

        if font_id == -1:
            print("Failed to load predator font.")
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.predator_font = QFont(font_family, 30, QFont.Bold)  # Adjust font size here

    def loadButtonFont(self):
        # Load the italic font for buttons
        font_path = os.path.join(os.path.dirname(__file__), '../Fonts', 'Squares-Bold-Italic.otf')
        font_id = QFontDatabase.addApplicationFont(font_path)

        if font_id == -1:
            print("Failed to load button font.")
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.button_font = QFont(font_family, 25, QFont.Bold)  # Adjust font size for buttons

    def loadLogo(self):
        # Load the logo image from the working directory
        logo_path = os.path.join(os.path.dirname(__file__), '../PredatorLogo.png')
        if os.path.exists(logo_path):
            self.logo_pixmap = QPixmap(logo_path)
        else:
            print("Logo image not found.")

    def addButtons(self):
        # Create a QWidget to hold the buttons
        button_widget = QWidget(self)
        button_widget.setGeometry(QRect(self.width() - 200, 0, 200, 40))
        button_widget.setAttribute(Qt.WA_TranslucentBackground)

        # Create the buttons
        self.settings_button = QPushButton('⚙', button_widget)
        self.settings_button.setGeometry(0, 0, 40, 40)
        self.settings_button.clicked.connect(openSettings)
        self.settings_button.setFont(self.button_font)  # Set button font

        self.minimize_button = QPushButton('—', button_widget)
        self.minimize_button.setGeometry(50, 0, 40, 40)
        self.minimize_button.clicked.connect(self.minimizeWindow)
        self.minimize_button.setFont(self.button_font)  # Set button font

        self.close_button = QPushButton('X', button_widget)
        self.close_button.setGeometry(100, 0, 40, 40)
        self.close_button.clicked.connect(self.closeWindow)
        self.close_button.setFont(self.button_font)  # Set button font

        # Set button styles (optional)
        for button in [self.settings_button, self.minimize_button, self.close_button]:
            button.setStyleSheet("color: #acacac; border: none; font-size: 25px;")
            button.setFixedSize(40, 40)

    def minimizeWindow(self):
        self.showMinimized()

    def closeWindow(self):
        self.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background or other custom content
        painter.setBrush(QBrush(QColor("#292929")))  # Set a background color
        painter.drawRect(self.rect())

        # Draw the logo in the top left corner, slightly moved to the right
        if self.logo_pixmap:
            painter.drawPixmap(60, 20, self.logo_pixmap)  # Adjust position as needed

        # Set the custom font if loaded
        if hasattr(self, 'predator_font'):
            painter.setFont(self.predator_font)

        # Create a QPainterPath for the inverted trapezoid background
        path = QPainterPath()
        path.moveTo(self.width() / 2 - 200, 0)  # Top left corner of the trapezoid
        path.lineTo(self.width() / 2 + 200, 0)  # Top right corner of the trapezoid
        path.lineTo(self.width() / 2 + 150, 70)  # Bottom right corner of the trapezoid
        path.lineTo(self.width() / 2 - 150, 70)  # Bottom left corner of the trapezoid
        path.closeSubpath()

        # Create a gradient from "#141414" to "#0D0D0D"
        gradient = QLinearGradient(self.width() / 2 - 200, 0, self.width() / 2 - 200, 70)
        gradient.setColorAt(0, QColor("#141414"))
        gradient.setColorAt(1, QColor("#0D0D0D"))

        # Set the gradient brush for the trapezoid background
        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)

        # Set the border for the trapezoid
        # border_pen = QPen(QColor("#00B0C8"), 3)  # Create a pen with border color and width
        # painter.setPen(border_pen)
        # painter.drawPath(path)  # Draw the trapezoid border

        # Center the text horizontally
        text = "PredatorSense"
        text_rect = painter.fontMetrics().boundingRect(text)
        text_width = text_rect.width()
        text_x = (self.width() - text_width) // 2
        text_y = 50  # Position text below the trapezoid background

        # Draw "Predator" and "Sense" with different colors
        painter.setPen(QColor("#d8d8d8"))  # Set color for "Predator"
        painter.drawText(text_x, text_y, "Predator")

        painter.setPen(QColor("#acacac"))  # Set color for "Sense"
        painter.drawText(text_x + painter.fontMetrics().width("Predator"), text_y, "Sense")


