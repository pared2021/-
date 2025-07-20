"""
输入控制器
实现键盘和鼠标的模拟输入
"""
import logging
from typing import Optional, Tuple

import pyautogui
import keyboard


class InputError(Exception):
    """输入控制相关错误"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class InputController:
    """输入控制器类"""

    def __init__(self):
        self.logger = logging.getLogger("InputController")

    def move_mouse(self, x: int, y: int, duration: float = 0.0):
        """
        移动鼠标到指定位置

        Args:
            x: 目标X坐标
            y: 目标Y坐标
            duration: 移动持续时间，0表示立即移动

        Raises:
            InputError: 当鼠标移动失败时抛出
        """
        try:
            pyautogui.moveTo(x, y, duration=duration)
        except Exception as e:
            error_msg = f"移动鼠标失败: {str(e)}"
            self.logger.error(error_msg)
            raise InputError(error_msg) from e

    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: str = "left",
        clicks: int = 1,
        interval: float = 0.0,
    ):
        """
        点击鼠标

        Args:
            x: 点击位置X坐标，None表示当前位置
            y: 点击位置Y坐标，None表示当前位置
            button: 鼠标按键，"left"或"right"
            clicks: 点击次数
            interval: 点击间隔时间

        Raises:
            InputError: 当鼠标点击失败时抛出
        """
        try:
            pyautogui.click(x=x, y=y, button=button, clicks=clicks, interval=interval)
        except Exception as e:
            error_msg = f"点击鼠标失败: {str(e)}"
            self.logger.error(error_msg)
            raise InputError(error_msg) from e

    def press_key(self, key: str, duration: float = 0.0):
        """
        按下键盘按键

        Args:
            key: 按键名称
            duration: 按住时间，0表示立即释放

        Raises:
            InputError: 当按键操作失败时抛出
        """
        try:
            keyboard.press(key)
            if duration > 0:
                pyautogui.sleep(duration)
            keyboard.release(key)
        except Exception as e:
            error_msg = f"按键操作失败: {str(e)}"
            self.logger.error(error_msg)
            raise InputError(error_msg) from e

    def type_string(self, text: str, interval: float = 0.0):
        """
        输入文本

        Args:
            text: 要输入的文本
            interval: 字符间隔时间

        Raises:
            InputError: 当文本输入失败时抛出
        """
        try:
            pyautogui.write(text, interval=interval)
        except Exception as e:
            error_msg = f"文本输入失败: {str(e)}"
            self.logger.error(error_msg)
            raise InputError(error_msg) from e

    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None):
        """
        滚动鼠标滚轮

        Args:
            clicks: 滚动量，正数向上滚动，负数向下滚动
            x: 滚动位置X坐标，None表示当前位置
            y: 滚动位置Y坐标，None表示当前位置

        Raises:
            InputError: 当滚动鼠标失败时抛出
        """
        try:
            pyautogui.scroll(clicks, x=x, y=y)
        except Exception as e:
            error_msg = f"滚动鼠标失败: {str(e)}"
            self.logger.error(error_msg)
            raise InputError(error_msg) from e

    def get_mouse_position(self) -> Tuple[int, int]:
        """
        获取当前鼠标位置

        Returns:
            鼠标位置坐标元组(x, y)

        Raises:
            InputError: 当获取鼠标位置失败时抛出
        """
        try:
            return pyautogui.position()
        except Exception as e:
            error_msg = f"获取鼠标位置失败: {str(e)}"
            self.logger.error(error_msg)
            raise InputError(error_msg) from e
