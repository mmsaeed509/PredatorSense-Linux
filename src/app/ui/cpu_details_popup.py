from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QPainter, QColor, QBrush, QRegion, QPolygon, QPen, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import pyqtSignal
from config import DEFAULT_FONT_FAMILY


class CPUDetailsPopup(QFrame):
    """CPU Details popup showing individual core frequencies and temperatures."""
    
    closed = pyqtSignal()  # Signal emitted when popup is closed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Popup behavior and look (same as SettingsPopup)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("CPUDetailsPopup")
        
        # Core data storage
        self.core_labels = {}
        self.core_count = 12  # Default for i7-9750H (6 cores, 12 threads)
        
        # Base widget to draw rounded rect via stylesheet (like SettingsPopup)
        self.container = QWidget(self)
        self.container.setObjectName("container")
        
        self._build_ui()
        
        # Overall size
        self.resize(450, 350)
        self.container.setGeometry(0, 0, self.width(), self.height())
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.request_update)
        self.update_timer.start(1000)  # Update every second
    
    def _build_ui(self):
        """Build the popup UI with core details."""
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # Header row to show column labels
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        core_header = QLabel("Core")
        core_header.setStyleSheet("color: #00B0C8; font-size: 11px; font-weight: bold;")
        core_header.setMinimumWidth(80)
        
        freq_header = QLabel("Frequency")
        freq_header.setStyleSheet("color: #00B0C8; font-size: 11px; font-weight: bold;")
        freq_header.setMinimumWidth(90)
        freq_header.setAlignment(Qt.AlignRight)
        
        temp_header = QLabel("Temperature")
        temp_header.setStyleSheet("color: #00B0C8; font-size: 11px; font-weight: bold;")
        temp_header.setMinimumWidth(60)
        temp_header.setAlignment(Qt.AlignRight)
        
        header_layout.addWidget(core_header)
        header_layout.addStretch()
        header_layout.addWidget(freq_header)
        header_layout.addWidget(temp_header)
        
        layout.addLayout(header_layout)
        
        # Separator line (same style as SettingsPopup)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #00B0C8;")
        layout.addWidget(separator)
        
        # Core details container
        cores_container = QVBoxLayout()
        cores_container.setSpacing(4)
        
        # Create labels for each core
        for i in range(self.core_count):
            core_layout = self._create_core_row(i + 1)
            cores_container.addLayout(core_layout)
        
        layout.addLayout(cores_container)
        layout.addStretch()
        
        # Apply stylesheet similar to SettingsPopup
        self.setStyleSheet("""
            QWidget#container {
                background: #1A1A1A;
                border: 1px solid #00B0C8;
                border-radius: 6px;
            }
        """)
    
    def _create_core_row(self, core_num):
        """Create a row for a single core showing frequency and temperature."""
        row = QHBoxLayout()
        row.setSpacing(10)
        
        # Core label
        core_label = QLabel(f"Core #{core_num}")
        core_label.setStyleSheet("color: #d3d6d8; font-size: 12px; font-weight: bold;")
        core_label.setMinimumWidth(80)
        
        # Frequency label
        freq_label = QLabel("0 MHz")
        freq_label.setStyleSheet("color: #d3d6d8; font-size: 12px;")
        freq_label.setMinimumWidth(90)
        freq_label.setAlignment(Qt.AlignRight)
        
        # Temperature label
        temp_label = QLabel("0 °C")
        temp_label.setStyleSheet("color: #d3d6d8; font-size: 12px;")
        temp_label.setMinimumWidth(60)
        temp_label.setAlignment(Qt.AlignRight)
        
        # Store references for updates
        self.core_labels[core_num] = {
            'frequency': freq_label,
            'temperature': temp_label
        }
        
        row.addWidget(core_label)
        row.addStretch()
        row.addWidget(freq_label)
        row.addWidget(temp_label)
        
        return row
    
    def update_core_data(self, core_frequencies, core_temperatures):
        """Update the display with new core data."""
        for core_num in range(1, min(self.core_count + 1, len(core_frequencies) + 1)):
            if core_num in self.core_labels:
                # Update frequency
                if core_num - 1 < len(core_frequencies):
                    freq = core_frequencies[core_num - 1]
                    self.core_labels[core_num]['frequency'].setText(f"{freq} MHz")
                
                # Update temperature
                if core_num - 1 < len(core_temperatures):
                    temp = core_temperatures[core_num - 1]
                    self.core_labels[core_num]['temperature'].setText(f"{temp}°C")
    
    def request_update(self):
        """Request updated core data from parent."""
        if self.parent():
            self.parent().update_cpu_details_popup()
    
    # No paintEvent needed - styling handled by stylesheet like SettingsPopup
    
    def showAt(self, global_pos: QPoint):
        """Show the popup with its top-right positioned at the provided global position."""
        x = global_pos.x() - self.width() + 20  # Position to the left of the trigger point
        y = global_pos.y() + 10  # Slightly below the trigger
        self.move(x, y)
        self.show()
    
    def mousePressEvent(self, event):
        """Close popup when clicking outside."""
        if not self.rect().contains(event.pos()):
            self.close()
        super().mousePressEvent(event)
    
    def closeEvent(self, event):
        """Emit closed signal when popup is closed."""
        self.update_timer.stop()
        self.closed.emit()
        super().closeEvent(event)