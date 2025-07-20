"""
系统资源监控模块
监控CPU、内存、磁盘使用情况和性能指标
"""
import psutil
import time
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class SystemMetrics:
    """系统指标"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_available: int
    disk_percent: float
    disk_free: int
    process_count: int
    network_io: Dict[str, int]

@dataclass
class PerformanceAlert:
    """性能警报"""
    metric: str
    value: float
    threshold: float
    severity: str  # 'warning', 'critical'
    timestamp: float
    message: str

class SystemMonitor:
    """系统资源监控器"""
    
    def __init__(self, check_interval: float = 5.0):
        """
        初始化监控器
        
        Args:
            check_interval: 检查间隔（秒）
        """
        self.check_interval = check_interval
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # 性能阈值
        self.thresholds = {
            'cpu_warning': 80.0,
            'cpu_critical': 95.0,
            'memory_warning': 80.0,
            'memory_critical': 95.0,
            'disk_warning': 85.0,
            'disk_critical': 95.0
        }
        
        # 历史数据
        self.metrics_history: List[SystemMetrics] = []
        self.max_history_size = 1000
        self.alerts: List[PerformanceAlert] = []
        self.max_alerts = 100
        
        # 性能优化状态
        self.optimization_enabled = True
        self.last_optimization = 0
        self.optimization_interval = 300  # 5分钟
        
        self._lock = threading.Lock()
    
    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
    
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                # 收集系统指标
                metrics = self._collect_metrics()
                
                # 存储历史数据
                with self._lock:
                    self.metrics_history.append(metrics)
                    if len(self.metrics_history) > self.max_history_size:
                        self.metrics_history.pop(0)
                
                # 检查性能警报
                self._check_alerts(metrics)
                
                # 执行性能优化
                if self.optimization_enabled:
                    self._perform_optimization(metrics)
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"监控循环错误: {e}")
                time.sleep(self.check_interval)
    
    def _collect_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存信息
            memory = psutil.virtual_memory()
            
            # 磁盘信息
            disk = psutil.disk_usage('/')
            
            # 进程数量
            process_count = len(psutil.pids())
            
            # 网络IO
            net_io = psutil.net_io_counters()
            network_io = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
            
            return SystemMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available=memory.available,
                disk_percent=disk.percent,
                disk_free=disk.free,
                process_count=process_count,
                network_io=network_io
            )
            
        except Exception as e:
            print(f"收集系统指标失败: {e}")
            return SystemMetrics(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available=0,
                disk_percent=0.0,
                disk_free=0,
                process_count=0,
                network_io={}
            )
    
    def _check_alerts(self, metrics: SystemMetrics):
        """检查性能警报"""
        current_time = time.time()
        
        # 检查CPU使用率
        if metrics.cpu_percent >= self.thresholds['cpu_critical']:
            self._add_alert('cpu', metrics.cpu_percent, self.thresholds['cpu_critical'], 
                          'critical', current_time, f"CPU使用率达到临界值: {metrics.cpu_percent:.1f}%")
        elif metrics.cpu_percent >= self.thresholds['cpu_warning']:
            self._add_alert('cpu', metrics.cpu_percent, self.thresholds['cpu_warning'], 
                          'warning', current_time, f"CPU使用率过高: {metrics.cpu_percent:.1f}%")
        
        # 检查内存使用率
        if metrics.memory_percent >= self.thresholds['memory_critical']:
            self._add_alert('memory', metrics.memory_percent, self.thresholds['memory_critical'], 
                          'critical', current_time, f"内存使用率达到临界值: {metrics.memory_percent:.1f}%")
        elif metrics.memory_percent >= self.thresholds['memory_warning']:
            self._add_alert('memory', metrics.memory_percent, self.thresholds['memory_warning'], 
                          'warning', current_time, f"内存使用率过高: {metrics.memory_percent:.1f}%")
        
        # 检查磁盘使用率
        if metrics.disk_percent >= self.thresholds['disk_critical']:
            self._add_alert('disk', metrics.disk_percent, self.thresholds['disk_critical'], 
                          'critical', current_time, f"磁盘使用率达到临界值: {metrics.disk_percent:.1f}%")
        elif metrics.disk_percent >= self.thresholds['disk_warning']:
            self._add_alert('disk', metrics.disk_percent, self.thresholds['disk_warning'], 
                          'warning', current_time, f"磁盘使用率过高: {metrics.disk_percent:.1f}%")
    
    def _add_alert(self, metric: str, value: float, threshold: float, 
                   severity: str, timestamp: float, message: str):
        """添加警报"""
        alert = PerformanceAlert(
            metric=metric,
            value=value,
            threshold=threshold,
            severity=severity,
            timestamp=timestamp,
            message=message
        )
        
        with self._lock:
            self.alerts.append(alert)
            if len(self.alerts) > self.max_alerts:
                self.alerts.pop(0)
    
    def _perform_optimization(self, metrics: SystemMetrics):
        """执行性能优化"""
        current_time = time.time()
        
        # 检查是否需要优化
        if current_time - self.last_optimization < self.optimization_interval:
            return
        
        self.last_optimization = current_time
        
        try:
            # 内存优化
            if metrics.memory_percent > 85:
                self._optimize_memory()
            
            # CPU优化
            if metrics.cpu_percent > 90:
                self._optimize_cpu()
            
        except Exception as e:
            print(f"性能优化失败: {e}")
    
    def _optimize_memory(self):
        """内存优化"""
        try:
            import gc
            # 强制垃圾回收
            gc.collect()
            print("执行内存优化: 垃圾回收")
        except Exception as e:
            print(f"内存优化失败: {e}")
    
    def _optimize_cpu(self):
        """CPU优化"""
        try:
            # 降低当前进程优先级
            current_process = psutil.Process()
            if hasattr(psutil, 'BELOW_NORMAL_PRIORITY_CLASS'):
                current_process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            print("执行CPU优化: 降低进程优先级")
        except Exception as e:
            print(f"CPU优化失败: {e}")
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """获取当前系统指标"""
        with self._lock:
            if self.metrics_history:
                return self.metrics_history[-1]
        return None
    
    def get_metrics_history(self, duration_minutes: int = 60) -> List[SystemMetrics]:
        """获取指定时间范围内的历史指标"""
        cutoff_time = time.time() - (duration_minutes * 60)
        
        with self._lock:
            return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
    
    def get_alerts(self, severity: Optional[str] = None) -> List[PerformanceAlert]:
        """获取警报列表"""
        with self._lock:
            if severity:
                return [a for a in self.alerts if a.severity == severity]
            return self.alerts.copy()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        current = self.get_current_metrics()
        if not current:
            return {}
        
        recent_history = self.get_metrics_history(10)  # 最近10分钟
        
        # 计算平均值
        if recent_history:
            avg_cpu = sum(m.cpu_percent for m in recent_history) / len(recent_history)
            avg_memory = sum(m.memory_percent for m in recent_history) / len(recent_history)
        else:
            avg_cpu = current.cpu_percent
            avg_memory = current.memory_percent
        
        # 计算警报数量
        warning_count = len([a for a in self.alerts if a.severity == 'warning'])
        critical_count = len([a for a in self.alerts if a.severity == 'critical'])
        
        return {
            'current_cpu': current.cpu_percent,
            'current_memory': current.memory_percent,
            'current_disk': current.disk_percent,
            'avg_cpu_10min': avg_cpu,
            'avg_memory_10min': avg_memory,
            'warning_alerts': warning_count,
            'critical_alerts': critical_count,
            'process_count': current.process_count,
            'memory_available_gb': current.memory_available / (1024**3),
            'disk_free_gb': current.disk_free / (1024**3)
        }
    
    def set_thresholds(self, **thresholds):
        """设置性能阈值"""
        for key, value in thresholds.items():
            if key in self.thresholds:
                self.thresholds[key] = value
    
    def clear_alerts(self):
        """清空警报"""
        with self._lock:
            self.alerts.clear()
    
    def cleanup(self):
        """清理资源"""
        self.stop_monitoring()
        with self._lock:
            self.metrics_history.clear()
            self.alerts.clear()

# 全局实例
_global_monitor = None

def get_system_monitor() -> SystemMonitor:
    """获取全局系统监控器实例"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = SystemMonitor()
    return _global_monitor 