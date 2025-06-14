"""
自动战斗系统
"""
import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from src.services.config import Config as ConfigManager
from ..utils.cmd_recorder import CommandRecorder

# 使用统一的Action体系
from src.common.action_system import (
    ActionType, BattleAction, ActionSequence, ActionFactory, BaseAction
)

# 向后兼容性别名（如果需要旧的接口）
# BattleAction已从common.action_system导入


class AutoBattleSystem:
    def __init__(self, character_name: str, config_path: str):
        """
        初始化自动战斗系统

        Args:
            character_name: 角色名称
            config_path: 配置文件路径
        """
        self.character_name = character_name
        self.config_path = config_path
        self.config = ConfigManager()
        self.recorder = CommandRecorder()
        self.actions: List[BattleAction] = []
        self.current_state: Dict = {}

        # 加载角色战斗配置
        self._load_battle_config()

    def _load_battle_config(self):
        """加载战斗配置"""
        config_file = os.path.join(self.config_path, f"{self.character_name}.json")
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"找不到角色 {self.character_name} 的战斗配置文件")

        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)

        # 解析战斗动作
        self.actions = []
        for action_data in config_data["actions"]:
            # 创建统一的BattleAction对象
            action = BattleAction(
                name=action_data.get("name", f"battle_{action_data['type']}"),
                type=ActionType.BATTLE,
                action_type=action_data["type"],
                params={
                    "target": action_data["target"],
                    "conditions": action_data.get("conditions", [])
                },
                delay=action_data.get("delay", 0.0),
                fallback=action_data.get("fallback"),
                priority=action_data.get("priority", 0),
                cooldown=action_data.get("cooldown", 0.0)
            )
            self.actions.append(action)

    def update_state(self, new_state: Dict):
        """
        更新当前状态

        Args:
            new_state: 新的状态数据
        """
        self.current_state.update(new_state)

    def check_conditions(self, conditions: List[Dict]) -> bool:
        """
        检查条件是否满足

        Args:
            conditions: 条件列表

        Returns:
            bool: 是否满足所有条件
        """
        for condition in conditions:
            target = condition["target"]
            operator = condition["operator"]
            value = condition["value"]

            if target not in self.current_state:
                return False

            current_value = self.current_state[target]

            if operator == "eq" and current_value != value:
                return False
            elif operator == "gt" and current_value <= value:
                return False
            elif operator == "lt" and current_value >= value:
                return False
            elif operator == "contains" and value not in current_value:
                return False

        return True

    def get_next_action(self) -> Optional[BattleAction]:
        """
        获取下一个可执行的动作

        Returns:
            Optional[BattleAction]: 下一个动作，如果没有可执行的动作则返回None
        """
        for action in self.actions:
            conditions = action.params.get("conditions", [])
            if self.check_conditions(conditions):
                return action

            if action.fallback:
                # 检查是否有可用的后备动作
                for fallback_action in self.actions:
                    if fallback_action.action_type == action.fallback:
                        return fallback_action

        return None

    def record_action(self, action: BattleAction):
        """
        记录执行的动作

        Args:
            action: 执行的动作
        """
        self.recorder.record_command(
            {
                "type": action.action_type,
                "target": action.params.get("target", ""),
                "state": self.current_state.copy(),
            }
        )

    def save_recording(self, output_path: str):
        """
        保存录制的动作序列

        Args:
            output_path: 输出文件路径
        """
        self.recorder.save_recording(output_path)
