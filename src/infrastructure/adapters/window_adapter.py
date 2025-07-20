"""
窗口适配器实现

整合现有的GameWindowManager，提供Clean Architecture接口
"""
from typing import Optional, List, Tuple
import numpy as np
import logging
from dependency_injector.wiring import inject, Provide

from ...core.interfaces.adapters import IWindowAdapter, WindowInfo
from ...core.interfaces.repositories import IConfigRepository
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...application.containers.main_container import MainContainer

# 导入现有的窗口管理器实现
from ...services.window_manager import GameWindowManager, WindowInfo as ServiceWindowInfo
from ...services.config import Config
from ...services.logger import GameLogger
from ...services.error_handler import ErrorHandler


class WindowAdapter(IWindowAdapter):
    """
    窗口适配器实现
    
    封装现有的GameWindowManager，提供统一的窗口操作接口
    """
    
    @inject
    def __init__(self, config_repository: IConfigRepository = Provide['config_repository']):
        self._config_repository = config_repository
        self._logger = logging.getLogger(__name__)
        self._window_manager = None
        self._initialized = False
    
    def _ensure_initialized(self) -> bool:
        """确保窗口管理器已初始化"""
        if not self._initialized:
            try:
                # 获取配置实例
                config_instance = self._config_repository.get_config_instance()
                if config_instance is None:
                    config_instance = Config()
                
                # 创建日志实例
                logger = GameLogger(config_instance, "WindowAdapter")
                
                # 创建错误处理器
                error_handler = ErrorHandler(logger)
                
                # 创建窗口管理器实例
                self._window_manager = GameWindowManager(logger, config_instance, error_handler)
                
                self._initialized = True
                return True
                
            except Exception as e:
                self._logger.error(f"Failed to initialize window manager: {str(e)}")
                return False
        return True
    
    def find_window(self, title: str, class_name: Optional[str] = None) -> Optional[WindowInfo]:
        """查找窗口"""
        if not self._ensure_initialized():
            return None
        
        try:
            # 使用现有的窗口查找功能
            windows = self._window_manager.find_windows_by_pattern(
                title_pattern=title,
                class_pattern=class_name
            )
            
            if windows:
                # 转换为标准WindowInfo格式
                service_window = windows[0]
                return self._convert_window_info(service_window)
            
            return None
            
        except Exception as e:
            self._logger.error(f"Failed to find window: {str(e)}")
            return None
    
    def get_window_list(self) -> List[WindowInfo]:
        """获取窗口列表"""
        if not self._ensure_initialized():
            return []
        
        try:
            # 获取所有窗口
            windows = self._window_manager.get_all_windows()
            
            # 转换为WindowInfo列表
            window_list = []
            for hwnd, title in windows:
                try:
                    service_window = self._window_manager.get_window_info(hwnd)
                    if service_window:
                        window_info = self._convert_window_info(service_window)
                        window_list.append(window_info)
                except Exception as e:
                    self._logger.warning(f"Failed to get info for window {hwnd}: {str(e)}")
                    continue
            
            return window_list
            
        except Exception as e:
            self._logger.error(f"Failed to get window list: {str(e)}")
            return []
    
    def get_window_info(self, hwnd: int) -> Optional[WindowInfo]:
        """根据窗口句柄获取窗口信息"""
        if not self._ensure_initialized():
            return None
        
        try:
            service_window = self._window_manager.get_window_info(hwnd)
            if service_window:
                return self._convert_window_info(service_window)
            return None
            
        except Exception as e:
            self._logger.error(f"Failed to get window info for {hwnd}: {str(e)}")
            return None
    
    def capture_window(self, window_info: WindowInfo) -> Optional[np.ndarray]:
        """捕获窗口截图"""
        if not self._ensure_initialized():
            return None
        
        try:
            # 设置目标窗口
            self._window_manager.set_target_window(window_info.handle, window_info.title)
            
            # 查找并激活窗口
            if self._window_manager.find_window(window_info.handle):
                # 捕获窗口
                screenshot = self._window_manager.capture_window()
                return screenshot
            
            return None
            
        except Exception as e:
            self._logger.error(f"Failed to capture window: {str(e)}")
            return None
    
    def activate_window(self, window_info: WindowInfo) -> bool:
        """激活窗口"""
        if not self._ensure_initialized():
            return False
        
        try:
            # 设置目标窗口
            self._window_manager.set_target_window(window_info.handle, window_info.title)
            
            # 激活窗口
            return self._window_manager.set_foreground()
            
        except Exception as e:
            self._logger.error(f"Failed to activate window: {str(e)}")
            return False
    
    def resize_window(self, window_info: WindowInfo, width: int, height: int) -> bool:
        """调整窗口大小"""
        if not self._ensure_initialized():
            return False
        
        try:
            # 获取当前窗口位置
            x, y, _, _ = window_info.rect
            
            # 调整窗口大小
            return self._window_manager.set_window_pos_static(
                window_info.handle, x, y, width, height
            )
            
        except Exception as e:
            self._logger.error(f"Failed to resize window: {str(e)}")
            return False
    
    def move_window(self, window_info: WindowInfo, x: int, y: int) -> bool:
        """移动窗口"""
        if not self._ensure_initialized():
            return False
        
        try:
            # 获取当前窗口大小
            _, _, width, height = window_info.rect
            actual_width = width - window_info.rect[0]
            actual_height = height - window_info.rect[1]
            
            # 移动窗口
            return self._window_manager.set_window_pos_static(
                window_info.handle, x, y, actual_width, actual_height
            )
            
        except Exception as e:
            self._logger.error(f"Failed to move window: {str(e)}")
            return False
    
    def close_window(self, window_info: WindowInfo) -> bool:
        """关闭窗口"""
        try:
            import win32gui
            import win32con
            
            # 发送关闭消息
            win32gui.PostMessage(window_info.handle, win32con.WM_CLOSE, 0, 0)
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to close window: {str(e)}")
            return False
    
    def get_window_rect(self, window_info: WindowInfo) -> Tuple[int, int, int, int]:
        """获取窗口位置和大小"""
        try:
            if self._ensure_initialized():
                # 使用窗口管理器获取实时位置
                rect = self._window_manager.get_window_rect_static(window_info.handle)
                return rect
            else:
                # 使用窗口信息中的缓存位置
                return window_info.rect
                
        except Exception as e:
            self._logger.error(f"Failed to get window rect: {str(e)}")
            return window_info.rect
    
    def is_window_visible(self, window_info: WindowInfo) -> bool:
        """检查窗口是否可见"""
        try:
            if self._ensure_initialized():
                return self._window_manager.is_window_valid_static(window_info.handle)
            else:
                return window_info.is_visible
                
        except Exception as e:
            self._logger.error(f"Failed to check window visibility: {str(e)}")
            return False
    
    def _convert_window_info(self, service_window: ServiceWindowInfo) -> WindowInfo:
        """转换窗口信息格式"""
        return WindowInfo(
            title=service_window.title,
            handle=service_window.hwnd,
            pid=0,  # ServiceWindowInfo没有pid字段，需要单独获取
            rect=service_window.rect,
            is_visible=service_window.is_visible,
            is_active=service_window.is_enabled  # 使用enabled状态作为active的近似
        )
    
    def get_window_manager_instance(self) -> Optional[GameWindowManager]:
        """获取底层窗口管理器实例（用于兼容性）"""
        self._ensure_initialized()
        return self._window_manager
    
    def add_window_region(self, name: str, x: int, y: int, width: int, height: int, category: str = "") -> bool:
        """添加窗口区域（扩展功能）"""
        if not self._ensure_initialized():
            return False
        
        try:
            return self._window_manager.add_region(name, x, y, width, height, category)
        except Exception as e:
            self._logger.error(f"Failed to add window region: {str(e)}")
            return False
    
    def remove_window_region(self, name: str) -> bool:
        """移除窗口区域（扩展功能）"""
        if not self._ensure_initialized():
            return False
        
        try:
            return self._window_manager.remove_region(name)
        except Exception as e:
            self._logger.error(f"Failed to remove window region: {str(e)}")
            return False
    
    def get_region_screenshot(self, region_name: str) -> Optional[np.ndarray]:
        """获取区域截图（扩展功能）"""
        if not self._ensure_initialized():
            return None
        
        try:
            return self._window_manager.get_region_screenshot(region_name)
        except Exception as e:
            self._logger.error(f"Failed to get region screenshot: {str(e)}")
            return None