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
        cpu_gpu_layout.setSpacing(30)
        
        # CPU Section
        cpu_container = QVBoxLayout()
        cpu_container.setSpacing(10)
        
        # CPU Header
        cpu_header = QHBoxLayout()
        cpu_title = QLabel("CPU")
        cpu_title.setStyleSheet("color: #00B0C8; font-size: 16px; font-weight: bold;")
        self.cpu_labels['name'] = QLabel("Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz")
        self.cpu_labels['name'].setStyleSheet("color: #9aa0a6; font-size: 12px;")
        details_link = QLabel("Details")
        details_link.setStyleSheet("color: #00B0C8; font-size: 12px; text-decoration: underline;")
        
        cpu_header.addWidget(cpu_title)
        cpu_header.addWidget(self.cpu_labels['name'])
        cpu_header.addStretch()
        cpu_header.addWidget(details_link)
        cpu_container.addLayout(cpu_header)
        
        # CPU Content
        cpu_content = QHBoxLayout()
        cpu_content.setSpacing(20)
        
        # CPU Graph Section
        cpu_graph_section = QVBoxLayout()
        cpu_graph_section.setSpacing(5)
        
        temp_label = QLabel("Temperature (°C) / Loading (%)")
        temp_label.setStyleSheet("color: #9aa0a6; font-size: 11px;")
        cpu_graph_section.addWidget(temp_label)
        
        # Min/Max for CPU
        cpu_minmax = QHBoxLayout()
        self.cpu_labels['min_temp'] = QLabel("Min: 77°")
        self.cpu_labels['max_temp'] = QLabel("Max: 90°")
        self.cpu_labels['min_temp'].setStyleSheet("color: #9aa0a6; font-size: 10px;")
        self.cpu_labels['max_temp'].setStyleSheet("color: #9aa0a6; font-size: 10px;")
        cpu_minmax.addWidget(self.cpu_labels['min_temp'])
        cpu_minmax.addStretch()
        cpu_minmax.addWidget(self.cpu_labels['max_temp'])
        cpu_graph_section.addLayout(cpu_minmax)
        
        # CPU Graph with temperature display
        cpu_graph_container = QHBoxLayout()
        self.cpu_graph = TemperatureGraph()
        self.cpu_graph.setMinimumHeight(120)
        
        # Temperature and percentage display
        cpu_display = QVBoxLayout()
        cpu_display.setAlignment(Qt.AlignCenter)
        self.cpu_labels['temp_display'] = QLabel("90°")
        self.cpu_labels['temp_display'].setStyleSheet("color: #00B0C8; font-size: 32px; font-weight: bold;")
        self.cpu_labels['usage_display'] = QLabel("16 %")
        self.cpu_labels['usage_display'].setStyleSheet("color: #00B0C8; font-size: 16px;")
        cpu_display.addWidget(self.cpu_labels['temp_display'])
        cpu_display.addWidget(self.cpu_labels['usage_display'])
        
        cpu_graph_container.addWidget(self.cpu_graph, 3)
        cpu_graph_container.addLayout(cpu_display, 1)
        cpu_graph_section.addLayout(cpu_graph_container)
        
        # CPU Stats Section
        cpu_stats = QVBoxLayout()
        cpu_stats.setSpacing(15)
        cpu_stats.setAlignment(Qt.AlignTop)
        
        self.cpu_labels['fan_speed'] = self._create_stat_item("Fan speed", "3540 RPM")
        self.cpu_labels['frequency'] = self._create_stat_item("Frequency", "3760 MHz")
        self.cpu_labels['voltage'] = self._create_stat_item("Voltage", "1.091 V")
        
        cpu_stats.addLayout(self.cpu_labels['fan_speed']['layout'])
        cpu_stats.addLayout(self.cpu_labels['frequency']['layout'])
        cpu_stats.addLayout(self.cpu_labels['voltage']['layout'])
        cpu_stats.addStretch()
        
        cpu_content.addLayout(cpu_graph_section, 3)
        cpu_content.addLayout(cpu_stats, 1)
        cpu_container.addLayout(cpu_content)
        cpu_gpu_layout.addLayout(cpu_container)
        
        # GPU Section
        gpu_container = QVBoxLayout()
        gpu_container.setSpacing(10)
        
        # GPU Header
        gpu_header = QHBoxLayout()
        gpu_title = QLabel("GPU")
        gpu_title.setStyleSheet("color: #00B0C8; font-size: 16px; font-weight: bold;")
        self.gpu_labels['name'] = QLabel("GeForce GTX 1660 Ti")
        self.gpu_labels['name'].setStyleSheet("color: #9aa0a6; font-size: 12px;")
        
        gpu_header.addWidget(gpu_title)
        gpu_header.addWidget(self.gpu_labels['name'])
        gpu_header.addStretch()
        gpu_container.addLayout(gpu_header)
        
        # GPU Content
        gpu_content = QHBoxLayout()
        gpu_content.setSpacing(20)
        
        # GPU Graph Section
        gpu_graph_section = QVBoxLayout()
        gpu_graph_section.setSpacing(5)
        
        temp_label = QLabel("Temperature (°C) / Loading (%)")
        temp_label.setStyleSheet("color: #9aa0a6; font-size: 11px;")
        gpu_graph_section.addWidget(temp_label)
        
        # Min/Max for GPU
        gpu_minmax = QHBoxLayout()
        self.gpu_labels['min_temp'] = QLabel("Min: 62°")
        self.gpu_labels['max_temp'] = QLabel("Max: 74°")
        self.gpu_labels['min_temp'].setStyleSheet("color: #9aa0a6; font-size: 10px;")
        self.gpu_labels['max_temp'].setStyleSheet("color: #9aa0a6; font-size: 10px;")
        gpu_minmax.addWidget(self.gpu_labels['min_temp'])
        gpu_minmax.addStretch()
        gpu_minmax.addWidget(self.gpu_labels['max_temp'])
        gpu_graph_section.addLayout(gpu_minmax)
        
        # GPU Graph with temperature display
        gpu_graph_container = QHBoxLayout()
        self.gpu_graph = TemperatureGraph()
        self.gpu_graph.setMinimumHeight(120)
        
        # Temperature and percentage display
        gpu_display = QVBoxLayout()
        gpu_display.setAlignment(Qt.AlignCenter)
        self.gpu_labels['temp_display'] = QLabel("74°")
        self.gpu_labels['temp_display'].setStyleSheet("color: #00B0C8; font-size: 32px; font-weight: bold;")
        self.gpu_labels['usage_display'] = QLabel("26 %")
        self.gpu_labels['usage_display'].setStyleSheet("color: #00B0C8; font-size: 16px;")
        gpu_display.addWidget(self.gpu_labels['temp_display'])
        gpu_display.addWidget(self.gpu_labels['usage_display'])
        
        gpu_graph_container.addWidget(self.gpu_graph, 3)
        gpu_graph_container.addLayout(gpu_display, 1)
        gpu_graph_section.addLayout(gpu_graph_container)
        
        # GPU Stats Section
        gpu_stats = QVBoxLayout()
        gpu_stats.setSpacing(15)
        gpu_stats.setAlignment(Qt.AlignTop)
        
        self.gpu_labels['fan_speed'] = self._create_stat_item("Fan speed", "3960 RPM")
        self.gpu_labels['core_clock'] = self._create_stat_item("Core Clock", "1710 MHz")
        
        gpu_stats.addLayout(self.gpu_labels['fan_speed']['layout'])
        gpu_stats.addLayout(self.gpu_labels['core_clock']['layout'])
        gpu_stats.addStretch()
        
        gpu_content.addLayout(gpu_graph_section, 3)
        gpu_content.addLayout(gpu_stats, 1)
        gpu_container.addLayout(gpu_content)
        cpu_gpu_layout.addLayout(gpu_container)
        
        # System Tab
        system_tab = QWidget()
        system_layout = QVBoxLayout(system_tab)
        system_layout.setSpacing(20)
        
        # System Header
        system_header = QHBoxLayout()
        system_title = QLabel("System")
        system_title.setStyleSheet("color: #00B0C8; font-size: 16px; font-weight: bold;")
        temp_subtitle = QLabel("Temperature (°C)")
        temp_subtitle.setStyleSheet("color: #9aa0a6; font-size: 12px;")
        system_header.addWidget(system_title)
        system_header.addWidget(temp_subtitle)
        system_header.addStretch()
        system_layout.addLayout(system_header)
        
        # System temperature section
        system_temp_section = QHBoxLayout()
        system_temp_section.setSpacing(20)
        
        # System graph section
        system_graph_section = QVBoxLayout()
        
        # Min/Max for system
        system_minmax = QHBoxLayout()
        self.system_labels['min_temp'] = QLabel("Min: 53°")
        self.system_labels['max_temp'] = QLabel("Max: 65°")
        self.system_labels['min_temp'].setStyleSheet("color: #9aa0a6; font-size: 10px;")
        self.system_labels['max_temp'].setStyleSheet("color: #9aa0a6; font-size: 10px;")
        system_minmax.addWidget(self.system_labels['min_temp'])
        system_minmax.addStretch()
        system_minmax.addWidget(self.system_labels['max_temp'])
        system_graph_section.addLayout(system_minmax)
        
        # System graph with temperature display
        system_graph_container = QHBoxLayout()
        self.system_graph = TemperatureGraph()
        self.system_graph.setMinimumHeight(120)
        
        # System temperature display
        system_display = QVBoxLayout()
        system_display.setAlignment(Qt.AlignCenter)
        self.system_labels['temp_display'] = QLabel("65°")
        self.system_labels['temp_display'].setStyleSheet("color: #00B0C8; font-size: 48px; font-weight: bold;")
        system_display.addWidget(self.system_labels['temp_display'])
        
        system_graph_container.addWidget(self.system_graph, 3)
        system_graph_container.addLayout(system_display, 1)
        system_graph_section.addLayout(system_graph_container)
        
        system_temp_section.addLayout(system_graph_section)
        system_layout.addLayout(system_temp_section)
        
        # System metrics row
        system_metrics = QHBoxLayout()
        system_metrics.setSpacing(40)
        
        # RAM section
        ram_section = self._create_system_metric_section("RAM", "Frequency", "2667 MHz", "Usage", "4.8 GB (30.6%)")
        self.system_labels['ram_frequency'] = ram_section['value1']
        self.system_labels['ram_usage'] = ram_section['value2']
        
        # Ethernet section
        eth_section = self._create_system_metric_section("Ethernet", "Download", "0.0 Kbps", "Upload", "0.1 Kbps")
        self.system_labels['eth_download'] = eth_section['value1']
        self.system_labels['eth_upload'] = eth_section['value2']
        
        # Wi-Fi section
        wifi_section = self._create_system_metric_section("Wi-Fi", "Download", "20.9 Kbps", "Upload", "2.7 Kbps")
        self.system_labels['wifi_download'] = wifi_section['value1']
        self.system_labels['wifi_upload'] = wifi_section['value2']
        
        system_metrics.addLayout(ram_section['layout'])
        system_metrics.addLayout(eth_section['layout'])
        system_metrics.addLayout(wifi_section['layout'])
        system_metrics.addStretch()
        
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

    def _create_stat_item(self, label_text, initial_value):
        """Create a stat item layout with label and value."""
        layout = QVBoxLayout()
        layout.setSpacing(2)
        
        label = QLabel(label_text)
        label.setStyleSheet("color: #9aa0a6; font-size: 11px;")
        
        value = QLabel(initial_value)
        value.setStyleSheet("color: #00B0C8; font-size: 12px; font-weight: bold;")
        
        layout.addWidget(label)
        layout.addWidget(value)
        
        return {'layout': layout, 'value': value}
    
    def _create_system_metric_section(self, title, label1, value1, label2, value2):
        """Create a system metric section with title and two value pairs."""
        section = QVBoxLayout()
        section.setSpacing(8)
        section.setAlignment(Qt.AlignTop)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #9aa0a6; font-size: 14px; font-weight: bold;")
        section.addWidget(title_label)
        
        # First metric
        metric1_layout = QVBoxLayout()
        metric1_layout.setSpacing(2)
        label1_widget = QLabel(label1)
        label1_widget.setStyleSheet("color: #9aa0a6; font-size: 10px;")
        value1_widget = QLabel(value1)
        value1_widget.setStyleSheet("color: #00B0C8; font-size: 12px; font-weight: bold;")
        metric1_layout.addWidget(label1_widget)
        metric1_layout.addWidget(value1_widget)
        section.addLayout(metric1_layout)
        
        # Second metric
        metric2_layout = QVBoxLayout()
        metric2_layout.setSpacing(2)
        label2_widget = QLabel(label2)
        label2_widget.setStyleSheet("color: #9aa0a6; font-size: 10px;")
        value2_widget = QLabel(value2)
        value2_widget.setStyleSheet("color: #00B0C8; font-size: 12px; font-weight: bold;")
        metric2_layout.addWidget(label2_widget)
        metric2_layout.addWidget(value2_widget)
        section.addLayout(metric2_layout)
        
        return {
            'layout': section,
            'value1': value1_widget,
            'value2': value2_widget
        }
    
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
        
        # Update temperature and usage displays
        self.cpu_labels['temp_display'].setText(f"{cpu_metrics.temperature}°")
        self.cpu_labels['usage_display'].setText(f"{cpu_metrics.usage:.0f} %")
        
        # Update stats
        if cpu_metrics.fan_speed > 0:
            self.cpu_labels['fan_speed']['value'].setText(f"{cpu_metrics.fan_speed} RPM")
        else:
            self.cpu_labels['fan_speed']['value'].setText("-- RPM")
            
        if cpu_metrics.frequency > 0:
            self.cpu_labels['frequency']['value'].setText(f"{cpu_metrics.frequency} MHz")
        else:
            self.cpu_labels['frequency']['value'].setText("-- MHz")
            
        if cpu_metrics.voltage > 0:
            self.cpu_labels['voltage']['value'].setText(f"{cpu_metrics.voltage:.3f} V")
        else:
            self.cpu_labels['voltage']['value'].setText("-- V")
            
        self.cpu_labels['min_temp'].setText(f"Min: {cpu_metrics.min_temp}°")
        self.cpu_labels['max_temp'].setText(f"Max: {cpu_metrics.max_temp}°")
        
        # Update CPU graph
        if self.cpu_graph:
            self.cpu_graph.add_data_point(cpu_metrics.temperature, cpu_metrics.usage)
    
    def _update_gpu_metrics(self, gpu_metrics: GPUMetrics):
        """Update GPU metrics display."""
        self.gpu_labels['name'].setText(gpu_metrics.name)
        
        # Update temperature and usage displays
        self.gpu_labels['temp_display'].setText(f"{gpu_metrics.temperature}°")
        self.gpu_labels['usage_display'].setText(f"{gpu_metrics.usage:.0f} %")
        
        # Update stats
        # Always show fan speed, even if 0 (modern GPUs can have 0 RPM when idle)
        self.gpu_labels['fan_speed']['value'].setText(f"{gpu_metrics.fan_speed} RPM")
            
        if gpu_metrics.core_clock > 0:
            self.gpu_labels['core_clock']['value'].setText(f"{gpu_metrics.core_clock} MHz")
        else:
            self.gpu_labels['core_clock']['value'].setText("-- MHz")
            
        self.gpu_labels['min_temp'].setText(f"Min: {gpu_metrics.min_temp}°")
        self.gpu_labels['max_temp'].setText(f"Max: {gpu_metrics.max_temp}°")
        
        # Update GPU graph
        if self.gpu_graph:
            self.gpu_graph.add_data_point(gpu_metrics.temperature, gpu_metrics.usage)
    
    def _update_system_metrics(self, system_metrics: SystemMetrics):
        """Update system metrics display."""
        # Update temperature display
        self.system_labels['temp_display'].setText(f"{system_metrics.temperature}°")
        
        self.system_labels['min_temp'].setText(f"Min: {system_metrics.min_temp}°")
        self.system_labels['max_temp'].setText(f"Max: {system_metrics.max_temp}°")
        
        # Update RAM metrics
        if system_metrics.ram_frequency > 0:
            self.system_labels['ram_frequency'].setText(f"{system_metrics.ram_frequency} MHz")
        else:
            self.system_labels['ram_frequency'].setText("-- MHz")
            
        if system_metrics.ram_total_gb > 0:
            self.system_labels['ram_usage'].setText(
                f"{system_metrics.ram_usage_gb} GB ({system_metrics.ram_usage_percent:.1f}%)"
            )
        else:
            self.system_labels['ram_usage'].setText("-- GB (--%)")
            
        # Update network metrics
        self.system_labels['eth_download'].setText(f"{system_metrics.ethernet_download:.1f} Kbps")
        self.system_labels['eth_upload'].setText(f"{system_metrics.ethernet_upload:.1f} Kbps")
        
        self.system_labels['wifi_download'].setText(f"{system_metrics.wifi_download:.1f} Kbps")
        self.system_labels['wifi_upload'].setText(f"{system_metrics.wifi_upload:.1f} Kbps")
        
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
