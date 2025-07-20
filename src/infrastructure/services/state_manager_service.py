"""
状态管理器服务实现

基于Clean Architecture的状态管理服务实现
提供游戏状态的管理、存储和历史记录功能
"""
from typing import Dict, Any, List, Optional, Callable
import logging
import time
import json
import uuid
import threading
from collections import deque
from dependency_injector.wiring import inject, Provide
from typing import TYPE_CHECKING

from ...core.interfaces.services import IStateManager, IGameAnalyzer
from ...core.interfaces.repositories import IConfigRepository

if TYPE_CHECKING:
    from ...application.containers.main_container import MainContainer


class StateManagerService(IStateManager):
    """
    状态管理器服务实现
    
    提供游戏状态的存储、加载、历史管理和变化通知功能
    """
    
    @inject
    def __init__(self,
                 config_repository: IConfigRepository = Provide['config_repository'],
                 game_analyzer: IGameAnalyzer = Provide['game_analyzer']):
        self._config_repository = config_repository
        self._game_analyzer = game_analyzer
        self._logger = logging.getLogger(__name__)
        
        # 当前状态
        self._current_state = {}
        
        # 状态历史 (使用deque实现环形缓冲区)
        self._max_history_size = 1000
        self._state_history = deque(maxlen=self._max_history_size)
        
        # 持久化状态存储
        self._persistent_states = {}
        
        # 状态变化订阅者
        self._subscribers = {}
        self._subscriber_lock = threading.Lock()
        
        # 自动保存配置
        self._auto_save_enabled = True
        self._auto_save_interval = 60.0  # 60秒
        self._last_save_time = time.time()
        
        self._load_config()
        self._initialize_default_state()
    
    def _load_config(self) -> None:
        """加载配置"""
        try:
            state_config = self._config_repository.get_config('state_manager', {})
            self._max_history_size = state_config.get('max_history_size', 1000)
            self._auto_save_enabled = state_config.get('auto_save_enabled', True)
            self._auto_save_interval = state_config.get('auto_save_interval', 60.0)
            
            # 重新配置历史缓冲区大小
            if len(self._state_history) > self._max_history_size:
                # 创建新的deque并保留最新的状态
                new_history = deque(list(self._state_history)[-self._max_history_size:], 
                                  maxlen=self._max_history_size)
                self._state_history = new_history
            else:
                self._state_history = deque(self._state_history, maxlen=self._max_history_size)
                
        except Exception as e:
            self._logger.error(f"Failed to load state manager config: {str(e)}")
    
    def _initialize_default_state(self) -> None:
        """初始化默认状态"""
        try:
            self._current_state = {
                'game_id': '',
                'scene': 'unknown',
                'player_status': {},
                'ui_elements': {},
                'system_info': {
                    'timestamp': time.time(),
                    'session_id': str(uuid.uuid4())
                },
                'custom_data': {}
            }
        except Exception as e:
            self._logger.error(f"Failed to initialize default state: {str(e)}")
    
    def get_current_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        try:
            # 添加实时信息
            state_copy = self._current_state.copy()
            state_copy['system_info']['last_access'] = time.time()
            return state_copy
        except Exception as e:
            self._logger.error(f"Failed to get current state: {str(e)}")
            return {}
    
    def update_state(self, state_data: Dict[str, Any]) -> bool:
        """更新状态"""
        try:
            # 保存旧状态到历史
            old_state = self._current_state.copy()
            old_state['system_info']['archived_at'] = time.time()
            self._state_history.append(old_state)
            
            # 更新当前状态
            if isinstance(state_data, dict):
                # 深度合并状态数据
                self._deep_merge_state(self._current_state, state_data)
            else:
                self._logger.warning("State data must be a dictionary")
                return False
            
            # 更新时间戳
            self._current_state['system_info']['timestamp'] = time.time()
            
            # 通知订阅者
            self._notify_subscribers('state_updated', self._current_state)
            
            # 自动保存检查
            if self._auto_save_enabled:
                current_time = time.time()
                if current_time - self._last_save_time >= self._auto_save_interval:
                    self._auto_save_state()
                    self._last_save_time = current_time
            
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to update state: {str(e)}")
            return False
    
    def save_state(self, state_id: str) -> bool:
        """保存状态"""
        try:
            if not state_id:
                self._logger.error("State ID cannot be empty")
                return False
            
            # 创建状态快照
            state_snapshot = {
                'id': state_id,
                'timestamp': time.time(),
                'data': self._current_state.copy()
            }
            
            # 保存到持久化存储
            self._persistent_states[state_id] = state_snapshot
            
            # 保存到配置仓储
            self._save_persistent_states()
            
            self._logger.info(f"State saved with ID: {state_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to save state '{state_id}': {str(e)}")
            return False
    
    def load_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """加载状态"""
        try:
            if state_id not in self._persistent_states:
                self._logger.warning(f"State '{state_id}' not found")
                return None
            
            state_snapshot = self._persistent_states[state_id]
            return state_snapshot['data'].copy()
            
        except Exception as e:
            self._logger.error(f"Failed to load state '{state_id}': {str(e)}")
            return None
    
    def get_state_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取状态历史"""
        try:
            # 限制返回的历史记录数量
            actual_limit = min(limit, len(self._state_history))
            
            if actual_limit <= 0:
                return []
            
            # 返回最新的历史记录
            recent_history = list(self._state_history)[-actual_limit:]
            return recent_history
            
        except Exception as e:
            self._logger.error(f"Failed to get state history: {str(e)}")
            return []
    
    def clear_state_history(self) -> bool:
        """清空状态历史"""
        try:
            self._state_history.clear()
            self._logger.info("State history cleared")
            return True
        except Exception as e:
            self._logger.error(f"Failed to clear state history: {str(e)}")
            return False
    
    def subscribe_state_change(self, callback: Callable) -> str:
        """订阅状态变化"""
        try:
            subscription_id = str(uuid.uuid4())
            
            with self._subscriber_lock:
                self._subscribers[subscription_id] = {
                    'callback': callback,
                    'created_at': time.time()
                }
            
            self._logger.info(f"State change subscription created: {subscription_id}")
            return subscription_id
            
        except Exception as e:
            self._logger.error(f"Failed to subscribe to state changes: {str(e)}")
            return ""
    
    def unsubscribe_state_change(self, subscription_id: str) -> bool:
        """取消订阅状态变化"""
        try:
            with self._subscriber_lock:
                if subscription_id in self._subscribers:
                    del self._subscribers[subscription_id]
                    self._logger.info(f"State change subscription removed: {subscription_id}")
                    return True
                else:
                    self._logger.warning(f"Subscription '{subscription_id}' not found")
                    return False
                    
        except Exception as e:
            self._logger.error(f"Failed to unsubscribe from state changes: {str(e)}")
            return False
    
    def _deep_merge_state(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """深度合并状态数据"""
        try:
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    self._deep_merge_state(target[key], value)
                else:
                    target[key] = value
        except Exception as e:
            self._logger.error(f"Failed to merge state data: {str(e)}")
    
    def _notify_subscribers(self, event_type: str, data: Any) -> None:
        """通知订阅者"""
        try:
            with self._subscriber_lock:
                subscribers_to_remove = []
                
                for subscription_id, subscriber_info in self._subscribers.items():
                    try:
                        callback = subscriber_info['callback']
                        callback(event_type, data)
                    except Exception as e:
                        self._logger.error(f"Subscriber callback failed: {str(e)}")
                        subscribers_to_remove.append(subscription_id)
                
                # 移除失败的订阅者
                for subscription_id in subscribers_to_remove:
                    del self._subscribers[subscription_id]
                    
        except Exception as e:
            self._logger.error(f"Failed to notify subscribers: {str(e)}")
    
    def _auto_save_state(self) -> None:
        """自动保存状态"""
        try:
            auto_save_id = f"auto_save_{int(time.time())}"
            self.save_state(auto_save_id)
            
            # 清理旧的自动保存
            self._cleanup_auto_saves()
            
        except Exception as e:
            self._logger.error(f"Auto save failed: {str(e)}")
    
    def _cleanup_auto_saves(self) -> None:
        """清理旧的自动保存"""
        try:
            # 保留最新的10个自动保存
            auto_save_states = {
                k: v for k, v in self._persistent_states.items() 
                if k.startswith('auto_save_')
            }
            
            if len(auto_save_states) > 10:
                # 按时间戳排序，删除最旧的
                sorted_saves = sorted(
                    auto_save_states.items(), 
                    key=lambda x: x[1]['timestamp'], 
                    reverse=True
                )
                
                for state_id, _ in sorted_saves[10:]:
                    del self._persistent_states[state_id]
                    
        except Exception as e:
            self._logger.error(f"Failed to cleanup auto saves: {str(e)}")
    
    def _save_persistent_states(self) -> bool:
        """保存持久化状态到配置"""
        try:
            self._config_repository.set_config('saved_states', self._persistent_states)
            return self._config_repository.save_configs()
        except Exception as e:
            self._logger.error(f"Failed to save persistent states: {str(e)}")
            return False
    
    def _load_persistent_states(self) -> bool:
        """从配置加载持久化状态"""
        try:
            saved_states = self._config_repository.get_config('saved_states', {})
            if isinstance(saved_states, dict):
                self._persistent_states = saved_states
                return True
            return False
        except Exception as e:
            self._logger.error(f"Failed to load persistent states: {str(e)}")
            return False
    
    def get_state_statistics(self) -> Dict[str, Any]:
        """获取状态统计信息"""
        try:
            return {
                'current_state_size': len(str(self._current_state)),
                'history_count': len(self._state_history),
                'max_history_size': self._max_history_size,
                'persistent_states_count': len(self._persistent_states),
                'subscribers_count': len(self._subscribers),
                'auto_save_enabled': self._auto_save_enabled,
                'last_save_time': self._last_save_time,
                'session_id': self._current_state.get('system_info', {}).get('session_id', '')
            }
        except Exception as e:
            self._logger.error(f"Failed to get state statistics: {str(e)}")
            return {}
    
    def reset_state(self) -> bool:
        """重置状态到默认值"""
        try:
            self._initialize_default_state()
            self._notify_subscribers('state_reset', self._current_state)
            self._logger.info("State reset to default")
            return True
        except Exception as e:
            self._logger.error(f"Failed to reset state: {str(e)}")
            return False