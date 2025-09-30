import os
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPainter, QBrush, QPolygon, QColor, QRegion, QFont, QFontDatabase, QPixmap, QPainterPath, \
    QLinearGradient, QPen
from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QWidget,
    QApplication,
    QVBoxLayout,
    QButtonGroup,
)
from app.ui.internal_window import InternalWindow
from app.ui.fan_control_window import FanControlWindow
from app.ui.settings_popup import SettingsPopup
from app.ui.monitoring_window import MonitoringWindow
from app.ui.battery_usb_window import BatteryUSBWindow
from app.utils import ui_utils
from config import WM_CLASS, WM_CLASS_2, FONTS_DIR, ICONS_DIR, DEFAULT_FONT_FAMILY
from app.utils import x11_utils
from app.core import CoreController, Tab
from app.core.models import TemperatureUnit

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

 


class CustomShapeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = CoreController(self)
        self.internal_window = None
        self.fan_window = None
        self.monitoring_window = None
        self.battery_usb_window = None
        self.current_content = None
        self.close_button = None
        self.settings_button = None
        self.minimize_button = None
        self.settings_popup = None
        self.sidebar = None
        self.menu_group = None
        self.menu_buttons = {}
        self.predator_font = None
        self.button_font = None
        self.logo_pixmap = None
        self._wm_class_set = False
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
        self.internal_window = InternalWindow(self, controller=self.controller)
        self.internal_window.show()
        self.current_content = self.internal_window

        # Sidebar menu
        self.createSidebar()

        # React to tab changes to swap content views
        self.controller.tabChanged.connect(self._onTabChanged)

        # Settings popup
        try:
            family = None
            if self.button_font:
                family = self.button_font.family()
            self.settings_popup = SettingsPopup(self, font_family=family)
            # Wire radios -> controller
            if self.settings_popup:
                self.settings_popup.r_c.toggled.connect(self._onCelsiusToggled)
                self.settings_popup.r_f.toggled.connect(self._onFahrenheitToggled)
                # Controller -> radios (sync)
                self.controller.temperatureUnitChanged.connect(self.settings_popup.setUnit)
                # Initial sync
                self.settings_popup.setUnit(self.controller.temperature_unit)
        except Exception as e:
            print(f"Failed to create settings popup: {e}")

    # Set the WM_CLASS property with instance and class names
    def set_wm_class(self):
        # Get the native window ID
        win_id = self.winId().__int__()
        x11_utils.set_wm_class(win_id, WM_CLASS_2, WM_CLASS)

    def showEvent(self, event):
        super().showEvent(event)
        # Ensure WM_CLASS is set once the native window is created (after show)
        if not self._wm_class_set:
            try:
                self.set_wm_class()
                self._wm_class_set = True
            except Exception as e:
                # Avoid crashing on platforms without X11 or if Xlib is unavailable
                print(f"Failed to set WM_CLASS: {e}")
        # start core services
        try:
            self.controller.start()
        except Exception as e:
            print(f"Controller start error: {e}")

    def loadPredatorFont(self):
        # Load the font from the Fonts directory
        font_path = os.path.join(FONTS_DIR, f'{DEFAULT_FONT_FAMILY}.otf')
        font_id = QFontDatabase.addApplicationFont(font_path)

        if font_id == -1:
            print("Failed to load predator font.")
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.predator_font = QFont(font_family, 30, QFont.Bold)  # Adjust font size here

    def loadButtonFont(self):
        # Use default family for buttons as requested
        font_path = os.path.join(FONTS_DIR, f'{DEFAULT_FONT_FAMILY}.otf')
        font_id = QFontDatabase.addApplicationFont(font_path)

        if font_id == -1:
            print("Failed to load button font.")
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.button_font = QFont(font_family, 25, QFont.Bold)  # Adjust font size for buttons

    def loadLogo(self):
        # Load the logo image from the working directory
        logo_path = os.path.join(ICONS_DIR, 'PredatorLogo.png')
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
        self.settings_button.clicked.connect(self.toggleSettingsPopup)
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

        # Save button widget for geometry reference
        self._button_widget = button_widget

    def toggleSettingsPopup(self):
        if not self.settings_popup:
            return
        if self.settings_popup.isVisible():
            self.settings_popup.hide()
            return
        # Position under the gear button, centered like the screenshot
        try:
            btn_center = self.settings_button.mapToGlobal(self.settings_button.rect().center())
            self.settings_popup.showAt(btn_center)
        except Exception:
            # Fallback: show near top-right
            top_right = self.mapToGlobal(QPoint(self.width() - 140, 40))
            self.settings_popup.showAt(top_right)

    def _onCelsiusToggled(self, checked: bool):
        if checked:
            try:
                self.controller.set_temperature_unit(TemperatureUnit.CELSIUS)
            except Exception as e:
                print(f"Set unit C error: {e}")

    def _onFahrenheitToggled(self, checked: bool):
        if checked:
            try:
                self.controller.set_temperature_unit(TemperatureUnit.FAHRENHEIT)
            except Exception as e:
                print(f"Set unit F error: {e}")

    def minimizeWindow(self):
        self.showMinimized()

    def closeWindow(self):
        self.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background gradient (dark)
        bg_grad = QLinearGradient(0, 0, 0, self.height())
        bg_grad.setColorAt(0.0, QColor("#242323"))
        bg_grad.setColorAt(1.0, QColor("#141414"))
        painter.setBrush(QBrush(bg_grad))
        painter.setPen(Qt.NoPen)
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

        # Create a gradient from "#141414" to "#242323"
        gradient = QLinearGradient(self.width() / 2 - 200, 0, self.width() / 2 - 200, 70)
        gradient.setColorAt(0, QColor("#141414"))
        gradient.setColorAt(1, QColor("#242323"))

        # Set the gradient brush for the trapezoid background
        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)

        # Center the text horizontally
        text = "PredatorSense"
        text_rect = painter.fontMetrics().boundingRect(text)
        text_width = text_rect.width()
        text_x = (self.width() - text_width) // 2
        text_y = 45  # Position text below the trapezoid background

        # Draw "Predator" and "Sense" with different colors
        painter.setPen(QColor("#d8d8d8"))  # Set color for "Predator"
        painter.drawText(text_x, text_y, "Predator")

        painter.setPen(QColor("#acacac"))  # Set color for "Sense"
        painter.drawText(text_x + painter.fontMetrics().width("Predator"), text_y, "Sense")

    def createSidebar(self):
        # Sidebar container
        self.sidebar = QWidget(self)
        self.sidebar.setGeometry(30, 120, 240, 520)
        self.sidebar.setStyleSheet(
            """
            QWidget { background-color: transparent; }
            QPushButton {
                color: #cfcfcf; background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px;
                padding: 10px 14px; text-align: left; font-size: 14px;
            }
            QPushButton:hover { border-color: #00B0C8; }
            QPushButton:checked {
                background: #0e2c31; border: 1px solid #00B0C8; color: #e6feff;
            }
            """
        )

        vbox = QVBoxLayout(self.sidebar)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(10)

        items = [
            "Home",
            "Lighting",
            "Overclocking",
            "Fan Control",
            "Monitoring",
            "Game Sync",
            "Battery and USB",
        ]

        self.menu_group = QButtonGroup(self)
        self.menu_group.setExclusive(True)

        for name in items:
            btn = QPushButton(name)
            btn.setCheckable(True)
            # Apply default font family for sidebar buttons
            if self.predator_font:
                btn.setFont(QFont(self.predator_font.family(), 14, QFont.Bold))
            btn.clicked.connect(lambda checked, n=name: self.onMenuSelected(n))
            vbox.addWidget(btn)
            self.menu_group.addButton(btn)
            self.menu_buttons[name] = btn

        # Default selection
        self.menu_buttons["Home"].setChecked(True)

    def onMenuSelected(self, name: str):
        # Highlighting handled by stylesheet via :checked
        # Update controller tab
        mapping = {
            "Home": Tab.HOME,
            "Lighting": Tab.LIGHTING,
            "Overclocking": Tab.OVERCLOCKING,
            "Fan Control": Tab.FAN_CONTROL,
            "Monitoring": Tab.MONITORING,
            "Game Sync": Tab.GAME_SYNC,
            "Battery and USB": Tab.BATTERY_USB,
        }
        tab = mapping.get(name)
        if tab:
            self.controller.set_tab(tab)

    def _ensureFanWindow(self):
        if self.fan_window is None:
            self.fan_window = FanControlWindow(self, controller=self.controller)
            # Wire buttons -> FanService actions
            try:
                self.fan_window.btn_auto.clicked.connect(lambda: self.controller.fans.set_auto())
                self.fan_window.btn_max.clicked.connect(lambda: self.controller.fans.set_max())
            except Exception:
                pass
            # Wire FanService RPM -> UI
            try:
                self.controller.fans.rpmUpdated.connect(self.fan_window.setRpm)
            except Exception:
                pass

    def _ensureMonitoringWindow(self):
        if self.monitoring_window is None:
            self.monitoring_window = MonitoringWindow(self, controller=self.controller)

    def _ensureBatteryUSBWindow(self):
        if self.battery_usb_window is None:
            self.battery_usb_window = BatteryUSBWindow(self, controller=self.controller)

    def _swapContent(self, new_widget: QWidget):
        if self.current_content is new_widget:
            return
        # Hide previous
        if self.current_content is not None:
            self.current_content.hide()
        # Show new
        if new_widget is not None:
            new_widget.show()
        self.current_content = new_widget

    def _onTabChanged(self, tab: Tab):
        if tab == Tab.FAN_CONTROL:
            self._ensureFanWindow()
            self._swapContent(self.fan_window)
        elif tab == Tab.MONITORING:
            self._ensureMonitoringWindow()
            self._swapContent(self.monitoring_window)
        elif tab == Tab.BATTERY_USB:
            self._ensureBatteryUSBWindow()
            self._swapContent(self.battery_usb_window)
        else:
            # Default to the Home internal window for all other tabs
            self._swapContent(self.internal_window)

    def closeEvent(self, event):
        try:
            self.controller.stop()
        except Exception:
            pass
        super().closeEvent(event)
