"""
宏录制器
实现按键、鼠标和延时的记录功能
"""
from typing import List, Dict, Optional, Any, Tuple
import time
import json
import keyboard
import mouse
from dataclasses import dataclass
from enum import Enum, auto
import logging
import threading
from queue import Queue


class MacroEventType(Enum):
    """宏事件类型"""

    KEY_DOWN = auto()
    KEY_UP = auto()
    MOUSE_DOWN = auto()
    MOUSE_UP = auto()
    MOUSE_MOVE = auto()
    MOUSE_WHEEL = auto()
    DELAY = auto()


@dataclass
class MacroEvent:
    """宏事件"""

    type: MacroEventType
    timestamp: float
    data: Dict[str, Any]


class MacroRecorder:
    """宏录制器"""

    def __init__(self) -> None:
        """初始化宏录制器"""
        self.logger = logging.getLogger("MacroRecorder")
        self.events: List[MacroEvent] = []
        self.recording: bool = False
        self.start_time: Optional[float] = None
        self.counts: Dict[MacroEventType, int] = {}

        # 事件队列和处理线程
        self.event_queue = Queue()
        self.process_thread = threading.Thread(target=self._process_events, daemon=True)
        self.process_thread.start()

        # 按键状态
        self.key_states = {}

        # 鼠标状态
        self.mouse_position = (0, 0)
        self.mouse_buttons = {"left": False, "right": False, "middle": False}

    def start_recording(self) -> None:
        """开始录制"""
        if self.recording:
            return

        self.recording = True
        self.events.clear()
        self.start_time = time.time()
        self.counts.clear()

        # 注册事件处理器
        keyboard.hook(self._on_keyboard_event)
        mouse.hook(self._on_mouse_event)

        self.logger.info("开始录制宏")

    def stop_recording(self) -> List[MacroEvent]:
        """停止录制"""
        if not self.recording:
            return self.events

        # 取消事件处理器
        keyboard.unhook_all()
        mouse.unhook_all()

        # 等待队列处理完成
        while not self.event_queue.empty():
            time.sleep(0.1)

        self.recording = False
        self.logger.info(f"停止录制宏，共记录 {len(self.events)} 个事件")

        return self.events

    def _process_events(self) -> None:
        """处理事件队列"""
        while True:
            try:
                event = self.event_queue.get()
                if event:
                    self._add_event(event)
                self.event_queue.task_done()
            except Exception as e:
                self.logger.error(f"处理事件失败: {e}", exc_info=True)

    def _add_event(self, event: MacroEvent) -> None:
        """添加事件"""
        if not self.recording:
            return

        # 计算相对时间
        event.timestamp -= self.start_time

        # 如果有前一个事件，添加延时
        if self.events:
            last_event = self.events[-1]
            if event.timestamp - last_event.timestamp > 0.01:  # 忽略小于10ms的延时
                delay_event = MacroEvent(
                    type=MacroEventType.DELAY,
                    timestamp=last_event.timestamp,
                    data={"duration": event.timestamp - last_event.timestamp},
                )
                self.events.append(delay_event)

        self.events.append(event)
        self.counts[event.type] = self.counts.get(event.type, 0) + 1

    def _on_keyboard_event(self, event) -> None:
        """键盘事件处理"""
        try:
            if not self.recording:
                return

            event_type = (
                MacroEventType.KEY_DOWN
                if event.event_type == "down"
                else MacroEventType.KEY_UP
            )

            # 检查按键状态变化
            if event.event_type == "down":
                if self.key_states.get(event.name, False):
                    return  # 忽略重复的按下事件
                self.key_states[event.name] = True
            else:
                if not self.key_states.get(event.name, False):
                    return  # 忽略重复的释放事件
                self.key_states[event.name] = False

            macro_event = MacroEvent(
                type=event_type,
                timestamp=time.time(),
                data={
                    "key": event.name,
                    "scan_code": event.scan_code,
                    "modifiers": {
                        "shift": keyboard.is_pressed("shift"),
                        "ctrl": keyboard.is_pressed("ctrl"),
                        "alt": keyboard.is_pressed("alt"),
                    },
                },
            )

            self.event_queue.put(macro_event)

        except Exception as e:
            self.logger.error(f"处理键盘事件失败: {e}", exc_info=True)

    def _on_mouse_event(self, event) -> None:
        """鼠标事件处理"""
        try:
            if not self.recording:
                return

            # 确定事件类型
            if hasattr(event, "button"):
                if event.event_type == "down":
                    event_type = MacroEventType.MOUSE_DOWN
                    self.mouse_buttons[event.button] = True
                else:
                    event_type = MacroEventType.MOUSE_UP
                    self.mouse_buttons[event.button] = False
            elif hasattr(event, "wheel"):
                event_type = MacroEventType.MOUSE_WHEEL
            else:
                event_type = MacroEventType.MOUSE_MOVE

            # 创建事件数据
            event_data = {
                "position": (event.x, event.y),
                "buttons": self.mouse_buttons.copy(),
            }

            # 添加特定事件数据
            if hasattr(event, "button"):
                event_data["button"] = event.button
            elif hasattr(event, "wheel"):
                event_data["wheel_delta"] = event.wheel

            macro_event = MacroEvent(
                type=event_type, timestamp=time.time(), data=event_data
            )

            # 更新鼠标位置
            self.mouse_position = (event.x, event.y)

            self.event_queue.put(macro_event)

        except Exception as e:
            self.logger.error(f"处理鼠标事件失败: {e}", exc_info=True)

    def save_macro(self, filename: str) -> None:
        """保存宏到文件"""
        try:
            macro_data = {
                "version": "1.0",
                "events": [
                    {
                        "type": event.type.name,
                        "timestamp": event.timestamp,
                        "data": event.data,
                    }
                    for event in self.events
                ],
            }

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(macro_data, f, indent=2)

            self.logger.info(f"宏保存到文件: {filename}")

        except Exception as e:
            self.logger.error(f"保存宏失败: {e}", exc_info=True)
            raise

    def load_macro(self, filename: str) -> List[MacroEvent]:
        """从文件加载宏"""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                macro_data = json.load(f)

            if macro_data.get("version") != "1.0":
                raise ValueError("不支持的宏文件版本")

            self.events = [
                MacroEvent(
                    type=MacroEventType[event["type"]],
                    timestamp=event["timestamp"],
                    data=event["data"],
                )
                for event in macro_data["events"]
            ]

            self.logger.info(f"从文件加载宏: {filename}")
            return self.events

        except Exception as e:
            self.logger.error(f"加载宏失败: {e}", exc_info=True)
            raise

    def optimize_macro(self) -> None:
        """优化宏"""
        if not self.events:
            return

        optimized_events = []
        last_event = None

        for event in self.events:
            if last_event is None:
                optimized_events.append(event)
                last_event = event
                continue

            # 合并连续的移动事件
            if (
                event.type == MacroEventType.MOUSE_MOVE
                and last_event.type == MacroEventType.MOUSE_MOVE
                and event.timestamp - last_event.timestamp < 0.05
            ):
                continue

            # 合并短延时
            if (
                event.type == MacroEventType.DELAY
                and last_event.type == MacroEventType.DELAY
            ):
                last_event.data["duration"] += event.data["duration"]
                continue

            optimized_events.append(event)
            last_event = event

        self.events = optimized_events
        self.logger.info(f"优化后的事件数量: {len(self.events)}")

    def get_total_duration(self) -> float:
        """获取宏总时长"""
        if not self.events:
            return 0
        return self.events[-1].timestamp

    def get_event_count(self) -> Dict[MacroEventType, int]:
        """获取各类事件数量"""
        return self.counts
