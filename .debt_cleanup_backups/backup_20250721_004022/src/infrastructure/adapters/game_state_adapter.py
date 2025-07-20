"""游戏状态服务适配器

这个模块提供了游戏状态服务的适配器实现，将现有的游戏状态管理系统包装为符合IGameStateService接口的服务。
使用适配器模式来保持向后兼容性，同时支持新的依赖注入架构。
"""

from typing import Dict, Any, Optional, List, Set
import time
import json
from datetime import datetime
from enum import Enum

from ...core.interfaces.services import (
    IGameStateService, ILoggerService, IConfigService, IErrorHandler,
    GameState
)


class GameStateServiceAdapter(IGameStateService):
    """游戏状态服务适配器
    
    将现有的游戏状态管理系统适配为IGameStateService接口。
    提供游戏状态跟踪、管理和持久化功能。
    """
    
    def __init__(self, logger_service: Optional[ILoggerService] = None,
                 config_service: Optional[IConfigService] = None,
                 error_handler: Optional[IErrorHandler] = None):
        self._logger_service = logger_service
        self._config_service = config_service
        self._error_handler = error_handler
        self._game_state_instance = None
        self._is_initialized = False
        
        # 状态管理
        self._current_state = GameState.UNKNOWN
        self._previous_state = GameState.UNKNOWN
        self._state_history: List[Dict[str, Any]] = []
        self._state_data: Dict[str, Any] = {}
        self._state_listeners: Dict[GameState, List[callable]] = {}
        self._global_listeners: List[callable] = []
        
        # 配置
        self._max_history_size = 100
        self._auto_save_enabled = True
        self._state_file_path = None
        
        # 统计
        self._state_changes = 0
        self._session_start_time = time.time()
    
    def _ensure_game_state_loaded(self) -> None:
        """确保游戏状态管理器已加载"""
        if not self._is_initialized:
            try:
                # 尝试导入现有的游戏状态系统
                from ...common.game_state import game_state
                self._game_state_instance = game_state
                self._is_initialized = True
                self._log_info("游戏状态管理器已加载")
                
                # 同步现有状态
                self._sync_with_existing_state()
                
            except ImportError as e:
                self._log_error(f"无法导入现有游戏状态系统: {e}")
                # 使用内置实现
                self._game_state_instance = self
                self._is_initialized = True
                self._log_info("使用内置游戏状态管理器")
            
            # 加载配置
            self._load_configuration()
            
            # 尝试加载保存的状态
            self._load_saved_state()
    
    def _sync_with_existing_state(self) -> None:
        """与现有状态系统同步"""
        try:
            if hasattr(self._game_state_instance, 'get_current_state'):
                current_state = self._game_state_instance.get_current_state()
                if isinstance(current_state, str):
                    # 转换字符串状态为枚举
                    self._current_state = self._convert_string_to_game_state(current_state)
                elif isinstance(current_state, GameState):
                    self._current_state = current_state
            
            if hasattr(self._game_state_instance, 'get_state_data'):
                state_data = self._game_state_instance.get_state_data()
                if isinstance(state_data, dict):
                    self._state_data.update(state_data)
            
            self._log_debug(f"已同步现有状态: {self._current_state}")
        
        except Exception as e:
            self._handle_error(e, {'operation': '_sync_with_existing_state'})
    
    def _convert_string_to_game_state(self, state_str: str) -> GameState:
        """将字符串状态转换为GameState枚举"""
        state_mapping = {
            'unknown': GameState.UNKNOWN,
            'menu': GameState.MENU,
            'loading': GameState.LOADING,
            'playing': GameState.PLAYING,
            'paused': GameState.PAUSED,
            'game_over': GameState.GAME_OVER,
            'victory': GameState.VICTORY,
            'defeat': GameState.DEFEAT,
            'error': GameState.ERROR
        }
        
        return state_mapping.get(state_str.lower(), GameState.UNKNOWN)
    
    def _load_configuration(self) -> None:
        """加载配置"""
        if self._config_service:
            self._max_history_size = self._config_service.get('game_state.max_history_size', 100)
            self._auto_save_enabled = self._config_service.get('game_state.auto_save_enabled', True)
            self._state_file_path = self._config_service.get('game_state.save_file_path', 'game_state.json')
    
    def _load_saved_state(self) -> None:
        """加载保存的状态"""
        if not self._auto_save_enabled or not self._state_file_path:
            return
        
        try:
            import os
            if os.path.exists(self._state_file_path):
                with open(self._state_file_path, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                
                # 恢复状态数据
                if 'state_data' in saved_data:
                    self._state_data.update(saved_data['state_data'])
                
                # 恢复历史记录
                if 'state_history' in saved_data:
                    self._state_history = saved_data['state_history'][-self._max_history_size:]
                
                self._log_info(f"已加载保存的游戏状态: {self._state_file_path}")
        
        except Exception as e:
            self._handle_error(e, {'operation': '_load_saved_state', 'file_path': self._state_file_path})
    
    def _save_state(self) -> None:
        """保存状态"""
        if not self._auto_save_enabled or not self._state_file_path:
            return
        
        try:
            save_data = {
                'current_state': self._current_state.value,
                'state_data': self._state_data,
                'state_history': self._state_history[-50:],  # 只保存最近50条历史
                'last_saved': time.time()
            }
            
            with open(self._state_file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            self._log_debug(f"游戏状态已保存: {self._state_file_path}")
        
        except Exception as e:
            self._handle_error(e, {'operation': '_save_state', 'file_path': self._state_file_path})
    
    def _log_info(self, message: str, **kwargs) -> None:
        """记录信息日志"""
        if self._logger_service:
            self._logger_service.info(message, **kwargs)
    
    def _log_error(self, message: str, **kwargs) -> None:
        """记录错误日志"""
        if self._logger_service:
            self._logger_service.error(message, **kwargs)
    
    def _log_warning(self, message: str, **kwargs) -> None:
        """记录警告日志"""
        if self._logger_service:
            self._logger_service.warning(message, **kwargs)
    
    def _log_debug(self, message: str, **kwargs) -> None:
        """记录调试日志"""
        if self._logger_service:
            self._logger_service.debug(message, **kwargs)
    
    def _handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """处理错误"""
        if self._error_handler:
            self._error_handler.handle_error(error, context)
        else:
            self._log_error(f"游戏状态错误: {error}")
    
    def _record_state_change(self, old_state: GameState, new_state: GameState, 
                           data: Optional[Dict[str, Any]] = None) -> None:
        """记录状态变化"""
        change_record = {
            'timestamp': time.time(),
            'old_state': old_state.value,
            'new_state': new_state.value,
            'data': data or {},
            'change_id': self._state_changes
        }
        
        self._state_history.append(change_record)
        
        # 限制历史记录大小
        if len(self._state_history) > self._max_history_size:
            self._state_history.pop(0)
        
        self._state_changes += 1
        
        # 自动保存
        if self._auto_save_enabled:
            self._save_state()
    
    def _notify_listeners(self, old_state: GameState, new_state: GameState, 
                         data: Optional[Dict[str, Any]] = None) -> None:
        """通知状态监听器"""
        # 通知特定状态的监听器
        if new_state in self._state_listeners:
            for listener in self._state_listeners[new_state]:
                try:
                    listener(old_state, new_state, data)
                except Exception as e:
                    self._handle_error(e, {'operation': 'state_listener', 'listener': listener})
        
        # 通知全局监听器
        for listener in self._global_listeners:
            try:
                listener(old_state, new_state, data)
            except Exception as e:
                self._handle_error(e, {'operation': 'global_listener', 'listener': listener})
    
    def get_current_state(self) -> GameState:
        """获取当前游戏状态"""
        self._ensure_game_state_loaded()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._game_state_instance, 'get_current_state') and 
                self._game_state_instance != self):
                current_state = self._game_state_instance.get_current_state()
                
                # 转换为标准格式
                if isinstance(current_state, str):
                    return self._convert_string_to_game_state(current_state)
                elif isinstance(current_state, GameState):
                    return current_state
            
            return self._current_state
        
        except Exception as e:
            self._handle_error(e, {'operation': 'get_current_state'})
            return GameState.UNKNOWN
    
    def set_state(self, state: GameState, data: Optional[Dict[str, Any]] = None) -> bool:
        """设置游戏状态"""
        self._ensure_game_state_loaded()
        
        try:
            old_state = self._current_state
            
            # 如果有现有的方法，使用它
            if (hasattr(self._game_state_instance, 'set_state') and 
                self._game_state_instance != self):
                success = self._game_state_instance.set_state(state, data)
                if not success:
                    return False
            
            # 更新内部状态
            self._previous_state = old_state
            self._current_state = state
            
            # 更新状态数据
            if data:
                self._state_data.update(data)
            
            # 记录状态变化
            self._record_state_change(old_state, state, data)
            
            # 通知监听器
            self._notify_listeners(old_state, state, data)
            
            self._log_info(f"游戏状态已更新: {old_state.value} -> {state.value}")
            
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'set_state', 'state': state})
            return False
    
    def get_previous_state(self) -> GameState:
        """获取上一个游戏状态"""
        self._ensure_game_state_loaded()
        return self._previous_state
    
    def get_state_data(self, key: Optional[str] = None) -> Any:
        """获取状态数据"""
        self._ensure_game_state_loaded()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._game_state_instance, 'get_state_data') and 
                self._game_state_instance != self):
                existing_data = self._game_state_instance.get_state_data(key)
                if existing_data is not None:
                    return existing_data
            
            # 使用内部数据
            if key is None:
                return self._state_data.copy()
            else:
                return self._state_data.get(key)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'get_state_data', 'key': key})
            return None
    
    def set_state_data(self, key: str, value: Any) -> bool:
        """设置状态数据"""
        self._ensure_game_state_loaded()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._game_state_instance, 'set_state_data') and 
                self._game_state_instance != self):
                success = self._game_state_instance.set_state_data(key, value)
                if not success:
                    return False
            
            # 更新内部数据
            self._state_data[key] = value
            
            # 自动保存
            if self._auto_save_enabled:
                self._save_state()
            
            self._log_debug(f"状态数据已更新: {key} = {value}")
            
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'set_state_data', 'key': key, 'value': value})
            return False
    
    def clear_state_data(self, key: Optional[str] = None) -> bool:
        """清除状态数据"""
        self._ensure_game_state_loaded()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._game_state_instance, 'clear_state_data') and 
                self._game_state_instance != self):
                success = self._game_state_instance.clear_state_data(key)
                if not success:
                    return False
            
            # 清除内部数据
            if key is None:
                self._state_data.clear()
                self._log_info("所有状态数据已清除")
            else:
                if key in self._state_data:
                    del self._state_data[key]
                    self._log_debug(f"状态数据已清除: {key}")
            
            # 自动保存
            if self._auto_save_enabled:
                self._save_state()
            
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'clear_state_data', 'key': key})
            return False
    
    def get_state_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取状态历史"""
        self._ensure_game_state_loaded()
        
        if limit is None:
            return self._state_history.copy()
        else:
            return self._state_history[-limit:]
    
    def clear_state_history(self) -> bool:
        """清除状态历史"""
        self._ensure_game_state_loaded()
        
        try:
            self._state_history.clear()
            self._state_changes = 0
            
            # 自动保存
            if self._auto_save_enabled:
                self._save_state()
            
            self._log_info("状态历史已清除")
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'clear_state_history'})
            return False
    
    def add_state_listener(self, state: GameState, callback: callable) -> bool:
        """添加状态监听器"""
        self._ensure_game_state_loaded()
        
        try:
            if state not in self._state_listeners:
                self._state_listeners[state] = []
            
            if callback not in self._state_listeners[state]:
                self._state_listeners[state].append(callback)
                self._log_debug(f"已添加状态监听器: {state.value}")
                return True
            
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'add_state_listener', 'state': state})
            return False
    
    def remove_state_listener(self, state: GameState, callback: callable) -> bool:
        """移除状态监听器"""
        self._ensure_game_state_loaded()
        
        try:
            if state in self._state_listeners and callback in self._state_listeners[state]:
                self._state_listeners[state].remove(callback)
                self._log_debug(f"已移除状态监听器: {state.value}")
                return True
            
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'remove_state_listener', 'state': state})
            return False
    
    def add_global_listener(self, callback: callable) -> bool:
        """添加全局状态监听器"""
        self._ensure_game_state_loaded()
        
        try:
            if callback not in self._global_listeners:
                self._global_listeners.append(callback)
                self._log_debug("已添加全局状态监听器")
                return True
            
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'add_global_listener'})
            return False
    
    def remove_global_listener(self, callback: callable) -> bool:
        """移除全局状态监听器"""
        self._ensure_game_state_loaded()
        
        try:
            if callback in self._global_listeners:
                self._global_listeners.remove(callback)
                self._log_debug("已移除全局状态监听器")
                return True
            
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'remove_global_listener'})
            return False
    
    def is_state(self, state: GameState) -> bool:
        """检查是否为指定状态"""
        return self.get_current_state() == state
    
    def is_any_state(self, states: List[GameState]) -> bool:
        """检查是否为任意指定状态"""
        current_state = self.get_current_state()
        return current_state in states
    
    def get_state_duration(self, state: Optional[GameState] = None) -> float:
        """获取状态持续时间"""
        self._ensure_game_state_loaded()
        
        target_state = state or self._current_state
        current_time = time.time()
        
        # 查找最近的状态变化
        for record in reversed(self._state_history):
            if record['new_state'] == target_state.value:
                return current_time - record['timestamp']
        
        # 如果没有找到记录，返回会话开始时间
        return current_time - self._session_start_time
    
    def get_state_statistics(self) -> Dict[str, Any]:
        """获取状态统计信息"""
        self._ensure_game_state_loaded()
        
        state_counts = {}
        state_durations = {}
        total_duration = 0.0
        
        # 统计状态次数和持续时间
        for i, record in enumerate(self._state_history):
            state = record['new_state']
            state_counts[state] = state_counts.get(state, 0) + 1
            
            # 计算持续时间
            if i < len(self._state_history) - 1:
                duration = self._state_history[i + 1]['timestamp'] - record['timestamp']
            else:
                duration = time.time() - record['timestamp']
            
            if state not in state_durations:
                state_durations[state] = 0.0
            state_durations[state] += duration
            total_duration += duration
        
        # 计算百分比
        state_percentages = {}
        if total_duration > 0:
            for state, duration in state_durations.items():
                state_percentages[state] = (duration / total_duration) * 100
        
        return {
            'current_state': self._current_state.value,
            'previous_state': self._previous_state.value,
            'total_state_changes': self._state_changes,
            'session_duration': time.time() - self._session_start_time,
            'state_counts': state_counts,
            'state_durations': state_durations,
            'state_percentages': state_percentages,
            'total_tracked_duration': total_duration
        }
    
    def reset_state(self) -> bool:
        """重置状态"""
        self._ensure_game_state_loaded()
        
        try:
            old_state = self._current_state
            
            # 重置为未知状态
            self._current_state = GameState.UNKNOWN
            self._previous_state = GameState.UNKNOWN
            
            # 清除状态数据
            self._state_data.clear()
            
            # 记录重置
            self._record_state_change(old_state, GameState.UNKNOWN, {'reset': True})
            
            # 通知监听器
            self._notify_listeners(old_state, GameState.UNKNOWN, {'reset': True})
            
            self._log_info("游戏状态已重置")
            
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'reset_state'})
            return False
    
    def save_state_to_file(self, file_path: str) -> bool:
        """保存状态到文件"""
        self._ensure_game_state_loaded()
        
        try:
            save_data = {
                'current_state': self._current_state.value,
                'previous_state': self._previous_state.value,
                'state_data': self._state_data,
                'state_history': self._state_history,
                'statistics': self.get_state_statistics(),
                'saved_at': time.time(),
                'version': '1.0'
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            self._log_info(f"游戏状态已保存到文件: {file_path}")
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'save_state_to_file', 'file_path': file_path})
            return False
    
    def load_state_from_file(self, file_path: str) -> bool:
        """从文件加载状态"""
        self._ensure_game_state_loaded()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            # 恢复状态
            if 'current_state' in saved_data:
                self._current_state = GameState(saved_data['current_state'])
            
            if 'previous_state' in saved_data:
                self._previous_state = GameState(saved_data['previous_state'])
            
            if 'state_data' in saved_data:
                self._state_data = saved_data['state_data']
            
            if 'state_history' in saved_data:
                self._state_history = saved_data['state_history']
            
            self._log_info(f"游戏状态已从文件加载: {file_path}")
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'load_state_from_file', 'file_path': file_path})
            return False