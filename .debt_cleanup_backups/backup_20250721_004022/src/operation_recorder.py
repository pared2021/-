"""操作记录器模块"""
import time
import json
from collections import Counter
from typing import List, Dict, Any


class OperationRecorder:
    """操作记录器类，用于记录和回放用户操作"""

    def __init__(self) -> None:
        """初始化操作记录器"""
        self.recording: bool = False
        self.operations: List[Dict[str, Any]] = []

    def start_recording(self) -> None:
        """开始录制操作"""
        self.recording = True
        self.operations.clear()

    def stop_recording(self) -> None:
        """停止录制操作"""
        self.recording = False

    def record_operation(self, operation_type: str, params: Dict[str, Any]) -> None:
        """记录一个操作

        Args:
            operation_type (str): 操作类型
            params (dict): 操作参数
        """
        if self.recording:
            self.operations.append(
                {"type": operation_type, "params": params, "timestamp": time.time()}
            )

    def clear_operations(self) -> None:
        """清空所有记录的操作"""
        self.operations.clear()

    def save_operations(self, filename: str) -> None:
        """保存操作记录到文件

        Args:
            filename (str): 文件名
        """
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.operations, f, indent=4)

    def load_operations(self, filename: str) -> None:
        """从文件加载操作记录

        Args:
            filename (str): 文件名
        """
        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.operations = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.operations = []

    def replay_operations(self, executor: Any) -> None:
        """回放操作记录

        Args:
            executor: 执行器对象，用于执行操作
        """
        for operation in self.operations:
            executor.execute_action(operation["type"], operation["params"])
            if operation != self.operations[-1]:  # 不是最后一个操作
                next_op = self.operations[self.operations.index(operation) + 1]
                time.sleep(next_op["timestamp"] - operation["timestamp"])

    def get_operation_count(self) -> int:
        """获取操作记录数量

        Returns:
            int: 操作记录数量
        """
        return len(self.operations)

    def get_operation_types(self) -> Dict[str, int]:
        """获取操作类型统计

        Returns:
            dict: 操作类型及其出现次数的字典
        """
        return Counter(op["type"] for op in self.operations)
