"""
配置管理器
负责管理和持久化配置
"""
import logging
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

import yaml


@dataclass
class ConfigVersion:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @staticmethod
    def from_string(version_str: str) -> "ConfigVersion":
        major, minor, patch = map(int, version_str.split("."))
        return ConfigVersion(major, minor, patch)

    def is_compatible(self, other: "ConfigVersion") -> bool:
        return self.major == other.major and self.minor >= other.minor


class ConfigManager:
    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        self.current_version = ConfigVersion(1, 0, 0)
        self.configs: Dict[str, Dict] = {}
        self.logger = logging.getLogger("ConfigManager")

    def load_game_config(self, game_name: str) -> Dict:
        """
        加载游戏配置

        Args:
            game_name: 游戏名称

        Returns:
            Dict: 游戏配置
        """
        config_path = os.path.join(self.config_dir, game_name, "config.yaml")
        if not os.path.exists(config_path):
            self.logger.warning(f"游戏 {game_name} 配置不存在")
            return self._create_default_config(game_name)

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # 版本检查
            config_version = ConfigVersion.from_string(config.get("version", "1.0.0"))
            if not self.current_version.is_compatible(config_version):
                self.logger.warning(f"配置版本 {config_version} 不兼容，需要升级")
                config = self._upgrade_config(config, game_name)

            # 验证配置
            if self._validate_config(config):
                self.configs[game_name] = config
                return config
            else:
                self.logger.error(f"游戏 {game_name} 配置验证失败")
                return self._create_default_config(game_name)

        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            return self._create_default_config(game_name)

    def save_game_config(self, game_name: str, config: Dict) -> bool:
        """
        保存游戏配置

        Args:
            game_name: 游戏名称
            config: 配置数据

        Returns:
            bool: 是否保存成功
        """
        try:
            config_dir = os.path.join(self.config_dir, game_name)
            os.makedirs(config_dir, exist_ok=True)

            # 备份当前配置
            self._backup_config(game_name)

            # 更新版本号
            config["version"] = str(self.current_version)

            # 保存配置
            config_path = os.path.join(config_dir, "config.yaml")
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, allow_unicode=True, sort_keys=False)

            self.configs[game_name] = config
            return True

        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
            return False

    def _create_default_config(self, game_name: str) -> Dict:
        """创建默认配置"""
        config = {
            "version": str(self.current_version),
            "game_name": game_name,
            "create_time": datetime.now().isoformat(),
            "global_params": {
                "check_interval": 0.1,
                "post_delay": 0.01,
                "retry_times": 3,
                "memory_limit": 2048,
            },
            "state_templates": {
                "default": {
                    "priority": 50,
                    "conditions": [],
                    "actions": [],
                    "next_states": [],
                }
            },
            "scene_logic": {"default": {"priority": 100, "states": ["default"]}},
        }
        return config

    def _validate_config(self, config: Dict) -> bool:
        """验证配置有效性"""
        required_fields = [
            "version",
            "game_name",
            "global_params",
            "state_templates",
            "scene_logic",
        ]

        # 检查必需字段
        for field in required_fields:
            if field not in config:
                self.logger.error(f"缺少必需字段: {field}")
                return False

        # 验证全局参数
        global_params = config["global_params"]
        if not isinstance(global_params, dict):
            self.logger.error("global_params 必须是字典类型")
            return False

        # 验证状态模板
        state_templates = config["state_templates"]
        if not isinstance(state_templates, dict):
            self.logger.error("state_templates 必须是字典类型")
            return False

        # 验证场景逻辑
        scene_logic = config["scene_logic"]
        if not isinstance(scene_logic, dict):
            self.logger.error("scene_logic 必须是字典类型")
            return False

        return True

    def _upgrade_config(self, config: Dict, game_name: str) -> Dict:
        """升级配置到当前版本"""
        old_version = ConfigVersion.from_string(config.get("version", "1.0.0"))

        # 备份旧配置
        self._backup_config(game_name, old_version)

        # 执行升级逻辑
        if old_version.major == 1:
            if old_version.minor == 0:
                # 1.0.x -> 1.1.0
                config = self._upgrade_1_0_to_1_1(config)

        # 更新版本号
        config["version"] = str(self.current_version)
        return config

    def _upgrade_1_0_to_1_1(self, config: Dict) -> Dict:
        """1.0.x 升级到 1.1.0"""
        # 添加新的配置字段
        if "global_params" not in config:
            config["global_params"] = {
                "check_interval": 0.1,
                "post_delay": 0.01,
                "retry_times": 3,
                "memory_limit": 2048,
            }

        # 更新状态模板格式
        for state in config["state_templates"].values():
            if "priority" not in state:
                state["priority"] = 50

        return config

    def _backup_config(
        self, game_name: str, version: Optional[ConfigVersion] = None
    ) -> None:
        """备份配置文件"""
        config_path = os.path.join(self.config_dir, game_name, "config.yaml")
        if not os.path.exists(config_path):
            return

        # 创建备份目录
        backup_dir = os.path.join(self.config_dir, game_name, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_str = f"_{version}" if version else ""
        backup_path = os.path.join(backup_dir, f"config_{timestamp}{version_str}.yaml")

        # 复制配置文件
        shutil.copy2(config_path, backup_path)
