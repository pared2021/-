"""状态管理服务适配器

这个模块提供了状态管理服务的适配器实现，将现有的状态机系统包装为符合IStateManager接口的服务。
使用适配器模式来保持向后兼容性，同时支持新的依赖注入架构。
"""

from typing import Dict, Any, Optional, List, Set, Callable
import time
import json
from datetime import datetime
from enum import Enum

from ...core.interfaces.services import (
    IStateManager, ILoggerService, IConfigService, IErrorHandler
)


class StateManagerServiceAdapter(IStateManager):
    """状态管理服务适配器
    
    将现有的状态机系统适配为IStateManager接口。
    提供状态转换、管理和监控功能。
    """
    
    def __init__(self, logger_service: Optional[ILoggerService] = None,
                 config_service: Optional[IConfigService] = None,
                 error_handler: Optional[IErrorHandler] = None):
        self._logger_service = logger_service
        self._config_service = config_service
        self._error_handler = error_handler
        self._state_manager_instance = None
        self._is_initialized = False
        
        # 状态管理
        self._current_state = 'initial'
        self._previous_state = None
        self._state_history: List[Dict[str, Any]] = []
        self._state_data: Dict[str, Any] = {}
        
        # 状态机定义
        self._states: Set[str] = {'initial'}
        self._transitions: Dict[str, Dict[str, str]] = {}
        self._state_handlers: Dict[str, List[Callable]] = {}
        self._transition_handlers: Dict[str, List[Callable]] = {}
        self._global_handlers: List[Callable] = []
        
        # 配置
        self._max_history_size = 100
        self._auto_save_enabled = True
        self._state_file_path = None
        self._strict_mode = True  # 严格模式下只允许定义的转换
        
        # 统计
        self._state_changes = 0
        self._transition_count: Dict[str, int] = {}
        self._session_start_time = time.time()
    
    def _ensure_state_manager_loaded(self) -> None:
        """确保状态管理器已加载"""
        if not self._is_initialized:
            try:
                # 尝试导入现有的状态机系统
                from ...common.state_machine import state_machine
                self._state_manager_instance = state_machine
                self._is_initialized = True
                self._log_info("状态管理器已加载")
                
                # 同步现有状态
                self._sync_with_existing_state_manager()
                
            except ImportError as e:
                self._log_error(f"无法导入现有状态机系统: {e}")
                # 使用内置实现
                self._state_manager_instance = self
                self._is_initialized = True
                self._log_info("使用内置状态管理器")
            
            # 加载配置
            self._load_configuration()
            
            # 尝试加载保存的状态
            self._load_saved_state()
    
    def _sync_with_existing_state_manager(self) -> None:
        """与现有状态管理器同步"""
        try:
            if hasattr(self._state_manager_instance, 'get_current_state'):
                current_state = self._state_manager_instance.get_current_state()
                if current_state:
                    self._current_state = str(current_state)
            
            if hasattr(self._state_manager_instance, 'get_states'):
                states = self._state_manager_instance.get_states()
                if states:
                    self._states.update(str(s) for s in states)
            
            if hasattr(self._state_manager_instance, 'get_transitions'):
                transitions = self._state_manager_instance.get_transitions()
                if isinstance(transitions, dict):
                    self._transitions.update(transitions)
            
            self._log_debug(f"已同步现有状态管理器: 当前状态 {self._current_state}")
        
        except Exception as e:
            self._handle_error(e, {'operation': '_sync_with_existing_state_manager'})
    
    def _load_configuration(self) -> None:
        """加载配置"""
        if self._config_service:
            self._max_history_size = self._config_service.get('state_manager.max_history_size', 100)
            self._auto_save_enabled = self._config_service.get('state_manager.auto_save_enabled', True)
            self._state_file_path = self._config_service.get('state_manager.save_file_path', 'state_manager.json')
            self._strict_mode = self._config_service.get('state_manager.strict_mode', True)
    
    def _load_saved_state(self) -> None:
        """加载保存的状态"""
        if not self._auto_save_enabled or not self._state_file_path:
            return
        
        try:
            import os
            if os.path.exists(self._state_file_path):
                with open(self._state_file_path, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                
                # 恢复状态
                if 'current_state' in saved_data:
                    self._current_state = saved_data['current_state']
                
                if 'states' in saved_data:
                    self._states.update(saved_data['states'])
                
                if 'transitions' in saved_data:
                    self._transitions.update(saved_data['transitions'])
                
                if 'state_data' in saved_data:
                    self._state_data.update(saved_data['state_data'])
                
                if 'state_history' in saved_data:
                    self._state_history = saved_data['state_history'][-self._max_history_size:]
                
                if 'transition_count' in saved_data:
                    self._transition_count.update(saved_data['transition_count'])
                
                self._log_info(f"已加载保存的状态管理器数据: {self._state_file_path}")
        
        except Exception as e:
            self._handle_error(e, {'operation': '_load_saved_state', 'file_path': self._state_file_path})
    
    def _save_state(self) -> None:
        """保存状态"""
        if not self._auto_save_enabled or not self._state_file_path:
            return
        
        try:
            save_data = {
                'current_state': self._current_state,
                'previous_state': self._previous_state,
                'states': list(self._states),
                'transitions': self._transitions,
                'state_data': self._state_data,
                'state_history': self._state_history[-50:],  # 只保存最近50条历史
                'transition_count': self._transition_count,
                'last_saved': time.time(),
                'version': '1.0'
            }
            
            with open(self._state_file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            self._log_debug(f"状态管理器数据已保存: {self._state_file_path}")
        
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
            self._log_error(f"状态管理错误: {error}")
    
    def _record_state_change(self, old_state: str, new_state: str, 
                           trigger: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> None:
        """记录状态变化"""
        change_record = {
            'timestamp': time.time(),
            'old_state': old_state,
            'new_state': new_state,
            'trigger': trigger,
            'data': data or {},
            'change_id': self._state_changes
        }
        
        self._state_history.append(change_record)
        
        # 限制历史记录大小
        if len(self._state_history) > self._max_history_size:
            self._state_history.pop(0)
        
        self._state_changes += 1
        
        # 更新转换计数
        transition_key = f"{old_state}->{new_state}"
        self._transition_count[transition_key] = self._transition_count.get(transition_key, 0) + 1
        
        # 自动保存
        if self._auto_save_enabled:
            self._save_state()
    
    def _notify_state_handlers(self, state: str, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        """通知状态处理器"""
        # 通知特定状态的处理器
        if state in self._state_handlers:
            for handler in self._state_handlers[state]:
                try:
                    handler(state, event_type, data)
                except Exception as e:
                    self._handle_error(e, {'operation': 'state_handler', 'state': state, 'event_type': event_type})
        
        # 通知全局处理器
        for handler in self._global_handlers:
            try:
                handler(state, event_type, data)
            except Exception as e:
                self._handle_error(e, {'operation': 'global_handler', 'state': state, 'event_type': event_type})
    
    def _notify_transition_handlers(self, from_state: str, to_state: str, 
                                  trigger: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> None:
        """通知转换处理器"""
        transition_key = f"{from_state}->{to_state}"
        
        if transition_key in self._transition_handlers:
            for handler in self._transition_handlers[transition_key]:
                try:
                    handler(from_state, to_state, trigger, data)
                except Exception as e:
                    self._handle_error(e, {'operation': 'transition_handler', 'transition': transition_key})
    
    def get_current_state(self) -> str:
        """获取当前状态"""
        self._ensure_state_manager_loaded()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._state_manager_instance, 'get_current_state') and 
                self._state_manager_instance != self):
                current_state = self._state_manager_instance.get_current_state()
                if current_state:
                    return str(current_state)
            
            return self._current_state
        
        except Exception as e:
            self._handle_error(e, {'operation': 'get_current_state'})
            return self._current_state
    
    def set_state(self, state: str, trigger: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> bool:
        """设置状态"""
        self._ensure_state_manager_loaded()
        
        try:
            old_state = self._current_state
            
            # 检查状态是否存在
            if state not in self._states:
                if self._strict_mode:
                    self._log_warning(f"状态不存在: {state}")
                    return False
                else:
                    # 非严格模式下自动添加状态
                    self._states.add(state)
                    self._log_info(f"自动添加新状态: {state}")
            
            # 检查转换是否允许
            if self._strict_mode and old_state in self._transitions:
                allowed_transitions = self._transitions[old_state]
                if trigger and trigger in allowed_transitions:
                    expected_state = allowed_transitions[trigger]
                    if expected_state != state:
                        self._log_warning(f"转换不匹配: 触发器 {trigger} 期望状态 {expected_state}, 实际状态 {state}")
                        return False
                elif not trigger:
                    # 没有触发器时，检查是否有直接转换
                    if state not in allowed_transitions.values():
                        self._log_warning(f"不允许的状态转换: {old_state} -> {state}")
                        return False
            
            # 如果有现有的方法，使用它
            if (hasattr(self._state_manager_instance, 'set_state') and 
                self._state_manager_instance != self):
                success = self._state_manager_instance.set_state(state, trigger, data)
                if not success:
                    return False
            
            # 通知状态退出
            self._notify_state_handlers(old_state, 'exit', data)
            
            # 更新状态
            self._previous_state = old_state
            self._current_state = state
            
            # 更新状态数据
            if data:
                self._state_data.update(data)
            
            # 记录状态变化
            self._record_state_change(old_state, state, trigger, data)
            
            # 通知转换处理器
            self._notify_transition_handlers(old_state, state, trigger, data)
            
            # 通知状态进入
            self._notify_state_handlers(state, 'enter', data)
            
            self._log_info(f"状态已更新: {old_state} -> {state}" + (f" (触发器: {trigger})" if trigger else ""))
            
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'set_state', 'state': state, 'trigger': trigger})
            return False
    
    def trigger_transition(self, trigger: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """触发状态转换"""
        self._ensure_state_manager_loaded()
        
        try:
            current_state = self._current_state
            
            # 检查当前状态是否有定义的转换
            if current_state not in self._transitions:
                self._log_warning(f"当前状态 {current_state} 没有定义转换")
                return False
            
            # 检查触发器是否存在
            if trigger not in self._transitions[current_state]:
                self._log_warning(f"触发器 {trigger} 在状态 {current_state} 中不存在")
                return False
            
            # 获取目标状态
            target_state = self._transitions[current_state][trigger]
            
            # 如果有现有的方法，使用它
            if (hasattr(self._state_manager_instance, 'trigger_transition') and 
                self._state_manager_instance != self):
                success = self._state_manager_instance.trigger_transition(trigger, data)
                if not success:
                    return False
            
            # 执行状态转换
            return self.set_state(target_state, trigger, data)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'trigger_transition', 'trigger': trigger})
            return False
    
    def add_state(self, state: str) -> bool:
        """添加状态"""
        self._ensure_state_manager_loaded()
        
        try:
            if state in self._states:
                self._log_warning(f"状态已存在: {state}")
                return False
            
            # 如果有现有的方法，使用它
            if (hasattr(self._state_manager_instance, 'add_state') and 
                self._state_manager_instance != self):
                success = self._state_manager_instance.add_state(state)
                if not success:
                    return False
            
            self._states.add(state)
            
            # 自动保存
            if self._auto_save_enabled:
                self._save_state()
            
            self._log_info(f"状态已添加: {state}")
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'add_state', 'state': state})
            return False
    
    def remove_state(self, state: str) -> bool:
        """移除状态"""
        self._ensure_state_manager_loaded()
        
        try:
            if state not in self._states:
                self._log_warning(f"状态不存在: {state}")
                return False
            
            if state == self._current_state:
                self._log_warning(f"无法移除当前状态: {state}")
                return False
            
            # 如果有现有的方法，使用它
            if (hasattr(self._state_manager_instance, 'remove_state') and 
                self._state_manager_instance != self):
                success = self._state_manager_instance.remove_state(state)
                if not success:
                    return False
            
            self._states.remove(state)
            
            # 清理相关的转换
            states_to_remove = []
            for from_state in self._transitions:
                triggers_to_remove = []
                for trigger, to_state in self._transitions[from_state].items():
                    if to_state == state:
                        triggers_to_remove.append(trigger)
                
                for trigger in triggers_to_remove:
                    del self._transitions[from_state][trigger]
                
                if not self._transitions[from_state]:
                    states_to_remove.append(from_state)
            
            for from_state in states_to_remove:
                del self._transitions[from_state]
            
            if state in self._transitions:
                del self._transitions[state]
            
            # 清理处理器
            if state in self._state_handlers:
                del self._state_handlers[state]
            
            # 自动保存
            if self._auto_save_enabled:
                self._save_state()
            
            self._log_info(f"状态已移除: {state}")
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'remove_state', 'state': state})
            return False
    
    def add_transition(self, from_state: str, to_state: str, trigger: str) -> bool:
        """添加状态转换"""
        self._ensure_state_manager_loaded()
        
        try:
            # 检查状态是否存在
            if from_state not in self._states:
                self._log_warning(f"源状态不存在: {from_state}")
                return False
            
            if to_state not in self._states:
                self._log_warning(f"目标状态不存在: {to_state}")
                return False
            
            # 如果有现有的方法，使用它
            if (hasattr(self._state_manager_instance, 'add_transition') and 
                self._state_manager_instance != self):
                success = self._state_manager_instance.add_transition(from_state, to_state, trigger)
                if not success:
                    return False
            
            # 添加转换
            if from_state not in self._transitions:
                self._transitions[from_state] = {}
            
            self._transitions[from_state][trigger] = to_state
            
            # 自动保存
            if self._auto_save_enabled:
                self._save_state()
            
            self._log_info(f"转换已添加: {from_state} --{trigger}--> {to_state}")
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'add_transition', 'from_state': from_state, 'to_state': to_state, 'trigger': trigger})
            return False
    
    def remove_transition(self, from_state: str, trigger: str) -> bool:
        """移除状态转换"""
        self._ensure_state_manager_loaded()
        
        try:
            if from_state not in self._transitions:
                self._log_warning(f"状态 {from_state} 没有转换")
                return False
            
            if trigger not in self._transitions[from_state]:
                self._log_warning(f"触发器 {trigger} 在状态 {from_state} 中不存在")
                return False
            
            # 如果有现有的方法，使用它
            if (hasattr(self._state_manager_instance, 'remove_transition') and 
                self._state_manager_instance != self):
                success = self._state_manager_instance.remove_transition(from_state, trigger)
                if not success:
                    return False
            
            to_state = self._transitions[from_state][trigger]
            del self._transitions[from_state][trigger]
            
            # 如果没有更多转换，移除状态条目
            if not self._transitions[from_state]:
                del self._transitions[from_state]
            
            # 自动保存
            if self._auto_save_enabled:
                self._save_state()
            
            self._log_info(f"转换已移除: {from_state} --{trigger}--> {to_state}")
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'remove_transition', 'from_state': from_state, 'trigger': trigger})
            return False
    
    def get_states(self) -> List[str]:
        """获取所有状态"""
        self._ensure_state_manager_loaded()
        return list(self._states)
    
    def get_transitions(self, from_state: Optional[str] = None) -> Dict[str, Any]:
        """获取状态转换"""
        self._ensure_state_manager_loaded()
        
        if from_state is None:
            return self._transitions.copy()
        else:
            return self._transitions.get(from_state, {}).copy()
    
    def get_available_triggers(self, state: Optional[str] = None) -> List[str]:
        """获取可用的触发器"""
        self._ensure_state_manager_loaded()
        
        target_state = state or self._current_state
        
        if target_state in self._transitions:
            return list(self._transitions[target_state].keys())
        else:
            return []
    
    def can_transition(self, from_state: str, to_state: str, trigger: Optional[str] = None) -> bool:
        """检查是否可以转换"""
        self._ensure_state_manager_loaded()
        
        if from_state not in self._transitions:
            return not self._strict_mode
        
        if trigger:
            return (trigger in self._transitions[from_state] and 
                   self._transitions[from_state][trigger] == to_state)
        else:
            return to_state in self._transitions[from_state].values()
    
    def get_state_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取状态历史"""
        self._ensure_state_manager_loaded()
        
        if limit is None:
            return self._state_history.copy()
        else:
            return self._state_history[-limit:]
    
    def clear_state_history(self) -> bool:
        """清除状态历史"""
        self._ensure_state_manager_loaded()
        
        try:
            self._state_history.clear()
            self._state_changes = 0
            self._transition_count.clear()
            
            # 自动保存
            if self._auto_save_enabled:
                self._save_state()
            
            self._log_info("状态历史已清除")
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'clear_state_history'})
            return False
    
    def add_state_handler(self, state: str, handler: Callable) -> bool:
        """添加状态处理器"""
        self._ensure_state_manager_loaded()
        
        try:
            if state not in self._state_handlers:
                self._state_handlers[state] = []
            
            if handler not in self._state_handlers[state]:
                self._state_handlers[state].append(handler)
                self._log_debug(f"已添加状态处理器: {state}")
                return True
            
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'add_state_handler', 'state': state})
            return False
    
    def remove_state_handler(self, state: str, handler: Callable) -> bool:
        """移除状态处理器"""
        self._ensure_state_manager_loaded()
        
        try:
            if state in self._state_handlers and handler in self._state_handlers[state]:
                self._state_handlers[state].remove(handler)
                self._log_debug(f"已移除状态处理器: {state}")
                return True
            
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'remove_state_handler', 'state': state})
            return False
    
    def add_transition_handler(self, from_state: str, to_state: str, handler: Callable) -> bool:
        """添加转换处理器"""
        self._ensure_state_manager_loaded()
        
        try:
            transition_key = f"{from_state}->{to_state}"
            
            if transition_key not in self._transition_handlers:
                self._transition_handlers[transition_key] = []
            
            if handler not in self._transition_handlers[transition_key]:
                self._transition_handlers[transition_key].append(handler)
                self._log_debug(f"已添加转换处理器: {transition_key}")
                return True
            
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'add_transition_handler', 'from_state': from_state, 'to_state': to_state})
            return False
    
    def remove_transition_handler(self, from_state: str, to_state: str, handler: Callable) -> bool:
        """移除转换处理器"""
        self._ensure_state_manager_loaded()
        
        try:
            transition_key = f"{from_state}->{to_state}"
            
            if (transition_key in self._transition_handlers and 
                handler in self._transition_handlers[transition_key]):
                self._transition_handlers[transition_key].remove(handler)
                self._log_debug(f"已移除转换处理器: {transition_key}")
                return True
            
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'remove_transition_handler', 'from_state': from_state, 'to_state': to_state})
            return False
    
    def add_global_handler(self, handler: Callable) -> bool:
        """添加全局处理器"""
        self._ensure_state_manager_loaded()
        
        try:
            if handler not in self._global_handlers:
                self._global_handlers.append(handler)
                self._log_debug("已添加全局处理器")
                return True
            
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'add_global_handler'})
            return False
    
    def remove_global_handler(self, handler: Callable) -> bool:
        """移除全局处理器"""
        self._ensure_state_manager_loaded()
        
        try:
            if handler in self._global_handlers:
                self._global_handlers.remove(handler)
                self._log_debug("已移除全局处理器")
                return True
            
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'remove_global_handler'})
            return False
    
    def get_state_statistics(self) -> Dict[str, Any]:
        """获取状态统计信息"""
        self._ensure_state_manager_loaded()
        
        # 计算状态持续时间
        state_durations = {}
        current_time = time.time()
        
        for i, record in enumerate(self._state_history):
            state = record['new_state']
            
            if i < len(self._state_history) - 1:
                duration = self._state_history[i + 1]['timestamp'] - record['timestamp']
            else:
                duration = current_time - record['timestamp']
            
            if state not in state_durations:
                state_durations[state] = 0.0
            state_durations[state] += duration
        
        # 计算转换频率
        transition_frequencies = {}
        for transition, count in self._transition_count.items():
            session_duration = current_time - self._session_start_time
            frequency = count / (session_duration / 3600) if session_duration > 0 else 0.0  # 每小时
            transition_frequencies[transition] = frequency
        
        return {
            'current_state': self._current_state,
            'previous_state': self._previous_state,
            'total_states': len(self._states),
            'total_transitions': sum(len(transitions) for transitions in self._transitions.values()),
            'total_state_changes': self._state_changes,
            'session_duration': current_time - self._session_start_time,
            'state_durations': state_durations,
            'transition_count': self._transition_count,
            'transition_frequencies': transition_frequencies,
            'states': list(self._states),
            'available_triggers': self.get_available_triggers()
        }
    
    def reset_state_machine(self) -> bool:
        """重置状态机"""
        self._ensure_state_manager_loaded()
        
        try:
            old_state = self._current_state
            
            # 重置为初始状态
            self._current_state = 'initial'
            self._previous_state = None
            
            # 清除状态数据
            self._state_data.clear()
            
            # 记录重置
            self._record_state_change(old_state, 'initial', 'reset', {'reset': True})
            
            # 通知处理器
            self._notify_state_handlers(old_state, 'exit', {'reset': True})
            self._notify_state_handlers('initial', 'enter', {'reset': True})
            
            self._log_info("状态机已重置")
            
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'reset_state_machine'})
            return False
    
    def export_state_machine(self, file_path: str) -> bool:
        """导出状态机定义"""
        self._ensure_state_manager_loaded()
        
        try:
            export_data = {
                'states': list(self._states),
                'transitions': self._transitions,
                'current_state': self._current_state,
                'state_data': self._state_data,
                'statistics': self.get_state_statistics(),
                'exported_at': time.time(),
                'version': '1.0'
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self._log_info(f"状态机已导出到文件: {file_path}")
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'export_state_machine', 'file_path': file_path})
            return False
    
    def import_state_machine(self, file_path: str) -> bool:
        """导入状态机定义"""
        self._ensure_state_manager_loaded()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # 导入状态
            if 'states' in import_data:
                self._states = set(import_data['states'])
            
            # 导入转换
            if 'transitions' in import_data:
                self._transitions = import_data['transitions']
            
            # 导入当前状态
            if 'current_state' in import_data:
                self._current_state = import_data['current_state']
            
            # 导入状态数据
            if 'state_data' in import_data:
                self._state_data = import_data['state_data']
            
            # 自动保存
            if self._auto_save_enabled:
                self._save_state()
            
            self._log_info(f"状态机已从文件导入: {file_path}")
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'import_state_machine', 'file_path': file_path})
            return False