"""
窗口管理服务
负责窗口的查找、管理和基本操作
"""
from typing import List, Optional, Dict
import win32gui
import win32con
from dataclasses import dataclass
from core.error_handler import ErrorHandler, ErrorCode, ErrorContext

@dataclass
class WindowInfo:
    """窗口信息"""
    hwnd: int  # 窗口句柄
    title: str  # 窗口标题
    class_name: str  # 窗口类名
    rect: tuple  # 窗口位置和大小 (left, top, right, bottom)
    is_visible: bool  # 是否可见
    is_enabled: bool  # 是否启用

class WindowManager:
    """窗口管理器"""
    
    def __init__(self, error_handler: ErrorHandler):
        """初始化
        
        Args:
            error_handler: 错误处理器
        """
        self.error_handler = error_handler
        self.windows: Dict[int, WindowInfo] = {}
        
    def find_windows(self, title_pattern: Optional[str] = None, 
                    class_pattern: Optional[str] = None) -> List[WindowInfo]:
        """查找窗口
        
        Args:
            title_pattern: 标题匹配模式
            class_pattern: 类名匹配模式
            
        Returns:
            List[WindowInfo]: 窗口列表
        """
        try:
            windows = []
            
            def callback(hwnd, _):
                if not win32gui.IsWindowVisible(hwnd):
                    return True
                    
                title = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                
                # 检查标题和类名是否匹配
                if title_pattern and title_pattern not in title:
                    return True
                if class_pattern and class_pattern not in class_name:
                    return True
                    
                # 获取窗口信息
                rect = win32gui.GetWindowRect(hwnd)
                is_visible = win32gui.IsWindowVisible(hwnd)
                is_enabled = win32gui.IsWindowEnabled(hwnd)
                
                window_info = WindowInfo(
                    hwnd=hwnd,
                    title=title,
                    class_name=class_name,
                    rect=rect,
                    is_visible=is_visible,
                    is_enabled=is_enabled
                )
                
                windows.append(window_info)
                self.windows[hwnd] = window_info
                return True
                
            win32gui.EnumWindows(callback, None)
            return windows
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.WINDOW_ERROR,
                "查找窗口失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="WindowManager.find_windows"
                )
            )
            return []
            
    def get_window_info(self, hwnd: int) -> Optional[WindowInfo]:
        """获取窗口信息
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            Optional[WindowInfo]: 窗口信息
        """
        try:
            if hwnd in self.windows:
                return self.windows[hwnd]
                
            if not win32gui.IsWindow(hwnd):
                return None
                
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            rect = win32gui.GetWindowRect(hwnd)
            is_visible = win32gui.IsWindowVisible(hwnd)
            is_enabled = win32gui.IsWindowEnabled(hwnd)
            
            window_info = WindowInfo(
                hwnd=hwnd,
                title=title,
                class_name=class_name,
                rect=rect,
                is_visible=is_visible,
                is_enabled=is_enabled
            )
            
            self.windows[hwnd] = window_info
            return window_info
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.WINDOW_ERROR,
                "获取窗口信息失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="WindowManager.get_window_info"
                )
            )
            return None
            
    def set_window_pos(self, hwnd: int, x: int, y: int, 
                      width: int, height: int) -> bool:
        """设置窗口位置和大小
        
        Args:
            hwnd: 窗口句柄
            x: 左上角x坐标
            y: 左上角y坐标
            width: 宽度
            height: 高度
            
        Returns:
            bool: 是否成功
        """
        try:
            flags = win32con.SWP_SHOWWINDOW
            return win32gui.SetWindowPos(hwnd, 0, x, y, width, height, flags)
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.WINDOW_ERROR,
                "设置窗口位置失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="WindowManager.set_window_pos"
                )
            )
            return False
            
    def set_window_foreground(self, hwnd: int) -> bool:
        """将窗口置于前台
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            bool: 是否成功
        """
        try:
            return win32gui.SetForegroundWindow(hwnd)
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.WINDOW_ERROR,
                "设置窗口前台失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="WindowManager.set_window_foreground"
                )
            )
            return False
            
    def is_window_valid(self, hwnd: int) -> bool:
        """检查窗口是否有效
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            bool: 是否有效
        """
        try:
            return win32gui.IsWindow(hwnd)
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.WINDOW_ERROR,
                "检查窗口有效性失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="WindowManager.is_window_valid"
                )
            )
            return False 