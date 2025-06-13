"""
决策引擎
负责游戏状态分析和行为决策
"""
import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Callable

import cv2
import numpy as np


@dataclass
class Rule:
    """规则类"""

    name: str
    condition: Callable[[Dict[str, Any]], bool]
    action: Callable[[Dict[str, Any]], None]
    priority: int = 0
    description: str = ""


class DecisionEngineError(Exception):
    """决策引擎相关错误"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class StateValidator:
    """状态验证器"""

    @staticmethod
    def validate_state_update(state_update: Dict[str, Any]) -> bool:
        """
        验证状态更新的格式

        Args:
            state_update: 状态更新字典

        Returns:
            bool: 是否有效
        """
        required_fields = ["timestamp", "source", "data"]
        if not all(field in state_update for field in required_fields):
            return False

        if not isinstance(state_update["timestamp"], (int, float)):
            return False

        if not isinstance(state_update["data"], dict):
            return False

        if not StateValidator.validate_data(state_update["data"]):
            return False

        return True

    @staticmethod
    def validate_data(data: Dict[str, Any]) -> bool:
        """
        验证数据字典的格式

        Args:
            data: 数据字典

        Returns:
            bool: 是否有效
        """
        if not data:
            return False

        for value in data.values():
            if not isinstance(value, (bool, int, float, str, list, dict)):
                return False

        return True


class DecisionEngine:
    """决策引擎类"""

    def __init__(self) -> None:
        """初始化决策引擎"""
        self.logger = logging.getLogger("DecisionEngine")
        self.rules: Dict[str, Rule] = {}
        self.state: Dict[str, Any] = {}
        self.actions: Dict[str, Callable] = {}
        self.state_validator = StateValidator()

    def register_rule(self, rule: Rule) -> None:
        """
        注册决策规则

        Args:
            rule: 规则对象

        Raises:
            DecisionEngineError: 当规则无效时抛出
        """
        if not rule.name:
            raise DecisionEngineError("规则名称不能为空")

        if rule.name in self.rules:
            raise DecisionEngineError(f"规则'{rule.name}'已存在")

        if not callable(rule.condition) or not callable(rule.action):
            raise DecisionEngineError("规则的条件和动作必须是可调用对象")

        self.rules[rule.name] = rule
        self.logger.info(f"规则'{rule.name}'已注册")

    def register_action(
        self, name: str, action: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        注册动作

        Args:
            name: 动作名称
            action: 动作执行函数

        Raises:
            DecisionEngineError: 当动作注册失败时抛出
        """
        try:
            if name in self.actions:
                raise DecisionEngineError(f"动作'{name}'已存在")

            self.actions[name] = action
            self.logger.info(f"动作'{name}'已注册")

        except Exception as e:
            raise DecisionEngineError(f"注册动作失败: {str(e)}") from e

    def update_state(self, state_update: Dict[str, Any]) -> None:
        """
        更新状态

        Args:
            state_update: 状态更新字典

        Raises:
            DecisionEngineError: 当状态更新无效时抛出
        """
        try:
            if not self.state_validator.validate_state_update(state_update):
                raise DecisionEngineError("无效的状态更新格式")

            if (
                "timestamp" in self.state
                and state_update["timestamp"] < self.state["timestamp"]
            ):
                self.logger.warning("收到过期的状态更新，已忽略")
                return

            self.state.update(state_update)
            self.logger.debug(f"状态已更新: {state_update}")

        except Exception as e:
            raise DecisionEngineError(f"状态更新失败: {str(e)}") from e

    def make_decision(self) -> Optional[str]:
        """
        根据当前状态做出决策

        Returns:
            str: 执行的动作名称

        Raises:
            DecisionEngineError: 当决策过程失败时抛出
        """
        try:
            if not self.state:
                raise DecisionEngineError("状态为空，无法做出决策")

            if not self.rules:
                raise DecisionEngineError("没有注册任何规则")

            sorted_rules = sorted(
                self.rules.values(), key=lambda x: x.priority, reverse=True
            )

            for rule in sorted_rules:
                try:
                    if rule.condition(self.state):
                        rule.action(self.state)
                        self.logger.info(f"执行规则: {rule.name}")
                        return rule.name
                except Exception as e:
                    self.logger.error(f"规则'{rule.name}'执行失败: {e}")
                    continue

            self.logger.debug("没有满足条件的规则")
            return None

        except Exception as e:
            raise DecisionEngineError(f"决策失败: {str(e)}") from e

    def execute_action(self, action_name: str) -> bool:
        """
        执行动作

        Args:
            action_name: 动作名称

        Returns:
            执行是否成功

        Raises:
            DecisionEngineError: 当动作执行失败时抛出
        """
        try:
            if action_name not in self.actions:
                raise DecisionEngineError(f"未知的动作: {action_name}")

            self.actions[action_name](self.state)
            self.logger.info(f"执行动作: {action_name}")
            return True

        except Exception as e:
            raise DecisionEngineError(f"执行动作失败: {str(e)}") from e

    def analyze_image(self, image: np.ndarray) -> Dict[str, Any]:
        """
        分析图像特征

        Args:
            image: 图像数据

        Returns:
            Dict: 分析结果

        Raises:
            DecisionEngineError: 当分析失败时抛出
        """
        results: Dict[str, Any] = {}

        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 边缘检测
            edges = cv2.Canny(gray, 50, 150)

            # 查找轮廓
            contours, _ = cv2.findContours(
                edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # 分析结果
            results["contours"] = len(contours)
            results["edges"] = float(np.mean(edges))
            results["brightness"] = float(np.mean(gray))

            # 颜色分析
            if len(image.shape) == 3:
                results["color_mean"] = image.mean(axis=(0, 1)).tolist()
                results["color_std"] = image.std(axis=(0, 1)).tolist()

            return results

        except Exception as e:
            raise DecisionEngineError(f"图像分析失败: {str(e)}") from e

    def clear_state(self) -> None:
        """清除当前状态"""
        self.state.clear()
        self.logger.info("状态已清除")

    def clear_rules(self) -> None:
        """清除所有规则"""
        self.rules.clear()
        self.logger.info("规则已清除")

    def clear_actions(self) -> None:
        """清除所有动作"""
        self.actions.clear()
        self.logger.info("动作已清除")

    def get_rule_info(self, rule_name: str) -> Optional[Dict[str, Any]]:
        """
        获取规则信息

        Args:
            rule_name: 规则名称

        Returns:
            规则信息字典
        """
        if rule_name not in self.rules:
            return None

        rule = self.rules[rule_name]
        return {
            "name": rule.name,
            "priority": rule.priority,
            "description": rule.description,
        }

    def get_all_rules_info(self) -> List[Dict[str, Any]]:
        """
        获取所有规则信息

        Returns:
            规则信息列表
        """
        return [
            {
                "name": rule.name,
                "priority": rule.priority,
                "description": rule.description,
            }
            for rule in sorted(
                self.rules.values(), key=lambda x: x.priority, reverse=True
            )
        ]
