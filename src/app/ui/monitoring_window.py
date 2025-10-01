from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QPainter, QColor, QBrush, QRegion, QPolygon, QPen, QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTabWidget, QFrame)
from app.utils.ui_utils import CircularGauge
from app.core import CoreController
from app.core.metrics_service import CPUMetrics, GPUMetrics, SystemMetrics
from app.ui.temperature_graph import TemperatureGraph
from config import DEFAULT_FONT_FAMILY

class MonitoringWindow(QWidget):
    def __init__(self, parent=None, controller: CoreController = None):
        super().__init__(parent)
        self.controller = controller
        self.setGeometry(300, 100, 1100, 600)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.polygon = self._create_mask()
        
        # Store references to dynamic labels and graphs
        self.cpu_labels = {}
        self.gpu_labels = {}
        self.system_labels = {}
        self.cpu_graph = None
        self.gpu_graph = None
        self.system_graph = None
        
        self._build_ui()
        self._connect_signals()
        
        # Update timer for UI refresh
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(1000)  # Update every second

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
        cpu_section = self._create_section("CPU", "Loading...")
        self.cpu_labels['name'] = cpu_section.itemAt(0).layout().itemAt(1).widget()
        cpu_metrics = QHBoxLayout()
        
        # Temperature with graph
        temp_box = QVBoxLayout()
        temp_label = QLabel("Temperature (°C) / Loading (%)")
        temp_label.setStyleSheet("color: #9aa0a6;")
        temp_box.addWidget(temp_label)
        
        # Min/Max temp display
        minmax_layout = QHBoxLayout()
        self.cpu_labels['min_temp'] = QLabel("Min: --°")
        self.cpu_labels['max_temp'] = QLabel("Max: --°")
        self.cpu_labels['min_temp'].setStyleSheet("color: #9aa0a6; font-size: 10px;")
        self.cpu_labels['max_temp'].setStyleSheet("color: #9aa0a6; font-size: 10px;")
        minmax_layout.addWidget(self.cpu_labels['min_temp'])
        minmax_layout.addStretch()
        minmax_layout.addWidget(self.cpu_labels['max_temp'])
        temp_box.addLayout(minmax_layout)
        
        # Create CPU temperature graph
        self.cpu_graph = TemperatureGraph()
        temp_box.addWidget(self.cpu_graph)
        
        # Stats column
        stats_box = QVBoxLayout()
        
        # Create dynamic stat rows
        self.cpu_labels['fan_speed'] = self._create_dynamic_stat_row("Fan speed", "-- RPM", stats_box)
        self.cpu_labels['frequency'] = self._create_dynamic_stat_row("Frequency", "-- MHz", stats_box)
        self.cpu_labels['voltage'] = self._create_dynamic_stat_row("Voltage", "-- V", stats_box)
        
        cpu_metrics.addLayout(temp_box, 2)
        cpu_metrics.addLayout(stats_box, 1)
        cpu_section.addLayout(cpu_metrics)
        cpu_gpu_layout.addLayout(cpu_section)
        
        # GPU Section
        gpu_section = self._create_section("GPU", "Loading...")
        self.gpu_labels['name'] = gpu_section.itemAt(0).layout().itemAt(1).widget()
        gpu_metrics = QHBoxLayout()
        
        temp_box = QVBoxLayout()
        temp_label = QLabel("Temperature (°C) / Loading (%)")
        temp_label.setStyleSheet("color: #9aa0a6;")
        temp_box.addWidget(temp_label)
        
        # Min/Max temp display
        minmax_layout = QHBoxLayout()
        self.gpu_labels['min_temp'] = QLabel("Min: --°")
        self.gpu_labels['max_temp'] = QLabel("Max: --°")
        self.gpu_labels['min_temp'].setStyleSheet("color: #9aa0a6; font-size: 10px;")
        self.gpu_labels['max_temp'].setStyleSheet("color: #9aa0a6; font-size: 10px;")
        minmax_layout.addWidget(self.gpu_labels['min_temp'])
        minmax_layout.addStretch()
        minmax_layout.addWidget(self.gpu_labels['max_temp'])
        temp_box.addLayout(minmax_layout)
        
        # Create GPU temperature graph
        self.gpu_graph = TemperatureGraph()
        temp_box.addWidget(self.gpu_graph)
        
        stats_box = QVBoxLayout()
        
        # Create dynamic stat rows
        self.gpu_labels['fan_speed'] = self._create_dynamic_stat_row("Fan speed", "-- RPM", stats_box)
        self.gpu_labels['core_clock'] = self._create_dynamic_stat_row("Core Clock", "-- MHz", stats_box)
            
        gpu_metrics.addLayout(temp_box, 2)
        gpu_metrics.addLayout(stats_box, 1)
        gpu_section.addLayout(gpu_metrics)
        cpu_gpu_layout.addLayout(gpu_section)
        
        # System Tab
        system_tab = QWidget()
        system_layout = QVBoxLayout(system_tab)
        
        # System temperature graph section
        temp_section = QVBoxLayout()
        temp_header = QLabel("System Temperature (°C)")
        temp_header.setStyleSheet("color: #00B0C8; font-size: 14px; font-weight: bold;")
        temp_section.addWidget(temp_header)
        
        # Min/Max temp display for system
        sys_minmax_layout = QHBoxLayout()
        self.system_labels['min_temp'] = QLabel("Min: --°")
        self.system_labels['max_temp'] = QLabel("Max: --°")
        self.system_labels['min_temp'].setStyleSheet("color: #9aa0a6; font-size: 10px;")
        self.system_labels['max_temp'].setStyleSheet("color: #9aa0a6; font-size: 10px;")
        sys_minmax_layout.addWidget(self.system_labels['min_temp'])
        sys_minmax_layout.addStretch()
        sys_minmax_layout.addWidget(self.system_labels['max_temp'])
        temp_section.addLayout(sys_minmax_layout)
        
        # Create system temperature graph
        self.system_graph = TemperatureGraph()
        temp_section.addWidget(self.system_graph)
        system_layout.addLayout(temp_section)
        
        # System metrics
        system_metrics = QHBoxLayout()
        
        # RAM section
        ram_box = self._create_dynamic_metric_box("RAM\nFrequency", "-- MHz", "Usage: -- GB (--%)")
        self.system_labels['ram_frequency'] = ram_box['stat1']
        self.system_labels['ram_usage'] = ram_box['stat2']
        system_metrics.addLayout(ram_box['layout'])
        
        # Ethernet section
        eth_box = self._create_dynamic_metric_box("Ethernet\nDownload", "-- Kbps", "Upload: -- Kbps")
        self.system_labels['eth_download'] = eth_box['stat1']
        self.system_labels['eth_upload'] = eth_box['stat2']
        system_metrics.addLayout(eth_box['layout'])
        
        # Wi-Fi section
        wifi_box = self._create_dynamic_metric_box("Wi-Fi\nDownload", "-- Kbps", "Upload: -- Kbps")
        self.system_labels['wifi_download'] = wifi_box['stat1']
        self.system_labels['wifi_upload'] = wifi_box['stat2']
        system_metrics.addLayout(wifi_box['layout'])
            
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

    def _create_dynamic_stat_row(self, label_text, initial_value, parent_layout):
        """Create a stat row and return the value label for dynamic updates."""
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("color: #9aa0a6;")
        value_label = QLabel(initial_value)
        value_label.setStyleSheet("color: #00B0C8;")
        row.addWidget(label)
        row.addStretch()
        row.addWidget(value_label)
        parent_layout.addLayout(row)
        return value_label
    
    def _create_dynamic_metric_box(self, title, stat1, stat2):
        """Create a metric box and return references to dynamic labels."""
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
        
        return {
            'layout': box,
            'stat1': stat1_label,
            'stat2': stat2_label
        }

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
    
    def _connect_signals(self):
        """Connect to controller signals for real-time updates."""
        if self.controller and self.controller.metrics:
            self.controller.metrics.cpuMetricsUpdated.connect(self._update_cpu_metrics)
            self.controller.metrics.gpuMetricsUpdated.connect(self._update_gpu_metrics)
            self.controller.metrics.systemMetricsUpdated.connect(self._update_system_metrics)
    
    def _update_cpu_metrics(self, cpu_metrics: CPUMetrics):
        """Update CPU metrics display."""
        self.cpu_labels['name'].setText(cpu_metrics.name)
        
        if cpu_metrics.fan_speed > 0:
            self.cpu_labels['fan_speed'].setText(f"{cpu_metrics.fan_speed} RPM")
        else:
            self.cpu_labels['fan_speed'].setText("-- RPM")
            
        if cpu_metrics.frequency > 0:
            self.cpu_labels['frequency'].setText(f"{cpu_metrics.frequency} MHz")
        else:
            self.cpu_labels['frequency'].setText("-- MHz")
            
        if cpu_metrics.voltage > 0:
            self.cpu_labels['voltage'].setText(f"{cpu_metrics.voltage:.3f} V")
        else:
            self.cpu_labels['voltage'].setText("-- V")
            
        self.cpu_labels['min_temp'].setText(f"Min: {cpu_metrics.min_temp}°")
        self.cpu_labels['max_temp'].setText(f"Max: {cpu_metrics.max_temp}°")
        
        # Update CPU graph
        if self.cpu_graph:
            self.cpu_graph.add_data_point(cpu_metrics.temperature, cpu_metrics.usage)
    
    def _update_gpu_metrics(self, gpu_metrics: GPUMetrics):
        """Update GPU metrics display."""
        self.gpu_labels['name'].setText(gpu_metrics.name)
        
        if gpu_metrics.fan_speed > 0:
            self.gpu_labels['fan_speed'].setText(f"{gpu_metrics.fan_speed} RPM")
        else:
            self.gpu_labels['fan_speed'].setText("-- RPM")
            
        if gpu_metrics.core_clock > 0:
            self.gpu_labels['core_clock'].setText(f"{gpu_metrics.core_clock} MHz")
        else:
            self.gpu_labels['core_clock'].setText("-- MHz")
            
        self.gpu_labels['min_temp'].setText(f"Min: {gpu_metrics.min_temp}°")
        self.gpu_labels['max_temp'].setText(f"Max: {gpu_metrics.max_temp}°")
        
        # Update GPU graph
        if self.gpu_graph:
            self.gpu_graph.add_data_point(gpu_metrics.temperature, gpu_metrics.usage)
    
    def _update_system_metrics(self, system_metrics: SystemMetrics):
        """Update system metrics display."""
        self.system_labels['min_temp'].setText(f"Min: {system_metrics.min_temp}°")
        self.system_labels['max_temp'].setText(f"Max: {system_metrics.max_temp}°")
        
        if system_metrics.ram_frequency > 0:
            self.system_labels['ram_frequency'].setText(f"{system_metrics.ram_frequency} MHz")
        else:
            self.system_labels['ram_frequency'].setText("-- MHz")
            
        if system_metrics.ram_total_gb > 0:
            self.system_labels['ram_usage'].setText(
                f"Usage: {system_metrics.ram_usage_gb} GB ({system_metrics.ram_usage_percent}%)"
            )
        else:
            self.system_labels['ram_usage'].setText("Usage: -- GB (--%)")
            
        self.system_labels['eth_download'].setText(f"{system_metrics.ethernet_download} Kbps")
        self.system_labels['eth_upload'].setText(f"Upload: {system_metrics.ethernet_upload} Kbps")
        
        self.system_labels['wifi_download'].setText(f"{system_metrics.wifi_download} Kbps")
        self.system_labels['wifi_upload'].setText(f"Upload: {system_metrics.wifi_upload} Kbps")
        
        # Update system temperature graph (using RAM usage as a proxy for system load)
        if self.system_graph:
            self.system_graph.add_data_point(system_metrics.temperature, system_metrics.ram_usage_percent)
    
    def _update_display(self):
        """Periodic update to refresh display with latest metrics."""
        if self.controller and self.controller.metrics:
            # Trigger updates with current metrics
            cpu_metrics = self.controller.metrics.get_cpu_metrics()
            gpu_metrics = self.controller.metrics.get_gpu_metrics()
            system_metrics = self.controller.metrics.get_system_metrics()
            
            self._update_cpu_metrics(cpu_metrics)
            self._update_gpu_metrics(gpu_metrics)
            self._update_system_metrics(system_metrics)

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
