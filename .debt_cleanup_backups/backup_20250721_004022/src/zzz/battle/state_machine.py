"""
战斗状态机
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Tuple
import yaml
import re
import time


@dataclass
class Trigger:
    """触发器数据类"""

    condition: str  # 触发条件
    action: str  # 触发动作
    priority: int  # 优先级


@dataclass
class State:
    """状态数据类"""

    name: str  # 状态名称
    operations: List[str]  # 操作序列
    transitions: Dict[str, str]  # 状态转换条件
    timeout: Optional[float]  # 超时时间


class BattleStateMachine:
    def __init__(self):
        self.states: Dict[str, State] = {}
        self.triggers: List[Trigger] = []
        self.current_state: Optional[State] = None
        self.state_enter_time: float = 0

    def load_config(self, config_path: str):
        """加载YAML配置"""
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # 解析状态
        for state_name, state_data in config.get("states", {}).items():
            state = State(
                name=state_name,
                operations=state_data.get("operations", []),
                transitions=state_data.get("transitions", {}),
                timeout=state_data.get("timeout"),
            )
            self.states[state_name] = state

        # 解析触发器
        for trigger_data in config.get("triggers", []):
            trigger = Trigger(
                condition=trigger_data["condition"],
                action=trigger_data["action"],
                priority=trigger_data.get("priority", 0),
            )
            self.triggers.append(trigger)

        # 排序触发器（按优先级）
        self.triggers.sort(key=lambda x: x.priority, reverse=True)

    def evaluate_condition(self, condition: str, game_state: Dict) -> bool:
        """
        评估条件表达式

        支持的操作符：
        - 状态存在性判断：[状态名]
        - 数值区间：{min,max}
        - 时间判断：[状态名,start,duration]
        - 逻辑运算符：&(与)、|(或)、!(非)
        """
        # 处理逻辑运算符
        if "&" in condition:
            return all(
                self.evaluate_condition(c.strip(), game_state)
                for c in condition.split("&")
            )
        if "|" in condition:
            return any(
                self.evaluate_condition(c.strip(), game_state)
                for c in condition.split("|")
            )
        if condition.startswith("!"):
            return not self.evaluate_condition(condition[1:].strip(), game_state)

        # 状态存在性判断
        if condition.startswith("[") and condition.endswith("]"):
            state_name = condition[1:-1]
            if "," in state_name:  # 时间判断
                state, start, duration = state_name.split(",")
                if state not in game_state:
                    return False
                state_time = game_state.get(f"{state}_time", 0)
                return time.time() - state_time >= float(
                    start
                ) and time.time() - state_time < float(start) + float(duration)
            return state_name in game_state

        # 数值区间判断
        if condition.startswith("{") and condition.endswith("}"):
            var_name, range_str = condition[1:-1].split(":")
            min_val, max_val = map(float, range_str.split(","))
            return var_name in game_state and min_val <= game_state[var_name] <= max_val

        return False

    def update(self, game_state: Dict) -> Optional[str]:
        """
        更新状态机

        Returns:
            Optional[str]: 需要执行的操作
        """
        # 检查触发器
        for trigger in self.triggers:
            if self.evaluate_condition(trigger.condition, game_state):
                return trigger.action

        if not self.current_state:
            # 初始化默认状态
            self.current_state = next(iter(self.states.values()), None)
            self.state_enter_time = time.time()
            return None

        # 检查超时
        if (
            self.current_state.timeout
            and time.time() - self.state_enter_time > self.current_state.timeout
        ):
            # 超时转换到下一个状态
            next_state = next(iter(self.states.values()), None)
            if next_state:
                self.current_state = next_state
                self.state_enter_time = time.time()
                return next_state.operations[0] if next_state.operations else None

        # 检查状态转换
        for condition, next_state_name in self.current_state.transitions.items():
            if self.evaluate_condition(condition, game_state):
                next_state = self.states.get(next_state_name)
                if next_state:
                    self.current_state = next_state
                    self.state_enter_time = time.time()
                    return next_state.operations[0] if next_state.operations else None

        # 执行当前状态的操作序列
        current_time = time.time() - self.state_enter_time
        operation_index = int(current_time / 0.1) % len(self.current_state.operations)
        return self.current_state.operations[operation_index]
