from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import numpy as np
from src.models.game_automation_model import GameAutomationModel
from src.services.config import Config
from src.services.logger import GameLogger
from src.services.window_manager import GameWindowManager
from src.services.game_analyzer import GameAnalyzer
from src.services.image_processor import ImageProcessor
from src.services.action_simulator import ActionSimulator
from src.services.game_state import GameState
from src.services.auto_operator import AutoOperator
from src.services.config_manager import ConfigManager
from src.services.config import config
import os
from typing import Optional

class MainViewModel(QObject):
    """主窗口视图模型"""
    # 定义信号
    window_list_updated = pyqtSignal(list)
    frame_updated = pyqtSignal(object)
    status_updated = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    automation_started = pyqtSignal()
    automation_stopped = pyqtSignal()
    game_state_updated = pyqtSignal(dict)  # 游戏状态更新
    
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
        
        # 创建模型和配置管理器
        self.model = GameAutomationModel(
            logger=logger,
            window_manager=window_manager,
            game_analyzer=game_analyzer,
            auto_operator=auto_operator,
            image_processor=image_processor,
            action_simulator=action_simulator,
            game_state=game_state,
            config=config
        )
        self.config_manager = ConfigManager(config)
        
        # 初始化属性
        self._current_window: Optional[str] = None
        self._is_running = False
        
        self._init_connections()
        self._init_timers()
        self._init_state()
        self._load_config()
        
    def _init_state(self):
        """初始化状态"""
        self._current_game_state = None
        
    def _load_config(self):
        """加载配置"""
        try:
            # 加载窗口配置
            window_config = self.config_manager.get_window_config()
            if window_config:
                config.window.refresh_interval = window_config.get('refresh_interval', config.window.refresh_interval)
                
            # 加载游戏状态配置
            game_state_config = self.config_manager.get_game_state_config()
            if game_state_config:
                config.game_state.analysis_interval = game_state_config.get('analysis_interval', config.game_state.analysis_interval)
                self._current_game_state = game_state_config.get('last_state', {})
                
        except Exception as e:
            self.logger.error(f"加载配置失败: {str(e)}")
            
    def _save_config(self):
        """保存配置"""
        try:
            # 保存窗口配置
            self.config_manager.set_value('window.refresh_interval', config.window.refresh_interval)
            
            # 保存游戏状态配置
            self.config_manager.set_value('game_state.analysis_interval', config.game_state.analysis_interval)
            if self._current_game_state:
                self.config_manager.update_last_game_state(self._current_game_state)
                
        except Exception as e:
            self.logger.error(f"保存配置失败: {str(e)}")
            
    def _init_connections(self):
        """初始化信号连接"""
        # 连接模型信号
        self.model.window_list_updated.connect(self.window_list_updated)
        self.model.frame_updated.connect(self.frame_updated)
        self.model.status_updated.connect(self.status_updated)
        self.model.automation_started.connect(self.automation_started)
        self.model.automation_stopped.connect(self.automation_stopped)
        self.model.automation_error.connect(self.error_occurred)
        self.model.game_state_updated.connect(self._on_game_state_updated)
        
        # 连接窗口管理器信号
        self.window_manager.window_changed.connect(self._on_window_changed)
        self.window_manager.window_selected.connect(self._on_window_selected)
        self.window_manager.screenshot_updated.connect(self._on_screenshot_updated)
        
    def _init_timers(self):
        """初始化定时器"""
        # 窗口列表刷新定时器
        self.window_refresh_timer = QTimer()
        self.window_refresh_timer.timeout.connect(self.refresh_windows)
        self.window_refresh_timer.setInterval(config.window.refresh_interval)
        
        # 画面更新定时器
        self.frame_update_timer = QTimer()
        self.frame_update_timer.timeout.connect(self.update_frame)
        self.frame_update_timer.setInterval(config.frame.update_interval)
        
        # 游戏状态分析定时器
        self.game_state_timer = QTimer()
        self.game_state_timer.timeout.connect(self._analyze_current_game_state)
        self.game_state_timer.setInterval(config.game_state.analysis_interval)
        
    def _on_game_state_updated(self, state: dict):
        """处理游戏状态更新"""
        self._current_game_state = state
        self.game_state_updated.emit(state)
        self.config_manager.update_last_game_state(state)
        
    def _analyze_current_game_state(self):
        """分析当前游戏状态"""
        if self.model._current_window and self.model.is_running:
            try:
                frame = self.model.capture_window()
                # 确保frame不是布尔值
                if isinstance(frame, bool):
                    self.logger.warning(f"无法分析游戏状态：帧数据为布尔值 ({frame})")
                    return
                    
                if frame is not None and isinstance(frame, np.ndarray) and frame.size > 0:
                    self.analyze_game_state(frame)
                else:
                    self.logger.debug("无法分析游戏状态：帧数据无效")
            except Exception as e:
                self.logger.error(f"分析游戏状态失败: {str(e)}")
                
    def start_window_refresh(self):
        """开始刷新窗口列表"""
        self.window_refresh_timer.start()
        self.refresh_windows()
        
    def stop_window_refresh(self):
        """停止刷新窗口列表"""
        self.window_refresh_timer.stop()
        
    def start_frame_update(self):
        """开始更新画面"""
        self.frame_update_timer.start()
        self.update_frame()
        
    def stop_frame_update(self):
        """停止更新画面"""
        self.frame_update_timer.stop()
        
    def start_game_state_analysis(self):
        """开始游戏状态分析"""
        self.game_state_timer.start()
        
    def stop_game_state_analysis(self):
        """停止游戏状态分析"""
        self.game_state_timer.stop()
        
    def refresh_windows(self):
        """刷新窗口列表"""
        try:
            self.model.get_window_list()
        except Exception as e:
            self.error_occurred.emit(f"刷新窗口列表失败: {str(e)}")
            self.logger.error(f"刷新窗口列表失败: {str(e)}")
            
    def update_frame(self):
        """更新画面"""
        try:
            if self.model._current_window:
                frame = self.model.capture_window()
                
                # 检查帧数据有效性
                if frame is not None and isinstance(frame, np.ndarray) and frame.size > 0:
                    self.frame_updated.emit(frame)
                elif isinstance(frame, bool):
                    self.logger.warning(f"更新画面失败：帧数据类型错误 (布尔值: {frame})")
                elif frame is None:
                    self.logger.debug("更新画面失败：帧数据为None")
                else:
                    self.logger.warning(f"更新画面失败：无效的帧数据类型 ({type(frame)})")
        except Exception as e:
            self.error_occurred.emit(f"更新画面失败: {str(e)}")
            self.logger.error(f"更新画面失败: {str(e)}")
            
    def start_automation(self):
        """开始自动化"""
        try:
            if not self.window_manager.get_selected_window():
                self.error_occurred.emit("请先选择游戏窗口")
                return
                
            self.auto_operator.start()
            self.automation_started.emit()
        except Exception as e:
            self.error_occurred.emit(f"启动自动化失败: {str(e)}")
            
    def stop_automation(self):
        """停止自动化"""
        try:
            self.auto_operator.stop()
            self.automation_stopped.emit()
        except Exception as e:
            self.error_occurred.emit(f"停止自动化失败: {str(e)}")
            
    def pause_automation(self):
        """暂停自动化"""
        try:
            self.auto_operator.pause()
        except Exception as e:
            self.error_occurred.emit(f"暂停自动化失败: {str(e)}")
            
    def resume_automation(self):
        """恢复自动化"""
        try:
            self.auto_operator.resume()
        except Exception as e:
            self.error_occurred.emit(f"恢复自动化失败: {str(e)}")
            
    def set_speed(self, value: int):
        """设置速度
        
        Args:
            value: 速度值(1-10)
        """
        try:
            self.auto_operator.set_speed(value)
        except Exception as e:
            self.error_occurred.emit(f"设置速度失败: {str(e)}")
            
    def set_auto_analyze(self, enabled: bool):
        """设置自动分析
        
        Args:
            enabled: 是否启用
        """
        try:
            self.auto_operator.set_auto_analyze(enabled)
        except Exception as e:
            self.error_occurred.emit(f"设置自动分析失败: {str(e)}")
            
    def set_auto_save(self, enabled: bool):
        """设置自动保存
        
        Args:
            enabled: 是否启用
        """
        try:
            self.auto_operator.set_auto_save(enabled)
        except Exception as e:
            self.error_occurred.emit(f"设置自动保存失败: {str(e)}")
            
    def analyze_game_state(self, frame=None):
        """分析游戏状态"""
        try:
            # 如果没有提供帧数据，尝试从模型获取
            if frame is None and self.model._current_window:
                frame = self.model.capture_window()
                
            # 检查帧数据类型
            if isinstance(frame, bool):
                self.logger.warning(f"无法分析游戏状态：帧数据为布尔值 ({frame})")
                return None
                
            # 检查帧数据有效性
            if frame is not None and isinstance(frame, np.ndarray) and frame.size > 0:
                # 分析游戏状态
                state = self.model.analyze_game_state(frame)
                if state:
                    self.logger.debug(f"成功分析游戏状态: {len(state)} 个属性")
                    return state
                else:
                    self.logger.warning("游戏状态分析返回空结果")
            else:
                self.logger.warning(f"无法分析游戏状态：无效的帧数据 (类型: {type(frame)})")
                
            return None
        except Exception as e:
            self.error_occurred.emit(f"分析游戏状态失败: {str(e)}")
            self.logger.error(f"分析游戏状态失败: {str(e)}")
            return None
    
    def get_current_window(self):
        """获取当前窗口"""
        return self.model._current_window
    
    def is_automation_running(self):
        """检查自动化是否正在运行"""
        return self.model.is_running
    
    def get_current_game_state(self):
        """获取当前游戏状态"""
        return self._current_game_state
    
    def get_last_selected_window(self) -> Optional[str]:
        """获取上次选择的窗口"""
        return self.config_manager.get_value('window.last_selected')
    
    def update_last_selected_window(self, window_title: str):
        """更新上次选择的窗口"""
        self.config_manager.set_value('window.last_selected', window_title)
    
    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self.model.is_running
    
    @property
    def current_window_handle(self) -> Optional[int]:
        """获取当前窗口句柄"""
        return self.model._current_window
        
    def _on_window_changed(self, window_list: list):
        """处理窗口列表更新"""
        self.window_list_updated.emit(window_list)
        
    def _on_window_selected(self, window_title: str):
        """处理窗口选择"""
        self._current_window = window_title
        self.logger.info(f"选择窗口: {window_title}")
        
    def _on_screenshot_updated(self, screenshot):
        """处理截图更新"""
        self.frame_updated.emit(screenshot)
        
    def select_window(self, window_handle: int):
        """选择游戏窗口
        
        Args:
            window_handle: 窗口句柄
        """
        try:
            self.window_manager.select_window(window_handle)
            self.status_updated.emit("已选择游戏窗口")
        except Exception as e:
            self.error_occurred.emit(f"选择窗口失败: {str(e)}")
            
    def start_automation(self):
        """开始自动化"""
        try:
            if not self.window_manager.get_selected_window():
                self.error_occurred.emit("请先选择游戏窗口")
                return
                
            self.auto_operator.start()
            self.automation_started.emit()
        except Exception as e:
            self.error_occurred.emit(f"启动自动化失败: {str(e)}")
            
    def stop_automation(self):
        """停止自动化"""
        try:
            self.auto_operator.stop()
            self.automation_stopped.emit()
        except Exception as e:
            self.error_occurred.emit(f"停止自动化失败: {str(e)}")
            
    def pause_automation(self):
        """暂停自动化"""
        try:
            self.auto_operator.pause()
        except Exception as e:
            self.error_occurred.emit(f"暂停自动化失败: {str(e)}")
            
    def resume_automation(self):
        """恢复自动化"""
        try:
            self.auto_operator.resume()
        except Exception as e:
            self.error_occurred.emit(f"恢复自动化失败: {str(e)}")
            
    def set_speed(self, value: int):
        """设置速度
        
        Args:
            value: 速度值(1-10)
        """
        try:
            self.auto_operator.set_speed(value)
        except Exception as e:
            self.error_occurred.emit(f"设置速度失败: {str(e)}")
            
    def set_auto_analyze(self, enabled: bool):
        """设置自动分析
        
        Args:
            enabled: 是否启用
        """
        try:
            self.auto_operator.set_auto_analyze(enabled)
        except Exception as e:
            self.error_occurred.emit(f"设置自动分析失败: {str(e)}")
            
    def set_auto_save(self, enabled: bool):
        """设置自动保存
        
        Args:
            enabled: 是否启用
        """
        try:
            self.auto_operator.set_auto_save(enabled)
        except Exception as e:
            self.error_occurred.emit(f"设置自动保存失败: {str(e)}") 