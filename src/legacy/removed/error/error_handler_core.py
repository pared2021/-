"""
错误处理模块
负责错误处理和日志记录
"""
import json
import logging
import os
import platform
import sys
import time
import traceback
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, Callable, List

import psutil


class ErrorLevel(Enum):
    """错误级别"""

    INFO = 0  # 提示信息
    WARNING = 1  # 警告信息
    ERROR = 2  # 错误信息
    CRITICAL = 3  # 严重错误


class ErrorType(Enum):
    """错误类型"""

    NETWORK = "network"  # 网络错误
    STATE = "state"  # 状态错误
    RESOURCE = "resource"  # 资源错误
    CONFIG = "config"  # 配置错误
    RUNTIME = "runtime"  # 运行时错误


@dataclass
class ErrorInfo:
    """错误信息"""

    level: ErrorLevel
    type: ErrorType
    message: str
    timestamp: float
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = None


class ErrorHandler:
    def __init__(self, snapshot_dir: str):
        self.snapshot_dir = snapshot_dir
        self.logger = logging.getLogger("ErrorHandler")
        self.error_handlers: Dict[ErrorType, List[Callable]] = {
            error_type: [] for error_type in ErrorType
        }
        self.error_counts: Dict[ErrorType, int] = {
            error_type: 0 for error_type in ErrorType
        }
        self.last_snapshot_time = 0
        self.snapshot_interval = 3600  # 1小时
        self.lock = threading.Lock()

    def register_handler(self, error_type: ErrorType, handler: Callable) -> None:
        """注册错误处理器"""
        with self.lock:
            self.error_handlers[error_type].append(handler)

    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """处理错误"""
        error_info = self._classify_error(error, context)

        # 记录错误
        self._log_error(error_info)

        # 更新错误计数
        with self.lock:
            self.error_counts[error_info.type] += 1

        # 执行对应的处理器
        self._execute_handlers(error_info)

        # 检查是否需要创建快照
        self._check_snapshot()

    def _classify_error(
        self, error: Exception, context: Dict[str, Any] = None
    ) -> ErrorInfo:
        """分类错误"""
        if isinstance(error, ConnectionError):
            return ErrorInfo(
                level=ErrorLevel.ERROR,
                type=ErrorType.NETWORK,
                message=str(error),
                timestamp=time.time(),
                stack_trace=traceback.format_exc(),
                context=context,
            )
        elif isinstance(error, MemoryError):
            return ErrorInfo(
                level=ErrorLevel.CRITICAL,
                type=ErrorType.RESOURCE,
                message=str(error),
                timestamp=time.time(),
                stack_trace=traceback.format_exc(),
                context=context,
            )
        elif isinstance(error, ValueError):
            return ErrorInfo(
                level=ErrorLevel.WARNING,
                type=ErrorType.CONFIG,
                message=str(error),
                timestamp=time.time(),
                stack_trace=traceback.format_exc(),
                context=context,
            )
        else:
            return ErrorInfo(
                level=ErrorLevel.ERROR,
                type=ErrorType.RUNTIME,
                message=str(error),
                timestamp=time.time(),
                stack_trace=traceback.format_exc(),
                context=context,
            )

    def _log_error(self, error_info: ErrorInfo) -> None:
        """记录错误信息"""
        log_message = (
            f"[{error_info.level.name}] {error_info.type.value}: {error_info.message}\n"
            f"Context: {json.dumps(error_info.context, indent=2) if error_info.context else 'None'}\n"
            f"Stack Trace:\n{error_info.stack_trace if error_info.stack_trace else 'None'}"
        )

        if error_info.level == ErrorLevel.CRITICAL:
            self.logger.critical(log_message)
        elif error_info.level == ErrorLevel.ERROR:
            self.logger.error(log_message)
        elif error_info.level == ErrorLevel.WARNING:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    def _execute_handlers(self, error_info: ErrorInfo) -> None:
        """执行错误处理器"""
        handlers = self.error_handlers[error_info.type]
        for handler in handlers:
            try:
                handler(error_info)
            except Exception as e:
                self.logger.error(f"执行错误处理器失败: {e}")

    def _check_snapshot(self) -> None:
        """检查是否需要创建快照"""
        current_time = time.time()
        if current_time - self.last_snapshot_time >= self.snapshot_interval:
            self.create_snapshot()

    def create_snapshot(self) -> str:
        """创建状态快照"""
        try:
            # 确保快照目录存在
            os.makedirs(self.snapshot_dir, exist_ok=True)

            # 生成快照文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_path = os.path.join(
                self.snapshot_dir, f"snapshot_{timestamp}.json"
            )

            # 收集快照数据
            snapshot_data = {
                "timestamp": time.time(),
                "error_counts": self.error_counts,
                "system_info": self._get_system_info(),
            }

            # 保存快照
            with open(snapshot_path, "w", encoding="utf-8") as f:
                json.dump(snapshot_data, f, indent=4, ensure_ascii=False)

            self.last_snapshot_time = time.time()
            return snapshot_path

        except Exception as e:
            self.logger.error(f"创建快照失败: {e}")
            return ""

    def restore_from_snapshot(self, snapshot_path: str) -> bool:
        """从快照恢复"""
        try:
            with open(snapshot_path, "r", encoding="utf-8") as f:
                snapshot_data = json.load(f)

            # 恢复错误计数
            self.error_counts = snapshot_data["error_counts"]

            return True

        except Exception as e:
            self.logger.error(f"从快照恢复失败: {e}")
            return False

    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "platform": platform.platform(),
            "python_version": sys.version,
            "memory_total": memory.total,
            "memory_available": memory.available,
            "memory_percent": memory.percent,
            "disk_total": disk.total,
            "disk_free": disk.free,
            "disk_percent": disk.percent,
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
        }

    def clear_error_counts(self) -> None:
        """清除错误计数"""
        with self.lock:
            for error_type in ErrorType:
                self.error_counts[error_type] = 0

    def _save_error_report(self, error_info: Dict[str, Any]) -> Optional[str]:
        """保存错误报告到文件"""
        try:
            # 创建错误报告目录
            if not os.path.exists(self.snapshot_dir):
                os.makedirs(self.snapshot_dir)

            # 生成错误报告文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_report_{timestamp}.json"
            filepath = os.path.join(self.snapshot_dir, filename)

            # 保存错误报告
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(error_info, f, indent=4, ensure_ascii=False)

            return filepath

        except Exception as e:
            self.logger.error("保存错误报告失败: %s", e)
            return None

    def _load_error_report(self, filepath: str) -> Optional[Dict[str, Any]]:
        """加载错误报告"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error("加载错误报告失败: %s", e)
            return None

    def _collect_system_info(self) -> Dict[str, Any]:
        """收集系统信息"""
        try:
            system_info = {
                "platform": platform.platform(),
                "python_version": sys.version,
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": {
                    path.mountpoint: {
                        "total": psutil.disk_usage(path.mountpoint).total,
                        "used": psutil.disk_usage(path.mountpoint).used,
                        "free": psutil.disk_usage(path.mountpoint).free,
                    }
                    for path in psutil.disk_partitions()
                    if os.path.exists(path.mountpoint)
                },
            }

            return system_info

        except Exception as e:
            self.logger.error("收集系统信息失败: %s", e)
            return {}
