"""动作模拟服务适配器

这个模块提供了动作模拟服务的适配器实现，将现有的动作模拟系统包装为符合IActionSimulatorService接口的服务。
使用适配器模式来保持向后兼容性，同时支持新的依赖注入架构。
"""

from typing import Dict, Any, Optional, List, Tuple
import time
from datetime import datetime

from ...core.interfaces.services import (
    IActionSimulatorService, ILoggerService, IWindowManagerService, IConfigService, IErrorHandler,
    Point, ActionResult, ActionType
)


class ActionSimulatorServiceAdapter(IActionSimulatorService):
    """动作模拟服务适配器
    
    将现有的动作模拟系统适配为IActionSimulatorService接口。
    提供鼠标、键盘操作模拟功能。
    """
    
    def __init__(self, logger_service: Optional[ILoggerService] = None,
                 window_manager: Optional[IWindowManagerService] = None,
                 config_service: Optional[IConfigService] = None,
                 error_handler: Optional[IErrorHandler] = None):
        self._logger_service = logger_service
        self._window_manager = window_manager
        self._config_service = config_service
        self._error_handler = error_handler
        self._action_simulator_instance = None
        self._is_initialized = False
        self._action_history: List[Dict[str, Any]] = []
        self._max_history_size = 100
        self._default_delay = 0.1
        self._action_count = 0
    
    def _ensure_action_simulator_loaded(self) -> None:
        """确保动作模拟器已加载"""
        if not self._is_initialized:
            try:
                # 尝试导入现有的动作模拟系统
                from ...common.action_simulator import action_simulator
                self._action_simulator_instance = action_simulator
                self._is_initialized = True
                self._log_info("动作模拟器已加载")
            except ImportError as e:
                self._log_error(f"无法导入现有动作模拟系统: {e}")
                # 创建一个基本的动作模拟器实现
                self._create_fallback_action_simulator()
                self._is_initialized = True
    
    def _create_fallback_action_simulator(self) -> None:
        """创建备用动作模拟器"""
        try:
            import pyautogui
            self._pyautogui = pyautogui
            # 设置安全模式
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
            self._action_simulator_instance = self
            self._log_info("使用备用动作模拟器 (pyautogui)")
        except ImportError:
            self._log_error("无法导入pyautogui，动作模拟功能将受限")
            self._action_simulator_instance = None
    
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
            self._log_error(f"动作模拟错误: {error}")
    
    def _get_delay(self) -> float:
        """获取操作延迟"""
        if self._config_service:
            return self._config_service.get('action_simulator.delay', self._default_delay)
        return self._default_delay
    
    def _record_action(self, action_type: ActionType, details: Dict[str, Any], result: ActionResult) -> None:
        """记录动作历史"""
        action_record = {
            'id': self._action_count,
            'type': action_type.value,
            'details': details,
            'result': {
                'success': result.success,
                'message': result.message,
                'execution_time': result.execution_time
            },
            'timestamp': time.time()
        }
        
        self._action_history.append(action_record)
        
        # 限制历史记录大小
        if len(self._action_history) > self._max_history_size:
            self._action_history.pop(0)
        
        self._action_count += 1
    
    def _create_action_result(self, success: bool, message: str, 
                             execution_time: float, data: Optional[Dict[str, Any]] = None) -> ActionResult:
        """创建动作结果"""
        return ActionResult(
            success=success,
            message=message,
            execution_time=execution_time,
            timestamp=time.time(),
            data=data or {}
        )
    
    def click(self, position: Point, button: str = 'left', **options) -> ActionResult:
        """点击操作"""
        self._ensure_action_simulator_loaded()
        
        start_time = time.time()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._action_simulator_instance, 'click') and 
                self._action_simulator_instance != self):
                result = self._action_simulator_instance.click(position, button, **options)
                # 转换为ActionResult格式
                action_result = self._convert_to_action_result(result, start_time)
            else:
                # 使用备用实现
                action_result = self._click_fallback(position, button, **options)
            
            # 记录动作
            self._record_action(
                ActionType.CLICK,
                {'position': position, 'button': button, 'options': options},
                action_result
            )
            
            return action_result
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_error(e, {'operation': 'click', 'position': position, 'button': button})
            return self._create_action_result(False, f"点击失败: {e}", execution_time)
    
    def _click_fallback(self, position: Point, button: str = 'left', **options) -> ActionResult:
        """备用点击实现"""
        start_time = time.time()
        
        if not hasattr(self, '_pyautogui'):
            execution_time = time.time() - start_time
            return self._create_action_result(False, "pyautogui不可用", execution_time)
        
        try:
            # 获取延迟设置
            delay = options.get('delay', self._get_delay())
            
            # 执行点击
            self._pyautogui.click(position.x, position.y, button=button)
            
            # 等待延迟
            if delay > 0:
                time.sleep(delay)
            
            execution_time = time.time() - start_time
            self._log_debug(f"点击完成: ({position.x}, {position.y}), 按钮: {button}")
            
            return self._create_action_result(
                True, 
                f"点击成功: ({position.x}, {position.y})", 
                execution_time,
                {'position': position, 'button': button}
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_error(e, {'operation': '_click_fallback'})
            return self._create_action_result(False, f"点击失败: {e}", execution_time)
    
    def double_click(self, position: Point, button: str = 'left', **options) -> ActionResult:
        """双击操作"""
        self._ensure_action_simulator_loaded()
        
        start_time = time.time()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._action_simulator_instance, 'double_click') and 
                self._action_simulator_instance != self):
                result = self._action_simulator_instance.double_click(position, button, **options)
                action_result = self._convert_to_action_result(result, start_time)
            else:
                # 使用备用实现
                action_result = self._double_click_fallback(position, button, **options)
            
            # 记录动作
            self._record_action(
                ActionType.DOUBLE_CLICK,
                {'position': position, 'button': button, 'options': options},
                action_result
            )
            
            return action_result
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_error(e, {'operation': 'double_click', 'position': position})
            return self._create_action_result(False, f"双击失败: {e}", execution_time)
    
    def _double_click_fallback(self, position: Point, button: str = 'left', **options) -> ActionResult:
        """备用双击实现"""
        start_time = time.time()
        
        if not hasattr(self, '_pyautogui'):
            execution_time = time.time() - start_time
            return self._create_action_result(False, "pyautogui不可用", execution_time)
        
        try:
            delay = options.get('delay', self._get_delay())
            
            self._pyautogui.doubleClick(position.x, position.y, button=button)
            
            if delay > 0:
                time.sleep(delay)
            
            execution_time = time.time() - start_time
            self._log_debug(f"双击完成: ({position.x}, {position.y})")
            
            return self._create_action_result(
                True, 
                f"双击成功: ({position.x}, {position.y})", 
                execution_time,
                {'position': position, 'button': button}
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_error(e, {'operation': '_double_click_fallback'})
            return self._create_action_result(False, f"双击失败: {e}", execution_time)
    
    def drag(self, start_position: Point, end_position: Point, **options) -> ActionResult:
        """拖拽操作"""
        self._ensure_action_simulator_loaded()
        
        start_time = time.time()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._action_simulator_instance, 'drag') and 
                self._action_simulator_instance != self):
                result = self._action_simulator_instance.drag(start_position, end_position, **options)
                action_result = self._convert_to_action_result(result, start_time)
            else:
                # 使用备用实现
                action_result = self._drag_fallback(start_position, end_position, **options)
            
            # 记录动作
            self._record_action(
                ActionType.DRAG,
                {'start': start_position, 'end': end_position, 'options': options},
                action_result
            )
            
            return action_result
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_error(e, {'operation': 'drag', 'start': start_position, 'end': end_position})
            return self._create_action_result(False, f"拖拽失败: {e}", execution_time)
    
    def _drag_fallback(self, start_position: Point, end_position: Point, **options) -> ActionResult:
        """备用拖拽实现"""
        start_time = time.time()
        
        if not hasattr(self, '_pyautogui'):
            execution_time = time.time() - start_time
            return self._create_action_result(False, "pyautogui不可用", execution_time)
        
        try:
            delay = options.get('delay', self._get_delay())
            duration = options.get('duration', 0.5)
            
            self._pyautogui.drag(
                end_position.x - start_position.x,
                end_position.y - start_position.y,
                duration=duration,
                button='left'
            )
            
            if delay > 0:
                time.sleep(delay)
            
            execution_time = time.time() - start_time
            self._log_debug(f"拖拽完成: ({start_position.x}, {start_position.y}) -> ({end_position.x}, {end_position.y})")
            
            return self._create_action_result(
                True, 
                f"拖拽成功: ({start_position.x}, {start_position.y}) -> ({end_position.x}, {end_position.y})", 
                execution_time,
                {'start': start_position, 'end': end_position, 'duration': duration}
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_error(e, {'operation': '_drag_fallback'})
            return self._create_action_result(False, f"拖拽失败: {e}", execution_time)
    
    def type_text(self, text: str, **options) -> ActionResult:
        """输入文本"""
        self._ensure_action_simulator_loaded()
        
        start_time = time.time()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._action_simulator_instance, 'type_text') and 
                self._action_simulator_instance != self):
                result = self._action_simulator_instance.type_text(text, **options)
                action_result = self._convert_to_action_result(result, start_time)
            else:
                # 使用备用实现
                action_result = self._type_text_fallback(text, **options)
            
            # 记录动作
            self._record_action(
                ActionType.TYPE,
                {'text': text[:50] + '...' if len(text) > 50 else text, 'options': options},
                action_result
            )
            
            return action_result
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_error(e, {'operation': 'type_text', 'text_length': len(text)})
            return self._create_action_result(False, f"文本输入失败: {e}", execution_time)
    
    def _type_text_fallback(self, text: str, **options) -> ActionResult:
        """备用文本输入实现"""
        start_time = time.time()
        
        if not hasattr(self, '_pyautogui'):
            execution_time = time.time() - start_time
            return self._create_action_result(False, "pyautogui不可用", execution_time)
        
        try:
            delay = options.get('delay', self._get_delay())
            interval = options.get('interval', 0.01)
            
            self._pyautogui.typewrite(text, interval=interval)
            
            if delay > 0:
                time.sleep(delay)
            
            execution_time = time.time() - start_time
            self._log_debug(f"文本输入完成: {len(text)} 个字符")
            
            return self._create_action_result(
                True, 
                f"文本输入成功: {len(text)} 个字符", 
                execution_time,
                {'text_length': len(text), 'interval': interval}
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_error(e, {'operation': '_type_text_fallback'})
            return self._create_action_result(False, f"文本输入失败: {e}", execution_time)
    
    def press_key(self, key: str, **options) -> ActionResult:
        """按键操作"""
        self._ensure_action_simulator_loaded()
        
        start_time = time.time()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._action_simulator_instance, 'press_key') and 
                self._action_simulator_instance != self):
                result = self._action_simulator_instance.press_key(key, **options)
                action_result = self._convert_to_action_result(result, start_time)
            else:
                # 使用备用实现
                action_result = self._press_key_fallback(key, **options)
            
            # 记录动作
            self._record_action(
                ActionType.KEY_PRESS,
                {'key': key, 'options': options},
                action_result
            )
            
            return action_result
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_error(e, {'operation': 'press_key', 'key': key})
            return self._create_action_result(False, f"按键失败: {e}", execution_time)
    
    def _press_key_fallback(self, key: str, **options) -> ActionResult:
        """备用按键实现"""
        start_time = time.time()
        
        if not hasattr(self, '_pyautogui'):
            execution_time = time.time() - start_time
            return self._create_action_result(False, "pyautogui不可用", execution_time)
        
        try:
            delay = options.get('delay', self._get_delay())
            
            self._pyautogui.press(key)
            
            if delay > 0:
                time.sleep(delay)
            
            execution_time = time.time() - start_time
            self._log_debug(f"按键完成: {key}")
            
            return self._create_action_result(
                True, 
                f"按键成功: {key}", 
                execution_time,
                {'key': key}
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_error(e, {'operation': '_press_key_fallback'})
            return self._create_action_result(False, f"按键失败: {e}", execution_time)
    
    def key_combination(self, keys: List[str], **options) -> ActionResult:
        """组合键操作"""
        self._ensure_action_simulator_loaded()
        
        start_time = time.time()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._action_simulator_instance, 'key_combination') and 
                self._action_simulator_instance != self):
                result = self._action_simulator_instance.key_combination(keys, **options)
                action_result = self._convert_to_action_result(result, start_time)
            else:
                # 使用备用实现
                action_result = self._key_combination_fallback(keys, **options)
            
            # 记录动作
            self._record_action(
                ActionType.KEY_COMBINATION,
                {'keys': keys, 'options': options},
                action_result
            )
            
            return action_result
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_error(e, {'operation': 'key_combination', 'keys': keys})
            return self._create_action_result(False, f"组合键失败: {e}", execution_time)
    
    def _key_combination_fallback(self, keys: List[str], **options) -> ActionResult:
        """备用组合键实现"""
        start_time = time.time()
        
        if not hasattr(self, '_pyautogui'):
            execution_time = time.time() - start_time
            return self._create_action_result(False, "pyautogui不可用", execution_time)
        
        try:
            delay = options.get('delay', self._get_delay())
            
            self._pyautogui.hotkey(*keys)
            
            if delay > 0:
                time.sleep(delay)
            
            execution_time = time.time() - start_time
            self._log_debug(f"组合键完成: {'+'.join(keys)}")
            
            return self._create_action_result(
                True, 
                f"组合键成功: {'+'.join(keys)}", 
                execution_time,
                {'keys': keys}
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_error(e, {'operation': '_key_combination_fallback'})
            return self._create_action_result(False, f"组合键失败: {e}", execution_time)
    
    def _convert_to_action_result(self, result: Any, start_time: float) -> ActionResult:
        """转换动作结果格式"""
        execution_time = time.time() - start_time
        
        if isinstance(result, ActionResult):
            return result
        
        if isinstance(result, dict):
            return ActionResult(
                success=result.get('success', True),
                message=result.get('message', '操作完成'),
                execution_time=result.get('execution_time', execution_time),
                timestamp=result.get('timestamp', time.time()),
                data=result.get('data', {})
            )
        
        if isinstance(result, bool):
            return self._create_action_result(
                result, 
                '操作成功' if result else '操作失败', 
                execution_time
            )
        
        return self._create_action_result(True, '操作完成', execution_time)
    
    def get_mouse_position(self) -> Point:
        """获取鼠标位置"""
        self._ensure_action_simulator_loaded()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._action_simulator_instance, 'get_mouse_position') and 
                self._action_simulator_instance != self):
                return self._action_simulator_instance.get_mouse_position()
            
            # 使用备用实现
            return self._get_mouse_position_fallback()
        
        except Exception as e:
            self._handle_error(e, {'operation': 'get_mouse_position'})
            return Point(0, 0)
    
    def _get_mouse_position_fallback(self) -> Point:
        """备用获取鼠标位置实现"""
        if not hasattr(self, '_pyautogui'):
            return Point(0, 0)
        
        try:
            x, y = self._pyautogui.position()
            return Point(x, y)
        
        except Exception as e:
            self._handle_error(e, {'operation': '_get_mouse_position_fallback'})
            return Point(0, 0)
    
    def move_mouse(self, position: Point, **options) -> ActionResult:
        """移动鼠标"""
        self._ensure_action_simulator_loaded()
        
        start_time = time.time()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._action_simulator_instance, 'move_mouse') and 
                self._action_simulator_instance != self):
                result = self._action_simulator_instance.move_mouse(position, **options)
                action_result = self._convert_to_action_result(result, start_time)
            else:
                # 使用备用实现
                action_result = self._move_mouse_fallback(position, **options)
            
            # 记录动作
            self._record_action(
                ActionType.MOUSE_MOVE,
                {'position': position, 'options': options},
                action_result
            )
            
            return action_result
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_error(e, {'operation': 'move_mouse', 'position': position})
            return self._create_action_result(False, f"鼠标移动失败: {e}", execution_time)
    
    def _move_mouse_fallback(self, position: Point, **options) -> ActionResult:
        """备用鼠标移动实现"""
        start_time = time.time()
        
        if not hasattr(self, '_pyautogui'):
            execution_time = time.time() - start_time
            return self._create_action_result(False, "pyautogui不可用", execution_time)
        
        try:
            duration = options.get('duration', 0.2)
            
            self._pyautogui.moveTo(position.x, position.y, duration=duration)
            
            execution_time = time.time() - start_time
            self._log_debug(f"鼠标移动完成: ({position.x}, {position.y})")
            
            return self._create_action_result(
                True, 
                f"鼠标移动成功: ({position.x}, {position.y})", 
                execution_time,
                {'position': position, 'duration': duration}
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_error(e, {'operation': '_move_mouse_fallback'})
            return self._create_action_result(False, f"鼠标移动失败: {e}", execution_time)
    
    def get_action_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取动作历史"""
        if limit is None:
            return self._action_history.copy()
        else:
            return self._action_history[-limit:]
    
    def clear_action_history(self) -> None:
        """清除动作历史"""
        self._action_history.clear()
        self._action_count = 0
        self._log_info("动作历史已清除")
    
    def get_action_stats(self) -> Dict[str, Any]:
        """获取动作统计"""
        action_types = {}
        success_count = 0
        total_execution_time = 0.0
        
        for action in self._action_history:
            action_type = action['type']
            action_types[action_type] = action_types.get(action_type, 0) + 1
            
            if action['result']['success']:
                success_count += 1
            
            total_execution_time += action['result']['execution_time']
        
        total_actions = len(self._action_history)
        
        return {
            'total_actions': total_actions,
            'success_rate': success_count / total_actions if total_actions > 0 else 0.0,
            'average_execution_time': total_execution_time / total_actions if total_actions > 0 else 0.0,
            'action_types': action_types,
            'total_execution_time': total_execution_time
        }
    
    def set_default_delay(self, delay: float) -> None:
        """设置默认延迟"""
        self._default_delay = max(0.0, delay)
        self._log_info(f"默认延迟已设置为: {self._default_delay}秒")
    
    def get_default_delay(self) -> float:
        """获取默认延迟"""
        return self._default_delay