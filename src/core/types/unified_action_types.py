"""统一动作类型定义"""

from enum import Enum
from typing import Set, List


class UnifiedActionType(Enum):
    """统一的动作类型枚举
    
    整合了原有的两个ActionType定义：
    - 服务接口层的基础操作类型（core/interfaces/services.py）
    - 动作系统层的扩展操作类型（common/action_system.py）
    """
    
    # 基础鼠标操作（来自两个版本的共同部分）
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    MOUSE_MOVE = "mouse_move"
    MOUSE_DRAG = "mouse_drag"
    SCROLL = "scroll"
    DRAG = "drag"
    
    # 键盘操作（来自 services.py）
    KEY_PRESS = "key_press"
    KEY_COMBINATION = "key_combination"
    KEY = "key"  # 来自 action_system.py 的简化版本
    
    # 控制操作（两个版本都有）
    WAIT = "wait"
    
    # 条件和逻辑操作（来自 action_system.py）
    CONDITION = "condition"
    
    # 游戏特定操作（来自 action_system.py）
    BATTLE = "battle"
    UI = "ui"
    MACRO = "macro"
    GAME_SPECIFIC = "game_specific"
    ZZZ_ACTION = "zzz_action"
    
    # 编辑操作（来自 action_system.py）
    EDIT = "edit"
    UNDO = "undo"
    REDO = "redo"
    
    @classmethod
    def get_basic_actions(cls) -> Set['UnifiedActionType']:
        """获取基础操作类型（来自原 services.py）"""
        return {
            cls.CLICK, cls.DOUBLE_CLICK, cls.RIGHT_CLICK,
            cls.KEY_PRESS, cls.KEY_COMBINATION, cls.MOUSE_MOVE,
            cls.SCROLL, cls.DRAG, cls.WAIT
        }
    
    @classmethod
    def get_mouse_actions(cls) -> Set['UnifiedActionType']:
        """获取鼠标相关操作"""
        return {
            cls.CLICK, cls.DOUBLE_CLICK, cls.RIGHT_CLICK,
            cls.MOUSE_MOVE, cls.MOUSE_DRAG, cls.SCROLL, cls.DRAG
        }
    
    @classmethod
    def get_keyboard_actions(cls) -> Set['UnifiedActionType']:
        """获取键盘相关操作"""
        return {cls.KEY_PRESS, cls.KEY_COMBINATION, cls.KEY}
    
    @classmethod
    def get_game_actions(cls) -> Set['UnifiedActionType']:
        """获取游戏特定操作"""
        return {
            cls.BATTLE, cls.UI, cls.MACRO, 
            cls.GAME_SPECIFIC, cls.ZZZ_ACTION
        }
    
    @classmethod
    def get_control_actions(cls) -> Set['UnifiedActionType']:
        """获取控制操作"""
        return {cls.WAIT, cls.CONDITION}
    
    @classmethod
    def get_edit_actions(cls) -> Set['UnifiedActionType']:
        """获取编辑操作"""
        return {cls.EDIT, cls.UNDO, cls.REDO}
    
    @classmethod
    def get_all_actions(cls) -> List['UnifiedActionType']:
        """获取所有操作类型"""
        return list(cls)
    
    def is_basic_action(self) -> bool:
        """检查是否为基础操作"""
        return self in self.get_basic_actions()
    
    def is_mouse_action(self) -> bool:
        """检查是否为鼠标操作"""
        return self in self.get_mouse_actions()
    
    def is_keyboard_action(self) -> bool:
        """检查是否为键盘操作"""
        return self in self.get_keyboard_actions()
    
    def is_game_action(self) -> bool:
        """检查是否为游戏特定操作"""
        return self in self.get_game_actions()
    
    def is_control_action(self) -> bool:
        """检查是否为控制操作"""
        return self in self.get_control_actions()
    
    def is_edit_action(self) -> bool:
        """检查是否为编辑操作"""
        return self in self.get_edit_actions()
    
    @classmethod
    def from_legacy_services(cls, action_type: str) -> 'UnifiedActionType':
        """从原 services.py 的ActionType转换"""
        # 映射原 services.py 中的值到统一类型
        legacy_mapping = {
            "click": cls.CLICK,
            "double_click": cls.DOUBLE_CLICK,
            "right_click": cls.RIGHT_CLICK,
            "key_press": cls.KEY_PRESS,
            "key_combination": cls.KEY_COMBINATION,
            "mouse_move": cls.MOUSE_MOVE,
            "scroll": cls.SCROLL,
            "drag": cls.DRAG,
            "wait": cls.WAIT
        }
        
        if action_type in legacy_mapping:
            return legacy_mapping[action_type]
        
        # 如果找不到映射，尝试直接转换
        try:
            return cls(action_type)
        except ValueError:
            raise ValueError(f"Unknown legacy action type: {action_type}")
    
    @classmethod
    def from_legacy_action_system(cls, action_type: str) -> 'UnifiedActionType':
        """从原 action_system.py 的ActionType转换"""
        # 映射原 action_system.py 中的值到统一类型
        legacy_mapping = {
            "click": cls.CLICK,
            "key": cls.KEY,
            "wait": cls.WAIT,
            "condition": cls.CONDITION,
            "battle": cls.BATTLE,
            "ui": cls.UI,
            "macro": cls.MACRO,
            "mouse_move": cls.MOUSE_MOVE,
            "mouse_drag": cls.MOUSE_DRAG,
            "scroll": cls.SCROLL,
            "game_specific": cls.GAME_SPECIFIC,
            "zzz_action": cls.ZZZ_ACTION,
            "edit": cls.EDIT,
            "undo": cls.UNDO,
            "redo": cls.REDO
        }
        
        if action_type in legacy_mapping:
            return legacy_mapping[action_type]
        
        # 如果找不到映射，尝试直接转换
        try:
            return cls(action_type)
        except ValueError:
            raise ValueError(f"Unknown legacy action type: {action_type}")
    
    def to_legacy_services(self) -> str:
        """转换为原 services.py 兼容的字符串"""
        # 对于不在原 services.py 中的类型，映射到最接近的基础类型
        services_mapping = {
            self.KEY: "key_press",
            self.MOUSE_DRAG: "drag",
            self.CONDITION: "wait",  # 条件操作映射为等待
            self.BATTLE: "click",    # 游戏操作映射为点击
            self.UI: "click",
            self.MACRO: "click",
            self.GAME_SPECIFIC: "click",
            self.ZZZ_ACTION: "click",
            self.EDIT: "key_press",  # 编辑操作映射为按键
            self.UNDO: "key_combination",
            self.REDO: "key_combination"
        }
        
        return services_mapping.get(self, self.value)
    
    def to_legacy_action_system(self) -> str:
        """转换为原 action_system.py 兼容的字符串"""
        # 对于不在原 action_system.py 中的类型，映射到最接近的类型
        action_system_mapping = {
            self.DOUBLE_CLICK: "click",
            self.RIGHT_CLICK: "click",
            self.KEY_PRESS: "key",
            self.KEY_COMBINATION: "key",
            self.DRAG: "mouse_drag"
        }
        
        return action_system_mapping.get(self, self.value)