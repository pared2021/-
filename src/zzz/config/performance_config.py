"""
性能配置管理
"""
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import json
import os
import onnxruntime as ort  # type: ignore


@dataclass
class RenderConfig:
    """渲染配置"""

    resolution: Tuple[int, int]  # (width, height)
    fps_limit: int
    shadow_quality: int  # 0-4
    reflection_quality: int  # 0-4
    particle_quality: int  # 0-2
    texture_quality: str  # "high", "medium", "low"


@dataclass
class ComputeConfig:
    """计算配置"""

    fp16_enabled: bool = False
    async_compute: bool = False
    texture_compression: bool = False
    collision_precision: float = 0.5  # 0.5-1.0
    max_vram_usage: int = 0  # MB


class PerformanceConfig:
    render_config: Optional[RenderConfig]
    compute_config: Optional[ComputeConfig]

    def __init__(self, config_path: str = "config/01/performance.json"):
        self.config_path = config_path
        self.render_config: Optional[RenderConfig] = None
        self.compute_config: Optional[ComputeConfig] = ComputeConfig()

        # 加载配置
        self.load_config()

    def load_config(self):
        """加载性能配置"""
        if not os.path.exists(self.config_path):
            # 使用默认中等配置
            self._set_medium_config()
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            level = config.get("level", "medium")
            if level == "high":
                self._set_high_config()
            elif level == "low":
                self._set_low_config()
            else:
                self._set_medium_config()

        except Exception as e:
            print(f"加载性能配置失败: {e}")
            self._set_medium_config()

    def _set_high_config(self):
        """设置高配置"""
        self.render_config = RenderConfig(
            resolution=(3840, 2160),  # 4K
            fps_limit=120,
            shadow_quality=4,
            reflection_quality=4,
            particle_quality=2,
            texture_quality="high",
        )

        self.compute_config = ComputeConfig(
            fp16_enabled=True,
            async_compute=True,
            texture_compression=True,
            collision_precision=1.0,
            max_vram_usage=8192,  # 8GB
        )

    def _set_medium_config(self) -> None:
        """设置中配置"""
        if self.compute_config is not None:
            self.compute_config.fp16_enabled = True
            self.compute_config.async_compute = True

        self.render_config = RenderConfig(
            resolution=(1920, 1080),  # 1080P
            fps_limit=60,
            shadow_quality=2,
            reflection_quality=2,
            particle_quality=1,
            texture_quality="medium",
        )

        self.compute_config = ComputeConfig(
            fp16_enabled=True,
            async_compute=True,
            texture_compression=True,
            collision_precision=0.75,
            max_vram_usage=4096,  # 4GB
        )

    def _set_low_config(self):
        """设置低配置"""
        self.render_config = RenderConfig(
            resolution=(1280, 720),  # 720P
            fps_limit=30,
            shadow_quality=0,
            reflection_quality=0,
            particle_quality=0,
            texture_quality="low",
        )

        self.compute_config = ComputeConfig(
            fp16_enabled=False,
            async_compute=False,
            texture_compression=True,
            collision_precision=0.5,
            max_vram_usage=2048,  # 2GB
        )

    def save_config(self):
        """保存当前配置"""
        config = {
            "render": {
                "resolution": self.render_config.resolution,
                "fps_limit": self.render_config.fps_limit,
                "shadow_quality": self.render_config.shadow_quality,
                "reflection_quality": self.render_config.reflection_quality,
                "particle_quality": self.render_config.particle_quality,
                "texture_quality": self.render_config.texture_quality,
            },
            "compute": {
                "fp16_enabled": self.compute_config.fp16_enabled,
                "async_compute": self.compute_config.async_compute,
                "texture_compression": self.compute_config.texture_compression,
                "collision_precision": self.compute_config.collision_precision,
                "max_vram_usage": self.compute_config.max_vram_usage,
            },
        }

        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

    def apply_directml_config(self, session_options: "ort.SessionOptions"):
        """
        应用DirectML相关配置

        Args:
            session_options: ONNX Runtime会话选项
        """
        if self.compute_config and self.compute_config.fp16_enabled:
            session_options.graph_optimization_level = 99  # 启用所有优化
            # 设置DirectML执行器选项
            session_options.add_session_config_entry("DirectML.EnableF16Reduce", "1")

        if self.compute_config and self.compute_config.async_compute:
            session_options.add_session_config_entry("DirectML.AsyncCompute", "1")

        # 设置显存限制
        if self.compute_config:
            session_options.add_session_config_entry(
                "DirectML.MaximumMemoryMB", str(self.compute_config.max_vram_usage)
            )

    def enable_fp16(self) -> None:
        if self.compute_config:
            self.compute_config.fp16_enabled = True

    def disable_fp16(self) -> None:
        if self.compute_config:
            self.compute_config.fp16_enabled = False

    def enable_async_compute(self) -> None:
        if self.compute_config:
            self.compute_config.async_compute = True

    def disable_async_compute(self) -> None:
        if self.compute_config:
            self.compute_config.async_compute = False

    def set_max_vram_usage(self, max_mb: int) -> None:
        if self.compute_config:
            self.compute_config.max_vram_usage = max_mb

    def is_fp16_enabled(self) -> bool:
        if self.compute_config:
            return self.compute_config.fp16_enabled
        return False

    def is_async_compute_enabled(self) -> bool:
        if self.compute_config:
            return self.compute_config.async_compute
        return False

    def get_current_settings(
        self,
    ) -> Tuple[Optional[RenderConfig], Optional[ComputeConfig]]:
        return (self.render_config, self.compute_config)

    def get_render_settings(self) -> Tuple[Optional[int], ...]:
        if self.render_config:
            return (self.render_config.resolution[0], self.render_config.fps_limit)
        return (None, None)
