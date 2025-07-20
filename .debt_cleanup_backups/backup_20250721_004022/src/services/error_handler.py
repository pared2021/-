import time
import traceback
from typing import Dict, Any, Optional, Callable, List
from threading import Lock
from src.common.error_types import (
    GameAutomationError,
    ErrorCode,
    ErrorContext,
    ERROR_TYPE_MAP,
    WindowError,
    ImageProcessingError,
    ActionError,
    StateError,
    ModelError
)
from src.services.logger import GameLogger
import numpy as np
import psutil
import os

class ErrorHandler:
    """统一的错误处理服务"""
    
    def __init__(self, logger: GameLogger):
        self.logger = logger
        self.recovery_handlers: Dict[ErrorCode, Callable] = {}
        self.error_stats: Dict[ErrorCode, int] = {}
        self.recovery_stats: Dict[ErrorCode, int] = {}
        self.error_lock = Lock()
        self.recovery_lock = Lock()
        
        # 错误追踪
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        self.last_error_time = 0
        self.error_window = 5.0  # 5秒内的错误被视为连续错误
        
        # 恢复设置
        self.max_retries = 3
        self.retry_delay = 1.0
        self.recovery_attempts = 0
        self.max_recovery_attempts = 5
        self.last_recovery_time = 0
        
        # 服务引用（延迟初始化）
        self.window_manager = None
        self.image_processor = None
        self.action_simulator = None
        self.game_state = None
        self.game_analyzer = None
        self.config = None
        
    def set_window_manager(self, window_manager):
        """设置窗口管理器引用"""
        self.window_manager = window_manager
    
    def set_image_processor(self, image_processor):
        """设置图像处理器引用"""
        self.image_processor = image_processor
    
    def set_action_simulator(self, action_simulator):
        """设置动作模拟器引用"""
        self.action_simulator = action_simulator
    
    def set_game_state(self, game_state):
        """设置游戏状态引用"""
        self.game_state = game_state
    
    def set_game_analyzer(self, game_analyzer):
        """设置游戏分析器引用"""
        self.game_analyzer = game_analyzer
    
    def set_config(self, config):
        """设置配置引用"""
        self.config = config
    
    def register_handler(self, error_code: ErrorCode, handler: Callable):
        """注册错误恢复处理函数"""
        with self.recovery_lock:
            self.recovery_handlers[error_code] = handler
            self.logger.debug(f"注册错误处理函数: {error_code.name}")
    
    def handle_error(self, error: GameAutomationError) -> bool:
        """处理错误并尝试恢复
        
        Args:
            error: 错误对象
            
        Returns:
            bool: 是否成功恢复
        """
        with self.error_lock:
            # 更新错误统计
            self.error_stats[error.error_code] = self.error_stats.get(error.error_code, 0) + 1
            
            # 检查连续错误
            current_time = time.time()
            if current_time - self.last_error_time < self.error_window:
                self.consecutive_errors += 1
            else:
                self.consecutive_errors = 1
            self.last_error_time = current_time
            
            # 记录错误
            self.logger.error(
                f"发生错误: {error.message} (错误码: {error.error_code.name})",
                extra={"error_context": error.context.details}
            )
        
        # 尝试恢复
        return self._attempt_recovery(error)
    
    def _attempt_recovery(self, error: GameAutomationError) -> bool:
        """尝试恢复错误
        
        Args:
            error: 错误对象
            
        Returns:
            bool: 是否成功恢复
        """
        with self.recovery_lock:
            current_time = time.time()
            self.last_recovery_time = current_time
            self.recovery_attempts += 1
            
            # 检查恢复尝试次数
            if self.recovery_attempts > self.max_recovery_attempts:
                self.recovery_attempts = 0
                self.logger.warning("恢复尝试次数过多，等待较长时间后再尝试")
                time.sleep(5.0)
            
            # 获取恢复处理函数
            handler = self._get_recovery_handler(error.error_code)
            if not handler:
                self.logger.warning(f"未找到错误码 {error.error_code.name} 的恢复处理函数")
                return False
            
            # 尝试恢复
            for attempt in range(self.max_retries):
                try:
                    self.logger.info(f"尝试恢复 (第 {attempt + 1} 次)")
                    handler()
                    
                    # 验证恢复是否成功
                    if self._verify_recovery(error):
                        self.logger.info("恢复成功")
                        self.consecutive_errors = 0
                        self.recovery_stats[error.error_code] = self.recovery_stats.get(error.error_code, 0) + 1
                        return True
                    else:
                        self.logger.warning(f"恢复操作完成但验证失败 (尝试 {attempt + 1}/{self.max_retries})")
                        if attempt < self.max_retries - 1:
                            time.sleep(self.retry_delay * (attempt + 2))
                        
                except Exception as e:
                    self.logger.error(f"恢复失败: {str(e)}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
            
            # 尝试备用恢复策略
            try:
                self.logger.warning("常规恢复策略失败，尝试备用恢复策略")
                success = self._backup_recovery_strategy(error)
                if success:
                    self.logger.info("备用恢复策略成功")
                    self.consecutive_errors = 0
                    self.recovery_stats[error.error_code] = self.recovery_stats.get(error.error_code, 0) + 1
                    return True
            except Exception as e:
                self.logger.error(f"备用恢复策略失败: {str(e)}")
            
            self.logger.error("所有恢复尝试均失败")
            return False
    
    def _get_recovery_handler(self, error_code: ErrorCode) -> Optional[Callable]:
        """获取错误恢复处理函数
        
        Args:
            error_code: 错误码
            
        Returns:
            Optional[Callable]: 恢复处理函数，如果不存在则返回None
        """
        # 检查是否有对应的恢复处理函数
        if error_code in self.recovery_handlers:
            return self.recovery_handlers[error_code]
        
        # 尝试使用基础错误码
        base_error_code = ErrorCode((error_code.value // 1000) * 1000)
        if base_error_code in self.recovery_handlers:
            self.logger.info(f"使用基础错误码 {base_error_code.name} 的恢复处理函数")
            return self.recovery_handlers[base_error_code]
        
        return None
    
    def _verify_recovery(self, error: GameAutomationError) -> bool:
        """验证恢复是否成功
        
        Args:
            error: 错误对象
            
        Returns:
            bool: 恢复是否成功
        """
        # 优先使用全面验证
        if self._comprehensive_recovery_verification(error):
            return True
            
        # 回退到原有的类型特定验证
        if 'Window' in str(type(error)):
            return self._verify_window_recovery(error)
        elif 'ImageProcessing' in str(type(error)):
            return self._verify_image_processing_recovery(error)
        elif 'Action' in str(type(error)):
            return self._verify_action_recovery(error)
        elif 'State' in str(type(error)):
            return self._verify_state_recovery(error)
        elif 'Model' in str(type(error)):
            return self._verify_model_recovery(error)
        
        return False
    
    def _verify_window_recovery(self, error: WindowError) -> bool:
        """验证窗口恢复是否成功"""
        if not self.window_manager:
            return False
            
        try:
            # 检查窗口是否存在
            if not self.window_manager.is_window_exists(error.window_handle):
                return False
                
            # 检查窗口是否有效
            if not self.window_manager.is_window_valid(error.window_handle):
                return False
                
            # 检查窗口是否可见
            if not self.window_manager.is_window_visible(error.window_handle):
                return False
                
            # 检查窗口是否最小化
            if self.window_manager.is_window_minimized(error.window_handle):
                return False
                
            # 尝试捕获窗口内容
            screenshot = self.window_manager.capture_window(error.window_handle)
            if screenshot is None:
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"窗口恢复验证失败: {str(e)}")
            return False
            
    def _verify_image_processing_recovery(self, error: ImageProcessingError) -> bool:
        """验证图像处理恢复是否成功"""
        if not self.image_processor:
            return False
            
        try:
            # 检查图像处理器是否初始化
            if not self.image_processor.is_initialized():
                return False
                
            # 尝试处理测试图像
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            result = self.image_processor.process_image(test_image)
            if result is None:
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"图像处理恢复验证失败: {str(e)}")
            return False
            
    def _verify_action_recovery(self, error: ActionError) -> bool:
        """验证动作恢复是否成功"""
        if not self.action_simulator:
            return False
            
        try:
            # 检查动作模拟器是否初始化
            if not self.action_simulator.is_initialized():
                return False
                
            # 尝试执行测试动作
            test_action = {"type": "mouse_move", "x": 0, "y": 0}
            result = self.action_simulator.execute_action(test_action)
            if not result:
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"动作恢复验证失败: {str(e)}")
            return False
            
    def _verify_state_recovery(self, error: StateError) -> bool:
        """验证状态恢复是否成功"""
        if not self.game_state:
            return False
            
        try:
            # 检查状态管理器是否初始化
            if not self.game_state.is_initialized():
                return False
                
            # 尝试获取当前状态
            current_state = self.game_state.get_current_state()
            if current_state is None:
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"状态恢复验证失败: {str(e)}")
            return False
            
    def _verify_model_recovery(self, error: ModelError) -> bool:
        """验证模型恢复是否成功"""
        if not self.game_analyzer:
            return False
            
        try:
            # 检查游戏分析器是否初始化
            if not self.game_analyzer.is_initialized():
                return False
                
            # 检查模型是否加载
            if not self.game_analyzer.is_model_loaded():
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"模型恢复验证失败: {str(e)}")
            return False
    
    def _backup_recovery_strategy(self, error: GameAutomationError) -> bool:
        """实现备用恢复策略
        
        Returns:
            bool: 是否成功恢复
        """
        try:
            # 首先尝试高级备用恢复
            if self._advanced_backup_recovery(error):
                return True
                
            # 如果高级恢复失败，回退到原有逻辑
            # 根据错误类型选择不同的恢复策略
            if 'Window' in str(type(error)):
                return self._backup_window_recovery(error)
            elif 'ImageProcessing' in str(type(error)):
                return self._backup_image_processing_recovery(error)
            elif 'Action' in str(type(error)):
                return self._backup_action_recovery(error)
            elif 'State' in str(type(error)):
                return self._backup_state_recovery(error)
            elif 'Model' in str(type(error)):
                return self._backup_model_recovery(error)
            
            # 通用恢复策略
            return self._generic_recovery_strategy(error)
        except Exception as e:
            self.logger.error(f"备用恢复策略执行失败: {str(e)}")
            return False
    
    def _backup_window_recovery(self, error: WindowError) -> bool:
        """窗口错误备用恢复策略"""
        if not self.window_manager:
            return False
            
        try:
            # 尝试重新查找窗口
            window_handle = self.window_manager.find_window(error.window_title)
            if window_handle:
                # 更新窗口句柄
                self.window_manager.set_window_handle(window_handle)
                # 尝试激活窗口
                self.window_manager.activate_window()
                return True
            return False
        except Exception as e:
            self.logger.error(f"窗口备用恢复失败: {str(e)}")
            return False
            
    def _backup_image_processing_recovery(self, error: ImageProcessingError) -> bool:
        """图像处理错误备用恢复策略"""
        if not self.image_processor:
            return False
            
        try:
            # 尝试重新初始化图像处理器
            self.image_processor.initialize()
            # 重新加载模板
            self.image_processor.load_templates()
            return True
        except Exception as e:
            self.logger.error(f"图像处理备用恢复失败: {str(e)}")
            return False
            
    def _backup_action_recovery(self, error: ActionError) -> bool:
        """动作错误备用恢复策略"""
        if not self.action_simulator:
            return False
            
        try:
            # 尝试重新初始化动作模拟器
            self.action_simulator.initialize()
            # 重置鼠标位置
            self.action_simulator.reset_mouse_position()
            return True
        except Exception as e:
            self.logger.error(f"动作备用恢复失败: {str(e)}")
            return False
            
    def _backup_state_recovery(self, error: StateError) -> bool:
        """状态错误备用恢复策略"""
        if not self.game_state:
            return False
            
        try:
            # 尝试重新初始化状态管理器
            self.game_state.initialize()
            # 重置状态
            self.game_state.reset_state()
            return True
        except Exception as e:
            self.logger.error(f"状态备用恢复失败: {str(e)}")
            return False
            
    def _backup_model_recovery(self, error: ModelError) -> bool:
        """模型错误备用恢复策略"""
        if not self.game_analyzer:
            return False
            
        try:
            # 尝试重新加载模型
            self.game_analyzer.reload_model()
            return True
        except Exception as e:
            self.logger.error(f"模型备用恢复失败: {str(e)}")
            return False
            
    def _generic_recovery_strategy(self, error: GameAutomationError) -> bool:
        """通用恢复策略"""
        try:
            # 记录错误
            self.logger.error(f"执行通用恢复策略: {str(error)}")
            
            # 等待一段时间
            time.sleep(self.retry_delay)
            
            # 检查系统资源
            if self._check_system_resources():
                return True
                
            return False
        except Exception as e:
            self.logger.error(f"通用恢复策略执行失败: {str(e)}")
            return False
            
    def _check_system_resources(self) -> bool:
        """检查系统资源状态"""
        try:
            # 检查内存使用
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                self.logger.warning("内存使用率过高")
                return False
                
            # 检查CPU使用
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                self.logger.warning("CPU使用率过高")
                return False
                
            # 检查磁盘空间
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                self.logger.warning("磁盘空间不足")
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"系统资源检查失败: {str(e)}")
            return False
    
    def _enhanced_window_recovery(self, error: 'WindowError') -> bool:
        """增强的窗口恢复策略 - 来自recovery.py
        
        Args:
            error: 窗口错误对象
            
        Returns:
            bool: 是否成功恢复
        """
        self.logger.info("执行增强窗口恢复策略...")
        
        if not self.window_manager:
            self.logger.warning("窗口管理器未初始化")
            return False
            
        # 步骤1: 检查当前窗口是否有效
        try:
            import win32gui, win32con
            current_hwnd = self.window_manager.window_handle if hasattr(self.window_manager, 'window_handle') else None
            
            if current_hwnd and win32gui.IsWindow(current_hwnd):
                self.logger.info("当前窗口句柄有效，尝试修复窗口状态")
                
                # 检查窗口是否最小化
                if win32gui.IsIconic(current_hwnd):
                    win32gui.ShowWindow(current_hwnd, win32con.SW_RESTORE)
                    self.logger.info("恢复最小化窗口")
                    time.sleep(0.5)
                
                # 检查窗口是否可见
                if not win32gui.IsWindowVisible(current_hwnd):
                    win32gui.ShowWindow(current_hwnd, win32con.SW_SHOW)
                    self.logger.info("显示隐藏窗口")
                    time.sleep(0.5)
                
                # 尝试激活窗口
                if hasattr(self.window_manager, 'set_foreground'):
                    if self.window_manager.set_foreground():
                        self.logger.info("窗口已激活")
                        
                        # 验证恢复
                        if self._comprehensive_recovery_verification(error):
                            return True
                        else:
                            self.logger.warning("窗口状态修复后验证失败")
            
            # 步骤2: 尝试通过现有信息找回窗口
            if hasattr(self.window_manager, 'find_window'):
                if self.window_manager.find_window():
                    self.logger.info("成功重新找到窗口")
                    if self._comprehensive_recovery_verification(error):
                        return True
                    else:
                        self.logger.warning("窗口重新找回后验证失败")
            
            # 步骤3: 尝试在当前窗口列表中查找匹配窗口
            if hasattr(self.window_manager, 'update_window_list'):
                self.window_manager.update_window_list()
                
                # 查找匹配窗口
                target_title = None
                if hasattr(self.window_manager, 'target_title') and self.window_manager.target_title:
                    target_title = self.window_manager.target_title
                elif hasattr(error, 'window_title') and error.window_title:
                    target_title = error.window_title
                    
                if target_title and hasattr(self.window_manager, 'windows_cache'):
                    self.logger.info(f"查找包含 '{target_title}' 的窗口")
                    for hwnd, title in self.window_manager.windows_cache:
                        if target_title.lower() in title.lower():
                            self.logger.info(f"找到匹配窗口: {title}")
                            if hasattr(self.window_manager, 'set_target_window'):
                                self.window_manager.set_target_window(hwnd, title)
                                time.sleep(0.5)
                                
                                if self._comprehensive_recovery_verification(error):
                                    return True
                                else:
                                    self.logger.warning("设置匹配窗口后验证失败")
            
            # 步骤4: 尝试使用第一个可见窗口
            if hasattr(self.window_manager, 'windows_cache') and self.window_manager.windows_cache:
                hwnd, title = self.window_manager.windows_cache[0]
                self.logger.info(f"使用第一个可见窗口作为备选: {title}")
                if hasattr(self.window_manager, 'set_target_window'):
                    self.window_manager.set_target_window(hwnd, title)
                    time.sleep(0.5)
                    
                    if self._comprehensive_recovery_verification(error):
                        return True
                    else:
                        self.logger.warning("使用备选窗口后验证失败")
            
            self.logger.error("所有增强窗口恢复策略均失败")
            return False
            
        except Exception as e:
            self.logger.error(f"增强窗口恢复策略异常: {str(e)}")
            return False
    
    def _advanced_backup_recovery(self, error: 'GameAutomationError') -> bool:
        """高级备用恢复策略 - 来自recovery.py
        
        Args:
            error: 错误对象
            
        Returns:
            bool: 是否成功恢复
        """
        self.logger.info("执行高级备用恢复策略...")
        
        try:
            # 策略1: 重新创建窗口管理器（仅窗口错误）
            if isinstance(error, type(error)) and 'Window' in str(type(error)):
                self.logger.info("尝试重新创建窗口管理器")
                
                # 保存当前窗口信息
                old_target_title = None
                old_target_class = None
                if self.window_manager:
                    if hasattr(self.window_manager, 'target_title'):
                        old_target_title = self.window_manager.target_title
                    if hasattr(self.window_manager, 'target_class'):
                        old_target_class = self.window_manager.target_class
                        
                    # 尝试清理旧资源
                    try:
                        if hasattr(self.window_manager, 'cleanup'):
                            self.window_manager.cleanup()
                    except:
                        pass
                        
                # 创建新的窗口管理器
                from src.services.window_manager import GameWindowManager
                if self.config:
                    self.window_manager = GameWindowManager(self.logger, self.config)
                    
                    # 恢复窗口设置
                    if old_target_title:
                        self.window_manager.target_title = old_target_title
                    if old_target_class:
                        self.window_manager.target_class = old_target_class
                        
                    # 更新窗口列表并尝试查找窗口
                    if hasattr(self.window_manager, 'update_window_list'):
                        self.window_manager.update_window_list()
                    
                    # 尝试找到匹配窗口
                    if hasattr(self.window_manager, 'find_window'):
                        if self.window_manager.find_window():
                            self.logger.info("成功找到目标窗口")
                            time.sleep(0.5)
                            
                            # 验证恢复
                            if self._comprehensive_recovery_verification(error):
                                return True
            
            # 策略2: 遍历所有窗口并尝试激活捕获
            if self.window_manager and hasattr(self.window_manager, 'windows_cache'):
                self.logger.info("尝试遍历所有窗口")
                for hwnd, title in self.window_manager.windows_cache:
                    self.logger.info(f"尝试窗口: {title}")
                    try:
                        if hasattr(self.window_manager, 'set_target_window'):
                            self.window_manager.set_target_window(hwnd, title)
                            time.sleep(0.5)
                        if hasattr(self.window_manager, 'set_foreground'):
                            self.window_manager.set_foreground()
                            time.sleep(0.5)
                        
                        # 尝试捕获
                        if hasattr(self.window_manager, 'capture_window'):
                            frame = self.window_manager.capture_window()
                            if frame is not None and isinstance(frame, np.ndarray) and frame.size > 0:
                                self.logger.info(f"成功捕获窗口: {title}")
                                return True
                    except Exception as e:
                        self.logger.warning(f"尝试窗口 {title} 时失败: {e}")
                        continue
                        
            # 策略3: 重置捕获引擎并再次尝试
            if self.window_manager:
                try:
                    self.logger.info("尝试完全重置捕获引擎")
                    
                    if hasattr(self.window_manager, 'capture_engine'):
                        try:
                            self.window_manager.capture_engine.cleanup()
                        except:
                            pass
                            
                    time.sleep(1.0)  # 等待较长时间确保资源释放
                    
                    # 重新创建捕获引擎
                    from src.services.capture_engines import GameCaptureEngine
                    self.window_manager.capture_engine = GameCaptureEngine(self.logger)
                    time.sleep(0.5)
                    
                    # 再次尝试捕获
                    if hasattr(self.window_manager, 'capture_window'):
                        frame = self.window_manager.capture_window()
                        if frame is not None and isinstance(frame, np.ndarray) and frame.size > 0:
                            self.logger.info("重置捕获引擎后成功捕获窗口")
                            return True
                except Exception as e:
                    self.logger.error(f"重置捕获引擎失败: {e}")
                    
            self.logger.error("所有高级备用恢复策略均失败")
            return False
            
        except Exception as e:
            self.logger.error(f"执行高级备用恢复策略时发生异常: {e}")
            return False
    
    def _comprehensive_recovery_verification(self, error: 'GameAutomationError') -> bool:
        """全面的恢复验证 - 整合两套验证逻辑
        
        Args:
            error: 错误对象
            
        Returns:
            bool: 恢复是否成功
        """
        self.logger.info("执行全面恢复验证...")
        
        if not self.window_manager:
            self.logger.warning("无法验证恢复: 窗口管理器未初始化")
            return False
            
        try:
            # 验证窗口是否存在且有效
            import win32gui
            import win32con
            
            window_handle = getattr(self.window_manager, 'window_handle', None)
            if not window_handle or not win32gui.IsWindow(window_handle):
                self.logger.warning("恢复验证失败: 窗口句柄无效")
                return False
            
            # 验证窗口是否可见
            if not win32gui.IsWindowVisible(window_handle):
                self.logger.warning("恢复验证失败: 窗口不可见，尝试激活窗口")
                # 检查窗口是否最小化
                if win32gui.IsIconic(window_handle):
                    win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)
                    self.logger.info("恢复最小化窗口")
                    time.sleep(0.5)
                
                # 尝试激活窗口
                if hasattr(self.window_manager, 'set_foreground'):
                    self.window_manager.set_foreground()
                    time.sleep(0.5)
                
                # 再次检查窗口是否可见
                if not win32gui.IsWindowVisible(window_handle):
                    self.logger.warning("激活窗口后仍不可见")
                    return False
            
            # 更新窗口位置信息
            try:
                if hasattr(self.window_manager, 'window_rect'):
                    self.window_manager.window_rect = win32gui.GetWindowRect(window_handle)
                    self.logger.info(f"更新窗口位置: {self.window_manager.window_rect}")
            except Exception as e:
                self.logger.warning(f"获取窗口位置失败: {e}")
            
            # 验证是否能够捕获窗口画面
            if hasattr(self.window_manager, 'capture_window'):
                frame = self.window_manager.capture_window()
                if frame is None:
                    self.logger.warning("恢复验证失败: 无法捕获窗口画面")
                    return False
                    
                if isinstance(frame, bool) or not isinstance(frame, np.ndarray) or frame.size == 0:
                    self.logger.warning("恢复验证失败: 捕获的窗口画面无效")
                    return False
                    
                # 验证图像是否有效（非全黑或全白）
                if frame.size > 0:
                    # 检查图像是否全黑或全白
                    mean_value = np.mean(frame)
                    if mean_value < 5 or mean_value > 250:
                        self.logger.warning(f"恢复验证警告: 捕获的图像可能无效，平均值: {mean_value}")
                        # 不直接返回失败，但记录警告
                    
                self.logger.info("恢复验证成功: 已成功捕获窗口画面")
                return True
            else:
                self.logger.warning("窗口管理器缺少capture_window方法")
                return False
                
        except Exception as e:
            self.logger.error(f"全面恢复验证异常: {str(e)}")
            return False
    
    def _handle_window_capture_error(self, error: 'WindowError') -> bool:
        """处理窗口捕获错误 - 来自recovery.py
        
        Args:
            error: 窗口错误对象
            
        Returns:
            bool: 是否成功恢复
        """
        self.logger.info("处理窗口捕获错误...")
        
        if not self.window_manager:
            self.logger.warning("窗口管理器未初始化")
            return False
            
        # 重新初始化捕获引擎
        try:
            # 如果存在capture_engine，尝试清理并重新初始化
            if hasattr(self.window_manager, 'capture_engine'):
                self.window_manager.capture_engine.cleanup()
                time.sleep(0.5)  # 等待资源释放
                
                # 重新初始化捕获引擎
                from src.services.capture_engines import GameCaptureEngine
                self.window_manager.capture_engine = GameCaptureEngine(self.logger)
                self.logger.info("重新初始化捕获引擎完成")
        except Exception as e:
            self.logger.error(f"重新初始化捕获引擎失败: {e}")
            
        # 确保窗口处于可捕获状态
        window_handle = getattr(self.window_manager, 'window_handle', None)
        if window_handle:
            # 尝试激活窗口
            try:
                import win32gui
                import win32con
                
                # 检查窗口是否最小化
                if win32gui.IsIconic(window_handle):
                    win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)
                    self.logger.info("恢复最小化窗口")
                    time.sleep(0.5)
                    
                # 尝试激活窗口
                if hasattr(self.window_manager, 'set_foreground'):
                    self.window_manager.set_foreground()
                    self.logger.info("激活窗口")
                    time.sleep(0.5)
                
                # 更新进程ID信息
                if hasattr(self.window_manager, 'process_id') and not getattr(self.window_manager, 'process_id', None):
                    import win32process
                    _, process_id = win32process.GetWindowThreadProcessId(window_handle)
                    self.window_manager.process_id = process_id
                    self.logger.info(f"更新进程ID: {process_id}")
                
                # 更新窗口位置信息
                try:
                    if hasattr(self.window_manager, 'window_rect'):
                        self.window_manager.window_rect = win32gui.GetWindowRect(window_handle)
                        self.logger.info(f"更新窗口位置: {self.window_manager.window_rect}")
                except Exception as e:
                    self.logger.error(f"获取窗口位置失败: {e}")
                    
            except Exception as e:
                self.logger.error(f"激活窗口失败: {e}")
                
        # 尝试捕获一次，验证恢复是否成功
        try:
            if hasattr(self.window_manager, 'capture_window'):
                frame = self.window_manager.capture_window()
                if frame is not None:
                    self.logger.info("捕获测试成功，窗口捕获恢复正常")
                    return True
                else:
                    self.logger.warning("捕获测试失败，可能需要进一步恢复操作")
                    return False
            else:
                self.logger.warning("窗口管理器缺少capture_window方法")
                return False
        except Exception as e:
            self.logger.error(f"捕获测试异常: {e}")
            return False
    
    def _system_health_check(self) -> bool:
        """系统健康检查 - 来自recovery.py
        
        Returns:
            bool: 系统是否健康
        """
        try:
            self.logger.info("执行系统健康检查...")
            
            # 检查内存使用率
            memory = psutil.virtual_memory()
            self.logger.info(f"内存使用率: {memory.percent}%")
            if memory.percent > 95:
                self.logger.error(f"内存使用率过高: {memory.percent}%")
                return False
            elif memory.percent > 85:
                self.logger.warning(f"内存使用率较高: {memory.percent}%")
                
            # 检查CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            self.logger.info(f"CPU使用率: {cpu_percent}%")
            if cpu_percent > 95:
                self.logger.error(f"CPU使用率过高: {cpu_percent}%")
                return False
            elif cpu_percent > 85:
                self.logger.warning(f"CPU使用率较高: {cpu_percent}%")
                
            # 检查磁盘空间
            try:
                disk = psutil.disk_usage('C:' if os.name == 'nt' else '/')
                self.logger.info(f"磁盘使用率: {disk.percent}%")
                if disk.percent > 95:
                    self.logger.error(f"磁盘空间严重不足: {disk.percent}%")
                    return False
                elif disk.percent > 85:
                    self.logger.warning(f"磁盘空间不足: {disk.percent}%")
            except:
                self.logger.warning("无法检查磁盘使用情况")
                
            self.logger.info("系统健康检查通过")
            return True
            
        except Exception as e:
            self.logger.error(f"系统健康检查失败: {str(e)}")
            return False
    
    def add_default_handlers(self):
        """添加默认的恢复处理函数 - 来自recovery.py"""
        # 窗口相关错误恢复
        self.register_handler(ErrorCode.WINDOW_ERROR, self._enhanced_window_recovery)
        self.register_handler(ErrorCode.WINDOW_NOT_FOUND, self._enhanced_window_recovery)
        self.register_handler(ErrorCode.WINDOW_CAPTURE_ERROR, self._handle_window_capture_error)
        self.register_handler(ErrorCode.WINDOW_STATE_ERROR, self._enhanced_window_recovery)
        
        # 图像处理相关错误恢复
        # self.register_handler(ErrorCode.IMAGE_PROCESSING_ERROR, self._handle_image_processing_error)
        
        # 动作模拟相关错误恢复
        # self.register_handler(ErrorCode.ACTION_ERROR, self._handle_action_error)
        
        # 模型相关错误恢复
        # self.register_handler(ErrorCode.MODEL_ERROR, self._handle_model_error)
        
        # 配置相关错误恢复
        # self.register_handler(ErrorCode.CONFIG_ERROR, self._handle_config_error)
        
        # 状态管理相关错误恢复
        # self.register_handler(ErrorCode.STATE_ERROR, self._handle_state_error)
        
        self.logger.info("默认错误恢复处理函数已注册")

    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计信息
        
        Returns:
            Dict[str, Any]: 错误统计信息
        """
        with self.error_lock:
            return {
                "error_stats": self.error_stats,
                "recovery_stats": self.recovery_stats,
                "consecutive_errors": self.consecutive_errors,
                "recovery_attempts": self.recovery_attempts
            }
    
    def reset_stats(self):
        """重置统计信息"""
        with self.error_lock:
            self.error_stats.clear()
            self.recovery_stats.clear()
            self.consecutive_errors = 0
            self.recovery_attempts = 0 