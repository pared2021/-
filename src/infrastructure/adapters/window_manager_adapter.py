"""窗口管理服务适配器

这个模块提供了窗口管理服务的适配器实现，将现有的窗口管理系统包装为符合IWindowManagerService接口的服务。
使用适配器模式来保持向后兼容性，同时支持新的依赖注入架构。
"""

from typing import List, Optional, Tuple, Dict, Any
import time

from ...core.interfaces.services import (
    IWindowManagerService, ILoggerService, IConfigService, IErrorHandler,
    Point, Rectangle, WindowInfo
)


class WindowManagerServiceAdapter(IWindowManagerService):
    """窗口管理服务适配器
    
    将现有的窗口管理系统适配为IWindowManagerService接口。
    提供窗口查找、操作和监控功能。
    """
    
    def __init__(self, logger_service: Optional[ILoggerService] = None,
                 config_service: Optional[IConfigService] = None,
                 error_handler: Optional[IErrorHandler] = None):
        self._logger_service = logger_service
        self._config_service = config_service
        self._error_handler = error_handler
        self._window_manager_instance = None
        self._is_initialized = False
        self._cached_windows: Dict[str, WindowInfo] = {}
        self._cache_timeout = 5.0  # 缓存超时时间（秒）
        self._last_cache_update = 0
    
    def _ensure_window_manager_loaded(self) -> None:
        """确保窗口管理器已加载"""
        if not self._is_initialized:
            try:
                # 尝试导入现有的窗口管理系统
                from ...common.window_manager import window_manager
                self._window_manager_instance = window_manager
                self._is_initialized = True
                self._log_info("窗口管理器已加载")
            except ImportError as e:
                self._log_error(f"无法导入现有窗口管理系统: {e}")
                # 创建一个基本的窗口管理器实现
                self._create_fallback_window_manager()
                self._is_initialized = True
    
    def _create_fallback_window_manager(self) -> None:
        """创建备用窗口管理器"""
        try:
            import win32gui
            import win32con
            self._win32gui = win32gui
            self._win32con = win32con
            self._window_manager_instance = self
            self._log_info("使用备用窗口管理器")
        except ImportError:
            self._log_error("无法导入win32gui，窗口管理功能将受限")
            self._window_manager_instance = None
    
    def _log_info(self, message: str, **kwargs) -> None:
        """记录信息日志"""
        if self._logger_service:
            self._logger_service.info(message, **kwargs)
    
    def _log_error(self, message: str, **kwargs) -> None:
        """记录错误日志"""
        if self._logger_service:
            self._logger_service.error(message, **kwargs)
    
    def _log_warning(self, message: str, **kwargs) -> None:
        """记录警告日志"""
        if self._logger_service:
            self._logger_service.warning(message, **kwargs)
    
    def _handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """处理错误"""
        if self._error_handler:
            self._error_handler.handle_error(error, context)
        else:
            self._log_error(f"窗口管理错误: {error}")
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        return (time.time() - self._last_cache_update) < self._cache_timeout
    
    def _update_cache(self) -> None:
        """更新窗口缓存"""
        self._cached_windows.clear()
        self._last_cache_update = time.time()
    
    def find_window(self, title: Optional[str] = None, 
                   class_name: Optional[str] = None) -> Optional[WindowInfo]:
        """查找窗口"""
        self._ensure_window_manager_loaded()
        
        if not self._window_manager_instance:
            return None
        
        try:
            # 如果有现有的窗口管理器方法，使用它
            if (hasattr(self._window_manager_instance, 'find_window') and 
                self._window_manager_instance != self):
                result = self._window_manager_instance.find_window(title, class_name)
                if result:
                    # 转换为WindowInfo格式
                    return self._convert_to_window_info(result)
            
            # 使用备用实现
            return self._find_window_fallback(title, class_name)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'find_window', 'title': title, 'class_name': class_name})
            return None
    
    def _find_window_fallback(self, title: Optional[str] = None, 
                             class_name: Optional[str] = None) -> Optional[WindowInfo]:
        """备用窗口查找实现"""
        if not hasattr(self, '_win32gui'):
            return None
        
        try:
            def enum_windows_callback(hwnd, windows):
                if self._win32gui.IsWindowVisible(hwnd):
                    window_title = self._win32gui.GetWindowText(hwnd)
                    window_class = self._win32gui.GetClassName(hwnd)
                    
                    title_match = not title or (title.lower() in window_title.lower())
                    class_match = not class_name or (class_name.lower() in window_class.lower())
                    
                    if title_match and class_match:
                        rect = self._win32gui.GetWindowRect(hwnd)
                        windows.append({
                            'hwnd': hwnd,
                            'title': window_title,
                            'class_name': window_class,
                            'rect': rect
                        })
            
            windows = []
            self._win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                window_data = windows[0]  # 返回第一个匹配的窗口
                rect = window_data['rect']
                return WindowInfo(
                    handle=window_data['hwnd'],
                    title=window_data['title'],
                    class_name=window_data['class_name'],
                    bounds=Rectangle(
                        x=rect[0], y=rect[1],
                        width=rect[2] - rect[0],
                        height=rect[3] - rect[1]
                    ),
                    is_visible=True,
                    is_minimized=self._win32gui.IsIconic(window_data['hwnd']),
                    process_id=0  # 需要额外的API调用来获取
                )
        
        except Exception as e:
            self._handle_error(e, {'operation': '_find_window_fallback'})
        
        return None
    
    def _convert_to_window_info(self, window_data: Any) -> WindowInfo:
        """转换窗口数据为WindowInfo格式"""
        # 这里需要根据现有窗口管理器的返回格式进行适配
        if hasattr(window_data, 'hwnd'):
            return WindowInfo(
                handle=getattr(window_data, 'hwnd', 0),
                title=getattr(window_data, 'title', ''),
                class_name=getattr(window_data, 'class_name', ''),
                bounds=getattr(window_data, 'bounds', Rectangle(0, 0, 0, 0)),
                is_visible=getattr(window_data, 'is_visible', True),
                is_minimized=getattr(window_data, 'is_minimized', False),
                process_id=getattr(window_data, 'process_id', 0)
            )
        else:
            # 如果是字典格式
            return WindowInfo(
                handle=window_data.get('hwnd', 0),
                title=window_data.get('title', ''),
                class_name=window_data.get('class_name', ''),
                bounds=window_data.get('bounds', Rectangle(0, 0, 0, 0)),
                is_visible=window_data.get('is_visible', True),
                is_minimized=window_data.get('is_minimized', False),
                process_id=window_data.get('process_id', 0)
            )
    
    def get_all_windows(self) -> List[WindowInfo]:
        """获取所有窗口"""
        self._ensure_window_manager_loaded()
        
        if not self._window_manager_instance:
            return []
        
        try:
            # 检查缓存
            if self._is_cache_valid() and self._cached_windows:
                return list(self._cached_windows.values())
            
            # 如果有现有的方法，使用它
            if (hasattr(self._window_manager_instance, 'get_all_windows') and 
                self._window_manager_instance != self):
                windows = self._window_manager_instance.get_all_windows()
                return [self._convert_to_window_info(w) for w in windows]
            
            # 使用备用实现
            return self._get_all_windows_fallback()
        
        except Exception as e:
            self._handle_error(e, {'operation': 'get_all_windows'})
            return []
    
    def _get_all_windows_fallback(self) -> List[WindowInfo]:
        """备用获取所有窗口实现"""
        if not hasattr(self, '_win32gui'):
            return []
        
        try:
            def enum_windows_callback(hwnd, windows):
                if self._win32gui.IsWindowVisible(hwnd):
                    window_title = self._win32gui.GetWindowText(hwnd)
                    window_class = self._win32gui.GetClassName(hwnd)
                    rect = self._win32gui.GetWindowRect(hwnd)
                    
                    window_info = WindowInfo(
                        handle=hwnd,
                        title=window_title,
                        class_name=window_class,
                        bounds=Rectangle(
                            x=rect[0], y=rect[1],
                            width=rect[2] - rect[0],
                            height=rect[3] - rect[1]
                        ),
                        is_visible=True,
                        is_minimized=self._win32gui.IsIconic(hwnd),
                        process_id=0
                    )
                    windows.append(window_info)
            
            windows = []
            self._win32gui.EnumWindows(enum_windows_callback, windows)
            
            # 更新缓存
            self._cached_windows = {w.title: w for w in windows}
            self._update_cache()
            
            return windows
        
        except Exception as e:
            self._handle_error(e, {'operation': '_get_all_windows_fallback'})
            return []
    
    def activate_window(self, window: WindowInfo) -> bool:
        """激活窗口"""
        self._ensure_window_manager_loaded()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._window_manager_instance, 'activate_window') and 
                self._window_manager_instance != self):
                return self._window_manager_instance.activate_window(window)
            
            # 使用备用实现
            return self._activate_window_fallback(window)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'activate_window', 'window': window.title})
            return False
    
    def _activate_window_fallback(self, window: WindowInfo) -> bool:
        """备用窗口激活实现"""
        if not hasattr(self, '_win32gui'):
            return False
        
        try:
            hwnd = window.handle
            if hwnd:
                # 如果窗口最小化，先恢复
                if self._win32gui.IsIconic(hwnd):
                    self._win32gui.ShowWindow(hwnd, self._win32con.SW_RESTORE)
                
                # 激活窗口
                self._win32gui.SetForegroundWindow(hwnd)
                self._win32gui.SetActiveWindow(hwnd)
                
                self._log_info(f"窗口已激活: {window.title}")
                return True
        
        except Exception as e:
            self._handle_error(e, {'operation': '_activate_window_fallback'})
        
        return False
    
    def get_window_bounds(self, window: WindowInfo) -> Rectangle:
        """获取窗口边界"""
        self._ensure_window_manager_loaded()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._window_manager_instance, 'get_window_bounds') and 
                self._window_manager_instance != self):
                return self._window_manager_instance.get_window_bounds(window)
            
            # 使用备用实现
            return self._get_window_bounds_fallback(window)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'get_window_bounds', 'window': window.title})
            return Rectangle(0, 0, 0, 0)
    
    def _get_window_bounds_fallback(self, window: WindowInfo) -> Rectangle:
        """备用获取窗口边界实现"""
        if not hasattr(self, '_win32gui'):
            return window.bounds
        
        try:
            hwnd = window.handle
            if hwnd:
                rect = self._win32gui.GetWindowRect(hwnd)
                return Rectangle(
                    x=rect[0], y=rect[1],
                    width=rect[2] - rect[0],
                    height=rect[3] - rect[1]
                )
        
        except Exception as e:
            self._handle_error(e, {'operation': '_get_window_bounds_fallback'})
        
        return window.bounds
    
    def set_window_position(self, window: WindowInfo, position: Point) -> bool:
        """设置窗口位置"""
        self._ensure_window_manager_loaded()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._window_manager_instance, 'set_window_position') and 
                self._window_manager_instance != self):
                return self._window_manager_instance.set_window_position(window, position)
            
            # 使用备用实现
            return self._set_window_position_fallback(window, position)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'set_window_position', 'window': window.title})
            return False
    
    def _set_window_position_fallback(self, window: WindowInfo, position: Point) -> bool:
        """备用设置窗口位置实现"""
        if not hasattr(self, '_win32gui'):
            return False
        
        try:
            hwnd = window.handle
            if hwnd:
                bounds = self.get_window_bounds(window)
                self._win32gui.SetWindowPos(
                    hwnd, 0, position.x, position.y, 
                    bounds.width, bounds.height, 0
                )
                self._log_info(f"窗口位置已设置: {window.title} -> ({position.x}, {position.y})")
                return True
        
        except Exception as e:
            self._handle_error(e, {'operation': '_set_window_position_fallback'})
        
        return False
    
    def set_window_size(self, window: WindowInfo, width: int, height: int) -> bool:
        """设置窗口大小"""
        self._ensure_window_manager_loaded()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._window_manager_instance, 'set_window_size') and 
                self._window_manager_instance != self):
                return self._window_manager_instance.set_window_size(window, width, height)
            
            # 使用备用实现
            return self._set_window_size_fallback(window, width, height)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'set_window_size', 'window': window.title})
            return False
    
    def _set_window_size_fallback(self, window: WindowInfo, width: int, height: int) -> bool:
        """备用设置窗口大小实现"""
        if not hasattr(self, '_win32gui'):
            return False
        
        try:
            hwnd = window.handle
            if hwnd:
                bounds = self.get_window_bounds(window)
                self._win32gui.SetWindowPos(
                    hwnd, 0, bounds.x, bounds.y, width, height, 0
                )
                self._log_info(f"窗口大小已设置: {window.title} -> {width}x{height}")
                return True
        
        except Exception as e:
            self._handle_error(e, {'operation': '_set_window_size_fallback'})
        
        return False
    
    def is_window_visible(self, window: WindowInfo) -> bool:
        """检查窗口是否可见"""
        self._ensure_window_manager_loaded()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._window_manager_instance, 'is_window_visible') and 
                self._window_manager_instance != self):
                return self._window_manager_instance.is_window_visible(window)
            
            # 使用备用实现
            return self._is_window_visible_fallback(window)
        
        except Exception as e:
            self._handle_error(e, {'operation': 'is_window_visible', 'window': window.title})
            return False
    
    def _is_window_visible_fallback(self, window: WindowInfo) -> bool:
        """备用检查窗口可见性实现"""
        if not hasattr(self, '_win32gui'):
            return window.is_visible
        
        try:
            hwnd = window.handle
            if hwnd:
                return self._win32gui.IsWindowVisible(hwnd)
        
        except Exception as e:
            self._handle_error(e, {'operation': '_is_window_visible_fallback'})
        
        return window.is_visible
    
    def capture_window(self, window: WindowInfo) -> Optional[bytes]:
        """捕获窗口截图"""
        self._ensure_window_manager_loaded()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._window_manager_instance, 'capture_window') and 
                self._window_manager_instance != self):
                return self._window_manager_instance.capture_window(window)
            
            # 这里需要图像处理服务的支持，暂时返回None
            self._log_warning("窗口截图功能需要图像处理服务支持")
            return None
        
        except Exception as e:
            self._handle_error(e, {'operation': 'capture_window', 'window': window.title})
            return None
    
    def clear_cache(self) -> None:
        """清除窗口缓存"""
        self._cached_windows.clear()
        self._last_cache_update = 0
        self._log_info("窗口缓存已清除")
    
    def get_active_window(self) -> Optional[WindowInfo]:
        """获取当前活动窗口"""
        self._ensure_window_manager_loaded()
        
        try:
            # 如果有现有的方法，使用它
            if (hasattr(self._window_manager_instance, 'get_active_window') and 
                self._window_manager_instance != self):
                result = self._window_manager_instance.get_active_window()
                if result:
                    return self._convert_to_window_info(result)
            
            # 使用备用实现
            return self._get_active_window_fallback()
        
        except Exception as e:
            self._handle_error(e, {'operation': 'get_active_window'})
            return None
    
    def _get_active_window_fallback(self) -> Optional[WindowInfo]:
        """备用获取活动窗口实现"""
        if not hasattr(self, '_win32gui'):
            return None
        
        try:
            hwnd = self._win32gui.GetForegroundWindow()
            if hwnd:
                title = self._win32gui.GetWindowText(hwnd)
                class_name = self._win32gui.GetClassName(hwnd)
                rect = self._win32gui.GetWindowRect(hwnd)
                
                return WindowInfo(
                    handle=hwnd,
                    title=title,
                    class_name=class_name,
                    bounds=Rectangle(
                        x=rect[0], y=rect[1],
                        width=rect[2] - rect[0],
                        height=rect[3] - rect[1]
                    ),
                    is_visible=self._win32gui.IsWindowVisible(hwnd),
                    is_minimized=self._win32gui.IsIconic(hwnd),
                    process_id=0
                )
        
        except Exception as e:
            self._handle_error(e, {'operation': '_get_active_window_fallback'})
        
        return None