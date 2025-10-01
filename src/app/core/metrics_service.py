import json
import random
import subprocess
import time
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass

from PyQt5.QtCore import QObject, QTimer, pyqtSignal


@dataclass
class CPUMetrics:
    name: str = "Unknown CPU"
    fan_speed: int = 0  # RPM
    frequency: int = 0  # MHz
    voltage: float = 0.0  # V
    temperature: int = 0  # °C
    usage: float = 0.0  # %
    min_temp: int = 0
    max_temp: int = 0


@dataclass
class GPUMetrics:
    name: str = "Unknown GPU"
    fan_speed: int = 0  # RPM
    core_clock: int = 0  # MHz
    temperature: int = 0  # °C
    usage: float = 0.0  # %
    min_temp: int = 0
    max_temp: int = 0


@dataclass
class SystemMetrics:
    temperature: int = 0  # °C
    min_temp: int = 0
    max_temp: int = 0
    ram_frequency: int = 0  # MHz
    ram_usage_gb: float = 0.0  # GB
    ram_usage_percent: float = 0.0  # %
    ram_total_gb: float = 0.0  # GB
    ethernet_download: float = 0.0  # Kbps
    ethernet_upload: float = 0.0  # Kbps
    wifi_download: float = 0.0  # Kbps
    wifi_upload: float = 0.0  # Kbps


class MetricsService(QObject):
    """Comprehensive system metrics provider."""

    metricsUpdated = pyqtSignal(int, int, int)  # cpu, gpu, system (in °C)
    cpuMetricsUpdated = pyqtSignal(object)  # CPUMetrics
    gpuMetricsUpdated = pyqtSignal(object)  # GPUMetrics
    systemMetricsUpdated = pyqtSignal(object)  # SystemMetrics

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._timer.setInterval(1000)  # 1s
        
        # Initialize metrics objects
        self._cpu_metrics = CPUMetrics()
        self._gpu_metrics = GPUMetrics()
        self._system_metrics = SystemMetrics()
        
        # Temperature tracking for min/max
        self._temp_history = {
            'cpu': [],
            'gpu': [],
            'system': []
        }
        
        # Network tracking for speed calculation
        self._last_network_stats = {}
        self._last_network_time = time.time()
        
        # Initialize psutil if available
        self._psutil_available = False
        try:
            import psutil
            self._psutil_available = True
        except ImportError:
            pass

    def start(self):
        if not self._timer.isActive():
            self._timer.start()

    def stop(self):
        if self._timer.isActive():
            self._timer.stop()

    # --- Providers ---
    def _read_psutil(self) -> Optional[Tuple[int, int, int]]:
        try:
            import psutil  # type: ignore
        except Exception:
            return None
        try:
            temps = psutil.sensors_temperatures(fahrenheit=False)
            if not temps:
                return None

            cpu = None
            # Prefer coretemp package value
            for key, entries in temps.items():
                if key.lower().startswith("coretemp"):
                    # pick 'Package id 0' if exists, else max of entries
                    pkg = None
                    max_core = None
                    for e in entries:
                        label = (e.label or "").lower()
                        if "package id" in label:
                            pkg = int(e.current)
                        if "core" in label:
                            v = int(e.current)
                            max_core = v if max_core is None else max(max_core, v)
                    cpu = pkg if pkg is not None else (max_core if max_core is not None else None)
                    break

            # GPU (best-effort from psutil)
            gpu = None
            for key, entries in temps.items():
                lk = key.lower()
                if "amdgpu" in lk or "nvidia" in lk:
                    for e in entries:
                        if e.current is not None:
                            gpu = int(e.current)
                            break
                if gpu is not None:
                    break

            # System: try pch or acpitz or any other meaningful source
            system = None
            for pref in ("pch", "acpitz", "iwlwifi", "acer", "nvme"):
                for key, entries in temps.items():
                    if pref in key.lower():
                        for e in entries:
                            if e.current is not None:
                                system = int(e.current)
                                break
                    if system is not None:
                        break
                if system is not None:
                    break

            # fill fallbacks from what's available
            if cpu is None:
                # Scan any source
                for entries in temps.values():
                    for e in entries:
                        if e.current is not None:
                            cpu = int(e.current)
                            break
                    if cpu is not None:
                        break

            if gpu is None and cpu is not None:
                gpu = max(0, cpu - 5)
            if system is None and cpu is not None:
                system = max(0, cpu - 10)

            if cpu is None or gpu is None or system is None:
                return None
            return int(cpu), int(gpu), int(system)
        except Exception:
            return None

    def _read_sensors_json(self) -> Optional[Tuple[int, int, int]]:
        try:
            out = subprocess.check_output(["sensors", "-j"], text=True, timeout=1.5)
            data = json.loads(out)
        except Exception:
            return None

        def pick_temp(obj, keys):
            # walk dict to find any temp*_input under known device keys
            for k in list(obj.keys()):
                low = k.lower()
                if any(p in low for p in keys):
                    # search nested for xxx_input values
                    stack = [obj[k]]
                    while stack:
                        cur = stack.pop()
                        if isinstance(cur, dict):
                            for kk, vv in cur.items():
                                if isinstance(vv, (dict, list)):
                                    stack.append(vv)
                                else:
                                    if isinstance(kk, str) and kk.endswith("_input") and isinstance(vv, (int, float)):
                                        return int(round(vv))
                        elif isinstance(cur, list):
                            stack.extend(cur)
            return None

        # Prefer explicit acer-isa-0ace mapping if present
        cpu = gpu = system = None
        try:
            for dev_name, dev_val in data.items():
                if dev_name.lower().startswith("acer-isa-0ace") and isinstance(dev_val, dict):
                    # find temp1_input/temp2_input/temp3_input
                    def find_input(dct, key):
                        v = dct.get(key)
                        if isinstance(v, (int, float)):
                            return int(round(v))
                        return None
                    # Some versions nest under another level; flatten one level
                    flat = {}
                    stack = [dev_val]
                    while stack:
                        cur = stack.pop()
                        if isinstance(cur, dict):
                            flat.update(cur)
                            for vv in cur.values():
                                if isinstance(vv, dict):
                                    stack.append(vv)
                    c = find_input(flat, "temp1_input")
                    g = find_input(flat, "temp2_input")
                    s = find_input(flat, "temp3_input")
                    if c is not None:
                        cpu = c
                    if g is not None:
                        gpu = g
                    if s is not None:
                        system = s
                    break
        except Exception:
            pass

        # If anything is missing, fall back to generic picks
        if cpu is None:
            cpu = pick_temp(data, ["coretemp", "package id", "cpu"]) or pick_temp(data, ["acer"]) 
        if gpu is None:
            gpu = pick_temp(data, ["amdgpu", "nvidia"]) or (cpu - 5 if cpu is not None else None)
        if system is None:
            system = pick_temp(data, ["pch", "acpitz", "acer"]) or (cpu - 10 if cpu is not None else None)

        if cpu is None or gpu is None or system is None:
            return None
        return int(cpu), int(gpu), int(system)

    def _get_cpu_info(self) -> CPUMetrics:
        """Get comprehensive CPU information."""
        cpu_metrics = CPUMetrics()
        
        if self._psutil_available:
            import psutil
            
            # CPU name
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('model name'):
                            cpu_metrics.name = line.split(':', 1)[1].strip()
                            break
            except:
                cpu_metrics.name = "Unknown CPU"
            
            # CPU frequency
            try:
                freq = psutil.cpu_freq()
                if freq:
                    cpu_metrics.frequency = int(freq.current)
            except:
                pass
            
            # CPU usage
            try:
                cpu_metrics.usage = psutil.cpu_percent(interval=0.1)
            except:
                pass
        
        # CPU fan speed and voltage from sensors
        try:
            result = subprocess.run(['sensors', '-j'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # Look for fan speeds
                for device, sensors in data.items():
                    if isinstance(sensors, dict):
                        for sensor_name, sensor_data in sensors.items():
                            if 'fan' in sensor_name.lower() and isinstance(sensor_data, dict):
                                for key, value in sensor_data.items():
                                    if key.endswith('_input') and isinstance(value, (int, float)):
                                        cpu_metrics.fan_speed = int(value)
                                        break
                            elif 'in' in sensor_name.lower() and isinstance(sensor_data, dict):
                                for key, value in sensor_data.items():
                                    if key.endswith('_input') and isinstance(value, (int, float)):
                                        cpu_metrics.voltage = round(value, 3)
                                        break
        except:
            pass
        
        return cpu_metrics
    
    def _get_gpu_info(self) -> GPUMetrics:
        """Get comprehensive GPU information."""
        gpu_metrics = GPUMetrics()
        
        # Try nvidia-smi first
        try:
            result = subprocess.run([
                'nvidia-smi', '--query-gpu=name,fan.speed,clocks.gr,temperature.gpu,utilization.gpu',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                parts = result.stdout.strip().split(', ')
                if len(parts) >= 5:
                    gpu_metrics.name = parts[0]
                    try:
                        gpu_metrics.fan_speed = int(parts[1]) if parts[1] != '[N/A]' else 0
                    except:
                        pass
                    try:
                        gpu_metrics.core_clock = int(parts[2]) if parts[2] != '[N/A]' else 0
                    except:
                        pass
                    try:
                        gpu_metrics.temperature = int(parts[3]) if parts[3] != '[N/A]' else 0
                    except:
                        pass
                    try:
                        gpu_metrics.usage = float(parts[4]) if parts[4] != '[N/A]' else 0.0
                    except:
                        pass
                return gpu_metrics
        except:
            pass
        
        # Try AMD tools
        try:
            result = subprocess.run(['rocm-smi', '--showtemp', '--showclocks'], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'GPU' in line and 'Temperature' in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part.endswith('C'):
                                try:
                                    gpu_metrics.temperature = int(part[:-1])
                                except:
                                    pass
        except:
            pass
        
        # Fallback: try to get GPU name from lspci
        if gpu_metrics.name == "Unknown GPU":
            try:
                result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'VGA' in line or 'Display' in line:
                            if 'NVIDIA' in line or 'GeForce' in line:
                                gpu_metrics.name = line.split(': ', 1)[-1]
                                break
                            elif 'AMD' in line or 'Radeon' in line:
                                gpu_metrics.name = line.split(': ', 1)[-1]
                                break
            except:
                pass
        
        return gpu_metrics
    
    def _get_system_info(self) -> SystemMetrics:
        """Get comprehensive system information."""
        system_metrics = SystemMetrics()
        
        if self._psutil_available:
            import psutil
            
            # RAM information
            try:
                mem = psutil.virtual_memory()
                system_metrics.ram_total_gb = round(mem.total / (1024**3), 1)
                system_metrics.ram_usage_gb = round(mem.used / (1024**3), 1)
                system_metrics.ram_usage_percent = round(mem.percent, 1)
            except:
                pass
            
            # Network information
            try:
                net_io = psutil.net_io_counters(pernic=True)
                current_time = time.time()
                time_diff = current_time - self._last_network_time
                
                if time_diff > 0 and self._last_network_stats:
                    # Calculate speeds
                    for interface, stats in net_io.items():
                        if interface in self._last_network_stats:
                            old_stats = self._last_network_stats[interface]
                            
                            # Calculate Kbps
                            download_kbps = ((stats.bytes_recv - old_stats.bytes_recv) * 8) / (time_diff * 1000)
                            upload_kbps = ((stats.bytes_sent - old_stats.bytes_sent) * 8) / (time_diff * 1000)
                            
                            # Classify interface type
                            if 'eth' in interface.lower() or 'enp' in interface.lower():
                                system_metrics.ethernet_download = max(0, round(download_kbps, 1))
                                system_metrics.ethernet_upload = max(0, round(upload_kbps, 1))
                            elif 'wl' in interface.lower() or 'wlan' in interface.lower():
                                system_metrics.wifi_download = max(0, round(download_kbps, 1))
                                system_metrics.wifi_upload = max(0, round(upload_kbps, 1))
                
                # Store current stats for next calculation
                self._last_network_stats = net_io.copy()
                self._last_network_time = current_time
            except:
                pass
        
        # RAM frequency from multiple sources
        try:
            # Try dmidecode first
            result = subprocess.run(['dmidecode', '-t', 'memory'], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Speed:' in line and 'MHz' in line and 'Unknown' not in line:
                        try:
                            speed_str = line.split('Speed:')[1].strip()
                            speed = int(speed_str.split()[0])
                            if speed > system_metrics.ram_frequency and speed < 10000:  # Reasonable range
                                system_metrics.ram_frequency = speed
                        except:
                            pass
        except:
            pass
        
        # Fallback: try /proc/meminfo or lshw
        if system_metrics.ram_frequency == 0:
            try:
                result = subprocess.run(['lshw', '-short', '-C', 'memory'], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'MHz' in line and 'DIMM' in line:
                            try:
                                parts = line.split()
                                for part in parts:
                                    if 'MHz' in part:
                                        speed = int(part.replace('MHz', ''))
                                        if speed > system_metrics.ram_frequency and speed < 10000:
                                            system_metrics.ram_frequency = speed
                            except:
                                pass
            except:
                pass
        
        return system_metrics
    
    def _update_temperature_history(self, cpu_temp: int, gpu_temp: int, sys_temp: int):
        """Update temperature history for min/max tracking."""
        # Keep last 60 readings (1 minute of history)
        max_history = 60
        
        self._temp_history['cpu'].append(cpu_temp)
        self._temp_history['gpu'].append(gpu_temp)
        self._temp_history['system'].append(sys_temp)
        
        # Trim history
        for key in self._temp_history:
            if len(self._temp_history[key]) > max_history:
                self._temp_history[key] = self._temp_history[key][-max_history:]
        
        # Update min/max in metrics
        if self._temp_history['cpu']:
            self._cpu_metrics.min_temp = min(self._temp_history['cpu'])
            self._cpu_metrics.max_temp = max(self._temp_history['cpu'])
        
        if self._temp_history['gpu']:
            self._gpu_metrics.min_temp = min(self._temp_history['gpu'])
            self._gpu_metrics.max_temp = max(self._temp_history['gpu'])
        
        if self._temp_history['system']:
            self._system_metrics.min_temp = min(self._temp_history['system'])
            self._system_metrics.max_temp = max(self._temp_history['system'])

    # --- Tick ---
    def _update(self):
        # Get temperature data (existing logic)
        vals = self._read_sensors_json()
        if vals is None:
            vals = self._read_psutil()

        if vals is None:
            # fallback: small random walk
            cpu_temp = max(30, min(95, self._cpu_metrics.temperature + random.randint(-2, 3)))
            gpu_temp = max(30, min(95, self._gpu_metrics.temperature + random.randint(-2, 2)))
            sys_temp = max(25, min(85, self._system_metrics.temperature + random.randint(-1, 2)))
        else:
            cpu_temp, gpu_temp, sys_temp = vals

        # Update comprehensive metrics
        self._cpu_metrics = self._get_cpu_info()
        self._cpu_metrics.temperature = cpu_temp
        
        self._gpu_metrics = self._get_gpu_info()
        self._gpu_metrics.temperature = gpu_temp
        
        self._system_metrics = self._get_system_info()
        self._system_metrics.temperature = sys_temp
        
        # Update temperature history
        self._update_temperature_history(cpu_temp, gpu_temp, sys_temp)
        
        # Emit signals
        self.metricsUpdated.emit(cpu_temp, gpu_temp, sys_temp)
        self.cpuMetricsUpdated.emit(self._cpu_metrics)
        self.gpuMetricsUpdated.emit(self._gpu_metrics)
        self.systemMetricsUpdated.emit(self._system_metrics)
    
    # Public getters
    def get_cpu_metrics(self) -> CPUMetrics:
        return self._cpu_metrics
    
    def get_gpu_metrics(self) -> GPUMetrics:
        return self._gpu_metrics
    
    def get_system_metrics(self) -> SystemMetrics:
        return self._system_metrics
