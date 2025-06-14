import time
from typing import Callable, Dict, Any
from src.common.exceptions import GameAutomationError, RecoveryError
from src.services.logger import GameLogger
import numpy as np

class RecoveryManager:
    """异常恢复管理器"""
    
    def __init__(self, logger: GameLogger):
        """
        初始化恢复管理器
        
        Args:
            logger: 日志对象
        """
        self.logger = logger
        self.recovery_handlers: Dict[int, Callable] = {}  # 错误码到恢复处理函数的映射
        self.max_retries = 3  # 最大重试次数
        self.retry_delay = 1.0  # 重试延迟（秒）
        self.window_manager = None  # 窗口管理器引用，延迟初始化
        self.config = None  # 配置引用，延迟初始化
        
        # 错误追踪
        self.consecutive_errors = 0  # 连续错误计数
        self.max_consecutive_errors = 5  # 连续错误阈值
        self.last_error_time = 0  # 上次错误时间
        self.error_types = {}  # 错误类型统计
        
        # 恢复状态
        self.last_recovery_time = 0  # 上次恢复时间
        self.recovery_attempts = 0  # 恢复尝试次数
        self.max_recovery_attempts = 5  # 最大恢复尝试次数
        self.recovery_success_count = 0  # 成功恢复次数
        
    def register_handler(self, error_code: int, handler: Callable):
        """
        注册恢复处理函数
        
        Args:
            error_code: 错误码
            handler: 恢复处理函数
        """
        self.recovery_handlers[error_code] = handler
        self.logger.debug(f"注册恢复处理函数: {error_code}")
        
    def set_window_manager(self, window_manager):
        """
        设置窗口管理器引用
        
        Args:
            window_manager: 窗口管理器实例
        """
        self.window_manager = window_manager
        
    def set_config(self, config):
        """
        设置配置引用
        
        Args:
            config: 配置实例
        """
        self.config = config
    
    def track_error(self, error_type: str):
        """
        追踪错误
        
        Args:
            error_type: 错误类型
        
        Returns:
            bool: 是否需要触发恢复
        """
        current_time = time.time()
        
        # 统计错误类型
        if error_type not in self.error_types:
            self.error_types[error_type] = 1
        else:
            self.error_types[error_type] += 1
        
        # 判断是否为短时间内连续错误
        if current_time - self.last_error_time < 5.0:  # 5秒内的连续错误
            self.consecutive_errors += 1
        else:
            self.consecutive_errors = 1
            
        self.last_error_time = current_time
        
        # 如果连续错误达到阈值，需要触发恢复
        need_recovery = self.consecutive_errors >= self.max_consecutive_errors
        
        # 检查恢复尝试频率
        if need_recovery and current_time - self.last_recovery_time < 30.0:
            # 如果30秒内已经尝试过恢复，增加阈值
            self.max_consecutive_errors = min(20, self.max_consecutive_errors + 1)
            need_recovery = self.consecutive_errors >= self.max_consecutive_errors
            
        return need_recovery
        
    def handle_error(self, error: GameAutomationError) -> bool:
        """
        处理异常并尝试恢复
        
        Args:
            error: 异常对象
            
        Returns:
            bool: 是否成功恢复
        """
        self.logger.error(f"发生异常: {error.message} (错误码: {error.error_code})")
        
        # 更新恢复状态
        current_time = time.time()
        self.last_recovery_time = current_time
        self.recovery_attempts += 1
        
        # 如果恢复尝试次数过多，增加等待时间
        if self.recovery_attempts > self.max_recovery_attempts:
            self.recovery_attempts = 0  # 重置计数
            self.logger.warning(f"恢复尝试次数过多，等待较长时间后再尝试")
            time.sleep(5.0)  # 等待5秒后再尝试
        
        # 检查是否有对应的恢复处理函数
        if error.error_code not in self.recovery_handlers:
            self.logger.warning(f"未找到错误码 {error.error_code} 的恢复处理函数")
            
            # 尝试使用基础错误码(向下取整到最近的千位数)
            base_error_code = (error.error_code // 1000) * 1000
            if base_error_code in self.recovery_handlers:
                self.logger.info(f"使用基础错误码 {base_error_code} 的恢复处理函数")
                handler = self.recovery_handlers[base_error_code]
            else:
                return False
        else:
            handler = self.recovery_handlers[error.error_code]
        
        # 尝试恢复
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"尝试恢复 (第 {attempt + 1} 次)")
                handler()
                
                # 验证恢复是否成功
                if self.verify_recovery():
                    self.logger.info("恢复成功")
                    self.consecutive_errors = 0  # 重置连续错误计数
                    self.recovery_success_count += 1
                    return True
                else:
                    self.logger.warning(f"恢复操作完成但验证失败 (尝试 {attempt + 1}/{self.max_retries})")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 2))  # 递增延迟
                    
            except Exception as e:
                self.logger.error(f"恢复失败: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # 递增延迟
        
        # 常规恢复失败，尝试备用恢复策略
        try:
            self.logger.warning("常规恢复策略失败，尝试备用恢复策略")
            success = self.backup_recovery_strategy()
            if success:
                self.logger.info("备用恢复策略成功")
                self.consecutive_errors = 0
                self.recovery_success_count += 1
                return True
        except Exception as e:
            self.logger.error(f"备用恢复策略失败: {str(e)}")
            
        self.logger.error("所有恢复尝试均失败")
        return False
        
    def verify_recovery(self) -> bool:
        """
        验证恢复操作是否成功
        
        Returns:
            bool: 恢复是否成功
        """
        self.logger.info("验证恢复操作是否成功")
        
        if not self.window_manager:
            self.logger.warning("无法验证恢复: 窗口管理器未初始化")
            return False
            
        try:
            # 验证窗口是否存在且有效
            import win32gui
            import win32con
            
            if not self.window_manager.window_handle or not win32gui.IsWindow(self.window_manager.window_handle):
                self.logger.warning("恢复验证失败: 窗口句柄无效")
                return False
            
            # 验证窗口是否可见
            if not win32gui.IsWindowVisible(self.window_manager.window_handle):
                self.logger.warning("恢复验证失败: 窗口不可见，尝试激活窗口")
                # 检查窗口是否最小化
                if win32gui.IsIconic(self.window_manager.window_handle):
                    win32gui.ShowWindow(self.window_manager.window_handle, win32con.SW_RESTORE)
                    self.logger.info("恢复最小化窗口")
                    time.sleep(0.5)
                
                # 尝试激活窗口
                self.window_manager.set_foreground()
                time.sleep(0.5)
                
                # 再次检查窗口是否可见
                if not win32gui.IsWindowVisible(self.window_manager.window_handle):
                    self.logger.warning("激活窗口后仍不可见")
                    return False
            
            # 更新窗口位置信息
            try:
                self.window_manager.window_rect = win32gui.GetWindowRect(self.window_manager.window_handle)
                self.logger.info(f"更新窗口位置: {self.window_manager.window_rect}")
            except Exception as e:
                self.logger.warning(f"获取窗口位置失败: {e}")
            
            # 验证是否能够捕获窗口画面
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
            
        except Exception as e:
            self.logger.error(f"恢复验证异常: {str(e)}")
            return False
        
    def add_default_handlers(self):
        """添加默认的恢复处理函数"""
        # 窗口相关错误恢复
        self.register_handler(1000, self._handle_window_error)  # 通用窗口错误
        self.register_handler(1001, self._handle_window_not_found)  # 窗口未找到
        self.register_handler(1002, self._handle_window_capture_error)  # 窗口捕获错误
        self.register_handler(1003, self._handle_window_state_error)  # 窗口状态错误
        
        # 图像处理相关错误恢复
        self.register_handler(2000, self._handle_image_processing_error)
        
        # 动作模拟相关错误恢复
        self.register_handler(3000, self._handle_action_error)
        
        # 模型相关错误恢复
        self.register_handler(4000, self._handle_model_error)
        
        # 配置相关错误恢复
        self.register_handler(5000, self._handle_config_error)
        
        # 状态管理相关错误恢复
        self.register_handler(6000, self._handle_state_error)
        
    def _handle_window_error(self):
        """处理通用窗口相关错误"""
        self.logger.info("尝试处理窗口错误...")
        
        # 延迟初始化窗口管理器
        if not self.window_manager:
            from src.services.window_manager import GameWindowManager
            from src.services.config import Config
            if not self.config:
                self.config = Config()
            self.window_manager = GameWindowManager(self.logger, self.config)
            
        # 执行窗口恢复策略
        success = self.window_recovery_strategy()
        if not success:
            raise RecoveryError("窗口恢复失败")
            
    def _handle_window_not_found(self):
        """处理窗口未找到错误"""
        self.logger.info("处理窗口未找到错误...")
        
        # 延迟初始化窗口管理器
        if not self.window_manager:
            from src.services.window_manager import GameWindowManager
            from src.services.config import Config
            if not self.config:
                self.config = Config()
            self.window_manager = GameWindowManager(self.logger, self.config)
            
        # 尝试更新窗口列表并在列表中查找目标窗口
        self.window_manager.update_window_list()
        
        target_title = self.window_manager.target_title
        if not target_title and hasattr(self.window_manager, 'window_title'):
            target_title = self.window_manager.window_title
            
        if target_title:
            self.logger.info(f"查找名称包含 '{target_title}' 的窗口")
            # 遍历窗口列表
            for hwnd, title in self.window_manager.windows_cache:
                if target_title.lower() in title.lower():
                    self.logger.info(f"找到匹配窗口: {title}")
                    self.window_manager.set_target_window(hwnd, title)
                    return
                    
        # 如果未找到任何窗口，但存在其他窗口，使用第一个可见窗口
        if self.window_manager.windows_cache:
            hwnd, title = self.window_manager.windows_cache[0]
            self.logger.warning(f"未找到匹配窗口，使用第一个可见窗口: {title}")
            self.window_manager.set_target_window(hwnd, title)
            return
            
        # 如果未找到任何窗口
        raise RecoveryError("没有找到匹配的窗口")
        
    def _handle_window_capture_error(self):
        """处理窗口捕获错误"""
        self.logger.info("处理窗口捕获错误...")
        
        # 延迟初始化窗口管理器
        if not self.window_manager:
            from src.services.window_manager import GameWindowManager
            from src.services.config import Config
            if not self.config:
                self.config = Config()
            self.window_manager = GameWindowManager(self.logger, self.config)
            
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
        if self.window_manager.window_handle:
            # 尝试激活窗口
            try:
                import win32gui
                import win32con
                
                # 检查窗口是否最小化
                if win32gui.IsIconic(self.window_manager.window_handle):
                    win32gui.ShowWindow(self.window_manager.window_handle, win32con.SW_RESTORE)
                    self.logger.info("恢复最小化窗口")
                    time.sleep(0.5)
                    
                # 尝试激活窗口
                self.window_manager.set_foreground()
                self.logger.info("激活窗口")
                time.sleep(0.5)
                
                # 更新进程ID信息
                if hasattr(self.window_manager, 'process_id') and not self.window_manager.process_id:
                    import win32process
                    _, process_id = win32process.GetWindowThreadProcessId(self.window_manager.window_handle)
                    self.window_manager.process_id = process_id
                    self.logger.info(f"更新进程ID: {process_id}")
                
                # 更新窗口位置信息
                try:
                    self.window_manager.window_rect = win32gui.GetWindowRect(self.window_manager.window_handle)
                    self.logger.info(f"更新窗口位置: {self.window_manager.window_rect}")
                except Exception as e:
                    self.logger.error(f"获取窗口位置失败: {e}")
                    
            except Exception as e:
                self.logger.error(f"激活窗口失败: {e}")
                
        # 尝试捕获一次，验证恢复是否成功
        try:
            frame = self.window_manager.capture_window()
            if frame is not None:
                self.logger.info("捕获测试成功，窗口捕获恢复正常")
                return
            else:
                self.logger.warning("捕获测试失败，可能需要进一步恢复操作")
        except Exception as e:
            self.logger.error(f"捕获测试异常: {e}")
            raise RecoveryError(f"窗口捕获恢复失败: {e}")
        
    def _handle_window_state_error(self):
        """处理窗口状态错误"""
        self.logger.info("处理窗口状态错误...")
        
        # 延迟初始化窗口管理器
        if not self.window_manager:
            from src.services.window_manager import GameWindowManager
            from src.services.config import Config
            if not self.config:
                self.config = Config()
            self.window_manager = GameWindowManager(self.logger, self.config)
            
        # 检查窗口是否有效
        import win32gui
        if not self.window_manager.window_handle or not win32gui.IsWindow(self.window_manager.window_handle):
            # 窗口无效，需要重新查找
            self._handle_window_not_found()
            return
            
        # 尝试修复窗口状态
        try:
            import win32con
            
            # 检查窗口是否最小化
            if win32gui.IsIconic(self.window_manager.window_handle):
                win32gui.ShowWindow(self.window_manager.window_handle, win32con.SW_RESTORE)
                self.logger.info("恢复最小化窗口")
                time.sleep(0.5)
            
            # 尝试激活窗口
            self.window_manager.set_foreground()
            self.logger.info("激活窗口")
            time.sleep(0.3)
            
            # 获取新的窗口信息
            try:
                self.window_manager.window_rect = win32gui.GetWindowRect(self.window_manager.window_handle)
                self.logger.info(f"更新窗口位置: {self.window_manager.window_rect}")
            except Exception as e:
                self.logger.error(f"获取窗口位置失败: {e}")
                
        except Exception as e:
            self.logger.error(f"修复窗口状态失败: {e}")
            raise RecoveryError(f"修复窗口状态失败: {e}")
            
    def window_recovery_strategy(self):
        """
        窗口恢复策略，尝试多种方法恢复窗口
        
        Returns:
            bool: 是否成功恢复
        """
        self.logger.info("执行窗口恢复策略...")
        
        # 延迟初始化窗口管理器
        if not self.window_manager:
            from src.services.window_manager import GameWindowManager
            from src.services.config import Config
            if not self.config:
                self.config = Config()
            self.window_manager = GameWindowManager(self.logger, self.config)
            
        # 步骤1: 检查当前窗口是否有效
        import win32gui, win32con
        current_hwnd = self.window_manager.window_handle
        if current_hwnd and win32gui.IsWindow(current_hwnd):
            self.logger.info("当前窗口句柄有效，尝试修复窗口状态")
            try:
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
                if self.window_manager.set_foreground():
                    self.logger.info("窗口已激活")
                    
                    # 验证恢复
                    if self.verify_recovery():
                        return True
                    else:
                        self.logger.warning("窗口状态修复后验证失败")
            except Exception as e:
                self.logger.warning(f"修复窗口状态失败: {e}")
                # 继续尝试其他恢复方法
        
        # 步骤2: 尝试通过现有信息找回窗口
        try:
            if self.window_manager.find_window():
                self.logger.info("成功重新找到窗口")
                
                # 验证恢复
                if self.verify_recovery():
                    return True
                else:
                    self.logger.warning("窗口重新找回后验证失败")
        except Exception as e:
            self.logger.warning(f"通过现有信息找回窗口失败: {e}")
        
        # 步骤3: 尝试在当前窗口列表中查找匹配窗口
        try:
            self.window_manager.update_window_list()
            
            # 查找匹配窗口
            target_title = None
            if hasattr(self.window_manager, 'target_title') and self.window_manager.target_title:
                target_title = self.window_manager.target_title
            elif hasattr(self.window_manager, 'window_title') and self.window_manager.window_title:
                target_title = self.window_manager.window_title
                
            if target_title:
                self.logger.info(f"查找包含 '{target_title}' 的窗口")
                for hwnd, title in self.window_manager.windows_cache:
                    if target_title.lower() in title.lower():
                        self.logger.info(f"找到匹配窗口: {title}")
                        self.window_manager.set_target_window(hwnd, title)
                        time.sleep(0.5)  # 等待窗口设置生效
                        
                        # 验证恢复
                        if self.verify_recovery():
                            return True
                        else:
                            self.logger.warning("设置匹配窗口后验证失败")
        except Exception as e:
            self.logger.warning(f"查找匹配窗口失败: {e}")
        
        # 步骤4: 尝试使用第一个可见窗口
        try:
            if self.window_manager.windows_cache:
                hwnd, title = self.window_manager.windows_cache[0]
                self.logger.info(f"使用第一个可见窗口作为备选: {title}")
                self.window_manager.set_target_window(hwnd, title)
                time.sleep(0.5)  # 等待窗口设置生效
                
                # 验证恢复
                if self.verify_recovery():
                    return True
                else:
                    self.logger.warning("使用备选窗口后验证失败")
        except Exception as e:
            self.logger.error(f"使用备选窗口失败: {e}")
        
        self.logger.error("所有窗口恢复策略均失败")
        return False
            
    def backup_recovery_strategy(self):
        """
        备用恢复策略，在常规恢复策略失败时尝试
        
        Returns:
            bool: 是否成功恢复
        """
        self.logger.info("执行备用恢复策略...")
        
        try:
            # 策略1: 重新创建窗口管理器
            self.logger.info("尝试重新创建窗口管理器")
            from src.services.window_manager import GameWindowManager
            from src.services.config import Config
            if not self.config:
                self.config = Config()
                
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
                    self.window_manager.cleanup()
                except:
                    pass
                    
            # 创建新的窗口管理器
            self.window_manager = GameWindowManager(self.logger, self.config)
            
            # 恢复窗口设置
            if old_target_title:
                self.window_manager.target_title = old_target_title
            if old_target_class:
                self.window_manager.target_class = old_target_class
                
            # 更新窗口列表并尝试查找窗口
            self.window_manager.update_window_list()
            
            # 尝试找到匹配窗口
            if self.window_manager.find_window():
                self.logger.info("成功找到目标窗口")
                time.sleep(0.5)
                
                # 验证恢复
                if self.verify_recovery():
                    return True
                    
            # 策略2: 遍历所有窗口并尝试激活捕获
            self.logger.info("尝试遍历所有窗口")
            for hwnd, title in self.window_manager.windows_cache:
                self.logger.info(f"尝试窗口: {title}")
                try:
                    self.window_manager.set_target_window(hwnd, title)
                    time.sleep(0.5)
                    self.window_manager.set_foreground()
                    time.sleep(0.5)
                    
                    # 尝试捕获
                    frame = self.window_manager.capture_window()
                    if frame is not None and isinstance(frame, np.ndarray) and frame.size > 0:
                        self.logger.info(f"成功捕获窗口: {title}")
                        return True
                except Exception as e:
                    self.logger.warning(f"尝试窗口 {title} 时失败: {e}")
                    continue
                    
            # 策略3: 最后尝试重置捕获引擎并再次尝试
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
                frame = self.window_manager.capture_window()
                if frame is not None and isinstance(frame, np.ndarray) and frame.size > 0:
                    self.logger.info("重置捕获引擎后成功捕获窗口")
                    return True
            except Exception as e:
                self.logger.error(f"重置捕获引擎失败: {e}")
                
            self.logger.error("所有备用恢复策略均失败")
            return False
            
        except Exception as e:
            self.logger.error(f"执行备用恢复策略时发生异常: {e}")
            return False
            
    def _handle_image_processing_error(self):
        """处理图像处理相关错误"""
        # 重新初始化图像处理器
        from src.services.image_processor import ImageProcessor
        image_processor = ImageProcessor()
        if not image_processor.initialize():
            raise RecoveryError("无法重新初始化图像处理器")
            
    def _handle_action_error(self):
        """处理动作模拟相关错误"""
        # 重置鼠标位置
        import pyautogui
        pyautogui.moveTo(0, 0)
        
    def _handle_model_error(self):
        """处理模型相关错误"""
        # 重新加载模型
        from src.services.game_analyzer import GameAnalyzer
        analyzer = GameAnalyzer()
        if not analyzer.load_model():
            raise RecoveryError("无法重新加载模型")
            
    def _handle_config_error(self):
        """处理配置相关错误"""
        # 重新加载配置
        from src.services.config import Config
        config = Config()
        if not config.load():
            raise RecoveryError("无法重新加载配置")
            
    def _handle_state_error(self):
        """处理状态管理相关错误"""
        # 重置状态
        from src.services.game_state import StateManager
        state_manager = StateManager()
        state_manager.reset()