"""
状态机核心模块
实现状态转换、条件判断和动作执行
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import logging
import time
import re
from enum import Enum

# 使用统一的Action体系
from src.common.action_system import (
    ActionType, AutomationAction, ActionSequence, ActionFactory, BaseAction
)


class ConditionType(Enum):
    EXIST = "exist"
    NOT_EXIST = "not_exist"
    TIME_RANGE = "time_range"
    NUMERIC = "numeric"
    CUSTOM = "custom"


@dataclass
class Condition:
    """条件定义"""

    type: ConditionType
    target: str
    params: Dict

    @staticmethod
    def parse(condition_str: str) -> "Condition":
        """解析条件字符串"""
        if condition_str.startswith("!"):
            return Condition(
                type=ConditionType.NOT_EXIST, target=condition_str[1:], params={}
            )
        elif condition_str.startswith("[") and condition_str.endswith("]"):
            return Condition(
                type=ConditionType.EXIST, target=condition_str[1:-1], params={}
            )
        elif "{" in condition_str and "}" in condition_str:
            # 解析时间范围
            target = condition_str[: condition_str.find("{")]
            range_str = condition_str[
                condition_str.find("{") + 1 : condition_str.find("}")
            ]
            min_time, max_time = map(float, range_str.split(","))
            return Condition(
                type=ConditionType.TIME_RANGE,
                target=target,
                params={"min": min_time, "max": max_time},
            )
        else:
            # 尝试解析数值条件
            match = re.match(r"(\w+)(>=|<=|>|<|==)(\d+)", condition_str)
            if match:
                target, op, value = match.groups()
                return Condition(
                    type=ConditionType.NUMERIC,
                    target=target,
                    params={"op": op, "value": float(value)},
                )

            # 自定义条件
            return Condition(type=ConditionType.CUSTOM, target=condition_str, params={})


# 使用统一的Action体系
# Action类已从common.action_system导入


@dataclass
class State:
    """状态定义"""

    name: str
    priority: int
    conditions: List[Condition]
    actions: List[BaseAction]  # 使用统一的Action基类
    next_states: List[str]


class StateMachine:
    def __init__(self, config: Dict):
        self.config = config
        self.current_state: Optional[State] = None
        self.states: Dict[str, State] = {}
        self.variables: Dict[str, Any] = {}
        self.custom_conditions: Dict[str, Callable] = {}
        self.logger = logging.getLogger("StateMachine")
        self.state_start_time = 0.0

        # 加载状态定义
        self._load_states()

    def _load_states(self):
        """加载状态定义"""
        templates = self.config["state_templates"]
        for name, template in templates.items():
            # 解析条件
            conditions = []
            for cond_str in template.get("conditions", []):
                try:
                    conditions.append(Condition.parse(cond_str))
                except Exception as e:
                    self.logger.error(f"解析条件失败 {cond_str}: {e}")
                    continue

            # 解析动作
            actions = []
            for action in template.get("actions", []):
                try:
                    # 创建统一的Action对象
                    action_type = ActionType(action["type"]) if action["type"] in [e.value for e in ActionType] else ActionType.CLICK
                    automation_action = AutomationAction(
                        name=action.get("name", f"{action['type']}_action"),
                        type=action_type,
                        params=action.get("params", {}),
                        retry_count=action.get("repeat", 1),
                        delay=action.get("delay", 0.0),
                    )
                    actions.append(automation_action)
                except Exception as e:
                    self.logger.error(f"解析动作失败 {action}: {e}")
                    continue

            # 创建状态
            self.states[name] = State(
                name=name,
                priority=template.get("priority", 50),
                conditions=conditions,
                actions=actions,
                next_states=template.get("next_states", []),
            )

    def register_custom_condition(self, name: str, handler: Callable) -> None:
        """注册自定义条件处理器"""
        self.custom_conditions[name] = handler

    def set_variable(self, name: str, value: Any) -> None:
        """设置变量值"""
        self.variables[name] = value

    def get_variable(self, name: str) -> Any:
        """获取变量值"""
        return self.variables.get(name)

    def check_condition(self, condition: Condition) -> bool:
        """检查条件是否满足"""
        try:
            if condition.type == ConditionType.EXIST:
                return condition.target in self.variables

            elif condition.type == ConditionType.NOT_EXIST:
                return condition.target not in self.variables

            elif condition.type == ConditionType.TIME_RANGE:
                if self.state_start_time == 0:
                    return False
                elapsed = time.time() - self.state_start_time
                return condition.params["min"] <= elapsed <= condition.params["max"]

            elif condition.type == ConditionType.NUMERIC:
                if condition.target not in self.variables:
                    return False
                value = float(self.variables[condition.target])
                op = condition.params["op"]
                target = condition.params["value"]

                if op == ">=":
                    return value >= target
                elif op == "<=":
                    return value <= target
                elif op == ">":
                    return value > target
                elif op == "<":
                    return value < target
                elif op == "==":
                    return value == target

            elif condition.type == ConditionType.CUSTOM:
                if condition.target in self.custom_conditions:
                    return self.custom_conditions[condition.target](self.variables)

            return False

        except Exception as e:
            self.logger.error(f"检查条件失败 {condition}: {e}")
            return False

    def check_conditions(self, conditions: List[Condition]) -> bool:
        """检查条件组是否满足"""
        return all(self.check_condition(c) for c in conditions)

    def get_next_state(self) -> Optional[State]:
        """获取下一个状态"""
        candidates = []

        # 检查当前状态的后继状态
        if self.current_state:
            for name in self.current_state.next_states:
                state = self.states.get(name)
                if state and self.check_conditions(state.conditions):
                    candidates.append(state)

        # 检查所有可能的状态
        for state in self.states.values():
            if state.priority > (
                self.current_state.priority if self.current_state else 0
            ):
                if self.check_conditions(state.conditions):
                    candidates.append(state)

        # 按优先级排序
        candidates.sort(key=lambda s: s.priority, reverse=True)
        return candidates[0] if candidates else None

    def transition(self, new_state: Optional[State]) -> bool:
        """执行状态转换"""
        if new_state is None:
            return False

        if new_state != self.current_state:
            self.logger.info(
                f"状态转换: {self.current_state.name if self.current_state else 'None'} -> {new_state.name}"
            )
            self.current_state = new_state
            self.state_start_time = time.time()
            return True

        return False

    def get_current_actions(self) -> List[BaseAction]:
        """获取当前状态的动作列表"""
        if self.current_state:
            return self.current_state.actions
        return []

    def clear_state(self) -> None:
        """清除当前状态"""
        self.current_state = None
        self.state_start_time = 0

    def reset(self) -> None:
        """重置状态机"""
        self.clear_state()
        self.variables.clear()
