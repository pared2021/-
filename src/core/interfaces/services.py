"""核心业务服务接口定义

遵循Clean Architecture原则的接口定义，实现依赖倒置原则。
通过接口编程而不是具体实现，提高代码的可测试性和可维护性。
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Union, Protocol
import numpy as np
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


@dataclass
class Point:
    """坐标点"""
    x: int
    y: int


@dataclass
class Rectangle:
    """矩形区域"""
    x: int
    y: int
    width: int
    height: int


@dataclass
class WindowInfo:
    """窗口信息"""
    handle: int
    title: str
    class_name: str
    rect: Rectangle
    is_visible: bool
    is_active: bool


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ActionType(Enum):
    """动作类型"""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    KEY_PRESS = "key_press"
    KEY_COMBINATION = "key_combination"
    MOUSE_MOVE = "mouse_move"
    SCROLL = "scroll"
    DRAG = "drag"
    WAIT = "wait"


class GameState(Enum):
    """游戏状态"""
    UNKNOWN = "unknown"
    MENU = "menu"
    LOADING = "loading"
    IN_GAME = "in_game"
    PAUSED = "paused"
    BATTLE = "battle"
    INVENTORY = "inventory"
    SETTINGS = "settings"


@dataclass
class TemplateMatchResult:
    """模板匹配结果"""
    found: bool
    confidence: float
    location: Optional[Point] = None
    bounding_box: Optional[Rectangle] = None


@dataclass
class AnalysisResult:
    """分析结果数据类"""
    success: bool
    data: Dict[str, Any]
    confidence: float
    processing_time: float
    error_message: Optional[str] = None


class AutomationStatus(Enum):
    """自动化状态枚举"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class ActionResult:
    """操作结果数据类"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class IGameAnalyzer(ABC):
    """游戏分析器接口"""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化分析器"""
        pass
    
    @abstractmethod
    def analyze_frame(self, frame: np.ndarray) -> AnalysisResult:
        """分析游戏帧"""
        pass
    
    @abstractmethod
    def detect_game_state(self, frame: np.ndarray) -> Dict[str, Any]:
        """检测游戏状态"""
        pass
    
    @abstractmethod
    def find_elements(self, frame: np.ndarray, elements: List[str]) -> Dict[str, Any]:
        """查找界面元素"""
        pass
    
    @abstractmethod
    def get_supported_games(self) -> List[str]:
        """获取支持的游戏列表"""
        pass
    
    @abstractmethod
    def set_game_context(self, game_id: str) -> bool:
        """设置游戏上下文"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """清理资源"""
        pass


class IAutomationService(ABC):
    """自动化服务接口"""
    
    @abstractmethod
    def start_automation(self, task_config: Dict[str, Any]) -> bool:
        """启动自动化任务"""
        pass
    
    @abstractmethod
    def stop_automation(self) -> bool:
        """停止自动化任务"""
        pass
    
    @abstractmethod
    def pause_automation(self) -> bool:
        """暂停自动化任务"""
        pass
    
    @abstractmethod
    def resume_automation(self) -> bool:
        """恢复自动化任务"""
        pass
    
    @abstractmethod
    def get_automation_status(self) -> AutomationStatus:
        """获取自动化状态"""
        pass
    
    @abstractmethod
    def execute_action(self, action: Dict[str, Any]) -> ActionResult:
        """执行单个操作"""
        pass
    
    @abstractmethod
    def get_available_actions(self) -> List[Dict[str, Any]]:
        """获取可用操作列表"""
        pass
    
    @abstractmethod
    def validate_task_config(self, config: Dict[str, Any]) -> bool:
        """验证任务配置"""
        pass


class IStateManager(ABC):
    """状态管理器接口"""
    
    @abstractmethod
    def get_current_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        pass
    
    @abstractmethod
    def update_state(self, state_data: Dict[str, Any]) -> bool:
        """更新状态"""
        pass
    
    @abstractmethod
    def save_state(self, state_id: str) -> bool:
        """保存状态"""
        pass
    
    @abstractmethod
    def load_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """加载状态"""
        pass
    
    @abstractmethod
    def get_state_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取状态历史"""
        pass
    
    @abstractmethod
    def clear_state_history(self) -> bool:
        """清空状态历史"""
        pass
    
    @abstractmethod
    def subscribe_state_change(self, callback) -> str:
        """订阅状态变化"""
        pass
    
    @abstractmethod
    def unsubscribe_state_change(self, subscription_id: str) -> bool:
        """取消订阅状态变化"""
        pass


class IPerformanceMonitor(ABC):
    """性能监控接口"""
    
    @abstractmethod
    def start_monitoring(self) -> bool:
        """开始监控"""
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> bool:
        """停止监控"""
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        pass
    
    @abstractmethod
    def reset_metrics(self) -> bool:
        """重置性能指标"""
        pass


class IErrorHandler(ABC):
    """错误处理接口"""
    
    @abstractmethod
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """处理错误"""
        pass
    
    @abstractmethod
    def register_error_handler(self, error_type: type, handler: callable) -> None:
        """注册错误处理器"""
        pass
    
    @abstractmethod
    def get_error_statistics(self) -> Dict[str, int]:
        """获取错误统计"""
        pass


# ============================================================================
# 核心基础服务接口
# ============================================================================

class IConfigService(ABC):
    """配置服务接口"""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        pass
    
    @abstractmethod
    def has(self, key: str) -> bool:
        """检查配置项是否存在"""
        pass
    
    @abstractmethod
    def get_section(self, section: str) -> Dict[str, Any]:
        """获取配置段"""
        pass
    
    @abstractmethod
    def save(self) -> bool:
        """保存配置"""
        pass
    
    @abstractmethod
    def reload(self) -> bool:
        """重新加载配置"""
        pass


class ILoggerService(ABC):
    """日志服务接口"""
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """记录调试信息"""
        pass
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """记录信息"""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """记录警告"""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """记录错误"""
        pass
    
    @abstractmethod
    def critical(self, message: str, **kwargs) -> None:
        """记录严重错误"""
        pass
    
    @abstractmethod
    def set_level(self, level: LogLevel) -> None:
        """设置日志级别"""
        pass


class IWindowManagerService(ABC):
    """窗口管理服务接口"""
    
    @abstractmethod
    def find_game_window(self, window_title: str = None) -> Optional[WindowInfo]:
        """查找游戏窗口"""
        pass
    
    @abstractmethod
    def get_window_info(self, handle: int) -> Optional[WindowInfo]:
        """获取窗口信息"""
        pass
    
    @abstractmethod
    def activate_window(self, handle: int) -> bool:
        """激活窗口"""
        pass
    
    @abstractmethod
    def capture_window(self, handle: int) -> Optional[np.ndarray]:
        """捕获窗口截图"""
        pass
    
    @abstractmethod
    def get_window_rect(self, handle: int) -> Optional[Rectangle]:
        """获取窗口矩形"""
        pass


class IImageProcessorService(ABC):
    """图像处理服务接口"""
    
    @abstractmethod
    def match_template(self, image: np.ndarray, template: np.ndarray, 
                      threshold: float = 0.8) -> TemplateMatchResult:
        """模板匹配"""
        pass
    
    @abstractmethod
    def find_text(self, image: np.ndarray, text: str) -> List[Rectangle]:
        """查找文本"""
        pass
    
    @abstractmethod
    def extract_text(self, image: np.ndarray, region: Optional[Rectangle] = None) -> str:
        """提取文本"""
        pass
    
    @abstractmethod
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """预处理图像"""
        pass
    
    @abstractmethod
    def save_image(self, image: np.ndarray, path: Path) -> bool:
        """保存图像"""
        pass


class IActionSimulatorService(ABC):
    """动作模拟服务接口"""
    
    @abstractmethod
    def click(self, point: Point, window_handle: Optional[int] = None) -> ActionResult:
        """点击"""
        pass
    
    @abstractmethod
    def double_click(self, point: Point, window_handle: Optional[int] = None) -> ActionResult:
        """双击"""
        pass
    
    @abstractmethod
    def right_click(self, point: Point, window_handle: Optional[int] = None) -> ActionResult:
        """右键点击"""
        pass
    
    @abstractmethod
    def key_press(self, key: str, window_handle: Optional[int] = None) -> ActionResult:
        """按键"""
        pass
    
    @abstractmethod
    def key_combination(self, keys: List[str], window_handle: Optional[int] = None) -> ActionResult:
        """组合键"""
        pass
    
    @abstractmethod
    def mouse_move(self, point: Point, window_handle: Optional[int] = None) -> ActionResult:
        """移动鼠标"""
        pass
    
    @abstractmethod
    def scroll(self, point: Point, direction: str, amount: int, 
              window_handle: Optional[int] = None) -> ActionResult:
        """滚动"""
        pass
    
    @abstractmethod
    def drag(self, start: Point, end: Point, window_handle: Optional[int] = None) -> ActionResult:
        """拖拽"""
        pass


class IGameStateService(ABC):
    """游戏状态服务接口"""
    
    @abstractmethod
    def get_current_state(self) -> GameState:
        """获取当前状态"""
        pass
    
    @abstractmethod
    def update_state(self, new_state: GameState) -> None:
        """更新状态"""
        pass
    
    @abstractmethod
    def get_state_history(self, limit: int = 10) -> List[Tuple[GameState, float]]:
        """获取状态历史"""
        pass
    
    @abstractmethod
    def is_state_stable(self, duration: float = 1.0) -> bool:
        """检查状态是否稳定"""
        pass


# ============================================================================
# 服务工厂接口
# ============================================================================

class IServiceFactory(Protocol):
    """服务工厂接口"""
    
    def create_config_service(self) -> IConfigService:
        """创建配置服务"""
        ...
    
    def create_logger_service(self) -> ILoggerService:
        """创建日志服务"""
        ...
    
    def create_window_manager_service(self) -> IWindowManagerService:
        """创建窗口管理服务"""
        ...
    
    def create_image_processor_service(self) -> IImageProcessorService:
        """创建图像处理服务"""
        ...
    
    def create_game_analyzer_service(self) -> IGameAnalyzer:
        """创建游戏分析服务"""
        ...
    
    def create_action_simulator_service(self) -> IActionSimulatorService:
        """创建动作模拟服务"""
        ...
    
    def create_game_state_service(self) -> IGameStateService:
        """创建游戏状态服务"""
        ...
    
    def create_automation_service(self) -> IAutomationService:
        """创建自动化服务"""
        ...
    
    def create_error_handler_service(self) -> IErrorHandler:
        """创建错误处理服务"""
        ...
    
    @abstractmethod
    def get_error_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取错误日志"""
        pass
    
    @abstractmethod
    def clear_error_logs(self) -> bool:
        """清空错误日志"""
        pass