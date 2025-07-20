"""
动作执行器模块，负责执行各种自动化操作。
"""
import logging
import time
from typing import List, Optional, Dict, Any

import keyboard
import pyautogui
import win32con
import win32gui


class ActionExecutorError(Exception):
    """动作执行器相关错误"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ActionExecutor:
    """
    动作执行器类，负责执行各种自动化操作。
    提供了一系列功能，包括：
    - 鼠标操作（点击、移动、拖拽）
    - 键盘操作（按键、组合键）
    - 窗口操作（激活、最大化、最小化）
    - 屏幕操作（颜色检测、截图）
    """

    def __init__(self, window_title: str) -> None:
        """初始化动作执行器。

        Args:
            window_title: 目标窗口标题

        Raises:
            ValueError: 当窗口标题为空时抛出
        """
        if not window_title:
            raise ValueError("Window title cannot be empty")

        self.window_title = window_title
        self.window_handle: Optional[int] = None
        self.logger = logging.getLogger(__name__)
        self.emergency_stop = False

        # 配置PyAutoGUI安全设置
        pyautogui.PAUSE = 0.1  # 操作间隔时间
        pyautogui.FAILSAFE = True  # 启用故障保护

        # 设置紧急停止热键
        keyboard.on_press_key("esc", self._emergency_stop_handler)

    def _emergency_stop_handler(self, _) -> None:
        """紧急停止处理函数"""
        self.emergency_stop = True
        self.logger.warning("检测到紧急停止信号")

    def find_window(self) -> Optional[int]:
        """
        查找窗口句柄。

        Returns:
            Optional[int]: 窗口句柄，如果未找到则返回None

        Raises:
            ActionExecutorError: 当查找窗口失败时抛出
        """
        if not self.window_title:
            raise ValueError("Window title cannot be empty")

        try:
            handle = win32gui.FindWindow(None, self.window_title)
            if handle != 0:
                self.window_handle = handle
                return handle
            return None
        except Exception as e:
            error_msg = f"查找窗口失败: {str(e)}"
            self.logger.error(error_msg)
            raise ActionExecutorError(error_msg) from e

    def _ensure_window_active(self) -> bool:
        """
        确保窗口处于活动状态。

        Returns:
            bool: 是否成功激活窗口

        Raises:
            ActionExecutorError: 当窗口激活失败时抛出
        """
        if self.window_handle is None:
            handle = self.find_window()
            if handle is None:
                raise ActionExecutorError("Window not found")
            self.window_handle = handle

        try:
            # 检查紧急停止信号
            if self.emergency_stop:
                raise ActionExecutorError("Emergency stop triggered")

            # 检查窗口是否最小化
            placement = win32gui.GetWindowPlacement(self.window_handle)
            if placement[1] == win32con.SW_SHOWMINIMIZED:
                win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)

            # 激活窗口
            win32gui.SetForegroundWindow(self.window_handle)
            return True
        except ActionExecutorError:
            raise
        except Exception as e:
            error_msg = f"激活窗口失败: {str(e)}"
            self.logger.error(error_msg)
            raise ActionExecutorError(error_msg) from e

    def execute_action(self, action_type: str, params: Dict[str, Any]) -> bool:
        """
        执行动作。

        Args:
            action_type: 动作类型
            params: 动作参数

        Returns:
            bool: 是否执行成功

        Raises:
            ValueError: 参数无效
            ActionExecutorError: 执行失败
        """
        if not action_type:
            raise ValueError("Action type cannot be empty")

        # 检查紧急停止信号
        if self.emergency_stop:
            raise ActionExecutorError("Emergency stop triggered")

        if not self._ensure_window_active():
            raise ActionExecutorError("Failed to activate window")

        # 处理延迟参数
        delay = params.get("delay", 0)
        if not isinstance(delay, (int, float)) or delay < 0:
            raise ValueError("Invalid delay parameter")

        # 处理重试参数
        retry_count = params.get("retry_count", 0)
        retry_interval = params.get("retry_interval", 1)
        if not isinstance(retry_count, int) or retry_count < 0:
            raise ValueError("Invalid retry_count parameter")
        if not isinstance(retry_interval, (int, float)) or retry_interval < 0:
            raise ValueError("Invalid retry_interval parameter")

        # 执行动作
        for attempt in range(retry_count + 1):
            try:
                if self.emergency_stop:
                    raise ActionExecutorError("Emergency stop triggered")

                if action_type == "click":
                    self._handle_click(params)
                elif action_type == "double_click":
                    self._handle_double_click(params)
                elif action_type == "right_click":
                    self._handle_right_click(params)
                elif action_type == "move":
                    self._handle_move(params)
                elif action_type == "drag":
                    self._handle_drag(params)
                elif action_type == "key":
                    self._handle_key(params)
                elif action_type == "hotkey":
                    self._handle_hotkey(params)
                elif action_type == "text":
                    self._handle_text(params)
                elif action_type == "window":
                    self._handle_window(params)
                elif action_type == "scroll":
                    self._handle_scroll(params)
                else:
                    raise ValueError(f"Unknown action type: {action_type}")

                if delay > 0:
                    time.sleep(delay)
                return True

            except Exception as e:
                self.logger.error(
                    f"Action execution failed (attempt {attempt + 1}/{retry_count + 1}): {str(e)}"
                )
                if attempt < retry_count:
                    time.sleep(retry_interval)
                else:
                    if isinstance(e, (ValueError, ActionExecutorError)):
                        raise
                    raise ActionExecutorError(
                        f"Action execution failed after {retry_count + 1} attempts: {str(e)}"
                    ) from e

    def _handle_click(self, params: Dict[str, Any]) -> None:
        """处理点击动作"""
        x = params.get("x", 0)
        y = params.get("y", 0)
        if x < 0 or y < 0:
            raise ValueError("Coordinates cannot be negative")
        pyautogui.click(x=x, y=y)

    def _handle_double_click(self, params: Dict[str, Any]) -> None:
        """处理双击动作"""
        x = params.get("x", 0)
        y = params.get("y", 0)
        if x < 0 or y < 0:
            raise ValueError("Coordinates cannot be negative")
        pyautogui.doubleClick(x=x, y=y)

    def _handle_right_click(self, params: Dict[str, Any]) -> None:
        """处理右键点击动作"""
        x = params.get("x", 0)
        y = params.get("y", 0)
        if x < 0 or y < 0:
            raise ValueError("Coordinates cannot be negative")
        pyautogui.rightClick(x=x, y=y)

    def _handle_move(self, params: Dict[str, Any]) -> None:
        """处理移动动作"""
        x = params.get("x", 0)
        y = params.get("y", 0)
        if x < 0 or y < 0:
            raise ValueError("Coordinates cannot be negative")
        duration = params.get("duration", 0)
        pyautogui.moveTo(x=x, y=y, duration=duration)

    def _handle_drag(self, params: Dict[str, Any]) -> None:
        """处理拖动动作"""
        start_x = params.get("start_x", 0)
        start_y = params.get("start_y", 0)
        end_x = params.get("end_x", 0)
        end_y = params.get("end_y", 0)

        if start_x < 0 or start_y < 0 or end_x < 0 or end_y < 0:
            raise ValueError("Coordinates cannot be negative")

        if start_x == end_x and start_y == end_y:
            raise ValueError("Start and end positions cannot be the same")

        duration = params.get("duration", 0)
        pyautogui.dragTo(x=end_x, y=end_y, duration=duration)

    def _handle_key(self, params: Dict[str, Any]) -> None:
        """处理按键动作"""
        key = params.get("key")
        if not key:
            raise ValueError("Key parameter is required")
        pyautogui.press(key)

    def _handle_hotkey(self, params: Dict[str, Any]) -> None:
        """处理热键动作"""
        keys = params.get("keys", [])
        if not keys or not isinstance(keys, list):
            raise ValueError("Invalid keys parameter")
        pyautogui.hotkey(*keys)

    def _handle_text(self, params: Dict[str, Any]) -> None:
        """处理文本输入动作"""
        text = params.get("text")
        if not text:
            raise ValueError("Text parameter is required")
        pyautogui.write(text)

    def _handle_window(self, params: Dict[str, Any]) -> None:
        """处理窗口操作"""
        action = params.get("action")
        if not action:
            raise ValueError("Window action parameter is required")

        if action == "maximize":
            win32gui.ShowWindow(self.window_handle, win32con.SW_MAXIMIZE)
        elif action == "minimize":
            win32gui.ShowWindow(self.window_handle, win32con.SW_MINIMIZE)
        elif action == "restore":
            win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
        elif action == "close":
            win32gui.PostMessage(self.window_handle, win32con.WM_CLOSE, 0, 0)
        else:
            raise ValueError(f"Unknown window action: {action}")

    def _handle_scroll(self, params: Dict[str, Any]) -> None:
        """处理滚动动作"""
        clicks = params.get("clicks", 0)
        pyautogui.scroll(clicks)

    def get_pixel_color(self, x: int, y: int) -> Any:
        """
        获取指定位置的像素颜色。

        Args:
            x: X坐标
            y: Y坐标

        Returns:
            Any: RGB颜色值

        Raises:
            ValueError: 坐标无效
        """
        if x < 0 or y < 0:
            raise ValueError("Coordinates cannot be negative")
        return pyautogui.pixel(x, y)

    def search_color(self, color: Any, region: Optional[Any] = None) -> Optional[Any]:
        """
        在屏幕上搜索指定颜色。

        Args:
            color: RGB颜色值
            region: 搜索区域 (x, y, width, height)

        Returns:
            Optional[Any]: 找到的位置，未找到则返回None

        Raises:
            ValueError: 参数无效
        """
        if not all(0 <= c <= 255 for c in color):
            raise ValueError("Invalid color values")

        if region and (
            region[0] < 0 or region[1] < 0 or region[2] <= 0 or region[3] <= 0
        ):
            raise ValueError("Invalid region parameters")

        try:
            pos = (
                pyautogui.pixelMatchesColor(region[0], region[1], color)
                if region
                else None
            )
            return (region[0], region[1]) if pos else None
        except Exception:
            return None

    def activate_window(self, window_title: str) -> bool:
        """
        激活指定窗口

        Args:
            window_title: 窗口标题

        Returns:
            bool: 是否成功

        Raises:
            ActionExecutorError: 激活窗口失败时抛出
        """
        try:
            # 查找窗口句柄
            hwnd = win32gui.FindWindow(None, window_title)
            if not hwnd:
                raise ActionExecutorError(f"未找到窗口: {window_title}")

            # 保存窗口句柄
            self.window_handle = hwnd

            # 激活窗口
            if win32gui.IsIconic(hwnd):  # 如果窗口最小化
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # 恢复窗口
            win32gui.SetForegroundWindow(hwnd)  # 将窗口置于前台

            return True

        except Exception as e:
            raise ActionExecutorError(f"激活窗口失败: {str(e)}") from e

    def click(
        self,
        x: int,
        y: int,
        button: str = "left",
        clicks: int = 1,
        interval: float = 0.0,
    ) -> None:
        """
        点击指定位置

        Args:
            x: X坐标
            y: Y坐标
            button: 鼠标按键，可选值: "left", "right", "middle"
            clicks: 点击次数
            interval: 点击间隔时间(秒)

        Raises:
            ActionExecutorError: 点击失败时抛出
        """
        try:
            # 移动鼠标
            pyautogui.moveTo(x, y)

            # 执行点击
            pyautogui.click(x=x, y=y, button=button, clicks=clicks, interval=interval)

        except Exception as e:
            raise ActionExecutorError(f"点击失败: {str(e)}") from e

    def double_click(self, x: int, y: int, button: str = "left") -> None:
        """
        双击指定位置

        Args:
            x: X坐标
            y: Y坐标
            button: 鼠标按键，可选值: "left", "right", "middle"

        Raises:
            ActionExecutorError: 双击失败时抛出
        """
        try:
            self.click(x, y, button, clicks=2)

        except Exception as e:
            raise ActionExecutorError(f"双击失败: {str(e)}") from e

    def right_click(self, x: int, y: int) -> None:
        """
        右键点击指定位置

        Args:
            x: X坐标
            y: Y坐标

        Raises:
            ActionExecutorError: 右键点击失败时抛出
        """
        try:
            self.click(x, y, button="right")

        except Exception as e:
            raise ActionExecutorError(f"右键点击失败: {str(e)}") from e

    def drag(
        self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5
    ) -> None:
        """
        拖拽操作

        Args:
            start_x: 起始X坐标
            start_y: 起始Y坐标
            end_x: 结束X坐标
            end_y: 结束Y坐标
            duration: 拖拽持续时间(秒)

        Raises:
            ActionExecutorError: 拖拽失败时抛出
        """
        try:
            # 移动到起始位置
            pyautogui.moveTo(start_x, start_y)

            # 执行拖拽
            pyautogui.dragTo(end_x, end_y, duration=duration)

        except Exception as e:
            raise ActionExecutorError(f"拖拽失败: {str(e)}") from e

    def press_key(self, key: str, presses: int = 1, interval: float = 0.0) -> None:
        """
        按下指定按键

        Args:
            key: 按键名称
            presses: 按键次数
            interval: 按键间隔时间(秒)

        Raises:
            ActionExecutorError: 按键失败时抛出
        """
        try:
            for _ in range(presses):
                keyboard.press_and_release(key)
                if interval > 0:
                    time.sleep(interval)

        except Exception as e:
            raise ActionExecutorError(f"按键失败: {str(e)}") from e

    def type_string(self, text: str, interval: float = 0.0) -> None:
        """
        输入文本

        Args:
            text: 要输入的文本
            interval: 字符间隔时间(秒)

        Raises:
            ActionExecutorError: 输入失败时抛出
        """
        try:
            keyboard.write(text, delay=interval)

        except Exception as e:
            raise ActionExecutorError(f"输入失败: {str(e)}") from e

    def scroll(
        self, clicks: int, x: Optional[int] = None, y: Optional[int] = None
    ) -> None:
        """
        滚动鼠标滚轮

        Args:
            clicks: 滚动量，正数向上滚动，负数向下滚动
            x: 鼠标X坐标，None表示当前位置
            y: 鼠标Y坐标，None表示当前位置

        Raises:
            ActionExecutorError: 滚动失败时抛出
        """
        try:
            if x is not None and y is not None:
                pyautogui.moveTo(x, y)
            pyautogui.scroll(clicks)

        except Exception as e:
            raise ActionExecutorError(f"滚动失败: {str(e)}") from e

    def get_window_rect(self) -> Optional[Any]:
        """
        获取当前窗口的位置和大小

        Returns:
            Any: 窗口矩形(left, top, right, bottom)

        Raises:
            ActionExecutorError: 获取窗口位置失败时抛出
        """
        try:
            if self.window_handle is None:
                raise ActionExecutorError("未设置窗口句柄")

            return win32gui.GetWindowRect(self.window_handle)

        except Exception as e:
            raise ActionExecutorError(f"获取窗口位置失败: {str(e)}") from e

    def move_window(
        self, x: int, y: int, width: Optional[int] = None, height: Optional[int] = None
    ) -> None:
        """
        移动窗口

        Args:
            x: 新的X坐标
            y: 新的Y坐标
            width: 新的宽度，None表示保持不变
            height: 新的高度，None表示保持不变

        Raises:
            ActionExecutorError: 移动窗口失败时抛出
        """
        try:
            if self.window_handle is None:
                raise ActionExecutorError("未设置窗口句柄")

            # 获取当前窗口大小
            rect = win32gui.GetWindowRect(self.window_handle)
            current_width = rect[2] - rect[0]
            current_height = rect[3] - rect[1]

            # 使用指定的新大小或保持当前大小
            new_width = width if width is not None else current_width
            new_height = height if height is not None else current_height

            # 移动窗口
            win32gui.MoveWindow(self.window_handle, x, y, new_width, new_height, True)

        except Exception as e:
            raise ActionExecutorError(f"移动窗口失败: {str(e)}") from e
