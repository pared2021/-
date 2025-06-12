from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import cv2
import numpy as np
import time
from .game_analyzer import GameAnalyzer
from .logger import GameLogger

class GameState:
    """游戏状态服务，负责追踪和维护游戏状态"""
    
    def __init__(self, logger: GameLogger, game_analyzer: GameAnalyzer):
        """初始化游戏状态服务
        
        Args:
            logger: 日志服务
            game_analyzer: 游戏分析器
        """
        self.logger = logger
        self.game_analyzer = game_analyzer
        self.current_state = {}
        self.state_history = []
        self.max_history_size = 100
        
    def update_state(self, state: Dict[str, Any]):
        """更新游戏状态
        
        Args:
            state: 新的游戏状态
        """
        if not state:
            return
            
        # 添加时间戳
        if 'timestamp' not in state:
            state['timestamp'] = time.time()
            
        # 更新当前状态
        self.current_state = state
        
        # 添加到历史记录
        self.state_history.append(state)
        
        # 保持历史记录大小
        if len(self.state_history) > self.max_history_size:
            self.state_history.pop(0)
            
        self.logger.debug(f"游戏状态已更新: {state}")
        
    def get_current_state(self) -> Dict[str, Any]:
        """获取当前游戏状态
        
        Returns:
            当前游戏状态
        """
        return self.current_state
        
    def get_state_history(self) -> List[Dict[str, Any]]:
        """获取游戏状态历史
        
        Returns:
            游戏状态历史列表
        """
        return self.state_history
        
    def clear_history(self):
        """清除状态历史"""
        self.state_history = []
        
    def find_state_in_history(self, condition) -> Optional[Dict[str, Any]]:
        """在历史记录中查找满足条件的状态
        
        Args:
            condition: 条件函数，接受状态作为参数，返回布尔值
            
        Returns:
            满足条件的最新状态，如果没有则返回None
        """
        for state in reversed(self.state_history):
            if condition(state):
                return state
        return None

class StateManager:
    """状态管理器"""
    
    def __init__(self):
        self.states: Dict[str, GameState] = {}
        self.current_state: Optional[GameState] = None
        self.state_history: List[str] = []
        
    def add_state(self, state: GameState):
        """添加游戏状态"""
        self.states[state.name] = state
        
    def recognize_state(self, frame: np.ndarray, image_processor) -> Optional[GameState]:
        """识别当前游戏状态"""
        if not self.states:
            return None
            
        # 对每个状态，检查其模板是否出现在画面中
        for state in self.states.values():
            for template in state.templates:
                matches = image_processor.find_template(frame, template)
                if matches:
                    return state
                    
        return None
        
    def get_possible_actions(self) -> List[str]:
        """获取当前状态下可能的操作"""
        if self.current_state:
            return self.current_state.actions
        return []
        
    def update_state(self, new_state: GameState):
        """更新当前状态"""
        if self.current_state:
            self.state_history.append(self.current_state.name)
        self.current_state = new_state
        
    def predict_next_state(self, action: str) -> Optional[GameState]:
        """预测执行某个操作后的下一个状态"""
        if not self.current_state:
            return None
            
        # 这里可以根据历史数据和当前状态预测下一个状态
        # 目前简单实现为返回第一个可能的下一个状态
        if self.current_state.next_states:
            next_state_name = self.current_state.next_states[0]
            return self.states.get(next_state_name)
        return None 