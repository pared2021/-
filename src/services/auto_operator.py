from typing import Dict, Any, List, Optional, Tuple, Callable
import time
import random
import numpy as np
from src.services.logger import GameLogger
from src.services.action_simulator import ActionSimulator
from src.services.game_state import GameState
from src.services.image_processor import ImageProcessor
from src.services.config import Config
from dataclasses import dataclass
from src.common.error_types import ErrorCode, AutomationError, ErrorContext
from src.services.error_handler import ErrorHandler
from src.services.window_manager import WindowManager
from src.services.image_processor import ImageProcessor, TemplateMatchResult

# 使用统一的Action体系
from src.common.action_system import (
    ActionType, AutomationAction, ActionSequence, ActionFactory, BaseAction
)

# 向后兼容性别名
Action = AutomationAction

class AutoOperator:
    """自动化操作器"""
    
    def __init__(self, error_handler: ErrorHandler, window_manager: WindowManager, image_processor: ImageProcessor):
        """初始化自动化操作器
        
        Args:
            error_handler: 错误处理器
            window_manager: 窗口管理器
            image_processor: 图像处理器
        """
        self.error_handler = error_handler
        self.window_manager = window_manager
        self.image_processor = image_processor
        self.is_running = False
        self.current_action: Optional[Action] = None
        self.action_queue: List[Action] = []
        self.action_results: Dict[str, bool] = {}
        
    def add_action(self, action: Action) -> None:
        """添加动作
        
        Args:
            action: 动作定义
        """
        self.action_queue.append(action)
        
    def clear_actions(self) -> None:
        """清空动作队列"""
        self.action_queue.clear()
        self.action_results.clear()
        
    def start(self) -> bool:
        """开始执行自动化
        
        Returns:
            bool: 是否成功
        """
        try:
            if self.is_running:
                return False
                
            self.is_running = True
            self._execute_actions()
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.AUTOMATION_ERROR,
                AutomationError("启动自动化失败"),
                ErrorContext(
                    error_info=str(e),
                    error_location="AutoOperator.start"
                )
            )
            return False
            
    def stop(self) -> None:
        """停止执行自动化"""
        self.is_running = False
        self.current_action = None
        
    def _execute_actions(self) -> None:
        """执行动作队列"""
        while self.is_running and self.action_queue:
            action = self.action_queue[0]
            self.current_action = action
            
            try:
                if self._execute_action(action):
                    self.action_results[action.name] = True
                    self.action_queue.pop(0)
                else:
                    if action.retry_count > 0:
                        action.retry_count -= 1
                        time.sleep(1)  # 等待1秒后重试
                    else:
                        self.action_results[action.name] = False
                        self.action_queue.pop(0)
                        
            except Exception as e:
                self.error_handler.handle_error(
                    ErrorCode.AUTOMATION_ERROR,
                    AutomationError(f"执行动作失败: {action.name}"),
                    ErrorContext(
                        error_info=str(e),
                        error_location="AutoOperator._execute_actions",
                        action_name=action.name
                    )
                )
                self.action_results[action.name] = False
                self.action_queue.pop(0)
                
    def _execute_action(self, action: Action) -> bool:
        """执行单个动作
        
        Args:
            action: 动作定义
            
        Returns:
            bool: 是否成功
        """
        try:
            # 使用统一Action体系的执行方法
            if hasattr(action, 'execute') and callable(action.execute):
                return action.execute(executor=self)
            
            # 向后兼容性处理
            if action.type == ActionType.CLICK:
                return self._execute_click(action)
            elif action.type == ActionType.KEY:
                return self._execute_key(action)
            elif action.type == ActionType.WAIT:
                return self._execute_wait(action)
            elif action.type == ActionType.CONDITION:
                return self._execute_condition(action)
            else:
                raise ValueError(f"未知的动作类型: {action.type}")
                
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.AUTOMATION_ERROR,
                AutomationError(f"执行动作失败: {action.name}"),
                ErrorContext(
                    error_info=str(e),
                    error_location="AutoOperator._execute_action",
                    action_name=action.name,
                    action_type=str(action.type)
                )
            )
            return False
            
    def _execute_click(self, action: Action) -> bool:
        """执行点击动作
        
        Args:
            action: 动作定义
            
        Returns:
            bool: 是否成功
        """
        try:
            x = action.params.get("x")
            y = action.params.get("y")
            button = action.params.get("button", "left")
            
            if x is None or y is None:
                raise ValueError("缺少点击坐标")
                
            return self.window_manager.click_window(
                self.window_manager.current_window.hwnd,
                x, y, button
            )
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.AUTOMATION_ERROR,
                AutomationError(f"执行点击失败: {action.name}"),
                ErrorContext(
                    error_info=str(e),
                    error_location="AutoOperator._execute_click",
                    action_name=action.name,
                    click_position=(x, y)
                )
            )
            return False
            
    def _execute_key(self, action: Action) -> bool:
        """执行按键动作
        
        Args:
            action: 动作定义
            
        Returns:
            bool: 是否成功
        """
        try:
            key = action.params.get("key")
            if not key:
                raise ValueError("缺少按键定义")
                
            return self.window_manager.send_key(
                self.window_manager.current_window.hwnd,
                key
            )
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.AUTOMATION_ERROR,
                AutomationError(f"执行按键失败: {action.name}"),
                ErrorContext(
                    error_info=str(e),
                    error_location="AutoOperator._execute_key",
                    action_name=action.name,
                    key=key
                )
            )
            return False
            
    def _execute_wait(self, action: Action) -> bool:
        """执行等待动作
        
        Args:
            action: 动作定义
            
        Returns:
            bool: 是否成功
        """
        try:
            duration = action.params.get("duration", 1.0)
            time.sleep(duration)
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.AUTOMATION_ERROR,
                AutomationError(f"执行等待失败: {action.name}"),
                ErrorContext(
                    error_info=str(e),
                    error_location="AutoOperator._execute_wait",
                    action_name=action.name,
                    duration=duration
                )
            )
            return False
            
    def _execute_condition(self, action: Action) -> bool:
        """执行条件动作
        
        Args:
            action: 动作定义
            
        Returns:
            bool: 是否成功
        """
        try:
            if not action.condition:
                raise ValueError("缺少条件函数")
                
            start_time = time.time()
            while time.time() - start_time < action.timeout:
                if action.condition():
                    return True
                time.sleep(0.1)
            return False
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.AUTOMATION_ERROR,
                AutomationError(f"执行条件失败: {action.name}"),
                ErrorContext(
                    error_info=str(e),
                    error_location="AutoOperator._execute_condition",
                    action_name=action.name
                )
            )
            return False
            
    def get_action_results(self) -> Dict[str, bool]:
        """获取动作执行结果
        
        Returns:
            Dict[str, bool]: 动作执行结果
        """
        return self.action_results.copy()
        
    def get_current_action(self) -> Optional[Action]:
        """获取当前执行的动作
        
        Returns:
            Optional[Action]: 当前动作
        """
        return self.current_action

    def check_window_state(self):
        """检查窗口状态"""
        if not self.window_manager:
            return False
            
        return self.window_manager.is_window_active()
    
    # === 统一Action体系executor接口 ===
    
    def click(self, x: int, y: int, button: str = "left") -> bool:
        """点击操作 - executor接口
        
        Args:
            x: X坐标
            y: Y坐标
            button: 鼠标按钮
            
        Returns:
            bool: 是否成功
        """
        try:
            if not self.window_manager or not hasattr(self.window_manager, 'current_window'):
                return False
            return self.window_manager.click_window(
                self.window_manager.current_window.hwnd,
                x, y, button
            )
        except Exception:
            return False
    
    def send_key(self, key: str, hold_time: float = 0.0) -> bool:
        """发送按键 - executor接口
        
        Args:
            key: 按键
            hold_time: 按住时间
            
        Returns:
            bool: 是否成功
        """
        try:
            if not self.window_manager or not hasattr(self.window_manager, 'current_window'):
                return False
            result = self.window_manager.send_key(
                self.window_manager.current_window.hwnd,
                key
            )
            if hold_time > 0:
                time.sleep(hold_time)
            return result
        except Exception:
            return False
    
    def execute_action(self, action: BaseAction) -> bool:
        """执行动作 - executor接口
        
        Args:
            action: 动作对象
            
        Returns:
            bool: 是否成功
        """
        # 委托给原有的执行方法
        return self._execute_action(action) 