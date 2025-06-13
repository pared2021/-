from typing import Dict, Any, List, Optional, Tuple
import time
import random
import numpy as np
from src.services.logger import GameLogger
from src.services.action_simulator import ActionSimulator
from src.services.game_state import GameState
from src.services.image_processor import ImageProcessor
from src.services.config import Config

class ActionType:
    """动作类型"""
    CLICK = "click"
    RIGHT_CLICK = "right_click" 
    MOVE = "move"
    KEY_PRESS = "key_press"
    WAIT = "wait"
    NONE = "none"

class AutoOperator:
    """自动操作服务
    
    根据游戏状态自动执行相应操作。
    
    Attributes:
        logger: 日志服务
        action_simulator: 动作模拟服务
        game_state: 游戏状态服务
        image_processor: 图像处理服务
        config: 配置服务
    """
    
    def __init__(self, 
                 logger: GameLogger, 
                 action_simulator: ActionSimulator, 
                 game_state: GameState,
                 image_processor: ImageProcessor,
                 config: Config):
        """初始化自动操作服务
        
        Args:
            logger: 日志服务
            action_simulator: 动作模拟服务
            game_state: 游戏状态服务
            image_processor: 图像处理服务
            config: 配置服务
        """
        self.logger = logger
        self.action_simulator = action_simulator
        self.game_state = game_state
        self.image_processor = image_processor
        self.config = config
        
        # 初始化状态
        self._current_action = None
        self._last_action_time = 0
        self.action_rules = []
        
        # 初始化规则
        self._init_rules()
        
    def _init_rules(self):
        """初始化操作规则"""
        # 这里定义基本的操作规则，可以根据需要扩展
        self.action_rules = [
            # 规则格式: (状态条件函数, 动作函数, 优先级)
            (self._is_window_invalid, self._refresh_window, 20),  # 窗口无效时优先刷新
            (self._is_button_visible, self._click_button, 10),
            (self._is_enemy_visible, self._attack_enemy, 5),
            (self._is_item_pickable, self._pick_item, 8),
            (self._is_dialog_open, self._close_dialog, 9),
            (self._should_move_forward, self._move_forward, 3),
            (self._is_health_low, self._use_health_potion, 15),
            # 更多规则...
        ]
    
    def select_action(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """根据游戏状态选择操作
        
        根据当前游戏状态和预定义的规则选择要执行的操作。
        
        Args:
            state: 游戏状态
            
        Returns:
            操作描述字典，包含操作类型和参数
        """
        try:
            # 检查状态是否有效
            if not state:
                self.logger.warning("无法选择操作：状态为空")
                return {"type": ActionType.WAIT, "duration": 1.0}
                
            # 检查冷却时间
            current_time = time.time()
            if current_time - self._last_action_time < self.config.action.min_random_delay:
                return None
                
            # 应用规则并获取可行动作列表
            possible_actions = []
            for condition_func, action_func, priority in self.action_rules:
                try:
                    if condition_func(state):
                        action = action_func(state)
                        if action and isinstance(action, dict) and "type" in action:
                            possible_actions.append((action, priority))
                except Exception as e:
                    self.logger.warning(f"应用规则 {condition_func.__name__} 失败: {str(e)}")
            
            # 按优先级排序
            if possible_actions:
                possible_actions.sort(key=lambda x: x[1], reverse=True)
                self._current_action = possible_actions[0][0]
                self._last_action_time = current_time
                return self._current_action
                
            # 如果没有可行动作，返回等待
            return {"type": ActionType.WAIT, "duration": 0.5}
            
        except Exception as e:
            self.logger.error(f"选择操作失败: {str(e)}")
            return {"type": ActionType.WAIT, "duration": 1.0}
    
    def execute_action(self, action: Dict[str, Any]) -> bool:
        """执行操作
        
        根据操作描述执行相应的操作。
        
        Args:
            action: 操作描述字典
            
        Returns:
            操作是否成功
        """
        try:
            # 检查操作是否有效
            if not action or not isinstance(action, dict) or "type" not in action:
                self.logger.warning(f"无效的操作: {action}")
                return False
            
            action_type = action.get("type")
            
            # 检查窗口是否激活，除非是等待操作
            if action_type != ActionType.WAIT:
                window_active = self.action_simulator.check_window_active()
                if not window_active:
                    self.logger.warning("游戏窗口未激活，无法执行操作")
                    return False
            
            if action_type == ActionType.CLICK:
                position = action.get("position")
                if not position or not isinstance(position, tuple) or len(position) != 2:
                    self.logger.warning(f"无效的点击位置: {position}")
                    return False
                    
                x, y = position
                self.action_simulator.click(x, y)
                self.logger.debug(f"点击位置: ({x}, {y})")
                
            elif action_type == ActionType.RIGHT_CLICK:
                position = action.get("position")
                if not position or not isinstance(position, tuple) or len(position) != 2:
                    self.logger.warning(f"无效的右键点击位置: {position}")
                    return False
                    
                x, y = position
                self.action_simulator.click(x, y, button='right')
                self.logger.debug(f"右键点击位置: ({x}, {y})")
                
            elif action_type == ActionType.MOVE:
                position = action.get("position")
                if not position or not isinstance(position, tuple) or len(position) != 2:
                    self.logger.warning(f"无效的移动位置: {position}")
                    return False
                    
                x, y = position
                self.action_simulator.move_to(x, y)
                self.logger.debug(f"移动到位置: ({x}, {y})")
                
            elif action_type == ActionType.KEY_PRESS:
                key = action.get("key", "")
                if not key:
                    self.logger.warning("无效的按键")
                    return False
                    
                self.action_simulator.press_key(key)
                self.logger.debug(f"按下按键: {key}")
                
            elif action_type == ActionType.WAIT:
                duration = action.get("duration", 1.0)
                if not isinstance(duration, (int, float)) or duration <= 0:
                    duration = 1.0
                    
                time.sleep(duration)
                self.logger.debug(f"等待: {duration}秒")
                
            else:
                self.logger.warning(f"未知操作类型: {action_type}")
                return False
                
            # 添加随机延迟
            if action_type != ActionType.WAIT:  # 等待操作不需要额外延迟
                delay = random.uniform(
                    self.config.action.min_random_delay,
                    self.config.action.max_random_delay
                )
                time.sleep(delay)
                self.logger.debug(f"随机延迟: {delay}秒")
                
            return True
            
        except Exception as e:
            self.logger.error(f"执行操作失败: {str(e)}")
            return False
    
    # 以下是状态条件函数，根据游戏状态返回布尔值
    
    def _is_button_visible(self, state: Dict[str, Any]) -> bool:
        """检查按钮是否可见"""
        buttons = state.get("buttons", [])
        return len(buttons) > 0
    
    def _is_enemy_visible(self, state: Dict[str, Any]) -> bool:
        """检查敌人是否可见"""
        enemies = state.get("enemies", [])
        return len(enemies) > 0
    
    def _is_item_pickable(self, state: Dict[str, Any]) -> bool:
        """检查是否有可拾取物品"""
        items = state.get("items", [])
        return len(items) > 0
    
    def _is_dialog_open(self, state: Dict[str, Any]) -> bool:
        """检查对话框是否打开"""
        return state.get("dialog_open", False)
    
    def _should_move_forward(self, state: Dict[str, Any]) -> bool:
        """检查是否应该向前移动"""
        # 如果没有其他明确目标，且道路清晰，则应该向前移动
        if (not self._is_button_visible(state) and 
            not self._is_enemy_visible(state) and 
            not self._is_item_pickable(state) and 
            not self._is_dialog_open(state)):
            return True
        return False
    
    def _is_health_low(self, state: Dict[str, Any]) -> bool:
        """检查生命值是否过低"""
        health = state.get("health", 100)
        return health < 30
    
    def _is_window_invalid(self) -> bool:
        """检查游戏窗口是否无效
        
        Returns:
            bool: 如果窗口无效返回True，否则返回False
        """
        return not self.game_state.is_window_valid()
        
    def _refresh_window(self) -> bool:
        """刷新游戏窗口
        
        Returns:
            bool: 刷新成功返回True，否则返回False
        """
        self.logger.info("正在刷新游戏窗口...")
        self.game_state.refresh_windows()
        # 等待一段时间让窗口刷新生效
        self.action_simulator.sleep(1)
        return True
    
    # 以下是动作函数，根据游戏状态返回操作描述
    
    def _click_button(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """点击按钮"""
        buttons = state.get("buttons", [])
        if buttons:
            # 选择第一个按钮
            button = buttons[0]
            x, y = button.get("position", (0, 0))
            return {
                "type": ActionType.CLICK,
                "position": (x, y),
                "target": "button"
            }
        return None
    
    def _attack_enemy(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """攻击敌人"""
        enemies = state.get("enemies", [])
        if enemies:
            # 选择最近的敌人
            enemy = enemies[0]  # 假设已经按距离排序
            x, y = enemy.get("position", (0, 0))
            return {
                "type": ActionType.CLICK,
                "position": (x, y),
                "target": "enemy"
            }
        return None
    
    def _pick_item(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """拾取物品"""
        items = state.get("items", [])
        if items:
            # 选择最近的物品
            item = items[0]  # 假设已经按距离排序
            x, y = item.get("position", (0, 0))
            return {
                "type": ActionType.CLICK,
                "position": (x, y),
                "target": "item"
            }
        return None
    
    def _close_dialog(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """关闭对话框"""
        dialog = state.get("dialog", {})
        close_button = dialog.get("close_button", {})
        x, y = close_button.get("position", (0, 0))
        return {
            "type": ActionType.CLICK,
            "position": (x, y),
            "target": "dialog_close"
        }
    
    def _move_forward(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """向前移动"""
        # 使用W键向前移动
        return {
            "type": ActionType.KEY_PRESS,
            "key": "w",
            "duration": 1.0
        }
    
    def _use_health_potion(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """使用生命药水"""
        # 按H键使用生命药水
        return {
            "type": ActionType.KEY_PRESS,
            "key": "h",
            "target": "health_potion"
        }

    def check_window_state(self):
        """检查窗口状态"""
        if not self.window_manager:
            self.logger.debug("窗口管理器未初始化")
            return False
            
        return self.window_manager.is_window_active() 