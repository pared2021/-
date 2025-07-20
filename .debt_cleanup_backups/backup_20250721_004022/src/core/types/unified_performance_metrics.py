"""统一性能指标定义"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time


@dataclass
class UnifiedPerformanceMetrics:
    """统一的性能指标数据结构
    
    整合了原有的三个PerformanceMetrics定义：
    - 基础性能监控（performance_monitor.py）
    - 服务层性能监控（services/monitor/performance_monitor.py）
    - 通用性能监控（common/monitor.py）
    """
    
    timestamp: float = field(default_factory=time.time)
    
    # 基础性能指标（所有版本共有）
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used: int = 0  # 字节数
    
    # 游戏性能指标（来自 performance/performance_monitor.py）
    fps: float = 0.0
    response_time: float = 0.0
    
    # 延迟指标（来自 services/monitor/performance_monitor.py）
    latency: float = 0.0
    
    # 磁盘IO指标（整合不同格式）
    disk_io: Dict[str, float] = field(default_factory=lambda: {
        'read_bytes': 0.0,
        'write_bytes': 0.0,
        'read_count': 0.0,
        'write_count': 0.0,
        'read_total': 0.0,  # 来自 common/monitor.py
        'write_total': 0.0   # 来自 common/monitor.py
    })
    
    # 网络IO指标（整合不同格式）
    network_io: Dict[str, float] = field(default_factory=lambda: {
        'bytes_sent': 0.0,
        'bytes_recv': 0.0,
        'packets_sent': 0.0,
        'packets_recv': 0.0,
        'sent_total': 0.0,   # 来自 common/monitor.py
        'recv_total': 0.0    # 来自 common/monitor.py
    })
    
    # 扩展指标
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        # 确保时间戳有效
        if self.timestamp <= 0:
            self.timestamp = time.time()
        
        # 统一延迟和响应时间（如果只有一个值）
        if self.latency == 0.0 and self.response_time > 0.0:
            self.latency = self.response_time
        elif self.response_time == 0.0 and self.latency > 0.0:
            self.response_time = self.latency
    
    def is_valid(self) -> bool:
        """检查指标是否有效"""
        return (
            self.timestamp > 0 and
            0 <= self.cpu_percent <= 100 and
            0 <= self.memory_percent <= 100 and
            self.memory_used >= 0
        )
    
    def get_memory_mb(self) -> float:
        """获取内存使用量（MB）"""
        return self.memory_used / (1024 * 1024)
    
    def get_memory_gb(self) -> float:
        """获取内存使用量（GB）"""
        return self.memory_used / (1024 * 1024 * 1024)
    
    def get_disk_io_mb(self) -> Dict[str, float]:
        """获取磁盘IO（MB）"""
        return {
            'read_mb': self.disk_io.get('read_bytes', 0) / (1024 * 1024),
            'write_mb': self.disk_io.get('write_bytes', 0) / (1024 * 1024),
            'read_total_mb': self.disk_io.get('read_total', 0) / (1024 * 1024),
            'write_total_mb': self.disk_io.get('write_total', 0) / (1024 * 1024)
        }
    
    def get_network_io_mb(self) -> Dict[str, float]:
        """获取网络IO（MB）"""
        return {
            'sent_mb': self.network_io.get('bytes_sent', 0) / (1024 * 1024),
            'recv_mb': self.network_io.get('bytes_recv', 0) / (1024 * 1024),
            'sent_total_mb': self.network_io.get('sent_total', 0) / (1024 * 1024),
            'recv_total_mb': self.network_io.get('recv_total', 0) / (1024 * 1024)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'timestamp': self.timestamp,
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'memory_used': self.memory_used,
            'fps': self.fps,
            'response_time': self.response_time,
            'latency': self.latency,
            'disk_io': self.disk_io,
            'network_io': self.network_io,
            'custom_metrics': self.custom_metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedPerformanceMetrics':
        """从字典创建性能指标对象"""
        return cls(
            timestamp=data.get('timestamp', time.time()),
            cpu_percent=data.get('cpu_percent', 0.0),
            memory_percent=data.get('memory_percent', 0.0),
            memory_used=data.get('memory_used', 0),
            fps=data.get('fps', 0.0),
            response_time=data.get('response_time', 0.0),
            latency=data.get('latency', 0.0),
            disk_io=data.get('disk_io', {}),
            network_io=data.get('network_io', {}),
            custom_metrics=data.get('custom_metrics', {})
        )
    
    @classmethod
    def from_legacy_basic(cls, timestamp: float, cpu_percent: float, 
                         memory_percent: float, memory_used: int, 
                         fps: float, response_time: float) -> 'UnifiedPerformanceMetrics':
        """从基础性能监控数据创建（兼容 performance/performance_monitor.py）"""
        return cls(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used=memory_used,
            fps=fps,
            response_time=response_time
        )
    
    @classmethod
    def from_legacy_service(cls, cpu_percent: float, memory_percent: float,
                           disk_io: Dict[str, float], network_io: Dict[str, float],
                           fps: float, latency: float, timestamp: float) -> 'UnifiedPerformanceMetrics':
        """从服务层性能监控数据创建（兼容 services/monitor/performance_monitor.py）"""
        return cls(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            fps=fps,
            latency=latency,
            disk_io=disk_io,
            network_io=network_io
        )
    
    @classmethod
    def from_legacy_common(cls, timestamp: float, cpu_percent: float,
                          memory_percent: float, disk_io_read: float,
                          disk_io_write: float, network_io_sent: float,
                          network_io_recv: float) -> 'UnifiedPerformanceMetrics':
        """从通用性能监控数据创建（兼容 common/monitor.py）"""
        return cls(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_io={
                'read_total': disk_io_read,
                'write_total': disk_io_write
            },
            network_io={
                'sent_total': network_io_sent,
                'recv_total': network_io_recv
            }
        )
    
    def merge_with(self, other: 'UnifiedPerformanceMetrics') -> 'UnifiedPerformanceMetrics':
        """与另一个性能指标合并（取最新时间戳的数据为主）"""
        if other.timestamp > self.timestamp:
            primary, secondary = other, self
        else:
            primary, secondary = self, other
        
        # 合并IO数据
        merged_disk_io = {**secondary.disk_io, **primary.disk_io}
        merged_network_io = {**secondary.network_io, **primary.network_io}
        merged_custom = {**secondary.custom_metrics, **primary.custom_metrics}
        
        return UnifiedPerformanceMetrics(
            timestamp=primary.timestamp,
            cpu_percent=primary.cpu_percent,
            memory_percent=primary.memory_percent,
            memory_used=primary.memory_used,
            fps=primary.fps or secondary.fps,
            response_time=primary.response_time or secondary.response_time,
            latency=primary.latency or secondary.latency,
            disk_io=merged_disk_io,
            network_io=merged_network_io,
            custom_metrics=merged_custom
        )