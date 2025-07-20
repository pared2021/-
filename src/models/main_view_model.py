from typing import Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal
import numpy as np
from ..services.config import Config
from ..services.logger import GameLogger
from ..services.window_manager import GameWindowManager
from ..services.game_analyzer import GameAnalyzer
from ..services.dqn_agent import DQNAgent
from ..services.image_processor import ImageProcessor
from ..services.action_simulator import ActionSimulator
from ..services.template_collector import TemplateCollector
from ..core.types import UnifiedGameState as GameState

class MainViewModel(QObject):
    """主视图模型"""
    
    # 定义信号
    frame_updated = pyqtSignal(np.ndarray)  # 画面更新信号
    status_updated = pyqtSignal(str)  # 状态更新信号
    window_list_updated = pyqtSignal(list)  # 窗口列表更新信号
    template_collection_progress = pyqtSignal(int)  # 模板收集进度信号
    model_training_progress = pyqtSignal(int)  # 模型训练进度信号
    game_state_updated = pyqtSignal(dict)  # 游戏状态更新信号
    
    def __init__(self, 
                 config: Config,
                 logger: GameLogger,
                 window_manager: GameWindowManager,
                 game_analyzer: GameAnalyzer,
                 dqn_agent: DQNAgent,
                 image_processor: ImageProcessor,
                 action_simulator: ActionSimulator,
                 template_collector: TemplateCollector,
                 game_state: GameState):
        """
        初始化主视图模型
        
        Args:
            config: 配置对象
            logger: 日志对象
            window_manager: 窗口管理器
            game_analyzer: 游戏分析器
            dqn_agent: DQN代理
            image_processor: 图像处理器
            action_simulator: 动作模拟器
            template_collector: 模板收集器
            game_state: 游戏状态
        """
        super().__init__()
        
        # 保存服务实例
        self.config = config
        self.logger = logger
        self.window_manager = window_manager
        self.game_analyzer = game_analyzer
        self.dqn_agent = dqn_agent
        self.image_processor = image_processor
        self.action_simulator = action_simulator
        self.template_collector = template_collector
        self.game_state = game_state
        
        # 初始化状态
        self._current_window = None
        self._is_running = False
        
        # 连接信号
        self._connect_signals()
        
    def _connect_signals(self):
        """连接信号"""
        # 窗口管理器信号
        self.window_manager.window_changed.connect(self._on_window_changed)
        self.window_manager.window_selected.connect(self._on_window_selected)
        self.window_manager.screenshot_updated.connect(self._on_screenshot_updated)
        
        # DQN代理信号
        self.dqn_agent.training_started.connect(lambda: self.status_updated.emit("开始训练"))
        self.dqn_agent.training_finished.connect(lambda: self.status_updated.emit("训练完成"))
        self.dqn_agent.training_progress.connect(lambda x: self.model_training_progress.emit(int(x * 100)))
        
    def get_template_config(self) -> Dict[str, Any]:
        """
        获取模板配置
        
        Returns:
            Dict[str, Any]: 模板配置字典
        """
        try:
            return {
                'output_dir': self.config.template.output_dir,
                'image_similarity_threshold': self.config.template.image_similarity_threshold,
                'duration': self.config.template.duration,
                'interval': self.config.template.interval,
                'collection_interval': self.config.template.collection_interval,
                'min_template_size': self.config.template.min_template_size,
                'max_template_size': self.config.template.max_template_size
            }
        except Exception as e:
            self.logger.error(f"获取模板配置失败: {str(e)}")
            raise
            
    def _on_window_changed(self, window_handle: int):
        """窗口变化处理"""
        self._current_window = window_handle
        self.status_updated.emit(f"当前窗口: {window_handle}")
        
    def _on_window_selected(self, window_handle: int):
        """窗口选择处理"""
        self._current_window = window_handle
        self.status_updated.emit(f"选择窗口: {window_handle}")
        
    def _on_screenshot_updated(self, frame: np.ndarray):
        """截图更新处理"""
        self.frame_updated.emit(frame)
        
    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._is_running
        
    @property
    def current_window(self) -> Optional[int]:
        """当前窗口句柄"""
        return self._current_window