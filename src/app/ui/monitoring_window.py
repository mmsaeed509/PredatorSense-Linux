from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush, QRegion, QPolygon, QPen, QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTabWidget, QFrame)
from app.utils.ui_utils import CircularGauge
from app.core import CoreController
from config import DEFAULT_FONT_FAMILY

class MonitoringWindow(QWidget):
    def __init__(self, parent=None, controller: CoreController = None):
        super().__init__(parent)
        self.controller = controller
        self.setGeometry(300, 100, 1100, 600)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.polygon = self._create_mask()
        self._build_ui()

    def _create_mask(self):
        points = [
            QPoint(1080, 0), QPoint(1100, 20),
            QPoint(1100, 580), QPoint(1080, 600),
            QPoint(20, 600), QPoint(0, 580),
            QPoint(0, 560), QPoint(20, 540),
            QPoint(20, 60), QPoint(0, 40),
            QPoint(0, 20), QPoint(20, 0),
        ]
        polygon = QPolygon(points)
        self.setMask(QRegion(polygon))
        return polygon

    def _build_ui(self):
        wrapper = QWidget(self)
        wrapper.setAttribute(Qt.WA_TranslucentBackground)
        wrapper.setGeometry(30, 20, self.width() - 60, self.height() - 40)

        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(20)

        # Tab widget with custom style
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #1a1a1a;
                color: #9aa0a6;
                border: 1px solid #2a2a2a;
                padding: 8px 25px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #0e2c31;
                color: #00B0C8;
                border: 1px solid #00B0C8;
            }
            QTabBar::tab:hover:!selected {
                border-color: #00B0C8;
            }
        """)

        # CPU/GPU Tab
        cpu_gpu_tab = QWidget()
        cpu_gpu_layout = QVBoxLayout(cpu_gpu_tab)
        
        # CPU Section
        cpu_section = self._create_section("CPU", "Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz")
        cpu_metrics = QHBoxLayout()
        
        # Temperature with graph
        temp_box = QVBoxLayout()
        temp_box.addWidget(QLabel("Temperature (°C) / Loading (%)"))
        temp_box.addWidget(self._create_graph_placeholder())
        
        # Stats column
        stats_box = QVBoxLayout()
        stats = [
            ("Fan speed", "3540 RPM"),
            ("Frequency", "3760 MHz"),
            ("Voltage", "1.091 V")
        ]
        for label, value in stats:
            stat_row = self._create_stat_row(label, value)
            stats_box.addLayout(stat_row)
        
        cpu_metrics.addLayout(temp_box, 2)
        cpu_metrics.addLayout(stats_box, 1)
        cpu_section.addLayout(cpu_metrics)
        cpu_gpu_layout.addLayout(cpu_section)
        
        # GPU Section (similar structure)
        gpu_section = self._create_section("GPU", "GeForce GTX 1660 Ti")
        gpu_metrics = QHBoxLayout()
        
        temp_box = QVBoxLayout()
        temp_box.addWidget(QLabel("Temperature (°C) / Loading (%)"))
        temp_box.addWidget(self._create_graph_placeholder())
        
        stats_box = QVBoxLayout()
        stats = [
            ("Fan speed", "3960 RPM"),
            ("Core Clock", "1710 MHz")
        ]
        for label, value in stats:
            stat_row = self._create_stat_row(label, value)
            stats_box.addLayout(stat_row)
            
        gpu_metrics.addLayout(temp_box, 2)
        gpu_metrics.addLayout(stats_box, 1)
        gpu_section.addLayout(gpu_metrics)
        cpu_gpu_layout.addLayout(gpu_section)
        
        # System Tab
        system_tab = QWidget()
        system_layout = QVBoxLayout(system_tab)
        
        # System metrics
        system_metrics = QHBoxLayout()
        metrics = [
            ("Temperature", "Min: 53°", "Max: 65°"),
            ("RAM\nFrequency", "2667 MHz", "Usage: 4.8 GB (30.6%)"),
            ("Ethernet\nDownload", "0.0 Kbps", "Upload: 0.1 Kbps"),
            ("Wi-Fi\nDownload", "20.9 Kbps", "Upload: 2.7 Kbps")
        ]
        
        for title, stat1, stat2 in metrics:
            metric_box = self._create_metric_box(title, stat1, stat2)
            system_metrics.addLayout(metric_box)
            
        system_layout.addLayout(system_metrics)
        system_layout.addStretch()

        # Add tabs
        self.tabs.addTab(cpu_gpu_tab, "CPU / GPU")
        self.tabs.addTab(system_tab, "System")
        layout.addWidget(self.tabs)

    def _create_section(self, title, subtitle):
        section = QVBoxLayout()
        header = QHBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #00B0C8; font-size: 14px; font-weight: bold;")
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: #9aa0a6; font-size: 12px;")
        
        header.addWidget(title_label)
        header.addWidget(subtitle_label)
        header.addStretch()
        
        section.addLayout(header)
        return section

    def _create_stat_row(self, label, value):
        row = QHBoxLayout()
        label = QLabel(label)
        label.setStyleSheet("color: #9aa0a6;")
        value = QLabel(value)
        value.setStyleSheet("color: #00B0C8;")
        row.addWidget(label)
        row.addStretch()
        row.addWidget(value)
        return row

    def _create_graph_placeholder(self):
        # Placeholder for the graph area
        graph = QFrame()
        graph.setStyleSheet("background: #1a1a1a; border: 1px solid #2a2a2a;")
        graph.setMinimumHeight(100)
        return graph

    def _create_metric_box(self, title, stat1, stat2):
        box = QVBoxLayout()
        box.setSpacing(4)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #9aa0a6; font-weight: bold;")
        
        stat1_label = QLabel(stat1)
        stat1_label.setStyleSheet("color: #00B0C8;")
        
        stat2_label = QLabel(stat2)
        stat2_label.setStyleSheet("color: #00B0C8;")
        
        box.addWidget(title_label)
        box.addWidget(stat1_label)
        box.addWidget(stat2_label)
        box.addStretch()
        
        return box

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
