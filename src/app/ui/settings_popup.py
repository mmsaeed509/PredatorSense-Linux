from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QRadioButton
from app.core.models import TemperatureUnit
from app.core import linuwu_service as lw


class SettingsPopup(QFrame):
    """Small popup panel with settings toggles, styled similar to the screenshot."""

    def __init__(self, parent: QWidget = None, font_family: str = None):
        super().__init__(parent)
        # Popup behavior and look
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("SettingsPopup")

        # Base widget to draw rounded rect via stylesheet
        self.container = QWidget(self)
        self.container.setObjectName("container")

        # Layouts
        vbox = QVBoxLayout(self.container)
        vbox.setContentsMargins(14, 12, 14, 12)
        vbox.setSpacing(10)

        title1 = QLabel("Advanced Settings")
        title2 = QLabel("Keyboard Settings")
        for t in (title1, title2):
            if font_family:
                t.setFont(QFont(font_family, 10, QFont.DemiBold))
            t.setStyleSheet("color: #2b2f33;")

        # Switch helpers
        def make_switch(text: str, checked: bool = False) -> (QHBoxLayout, QCheckBox):
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(10)
            lbl = QLabel(text)
            if font_family:
                lbl.setFont(QFont(font_family, 10))
            lbl.setStyleSheet("color: #2b2f33;")
            sw = QCheckBox()
            sw.setChecked(checked)
            sw.setCursor(Qt.PointingHandCursor)
            sw.setObjectName("switch")
            row.addWidget(lbl, 1)
            row.addWidget(sw, 0)
            return row, sw

        # Advanced
        vbox.addWidget(title1)
        row, self.chk_boot = make_switch("System boot animation & sound", True)
        vbox.addLayout(row)
        row, self.chk_lcd = make_switch("LCD Overdrive", True)
        vbox.addLayout(row)

        # Temperature units row
        temp_row = QHBoxLayout()
        temp_row.setSpacing(10)
        tlbl = QLabel("Temperature units")
        if font_family:
            tlbl.setFont(QFont(font_family, 10))
        tlbl.setStyleSheet("color: #2b2f33;")
        self.r_c = QRadioButton("°C")
        self.r_f = QRadioButton("°F")
        self.r_c.setChecked(True)
        for r in (self.r_c, self.r_f):
            r.setCursor(Qt.PointingHandCursor)
            if font_family:
                r.setFont(QFont(font_family, 10))
            r.setStyleSheet("color: #2b2f33;")
        temp_row.addWidget(tlbl, 1)
        temp_row.addWidget(self.r_c)
        temp_row.addWidget(self.r_f)
        vbox.addLayout(temp_row)

        # Separator
        from PyQt5.QtWidgets import QFrame as _QFrame
        sep = _QFrame()
        sep.setFrameShape(_QFrame.HLine)
        sep.setStyleSheet("color: #d3d6d8;")
        vbox.addWidget(sep)

        # Keyboard
        vbox.addWidget(title2)
        row, self.chk_backlight = make_switch("Backlight off after 30 seconds", False)
        vbox.addLayout(row)
        # Placeholders for future features
        row, self.chk_sticky = make_switch("Sticky keys", False)
        vbox.addLayout(row)
        row, self.chk_winmenu = make_switch("Windows and menu key", True)
        vbox.addLayout(row)

        # Overall size
        self.resize(360, 260)
        self.container.setGeometry(0, 0, self.width(), self.height())

        # Stylesheet: light panel and switches
        self.setStyleSheet(
            """
            QWidget#container {
                background: #e9eef0;
                border: 1px solid #cdd3d6;
                border-radius: 6px;
            }
            QCheckBox#switch {
                spacing: 8px; /* no label, but keep standard spacing */
            }
            QCheckBox#switch::indicator {
                width: 46px; height: 24px;
            }
            QCheckBox#switch::indicator:unchecked {
                border-radius: 12px;
                background: #6a6f73;
            }
            QCheckBox#switch::indicator:unchecked:hover {
                background: #7a8084;
            }
            QCheckBox#switch::indicator:checked {
                border-radius: 12px;
                background: #00B0C8;
            }
            QRadioButton::indicator { width: 16px; height: 16px; }
            QRadioButton::indicator:checked { background: #00B0C8; border: 2px solid #007d8e; border-radius: 8px; }
            QRadioButton::indicator:unchecked { background: #b8bec2; border: 2px solid #8b9094; border-radius: 8px; }
            """
        )
        # Bind events and load current states once
        self._post_init()

    def showAt(self, global_pos: QPoint):
        """Show the popup with its top centered at the provided global position."""
        x = global_pos.x() - self.width() // 2
        y = global_pos.y() + 10
        self.move(x, y)
        # Refresh states from system each time we show
        self._refresh_states()
        self.show()

    def setUnit(self, unit: TemperatureUnit):
        if unit == TemperatureUnit.FAHRENHEIT:
            self.r_f.setChecked(True)
        else:
            self.r_c.setChecked(True)

    # --- Linuwu-Sense bindings ---
    def _refresh_states(self):
        try:
            v = lw.get_boot_animation_enabled()
            if v is not None:
                self.chk_boot.blockSignals(True)
                self.chk_boot.setChecked(bool(v))
                self.chk_boot.blockSignals(False)
        except Exception:
            pass
        try:
            v = lw.get_lcd_override_enabled()
            if v is not None:
                self.chk_lcd.blockSignals(True)
                self.chk_lcd.setChecked(bool(v))
                self.chk_lcd.blockSignals(False)
        except Exception:
            pass
        try:
            v = lw.get_backlight_timeout_enabled()
            if v is not None:
                self.chk_backlight.blockSignals(True)
                self.chk_backlight.setChecked(bool(v))
                self.chk_backlight.blockSignals(False)
        except Exception:
            pass

    def _bind_handlers(self):
        self.chk_boot.toggled.connect(self._on_boot_toggled)
        self.chk_lcd.toggled.connect(self._on_lcd_toggled)
        self.chk_backlight.toggled.connect(self._on_backlight_toggled)

    def _on_boot_toggled(self, checked: bool):
        ok = lw.set_boot_animation_enabled(bool(checked))
        if not ok:
            # revert
            self.chk_boot.blockSignals(True)
            self.chk_boot.setChecked(not checked)
            self.chk_boot.blockSignals(False)

    def _on_lcd_toggled(self, checked: bool):
        ok = lw.set_lcd_override_enabled(bool(checked))
        if not ok:
            self.chk_lcd.blockSignals(True)
            self.chk_lcd.setChecked(not checked)
            self.chk_lcd.blockSignals(False)

    def _on_backlight_toggled(self, checked: bool):
        ok = lw.set_backlight_timeout_enabled(bool(checked))
        if not ok:
            self.chk_backlight.blockSignals(True)
            self.chk_backlight.setChecked(not checked)
            self.chk_backlight.blockSignals(False)

    # After building UI, bind handlers and try initial refresh
    def _post_init(self):
        self._bind_handlers()
        self._refresh_states()

    # Call post-init at end of __init__
        
