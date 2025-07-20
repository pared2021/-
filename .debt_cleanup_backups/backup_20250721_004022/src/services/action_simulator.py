import pyautogui
import time
import random
from typing import Tuple, Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal
from .config import Config
from .logger import GameLogger
from .window_manager import GameWindowManager
from src.common.error_types import ErrorCode, ActionError, ErrorContext
import keyboard
import win32api
import win32con

class ActionSimulator(QObject):
    """操作模拟类，负责模拟鼠标和键盘操作"""
    
    # 定义信号
    action_started = pyqtSignal(str)  # 操作开始信号
    action_finished = pyqtSignal(str)  # 操作完成信号
    action_failed = pyqtSignal(str, str)  # 操作失败信号
    progress_updated = pyqtSignal(float)  # 进度更新信号
    
    def __init__(self, logger: GameLogger, window_manager: GameWindowManager, config: Config, error_handler):
        """初始化操作模拟器
        
        Args:
            logger: 日志对象
            window_manager: 窗口管理器实例
            config: 配置对象
            error_handler: 错误处理对象
        """
        super().__init__()
        self.config = config
        self.logger = logger
        self.window_manager = window_manager
        self.error_handler = error_handler
        self.is_initialized = False
        
        # 设置pyautogui安全特性
        pyautogui.FAILSAFE = True
        automation_config = config.get_automation_config()
        pyautogui.PAUSE = automation_config.get('key_press_delay', 0.1)
        
        self.logger.info("操作模拟器初始化完成")
    
    def initialize(self) -> bool:
        """初始化动作模拟器"""
        try:
            self.is_initialized = True
            return True
        except Exception as e:
            self.error_handler.handle_error(
                ActionError(
                    ErrorCode.ACTION_SIMULATOR_INIT_FAILED,
                    "动作模拟器初始化失败",
                    ErrorContext(
                        source="ActionSimulator.initialize",
                        details=str(e)
                    )
                )
            )
            return False
    
    def execute_action(self, action: Dict[str, Any]) -> bool:
        """执行动作"""
        try:
            if not self.is_initialized:
                self.error_handler.handle_error(
                    ActionError(
                        ErrorCode.ACTION_SIMULATOR_NOT_INITIALIZED,
                        "动作模拟器未初始化",
                        ErrorContext(
                            source="ActionSimulator.execute_action",
                            details="is_initialized is False"
                        )
                    )
                )
                return False
                
            action_type = action.get('type')
            if not action_type:
                self.error_handler.handle_error(
                    ActionError(
                        ErrorCode.INVALID_ACTION_TYPE,
                        "无效的动作类型",
                        ErrorContext(
                            source="ActionSimulator.execute_action",
                            details="action_type is None"
                        )
                    )
                )
                return False
                
            if action_type == 'mouse_move':
                return self.move_to(action['x'], action['y'])
            elif action_type == 'mouse_click':
                return self.click(action['x'], action['y'])
            elif action_type == 'key_press':
                return self.press_key(action['key'])
            elif action_type == 'key_release':
                return self.release_key(action['key'])
            else:
                self.error_handler.handle_error(
                    ActionError(
                        ErrorCode.UNKNOWN_ACTION_TYPE,
                        f"未知的动作类型: {action_type}",
                        ErrorContext(
                            source="ActionSimulator.execute_action",
                            details=f"action_type: {action_type}"
                        )
                    )
                )
                return False
                
        except Exception as e:
            self.error_handler.handle_error(
                ActionError(
                    ErrorCode.ACTION_EXECUTION_FAILED,
                    "动作执行失败",
                    ErrorContext(
                        source="ActionSimulator.execute_action",
                        details=str(e)
                    )
                )
            )
            return False
    
    def move_to(self, x: int, y: int) -> bool:
        """移动鼠标到指定位置"""
        self.action_started.emit("move_to")
        try:
            # 获取窗口位置
            window_rect = self.window_manager.get_window_rect()
            if not window_rect:
                return False
                
            # 计算相对坐标
            abs_x = window_rect[0] + x
            abs_y = window_rect[1] + y
            
            self.logger.debug(f"移动鼠标到: ({abs_x}, {abs_y})")
            pyautogui.moveTo(abs_x, abs_y)
            self.action_finished.emit("move_to")
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ActionError(
                    ErrorCode.MOUSE_MOVE_FAILED,
                    "鼠标移动失败",
                    ErrorContext(
                        source="ActionSimulator.move_to",
                        details=str(e)
                    )
                )
            )
            self.action_failed.emit("move_to", str(e))
            self.logger.error(f"移动鼠标失败: {e}")
            return False
    
    def click(self, x: int, y: int) -> bool:
        """点击指定位置"""
        self.action_started.emit("click")
        try:
            # 获取窗口位置
            window_rect = self.window_manager.get_window_rect()
            if not window_rect:
                return False
                
            # 计算相对坐标
            abs_x = window_rect[0] + x
            abs_y = window_rect[1] + y
            
            self.logger.debug(f"点击: ({abs_x}, {abs_y})")
            pyautogui.click(abs_x, abs_y)
            self.action_finished.emit("click")
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ActionError(
                    ErrorCode.MOUSE_CLICK_FAILED,
                    "鼠标点击失败",
                    ErrorContext(
                        source="ActionSimulator.click",
                        details=str(e)
                    )
                )
            )
            self.action_failed.emit("click", str(e))
            self.logger.error(f"点击失败: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """按下按键"""
        self.action_started.emit("press_key")
        try:
            self.logger.debug(f"按下按键: {key}")
            keyboard.press(key)
            self.action_finished.emit("press_key")
            return True
        except Exception as e:
            self.error_handler.handle_error(
                ActionError(
                    ErrorCode.KEY_PRESS_FAILED,
                    "按键按下失败",
                    ErrorContext(
                        source="ActionSimulator.press_key",
                        details=str(e)
                    )
                )
            )
            self.action_failed.emit("press_key", str(e))
            self.logger.error(f"按下按键失败: {e}")
            return False
    
    def release_key(self, key: str) -> bool:
        """释放按键"""
        self.action_started.emit("release_key")
        try:
            self.logger.debug(f"释放按键: {key}")
            keyboard.release(key)
            self.action_finished.emit("release_key")
            return True
        except Exception as e:
            self.error_handler.handle_error(
                ActionError(
                    ErrorCode.KEY_RELEASE_FAILED,
                    "按键释放失败",
                    ErrorContext(
                        source="ActionSimulator.release_key",
                        details=str(e)
                    )
                )
            )
            self.action_failed.emit("release_key", str(e))
            self.logger.error(f"释放按键失败: {e}")
            return False
    
    def drag_to(self, start_x: int, start_y: int, end_x: int, end_y: int, 
               duration: float = None):
        """
        拖拽鼠标
        
        Args:
            start_x: 起始x坐标
            start_y: 起始y坐标
            end_x: 结束x坐标
            end_y: 结束y坐标
            duration: 拖拽持续时间
        """
        self.action_started.emit("drag_to")
        try:
            self.logger.debug(f"拖拽: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
            self.move_to(start_x, start_y)
            pyautogui.dragTo(end_x, end_y, duration=duration, button='left')
            self.action_finished.emit("drag_to")
        except Exception as e:
            self.action_failed.emit("drag_to", str(e))
            self.logger.error(f"拖拽失败: {e}")
            raise
    
    def hotkey(self, *keys: str):
        """
        按下组合键
        
        Args:
            keys: 按键列表
        """
        self.action_started.emit("hotkey")
        try:
            self.logger.debug(f"按下组合键: {keys}")
            pyautogui.hotkey(*keys)
            self.action_finished.emit("hotkey")
        except Exception as e:
            self.action_failed.emit("hotkey", str(e))
            self.logger.error(f"按下组合键失败: {e}")
            raise
    
    def typewrite(self, text: str, interval: float = None):
        """
        输入文本
        
        Args:
            text: 要输入的文本
            interval: 按键间隔
        """
        self.action_started.emit("typewrite")
        try:
            if interval is None:
                automation_config = self.config.get_automation_config()
                interval = automation_config.get('key_press_delay', 0.1)
            
            self.logger.debug(f"输入文本: {text}")
            pyautogui.typewrite(text, interval=interval)
            self.action_finished.emit("typewrite")
        except Exception as e:
            self.action_failed.emit("typewrite", str(e))
            self.logger.error(f"输入文本失败: {e}")
            raise
    
    def scroll(self, clicks: int):
        """
        滚动鼠标滚轮
        
        Args:
            clicks: 滚动次数（正数向上，负数向下）
        """
        self.action_started.emit("scroll")
        try:
            self.logger.debug(f"滚动鼠标: {clicks}次")
            pyautogui.scroll(clicks)
            self.action_finished.emit("scroll")
        except Exception as e:
            self.action_failed.emit("scroll", str(e))
            self.logger.error(f"滚动鼠标失败: {e}")
            raise
    
    def wait(self, seconds: float):
        """
        等待指定时间
        
        Args:
            seconds: 等待秒数
        """
        self.action_started.emit("wait")
        try:
            self.logger.debug(f"等待: {seconds}秒")
            time.sleep(seconds)
            self.action_finished.emit("wait")
        except Exception as e:
            self.action_failed.emit("wait", str(e))
            self.logger.error(f"等待失败: {e}")
            raise
    
    def random_wait(self, min_seconds: float = None, max_seconds: float = None):
        """
        随机等待一段时间
        
        Args:
            min_seconds: 最小等待时间
            max_seconds: 最大等待时间
        """
        self.action_started.emit("random_wait")
        try:
            if min_seconds is None or max_seconds is None:
                automation_config = self.config.get_automation_config()
                min_seconds = min_seconds or automation_config.get('min_wait_time', 0.5)
                max_seconds = max_seconds or automation_config.get('max_wait_time', 2.0)
            
            wait_time = random.uniform(min_seconds, max_seconds)
            self.logger.debug(f"随机等待: {wait_time:.2f}秒")
            time.sleep(wait_time)
            self.action_finished.emit("random_wait")
        except Exception as e:
            self.action_failed.emit("random_wait", str(e))
            self.logger.error(f"随机等待失败: {e}")
            raise
    
    def ensure_window_active(self) -> bool:
        """
        确保目标窗口处于激活状态
        
        Returns:
            bool: 是否成功激活窗口
        """
        self.action_started.emit("ensure_window_active")
        try:
            if not self.window_manager.is_window_active():
                self.logger.debug("窗口未激活，尝试激活")
                if self.window_manager.set_foreground():
                    self.logger.info("窗口激活成功")
                    self.action_finished.emit("ensure_window_active")
                    return True
                else:
                    self.logger.error("窗口激活失败")
                    self.action_failed.emit("ensure_window_active", "窗口激活失败")
                    return False
            self.action_finished.emit("ensure_window_active")
            return True
        except Exception as e:
            self.action_failed.emit("ensure_window_active", str(e))
            self.logger.error(f"确保窗口激活失败: {e}")
            return False
    
    def check_window_active(self) -> bool:
        """
        检查窗口是否激活
        
        Returns:
            bool: 窗口是否激活
        """
        return self.window_manager.is_window_active()
        
    def activate_window(self) -> bool:
        """
        激活窗口
        
        Returns:
            bool: 是否成功激活
        """
        return self.window_manager.set_foreground()
    
    def get_position(self) -> Optional[Tuple[int, int]]:
        """获取当前鼠标位置"""
        try:
            x, y = pyautogui.position()
            return (x, y)
        except Exception as e:
            self.error_handler.handle_error(
                ActionError(
                    ErrorCode.GET_POSITION_FAILED,
                    "获取鼠标位置失败",
                    ErrorContext(
                        source="ActionSimulator.get_position",
                        details=str(e)
                    )
                )
            )
            return None
    
    def reset_mouse_position(self) -> bool:
        """重置鼠标位置"""
        try:
            # 获取窗口位置
            window_rect = self.window_manager.get_window_rect()
            if not window_rect:
                return False
                
            # 移动到窗口中心
            center_x = window_rect[0] + (window_rect[2] - window_rect[0]) // 2
            center_y = window_rect[1] + (window_rect[3] - window_rect[1]) // 2
            
            pyautogui.moveTo(center_x, center_y)
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ActionError(
                    ErrorCode.MOUSE_RESET_FAILED,
                    "重置鼠标位置失败",
                    ErrorContext(
                        source="ActionSimulator.reset_mouse_position",
                        details=str(e)
                    )
                )
            )
            return False
    
    def cleanup(self) -> None:
        """清理资源"""
        self.is_initialized = False 