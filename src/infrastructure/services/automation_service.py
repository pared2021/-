"""
自动化服务实现

基于Clean Architecture的自动化服务实现
整合游戏分析器和输入适配器提供自动化功能
"""
from typing import Dict, Any, List
import logging
import threading
import time
from dependency_injector.wiring import inject, Provide
from typing import TYPE_CHECKING

from ...core.interfaces.services import IAutomationService, IGameAnalyzer, AutomationStatus, ActionResult
from ...core.interfaces.adapters import IInputAdapter
from ...core.interfaces.repositories import IConfigRepository

if TYPE_CHECKING:
    from ...application.containers.main_container import MainContainer


class AutomationService(IAutomationService):
    """
    自动化服务实现
    
    提供游戏自动化功能，包括任务执行、状态管理等
    """
    
    @inject
    def __init__(self,
                 game_analyzer: IGameAnalyzer = Provide['game_analyzer'],
                 input_adapter: IInputAdapter = Provide['input_adapter'],
                 config_repository: IConfigRepository = Provide['config_repository']):
        self._game_analyzer = game_analyzer
        self._input_adapter = input_adapter
        self._config_repository = config_repository
        self._logger = logging.getLogger(__name__)
        
        # 自动化状态
        self._status = AutomationStatus.STOPPED
        self._current_task = None
        self._task_thread = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        
        # 配置参数
        self._action_delay = 0.1
        self._max_retry_count = 3
        self._safety_mode = True
        self._emergency_stop_key = "F12"
        
        # 统计信息
        self._task_stats = {
            'total_actions': 0,
            'successful_actions': 0,
            'failed_actions': 0,
            'start_time': None,
            'end_time': None
        }
        
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置"""
        try:
            automation_config = self._config_repository.get_config('automation', {})
            self._action_delay = automation_config.get('action_delay', 0.1)
            self._max_retry_count = automation_config.get('max_retry_count', 3)
            self._safety_mode = automation_config.get('safety_mode', True)
            self._emergency_stop_key = automation_config.get('emergency_stop_key', "F12")
        except Exception as e:
            self._logger.error(f"Failed to load automation config: {str(e)}")
    
    def start_automation(self, task_config: Dict[str, Any]) -> bool:
        """启动自动化任务"""
        try:
            if self._status != AutomationStatus.STOPPED:
                self._logger.warning("Automation is already running or paused")
                return False
            
            # 验证任务配置
            if not self.validate_task_config(task_config):
                self._logger.error("Invalid task configuration")
                return False
            
            # 重置状态
            self._stop_event.clear()
            self._pause_event.clear()
            self._current_task = task_config
            self._reset_stats()
            
            # 启动任务线程
            self._task_thread = threading.Thread(
                target=self._task_execution_loop,
                args=(task_config,),
                daemon=True
            )
            self._task_thread.start()
            
            self._status = AutomationStatus.RUNNING
            self._task_stats['start_time'] = time.time()
            
            self._logger.info(f"Automation started with task: {task_config.get('name', 'Unknown')}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to start automation: {str(e)}")
            return False
    
    def stop_automation(self) -> bool:
        """停止自动化任务"""
        try:
            if self._status == AutomationStatus.STOPPED:
                return True
            
            # 设置停止标志
            self._stop_event.set()
            
            # 等待任务线程结束
            if self._task_thread and self._task_thread.is_alive():
                self._task_thread.join(timeout=5.0)
            
            self._status = AutomationStatus.STOPPED
            self._task_stats['end_time'] = time.time()
            self._current_task = None
            
            self._logger.info("Automation stopped")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to stop automation: {str(e)}")
            return False
    
    def pause_automation(self) -> bool:
        """暂停自动化任务"""
        try:
            if self._status != AutomationStatus.RUNNING:
                return False
            
            self._pause_event.set()
            self._status = AutomationStatus.PAUSED
            
            self._logger.info("Automation paused")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to pause automation: {str(e)}")
            return False
    
    def resume_automation(self) -> bool:
        """恢复自动化任务"""
        try:
            if self._status != AutomationStatus.PAUSED:
                return False
            
            self._pause_event.clear()
            self._status = AutomationStatus.RUNNING
            
            self._logger.info("Automation resumed")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to resume automation: {str(e)}")
            return False
    
    def get_automation_status(self) -> AutomationStatus:
        """获取自动化状态"""
        return self._status
    
    def execute_action(self, action: Dict[str, Any]) -> ActionResult:
        """执行单个操作"""
        try:
            action_type = action.get('type', '').lower()
            
            if action_type == 'click':
                success = self._execute_click_action(action)
            elif action_type == 'key':
                success = self._execute_key_action(action)
            elif action_type == 'wait':
                success = self._execute_wait_action(action)
            elif action_type == 'analyze':
                success = self._execute_analyze_action(action)
            else:
                return ActionResult(
                    success=False,
                    message=f"Unknown action type: {action_type}"
                )
            
            # 更新统计信息
            self._task_stats['total_actions'] += 1
            if success:
                self._task_stats['successful_actions'] += 1
            else:
                self._task_stats['failed_actions'] += 1
            
            return ActionResult(
                success=success,
                message="Action executed successfully" if success else "Action execution failed",
                data={'action_type': action_type, 'stats': self._task_stats}
            )
            
        except Exception as e:
            self._logger.error(f"Action execution failed: {str(e)}")
            self._task_stats['total_actions'] += 1
            self._task_stats['failed_actions'] += 1
            
            return ActionResult(
                success=False,
                message=f"Action execution error: {str(e)}"
            )
    
    def get_available_actions(self) -> List[Dict[str, Any]]:
        """获取可用操作列表"""
        return [
            {
                'type': 'click',
                'description': 'Click at specified coordinates',
                'parameters': ['x', 'y', 'button', 'duration']
            },
            {
                'type': 'key',
                'description': 'Press keyboard key',
                'parameters': ['key', 'duration']
            },
            {
                'type': 'wait',
                'description': 'Wait for specified time',
                'parameters': ['duration']
            },
            {
                'type': 'analyze',
                'description': 'Analyze game frame',
                'parameters': ['elements', 'confidence_threshold']
            }
        ]
    
    def validate_task_config(self, config: Dict[str, Any]) -> bool:
        """验证任务配置"""
        try:
            # 检查必需字段
            required_fields = ['name', 'actions']
            for field in required_fields:
                if field not in config:
                    self._logger.error(f"Missing required field: {field}")
                    return False
            
            # 检查操作列表
            actions = config.get('actions', [])
            if not isinstance(actions, list) or len(actions) == 0:
                self._logger.error("Actions must be a non-empty list")
                return False
            
            # 验证每个操作
            for i, action in enumerate(actions):
                if not isinstance(action, dict):
                    self._logger.error(f"Action {i} must be a dictionary")
                    return False
                
                if 'type' not in action:
                    self._logger.error(f"Action {i} missing 'type' field")
                    return False
            
            return True
            
        except Exception as e:
            self._logger.error(f"Task config validation failed: {str(e)}")
            return False
    
    def _task_execution_loop(self, task_config: Dict[str, Any]) -> None:
        """任务执行循环"""
        try:
            actions = task_config.get('actions', [])
            repeat_count = task_config.get('repeat_count', 1)
            
            for iteration in range(repeat_count):
                if self._stop_event.is_set():
                    break
                
                self._logger.info(f"Starting iteration {iteration + 1}/{repeat_count}")
                
                for i, action in enumerate(actions):
                    # 检查停止标志
                    if self._stop_event.is_set():
                        break
                    
                    # 检查暂停标志
                    while self._pause_event.is_set() and not self._stop_event.is_set():
                        time.sleep(0.1)
                    
                    # 执行操作
                    result = self.execute_action(action)
                    
                    if not result.success and self._safety_mode:
                        retry_count = 0
                        while retry_count < self._max_retry_count and not self._stop_event.is_set():
                            self._logger.warning(f"Retrying action {i}, attempt {retry_count + 1}")
                            time.sleep(1.0)  # 重试延迟
                            
                            result = self.execute_action(action)
                            if result.success:
                                break
                            
                            retry_count += 1
                        
                        if not result.success:
                            self._logger.error(f"Action {i} failed after {self._max_retry_count} retries")
                            if self._safety_mode:
                                self._status = AutomationStatus.ERROR
                                return
                    
                    # 操作间延迟
                    if self._action_delay > 0:
                        time.sleep(self._action_delay)
                
                self._logger.info(f"Completed iteration {iteration + 1}/{repeat_count}")
            
            # 任务完成
            self._status = AutomationStatus.STOPPED
            self._task_stats['end_time'] = time.time()
            self._logger.info("Task execution completed")
            
        except Exception as e:
            self._logger.error(f"Task execution loop failed: {str(e)}")
            self._status = AutomationStatus.ERROR
    
    def _execute_click_action(self, action: Dict[str, Any]) -> bool:
        """执行点击操作"""
        try:
            x = action.get('x', 0)
            y = action.get('y', 0)
            button = action.get('button', 'left')
            duration = action.get('duration', 0.1)
            
            return self._input_adapter.click(x, y, button, duration)
        except Exception as e:
            self._logger.error(f"Click action failed: {str(e)}")
            return False
    
    def _execute_key_action(self, action: Dict[str, Any]) -> bool:
        """执行按键操作"""
        try:
            key = action.get('key', '')
            duration = action.get('duration', 0.1)
            
            if not key:
                return False
            
            return self._input_adapter.press_key(key, duration)
        except Exception as e:
            self._logger.error(f"Key action failed: {str(e)}")
            return False
    
    def _execute_wait_action(self, action: Dict[str, Any]) -> bool:
        """执行等待操作"""
        try:
            duration = action.get('duration', 1.0)
            time.sleep(duration)
            return True
        except Exception as e:
            self._logger.error(f"Wait action failed: {str(e)}")
            return False
    
    def _execute_analyze_action(self, action: Dict[str, Any]) -> bool:
        """执行分析操作"""
        try:
            # 这里需要实现游戏帧分析逻辑
            # 由于需要获取当前帧，这里简化处理
            self._logger.info("Analysis action executed (simplified)")
            return True
        except Exception as e:
            self._logger.error(f"Analyze action failed: {str(e)}")
            return False
    
    def _reset_stats(self) -> None:
        """重置统计信息"""
        self._task_stats = {
            'total_actions': 0,
            'successful_actions': 0,
            'failed_actions': 0,
            'start_time': None,
            'end_time': None
        }
    
    def get_task_stats(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        return self._task_stats.copy()
    
    def get_current_task(self) -> Dict[str, Any]:
        """获取当前任务信息"""
        return self._current_task.copy() if self._current_task else {}