import time
import psutil
import threading
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
from .logger import GameLogger

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_io_read: float
    disk_io_write: float
    network_io_sent: float
    network_io_recv: float

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, logger: GameLogger, interval: float = 1.0):
        """
        初始化性能监控器
        
        Args:
            logger: 日志对象
            interval: 监控间隔（秒）
        """
        self.logger = logger
        self.interval = interval
        self.metrics: List[PerformanceMetrics] = []
        self.is_monitoring = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        
        # 初始化基准值
        self._init_baseline()
        
    def _init_baseline(self):
        """初始化性能基准值"""
        self.baseline = {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_io': psutil.disk_io_counters(),
            'network_io': psutil.net_io_counters()
        }
        
    def start(self):
        """开始监控"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        self.logger.info("性能监控已启动")
        
    def stop(self):
        """停止监控"""
        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("性能监控已停止")
        
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                # 收集性能数据
                metrics = self._collect_metrics()
                
                # 存储数据
                with self.lock:
                    self.metrics.append(metrics)
                    
                # 检查性能异常
                self._check_performance(metrics)
                
                # 等待下一次收集
                time.sleep(self.interval)
            except Exception as e:
                self.logger.error(f"性能监控出错: {str(e)}")
                
    def _collect_metrics(self) -> PerformanceMetrics:
        """收集性能指标"""
        return PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=psutil.cpu_percent(),
            memory_percent=psutil.virtual_memory().percent,
            disk_io_read=psutil.disk_io_counters().read_bytes - self.baseline['disk_io'].read_bytes,
            disk_io_write=psutil.disk_io_counters().write_bytes - self.baseline['disk_io'].write_bytes,
            network_io_sent=psutil.net_io_counters().bytes_sent - self.baseline['network_io'].bytes_sent,
            network_io_recv=psutil.net_io_counters().bytes_recv - self.baseline['network_io'].bytes_recv
        )
        
    def _check_performance(self, metrics: PerformanceMetrics):
        """检查性能是否异常"""
        # CPU使用率检查
        if metrics.cpu_percent > 90:
            self.logger.warning(f"CPU使用率过高: {metrics.cpu_percent}%")
            
        # 内存使用率检查
        if metrics.memory_percent > 90:
            self.logger.warning(f"内存使用率过高: {metrics.memory_percent}%")
            
        # 磁盘IO检查
        if metrics.disk_io_read > 100 * 1024 * 1024:  # 100MB
            self.logger.warning(f"磁盘读取量过大: {metrics.disk_io_read / (1024*1024):.2f}MB")
        if metrics.disk_io_write > 100 * 1024 * 1024:  # 100MB
            self.logger.warning(f"磁盘写入量过大: {metrics.disk_io_write / (1024*1024):.2f}MB")
            
        # 网络IO检查
        if metrics.network_io_sent > 10 * 1024 * 1024:  # 10MB
            self.logger.warning(f"网络发送量过大: {metrics.network_io_sent / (1024*1024):.2f}MB")
        if metrics.network_io_recv > 10 * 1024 * 1024:  # 10MB
            self.logger.warning(f"网络接收量过大: {metrics.network_io_recv / (1024*1024):.2f}MB")
            
    def get_metrics(self, start_time: float = None, end_time: float = None) -> List[PerformanceMetrics]:
        """
        获取指定时间范围内的性能指标
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            List[PerformanceMetrics]: 性能指标列表
        """
        with self.lock:
            if start_time is None and end_time is None:
                return self.metrics.copy()
                
            filtered = []
            for metric in self.metrics:
                if start_time and metric.timestamp < start_time:
                    continue
                if end_time and metric.timestamp > end_time:
                    continue
                filtered.append(metric)
            return filtered
            
    def get_statistics(self, start_time: float = None, end_time: float = None) -> Dict[str, Any]:
        """
        获取性能统计信息
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        metrics = self.get_metrics(start_time, end_time)
        if not metrics:
            return {}
            
        # 计算统计值
        cpu_percents = [m.cpu_percent for m in metrics]
        memory_percents = [m.memory_percent for m in metrics]
        
        return {
            'cpu': {
                'min': min(cpu_percents),
                'max': max(cpu_percents),
                'avg': sum(cpu_percents) / len(cpu_percents)
            },
            'memory': {
                'min': min(memory_percents),
                'max': max(memory_percents),
                'avg': sum(memory_percents) / len(memory_percents)
            },
            'disk_io': {
                'total_read': sum(m.disk_io_read for m in metrics),
                'total_write': sum(m.disk_io_write for m in metrics)
            },
            'network_io': {
                'total_sent': sum(m.network_io_sent for m in metrics),
                'total_recv': sum(m.network_io_recv for m in metrics)
            }
        }
        
    def export_report(self, filepath: str):
        """
        导出性能报告
        
        Args:
            filepath: 报告文件路径
        """
        try:
            with open(filepath, 'w') as f:
                # 写入报告头
                f.write("性能监控报告\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n")
                
                # 写入统计信息
                stats = self.get_statistics()
                f.write("统计信息:\n")
                f.write(f"CPU使用率: 最小 {stats['cpu']['min']:.1f}%, 最大 {stats['cpu']['max']:.1f}%, 平均 {stats['cpu']['avg']:.1f}%\n")
                f.write(f"内存使用率: 最小 {stats['memory']['min']:.1f}%, 最大 {stats['memory']['max']:.1f}%, 平均 {stats['memory']['avg']:.1f}%\n")
                f.write(f"磁盘IO: 读取 {stats['disk_io']['total_read'] / (1024*1024):.2f}MB, 写入 {stats['disk_io']['total_write'] / (1024*1024):.2f}MB\n")
                f.write(f"网络IO: 发送 {stats['network_io']['total_sent'] / (1024*1024):.2f}MB, 接收 {stats['network_io']['total_recv'] / (1024*1024):.2f}MB\n")
                
            self.logger.info(f"性能报告已导出到: {filepath}")
        except Exception as e:
            self.logger.error(f"导出性能报告失败: {str(e)}") 