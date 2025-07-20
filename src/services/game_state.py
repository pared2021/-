from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import cv2
import numpy as np
import time
from .game_analyzer import GameAnalyzer
from .logger import GameLogger
from ..common.error_types import ErrorCode, StateError, ErrorContext
import json
import os

class GameState:
    """游戏状态管理服务"""
    
    def __init__(self, logger: GameLogger, game_analyzer, error_handler):
        self.logger = logger
        self.game_analyzer = game_analyzer
        self.error_handler = error_handler
        self.current_state = None
        self.state_history = []
        self.is_initialized = False
        self.state_file = "game_state.json"
        
    def initialize(self) -> bool:
        """初始化状态管理器"""
        try:
            # 加载保存的状态
            if os.path.exists(self.state_file):
                try:
                    with open(self.state_file, 'r', encoding='utf-8') as f:
                        saved_state = json.load(f)
                        self.current_state = saved_state.get('current_state')
                        self.state_history = saved_state.get('state_history', [])
                except Exception as e:
                    self.error_handler.handle_error(
                        StateError(
                            ErrorCode.STATE_LOAD_FAILED,
                            "加载保存的状态失败",
                            ErrorContext(
                                source="GameState.initialize",
                                details=str(e)
                            )
                        )
                    )
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                StateError(
                    ErrorCode.STATE_INIT_FAILED,
                    "状态管理器初始化失败",
                    ErrorContext(
                        source="GameState.initialize",
                        details=str(e)
                    )
                )
            )
            return False
            
    def get_current_state(self) -> Optional[Dict[str, Any]]:
        """获取当前状态"""
        try:
            if not self.is_initialized:
                self.error_handler.handle_error(
                    StateError(
                        ErrorCode.STATE_NOT_INITIALIZED,
                        "状态管理器未初始化",
                        ErrorContext(
                            source="GameState.get_current_state",
                            details="is_initialized is False"
                        )
                    )
                )
                return None
                
            return self.current_state
            
        except Exception as e:
            self.error_handler.handle_error(
                StateError(
                    ErrorCode.STATE_GET_FAILED,
                    "获取当前状态失败",
                    ErrorContext(
                        source="GameState.get_current_state",
                        details=str(e)
                    )
                )
            )
            return None
            
    def update_state(self, new_state: Dict[str, Any]) -> bool:
        """更新状态"""
        try:
            if not self.is_initialized:
                self.error_handler.handle_error(
                    StateError(
                        ErrorCode.STATE_NOT_INITIALIZED,
                        "状态管理器未初始化",
                        ErrorContext(
                            source="GameState.update_state",
                            details="is_initialized is False"
                        )
                    )
                )
                return False
                
            # 添加时间戳
            new_state['timestamp'] = time.time()
            
            # 更新状态历史
            if self.current_state:
                self.state_history.append(self.current_state)
                
            # 限制历史记录长度
            if len(self.state_history) > 100:
                self.state_history = self.state_history[-100:]
                
            # 更新当前状态
            self.current_state = new_state
            
            # 保存状态
            self._save_state()
            
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                StateError(
                    ErrorCode.STATE_UPDATE_FAILED,
                    "更新状态失败",
                    ErrorContext(
                        source="GameState.update_state",
                        details=str(e)
                    )
                )
            )
            return False
            
    def reset_state(self) -> bool:
        """重置状态"""
        try:
            if not self.is_initialized:
                self.error_handler.handle_error(
                    StateError(
                        ErrorCode.STATE_NOT_INITIALIZED,
                        "状态管理器未初始化",
                        ErrorContext(
                            source="GameState.reset_state",
                            details="is_initialized is False"
                        )
                    )
                )
                return False
                
            self.current_state = None
            self.state_history = []
            
            # 保存状态
            self._save_state()
            
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                StateError(
                    ErrorCode.STATE_RESET_FAILED,
                    "重置状态失败",
                    ErrorContext(
                        source="GameState.reset_state",
                        details=str(e)
                    )
                )
            )
            return False
            
    def get_state_history(self) -> List[Dict[str, Any]]:
        """获取状态历史"""
        try:
            if not self.is_initialized:
                self.error_handler.handle_error(
                    StateError(
                        ErrorCode.STATE_NOT_INITIALIZED,
                        "状态管理器未初始化",
                        ErrorContext(
                            source="GameState.get_state_history",
                            details="is_initialized is False"
                        )
                    )
                )
                return []
                
            return self.state_history
            
        except Exception as e:
            self.error_handler.handle_error(
                StateError(
                    ErrorCode.STATE_HISTORY_GET_FAILED,
                    "获取状态历史失败",
                    ErrorContext(
                        source="GameState.get_state_history",
                        details=str(e)
                    )
                )
            )
            return []
            
    def _save_state(self) -> bool:
        """保存状态到文件"""
        try:
            state_data = {
                'current_state': self.current_state,
                'state_history': self.state_history
            }
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                StateError(
                    ErrorCode.STATE_SAVE_FAILED,
                    "保存状态失败",
                    ErrorContext(
                        source="GameState._save_state",
                        details=str(e)
                    )
                )
            )
            return False
            
    def cleanup(self) -> None:
        """清理资源"""
        self.current_state = None
        self.state_history = []
        self.is_initialized = False

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