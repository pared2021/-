"""
宏播放器
实现宏的回放功能，支持速度调节和循环播放
"""
from typing import List, Dict, Optional, Any
import time
import keyboard
import mouse
import threading
import logging
from queue import Queue
from dataclasses import dataclass
from enum import Enum, auto

from .macro_recorder import MacroEvent, MacroEventType


class PlaybackStatus(Enum):
    """播放状态"""

    STOPPED = auto()
    PLAYING = auto()
    PAUSED = auto()


@dataclass
class PlaybackOptions:
    """播放选项"""

    speed: float = 1.0  # 播放速度倍率
    loop_count: int = 1  # 循环次数，-1表示无限循环
    random_delay: float = 0.0  # 随机延迟范围(秒)
    skip_delays: bool = False  # 是否跳过延迟


class MacroPlayer:
    """宏播放器"""

    def __init__(self):
        """初始化宏播放器"""
        self.logger = logging.getLogger("MacroPlayer")
        self.events: List[MacroEvent] = []
        self.status = PlaybackStatus.STOPPED
        self.current_loop = 0
        self.options = PlaybackOptions()
        self.start_time = None  # <--- Added this line

        # 播放线程
        self.play_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        # 事件处理器
        self.event_handlers = {
            MacroEventType.KEY_DOWN: self._handle_key_down,
            MacroEventType.KEY_UP: self._handle_key_up,
            MacroEventType.MOUSE_DOWN: self._handle_mouse_down,
            MacroEventType.MOUSE_UP: self._handle_mouse_up,
            MacroEventType.MOUSE_MOVE: self._handle_mouse_move,
            MacroEventType.MOUSE_WHEEL: self._handle_mouse_wheel,
            MacroEventType.DELAY: self._handle_delay,
        }

    def load_events(self, events: List[MacroEvent]):
        """加载事件列表"""
        if self.status != PlaybackStatus.STOPPED:
            raise RuntimeError("播放器正在运行")

        self.events = events.copy()
        self.logger.info(f"加载了 {len(events)} 个事件")

    def set_options(self, options: PlaybackOptions):
        """设置播放选项"""
        self.options = options
        self.logger.info(f"更新播放选项: {options}")

    def start(self):
        """开始播放"""
        if not self.events:
            raise ValueError("没有要播放的事件")

        if self.status != PlaybackStatus.STOPPED:
            raise RuntimeError("播放器已经在运行")

        self.status = PlaybackStatus.PLAYING
        self.current_loop = 0
        self.stop_event.clear()
        self.start_time = time.time()  # <--- Added this line

        self.play_thread = threading.Thread(target=self._playback_loop)
        self.play_thread.start()

        self.logger.info("开始播放宏")

    def pause(self):
        """暂停播放"""
        if self.status != PlaybackStatus.PLAYING:
            return

        self.status = PlaybackStatus.PAUSED
        self.logger.info("暂停播放")

    def resume(self):
        """恢复播放"""
        if self.status != PlaybackStatus.PAUSED:
            return

        self.status = PlaybackStatus.PLAYING
        self.logger.info("恢复播放")

    def stop(self):
        """停止播放"""
        if self.status == PlaybackStatus.STOPPED:
            return

        self.stop_event.set()
        if self.play_thread:
            self.play_thread.join()

        self.status = PlaybackStatus.STOPPED
        self.logger.info("停止播放")

    def _playback_loop(self):
        """播放循环"""
        try:
            while (
                self.options.loop_count == -1
                or self.current_loop < self.options.loop_count
            ) and not self.stop_event.is_set():
                self.logger.info("开始第 %d 次循环", self.current_loop + 1)
                self._play_events()

                if self.stop_event.is_set():
                    break

                self.current_loop += 1

        except Exception as e:
            self.logger.error("播放过程出错: %s", e, exc_info=True)
        finally:
            self.status = PlaybackStatus.STOPPED

    def _play_events(self):
        """播放事件序列"""
        if not self.events:
            return

        start_time = self.start_time  # <--- Changed this line
        last_event_time = self.events[0].timestamp

        for event in self.events:
            # 检查是否需要停止
            if self.stop_event.is_set():
                break

            # 处理暂停
            while self.status == PlaybackStatus.PAUSED:
                if self.stop_event.is_set():
                    return
                time.sleep(0.1)

            # 计算延时
            if not self.options.skip_delays:
                delay = (event.timestamp - last_event_time) / self.options.speed
                if delay > 0:
                    # 添加随机延迟
                    if self.options.random_delay > 0:
                        import random

                        delay += random.uniform(0, self.options.random_delay)
                    time.sleep(delay)

            # 执行事件
            try:
                handler = self.event_handlers.get(event.type)
                if handler:
                    handler(event.data)
            except Exception as e:
                self.logger.error("事件执行失败: %s", e, exc_info=True)

            last_event_time = event.timestamp

    def _handle_key_down(self, data: Dict):
        """处理按键按下"""
        try:
            key = data["key"]
            keyboard.press(key)
        except Exception as e:
            self.logger.error("按键按下失败: %s", e, exc_info=True)

    def _handle_key_up(self, data: Dict):
        """处理按键释放"""
        try:
            key = data["key"]
            keyboard.release(key)
        except Exception as e:
            self.logger.error("按键释放失败: %s", e, exc_info=True)

    def _handle_mouse_down(self, data: Dict):
        """处理鼠标按下"""
        try:
            button = data["button"]
            mouse.press(button=button)
        except Exception as e:
            self.logger.error("鼠标按下失败: %s", e, exc_info=True)

    def _handle_mouse_up(self, data: Dict):
        """处理鼠标释放"""
        try:
            button = data["button"]
            mouse.release(button=button)
        except Exception as e:
            self.logger.error("鼠标释放失败: %s", e, exc_info=True)

    def _handle_mouse_move(self, data: Dict):
        """处理鼠标移动"""
        try:
            x, y = data["position"]
            mouse.move(x, y)
        except Exception as e:
            self.logger.error("鼠标移动失败: %s", e, exc_info=True)

    def _handle_mouse_wheel(self, data: Dict):
        """处理鼠标滚轮"""
        try:
            delta = data["wheel_delta"]
            mouse.wheel(delta)
        except Exception as e:
            self.logger.error("鼠标滚轮失败: %s", e, exc_info=True)

    def _handle_delay(self, data: Dict):
        """处理延时"""
        if not self.options.skip_delays:
            try:
                duration = data["duration"] / self.options.speed
                if duration > 0:
                    time.sleep(duration)
            except Exception as e:
                self.logger.error("延时执行失败: %s", e, exc_info=True)

    def get_progress(self) -> Dict[str, Any]:
        """获取播放进度信息"""
        if not self.events or self.status == PlaybackStatus.STOPPED:
            return {
                "status": self.status.name,
                "progress": 0,
                "current_loop": 0,
                "total_loops": self.options.loop_count,
            }

        total_duration = self.events[-1].timestamp
        current_time = time.time()

        return {
            "status": self.status.name,
            "progress": min(1.0, (current_time - self.start_time) / total_duration),
            "current_loop": self.current_loop + 1,
            "total_loops": self.options.loop_count,
        }
