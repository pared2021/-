"""
宏编辑器
提供宏的编辑、优化和验证功能
"""
from typing import List, Dict, Optional, Any, Tuple
import json
import time
from dataclasses import dataclass
from enum import Enum, auto
import logging

from .macro_recorder import MacroEvent, MacroEventType

# 引入统一的Action体系（用于创建宏动作）
from ..common.action_system import (
    ActionType, MacroAction, ActionSequence, ActionFactory, BaseAction
)


class EditOperation(Enum):
    """编辑操作类型"""

    INSERT = auto()
    DELETE = auto()
    MODIFY = auto()
    MOVE = auto()


@dataclass
class EditAction:
    """编辑动作 - 编辑器内部操作记录"""

    operation: EditOperation
    index: int
    event: Optional[MacroEvent] = None
    old_event: Optional[MacroEvent] = None
    new_index: Optional[int] = None


class MacroEditor:
    """宏编辑器"""

    def __init__(self):
        """初始化宏编辑器"""
        self.logger = logging.getLogger("MacroEditor")
        self.events: List[MacroEvent] = []
        self.undo_stack: List[EditAction] = []
        self.redo_stack: List[EditAction] = []
        self.max_undo = 100

    def load_events(self, events: List[MacroEvent]):
        """加载事件列表"""
        self.events = events.copy()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.logger.info(f"加载了 {len(events)} 个事件")

    def insert_event(self, index: int, event: MacroEvent):
        """插入事件"""
        if index < 0 or index > len(self.events):
            raise ValueError("无效的索引")

        # 调整时间戳
        if index < len(self.events):
            time_diff = self.events[index].timestamp - event.timestamp
            for i in range(index, len(self.events)):
                self.events[i].timestamp += time_diff

        self.events.insert(index, event)

        # 记录操作
        action = EditAction(operation=EditOperation.INSERT, index=index, event=event)
        self._add_undo_action(action)

        self.logger.info(f"在位置 {index} 插入事件")

    def delete_event(self, index: int):
        """删除事件"""
        if index < 0 or index >= len(self.events):
            raise ValueError("无效的索引")

        event = self.events.pop(index)

        # 调整时间戳
        if index < len(self.events):
            time_diff = event.timestamp - (
                self.events[index - 1].timestamp if index > 0 else 0
            )
            for i in range(index, len(self.events)):
                self.events[i].timestamp -= time_diff

        # 记录操作
        action = EditAction(operation=EditOperation.DELETE, index=index, event=event)
        self._add_undo_action(action)

        self.logger.info(f"删除位置 {index} 的事件")

    def modify_event(self, index: int, new_event: MacroEvent):
        """修改事件"""
        if index < 0 or index >= len(self.events):
            raise ValueError("无效的索引")

        old_event = self.events[index]
        self.events[index] = new_event

        # 调整时间戳
        time_diff = new_event.timestamp - old_event.timestamp
        for i in range(index + 1, len(self.events)):
            self.events[i].timestamp += time_diff

        # 记录操作
        action = EditAction(
            operation=EditOperation.MODIFY,
            index=index,
            event=new_event,
            old_event=old_event,
        )
        self._add_undo_action(action)

        self.logger.info(f"修改位置 {index} 的事件")

    def move_event(self, from_index: int, to_index: int):
        """移动事件"""
        if from_index < 0 or from_index >= len(self.events):
            raise ValueError("无效的源索引")
        if to_index < 0 or to_index > len(self.events):
            raise ValueError("无效的目标索引")

        event = self.events.pop(from_index)
        self.events.insert(to_index, event)

        # 记录操作
        action = EditAction(
            operation=EditOperation.MOVE,
            index=from_index,
            new_index=to_index,
            event=event,
        )
        self._add_undo_action(action)

        self.logger.info(f"将事件从位置 {from_index} 移动到 {to_index}")

    def undo(self):
        """撤销操作"""
        if not self.undo_stack:
            return

        action = self.undo_stack.pop()

        if action.operation == EditOperation.INSERT:
            self.events.pop(action.index)
        elif action.operation == EditOperation.DELETE:
            self.events.insert(action.index, action.event)
        elif action.operation == EditOperation.MODIFY:
            self.events[action.index] = action.old_event
        elif action.operation == EditOperation.MOVE:
            event = self.events.pop(action.new_index)
            self.events.insert(action.index, event)

        self.redo_stack.append(action)
        self.logger.info("撤销上一个操作")

    def redo(self):
        """重做操作"""
        if not self.redo_stack:
            return

        action = self.redo_stack.pop()

        if action.operation == EditOperation.INSERT:
            self.events.insert(action.index, action.event)
        elif action.operation == EditOperation.DELETE:
            self.events.pop(action.index)
        elif action.operation == EditOperation.MODIFY:
            self.events[action.index] = action.event
        elif action.operation == EditOperation.MOVE:
            event = self.events.pop(action.index)
            self.events.insert(action.new_index, event)

        self.undo_stack.append(action)
        self.logger.info("重做上一个操作")

    def _add_undo_action(self, action: EditAction):
        """添加撤销动作"""
        self.undo_stack.append(action)
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def optimize(self):
        """优化宏"""
        if not self.events:
            return

        # 合并连续的移动事件
        i = 0
        while i < len(self.events) - 1:
            if (
                self.events[i].type == MacroEventType.MOUSE_MOVE
                and self.events[i + 1].type == MacroEventType.MOUSE_MOVE
            ):
                # 保留最后一个移动事件
                self.events.pop(i)
            else:
                i += 1

        # 合并短延时
        i = 0
        while i < len(self.events) - 1:
            if (
                self.events[i].type == MacroEventType.DELAY
                and self.events[i + 1].type == MacroEventType.DELAY
            ):
                # 合并延时
                self.events[i].data["duration"] += self.events[i + 1].data["duration"]
                self.events.pop(i + 1)
            else:
                i += 1

        # 移除过短的延时
        self.events = [
            event
            for event in self.events
            if event.type != MacroEventType.DELAY or event.data["duration"] >= 0.01
        ]

        self.logger.info(f"优化后的事件数量: {len(self.events)}")

    def validate(self) -> List[str]:
        """验证宏"""
        errors = []

        if not self.events:
            errors.append("宏是空的")
            return errors

        # 检查时间戳顺序
        for i in range(1, len(self.events)):
            if self.events[i].timestamp < self.events[i - 1].timestamp:
                errors.append(f"事件 {i} 的时间戳早于前一个事件")

        # 检查按键配对
        key_stack = {}
        for i, event in enumerate(self.events):
            if event.type == MacroEventType.KEY_DOWN:
                key = event.data["key"]
                if key in key_stack:
                    errors.append(f"事件 {i}: 重复的按键按下 {key}")
                key_stack[key] = i
            elif event.type == MacroEventType.KEY_UP:
                key = event.data["key"]
                if key not in key_stack:
                    errors.append(f"事件 {i}: 未配对的按键释放 {key}")
                key_stack.pop(key, None)

        # 检查未释放的按键
        for key, index in key_stack.items():
            errors.append(f"按键 {key} 在事件 {index} 按下后未释放")

        # 检查鼠标按键配对
        mouse_stack = {}
        for i, event in enumerate(self.events):
            if event.type == MacroEventType.MOUSE_DOWN:
                button = event.data["button"]
                if button in mouse_stack:
                    errors.append(f"事件 {i}: 重复的鼠标按下 {button}")
                mouse_stack[button] = i
            elif event.type == MacroEventType.MOUSE_UP:
                button = event.data["button"]
                if button not in mouse_stack:
                    errors.append(f"事件 {i}: 未配对的鼠标释放 {button}")
                mouse_stack.pop(button, None)

        # 检查未释放的鼠标按键
        for button, index in mouse_stack.items():
            errors.append(f"鼠标按键 {button} 在事件 {index} 按下后未释放")

        return errors

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.events:
            return {
                "total_events": 0,
                "duration": 0,
                "event_types": {},
                "key_counts": {},
                "mouse_counts": {},
            }

        stats = {
            "total_events": len(self.events),
            "duration": self.events[-1].timestamp,
            "event_types": {},
            "key_counts": {},
            "mouse_counts": {},
        }

        # 统计事件类型
        for event in self.events:
            stats["event_types"][event.type.name] = (
                stats["event_types"].get(event.type.name, 0) + 1
            )

            # 统计按键
            if event.type in (MacroEventType.KEY_DOWN, MacroEventType.KEY_UP):
                key = event.data["key"]
                stats["key_counts"][key] = stats["key_counts"].get(key, 0) + 1

            # 统计鼠标操作
            if event.type in (MacroEventType.MOUSE_DOWN, MacroEventType.MOUSE_UP):
                button = event.data["button"]
                stats["mouse_counts"][button] = stats["mouse_counts"].get(button, 0) + 1

        return stats
    
    # === 统一Action体系支持 ===
    
    def create_macro_action(self, name: str, operation: str, **kwargs) -> MacroAction:
        """创建宏动作 - 使用统一Action体系
        
        Args:
            name: 动作名称
            operation: 操作类型
            **kwargs: 其他参数
            
        Returns:
            MacroAction: 创建的宏动作
        """
        return MacroAction(
            name=name,
            type=ActionType.MACRO,
            operation=operation,
            target=kwargs.get("target"),
            old_value=kwargs.get("old_value"),
            new_value=kwargs.get("new_value"),
            params=kwargs
        )
    
    def events_to_macro_actions(self) -> List[MacroAction]:
        """将事件列表转换为宏动作列表
        
        Returns:
            List[MacroAction]: 宏动作列表
        """
        actions = []
        for i, event in enumerate(self.events):
            action = MacroAction(
                name=f"macro_event_{i}",
                type=ActionType.MACRO,
                operation="execute_event",
                params={
                    "event_type": event.type.name,
                    "event_data": event.data,
                    "timestamp": event.timestamp
                }
            )
            actions.append(action)
        return actions
    
    def create_action_sequence(self, name: str = "MacroSequence") -> ActionSequence:
        """创建动作序列
        
        Args:
            name: 序列名称
            
        Returns:
            ActionSequence: 动作序列
        """
        sequence = ActionSequence(name)
        sequence.add_actions(self.events_to_macro_actions())
        return sequence
