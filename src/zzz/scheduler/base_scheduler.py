"""
基础调度器 - 包含硬件加速和性能优化
"""
import os
import json
from typing import Dict, Optional
import onnxruntime as ort
from ...services.config import Config as ConfigManager


class BaseScheduler:
    def __init__(self):
        self.config = ConfigManager()
        self.performance_level = self._get_performance_level()
        self.dml_available = self._check_dml_support()
        self.providers = self._setup_providers()

    def _get_performance_level(self) -> str:
        """
        获取性能等级配置

        Returns:
            str: 性能等级 ('high', 'medium', 'low')
        """
        try:
            with open(os.path.join("config", "01", "performance.json"), "r") as f:
                config = json.load(f)
            return config.get("level", "medium")
        except:
            return "medium"

    def _check_dml_support(self) -> bool:
        """
        检查是否支持DirectML

        Returns:
            bool: 是否支持DirectML
        """
        try:
            providers = ort.get_available_providers()
            return "DmlExecutionProvider" in providers
        except:
            return False

    def _setup_providers(self) -> list:
        """
        设置ONNX Runtime的执行提供程序

        Returns:
            list: 执行提供程序列表
        """
        providers = []

        # 如果支持DirectML且性能等级为high，优先使用DirectML
        if self.dml_available and self.performance_level == "high":
            providers.append("DmlExecutionProvider")

        # 始终添加CPU作为后备
        providers.append("CPUExecutionProvider")

        return providers

    def get_execution_provider(self) -> str:
        """
        获取当前使用的执行提供程序

        Returns:
            str: 执行提供程序名称
        """
        return self.providers[0]

    def optimize_session_options(self) -> ort.SessionOptions:
        """
        根据性能等级优化会话选项

        Returns:
            ort.SessionOptions: 优化后的会话选项
        """
        options = ort.SessionOptions()

        if self.performance_level == "high":
            options.enable_mem_pattern = True
            options.enable_cpu_mem_arena = True
            options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        elif self.performance_level == "medium":
            options.enable_mem_pattern = True
            options.enable_cpu_mem_arena = True
            options.graph_optimization_level = (
                ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
            )
        else:  # low
            options.enable_mem_pattern = False
            options.enable_cpu_mem_arena = False
            options.graph_optimization_level = (
                ort.GraphOptimizationLevel.ORT_DISABLE_ALL
            )

        return options

    def create_inference_session(self, model_path: str) -> ort.InferenceSession:
        """
        创建推理会话

        Args:
            model_path: 模型文件路径

        Returns:
            ort.InferenceSession: 推理会话
        """
        options = self.optimize_session_options()
        return ort.InferenceSession(model_path, options, providers=self.providers)

    def get_performance_config(self) -> Dict:
        """
        获取性能相关配置

        Returns:
            Dict: 性能配置
        """
        return {
            "performance_level": self.performance_level,
            "dml_available": self.dml_available,
            "active_provider": self.get_execution_provider(),
            "all_providers": self.providers,
        }
