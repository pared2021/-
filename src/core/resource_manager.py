"""
资源管理器
负责管理和监控系统资源使用
"""
import ctypes
import gc
import json
import logging
import os
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any

import GPUtil
import numpy as np
import psutil


class ResourceType(Enum):
    """资源类型"""

    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    DISK = "disk"


@dataclass
class ResourceLimit:
    """资源限制"""

    max_cpu_percent: float = 80.0
    max_memory_mb: int = 2048
    max_gpu_memory_mb: int = 4096
    min_free_disk_mb: int = 1024


@dataclass
class ResourceUsage:
    """资源使用情况"""

    cpu_percent: float
    memory_mb: int
    gpu_memory_mb: int
    free_disk_mb: int
    timestamp: float


class ResourceManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.logger = logging.getLogger("ResourceManager")
        self.resource_limit = ResourceLimit()
        self.usage_history: List[ResourceUsage] = []
        self.history_max_size = 1000
        self.check_interval = 5  # 5秒
        self.lock = threading.Lock()
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.stats_file = "resource_stats.json"

        # 加载配置
        self._load_config()

    def _load_config(self) -> None:
        """加载资源配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)

                self.resource_limit = ResourceLimit(
                    max_cpu_percent=config.get("max_cpu_percent", 80.0),
                    max_memory_mb=config.get("max_memory_mb", 2048),
                    max_gpu_memory_mb=config.get("max_gpu_memory_mb", 4096),
                    min_free_disk_mb=config.get("min_free_disk_mb", 1024),
                )
        except Exception as e:
            self.logger.error(f"加载资源配置失败: {e}")

    def save_config(self) -> None:
        """保存资源配置"""
        try:
            config = {
                "max_cpu_percent": self.resource_limit.max_cpu_percent,
                "max_memory_mb": self.resource_limit.max_memory_mb,
                "max_gpu_memory_mb": self.resource_limit.max_gpu_memory_mb,
                "min_free_disk_mb": self.resource_limit.min_free_disk_mb,
            }

            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"保存资源配置失败: {e}")

    def start_monitoring(self) -> None:
        """启动资源监控"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self) -> None:
        """停止资源监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def _monitor_loop(self) -> None:
        """监控循环"""
        while self.monitoring:
            try:
                usage = self._get_resource_usage()
                self._update_history(usage)
                self._check_limits(usage)
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"资源监控失败: {e}")

    def _get_resource_usage(self) -> ResourceUsage:
        """获取资源使用情况"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent()

        # 内存使用
        memory = psutil.Process().memory_info()
        memory_mb = memory.rss / 1024 / 1024

        # GPU使用
        gpu_memory_mb = 0
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_memory_mb = gpus[0].memoryUsed
        except Exception:
            pass

        # 磁盘空间
        disk = psutil.disk_usage("/")
        free_disk_mb = disk.free / 1024 / 1024

        return ResourceUsage(
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            gpu_memory_mb=gpu_memory_mb,
            free_disk_mb=free_disk_mb,
            timestamp=time.time(),
        )

    def _update_history(self, usage: ResourceUsage) -> None:
        """更新使用历史"""
        with self.lock:
            self.usage_history.append(usage)
            if len(self.usage_history) > self.history_max_size:
                self.usage_history = self.usage_history[-self.history_max_size :]

    def _check_limits(self, usage: ResourceUsage) -> None:
        """检查资源限制"""
        warnings = []

        if usage.cpu_percent > self.resource_limit.max_cpu_percent:
            warnings.append(f"CPU使用率过高: {usage.cpu_percent:.1f}%")

        if usage.memory_mb > self.resource_limit.max_memory_mb:
            warnings.append(f"内存使用过高: {usage.memory_mb:.1f}MB")

        if usage.gpu_memory_mb > self.resource_limit.max_gpu_memory_mb:
            warnings.append(f"GPU内存使用过高: {usage.gpu_memory_mb:.1f}MB")

        if usage.free_disk_mb < self.resource_limit.min_free_disk_mb:
            warnings.append(f"磁盘空间不足: {usage.free_disk_mb:.1f}MB")

        if warnings:
            self.logger.warning("资源警告:\n" + "\n".join(warnings))

    def get_resource_stats(self) -> Dict[str, Any]:
        """获取资源统计信息"""
        with self.lock:
            if not self.usage_history:
                return {}

            # 转换为numpy数组以便计算
            cpu_usage = np.array([u.cpu_percent for u in self.usage_history])
            memory_usage = np.array([u.memory_mb for u in self.usage_history])
            gpu_usage = np.array([u.gpu_memory_mb for u in self.usage_history])

            return {
                "cpu": {
                    "current": self.usage_history[-1].cpu_percent,
                    "mean": np.mean(cpu_usage),
                    "max": np.max(cpu_usage),
                    "min": np.min(cpu_usage),
                },
                "memory": {
                    "current": self.usage_history[-1].memory_mb,
                    "mean": np.mean(memory_usage),
                    "max": np.max(memory_usage),
                    "min": np.min(memory_usage),
                },
                "gpu": {
                    "current": self.usage_history[-1].gpu_memory_mb,
                    "mean": np.mean(gpu_usage),
                    "max": np.max(gpu_usage),
                    "min": np.min(gpu_usage),
                },
                "disk": {"free": self.usage_history[-1].free_disk_mb},
            }

    def _save_resource_stats(self, stats: Dict) -> bool:
        """保存资源统计信息"""
        try:
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error("保存资源统计失败: %s", e)
            return False

    def _load_resource_stats(self) -> Optional[Dict]:
        """加载资源统计信息"""
        try:
            with open(self.stats_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error("加载资源统计失败: %s", e)
            return None

    def _log_resource_usage(self):
        """记录资源使用情况"""
        try:
            memory = psutil.Process().memory_info()
            rss_mb = memory.rss / (1024 * 1024)
            vms_mb = memory.vms / (1024 * 1024)
            self.logger.info(
                "资源使用情况 - RSS: %s MB, VMS: %s MB", f"{rss_mb:.1f}", f"{vms_mb:.1f}"
            )
        except Exception as e:
            self.logger.error("记录资源使用失败: %s", e)

    def _cleanup_memory(self):
        """清理内存"""
        try:
            # 强制进行垃圾回收
            gc.collect()

            # 在Linux系统上尝试调用malloc_trim
            try:
                ctypes.CDLL("libc.so.6").malloc_trim(0)
            except Exception:
                pass

        except Exception as e:
            self.logger.error("清理内存失败: %s", e)

    def optimize_resource_usage(self) -> None:
        """优化资源使用"""
        self._cleanup_memory()

        # 获取当前进程
        process = psutil.Process()

        # 如果内存使用过高，尝试清理内存
        if (
            process.memory_info().rss / (1024 * 1024)
            > self.resource_limit.max_memory_mb
        ):
            try:
                ctypes.CDLL("libc.so.6").malloc_trim(0)
            except Exception:
                pass
