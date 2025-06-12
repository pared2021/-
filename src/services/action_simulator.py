import pyautogui
import time
import random
from typing import Tuple, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from .config import Config
from .logger import GameLogger
from .window_manager import GameWindowManager

class ActionSimulator(QObject):
    """操作模拟类，负责模拟鼠标和键盘操作"""
    
    # 定义信号
    action_started = pyqtSignal(str)  # 操作开始信号
    action_finished = pyqtSignal(str)  # 操作完成信号
    action_failed = pyqtSignal(str, str)  # 操作失败信号
    progress_updated = pyqtSignal(float)  # 进度更新信号
    
    def __init__(self, logger: GameLogger, window_manager: GameWindowManager, config: Config):
        """初始化操作模拟器
        
        Args:
            logger: 日志对象
            window_manager: 窗口管理器实例
            config: 配置对象
        """
        super().__init__()
        self.config = config
        self.logger = logger
        self.window_manager = window_manager
        
        # 设置pyautogui安全特性
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = config.action.key_press_delay
        
        self.logger.info("操作模拟器初始化完成")
    
    def move_to(self, x: int, y: int, duration: float = None):
        """
        移动鼠标到指定位置
        
        Args:
            x: 目标x坐标
            y: 目标y坐标
            duration: 移动持续时间（秒）。如果为 None，则使用配置中的 mouse_speed。
        """
        self.action_started.emit("move_to")
        try:
            # 添加随机偏移
            offset = self.config.action.mouse_offset
            x += random.randint(-offset, offset)
            y += random.randint(-offset, offset)
            
            # 获取或设置移动持续时间
            move_duration = duration if duration is not None else self.config.action.mouse_speed
            
            self.logger.debug(f"移动鼠标到: ({x}, {y}), 持续时间: {move_duration}")
            pyautogui.moveTo(x, y, duration=move_duration, tween=pyautogui.easeInOutQuad)
            self.action_finished.emit("move_to")
        except Exception as e:
            self.action_failed.emit("move_to", str(e))
            self.logger.error(f"移动鼠标失败: {e}")
            raise
    
    def click(self, x: int, y: int, button: str = 'left', 
             clicks: int = 1, interval: float = None):
        """
        点击指定位置
        
        Args:
            x: 点击x坐标
            y: 点击y坐标
            button: 鼠标按钮（left/right/middle）
            clicks: 点击次数
            interval: 点击间隔
        """
        self.action_started.emit("click")
        try:
            interval = interval or self.config.action.click_delay
            
            self.logger.debug(f"点击: ({x}, {y}), 按钮: {button}, 次数: {clicks}")
            self.move_to(x, y)
            pyautogui.click(button=button, clicks=clicks, interval=interval)
            self.action_finished.emit("click")
        except Exception as e:
            self.action_failed.emit("click", str(e))
            self.logger.error(f"点击失败: {e}")
            raise
    
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
    
    def press_key(self, key: str, presses: int = 1, interval: float = None):
        """
        按下键盘按键
        
        Args:
            key: 按键名称
            presses: 按下次数
            interval: 按键间隔
        """
        self.action_started.emit("press_key")
        try:
            interval = interval or self.config.action.key_press_delay
            
            self.logger.debug(f"按下按键: {key}, 次数: {presses}")
            pyautogui.press(key, presses=presses, interval=interval)
            self.action_finished.emit("press_key")
        except Exception as e:
            self.action_failed.emit("press_key", str(e))
            self.logger.error(f"按下按键失败: {e}")
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
            interval = interval or self.config.action.key_press_delay
            
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
            min_seconds = min_seconds or self.config.action.min_wait_time
            max_seconds = max_seconds or self.config.action.max_wait_time
            
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