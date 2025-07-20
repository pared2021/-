"""遗留窗口适配器

这个模块提供了一个适配器，用于将现有的GUI代码
平滑迁移到新的统一窗口管理器系统。
"""

import logging
from typing import List, Optional, Tuple, Any, Dict

from ...core.interfaces.window_manager import IWindowManager
from ...core.domain.window_models import WindowInfo, WindowRect
from ...infrastructure.window_manager.window_manager_factory import get_default_window_manager


class LegacyWindowAdapter:
    """遗留窗口适配器
    
    这个适配器提供了与旧版本窗口管理代码兼容的接口，
    同时在底层使用新的统一窗口管理器。
    
    主要用途：
    1. 为现有GUI代码提供向后兼容的接口
    2. 逐步迁移现有代码到新架构
    3. 减少重构过程中的风险
    """
    
    def __init__(self, window_manager: IWindowManager = None):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._window_manager = window_manager or get_default_window_manager()
        self._initialized = False
    
    def _ensure_initialized(self) -> None:
        """确保窗口管理器已初始化"""
        if not self._initialized:
            try:
                if not self._window_manager.is_initialized():
                    self._window_manager.initialize()
                self._initialized = True
            except Exception as e:
                self._logger.error(f"Failed to initialize window manager: {e}")
                raise
    
    # === 兼容旧版本 WindowAdapter 接口 ===
    
    def get_window_list(self) -> List[Tuple[int, str]]:
        """获取窗口列表（旧格式）
        
        返回格式：[(handle, title), ...]
        这是为了兼容现有GUI代码的期望格式
        """
        self._ensure_initialized()
        
        try:
            snapshot = self._window_manager.get_all_windows(include_hidden=False)
            return snapshot.to_legacy_format()
        except Exception as e:
            self._logger.error(f"Failed to get window list: {e}")
            return []
    
    def get_window_info(self, handle: int) -> Optional[Dict[str, Any]]:
        """获取窗口信息（旧格式）
        
        返回格式：兼容services.window_manager.WindowInfo的字典格式
        """
        self._ensure_initialized()
        
        try:
            window_info = self._window_manager.get_window_by_handle(handle)
            if window_info:
                return window_info.to_service_window_info()
            return None
        except Exception as e:
            self._logger.error(f"Failed to get window info for {handle}: {e}")
            return None
    
    def find_window(self, title: str) -> Optional[int]:
        """查找窗口（旧接口）
        
        返回第一个匹配的窗口句柄
        """
        self._ensure_initialized()
        
        try:
            windows = self._window_manager.find_windows_by_title(title, exact_match=False)
            return windows[0].handle if windows else None
        except Exception as e:
            self._logger.error(f"Failed to find window '{title}': {e}")
            return None
    
    def activate_window(self, handle: int) -> bool:
        """激活窗口"""
        self._ensure_initialized()
        
        try:
            return self._window_manager.activate_window(handle)
        except Exception as e:
            self._logger.error(f"Failed to activate window {handle}: {e}")
            return False
    
    def capture_window(self, handle: int, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[bytes]:
        """捕获窗口（旧接口）
        
        Args:
            handle: 窗口句柄
            region: 捕获区域 (x, y, width, height)
        """
        self._ensure_initialized()
        
        try:
            window_rect = None
            if region:
                window_rect = WindowRect.from_tuple(region)
            
            return self._window_manager.capture_window(handle, window_rect)
        except Exception as e:
            self._logger.error(f"Failed to capture window {handle}: {e}")
            return None
    
    def resize_window(self, handle: int, width: int, height: int) -> bool:
        """调整窗口大小"""
        self._ensure_initialized()
        
        try:
            return self._window_manager.resize_window(handle, width, height)
        except Exception as e:
            self._logger.error(f"Failed to resize window {handle}: {e}")
            return False
    
    def move_window(self, handle: int, x: int, y: int) -> bool:
        """移动窗口"""
        self._ensure_initialized()
        
        try:
            return self._window_manager.move_window(handle, x, y)
        except Exception as e:
            self._logger.error(f"Failed to move window {handle}: {e}")
            return False
    
    def close_window(self, handle: int) -> bool:
        """关闭窗口"""
        self._ensure_initialized()
        
        try:
            return self._window_manager.close_window(handle)
        except Exception as e:
            self._logger.error(f"Failed to close window {handle}: {e}")
            return False
    
    def get_window_rect(self, handle: int) -> Optional[Tuple[int, int, int, int]]:
        """获取窗口矩形（旧格式）
        
        返回格式：(x, y, width, height)
        """
        self._ensure_initialized()
        
        try:
            rect = self._window_manager.get_window_rect(handle)
            return rect.to_tuple()
        except Exception as e:
            self._logger.error(f"Failed to get window rect {handle}: {e}")
            return None
    
    def is_window_visible(self, handle: int) -> bool:
        """检查窗口是否可见"""
        self._ensure_initialized()
        
        try:
            return self._window_manager.is_window_visible(handle)
        except Exception as e:
            self._logger.error(f"Failed to check window visibility {handle}: {e}")
            return False
    
    # === 兼容旧版本 WindowManagerServiceAdapter 接口 ===
    
    def find_game_window(self, title: str = None) -> Optional[Dict[str, Any]]:
        """查找游戏窗口（旧接口）
        
        返回格式：兼容IWindowManagerService的字典格式
        """
        self._ensure_initialized()
        
        try:
            if title:
                windows = self._window_manager.find_windows_by_title(title)
                game_windows = [w for w in windows if w.is_game_window()]
            else:
                game_windows = self._window_manager.find_game_windows()
            
            if game_windows:
                window = game_windows[0]
                return {
                    'handle': window.handle,
                    'title': window.title,
                    'class_name': window.class_name,
                    'rect': window.rect.to_win32_rect(),  # (left, top, right, bottom)
                    'is_visible': window.is_visible,
                    'is_active': window.is_active
                }
            
            return None
        except Exception as e:
            self._logger.error(f"Failed to find game window: {e}")
            return None
    
    def get_all_windows(self) -> List[Dict[str, Any]]:
        """获取所有窗口（服务接口格式）
        
        返回格式：兼容IWindowManagerService的字典列表
        """
        self._ensure_initialized()
        
        try:
            snapshot = self._window_manager.get_all_windows(include_hidden=False)
            result = []
            
            for window in snapshot.windows:
                result.append({
                    'handle': window.handle,
                    'title': window.title,
                    'class_name': window.class_name,
                    'rect': window.rect.to_win32_rect(),
                    'is_visible': window.is_visible,
                    'is_active': window.is_active,
                    'process_id': window.process_id
                })
            
            return result
        except Exception as e:
            self._logger.error(f"Failed to get all windows: {e}")
            return []
    
    # === 兼容旧版本 GameWindowManager 接口 ===
    
    def update_window_list(self) -> None:
        """更新窗口列表（旧接口）"""
        self._ensure_initialized()
        
        try:
            self._window_manager.refresh_window_list()
        except Exception as e:
            self._logger.error(f"Failed to update window list: {e}")
    
    def setup_window_hook(self) -> None:
        """设置窗口钩子（旧接口）
        
        在新架构中，这对应于启动窗口监控
        """
        self._ensure_initialized()
        
        try:
            self._window_manager.start_monitoring()
        except Exception as e:
            self._logger.error(f"Failed to setup window hook: {e}")
    
    def on_window_created(self, hwnd: int) -> None:
        """窗口创建事件处理（旧接口）
        
        在新架构中，这通过事件系统处理
        """
        # 在新架构中，这个方法不需要直接调用
        # 事件会通过统一的事件系统处理
        pass
    
    def on_window_destroyed(self, hwnd: int) -> None:
        """窗口销毁事件处理（旧接口）
        
        在新架构中，这通过事件系统处理
        """
        # 在新架构中，这个方法不需要直接调用
        # 事件会通过统一的事件系统处理
        pass
    
    # === 新增的便捷方法 ===
    
    def get_unified_window_info(self, handle: int) -> Optional[WindowInfo]:
        """获取统一格式的窗口信息
        
        这个方法返回新的WindowInfo对象，
        建议新代码使用这个方法
        """
        self._ensure_initialized()
        
        try:
            return self._window_manager.get_window_by_handle(handle)
        except Exception as e:
            self._logger.error(f"Failed to get unified window info {handle}: {e}")
            return None
    
    def get_unified_window_list(self) -> List[WindowInfo]:
        """获取统一格式的窗口列表
        
        这个方法返回新的WindowInfo对象列表，
        建议新代码使用这个方法
        """
        self._ensure_initialized()
        
        try:
            snapshot = self._window_manager.get_all_windows(include_hidden=False)
            return list(snapshot.windows)
        except Exception as e:
            self._logger.error(f"Failed to get unified window list: {e}")
            return []
    
    def find_windows_by_title_unified(self, title: str, exact_match: bool = False) -> List[WindowInfo]:
        """根据标题查找窗口（统一格式）
        
        建议新代码使用这个方法
        """
        self._ensure_initialized()
        
        try:
            return self._window_manager.find_windows_by_title(title, exact_match)
        except Exception as e:
            self._logger.error(f"Failed to find windows by title '{title}': {e}")
            return []
    
    def get_window_manager(self) -> IWindowManager:
        """获取底层的窗口管理器实例
        
        用于需要直接访问新接口的代码
        """
        self._ensure_initialized()
        return self._window_manager
    
    # === 生命周期管理 ===
    
    def shutdown(self) -> None:
        """关闭适配器"""
        try:
            if self._window_manager and self._window_manager.is_initialized():
                self._window_manager.shutdown()
            self._initialized = False
        except Exception as e:
            self._logger.error(f"Error during shutdown: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        self._ensure_initialized()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.shutdown()


# === 全局实例和便捷函数 ===

_global_adapter: Optional[LegacyWindowAdapter] = None


def get_legacy_window_adapter() -> LegacyWindowAdapter:
    """获取全局遗留窗口适配器实例"""
    global _global_adapter
    if _global_adapter is None:
        _global_adapter = LegacyWindowAdapter()
    return _global_adapter


def shutdown_legacy_adapter() -> None:
    """关闭全局遗留窗口适配器"""
    global _global_adapter
    if _global_adapter:
        _global_adapter.shutdown()
        _global_adapter = None


# === 向后兼容的便捷函数 ===

def get_window_list() -> List[Tuple[int, str]]:
    """便捷函数：获取窗口列表（旧格式）"""
    adapter = get_legacy_window_adapter()
    return adapter.get_window_list()


def find_window(title: str) -> Optional[int]:
    """便捷函数：查找窗口"""
    adapter = get_legacy_window_adapter()
    return adapter.find_window(title)


def get_window_info(handle: int) -> Optional[Dict[str, Any]]:
    """便捷函数：获取窗口信息（旧格式）"""
    adapter = get_legacy_window_adapter()
    return adapter.get_window_info(handle)


def activate_window(handle: int) -> bool:
    """便捷函数：激活窗口"""
    adapter = get_legacy_window_adapter()
    return adapter.activate_window(handle)