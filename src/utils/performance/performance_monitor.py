"""
性能监控
监控CPU、内存使用率、帧率和响应时间
"""
from typing import Dict, List, Optional, Any, Tuple
import psutil
import time
import threading
import logging
import win32gui
import win32process
from dataclasses import dataclass
from collections import deque
import numpy as np


@dataclass
class PerformanceMetrics:
    """性能指标"""

    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used: int
    fps: float
    response_time: float


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, window_title: str, max_samples: int = 1000):
        """初始化性能监控器

        Args:
            window_title: 要监控的窗口标题
            max_samples: 最大样本数量
        """
        self.logger = logging.getLogger("PerformanceMonitor")
        self.window_title = window_title
        self.max_samples = max_samples

        # 性能数据
        self.metrics: deque[PerformanceMetrics] = deque(maxlen=max_samples)

        # 监控状态
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None

        # FPS计算
        self.frame_times: deque[float] = deque(maxlen=120)  # 2秒内的帧时间
        self.last_frame_time = 0

        # 响应时间计算
        self.response_times: deque[float] = deque(maxlen=100)

        # 查找目标窗口
        self._find_target_window()

    def _find_target_window(self):
        """查找目标窗口"""

        def callback(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if self.window_title.lower() in title.lower():
                    ctx.append(hwnd)
            return True

        windows = []
        win32gui.EnumWindows(callback, windows)

        if not windows:
            self.logger.warning(f"未找到标题包含 '{self.window_title}' 的窗口")
            self.window_handle = None
            self.process = None
            return

        self.window_handle = windows[0]

        # 获取进程ID
        _, pid = win32process.GetWindowThreadProcessId(self.window_handle)
        try:
            self.process = psutil.Process(pid)
            self.logger.info(f"找到目标进程: {self.process.name()} (PID: {pid})")
        except psutil.NoSuchProcess:
            self.logger.error(f"无法获取进程 {pid}")
            self.process = None

    def start(self):
        """开始监控"""
        if self.running:
            return

        if not self.process:
            self.logger.error("未找到目标进程，无法开始监控")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        self.logger.info("开始性能监控")

    def stop(self):
        """停止监控"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("停止性能监控")

    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 检查进程是否存在
                if not self.process.is_running():
                    self.logger.error("目标进程已终止")
                    break

                # 收集性能指标
                metrics = self._collect_metrics()
                self.metrics.append(metrics)

                # 每秒收集10次样本
                time.sleep(0.1)

            except Exception as e:
                self.logger.error(f"监控出错: {e}", exc_info=True)
                break

        self.running = False

    def _collect_metrics(self) -> PerformanceMetrics:
        """收集性能指标"""
        now = time.time()

        # CPU使用率
        try:
            cpu_percent = self.process.cpu_percent()
        except:
            cpu_percent = 0

        # 内存使用
        try:
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            memory_used = memory_info.rss
        except:
            memory_percent = 0
            memory_used = 0

        # 计算FPS
        fps = self._calculate_fps(now)

        # 计算平均响应时间
        response_time = self._calculate_response_time()

        return PerformanceMetrics(
            timestamp=now,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used=memory_used,
            fps=fps,
            response_time=response_time,
        )

    def _calculate_fps(self, now: float) -> float:
        """计算FPS"""
        # 记录帧时间
        if self.last_frame_time:
            frame_time = now - self.last_frame_time
            self.frame_times.append(frame_time)

        self.last_frame_time = now

        # 计算FPS
        if len(self.frame_times) < 2:
            return 0

        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1 / avg_frame_time if avg_frame_time > 0 else 0

    def _calculate_response_time(self) -> float:
        """计算响应时间"""
        if not self.response_times:
            return 0
        return sum(self.response_times) / len(self.response_times)

    def record_response_time(self, response_time: float):
        """记录响应时间

        Args:
            response_time: 响应时间(秒)
        """
        self.response_times.append(response_time)

    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """获取当前性能指标"""
        if not self.metrics:
            return None
        return self.metrics[-1]

    def get_metrics_history(self, duration: float = 60.0) -> List[PerformanceMetrics]:
        """获取历史性能指标

        Args:
            duration: 历史时长(秒)

        Returns:
            指定时长内的性能指标列表
        """
        if not self.metrics:
            return []

        now = time.time()
        return [m for m in self.metrics if now - m.timestamp <= duration]

    def get_statistics(self, duration: float = 60.0) -> Dict[str, Any]:
        """获取统计信息

        Args:
            duration: 统计时长(秒)

        Returns:
            统计信息字典
        """
        metrics = self.get_metrics_history(duration)
        if not metrics:
            return {"duration": duration, "samples": 0}

        # 提取数据
        cpu_data = [m.cpu_percent for m in metrics]
        memory_data = [m.memory_percent for m in metrics]
        fps_data = [m.fps for m in metrics]
        response_data = [m.response_time for m in metrics]

        # 计算统计值
        def calculate_stats(data: List[float]) -> Dict[str, float]:
            if not data:
                return {"min": 0, "max": 0, "avg": 0, "std": 0}
            return {
                "min": min(data),
                "max": max(data),
                "avg": sum(data) / len(data),
                "std": float(np.std(data)),
            }

        return {
            "duration": duration,
            "samples": len(metrics),
            "cpu": calculate_stats(cpu_data),
            "memory": calculate_stats(memory_data),
            "fps": calculate_stats(fps_data),
            "response_time": calculate_stats(response_data),
        }
