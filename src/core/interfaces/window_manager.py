"""统一窗口管理器接口

这个模块定义了统一的窗口管理器接口，
替代现有的多个分散的窗口管理接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Dict, Any
from ..domain.window_models import WindowInfo, WindowListSnapshot, WindowRect


class WindowEventType:
    """窗口事件类型常量"""
    CREATED = "window_created"
    DESTROYED = "window_destroyed"
    ACTIVATED = "window_activated"
    DEACTIVATED = "window_deactivated"
    MOVED = "window_moved"
    RESIZED = "window_resized"
    TITLE_CHANGED = "window_title_changed"
    STATE_CHANGED = "window_state_changed"


class WindowManagerError(Exception):
    """窗口管理器异常基类"""
    pass


class WindowNotFoundError(WindowManagerError):
    """窗口未找到异常"""
    def __init__(self, handle: int, message: str = None):
        self.handle = handle
        super().__init__(message or f"Window with handle {handle} not found")


class WindowOperationError(WindowManagerError):
    """窗口操作异常"""
    def __init__(self, operation: str, handle: int, message: str = None):
        self.operation = operation
        self.handle = handle
        super().__init__(message or f"Failed to {operation} window {handle}")


class IWindowEventHandler(ABC):
    """窗口事件处理器接口"""
    
    @abstractmethod
    def on_window_event(self, event_type: str, window_info: WindowInfo, **kwargs) -> None:
        """处理窗口事件
        
        Args:
            event_type: 事件类型
            window_info: 窗口信息
            **kwargs: 额外的事件数据
        """
        pass


class IWindowManager(ABC):
    """统一窗口管理器接口
    
    这是整个系统中唯一的窗口管理器接口，
    所有窗口相关操作都应该通过这个接口进行。
    """
    
    # 窗口发现和查询
    @abstractmethod
    def get_all_windows(self, include_hidden: bool = False) -> WindowListSnapshot:
        """获取所有窗口列表
        
        Args:
            include_hidden: 是否包含隐藏窗口
            
        Returns:
            窗口列表快照
            
        Raises:
            WindowManagerError: 获取窗口列表失败
        """
        pass
    
    @abstractmethod
    def get_window_by_handle(self, handle: int) -> Optional[WindowInfo]:
        """根据句柄获取窗口信息
        
        Args:
            handle: 窗口句柄
            
        Returns:
            窗口信息，如果不存在返回None
            
        Raises:
            WindowManagerError: 获取窗口信息失败
        """
        pass
    
    @abstractmethod
    def find_windows_by_title(self, title: str, exact_match: bool = False) -> List[WindowInfo]:
        """根据标题查找窗口
        
        Args:
            title: 窗口标题
            exact_match: 是否精确匹配
            
        Returns:
            匹配的窗口列表
            
        Raises:
            WindowManagerError: 查找窗口失败
        """
        pass
    
    @abstractmethod
    def find_windows_by_class(self, class_name: str) -> List[WindowInfo]:
        """根据类名查找窗口
        
        Args:
            class_name: 窗口类名
            
        Returns:
            匹配的窗口列表
            
        Raises:
            WindowManagerError: 查找窗口失败
        """
        pass
    
    @abstractmethod
    def find_windows_by_process(self, process_id: int = None, process_name: str = None) -> List[WindowInfo]:
        """根据进程查找窗口
        
        Args:
            process_id: 进程ID
            process_name: 进程名称
            
        Returns:
            匹配的窗口列表
            
        Raises:
            WindowManagerError: 查找窗口失败
        """
        pass
    
    @abstractmethod
    def find_game_windows(self) -> List[WindowInfo]:
        """查找游戏窗口
        
        Returns:
            游戏窗口列表
            
        Raises:
            WindowManagerError: 查找游戏窗口失败
        """
        pass
    
    # 窗口操作
    @abstractmethod
    def activate_window(self, handle: int) -> bool:
        """激活窗口
        
        Args:
            handle: 窗口句柄
            
        Returns:
            操作是否成功
            
        Raises:
            WindowNotFoundError: 窗口不存在
            WindowOperationError: 激活失败
        """
        pass
    
    @abstractmethod
    def move_window(self, handle: int, x: int, y: int) -> bool:
        """移动窗口
        
        Args:
            handle: 窗口句柄
            x: 新的X坐标
            y: 新的Y坐标
            
        Returns:
            操作是否成功
            
        Raises:
            WindowNotFoundError: 窗口不存在
            WindowOperationError: 移动失败
        """
        pass
    
    @abstractmethod
    def resize_window(self, handle: int, width: int, height: int) -> bool:
        """调整窗口大小
        
        Args:
            handle: 窗口句柄
            width: 新的宽度
            height: 新的高度
            
        Returns:
            操作是否成功
            
        Raises:
            WindowNotFoundError: 窗口不存在
            WindowOperationError: 调整大小失败
        """
        pass
    
    @abstractmethod
    def set_window_rect(self, handle: int, rect: WindowRect) -> bool:
        """设置窗口矩形区域
        
        Args:
            handle: 窗口句柄
            rect: 新的窗口矩形
            
        Returns:
            操作是否成功
            
        Raises:
            WindowNotFoundError: 窗口不存在
            WindowOperationError: 设置失败
        """
        pass
    
    @abstractmethod
    def close_window(self, handle: int, force: bool = False) -> bool:
        """关闭窗口
        
        Args:
            handle: 窗口句柄
            force: 是否强制关闭
            
        Returns:
            操作是否成功
            
        Raises:
            WindowNotFoundError: 窗口不存在
            WindowOperationError: 关闭失败
        """
        pass
    
    @abstractmethod
    def minimize_window(self, handle: int) -> bool:
        """最小化窗口
        
        Args:
            handle: 窗口句柄
            
        Returns:
            操作是否成功
            
        Raises:
            WindowNotFoundError: 窗口不存在
            WindowOperationError: 最小化失败
        """
        pass
    
    @abstractmethod
    def maximize_window(self, handle: int) -> bool:
        """最大化窗口
        
        Args:
            handle: 窗口句柄
            
        Returns:
            操作是否成功
            
        Raises:
            WindowNotFoundError: 窗口不存在
            WindowOperationError: 最大化失败
        """
        pass
    
    @abstractmethod
    def restore_window(self, handle: int) -> bool:
        """恢复窗口
        
        Args:
            handle: 窗口句柄
            
        Returns:
            操作是否成功
            
        Raises:
            WindowNotFoundError: 窗口不存在
            WindowOperationError: 恢复失败
        """
        pass
    
    # 窗口状态查询
    @abstractmethod
    def is_window_visible(self, handle: int) -> bool:
        """检查窗口是否可见
        
        Args:
            handle: 窗口句柄
            
        Returns:
            窗口是否可见
            
        Raises:
            WindowNotFoundError: 窗口不存在
        """
        pass
    
    @abstractmethod
    def is_window_active(self, handle: int) -> bool:
        """检查窗口是否激活
        
        Args:
            handle: 窗口句柄
            
        Returns:
            窗口是否激活
            
        Raises:
            WindowNotFoundError: 窗口不存在
        """
        pass
    
    @abstractmethod
    def get_window_rect(self, handle: int) -> WindowRect:
        """获取窗口矩形区域
        
        Args:
            handle: 窗口句柄
            
        Returns:
            窗口矩形区域
            
        Raises:
            WindowNotFoundError: 窗口不存在
        """
        pass
    
    # 窗口捕获
    @abstractmethod
    def capture_window(self, handle: int, region: Optional[WindowRect] = None) -> Optional[bytes]:
        """捕获窗口截图
        
        Args:
            handle: 窗口句柄
            region: 捕获区域，None表示整个窗口
            
        Returns:
            图像数据，失败返回None
            
        Raises:
            WindowNotFoundError: 窗口不存在
            WindowOperationError: 捕获失败
        """
        pass
    
    # 事件处理
    @abstractmethod
    def add_event_handler(self, handler: IWindowEventHandler) -> None:
        """添加事件处理器
        
        Args:
            handler: 事件处理器
        """
        pass
    
    @abstractmethod
    def remove_event_handler(self, handler: IWindowEventHandler) -> None:
        """移除事件处理器
        
        Args:
            handler: 事件处理器
        """
        pass
    
    @abstractmethod
    def start_monitoring(self) -> None:
        """开始监控窗口事件
        
        Raises:
            WindowManagerError: 启动监控失败
        """
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> None:
        """停止监控窗口事件
        
        Raises:
            WindowManagerError: 停止监控失败
        """
        pass
    
    # 缓存和性能
    @abstractmethod
    def refresh_window_list(self) -> None:
        """刷新窗口列表缓存
        
        Raises:
            WindowManagerError: 刷新失败
        """
        pass
    
    @abstractmethod
    def clear_cache(self) -> None:
        """清除所有缓存"""
        pass
    
    # 配置和状态
    @abstractmethod
    def get_configuration(self) -> Dict[str, Any]:
        """获取配置信息
        
        Returns:
            配置字典
        """
        pass
    
    @abstractmethod
    def set_configuration(self, config: Dict[str, Any]) -> None:
        """设置配置信息
        
        Args:
            config: 配置字典
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """获取管理器状态
        
        Returns:
            状态字典
        """
        pass
    
    # 生命周期管理
    @abstractmethod
    def initialize(self) -> None:
        """初始化窗口管理器
        
        Raises:
            WindowManagerError: 初始化失败
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """关闭窗口管理器
        
        Raises:
            WindowManagerError: 关闭失败
        """
        pass
    
    @abstractmethod
    def is_initialized(self) -> bool:
        """检查是否已初始化
        
        Returns:
            是否已初始化
        """
        pass


class IWindowManagerFactory(ABC):
    """窗口管理器工厂接口"""
    
    @abstractmethod
    def create_window_manager(self, config: Dict[str, Any] = None) -> IWindowManager:
        """创建窗口管理器实例
        
        Args:
            config: 配置参数
            
        Returns:
            窗口管理器实例
            
        Raises:
            WindowManagerError: 创建失败
        """
        pass
    
    @abstractmethod
    def get_supported_platforms(self) -> List[str]:
        """获取支持的平台列表
        
        Returns:
            支持的平台列表
        """
        pass
    
    @abstractmethod
    def is_platform_supported(self, platform: str) -> bool:
        """检查平台是否支持
        
        Args:
            platform: 平台名称
            
        Returns:
            是否支持
        """
        pass