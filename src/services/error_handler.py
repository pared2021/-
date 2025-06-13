import time
import traceback
from typing import Dict, Any, Optional, Callable, List
from threading import Lock
from src.common.error_types import (
    GameAutomationError,
    ErrorCode,
    ErrorContext,
    ERROR_TYPE_MAP
)
from src.services.logger import GameLogger
import numpy as np
import psutil

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
        # 根据错误类型执行不同的验证
        if isinstance(error, WindowError):
            return self._verify_window_recovery(error)
        elif isinstance(error, ImageProcessingError):
            return self._verify_image_processing_recovery(error)
        elif isinstance(error, ActionError):
            return self._verify_action_recovery(error)
        elif isinstance(error, StateError):
            return self._verify_state_recovery(error)
        elif isinstance(error, ModelError):
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
        """实现备用恢复策略"""
        try:
            # 根据错误类型选择不同的恢复策略
            if isinstance(error, WindowError):
                return self._backup_window_recovery(error)
            elif isinstance(error, ImageProcessingError):
                return self._backup_image_processing_recovery(error)
            elif isinstance(error, ActionError):
                return self._backup_action_recovery(error)
            elif isinstance(error, StateError):
                return self._backup_state_recovery(error)
            elif isinstance(error, ModelError):
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