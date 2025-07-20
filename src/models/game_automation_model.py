from PyQt6.QtCore import QObject, pyqtSignal, QThread
import cv2
import numpy as np
from ..services.window_manager import GameWindowManager
from ..services.image_processor import ImageProcessor
from ..services.action_simulator import ActionSimulator
from ..core.types import UnifiedGameState as GameState
from ..services.game_analyzer import GameAnalyzer
from ..services.auto_operator import AutoOperator
from ..services.logger import GameLogger
from ..services.config import Config
import time
from ..services.error_handler import ErrorHandler

class AutomationThread(QThread):
    """自动化线程"""
    
    frame_updated = pyqtSignal(np.ndarray)
    status_updated = pyqtSignal(str)
    error_occurred = pyqtSignal(str)  # 增加错误信号
    recovery_attempted = pyqtSignal(bool)  # 恢复尝试信号，True表示成功，False表示失败
    
    def __init__(self, 
                 window_manager: GameWindowManager, 
                 image_processor: ImageProcessor,
                 action_simulator: ActionSimulator,
                 auto_operator: AutoOperator,
                 logger: GameLogger,
                 config: Config,
                 recovery_manager=None):  # 添加恢复管理器参数
        super().__init__()
        self.window_manager = window_manager
        self.image_processor = image_processor
        self.action_simulator = action_simulator
        self.auto_operator = auto_operator
        self.logger = logger
        self.config = config
        self.running = False
        
        # 使用传入的恢复管理器或创建新的
        if recovery_manager:
            self.recovery_manager = recovery_manager
        else:
            # 仅作为备选方案
            self.recovery_manager = ErrorHandler(logger)
            self.recovery_manager.add_default_handlers()
            self.recovery_manager.set_window_manager(window_manager)
            self.recovery_manager.set_config(config)
    
    def run(self):
        """运行自动化任务"""
        self.running = True
        self.logger.info("开始自动化任务")
        
        while self.running:
            try:
                # 确保窗口激活
                if not self.window_manager.is_window_active():
                    self.status_updated.emit("窗口未激活")
                    self.logger.warning("游戏窗口未激活")
                    
                    # 尝试激活窗口
                    if not self.window_manager.set_foreground():
                        # 使用错误处理器的错误跟踪（模拟track_error行为）
                        need_recovery = True  # 简化处理
                        
                        # 如果需要恢复，触发窗口状态错误恢复
                        if need_recovery:
                            self.status_updated.emit("尝试恢复窗口状态")
                            self.logger.warning("连续无法激活窗口，尝试恢复")
                            
                            # 创建窗口状态错误并尝试恢复
                            from ..common.exceptions import WindowError
                            error = WindowError("无法激活窗口", 1003)  # 窗口状态错误码
                            # 创建错误上下文并处理错误
                            from ..common.error_types import ErrorContext
                            error.context = ErrorContext(
                                source="AutomationThread.run",
                                details="窗口无法激活"
                            )
                            recovery_success = self.recovery_manager.handle_error(error)
                            
                            # 发送恢复信号
                            self.recovery_attempted.emit(recovery_success)
                            
                            if recovery_success:
                                self.logger.info("窗口状态恢复成功")
                            else:
                                self.logger.error("窗口状态恢复失败")
                                time.sleep(2.0)  # 恢复失败时等待较长时间
                    
                    time.sleep(1.0)  # 等待一秒后再尝试
                    continue
                
                # 获取游戏画面
                frame = self.window_manager.capture_window()
                
                # 检查画面是否有效
                if frame is None:
                    self.status_updated.emit("无法获取游戏画面")
                    self.logger.warning("无法获取游戏画面：返回为None")
                    
                    # 直接处理捕获失败
                    self._handle_capture_failure()
                    
                    time.sleep(0.5)
                    continue
                
                if isinstance(frame, bool):
                    self.status_updated.emit("无法获取游戏画面")
                    self.logger.warning(f"无法获取游戏画面：返回为布尔值 ({frame})")
                    self._handle_capture_failure()
                    time.sleep(0.5)
                    continue
                
                if not isinstance(frame, np.ndarray):
                    self.status_updated.emit("无法获取游戏画面")
                    self.logger.warning(f"无法获取游戏画面：返回非numpy数组 ({type(frame)})")
                    self._handle_capture_failure()
                    time.sleep(0.5)
                    continue
                
                if frame.size == 0:
                    self.status_updated.emit("无法获取游戏画面")
                    self.logger.warning("无法获取游戏画面：返回空数组")
                    self._handle_capture_failure()
                    time.sleep(0.5)
                    continue
                
                # 成功获取画面，重置错误统计
                self.recovery_manager.reset_stats()
                
                # 更新画面
                self.frame_updated.emit(frame)
                
                # 分析游戏状态
                try:
                    game_state = self.image_processor.analyze_frame(frame)
                    if not game_state:
                        self.logger.warning("分析游戏状态失败：返回空结果")
                        # 状态分析失败处理已简化
                        time.sleep(0.2)
                        continue
                except Exception as e:
                    self.logger.error(f"分析游戏状态异常: {str(e)}")
                    self._handle_image_processing_failure()
                    time.sleep(0.5)
                    continue
                
                # 根据状态选择并执行操作
                try:
                    action = self.auto_operator.select_action(game_state)
                    if action:
                        success = self.auto_operator.execute_action(action)
                        if success:
                            self.status_updated.emit(f"执行操作: {action['type']}")
                        else:
                            self.status_updated.emit(f"操作失败: {action['type']}")
                            # 动作失败处理已简化
                except Exception as e:
                    self.logger.error(f"执行操作异常: {str(e)}")
                    self._handle_action_failure()
                    time.sleep(0.5)
                    continue
                
                # 添加小延迟，防止CPU使用率过高
                time.sleep(0.05)
                
            except Exception as e:
                self.logger.error(f"自动化任务出错: {str(e)}")
                self.status_updated.emit(f"错误: {str(e)}")
                self.error_occurred.emit(str(e))
                
                # 根据错误类型尝试恢复
                error_msg = str(e).lower()
                from ..common.exceptions import WindowError, ImageProcessingError, ActionError
                
                if "window" in error_msg or "窗口" in error_msg or "handle" in error_msg:
                    error = WindowError(f"窗口操作异常: {str(e)}", 1000)
                elif "image" in error_msg or "图像" in error_msg or "截图" in error_msg:
                    error = ImageProcessingError(f"图像处理异常: {str(e)}", 2000)
                elif "action" in error_msg or "操作" in error_msg or "点击" in error_msg:
                    error = ActionError(f"动作执行异常: {str(e)}", 3000)
                else:
                    error = WindowError(f"未知异常: {str(e)}", 1000)
                    
                recovery_success = self.recovery_manager.handle_error(error)
                self.recovery_attempted.emit(recovery_success)
                
                time.sleep(1.0)  # 出错时等待较长时间
    
    def _handle_capture_failure(self):
        """处理捕获失败"""
        self.status_updated.emit("系统不稳定，尝试自动恢复窗口捕获")
        self.logger.warning("连续捕获失败，尝试恢复")
        
        # 创建窗口捕获错误并尝试恢复
        from ..common.exceptions import WindowError
        error = WindowError("连续窗口捕获失败", 1002)  # 窗口捕获错误码
        
        # 尝试恢复
        recovery_success = self.recovery_manager.handle_error(error)
        
        # 发送恢复信号
        self.recovery_attempted.emit(recovery_success)
        
        if recovery_success:
            self.logger.info("窗口捕获恢复成功")
        else:
            self.logger.error("窗口捕获恢复失败")
    
    def _handle_image_processing_failure(self):
        """处理图像处理失败"""
        self.status_updated.emit("系统不稳定，尝试自动恢复图像处理")
        self.logger.warning("连续图像处理失败，尝试恢复")
        
        # 创建图像处理错误并尝试恢复
        from ..common.exceptions import ImageProcessingError
        error = ImageProcessingError("连续图像处理失败", 2000)
        
        # 尝试恢复
        recovery_success = self.recovery_manager.handle_error(error)
        
        # 发送恢复信号
        self.recovery_attempted.emit(recovery_success)
    
    def _handle_action_failure(self):
        """处理动作执行失败"""
        self.status_updated.emit("系统不稳定，尝试自动恢复动作执行")
        self.logger.warning("连续动作执行失败，尝试恢复")
        
        # 创建动作执行错误并尝试恢复
        from ..common.exceptions import ActionError
        error = ActionError("连续动作执行失败", 3000)
        
        # 尝试恢复
        recovery_success = self.recovery_manager.handle_error(error)
        
        # 发送恢复信号
        self.recovery_attempted.emit(recovery_success)
    
    def stop(self):
        """停止自动化任务"""
        self.running = False
        self.logger.info("停止自动化任务")

class GameAutomationModel(QObject):
    """游戏自动化模型"""
    
    # 定义信号
    automation_started = pyqtSignal()
    automation_stopped = pyqtSignal()
    automation_error = pyqtSignal(str)
    window_list_updated = pyqtSignal(list)
    frame_updated = pyqtSignal(np.ndarray)
    status_updated = pyqtSignal(str)
    game_state_updated = pyqtSignal(dict)  # 游戏状态更新信号
    window_selected = pyqtSignal(str)
    
    def __init__(self,
                 logger: GameLogger,
                 window_manager: GameWindowManager,
                 game_analyzer: GameAnalyzer,
                 auto_operator: AutoOperator,
                 image_processor: ImageProcessor,
                 action_simulator: ActionSimulator,
                 game_state: GameState,
                 config: Config):
        super().__init__()
        
        # 保存注入的服务
        self.logger = logger
        self.window_manager = window_manager
        self.game_analyzer = game_analyzer
        self.auto_operator = auto_operator
        self.image_processor = image_processor
        self.action_simulator = action_simulator
        self.game_state = game_state
        self.config = config
        
        # 初始化错误处理器
        self.recovery_manager = ErrorHandler(logger)
        self.recovery_manager.add_default_handlers()
        self.recovery_manager.set_window_manager(window_manager)
        self.recovery_manager.set_config(config)  # 确保设置config
        
        self._is_running = False
        self._current_window = None
        self._current_window_title = None
        self.automation_thread = None
        
    @property
    def is_running(self):
        """获取自动化是否正在运行"""
        return self._is_running
        
    def start_automation(self, window_handle):
        """开始自动化"""
        try:
            if self._is_running:
                raise Exception("自动化已经在运行中")
                
            self._current_window = window_handle
            self._is_running = True
            
            # 设置窗口句柄
            self.logger.info(f"开始捕获窗口画面...")
            
            # 使用提供的窗口句柄直接找到窗口
            if not self.window_manager.find_window(specific_hwnd=window_handle):
                raise Exception("无法找到指定窗口，请重新选择")
                
            # 创建并启动自动化线程，传递统一的恢复管理器
            self.automation_thread = AutomationThread(
                self.window_manager,
                self.image_processor,
                self.action_simulator,
                self.auto_operator,
                self.logger,
                self.config,
                recovery_manager=self.recovery_manager  # 传递统一的恢复管理器
            )
            self.automation_thread.frame_updated.connect(self.frame_updated)
            self.automation_thread.status_updated.connect(self.status_updated)
            # 连接新增的错误和恢复信号
            self.automation_thread.error_occurred.connect(lambda msg: self.automation_error.emit(f"自动化错误: {msg}"))
            self.automation_thread.recovery_attempted.connect(self._on_recovery_attempted)
            self.automation_thread.start()
            
            self.automation_started.emit()
            
        except Exception as e:
            self._is_running = False
            self.automation_error.emit(f"启动自动化失败: {str(e)}")
            self.logger.error(f"启动自动化失败: {str(e)}")
            
    def _on_recovery_attempted(self, success: bool):
        """处理恢复尝试事件"""
        if success:
            status_msg = "系统自动恢复成功"
            self.logger.info(status_msg)
        else:
            status_msg = "系统自动恢复失败，可能需要手动干预"
            self.logger.warning(status_msg)
        
        # 通知UI
        self.status_updated.emit(status_msg)
        
    def stop_automation(self):
        """停止自动化"""
        try:
            if not self._is_running:
                return
                
            if self.automation_thread:
                self.automation_thread.stop()
                self.automation_thread.wait()
                self.automation_thread = None
                
            self._is_running = False
            self._current_window = None
            self._current_window_title = None
            self.automation_stopped.emit()
            
        except Exception as e:
            self.automation_error.emit(f"停止自动化失败: {str(e)}")
            
    def get_window_list(self):
        """获取窗口列表"""
        try:
            windows = self.window_manager.get_all_windows()
            self.window_list_updated.emit(windows)
            return windows
        except Exception as e:
            self.logger.error(f"获取窗口列表失败: {str(e)}")
            self.window_list_updated.emit([])
            return []
            
    def set_window(self, hwnd: int, title: str) -> bool:
        """设置当前窗口
        
        Args:
            hwnd: 窗口句柄
            title: 窗口标题
            
        Returns:
            bool: 是否成功
        """
        try:
            self._current_window = hwnd
            self._current_window_title = title
            self.window_manager.set_target_window(hwnd, title)
            
            # 尝试立即捕获一次窗口，检查是否成功
            frame = self.window_manager.capture_window()
            if frame is None or isinstance(frame, bool):
                self.logger.warning(f"无法捕获窗口 {title} 的画面")
                # 尝试激活窗口后再次捕获
                if self.window_manager.set_foreground():
                    time.sleep(0.5)  # 给窗口激活一些时间
                    frame = self.window_manager.capture_window()
                    if frame is None or isinstance(frame, bool):
                        self.logger.error(f"激活后仍无法捕获窗口 {title} 的画面")
                        return False
            
            self.window_selected.emit(title)
            self.logger.info(f"成功设置当前窗口: {title}")
            return True
        except Exception as e:
            self.logger.error(f"设置窗口失败: {str(e)}")
            return False
            
    def capture_window(self):
        """捕获窗口画面"""
        try:
            # 检查是否已经选择窗口
            if not self._current_window:
                self.logger.warning("未选择窗口，无法捕获画面")
                return None
                
            # 尝试捕获窗口
            frame = self.window_manager.capture_window()
            
            # 检查捕获结果
            if frame is None:
                self.logger.warning("捕获窗口画面失败：返回为None")
                
                # 使用恢复管理器跟踪错误
                need_recovery = self.recovery_manager.track_error("capture_failure")
                if need_recovery:
                    self.logger.warning("连续捕获失败，尝试自动恢复")
                    
                    # 创建窗口捕获错误并尝试恢复
                    from ..common.exceptions import WindowError
                    error = WindowError("连续多次窗口捕获失败", 1002)  # 窗口捕获错误码
                    
                    # 尝试恢复
                    recovery_success = self.recovery_manager.handle_error(error)
                    
                    if recovery_success:
                        self.logger.info("自动恢复成功")
                        
                        # 尝试再次捕获
                        frame = self.window_manager.capture_window()
                        if frame is not None and isinstance(frame, np.ndarray) and frame.size > 0:
                            self.logger.info("恢复后成功捕获窗口")
                            self.frame_updated.emit(frame)
                            return frame
                    else:
                        self.logger.error("自动恢复失败")
                
                return None
                
            if isinstance(frame, bool):
                self.logger.warning("捕获窗口画面失败：返回为布尔值")
                # 使用恢复管理器跟踪错误
                self.recovery_manager.track_error("capture_failure")
                return None
                
            # 检查是否是有效的numpy数组
            if not isinstance(frame, np.ndarray):
                self.logger.warning(f"捕获窗口画面失败：返回非numpy数组 ({type(frame)})")
                # 使用恢复管理器跟踪错误
                self.recovery_manager.track_error("capture_failure")
                return None
                
            if frame.size == 0:
                self.logger.warning("捕获窗口画面失败：返回空数组")
                # 使用恢复管理器跟踪错误
                self.recovery_manager.track_error("capture_failure")
                return None
                
            # 检查形状是否有效
            if len(frame.shape) != 3 or frame.shape[2] not in [1, 3, 4]:
                self.logger.warning(f"捕获窗口画面失败：形状无效 ({frame.shape})")
                # 使用恢复管理器跟踪错误
                self.recovery_manager.track_error("capture_failure")
                return None
                
            # 成功捕获，重置错误状态
            self.recovery_manager.consecutive_errors = 0
            if "capture_failure" in self.recovery_manager.error_types:
                self.recovery_manager.error_types["capture_failure"] = 0
                
            # 确保只发送有效的帧数据给UI
            self.frame_updated.emit(frame)
            self.logger.debug(f"成功捕获窗口画面: shape={frame.shape}, type={frame.dtype}")
            return frame
        except Exception as e:
            self.logger.error(f"捕获窗口画面失败: {str(e)}")
            
            # 使用恢复管理器跟踪错误
            need_recovery = self.recovery_manager.track_error("capture_exception")
            
            # 如果连续错误次数达到阈值，尝试恢复
            if need_recovery:
                self.logger.warning("捕获窗口时发生多次异常，尝试自动恢复")
                
                # 创建窗口错误并尝试恢复
                from ..common.exceptions import WindowError
                error = WindowError(f"捕获窗口时发生异常: {str(e)}", 1000)
                
                # 尝试恢复
                self.recovery_manager.handle_error(error)
            
            return None
    
    def analyze_game_state(self, frame: np.ndarray):
        """分析游戏状态"""
        try:
            # 验证输入
            if frame is None:
                self.logger.warning("无法分析游戏状态：帧数据为空")
                return None
                
            if not isinstance(frame, np.ndarray):
                self.logger.warning(f"无法分析游戏状态：帧数据类型错误 ({type(frame)})")
                return None
                
            if frame.size == 0:
                self.logger.warning("无法分析游戏状态：帧数据为空数组")
                return None
                
            # 分析游戏状态
            state = self.game_analyzer.analyze_frame(frame)
            if state:
                self.game_state.update_state(state)
                self.game_state_updated.emit(state)
                self.logger.debug(f"游戏状态已分析: {len(state)} 个属性")
                return state
            else:
                self.logger.warning("游戏状态分析返回空结果")
                return None
        except Exception as e:
            self.logger.error(f"分析游戏状态失败: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None