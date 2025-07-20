"""统一窗口管理器实现

这个模块实现了统一的窗口管理器，
整合了现有的所有窗口管理功能。
"""

import logging
import threading
import time
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field

from ...core.interfaces.window_manager import (
    IWindowManager, IWindowEventHandler, WindowEventType,
    WindowManagerError, WindowNotFoundError, WindowOperationError
)
from ...core.domain.window_models import WindowInfo, WindowListSnapshot, WindowRect
from ...services.window_manager import GameWindowManager
from ...infrastructure.adapters.window_adapter import WindowAdapter


@dataclass
class WindowManagerConfig:
    """窗口管理器配置"""
    enable_monitoring: bool = True
    cache_timeout: float = 1.0  # 缓存超时时间（秒）
    max_cache_size: int = 1000
    auto_refresh_interval: float = 5.0  # 自动刷新间隔（秒）
    enable_auto_refresh: bool = False
    log_level: str = "INFO"
    capture_engine: str = "auto"  # auto, gdi, dxgi
    

class UnifiedWindowManager(IWindowManager):
    """统一窗口管理器实现
    
    这个类整合了现有的GameWindowManager和WindowAdapter，
    提供统一的窗口管理接口。
    """
    
    def __init__(self, config: WindowManagerConfig = None):
        self._config = config or WindowManagerConfig()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(getattr(logging, self._config.log_level))
        
        # 核心组件
        self._game_window_manager: Optional[GameWindowManager] = None
        self._window_adapter: Optional[WindowAdapter] = None
        
        # 状态管理
        self._initialized = False
        self._monitoring = False
        self._shutdown_requested = False
        
        # 缓存管理
        self._window_cache: Dict[int, WindowInfo] = {}
        self._window_list_cache: Optional[WindowListSnapshot] = None
        self._cache_timestamp = 0.0
        self._cache_lock = threading.RLock()
        
        # 事件处理
        self._event_handlers: List[IWindowEventHandler] = []
        self._event_lock = threading.RLock()
        
        # 监控线程
        self._monitor_thread: Optional[threading.Thread] = None
        self._auto_refresh_thread: Optional[threading.Thread] = None
    
    def initialize(self) -> None:
        """初始化窗口管理器"""
        if self._initialized:
            return
        
        try:
            self._logger.info("Initializing unified window manager...")
            
            # 初始化核心组件
            self._game_window_manager = GameWindowManager()
            self._window_adapter = WindowAdapter()
            
            # 确保适配器初始化
            self._window_adapter._ensure_initialized()
            
            # 初始化窗口列表
            self.refresh_window_list()
            
            # 启动自动刷新
            if self._config.enable_auto_refresh:
                self._start_auto_refresh()
            
            # 启动监控
            if self._config.enable_monitoring:
                self.start_monitoring()
            
            self._initialized = True
            self._logger.info("Unified window manager initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize window manager: {e}")
            raise WindowManagerError(f"Initialization failed: {e}")
    
    def shutdown(self) -> None:
        """关闭窗口管理器"""
        if not self._initialized:
            return
        
        try:
            self._logger.info("Shutting down unified window manager...")
            self._shutdown_requested = True
            
            # 停止监控
            self.stop_monitoring()
            
            # 停止自动刷新
            self._stop_auto_refresh()
            
            # 清理缓存
            self.clear_cache()
            
            # 清理事件处理器
            with self._event_lock:
                self._event_handlers.clear()
            
            self._initialized = False
            self._logger.info("Unified window manager shut down successfully")
            
        except Exception as e:
            self._logger.error(f"Error during shutdown: {e}")
            raise WindowManagerError(f"Shutdown failed: {e}")
    
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized
    
    def _ensure_initialized(self) -> None:
        """确保已初始化"""
        if not self._initialized:
            self.initialize()
    
    def get_all_windows(self, include_hidden: bool = False) -> WindowListSnapshot:
        """获取所有窗口列表"""
        self._ensure_initialized()
        
        try:
            # 检查缓存
            if self._is_cache_valid():
                cached_snapshot = self._window_list_cache
                if cached_snapshot and (include_hidden or 
                    all(w.is_visible for w in cached_snapshot.windows)):
                    return cached_snapshot
            
            # 获取新的窗口列表
            window_list = self._window_adapter.get_window_list()
            
            # 转换为统一格式
            unified_windows = []
            for window_data in window_list:
                if isinstance(window_data, tuple) and len(window_data) == 2:
                    # 旧格式 (handle, title)
                    handle, title = window_data
                    window_info = self._get_window_info_from_handle(handle)
                    if window_info:
                        unified_windows.append(window_info)
                else:
                    # 新格式，直接转换
                    window_info = WindowInfo.from_service_window_info(window_data)
                    unified_windows.append(window_info)
            
            # 过滤隐藏窗口
            if not include_hidden:
                unified_windows = [w for w in unified_windows if w.is_visible]
            
            # 创建快照并缓存
            snapshot = WindowListSnapshot(unified_windows)
            self._update_cache(snapshot)
            
            return snapshot
            
        except Exception as e:
            self._logger.error(f"Failed to get window list: {e}")
            raise WindowManagerError(f"Failed to get window list: {e}")
    
    def get_window_by_handle(self, handle: int) -> Optional[WindowInfo]:
        """根据句柄获取窗口信息"""
        self._ensure_initialized()
        
        try:
            # 检查缓存
            with self._cache_lock:
                if handle in self._window_cache and self._is_cache_valid():
                    return self._window_cache[handle]
            
            # 从适配器获取
            window_info = self._get_window_info_from_handle(handle)
            
            # 更新缓存
            if window_info:
                with self._cache_lock:
                    self._window_cache[handle] = window_info
            
            return window_info
            
        except Exception as e:
            self._logger.error(f"Failed to get window {handle}: {e}")
            raise WindowManagerError(f"Failed to get window {handle}: {e}")
    
    def _get_window_info_from_handle(self, handle: int) -> Optional[WindowInfo]:
        """从句柄获取窗口信息的内部方法"""
        try:
            # 尝试使用适配器的get_window_info方法
            if hasattr(self._window_adapter, 'get_window_info'):
                service_info = self._window_adapter.get_window_info(handle)
                if service_info:
                    return WindowInfo.from_service_window_info(service_info)
            
            # 回退到从窗口列表中查找
            window_list = self._window_adapter.get_window_list()
            for window_data in window_list:
                if isinstance(window_data, tuple) and len(window_data) == 2:
                    window_handle, title = window_data
                    if window_handle == handle:
                        # 创建基本的WindowInfo
                        return WindowInfo(
                            handle=handle,
                            title=title,
                            class_name="",
                            rect=WindowRect(0, 0, 0, 0)
                        )
                else:
                    # 对象格式
                    if hasattr(window_data, 'hwnd') and window_data.hwnd == handle:
                        return WindowInfo.from_service_window_info(window_data)
                    elif hasattr(window_data, 'handle') and window_data.handle == handle:
                        return WindowInfo.from_service_window_info(window_data)
            
            return None
            
        except Exception as e:
            self._logger.error(f"Error getting window info for handle {handle}: {e}")
            return None
    
    def find_windows_by_title(self, title: str, exact_match: bool = False) -> List[WindowInfo]:
        """根据标题查找窗口"""
        self._ensure_initialized()
        
        try:
            snapshot = self.get_all_windows(include_hidden=True)
            return snapshot.get_windows_by_title(title, exact_match)
            
        except Exception as e:
            self._logger.error(f"Failed to find windows by title '{title}': {e}")
            raise WindowManagerError(f"Failed to find windows by title '{title}': {e}")
    
    def find_windows_by_class(self, class_name: str) -> List[WindowInfo]:
        """根据类名查找窗口"""
        self._ensure_initialized()
        
        try:
            snapshot = self.get_all_windows(include_hidden=True)
            return [w for w in snapshot.windows if w.class_name == class_name]
            
        except Exception as e:
            self._logger.error(f"Failed to find windows by class '{class_name}': {e}")
            raise WindowManagerError(f"Failed to find windows by class '{class_name}': {e}")
    
    def find_windows_by_process(self, process_id: int = None, process_name: str = None) -> List[WindowInfo]:
        """根据进程查找窗口"""
        self._ensure_initialized()
        
        try:
            snapshot = self.get_all_windows(include_hidden=True)
            result = []
            
            for window in snapshot.windows:
                if process_id is not None and window.process_id == process_id:
                    result.append(window)
                elif process_name is not None and window.process_name == process_name:
                    result.append(window)
            
            return result
            
        except Exception as e:
            self._logger.error(f"Failed to find windows by process: {e}")
            raise WindowManagerError(f"Failed to find windows by process: {e}")
    
    def find_game_windows(self) -> List[WindowInfo]:
        """查找游戏窗口"""
        self._ensure_initialized()
        
        try:
            snapshot = self.get_all_windows(include_hidden=False)
            return snapshot.get_game_windows()
            
        except Exception as e:
            self._logger.error(f"Failed to find game windows: {e}")
            raise WindowManagerError(f"Failed to find game windows: {e}")
    
    def activate_window(self, handle: int) -> bool:
        """激活窗口"""
        self._ensure_initialized()
        
        try:
            if not self.get_window_by_handle(handle):
                raise WindowNotFoundError(handle)
            
            result = self._window_adapter.activate_window(handle)
            
            if result:
                self._emit_event(WindowEventType.ACTIVATED, handle)
            
            return result
            
        except WindowNotFoundError:
            raise
        except Exception as e:
            self._logger.error(f"Failed to activate window {handle}: {e}")
            raise WindowOperationError("activate", handle, str(e))
    
    def move_window(self, handle: int, x: int, y: int) -> bool:
        """移动窗口"""
        self._ensure_initialized()
        
        try:
            if not self.get_window_by_handle(handle):
                raise WindowNotFoundError(handle)
            
            result = self._window_adapter.move_window(handle, x, y)
            
            if result:
                self._emit_event(WindowEventType.MOVED, handle, x=x, y=y)
                self._invalidate_window_cache(handle)
            
            return result
            
        except WindowNotFoundError:
            raise
        except Exception as e:
            self._logger.error(f"Failed to move window {handle}: {e}")
            raise WindowOperationError("move", handle, str(e))
    
    def resize_window(self, handle: int, width: int, height: int) -> bool:
        """调整窗口大小"""
        self._ensure_initialized()
        
        try:
            if not self.get_window_by_handle(handle):
                raise WindowNotFoundError(handle)
            
            result = self._window_adapter.resize_window(handle, width, height)
            
            if result:
                self._emit_event(WindowEventType.RESIZED, handle, width=width, height=height)
                self._invalidate_window_cache(handle)
            
            return result
            
        except WindowNotFoundError:
            raise
        except Exception as e:
            self._logger.error(f"Failed to resize window {handle}: {e}")
            raise WindowOperationError("resize", handle, str(e))
    
    def set_window_rect(self, handle: int, rect: WindowRect) -> bool:
        """设置窗口矩形区域"""
        self._ensure_initialized()
        
        try:
            if not self.get_window_by_handle(handle):
                raise WindowNotFoundError(handle)
            
            # 先移动再调整大小
            move_result = self.move_window(handle, rect.x, rect.y)
            resize_result = self.resize_window(handle, rect.width, rect.height)
            
            return move_result and resize_result
            
        except (WindowNotFoundError, WindowOperationError):
            raise
        except Exception as e:
            self._logger.error(f"Failed to set window rect {handle}: {e}")
            raise WindowOperationError("set_rect", handle, str(e))
    
    def close_window(self, handle: int, force: bool = False) -> bool:
        """关闭窗口"""
        self._ensure_initialized()
        
        try:
            if not self.get_window_by_handle(handle):
                raise WindowNotFoundError(handle)
            
            # 使用适配器的关闭方法
            if hasattr(self._window_adapter, 'close_window'):
                result = self._window_adapter.close_window(handle)
            else:
                # 回退到基本实现
                import win32gui
                if force:
                    result = win32gui.DestroyWindow(handle)
                else:
                    result = win32gui.PostMessage(handle, 0x0010, 0, 0)  # WM_CLOSE
            
            if result:
                self._emit_event(WindowEventType.DESTROYED, handle)
                self._invalidate_window_cache(handle)
            
            return result
            
        except WindowNotFoundError:
            raise
        except Exception as e:
            self._logger.error(f"Failed to close window {handle}: {e}")
            raise WindowOperationError("close", handle, str(e))
    
    def minimize_window(self, handle: int) -> bool:
        """最小化窗口"""
        return self._change_window_state(handle, "minimize")
    
    def maximize_window(self, handle: int) -> bool:
        """最大化窗口"""
        return self._change_window_state(handle, "maximize")
    
    def restore_window(self, handle: int) -> bool:
        """恢复窗口"""
        return self._change_window_state(handle, "restore")
    
    def _change_window_state(self, handle: int, operation: str) -> bool:
        """改变窗口状态的通用方法"""
        self._ensure_initialized()
        
        try:
            if not self.get_window_by_handle(handle):
                raise WindowNotFoundError(handle)
            
            import win32gui
            import win32con
            
            state_map = {
                "minimize": win32con.SW_MINIMIZE,
                "maximize": win32con.SW_MAXIMIZE,
                "restore": win32con.SW_RESTORE
            }
            
            if operation not in state_map:
                raise ValueError(f"Unknown operation: {operation}")
            
            result = win32gui.ShowWindow(handle, state_map[operation])
            
            if result:
                self._emit_event(WindowEventType.STATE_CHANGED, handle, operation=operation)
                self._invalidate_window_cache(handle)
            
            return result
            
        except WindowNotFoundError:
            raise
        except Exception as e:
            self._logger.error(f"Failed to {operation} window {handle}: {e}")
            raise WindowOperationError(operation, handle, str(e))
    
    def is_window_visible(self, handle: int) -> bool:
        """检查窗口是否可见"""
        self._ensure_initialized()
        
        try:
            window_info = self.get_window_by_handle(handle)
            if not window_info:
                raise WindowNotFoundError(handle)
            
            return window_info.is_visible
            
        except WindowNotFoundError:
            raise
        except Exception as e:
            self._logger.error(f"Failed to check visibility of window {handle}: {e}")
            return False
    
    def is_window_active(self, handle: int) -> bool:
        """检查窗口是否激活"""
        self._ensure_initialized()
        
        try:
            window_info = self.get_window_by_handle(handle)
            if not window_info:
                raise WindowNotFoundError(handle)
            
            return window_info.is_active
            
        except WindowNotFoundError:
            raise
        except Exception as e:
            self._logger.error(f"Failed to check active state of window {handle}: {e}")
            return False
    
    def get_window_rect(self, handle: int) -> WindowRect:
        """获取窗口矩形区域"""
        self._ensure_initialized()
        
        try:
            window_info = self.get_window_by_handle(handle)
            if not window_info:
                raise WindowNotFoundError(handle)
            
            return window_info.rect
            
        except WindowNotFoundError:
            raise
        except Exception as e:
            self._logger.error(f"Failed to get rect of window {handle}: {e}")
            raise WindowOperationError("get_rect", handle, str(e))
    
    def capture_window(self, handle: int, region: Optional[WindowRect] = None) -> Optional[bytes]:
        """捕获窗口截图"""
        self._ensure_initialized()
        
        try:
            if not self.get_window_by_handle(handle):
                raise WindowNotFoundError(handle)
            
            # 使用适配器的捕获方法
            if region:
                result = self._window_adapter.capture_window(handle, region.to_tuple())
            else:
                result = self._window_adapter.capture_window(handle)
            
            return result
            
        except WindowNotFoundError:
            raise
        except Exception as e:
            self._logger.error(f"Failed to capture window {handle}: {e}")
            raise WindowOperationError("capture", handle, str(e))
    
    def add_event_handler(self, handler: IWindowEventHandler) -> None:
        """添加事件处理器"""
        with self._event_lock:
            if handler not in self._event_handlers:
                self._event_handlers.append(handler)
    
    def remove_event_handler(self, handler: IWindowEventHandler) -> None:
        """移除事件处理器"""
        with self._event_lock:
            if handler in self._event_handlers:
                self._event_handlers.remove(handler)
    
    def start_monitoring(self) -> None:
        """开始监控窗口事件"""
        if self._monitoring:
            return
        
        try:
            self._monitoring = True
            self._monitor_thread = threading.Thread(
                target=self._monitor_windows,
                name="WindowMonitor",
                daemon=True
            )
            self._monitor_thread.start()
            self._logger.info("Window monitoring started")
            
        except Exception as e:
            self._monitoring = False
            self._logger.error(f"Failed to start monitoring: {e}")
            raise WindowManagerError(f"Failed to start monitoring: {e}")
    
    def stop_monitoring(self) -> None:
        """停止监控窗口事件"""
        if not self._monitoring:
            return
        
        try:
            self._monitoring = False
            
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=5.0)
            
            self._logger.info("Window monitoring stopped")
            
        except Exception as e:
            self._logger.error(f"Error stopping monitoring: {e}")
            raise WindowManagerError(f"Failed to stop monitoring: {e}")
    
    def _monitor_windows(self) -> None:
        """窗口监控线程"""
        self._logger.info("Window monitoring thread started")
        
        try:
            while self._monitoring and not self._shutdown_requested:
                try:
                    # 这里可以实现窗口事件监控逻辑
                    # 目前只是定期刷新窗口列表
                    time.sleep(1.0)
                    
                except Exception as e:
                    self._logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(1.0)
        
        except Exception as e:
            self._logger.error(f"Fatal error in monitoring thread: {e}")
        
        finally:
            self._logger.info("Window monitoring thread stopped")
    
    def _start_auto_refresh(self) -> None:
        """启动自动刷新"""
        if self._auto_refresh_thread and self._auto_refresh_thread.is_alive():
            return
        
        self._auto_refresh_thread = threading.Thread(
            target=self._auto_refresh_loop,
            name="WindowAutoRefresh",
            daemon=True
        )
        self._auto_refresh_thread.start()
        self._logger.info("Auto refresh started")
    
    def _stop_auto_refresh(self) -> None:
        """停止自动刷新"""
        if self._auto_refresh_thread and self._auto_refresh_thread.is_alive():
            self._auto_refresh_thread.join(timeout=2.0)
        self._logger.info("Auto refresh stopped")
    
    def _auto_refresh_loop(self) -> None:
        """自动刷新循环"""
        while not self._shutdown_requested and self._config.enable_auto_refresh:
            try:
                time.sleep(self._config.auto_refresh_interval)
                if not self._shutdown_requested:
                    self.refresh_window_list()
            except Exception as e:
                self._logger.error(f"Error in auto refresh: {e}")
    
    def refresh_window_list(self) -> None:
        """刷新窗口列表缓存"""
        try:
            # 清除缓存并重新获取
            with self._cache_lock:
                self._window_list_cache = None
                self._window_cache.clear()
                self._cache_timestamp = 0.0
            
            # 重新获取窗口列表
            self.get_all_windows(include_hidden=True)
            
            self._logger.debug("Window list refreshed")
            
        except Exception as e:
            self._logger.error(f"Failed to refresh window list: {e}")
            raise WindowManagerError(f"Failed to refresh window list: {e}")
    
    def clear_cache(self) -> None:
        """清除所有缓存"""
        with self._cache_lock:
            self._window_cache.clear()
            self._window_list_cache = None
            self._cache_timestamp = 0.0
        
        self._logger.debug("Cache cleared")
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        return (time.time() - self._cache_timestamp) < self._config.cache_timeout
    
    def _update_cache(self, snapshot: WindowListSnapshot) -> None:
        """更新缓存"""
        with self._cache_lock:
            self._window_list_cache = snapshot
            self._cache_timestamp = time.time()
            
            # 更新单个窗口缓存
            for window in snapshot.windows:
                self._window_cache[window.handle] = window
            
            # 限制缓存大小
            if len(self._window_cache) > self._config.max_cache_size:
                # 移除最旧的条目
                sorted_items = sorted(
                    self._window_cache.items(),
                    key=lambda x: x[1].updated_at
                )
                for handle, _ in sorted_items[:len(self._window_cache) - self._config.max_cache_size]:
                    del self._window_cache[handle]
    
    def _invalidate_window_cache(self, handle: int) -> None:
        """使特定窗口的缓存失效"""
        with self._cache_lock:
            if handle in self._window_cache:
                del self._window_cache[handle]
    
    def _emit_event(self, event_type: str, handle: int, **kwargs) -> None:
        """发送窗口事件"""
        try:
            window_info = self.get_window_by_handle(handle)
            if not window_info:
                return
            
            with self._event_lock:
                for handler in self._event_handlers:
                    try:
                        handler.on_window_event(event_type, window_info, **kwargs)
                    except Exception as e:
                        self._logger.error(f"Error in event handler: {e}")
        
        except Exception as e:
            self._logger.error(f"Error emitting event {event_type}: {e}")
    
    def get_configuration(self) -> Dict[str, Any]:
        """获取配置信息"""
        return {
            'enable_monitoring': self._config.enable_monitoring,
            'cache_timeout': self._config.cache_timeout,
            'max_cache_size': self._config.max_cache_size,
            'auto_refresh_interval': self._config.auto_refresh_interval,
            'enable_auto_refresh': self._config.enable_auto_refresh,
            'log_level': self._config.log_level,
            'capture_engine': self._config.capture_engine
        }
    
    def set_configuration(self, config: Dict[str, Any]) -> None:
        """设置配置信息"""
        for key, value in config.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        # 应用日志级别变更
        if 'log_level' in config:
            self._logger.setLevel(getattr(logging, config['log_level']))
    
    def get_status(self) -> Dict[str, Any]:
        """获取管理器状态"""
        with self._cache_lock:
            cache_size = len(self._window_cache)
            cache_valid = self._is_cache_valid()
        
        return {
            'initialized': self._initialized,
            'monitoring': self._monitoring,
            'cache_size': cache_size,
            'cache_valid': cache_valid,
            'event_handlers': len(self._event_handlers),
            'auto_refresh_enabled': self._config.enable_auto_refresh,
            'shutdown_requested': self._shutdown_requested
        }