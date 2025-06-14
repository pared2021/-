"""
统一的Action系统
定义游戏自动化中所有类型的动作基类和专门化类
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, List, Union
import time


class ActionType(Enum):
    """动作类型枚举"""
    # 基础动作类型
    CLICK = "click"
    KEY = "key"
    WAIT = "wait"
    CONDITION = "condition"
    
    # 专门化动作类型
    BATTLE = "battle"
    UI = "ui"
    MACRO = "macro"
    MOUSE_MOVE = "mouse_move"
    MOUSE_DRAG = "mouse_drag"
    SCROLL = "scroll"
    
    # 游戏特定动作类型
    GAME_SPECIFIC = "game_specific"
    ZZZ_ACTION = "zzz_action"
    
    # 编辑器动作类型
    EDIT = "edit"
    UNDO = "undo"
    REDO = "redo"


class ActionStatus(Enum):
    """动作状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


@dataclass
class BaseAction:
    """统一的Action基类"""
    
    # 基本属性
    name: str
    type: ActionType
    params: Dict[str, Any] = field(default_factory=dict)
    
    # 执行控制
    timeout: float = 5.0
    retry_count: int = 3
    delay: float = 0.0
    post_delay: float = 0.01
    
    # 条件和回调
    condition: Optional[Callable] = None
    pre_action: Optional[Callable] = None
    post_action: Optional[Callable] = None
    
    # 状态管理
    status: ActionStatus = ActionStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    result: Any = None
    
    # 重试和回退
    current_retry: int = 0
    fallback_actions: List['BaseAction'] = field(default_factory=list)
    
    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.type, str):
            self.type = ActionType(self.type)
    
    def execute(self, executor: Optional[Any] = None) -> bool:
        """执行动作
        
        Args:
            executor: 动作执行器
            
        Returns:
            bool: 是否执行成功
        """
        self.start_time = time.time()
        self.status = ActionStatus.RUNNING
        
        try:
            # 执行前置动作
            if self.pre_action:
                self.pre_action(self)
            
            # 检查执行条件
            if self.condition and not self.condition():
                self.status = ActionStatus.SKIPPED
                return True
            
            # 执行主要动作
            success = self._execute_core(executor)
            
            if success:
                self.status = ActionStatus.SUCCESS
                # 执行后置动作
                if self.post_action:
                    self.post_action(self)
                
                # 后置延迟
                if self.post_delay > 0:
                    time.sleep(self.post_delay)
                
                return True
            else:
                self.status = ActionStatus.FAILED
                return False
                
        except Exception as e:
            self.error_message = str(e)
            self.status = ActionStatus.FAILED
            return False
        finally:
            self.end_time = time.time()
    
    def _execute_core(self, executor: Optional[Any] = None) -> bool:
        """核心执行逻辑，由子类重写
        
        Args:
            executor: 动作执行器
            
        Returns:
            bool: 是否执行成功
        """
        raise NotImplementedError("子类必须实现_execute_core方法")
    
    def retry(self, executor: Optional[Any] = None) -> bool:
        """重试执行
        
        Args:
            executor: 动作执行器
            
        Returns:
            bool: 是否执行成功
        """
        if self.current_retry >= self.retry_count:
            return False
        
        self.current_retry += 1
        
        # 重试延迟
        if self.delay > 0:
            time.sleep(self.delay * self.current_retry)
        
        return self.execute(executor)
    
    def reset(self):
        """重置动作状态"""
        self.status = ActionStatus.PENDING
        self.start_time = None
        self.end_time = None
        self.error_message = None
        self.result = None
        self.current_retry = 0
    
    def get_duration(self) -> Optional[float]:
        """获取执行时间
        
        Returns:
            Optional[float]: 执行时间（秒），如果未完成则返回None
        """
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    def is_completed(self) -> bool:
        """检查是否已完成（成功或失败）
        
        Returns:
            bool: 是否已完成
        """
        return self.status in [ActionStatus.SUCCESS, ActionStatus.FAILED, ActionStatus.SKIPPED, ActionStatus.TIMEOUT]
    
    def is_successful(self) -> bool:
        """检查是否执行成功
        
        Returns:
            bool: 是否执行成功
        """
        return self.status == ActionStatus.SUCCESS


@dataclass
class AutomationAction(BaseAction):
    """自动化动作类 - 用于替代auto_operator.Action"""
    
    repeat: int = 1
    
    def _execute_core(self, executor: Optional[Any] = None) -> bool:
        """执行自动化动作"""
        if not executor:
            return False
        
        try:
            if self.type == ActionType.CLICK:
                return self._execute_click(executor)
            elif self.type == ActionType.KEY:
                return self._execute_key(executor)
            elif self.type == ActionType.WAIT:
                return self._execute_wait(executor)
            elif self.type == ActionType.CONDITION:
                return self._execute_condition(executor)
            else:
                # 委托给执行器处理
                if hasattr(executor, 'execute_action'):
                    return executor.execute_action(self)
                return False
        except Exception as e:
            self.error_message = str(e)
            return False
    
    def _execute_click(self, executor: Any) -> bool:
        """执行点击动作"""
        x = self.params.get("x", 0)
        y = self.params.get("y", 0)
        button = self.params.get("button", "left")
        
        for _ in range(self.repeat):
            if hasattr(executor, 'click'):
                if not executor.click(x, y, button):
                    return False
            if self.delay > 0:
                time.sleep(self.delay)
        
        return True
    
    def _execute_key(self, executor: Any) -> bool:
        """执行按键动作"""
        key = self.params.get("key")
        if not key:
            return False
        
        hold_time = self.params.get("hold_time", 0.0)
        
        for _ in range(self.repeat):
            if hasattr(executor, 'send_key'):
                if not executor.send_key(key, hold_time):
                    return False
            if self.delay > 0:
                time.sleep(self.delay)
        
        return True
    
    def _execute_wait(self, executor: Any) -> bool:
        """执行等待动作"""
        duration = self.params.get("duration", 1.0)
        time.sleep(duration)
        return True
    
    def _execute_condition(self, executor: Any) -> bool:
        """执行条件动作"""
        if not self.condition:
            return False
        
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            if self.condition():
                return True
            time.sleep(0.1)
        
        return False


@dataclass
class BattleAction(BaseAction):
    """战斗动作类 - 用于替代zzz.battle.auto_battle.BattleAction"""
    
    priority: int = 0
    cooldown: float = 0.0
    action_type: str = ""
    fallback: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.action_type and not self.name:
            self.name = self.action_type
    
    def _execute_core(self, executor: Optional[Any] = None) -> bool:
        """执行战斗动作"""
        if not executor:
            return False
        
        try:
            # 检查冷却时间
            if self.cooldown > 0:
                time.sleep(self.cooldown)
            
            # 执行战斗特定逻辑
            if hasattr(executor, 'execute_battle_action'):
                return executor.execute_battle_action(self)
            elif hasattr(executor, 'execute_action'):
                return executor.execute_action(self)
            
            return False
        except Exception as e:
            self.error_message = str(e)
            return False


@dataclass
class GameSpecificAction(BaseAction):
    """游戏特定动作类 - 用于替代games.zzz.zzz_adapter.ZZZAction"""
    
    key: str = ""
    hold_time: float = 0.0
    game_name: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        if self.key and not self.params.get("key"):
            self.params["key"] = self.key
        if self.hold_time and not self.params.get("hold_time"):
            self.params["hold_time"] = self.hold_time
    
    def _execute_core(self, executor: Optional[Any] = None) -> bool:
        """执行游戏特定动作"""
        if not executor:
            return False
        
        try:
            # 执行游戏特定逻辑
            if hasattr(executor, 'execute_game_action'):
                return executor.execute_game_action(self)
            elif hasattr(executor, 'execute_action'):
                return executor.execute_action(self)
            
            return False
        except Exception as e:
            self.error_message = str(e)
            return False


@dataclass
class UIAction(BaseAction):
    """UI动作类 - 用于界面操作"""
    
    widget_name: str = ""
    widget_id: str = ""
    
    def _execute_core(self, executor: Optional[Any] = None) -> bool:
        """执行UI动作"""
        if not executor:
            return False
        
        try:
            # 执行UI特定逻辑
            if hasattr(executor, 'execute_ui_action'):
                return executor.execute_ui_action(self)
            elif hasattr(executor, 'execute_action'):
                return executor.execute_action(self)
            
            return False
        except Exception as e:
            self.error_message = str(e)
            return False


@dataclass
class MacroAction(BaseAction):
    """宏动作类 - 用于替代macro.macro_editor.EditAction"""
    
    operation: str = ""
    target: Any = None
    old_value: Any = None
    new_value: Any = None
    
    def _execute_core(self, executor: Optional[Any] = None) -> bool:
        """执行宏动作"""
        if not executor:
            return False
        
        try:
            # 执行宏特定逻辑
            if hasattr(executor, 'execute_macro_action'):
                return executor.execute_macro_action(self)
            elif hasattr(executor, 'execute_action'):
                return executor.execute_action(self)
            
            return False
        except Exception as e:
            self.error_message = str(e)
            return False


class ActionSequence:
    """动作序列类 - 管理一系列动作的执行"""
    
    def __init__(self, name: str = "ActionSequence"):
        self.name = name
        self.actions: List[BaseAction] = []
        self.current_index = 0
        self.status = ActionStatus.PENDING
        self.parallel_execution = False
    
    def add_action(self, action: BaseAction):
        """添加动作"""
        self.actions.append(action)
    
    def add_actions(self, actions: List[BaseAction]):
        """批量添加动作"""
        self.actions.extend(actions)
    
    def execute(self, executor: Optional[Any] = None) -> bool:
        """执行动作序列"""
        self.status = ActionStatus.RUNNING
        
        try:
            if self.parallel_execution:
                return self._execute_parallel(executor)
            else:
                return self._execute_sequential(executor)
        except Exception as e:
            self.status = ActionStatus.FAILED
            return False
    
    def _execute_sequential(self, executor: Optional[Any] = None) -> bool:
        """顺序执行动作"""
        for i, action in enumerate(self.actions):
            self.current_index = i
            
            # 执行动作，支持重试
            success = False
            for attempt in range(action.retry_count + 1):
                if action.execute(executor):
                    success = True
                    break
                elif attempt < action.retry_count:
                    action.retry(executor)
            
            if not success:
                # 尝试执行回退动作
                if action.fallback_actions:
                    fallback_success = False
                    for fallback_action in action.fallback_actions:
                        if fallback_action.execute(executor):
                            fallback_success = True
                            break
                    
                    if not fallback_success:
                        self.status = ActionStatus.FAILED
                        return False
                else:
                    self.status = ActionStatus.FAILED
                    return False
        
        self.status = ActionStatus.SUCCESS
        return True
    
    def _execute_parallel(self, executor: Optional[Any] = None) -> bool:
        """并行执行动作（简化版本）"""
        # 这里可以实现真正的并行执行
        # 目前使用简化的顺序执行
        return self._execute_sequential(executor)
    
    def reset(self):
        """重置序列状态"""
        self.current_index = 0
        self.status = ActionStatus.PENDING
        for action in self.actions:
            action.reset()
    
    def get_progress(self) -> float:
        """获取执行进度"""
        if not self.actions:
            return 0.0
        return self.current_index / len(self.actions)


class ActionFactory:
    """动作工厂类 - 用于创建不同类型的动作"""
    
    @staticmethod
    def create_click_action(name: str, x: int, y: int, **kwargs) -> AutomationAction:
        """创建点击动作"""
        return AutomationAction(
            name=name,
            type=ActionType.CLICK,
            params={"x": x, "y": y, **kwargs}
        )
    
    @staticmethod
    def create_key_action(name: str, key: str, **kwargs) -> AutomationAction:
        """创建按键动作"""
        return AutomationAction(
            name=name,
            type=ActionType.KEY,
            params={"key": key, **kwargs}
        )
    
    @staticmethod
    def create_wait_action(name: str, duration: float, **kwargs) -> AutomationAction:
        """创建等待动作"""
        return AutomationAction(
            name=name,
            type=ActionType.WAIT,
            params={"duration": duration, **kwargs}
        )
    
    @staticmethod
    def create_battle_action(name: str, action_type: str, **kwargs) -> BattleAction:
        """创建战斗动作"""
        return BattleAction(
            name=name,
            type=ActionType.BATTLE,
            action_type=action_type,
            **kwargs
        )
    
    @staticmethod
    def create_game_action(name: str, game_name: str, key: str, **kwargs) -> GameSpecificAction:
        """创建游戏特定动作"""
        return GameSpecificAction(
            name=name,
            type=ActionType.GAME_SPECIFIC,
            game_name=game_name,
            key=key,
            **kwargs
        )
    
    @staticmethod
    def create_macro_action(name: str, operation: str, **kwargs) -> MacroAction:
        """创建宏动作"""
        return MacroAction(
            name=name,
            type=ActionType.MACRO,
            operation=operation,
            **kwargs
        )


# 向后兼容性别名
Action = BaseAction  # 通用别名
EditAction = MacroAction  # 编辑器动作别名
ZZZAction = GameSpecificAction  # ZZZ游戏动作别名


__all__ = [
    'ActionType', 'ActionStatus', 'BaseAction', 'AutomationAction', 
    'BattleAction', 'GameSpecificAction', 'UIAction', 'MacroAction',
    'ActionSequence', 'ActionFactory', 'Action', 'EditAction', 'ZZZAction'
] 