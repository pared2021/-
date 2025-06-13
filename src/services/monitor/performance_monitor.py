"""
性能监控服务
负责监控系统性能
"""
from typing import Dict, List, Optional
import time
import psutil
from dataclasses import dataclass
from core.error_handler import ErrorHandler, ErrorCode, ErrorContext

@dataclass
class PerformanceMetrics:
    """性能指标"""
    cpu_percent: float  # CPU使用率
    memory_percent: float  # 内存使用率
    disk_io: Dict[str, float]  # 磁盘IO
    network_io: Dict[str, float]  # 网络IO
    fps: float  # 帧率
    latency: float  # 延迟
    timestamp: float  # 时间戳

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, error_handler: ErrorHandler):
        """初始化
        
        Args:
            error_handler: 错误处理器
        """
        self.error_handler = error_handler
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history_size = 1000
        self.last_frame_time = 0
        self.frame_count = 0
        self.fps = 0
        self.fps_update_interval = 1.0
        self.last_fps_update = 0
        
    def update(self) -> Optional[PerformanceMetrics]:
        """更新性能指标
        
        Returns:
            Optional[PerformanceMetrics]: 性能指标
        """
        try:
            # 获取系统性能指标
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            network_io = psutil.net_io_counters()
            
            # 计算帧率
            current_time = time.time()
            self.frame_count += 1
            
            if current_time - self.last_fps_update >= self.fps_update_interval:
                self.fps = self.frame_count / (current_time - self.last_fps_update)
                self.frame_count = 0
                self.last_fps_update = current_time
                
            # 计算延迟
            latency = 0
            if self.last_frame_time > 0:
                latency = (current_time - self.last_frame_time) * 1000
            self.last_frame_time = current_time
            
            # 创建性能指标
            metrics = PerformanceMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_io={
                    "read_bytes": disk_io.read_bytes,
                    "write_bytes": disk_io.write_bytes,
                    "read_count": disk_io.read_count,
                    "write_count": disk_io.write_count
                },
                network_io={
                    "bytes_sent": network_io.bytes_sent,
                    "bytes_recv": network_io.bytes_recv,
                    "packets_sent": network_io.packets_sent,
                    "packets_recv": network_io.packets_recv
                },
                fps=self.fps,
                latency=latency,
                timestamp=current_time
            )
            
            # 更新历史记录
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history.pop(0)
                
            return metrics
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.PERFORMANCE_MONITOR_ERROR,
                "更新性能指标失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="PerformanceMonitor.update"
                )
            )
            return None
            
    def get_average_metrics(self, window_size: int = 10) -> Optional[PerformanceMetrics]:
        """获取平均性能指标
        
        Args:
            window_size: 窗口大小
            
        Returns:
            Optional[PerformanceMetrics]: 平均性能指标
        """
        try:
            if not self.metrics_history:
                return None
                
            # 获取最近的指标
            recent_metrics = self.metrics_history[-window_size:]
            
            # 计算平均值
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            avg_fps = sum(m.fps for m in recent_metrics) / len(recent_metrics)
            avg_latency = sum(m.latency for m in recent_metrics) / len(recent_metrics)
            
            # 计算IO平均值
            avg_disk_io = {
                "read_bytes": sum(m.disk_io["read_bytes"] for m in recent_metrics) / len(recent_metrics),
                "write_bytes": sum(m.disk_io["write_bytes"] for m in recent_metrics) / len(recent_metrics),
                "read_count": sum(m.disk_io["read_count"] for m in recent_metrics) / len(recent_metrics),
                "write_count": sum(m.disk_io["write_count"] for m in recent_metrics) / len(recent_metrics)
            }
            
            avg_network_io = {
                "bytes_sent": sum(m.network_io["bytes_sent"] for m in recent_metrics) / len(recent_metrics),
                "bytes_recv": sum(m.network_io["bytes_recv"] for m in recent_metrics) / len(recent_metrics),
                "packets_sent": sum(m.network_io["packets_sent"] for m in recent_metrics) / len(recent_metrics),
                "packets_recv": sum(m.network_io["packets_recv"] for m in recent_metrics) / len(recent_metrics)
            }
            
            return PerformanceMetrics(
                cpu_percent=avg_cpu,
                memory_percent=avg_memory,
                disk_io=avg_disk_io,
                network_io=avg_network_io,
                fps=avg_fps,
                latency=avg_latency,
                timestamp=time.time()
            )
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.PERFORMANCE_MONITOR_ERROR,
                "计算平均性能指标失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="PerformanceMonitor.get_average_metrics"
                )
            )
            return None
            
    def get_metrics_history(self) -> List[PerformanceMetrics]:
        """获取性能指标历史记录
        
        Returns:
            List[PerformanceMetrics]: 性能指标历史记录
        """
        return self.metrics_history.copy()
        
    def clear_history(self) -> None:
        """清空历史记录"""
        self.metrics_history.clear()
        
    def set_max_history_size(self, size: int) -> None:
        """设置最大历史记录大小
        
        Args:
            size: 最大历史记录大小
        """
        self.max_history_size = size
        while len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0) 