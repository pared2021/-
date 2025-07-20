"""自动化服务适配器

这个模块提供了自动化服务的适配器实现，将现有的自动化系统包装为符合IAutomationService接口的服务。
使用适配器模式来保持向后兼容性，同时支持新的依赖注入架构。
"""

from typing import Dict, Any, Optional, List, Callable
import time
import asyncio
from datetime import datetime
from enum import Enum

from ...core.interfaces.services import (
    IAutomationService, ILoggerService, IConfigService, IErrorHandler,
    IGameAnalyzer, IActionSimulatorService, IGameStateService,
    AutomationStatus, ActionResult, GameState
)


class AutomationServiceAdapter(IAutomationService):
    """自动化服务适配器
    
    将现有的自动化系统适配为IAutomationService接口。
    提供自动化任务执行、管理和监控功能。
    """
    
    def __init__(self, logger_service: Optional[ILoggerService] = None,
                 config_service: Optional[IConfigService] = None,
                 error_handler: Optional[IErrorHandler] = None,
                 game_analyzer: Optional[IGameAnalyzer] = None,
                 action_simulator: Optional[IActionSimulatorService] = None,
                 game_state: Optional[IGameStateService] = None):
        self._logger_service = logger_service
        self._config_service = config_service
        self._error_handler = error_handler
        self._game_analyzer = game_analyzer
        self._action_simulator = action_simulator
        self._game_state = game_state
        
        self._automation_instance = None
        self._is_initialized = False
        
        # 自动化状态
        self._current_status = AutomationStatus.STOPPED
        self._current_task = None
        self._task_queue: List[Dict[str, Any]] = []
        self._running_tasks: Dict[str, Dict[str, Any]] = {}
        self._completed_tasks: List[Dict[str, Any]] = []
        
        # 配置
        self._max_concurrent_tasks = 1
        self._task_timeout = 300.0  # 5分钟
        self._retry_attempts = 3
        self._retry_delay = 1.0
        
        # 统计
        self._total_tasks_executed = 0
        self._successful_tasks = 0
        self._failed_tasks = 0
        self._session_start_time = time.time()
        
        # 回调
        self._status_callbacks: List[Callable] = []
        self._task_callbacks: List[Callable] = []
    
    def _ensure_automation_loaded(self) -> None:
        """确保自动化系统已加载"""
        if not self._is_initialized:
            try:
                # 尝试导入现有的自动化系统
                from ...common.auto_operator import auto_operator
                self._automation_instance = auto_operator
                self._is_initialized = True
                self._log_info("自动化系统已加载")
                
                # 同步现有状态
                self._sync_with_existing_automation()
                
            except ImportError as e:
                self._log_error(f"无法导入现有自动化系统: {e}")
                # 使用内置实现
                self._automation_instance = self
                self._is_initialized = True
                self._log_info("使用内置自动化系统")
            
            # 加载配置
            self._load_configuration()
    
    def _sync_with_existing_automation(self) -> None:
        """与现有自动化系统同步"""
        try:
            if hasattr(self._automation_instance, 'get_status'):
                status = self._automation_instance.get_status()
                if isinstance(status, str):
                    self._current_status = self._convert_string_to_status(status)
                elif isinstance(status, AutomationStatus):
                    self._current_status = status
            
            if hasattr(self._automation_instance, 'get_current_task'):
                current_task = self._automation_instance.get_current_task()
                if current_task:
                    self._current_task = current_task
            
            self._log_debug(f"已同步现有自动化状态: {self._current_status}")
        
        except Exception as e:
            self._handle_error(e, {'operation': '_sync_with_existing_automation'})
    
    def _convert_string_to_status(self, status_str: str) -> AutomationStatus:
        """将字符串状态转换为AutomationStatus枚举"""
        status_mapping = {
            'stopped': AutomationStatus.STOPPED,
            'running': AutomationStatus.RUNNING,
            'paused': AutomationStatus.PAUSED,
            'error': AutomationStatus.ERROR,
            'completed': AutomationStatus.COMPLETED
        }
        
        return status_mapping.get(status_str.lower(), AutomationStatus.STOPPED)
    
    def _load_configuration(self) -> None:
        """加载配置"""
        if self._config_service:
            self._max_concurrent_tasks = self._config_service.get('automation.max_concurrent_tasks', 1)
            self._task_timeout = self._config_service.get('automation.task_timeout', 300.0)
            self._retry_attempts = self._config_service.get('automation.retry_attempts', 3)
            self._retry_delay = self._config_service.get('automation.retry_delay', 1.0)
    
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
            self._log_error(f"自动化错误: {error}")
    
    def _notify_status_change(self, old_status: AutomationStatus, new_status: AutomationStatus) -> None:
        """通知状态变化"""
        for callback in self._status_callbacks:
            try:
                callback(old_status, new_status)
            except Exception as e:
                self._handle_error(e, {'operation': 'status_callback'})
    
    def _notify_task_event(self, event_type: str, task_data: Dict[str, Any]) -> None:
        """通知任务事件"""
        for callback in self._task_callbacks:
            try:
                callback(event_type, task_data)
            except Exception as e:
                self._handle_error(e, {'operation': 'task_callback'})
    
    def _generate_task_id(self) -> str:
        """生成任务ID"""
        return f"task_{int(time.time() * 1000)}_{len(self._completed_tasks)}"
    
    def _create_task_data(self, task_id: str, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """创建任务数据"""
        return {
            'id': task_id,
            'type': task_type,
            'parameters': parameters,
            'status': 'pending',
            'created_at': time.time(),
            'started_at': None,
            'completed_at': None,
            'result': None,
            'error': None,
            'retry_count': 0,
            'max_retries': self._retry_attempts
        }
    
    def start_automation(self, task_type: str, parameters: Optional[Dict[str, Any]] = None) -> bool:
        """启动自动化"""
        self._ensure_automation_loaded()
        
        try:
            if self._current_status == AutomationStatus.RUNNING:
                self._log_warning("自动化已在运行中")
                return False
            
            old_status = self._current_status
            
            # 如果有现有的方法，使用它
            if (hasattr(self._automation_instance, 'start_automation') and 
                self._automation_instance != self):
                success = self._automation_instance.start_automation(task_type, parameters)
                if not success:
                    return False
            
            # 创建任务
            task_id = self._generate_task_id()
            task_data = self._create_task_data(task_id, task_type, parameters or {})
            
            # 添加到队列
            self._task_queue.append(task_data)
            self._current_task = task_data
            
            # 更新状态
            self._current_status = AutomationStatus.RUNNING
            
            # 通知状态变化
            self._notify_status_change(old_status, self._current_status)
            
            # 通知任务事件
            self._notify_task_event('task_started', task_data)
            
            self._log_info(f"自动化已启动: {task_type}, 任务ID: {task_id}")
            
            # 开始执行任务
            self._execute_current_task()
            
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'start_automation', 'task_type': task_type})
            self._current_status = AutomationStatus.ERROR
            return False
    
    def _execute_current_task(self) -> None:
        """执行当前任务"""
        if not self._current_task:
            return
        
        task_data = self._current_task
        task_id = task_data['id']
        task_type = task_data['type']
        parameters = task_data['parameters']
        
        try:
            # 更新任务状态
            task_data['status'] = 'running'
            task_data['started_at'] = time.time()
            self._running_tasks[task_id] = task_data
            
            # 执行具体任务
            result = self._execute_task_by_type(task_type, parameters)
            
            # 更新任务结果
            task_data['status'] = 'completed' if result.success else 'failed'
            task_data['completed_at'] = time.time()
            task_data['result'] = result
            
            if result.success:
                self._successful_tasks += 1
                self._log_info(f"任务执行成功: {task_id}")
            else:
                self._failed_tasks += 1
                self._log_error(f"任务执行失败: {task_id}, 错误: {result.message}")
                
                # 重试逻辑
                if task_data['retry_count'] < task_data['max_retries']:
                    task_data['retry_count'] += 1
                    self._log_info(f"任务重试: {task_id}, 第 {task_data['retry_count']} 次")
                    time.sleep(self._retry_delay)
                    self._execute_current_task()
                    return
            
            # 移动到完成列表
            if task_id in self._running_tasks:
                del self._running_tasks[task_id]
            self._completed_tasks.append(task_data)
            self._total_tasks_executed += 1
            
            # 通知任务完成
            self._notify_task_event('task_completed', task_data)
            
            # 检查是否有更多任务
            if self._task_queue:
                self._current_task = self._task_queue.pop(0)
                self._execute_current_task()
            else:
                # 所有任务完成
                self._current_task = None
                old_status = self._current_status
                self._current_status = AutomationStatus.COMPLETED
                self._notify_status_change(old_status, self._current_status)
                self._log_info("所有自动化任务已完成")
        
        except Exception as e:
            # 任务执行异常
            task_data['status'] = 'error'
            task_data['completed_at'] = time.time()
            task_data['error'] = str(e)
            
            self._failed_tasks += 1
            self._handle_error(e, {'operation': '_execute_current_task', 'task_id': task_id})
            
            # 移动到完成列表
            if task_id in self._running_tasks:
                del self._running_tasks[task_id]
            self._completed_tasks.append(task_data)
            self._total_tasks_executed += 1
            
            # 更新状态为错误
            old_status = self._current_status
            self._current_status = AutomationStatus.ERROR
            self._notify_status_change(old_status, self._current_status)
            
            # 通知任务错误
            self._notify_task_event('task_error', task_data)
    
    def _execute_task_by_type(self, task_type: str, parameters: Dict[str, Any]) -> ActionResult:
        """根据任务类型执行任务"""
        start_time = time.time()
        
        try:
            # 如果有现有的执行方法，使用它
            if (hasattr(self._automation_instance, 'execute_task') and 
                self._automation_instance != self):
                result = self._automation_instance.execute_task(task_type, parameters)
                if isinstance(result, ActionResult):
                    return result
                elif isinstance(result, dict):
                    return ActionResult(
                        success=result.get('success', True),
                        message=result.get('message', '任务完成'),
                        execution_time=result.get('execution_time', time.time() - start_time),
                        timestamp=time.time(),
                        data=result.get('data', {})
                    )
                elif isinstance(result, bool):
                    return ActionResult(
                        success=result,
                        message='任务完成' if result else '任务失败',
                        execution_time=time.time() - start_time,
                        timestamp=time.time(),
                        data={}
                    )
            
            # 使用内置任务执行器
            return self._execute_builtin_task(task_type, parameters)
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_error(e, {'operation': '_execute_task_by_type', 'task_type': task_type})
            return ActionResult(
                success=False,
                message=f"任务执行异常: {e}",
                execution_time=execution_time,
                timestamp=time.time(),
                data={'error': str(e)}
            )
    
    def _execute_builtin_task(self, task_type: str, parameters: Dict[str, Any]) -> ActionResult:
        """执行内置任务"""
        start_time = time.time()
        
        try:
            if task_type == 'click':
                return self._execute_click_task(parameters)
            elif task_type == 'type_text':
                return self._execute_type_task(parameters)
            elif task_type == 'wait':
                return self._execute_wait_task(parameters)
            elif task_type == 'analyze_screen':
                return self._execute_analyze_task(parameters)
            elif task_type == 'check_state':
                return self._execute_state_check_task(parameters)
            else:
                execution_time = time.time() - start_time
                return ActionResult(
                    success=False,
                    message=f"未知任务类型: {task_type}",
                    execution_time=execution_time,
                    timestamp=time.time(),
                    data={'task_type': task_type}
                )
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_error(e, {'operation': '_execute_builtin_task', 'task_type': task_type})
            return ActionResult(
                success=False,
                message=f"内置任务执行失败: {e}",
                execution_time=execution_time,
                timestamp=time.time(),
                data={'error': str(e)}
            )
    
    def _execute_click_task(self, parameters: Dict[str, Any]) -> ActionResult:
        """执行点击任务"""
        if not self._action_simulator:
            return ActionResult(
                success=False,
                message="动作模拟器不可用",
                execution_time=0.0,
                timestamp=time.time(),
                data={}
            )
        
        from ...core.interfaces.services import Point
        
        x = parameters.get('x', 0)
        y = parameters.get('y', 0)
        button = parameters.get('button', 'left')
        
        position = Point(x, y)
        return self._action_simulator.click(position, button)
    
    def _execute_type_task(self, parameters: Dict[str, Any]) -> ActionResult:
        """执行输入任务"""
        if not self._action_simulator:
            return ActionResult(
                success=False,
                message="动作模拟器不可用",
                execution_time=0.0,
                timestamp=time.time(),
                data={}
            )
        
        text = parameters.get('text', '')
        return self._action_simulator.type_text(text)
    
    def _execute_wait_task(self, parameters: Dict[str, Any]) -> ActionResult:
        """执行等待任务"""
        start_time = time.time()
        duration = parameters.get('duration', 1.0)
        
        time.sleep(duration)
        
        execution_time = time.time() - start_time
        return ActionResult(
            success=True,
            message=f"等待完成: {duration}秒",
            execution_time=execution_time,
            timestamp=time.time(),
            data={'duration': duration}
        )
    
    def _execute_analyze_task(self, parameters: Dict[str, Any]) -> ActionResult:
        """执行屏幕分析任务"""
        if not self._game_analyzer:
            return ActionResult(
                success=False,
                message="游戏分析器不可用",
                execution_time=0.0,
                timestamp=time.time(),
                data={}
            )
        
        region = parameters.get('region')
        template = parameters.get('template')
        
        result = self._game_analyzer.analyze_screen(region, template)
        
        return ActionResult(
            success=result.success,
            message=f"屏幕分析完成: {result.message}",
            execution_time=result.execution_time,
            timestamp=time.time(),
            data=result.data
        )
    
    def _execute_state_check_task(self, parameters: Dict[str, Any]) -> ActionResult:
        """执行状态检查任务"""
        if not self._game_state:
            return ActionResult(
                success=False,
                message="游戏状态服务不可用",
                execution_time=0.0,
                timestamp=time.time(),
                data={}
            )
        
        start_time = time.time()
        expected_state = parameters.get('expected_state')
        
        if isinstance(expected_state, str):
            expected_state = GameState(expected_state)
        
        current_state = self._game_state.get_current_state()
        success = current_state == expected_state
        
        execution_time = time.time() - start_time
        
        return ActionResult(
            success=success,
            message=f"状态检查: 期望 {expected_state.value}, 实际 {current_state.value}",
            execution_time=execution_time,
            timestamp=time.time(),
            data={
                'expected_state': expected_state.value,
                'current_state': current_state.value
            }
        )
    
    def stop_automation(self) -> bool:
        """停止自动化"""
        self._ensure_automation_loaded()
        
        try:
            if self._current_status == AutomationStatus.STOPPED:
                self._log_warning("自动化已停止")
                return True
            
            old_status = self._current_status
            
            # 如果有现有的方法，使用它
            if (hasattr(self._automation_instance, 'stop_automation') and 
                self._automation_instance != self):
                success = self._automation_instance.stop_automation()
                if not success:
                    return False
            
            # 停止当前任务
            if self._current_task:
                task_data = self._current_task
                task_data['status'] = 'stopped'
                task_data['completed_at'] = time.time()
                
                # 移动到完成列表
                task_id = task_data['id']
                if task_id in self._running_tasks:
                    del self._running_tasks[task_id]
                self._completed_tasks.append(task_data)
                
                # 通知任务停止
                self._notify_task_event('task_stopped', task_data)
            
            # 清空任务队列
            self._task_queue.clear()
            self._current_task = None
            
            # 更新状态
            self._current_status = AutomationStatus.STOPPED
            
            # 通知状态变化
            self._notify_status_change(old_status, self._current_status)
            
            self._log_info("自动化已停止")
            
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'stop_automation'})
            return False
    
    def pause_automation(self) -> bool:
        """暂停自动化"""
        self._ensure_automation_loaded()
        
        try:
            if self._current_status != AutomationStatus.RUNNING:
                self._log_warning("自动化未在运行中")
                return False
            
            old_status = self._current_status
            
            # 如果有现有的方法，使用它
            if (hasattr(self._automation_instance, 'pause_automation') and 
                self._automation_instance != self):
                success = self._automation_instance.pause_automation()
                if not success:
                    return False
            
            # 更新状态
            self._current_status = AutomationStatus.PAUSED
            
            # 通知状态变化
            self._notify_status_change(old_status, self._current_status)
            
            self._log_info("自动化已暂停")
            
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'pause_automation'})
            return False
    
    def resume_automation(self) -> bool:
        """恢复自动化"""
        self._ensure_automation_loaded()
        
        try:
            if self._current_status != AutomationStatus.PAUSED:
                self._log_warning("自动化未暂停")
                return False
            
            old_status = self._current_status
            
            # 如果有现有的方法，使用它
            if (hasattr(self._automation_instance, 'resume_automation') and 
                self._automation_instance != self):
                success = self._automation_instance.resume_automation()
                if not success:
                    return False
            
            # 更新状态
            self._current_status = AutomationStatus.RUNNING
            
            # 通知状态变化
            self._notify_status_change(old_status, self._current_status)
            
            # 继续执行任务
            if self._current_task:
                self._execute_current_task()
            
            self._log_info("自动化已恢复")
            
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'resume_automation'})
            return False
    
    def get_status(self) -> AutomationStatus:
        """获取自动化状态"""
        self._ensure_automation_loaded()
        return self._current_status
    
    def get_current_task(self) -> Optional[Dict[str, Any]]:
        """获取当前任务"""
        self._ensure_automation_loaded()
        return self._current_task.copy() if self._current_task else None
    
    def get_task_queue(self) -> List[Dict[str, Any]]:
        """获取任务队列"""
        self._ensure_automation_loaded()
        return [task.copy() for task in self._task_queue]
    
    def get_completed_tasks(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取已完成任务"""
        self._ensure_automation_loaded()
        
        if limit is None:
            return [task.copy() for task in self._completed_tasks]
        else:
            return [task.copy() for task in self._completed_tasks[-limit:]]
    
    def add_task_to_queue(self, task_type: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """添加任务到队列"""
        self._ensure_automation_loaded()
        
        task_id = self._generate_task_id()
        task_data = self._create_task_data(task_id, task_type, parameters or {})
        
        self._task_queue.append(task_data)
        
        self._log_info(f"任务已添加到队列: {task_type}, 任务ID: {task_id}")
        
        return task_id
    
    def remove_task_from_queue(self, task_id: str) -> bool:
        """从队列中移除任务"""
        self._ensure_automation_loaded()
        
        for i, task in enumerate(self._task_queue):
            if task['id'] == task_id:
                removed_task = self._task_queue.pop(i)
                self._log_info(f"任务已从队列移除: {task_id}")
                return True
        
        return False
    
    def clear_task_queue(self) -> bool:
        """清空任务队列"""
        self._ensure_automation_loaded()
        
        try:
            self._task_queue.clear()
            self._log_info("任务队列已清空")
            return True
        
        except Exception as e:
            self._handle_error(e, {'operation': 'clear_task_queue'})
            return False
    
    def get_automation_statistics(self) -> Dict[str, Any]:
        """获取自动化统计信息"""
        self._ensure_automation_loaded()
        
        session_duration = time.time() - self._session_start_time
        success_rate = (self._successful_tasks / self._total_tasks_executed * 100) if self._total_tasks_executed > 0 else 0.0
        
        return {
            'current_status': self._current_status.value,
            'total_tasks_executed': self._total_tasks_executed,
            'successful_tasks': self._successful_tasks,
            'failed_tasks': self._failed_tasks,
            'success_rate': success_rate,
            'tasks_in_queue': len(self._task_queue),
            'running_tasks': len(self._running_tasks),
            'completed_tasks': len(self._completed_tasks),
            'session_duration': session_duration,
            'tasks_per_minute': (self._total_tasks_executed / (session_duration / 60)) if session_duration > 0 else 0.0
        }
    
    def add_status_callback(self, callback: Callable) -> bool:
        """添加状态变化回调"""
        self._ensure_automation_loaded()
        
        try:
            if callback not in self._status_callbacks:
                self._status_callbacks.append(callback)
                self._log_debug("状态回调已添加")
                return True
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'add_status_callback'})
            return False
    
    def remove_status_callback(self, callback: Callable) -> bool:
        """移除状态变化回调"""
        self._ensure_automation_loaded()
        
        try:
            if callback in self._status_callbacks:
                self._status_callbacks.remove(callback)
                self._log_debug("状态回调已移除")
                return True
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'remove_status_callback'})
            return False
    
    def add_task_callback(self, callback: Callable) -> bool:
        """添加任务事件回调"""
        self._ensure_automation_loaded()
        
        try:
            if callback not in self._task_callbacks:
                self._task_callbacks.append(callback)
                self._log_debug("任务回调已添加")
                return True
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'add_task_callback'})
            return False
    
    def remove_task_callback(self, callback: Callable) -> bool:
        """移除任务事件回调"""
        self._ensure_automation_loaded()
        
        try:
            if callback in self._task_callbacks:
                self._task_callbacks.remove(callback)
                self._log_debug("任务回调已移除")
                return True
            return False
        
        except Exception as e:
            self._handle_error(e, {'operation': 'remove_task_callback'})
            return False