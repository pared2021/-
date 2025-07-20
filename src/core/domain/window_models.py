"""统一窗口数据模型

这个模块定义了整个系统中使用的统一窗口数据结构，
解决多重WindowInfo定义冲突的问题。
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Any, List
from enum import Enum
import time


class WindowState(Enum):
    """窗口状态枚举"""
    UNKNOWN = "unknown"
    VISIBLE = "visible"
    HIDDEN = "hidden"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    FULLSCREEN = "fullscreen"
    DESTROYED = "destroyed"


class WindowType(Enum):
    """窗口类型枚举"""
    UNKNOWN = "unknown"
    GAME = "game"
    APPLICATION = "application"
    SYSTEM = "system"
    DIALOG = "dialog"
    POPUP = "popup"


@dataclass(frozen=True)
class WindowRect:
    """窗口矩形区域
    
    使用不可变数据类确保数据一致性
    """
    x: int
    y: int
    width: int
    height: int
    
    @property
    def right(self) -> int:
        """右边界坐标"""
        return self.x + self.width
    
    @property
    def bottom(self) -> int:
        """下边界坐标"""
        return self.y + self.height
    
    @property
    def center(self) -> Tuple[int, int]:
        """中心点坐标"""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def area(self) -> int:
        """窗口面积"""
        return self.width * self.height
    
    def contains_point(self, x: int, y: int) -> bool:
        """检查点是否在窗口内"""
        return (self.x <= x <= self.right and 
                self.y <= y <= self.bottom)
    
    def intersects(self, other: 'WindowRect') -> bool:
        """检查是否与另一个矩形相交"""
        return not (self.right < other.x or 
                   other.right < self.x or 
                   self.bottom < other.y or 
                   other.bottom < self.y)
    
    def to_tuple(self) -> Tuple[int, int, int, int]:
        """转换为元组格式 (x, y, width, height)"""
        return (self.x, self.y, self.width, self.height)
    
    def to_win32_rect(self) -> Tuple[int, int, int, int]:
        """转换为Win32 RECT格式 (left, top, right, bottom)"""
        return (self.x, self.y, self.right, self.bottom)
    
    @classmethod
    def from_tuple(cls, rect_tuple: Tuple[int, int, int, int]) -> 'WindowRect':
        """从元组创建WindowRect"""
        return cls(rect_tuple[0], rect_tuple[1], rect_tuple[2], rect_tuple[3])
    
    @classmethod
    def from_win32_rect(cls, left: int, top: int, right: int, bottom: int) -> 'WindowRect':
        """从Win32 RECT格式创建WindowRect"""
        return cls(left, top, right - left, bottom - top)


@dataclass
class WindowInfo:
    """统一的窗口信息数据模型
    
    这是整个系统中唯一的WindowInfo定义，
    所有其他WindowInfo定义都应该被这个替代。
    """
    
    # 基本标识信息
    handle: int  # 窗口句柄
    title: str   # 窗口标题
    class_name: str = ""  # 窗口类名
    
    # 进程信息
    process_id: int = 0  # 进程ID
    process_name: str = ""  # 进程名称
    
    # 几何信息
    rect: WindowRect = field(default_factory=lambda: WindowRect(0, 0, 0, 0))
    
    # 状态信息
    state: WindowState = WindowState.UNKNOWN
    window_type: WindowType = WindowType.UNKNOWN
    is_visible: bool = True
    is_enabled: bool = True
    is_active: bool = False
    is_foreground: bool = False
    
    # 元数据
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    # 扩展属性
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """后初始化处理"""
        # 确保handle是有效的
        if self.handle <= 0:
            raise ValueError(f"Invalid window handle: {self.handle}")
        
        # 自动推断窗口类型
        if self.window_type == WindowType.UNKNOWN:
            self.window_type = self._infer_window_type()
        
        # 自动推断窗口状态
        if self.state == WindowState.UNKNOWN:
            self.state = self._infer_window_state()
    
    def _infer_window_type(self) -> WindowType:
        """根据窗口信息推断窗口类型"""
        title_lower = self.title.lower()
        class_lower = self.class_name.lower()
        
        # 游戏窗口特征
        game_indicators = ['game', 'unity', 'unreal', 'directx', 'opengl']
        if any(indicator in title_lower or indicator in class_lower 
               for indicator in game_indicators):
            return WindowType.GAME
        
        # 对话框特征
        dialog_indicators = ['dialog', 'messagebox', 'alert']
        if any(indicator in class_lower for indicator in dialog_indicators):
            return WindowType.DIALOG
        
        # 系统窗口特征
        system_indicators = ['explorer', 'taskbar', 'desktop']
        if any(indicator in class_lower for indicator in system_indicators):
            return WindowType.SYSTEM
        
        return WindowType.APPLICATION
    
    def _infer_window_state(self) -> WindowState:
        """根据窗口信息推断窗口状态"""
        if not self.is_visible:
            return WindowState.HIDDEN
        
        # 这里可以添加更多的状态推断逻辑
        # 例如检查窗口大小来判断是否最大化等
        
        return WindowState.VISIBLE
    
    def update_timestamp(self) -> None:
        """更新时间戳"""
        self.updated_at = time.time()
    
    def is_valid(self) -> bool:
        """检查窗口信息是否有效"""
        return (self.handle > 0 and 
                self.title is not None and 
                self.rect.width > 0 and 
                self.rect.height > 0)
    
    def is_game_window(self) -> bool:
        """检查是否为游戏窗口"""
        return self.window_type == WindowType.GAME
    
    def is_minimized(self) -> bool:
        """检查是否最小化"""
        return self.state == WindowState.MINIMIZED
    
    def is_maximized(self) -> bool:
        """检查是否最大化"""
        return self.state == WindowState.MAXIMIZED
    
    def is_fullscreen(self) -> bool:
        """检查是否全屏"""
        return self.state == WindowState.FULLSCREEN
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """获取扩展属性"""
        return self.properties.get(key, default)
    
    def set_property(self, key: str, value: Any) -> None:
        """设置扩展属性"""
        self.properties[key] = value
        self.update_timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'handle': self.handle,
            'title': self.title,
            'class_name': self.class_name,
            'process_id': self.process_id,
            'process_name': self.process_name,
            'rect': self.rect.to_tuple(),
            'state': self.state.value,
            'window_type': self.window_type.value,
            'is_visible': self.is_visible,
            'is_enabled': self.is_enabled,
            'is_active': self.is_active,
            'is_foreground': self.is_foreground,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'properties': self.properties.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WindowInfo':
        """从字典创建WindowInfo"""
        rect_data = data.get('rect', (0, 0, 0, 0))
        rect = WindowRect.from_tuple(rect_data)
        
        return cls(
            handle=data['handle'],
            title=data['title'],
            class_name=data.get('class_name', ''),
            process_id=data.get('process_id', 0),
            process_name=data.get('process_name', ''),
            rect=rect,
            state=WindowState(data.get('state', WindowState.UNKNOWN.value)),
            window_type=WindowType(data.get('window_type', WindowType.UNKNOWN.value)),
            is_visible=data.get('is_visible', True),
            is_enabled=data.get('is_enabled', True),
            is_active=data.get('is_active', False),
            is_foreground=data.get('is_foreground', False),
            created_at=data.get('created_at', time.time()),
            updated_at=data.get('updated_at', time.time()),
            properties=data.get('properties', {})
        )
    
    def to_legacy_tuple(self) -> Tuple[int, str]:
        """转换为旧版本的(handle, title)元组格式
        
        用于向后兼容GUI层的期望格式
        """
        return (self.handle, self.title)
    
    def to_service_window_info(self) -> Dict[str, Any]:
        """转换为服务层WindowInfo格式
        
        用于兼容现有的services.window_manager.WindowInfo
        """
        return {
            'hwnd': self.handle,
            'title': self.title,
            'class_name': self.class_name,
            'rect': self.rect.to_tuple(),
            'is_visible': self.is_visible,
            'is_enabled': self.is_enabled
        }
    
    @classmethod
    def from_service_window_info(cls, service_info: Any) -> 'WindowInfo':
        """从服务层WindowInfo创建统一WindowInfo"""
        if hasattr(service_info, 'hwnd'):
            # 对象格式
            handle = service_info.hwnd
            title = getattr(service_info, 'title', '')
            class_name = getattr(service_info, 'class_name', '')
            rect_tuple = getattr(service_info, 'rect', (0, 0, 0, 0))
            is_visible = getattr(service_info, 'is_visible', True)
            is_enabled = getattr(service_info, 'is_enabled', True)
        else:
            # 字典格式
            handle = service_info.get('hwnd', 0)
            title = service_info.get('title', '')
            class_name = service_info.get('class_name', '')
            rect_tuple = service_info.get('rect', (0, 0, 0, 0))
            is_visible = service_info.get('is_visible', True)
            is_enabled = service_info.get('is_enabled', True)
        
        return cls(
            handle=handle,
            title=title,
            class_name=class_name,
            rect=WindowRect.from_tuple(rect_tuple),
            is_visible=is_visible,
            is_enabled=is_enabled
        )
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"WindowInfo(handle={self.handle}, title='{self.title}', rect={self.rect})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"WindowInfo(handle={self.handle}, title='{self.title}', "
                f"class_name='{self.class_name}', rect={self.rect}, "
                f"state={self.state}, type={self.window_type})")


@dataclass
class WindowListSnapshot:
    """窗口列表快照
    
    用于缓存和比较窗口列表状态
    """
    windows: List[WindowInfo]
    timestamp: float = field(default_factory=time.time)
    
    def get_window_by_handle(self, handle: int) -> Optional[WindowInfo]:
        """根据句柄获取窗口"""
        for window in self.windows:
            if window.handle == handle:
                return window
        return None
    
    def get_windows_by_title(self, title: str, exact_match: bool = False) -> List[WindowInfo]:
        """根据标题获取窗口列表"""
        if exact_match:
            return [w for w in self.windows if w.title == title]
        else:
            title_lower = title.lower()
            return [w for w in self.windows if title_lower in w.title.lower()]
    
    def get_game_windows(self) -> List[WindowInfo]:
        """获取所有游戏窗口"""
        return [w for w in self.windows if w.is_game_window()]
    
    def to_legacy_format(self) -> List[Tuple[int, str]]:
        """转换为旧版本格式"""
        return [window.to_legacy_tuple() for window in self.windows]
    
    def __len__(self) -> int:
        return len(self.windows)
    
    def __iter__(self):
        return iter(self.windows)