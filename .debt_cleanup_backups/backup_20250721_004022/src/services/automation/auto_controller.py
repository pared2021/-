"""
自动化控制服务
负责执行自动化操作
"""
from typing import Optional, List, Dict, Callable
import time
from dataclasses import dataclass
from src.services.error_handler import ErrorHandler
from src.common.error_types import ErrorCode, ErrorContext
from ..vision.state_recognizer import GameState

# 使用统一的Action体系
from src.common.action_system import (
    ActionType, AutomationAction, ActionSequence, ActionFactory, BaseAction
)

# 向后兼容性别名
Action = AutomationAction

class AutoController:
    """自动化控制器"""
    
    def __init__(self, error_handler: ErrorHandler):
        """初始化
        
        Args:
            error_handler: 错误处理器
        """
        self.error_handler = error_handler
        self.actions: List[Action] = []
        self.is_running = False
        self.current_action_index = 0
        self.retry_count = 0
        self.start_time = 0
        
    def add_action(self, action: Action) -> None:
        """添加动作
        
        Args:
            action: 自动化动作
        """
        self.actions.append(action)
        
    def clear_actions(self) -> None:
        """清空动作列表"""
        self.actions.clear()
        self.current_action_index = 0
        self.retry_count = 0
        
    def start(self) -> bool:
        """开始执行自动化
        
        Returns:
            bool: 是否成功
        """
        try:
            if not self.actions:
                raise ValueError("没有可执行的动作")
                
            self.is_running = True
            self.current_action_index = 0
            self.retry_count = 0
            self.start_time = time.time()
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.AUTO_CONTROL_ERROR,
                "启动自动化失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="AutoController.start"
                )
            )
            return False
            
    def stop(self) -> None:
        """停止执行自动化"""
        self.is_running = False
        
    def execute(self, current_state: Optional[GameState]) -> bool:
        """执行自动化
        
        Args:
            current_state: 当前游戏状态
            
        Returns:
            bool: 是否继续执行
        """
        try:
            if not self.is_running:
                return False
                
            # 检查是否完成所有动作
            if self.current_action_index >= len(self.actions):
                self.is_running = False
                return False
                
            # 获取当前动作
            action = self.actions[self.current_action_index]
            
            # 检查超时
            if time.time() - self.start_time > action.timeout:
                self.error_handler.handle_error(
                    ErrorCode.AUTO_CONTROL_ERROR,
                    f"动作 {action.name} 执行超时",
                    ErrorContext(
                        error_info=f"超时时间: {action.timeout}秒",
                        error_location="AutoController.execute"
                    )
                )
                self.current_action_index += 1
                self.retry_count = 0
                self.start_time = time.time()
                return True
                
            # 检查执行条件
            if action.condition and not action.condition(current_state):
                return True
                
            # 执行动作
            success = self._execute_action(action, current_state)
            
            if success:
                self.current_action_index += 1
                self.retry_count = 0
                self.start_time = time.time()
            else:
                self.retry_count += 1
                if self.retry_count >= action.retry_count:
                    self.error_handler.handle_error(
                        ErrorCode.AUTO_CONTROL_ERROR,
                        f"动作 {action.name} 重试次数超限",
                        ErrorContext(
                            error_info=f"重试次数: {action.retry_count}",
                            error_location="AutoController.execute"
                        )
                    )
                    self.current_action_index += 1
                    self.retry_count = 0
                    self.start_time = time.time()
                    
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.AUTO_CONTROL_ERROR,
                "执行自动化失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="AutoController.execute"
                )
            )
            return False
            
    def _execute_action(self, action: Action, 
                       current_state: Optional[GameState]) -> bool:
        """执行单个动作
        
        Args:
            action: 自动化动作
            current_state: 当前游戏状态
            
        Returns:
            bool: 是否成功
        """
        try:
            # 使用统一Action体系的执行方法
            if hasattr(action, 'execute') and callable(action.execute):
                return action.execute(executor=self)
            
            # 向后兼容性处理
            if action.type == ActionType.CLICK:
                return self._execute_click(action.params)
            elif action.type == ActionType.KEY:
                return self._execute_key(action.params)
            elif action.type == ActionType.WAIT:
                return self._execute_wait(action.params)
            elif action.type == ActionType.CONDITION:
                return self._execute_condition(action.params, current_state)
            else:
                raise ValueError(f"未知的动作类型: {action.type}")
                
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.AUTO_CONTROL_ERROR,
                f"执行动作 {action.name} 失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="AutoController._execute_action"
                )
            )
            return False
            
    def _execute_click(self, params: Dict) -> bool:
        """执行点击动作
        
        Args:
            params: 动作参数
            
        Returns:
            bool: 是否成功
        """
        try:
            x = params.get("x")
            y = params.get("y")
            if x is None or y is None:
                raise ValueError("缺少点击坐标")
                
            # TODO: 实现点击操作
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.AUTO_CONTROL_ERROR,
                "执行点击动作失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="AutoController._execute_click"
                )
            )
            return False
            
    def _execute_key(self, params: Dict) -> bool:
        """执行按键动作
        
        Args:
            params: 动作参数
            
        Returns:
            bool: 是否成功
        """
        try:
            key = params.get("key")
            if key is None:
                raise ValueError("缺少按键信息")
                
            # TODO: 实现按键操作
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.AUTO_CONTROL_ERROR,
                "执行按键动作失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="AutoController._execute_key"
                )
            )
            return False
            
    def _execute_wait(self, params: Dict) -> bool:
        """执行等待动作
        
        Args:
            params: 动作参数
            
        Returns:
            bool: 是否成功
        """
        try:
            duration = params.get("duration", 1.0)
            time.sleep(duration)
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.AUTO_CONTROL_ERROR,
                "执行等待动作失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="AutoController._execute_wait"
                )
            )
            return False
            
    def _execute_condition(self, params: Dict, 
                          current_state: Optional[GameState]) -> bool:
        """执行条件动作
        
        Args:
            params: 动作参数
            current_state: 当前游戏状态
            
        Returns:
            bool: 是否成功
        """
        try:
            if current_state is None:
                return False
                
            state_name = params.get("state")
            if state_name is None:
                raise ValueError("缺少状态名称")
                
            return current_state.name == state_name
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.AUTO_CONTROL_ERROR,
                "执行条件动作失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="AutoController._execute_condition"
                )
            )
            return False
    
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
        return self._execute_click({"x": x, "y": y, "button": button})
    
    def send_key(self, key: str, hold_time: float = 0.0) -> bool:
        """发送按键 - executor接口
        
        Args:
            key: 按键
            hold_time: 按住时间
            
        Returns:
            bool: 是否成功
        """
        result = self._execute_key({"key": key})
        if hold_time > 0:
            time.sleep(hold_time)
        return result
    
    def execute_action(self, action: BaseAction) -> bool:
        """执行动作 - executor接口
        
        Args:
            action: 动作对象
            
        Returns:
            bool: 是否成功
        """
        return self._execute_action(action, None) 