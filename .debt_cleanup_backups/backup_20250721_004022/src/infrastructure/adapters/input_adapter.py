"""
输入适配器实现

整合现有的InputController，提供Clean Architecture接口
"""
from typing import List, Tuple
import logging
import time
from dependency_injector.wiring import inject, Provide

from src.core.interfaces.adapters import IInputAdapter, InputAction
from src.core.interfaces.repositories import IConfigRepository
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.application.containers.main_container import MainContainer

# 导入现有的输入控制器实现
from src.input_controller import InputController, InputError


class InputAdapter(IInputAdapter):
    """
    输入适配器实现
    
    封装现有的InputController，提供统一的输入操作接口
    """
    
    @inject
    def __init__(self, config_repository: IConfigRepository = Provide['config_repository']):
        self._config_repository = config_repository
        self._logger = logging.getLogger(__name__)
        self._input_controller = None
        self._initialized = False
        self._mouse_speed = 1.0
        self._keyboard_delay = 0.05
        self._scroll_speed = 3
    
    def _ensure_initialized(self) -> bool:
        """确保输入控制器已初始化"""
        if not self._initialized:
            try:
                # 创建输入控制器实例
                self._input_controller = InputController()
                
                # 从配置中获取设置
                input_config = self._config_repository.get_config('input_controller', {})
                self._mouse_speed = input_config.get('mouse_speed', 1.0)
                self._keyboard_delay = input_config.get('keyboard_delay', 0.05)
                self._scroll_speed = input_config.get('scroll_speed', 3)
                
                self._initialized = True
                return True
                
            except Exception as e:
                self._logger.error(f"Failed to initialize input controller: {str(e)}")
                return False
        return True
    
    def click(self, x: int, y: int, button: str = 'left', duration: float = 0.1) -> bool:
        """点击操作"""
        if not self._ensure_initialized():
            return False
        
        try:
            # 移动到目标位置
            move_duration = duration * self._mouse_speed if duration > 0 else 0
            self._input_controller.move_mouse(x, y, duration=move_duration)
            
            # 执行点击
            self._input_controller.click(x=x, y=y, button=button)
            
            # 等待一段时间
            if duration > 0:
                time.sleep(duration)
            
            return True
            
        except (InputError, Exception) as e:
            self._logger.error(f"Click operation failed: {str(e)}")
            return False
    
    def double_click(self, x: int, y: int, button: str = 'left') -> bool:
        """双击操作"""
        if not self._ensure_initialized():
            return False
        
        try:
            # 移动到目标位置
            self._input_controller.move_mouse(x, y)
            
            # 执行双击
            self._input_controller.click(x=x, y=y, button=button, clicks=2, interval=0.1)
            
            return True
            
        except (InputError, Exception) as e:
            self._logger.error(f"Double click operation failed: {str(e)}")
            return False
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1.0) -> bool:
        """拖拽操作"""
        if not self._ensure_initialized():
            return False
        
        try:
            # 移动到起始位置
            self._input_controller.move_mouse(start_x, start_y)
            
            # 按下鼠标按钮
            import pyautogui
            pyautogui.mouseDown()
            
            # 拖拽到目标位置
            drag_duration = duration * self._mouse_speed
            self._input_controller.move_mouse(end_x, end_y, duration=drag_duration)
            
            # 释放鼠标按钮
            pyautogui.mouseUp()
            
            return True
            
        except (InputError, Exception) as e:
            self._logger.error(f"Drag operation failed: {str(e)}")
            return False
    
    def scroll(self, x: int, y: int, direction: str, amount: int = 1) -> bool:
        """滚动操作"""
        if not self._ensure_initialized():
            return False
        
        try:
            # 移动到目标位置
            self._input_controller.move_mouse(x, y)
            
            # 计算滚动量
            scroll_amount = amount * self._scroll_speed
            if direction.lower() == 'down':
                scroll_amount = -scroll_amount
            
            # 执行滚动
            self._input_controller.scroll(scroll_amount, x=x, y=y)
            
            return True
            
        except (InputError, Exception) as e:
            self._logger.error(f"Scroll operation failed: {str(e)}")
            return False
    
    def press_key(self, key: str, duration: float = 0.1) -> bool:
        """按键操作"""
        if not self._ensure_initialized():
            return False
        
        try:
            # 执行按键操作
            press_duration = duration if duration > 0 else self._keyboard_delay
            self._input_controller.press_key(key, duration=press_duration)
            
            return True
            
        except (InputError, Exception) as e:
            self._logger.error(f"Key press operation failed: {str(e)}")
            return False
    
    def press_key_combination(self, keys: List[str]) -> bool:
        """组合键操作"""
        if not self._ensure_initialized():
            return False
        
        try:
            import keyboard
            
            # 按下所有按键
            for key in keys:
                keyboard.press(key)
                time.sleep(0.01)  # 短暂延迟
            
            # 等待一段时间
            time.sleep(self._keyboard_delay)
            
            # 释放所有按键（逆序）
            for key in reversed(keys):
                keyboard.release(key)
                time.sleep(0.01)  # 短暂延迟
            
            return True
            
        except Exception as e:
            self._logger.error(f"Key combination operation failed: {str(e)}")
            return False
    
    def type_text(self, text: str, delay: float = 0.05) -> bool:
        """输入文本"""
        if not self._ensure_initialized():
            return False
        
        try:
            # 计算输入间隔
            type_delay = delay if delay > 0 else self._keyboard_delay
            
            # 输入文本
            self._input_controller.type_string(text, interval=type_delay)
            
            return True
            
        except (InputError, Exception) as e:
            self._logger.error(f"Text input operation failed: {str(e)}")
            return False
    
    def execute_action(self, action: InputAction) -> bool:
        """执行输入操作"""
        if not self._ensure_initialized():
            return False
        
        try:
            action_type = action.action_type.lower()
            
            if action_type == 'click':
                return self.click(
                    action.x or 0, 
                    action.y or 0, 
                    action.button or 'left', 
                    action.duration or 0.1
                )
            
            elif action_type == 'double_click':
                return self.double_click(
                    action.x or 0, 
                    action.y or 0, 
                    action.button or 'left'
                )
            
            elif action_type == 'drag':
                # 拖拽需要额外的结束坐标信息
                if hasattr(action, 'end_x') and hasattr(action, 'end_y'):
                    return self.drag(
                        action.x or 0, 
                        action.y or 0, 
                        action.end_x, 
                        action.end_y, 
                        action.duration or 1.0
                    )
                else:
                    self._logger.error("Drag action requires end_x and end_y coordinates")
                    return False
            
            elif action_type == 'scroll':
                direction = getattr(action, 'direction', 'up')
                amount = getattr(action, 'amount', 1)
                return self.scroll(
                    action.x or 0, 
                    action.y or 0, 
                    direction, 
                    amount
                )
            
            elif action_type == 'key':
                return self.press_key(
                    action.key or '', 
                    action.duration or 0.1
                )
            
            elif action_type == 'type':
                text = getattr(action, 'text', '')
                delay = action.delay or 0.05
                return self.type_text(text, delay)
            
            else:
                self._logger.error(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            self._logger.error(f"Action execution failed: {str(e)}")
            return False
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """获取鼠标位置"""
        if not self._ensure_initialized():
            return (0, 0)
        
        try:
            return self._input_controller.get_mouse_position()
        except (InputError, Exception) as e:
            self._logger.error(f"Failed to get mouse position: {str(e)}")
            return (0, 0)
    
    def set_mouse_position(self, x: int, y: int) -> bool:
        """设置鼠标位置"""
        if not self._ensure_initialized():
            return False
        
        try:
            self._input_controller.move_mouse(x, y)
            return True
        except (InputError, Exception) as e:
            self._logger.error(f"Failed to set mouse position: {str(e)}")
            return False
    
    def get_input_controller_instance(self) -> InputController:
        """获取底层输入控制器实例（用于兼容性）"""
        self._ensure_initialized()
        return self._input_controller
    
    def set_input_settings(self, mouse_speed: float = None, keyboard_delay: float = None, scroll_speed: int = None) -> bool:
        """设置输入参数"""
        try:
            if mouse_speed is not None:
                self._mouse_speed = mouse_speed
            if keyboard_delay is not None:
                self._keyboard_delay = keyboard_delay
            if scroll_speed is not None:
                self._scroll_speed = scroll_speed
            
            # 保存到配置
            input_config = self._config_repository.get_config('input_controller', {})
            if mouse_speed is not None:
                input_config['mouse_speed'] = mouse_speed
            if keyboard_delay is not None:
                input_config['keyboard_delay'] = keyboard_delay
            if scroll_speed is not None:
                input_config['scroll_speed'] = scroll_speed
            
            self._config_repository.set_config('input_controller', input_config)
            
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to set input settings: {str(e)}")
            return False