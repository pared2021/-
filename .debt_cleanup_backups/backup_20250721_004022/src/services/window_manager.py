import win32gui
import win32ui
import win32con
import win32api
import ctypes
from ctypes import wintypes
import numpy as np
import cv2
import time
import threading
import win32process
from typing import Optional, Tuple, Dict, List, Callable, Any
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from .config import Config
from .logger import GameLogger
from .exceptions import WindowNotFoundError
from .capture_engines import GameCaptureEngine, TargetInfo
from src.common.error_types import ErrorCode, WindowError, ErrorContext
from src.services.error_handler import ErrorHandler

# 定义回调函数类型
WINEVENTPROC = ctypes.WINFUNCTYPE(
    None,
    wintypes.HANDLE,   # hWinEventHook
    wintypes.DWORD,    # event
    wintypes.HWND,     # hwnd
    wintypes.LONG,     # idObject
    wintypes.LONG,     # idChild
    wintypes.DWORD,    # dwEventThread
    wintypes.DWORD,    # dwmsEventTime
)

@dataclass
class WindowRegion:
    """窗口区域类"""
    x: int
    y: int
    width: int
    height: int
    name: str = ""
    category: str = ""

@dataclass
class WindowInfo:
    """窗口信息"""
    hwnd: int
    title: str
    class_name: str
    rect: Tuple[int, int, int, int]
    is_visible: bool
    is_enabled: bool

class GameWindowManager(QObject):
    """游戏窗口管理类"""
    
    # 定义信号
    window_changed = pyqtSignal(list)  # 窗口列表变化信号
    window_selected = pyqtSignal(str)  # 窗口选择信号
    region_added = pyqtSignal(str)  # 区域添加信号
    region_removed = pyqtSignal(str)  # 区域移除信号
    screenshot_updated = pyqtSignal(object)  # 截图更新信号
    
    def __init__(self, logger: GameLogger, config: Config, error_handler: ErrorHandler):
        """
        初始化窗口管理器
        
        Args:
            logger: 日志对象
            config: 配置对象
            error_handler: 错误处理对象
        """
        super().__init__()
        self.logger = logger
        self.config = config
        self.error_handler = error_handler
        
        # 窗口变量
        self.window_handle = None
        self.window_title = ""
        self.window_rect = (0, 0, 0, 0)
        self.process_id = None
        self.is_fullscreen = False
        
        # 初始化多引擎捕获系统
        self.capture_engine = GameCaptureEngine(logger)
        
        # 截图相关变量
        self.screenshot_thread = None
        self.is_capturing = False
        self.screenshot = None
        
        # 钩子相关变量
        self.hook = None
        self.hook_thread = None
        
        # 监控的窗口类名和标题（使用统一配置系统）
        window_config = config.get_window_config()
        self.target_class = window_config.get('window_class', '')
        self.target_title = window_config.get('window_title', '')
        
        # 初始化回调函数列表
        self.window_callbacks = []
        
        # 初始化区域字典
        self.regions = {}
        self.last_window_state = None
        
        # 初始化窗口缓存
        self.windows_cache = []
        
        self.logger.info("窗口管理器初始化完成")
        
        # 初始化窗口列表
        self.update_window_list()
        
        # 设置窗口消息钩子
        self.setup_window_hook()

    def update_window_list(self):
        """更新窗口列表"""
        windows = []
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    windows.append((hwnd, title))
            return True
        
        win32gui.EnumWindows(callback, windows)
        self.windows_cache = windows

    def setup_window_hook(self):
        """设置窗口消息钩子"""
        @WINEVENTPROC
        def win_event_callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
            # 只处理窗口事件
            if idObject != 0 or idChild != 0:
                return
            
            # 处理窗口创建和销毁事件
            if event == win32con.EVENT_OBJECT_CREATE:
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        self.on_window_created(hwnd, title)
            elif event == win32con.EVENT_OBJECT_DESTROY:
                self.on_window_destroyed(hwnd)
        
        # 保持回调函数的引用
        self.hook_callback = win_event_callback
        
        # 注册窗口事件钩子
        self.hook = ctypes.windll.user32.SetWinEventHook(
            win32con.EVENT_OBJECT_CREATE,  # 窗口创建事件
            win32con.EVENT_OBJECT_DESTROY,  # 窗口销毁事件
            0,  # 当前进程
            self.hook_callback,  # 回调函数
            0,  # 进程ID（0表示所有进程）
            0,  # 线程ID（0表示所有线程）
            win32con.WINEVENT_OUTOFCONTEXT | win32con.WINEVENT_SKIPOWNPROCESS  # 钩子标志
        )
        
        if self.hook == 0:
            self.logger.error("设置窗口钩子失败")
        else:
            self.logger.info("成功设置窗口钩子")

    def on_window_created(self, hwnd: int, title: str):
        """窗口创建事件处理"""
        self.logger.info(f"新窗口创建: {title}")
        self.windows_cache.append((hwnd, title))
        self.notify_window_changed()

    def on_window_destroyed(self, hwnd: int):
        """窗口销毁事件处理"""
        # 从缓存中移除窗口
        self.windows_cache = [(h, t) for h, t in self.windows_cache if h != hwnd]
        
        # 如果当前选择的窗口被销毁，重置选择
        if self.window_handle == hwnd:
            self.window_handle = None
            self.window_rect = None
            self.logger.warning("当前选择的窗口已被销毁")
        
        self.notify_window_changed()

    def register_window_callback(self, callback: Callable[[List[Tuple[int, str]]], None]):
        """
        注册窗口变化回调函数
        
        Args:
            callback: 回调函数，接收窗口列表作为参数
        """
        self.window_callbacks.append(callback)

    def notify_window_changed(self):
        """通知所有回调函数窗口列表已变化"""
        # 发送信号
        self.window_changed.emit(self.windows_cache)
        
        # 调用回调函数
        for callback in self.window_callbacks:
            try:
                callback(self.windows_cache)
            except Exception as e:
                self.logger.error(f"执行窗口变化回调失败: {e}")

    def get_all_windows(self) -> List[Tuple[int, str]]:
        """
        获取所有可见窗口列表
        
        Returns:
            List[Tuple[int, str]]: 窗口句柄和标题的列表
        """
        return self.windows_cache

    def find_window(self, specific_hwnd=None) -> bool:
        """
        查找游戏窗口
        
        Args:
            specific_hwnd: 可选的指定窗口句柄，如果提供则直接使用该句柄
            
        Returns:
            bool: 是否找到窗口
        """
        try:
            if specific_hwnd:
                # 使用指定的窗口句柄
                if win32gui.IsWindow(specific_hwnd):
                    title = win32gui.GetWindowText(specific_hwnd)
                    self.logger.info(f"使用指定窗口句柄: {specific_hwnd}, 标题: {title}")
                    self._update_window_info(specific_hwnd, title)
                    return True
                else:
                    self.logger.warning(f"指定的窗口句柄无效: {specific_hwnd}")
                    return False
            
            # 根据配置的标题查找窗口
            if self.target_title:
                self.logger.info(f"查找标题为 '{self.target_title}' 的窗口")
                windows = []
                
                def callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if self.target_title.lower() in title.lower():
                            windows.append((hwnd, title))
                    return True
                
                win32gui.EnumWindows(callback, windows)
                
                if windows:
                    # 找到匹配的窗口
                    hwnd, title = windows[0]
                    self.logger.info(f"找到窗口: {title}, 句柄: {hwnd}")
                    self._update_window_info(hwnd, title)
                    return True
                else:
                    self.logger.warning(f"未找到标题包含 '{self.target_title}' 的窗口")
                    return False
            
            # 如果没有指定标题，则使用之前缓存的窗口信息
            if self.window_handle and win32gui.IsWindow(self.window_handle):
                title = win32gui.GetWindowText(self.window_handle)
                if title:
                    self.logger.info(f"使用缓存的窗口句柄: {self.window_handle}, 标题: {title}")
                    self._update_window_info(self.window_handle, title)
                    return True
            
            self.logger.warning("未找到目标窗口")
            return False
            
        except Exception as e:
            self.logger.error(f"查找窗口时发生错误: {e}")
            return False
            
    def _update_window_info(self, hwnd: int, title: str):
        """更新窗口信息"""
        try:
            # 更新窗口句柄和标题
            self.window_handle = hwnd
            self.window_title = title
            
            # 获取窗口区域
            self.window_rect = win32gui.GetWindowRect(hwnd)
            
            # 获取进程ID
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            self.process_id = process_id
            
            # 检查是否是全屏窗口
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            left, top, right, bottom = self.window_rect
            width = right - left
            height = bottom - top
            
            # 如果窗口覆盖了整个屏幕，假定为全屏模式
            self.is_fullscreen = (width >= screen_width * 0.95 and height >= screen_height * 0.95)
            
            # 通知窗口选择
            self._emit_window_selected(hwnd, title)
            
        except Exception as e:
            self.logger.error(f"更新窗口信息时发生错误: {e}")

    def start_region_selection(self):
        """开始区域选择"""
        self.is_selecting_region = True
        self.selection_start = None
        self.selection_end = None
        self.logger.info("开始区域选择")
        
    def update_region_selection(self, x: int, y: int):
        """更新区域选择"""
        if not self.is_selecting_region:
            return
            
        if self.selection_start is None:
            self.selection_start = (x, y)
        self.selection_end = (x, y)
        
        # 发送截图更新信号
        if self.window_handle:
            screenshot = self.get_screenshot()
            if screenshot is not None:
                # 在截图上绘制选择框
                if self.selection_start and self.selection_end:
                    x1, y1 = self.selection_start
                    x2, y2 = self.selection_end
                    cv2.rectangle(screenshot, (x1, y1), (x2, y2), (0, 255, 0), 2)
                self.screenshot_updated.emit(screenshot)
                
    def end_region_selection(self) -> Optional[Tuple[int, int, int, int]]:
        """结束区域选择"""
        if not self.is_selecting_region or not self.selection_start or not self.selection_end:
            return None
            
        self.is_selecting_region = False
        
        # 计算区域坐标
        x1, y1 = self.selection_start
        x2, y2 = self.selection_end
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        # 重置选择状态
        self.selection_start = None
        self.selection_end = None
        
        return (x, y, width, height)
        
    def get_screenshot(self) -> Optional[np.ndarray]:
        """
        获取最新的窗口截图
        
        Returns:
            Optional[np.ndarray]: 窗口截图数组，如果没有截图则返回None
        """
        try:
            if self.screenshot is None:
                # 尝试捕获窗口
                screenshot = self.capture_window()
                
                # capture_window内部已经进行了验证，这里只需简单检查
                if screenshot is not None:
                    self.screenshot = screenshot
                    self.notify_screenshot_updated(screenshot)
                
            return self.screenshot
        except Exception as e:
            self.logger.error(f"获取截图失败: {e}")
            return None
    
    def get_window_info(self, hwnd: int) -> Optional[WindowInfo]:
        """获取窗口信息
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            Optional[WindowInfo]: 窗口信息
        """
        try:
            if not win32gui.IsWindow(hwnd):
                return None
                
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            rect = win32gui.GetWindowRect(hwnd)
            is_visible = win32gui.IsWindowVisible(hwnd)
            is_enabled = win32gui.IsWindowEnabled(hwnd)
            
            return WindowInfo(
                hwnd=hwnd,
                title=title,
                class_name=class_name,
                rect=rect,
                is_visible=is_visible,
                is_enabled=is_enabled
            )
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.WINDOW_ERROR,
                WindowError("获取窗口信息失败"),
                ErrorContext(
                    error_info=str(e),
                    error_location="WindowManager.get_window_info",
                    window_handle=hwnd
                )
            )
            return None
            
    def is_window_active(self) -> bool:
        """
        检查窗口是否激活
        
        Returns:
            bool: 窗口是否激活
        """
        try:
            if not self.window_handle:
                # 降级为调试级别，避免日志污染
                self.logger.debug("无法检查窗口状态: 窗口未找到")
                return False
            
            # 检查窗口是否存在
            if not win32gui.IsWindow(self.window_handle):
                self.logger.warning("无法检查窗口状态: 窗口不存在")
                self.window_handle = None
                return False
            
            # 检查窗口是否可见
            if not win32gui.IsWindowVisible(self.window_handle):
                self.logger.warning("无法检查窗口状态: 窗口不可见")
                return False
            
            # 检查窗口是否最小化
            placement = win32gui.GetWindowPlacement(self.window_handle)
            if placement[1] == win32con.SW_SHOWMINIMIZED:
                self.logger.warning("无法检查窗口状态: 窗口已最小化")
                return False
            
            # 检查窗口是否在前台
            foreground_window = win32gui.GetForegroundWindow()
            is_active = foreground_window == self.window_handle
            
            if not is_active:
                # 降级为调试级别，避免日志污染
                self.logger.debug("游戏窗口未激活")
                # 尝试激活窗口
                try:
                    win32gui.SetForegroundWindow(self.window_handle)
                    time.sleep(0.1)  # 等待窗口激活
                    is_active = win32gui.GetForegroundWindow() == self.window_handle
                except Exception as e:
                    self.logger.error(f"激活窗口失败: {e}")
            
            return is_active
            
        except Exception as e:
            self.logger.error(f"检查窗口状态失败: {e}")
            return False
    
    def set_foreground(self) -> bool:
        """
        将窗口设置为前台
        
        Returns:
            bool: 是否成功
        """
        if not self.window_handle:
            self.logger.warning("无法激活窗口: 窗口未找到")
            return False
        
        # 尝试不同的方法激活窗口
        try:
            self.logger.debug("开始激活窗口")
            
            # 方法1：使用SetForegroundWindow
            win32gui.SetForegroundWindow(self.window_handle)
            
            # 方法2：使用ShowWindow
            win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
            
            # 方法3：使用SetWindowPos
            win32gui.SetWindowPos(self.window_handle, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            win32gui.SetWindowPos(self.window_handle, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            
            # 等待窗口激活
            window_config = self.config.get_window_config()
            activation_delay = window_config.get('activation_delay', 0.5)
            time.sleep(activation_delay)
            
            self.logger.info("窗口激活成功")
            return True
        except Exception as e:
            self.logger.error(f"窗口激活失败: {e}")
            return False
    
    def add_region(self, name: str, x: int, y: int, width: int, height: int, category: str = "") -> bool:
        """
        添加一个需要监控的窗口区域
        
        Args:
            name: 区域名称
            x: 区域左上角x坐标（相对于窗口）
            y: 区域左上角y坐标（相对于窗口）
            width: 区域宽度
            height: 区域高度
            category: 区域类别
            
        Returns:
            bool: 是否添加成功
        """
        if not self.window_handle:
            self.logger.error("无法添加区域：窗口未找到")
            return False
            
        if name in self.regions:
            self.logger.warning(f"区域 {name} 已存在，将被覆盖")
            
        # 确保区域在窗口内
        window_width = self.window_rect[2] - self.window_rect[0]
        window_height = self.window_rect[3] - self.window_rect[1]
        
        if x < 0 or y < 0 or x + width > window_width or y + height > window_height:
            self.logger.error("区域超出窗口范围")
            return False
            
        self.regions[name] = WindowRegion(x, y, width, height, name, category)
        self.logger.info(f"添加区域成功: {name}, 位置=({x}, {y}), 大小={width}x{height}")
        self.notify_region_added(name)
        return True
        
    def remove_region(self, name: str) -> bool:
        """
        移除一个监控区域
        
        Args:
            name: 区域名称
            
        Returns:
            bool: 是否移除成功
        """
        if name in self.regions:
            del self.regions[name]
            self.logger.info(f"移除区域: {name}")
            self.notify_region_removed(name)
            return True
        self.logger.warning(f"区域不存在: {name}")
        return False
        
    def get_region_screenshot(self, region_name: str) -> Optional[np.ndarray]:
        """
        获取指定区域的截图
        
        Args:
            region_name: 区域名称
            
        Returns:
            Optional[np.ndarray]: 区域截图，如果失败则返回None
        """
        if region_name not in self.regions:
            self.logger.error(f"区域不存在: {region_name}")
            return None
            
        full_screenshot = self.get_screenshot()
        if full_screenshot is None:
            return None
            
        region = self.regions[region_name]
        try:
            region_img = full_screenshot[region.y:region.y+region.height, 
                                      region.x:region.x+region.width]
            self.logger.debug(f"获取区域 {region_name} 的截图成功")
            self.notify_screenshot_updated(region_img)
            return region_img
        except Exception as e:
            self.logger.error(f"获取区域截图失败: {e}")
            return None
            
    def get_window_state(self) -> Dict:
        """
        获取窗口当前状态
        
        Returns:
            Dict: 窗口状态信息
        """
        if not self.window_handle:
            self.logger.warning("无法获取窗口状态：窗口未找到")
            return {}
            
        try:
            placement = win32gui.GetWindowPlacement(self.window_handle)
            is_minimized = placement[1] == win32con.SW_SHOWMINIMIZED
            is_maximized = placement[1] == win32con.SW_SHOWMAXIMIZED
            rect = win32gui.GetWindowRect(self.window_handle)
            
            state = {
                'minimized': is_minimized,
                'maximized': is_maximized,
                'position': rect,
                'size': (rect[2] - rect[0], rect[3] - rect[1]),
                'active': self.is_window_active()
            }
            
            # 检查状态变化
            if self.last_window_state is not None:
                for key, value in state.items():
                    if self.last_window_state.get(key) != value:
                        self.logger.info(f"窗口状态变化: {key} = {value}")
            
            self.last_window_state = state
            return state
        except Exception as e:
            self.logger.error(f"获取窗口状态失败: {e}")
            return {}
            
    def wait_for_window_state(self, target_state: Dict, timeout: float = 5.0) -> bool:
        """
        等待窗口达到指定状态
        
        Args:
            target_state: 目标状态
            timeout: 超时时间（秒）
            
        Returns:
            bool: 是否达到目标状态
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_state = self.get_window_state()
            matches = all(current_state.get(k) == v for k, v in target_state.items())
            
            if matches:
                self.logger.info("窗口达到目标状态")
                return True
                
            time.sleep(0.1)
            
        self.logger.warning("等待窗口状态超时")
        return False

    def notify_region_added(self, name: str):
        """通知区域添加"""
        self.region_added.emit(name)
        
    def notify_region_removed(self, name: str):
        """通知区域移除"""
        self.region_removed.emit(name)
        
    def notify_screenshot_updated(self, screenshot: np.ndarray):
        """通知截图更新"""
        self.screenshot_updated.emit(screenshot)

    def set_target_window(self, hwnd: int, title: str):
        """设置目标窗口
        
        Args:
            hwnd: 窗口句柄
            title: 窗口标题
        """
        # 检查窗口是否有效
        if not win32gui.IsWindow(hwnd):
            self.logger.error(f"无效的窗口句柄: {hwnd}")
            return
            
        # 检查是否与当前窗口相同，避免不必要的操作
        if self.window_handle == hwnd:
            return
            
        # 直接更新窗口信息，不进行额外处理
        self.window_handle = hwnd
        self.window_title = title
        self.window_rect = win32gui.GetWindowRect(hwnd)
        
        # 不使用日志记录，直接使用print输出信息，避免日志系统的递归
        print(f"已设置目标窗口: {title}")
        
        # 延迟发送信号，避免在事件循环中引起递归
        QTimer.singleShot(0, lambda: self._emit_window_selected(hwnd, title))
    
    def _emit_window_selected(self, hwnd, title):
        """安全发送窗口选择信号"""
        try:
            self.window_selected.emit(title)
        except Exception as e:
            print(f"发送窗口选择信号失败: {e}")

    def cleanup(self):
        """清理资源"""
        try:
            # 停止捕获
            if self.is_capturing:
                self.stop_capture()
            
            # 清理钩子
            if self.hook:
                ctypes.windll.user32.UnhookWinEvent(self.hook)
                self.hook = None
            
            # 清理新的捕获引擎
            if hasattr(self, 'capture_engine'):
                self.capture_engine.cleanup()
                
            self.logger.info("窗口管理器资源已清理")
        except Exception as e:
            self.logger.error(f"清理窗口管理器资源时发生错误: {e}")

    def __del__(self):
        """析构函数，确保资源被释放"""
        self.cleanup()
        self.hook_callback = None

    def capture_window(self) -> Optional[np.ndarray]:
        """
        捕获窗口截图 - 使用多引擎架构
        
        Returns:
            Optional[np.ndarray]: 窗口截图数组，如果失败则返回None
        """
        try:
            self.logger.debug("开始捕获窗口画面...")
            
            # 检查窗口句柄
            if not self.window_handle:
                self.logger.warning("窗口句柄为空，尝试重新查找窗口")
                # 重试查找窗口，使用缓存的窗口标题
                if self.window_title:
                    self.logger.info(f"尝试使用缓存的窗口标题重新查找: {self.window_title}")
                    self.target_title = self.window_title
                
                # 调用find_window
                if not self.find_window():
                    self.logger.error("无法找到目标窗口，窗口可能已关闭或无法访问")
                    return None
            
            # 验证窗口状态
            if not win32gui.IsWindow(self.window_handle):
                self.logger.warning("窗口句柄无效，窗口可能已被关闭")
                self.window_handle = None
                # 记录当前标题以便后续恢复
                if hasattr(self, 'window_title') and self.window_title:
                    self.target_title = self.window_title
                # 触发窗口更改事件
                self.notify_window_changed()
                return None
            
            # 尝试激活窗口
            if not win32gui.IsWindowVisible(self.window_handle) or win32gui.IsIconic(self.window_handle):
                self.logger.warning("目标窗口不可见或已最小化，尝试激活窗口")
                # 尝试激活窗口
                self.set_foreground()
                time.sleep(0.2)
            
            # 获取窗口位置和大小
            try:
                self.window_rect = win32gui.GetWindowRect(self.window_handle)
            except Exception as e:
                self.logger.error(f"获取窗口位置和大小失败: {e}")
                if not win32gui.IsWindow(self.window_handle):
                    self.window_handle = None
                    self.notify_window_changed()
                return None
            
            # 准备目标信息
            target_info = TargetInfo(
                hwnd=self.window_handle,
                title=self.window_title,
                process_id=self.process_id,
                window_rect=self.window_rect,
                is_fullscreen=self.is_fullscreen
            )
            
            # 使用捕获引擎捕获窗口
            frame = self.capture_engine.capture(target_info)
            
            # 验证捕获结果
            validated_frame = self._validate_capture_result(frame)
            if validated_frame is None:
                self.logger.error("所有捕获引擎都失败了或返回无效数据")
                return None
            
            # 存储截图
            self.screenshot = validated_frame.copy()
            
            # 通知截图更新
            self.notify_screenshot_updated(validated_frame)
            
            return validated_frame
                
        except Exception as e:
            self.logger.error(f"捕获窗口画面失败: {e}")
            return None
    
    def _validate_capture_result(self, frame: Any) -> Optional[np.ndarray]:
        """验证捕获结果的数据类型和有效性
        
        Args:
            frame: 捕获引擎返回的数据
            
        Returns:
            Optional[np.ndarray]: 验证后的图像数组，如果无效则返回None
        """
        try:
            # 检查是否为None
            if frame is None:
                self.logger.debug("捕获结果为None")
                return None
            
            # 检查是否为布尔值（错误返回）
            if isinstance(frame, bool):
                self.logger.warning(f"捕获引擎返回布尔值: {frame}")
                return None
            
            # 检查是否为numpy数组
            if not isinstance(frame, np.ndarray):
                self.logger.warning(f"捕获结果类型错误: {type(frame)}, 期望np.ndarray")
                return None
            
            # 检查数组维度
            if frame.ndim not in [2, 3]:
                self.logger.warning(f"图像数组维度错误: {frame.ndim}, 期望2或3维")
                return None
            
            # 检查数组大小
            if frame.size == 0:
                self.logger.warning("图像数组为空")
                return None
            
            # 检查图像尺寸合理性
            if frame.shape[0] < 10 or frame.shape[1] < 10:
                self.logger.warning(f"图像尺寸过小: {frame.shape}")
                return None
            
            # 如果是3维数组，检查通道数
            if frame.ndim == 3 and frame.shape[2] not in [1, 3, 4]:
                self.logger.warning(f"图像通道数错误: {frame.shape[2]}, 期望1、3或4")
                return None
            
            return frame
            
        except Exception as e:
            self.logger.error(f"验证捕获结果时发生错误: {e}")
            return None
    
    def start_capture(self):
        """开始持续捕获窗口画面"""
        if self.is_capturing:
            return
        
        # 检查窗口是否存在
        if not self.window_handle:
            self.logger.warning("无法开始截图：窗口未找到")
            return
            
        # 确认窗口有效
        if not win32gui.IsWindow(self.window_handle):
            self.logger.warning("无法开始截图：窗口不存在")
            self.window_handle = None
            return
            
        self.is_capturing = True
        self.screenshot_thread = threading.Thread(target=self._capture_loop)
        self.screenshot_thread.daemon = True
        self.screenshot_thread.start()
        
    def stop_capture(self):
        """停止持续捕获窗口画面"""
        self.is_capturing = False
        if self.screenshot_thread:
            self.screenshot_thread.join()
            self.screenshot_thread = None
            
    def _capture_loop(self):
        """截图循环"""
        while self.is_capturing:
            screenshot = self.capture_window()
            if screenshot is not None:
                self.screenshot = screenshot
                self.notify_screenshot_updated(screenshot)
            time.sleep(1.0 / 30)  # 限制帧率为30fps 

    # === 兼容zzz/utils/window_manager.py的静态方法 ===
    
    @staticmethod
    def find_window_by_title(title: str) -> Optional[int]:
        """查找指定标题的窗口 - 兼容zzz/utils版本
        
        Args:
            title: 窗口标题
            
        Returns:
            Optional[int]: 窗口句柄
        """
        return win32gui.FindWindow(None, title)
    
    @staticmethod
    def get_window_rect_static(hwnd: int) -> Tuple[int, int, int, int]:
        """获取窗口位置和大小 - 兼容zzz/utils版本
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            Tuple[int, int, int, int]: (左, 上, 右, 下)
        """
        return win32gui.GetWindowRect(hwnd)
    
    @staticmethod
    def activate_window_static(hwnd: int):
        """激活窗口 - 兼容zzz/utils版本
        
        Args:
            hwnd: 窗口句柄
        """
        if win32gui.IsIconic(hwnd):  # 如果窗口最小化
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
    
    @staticmethod
    def get_window_state_info(hwnd: int) -> Dict:
        """获取窗口状态 - 兼容zzz/utils版本
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            Dict: 窗口状态信息
        """
        rect = win32gui.GetWindowRect(hwnd)
        return {
            "position": {"x": rect[0], "y": rect[1]},
            "size": {"width": rect[2] - rect[0], "height": rect[3] - rect[1]},
            "active": hwnd == win32gui.GetForegroundWindow(),
            "minimized": win32gui.IsIconic(hwnd),
            "maximized": win32gui.IsZoomed(hwnd),
        }
    
    def capture_window_legacy(self, hwnd: int) -> Optional[np.ndarray]:
        """捕获窗口截图 - 兼容zzz/utils版本
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            Optional[np.ndarray]: 窗口截图数据
        """
        try:
            # 获取窗口大小
            left, top, right, bottom = self.get_window_rect_static(hwnd)
            width = right - left
            height = bottom - top

            # 创建设备上下文
            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            # 创建位图对象
            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(save_bitmap)

            # 复制屏幕到位图
            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

            # 获取位图信息
            bmp_info = save_bitmap.GetInfo()
            bmp_str = save_bitmap.GetBitmapBits(True)

            # 转换为numpy数组
            img = np.frombuffer(bmp_str, dtype="uint8")
            img.shape = (height, width, 4)  # RGBA格式

            # 清理资源
            win32gui.DeleteObject(save_bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)

            return img

        except Exception as e:
            self.logger.error(f"截图失败: {e}")
            return None
            
    def find_windows_by_pattern(self, title_pattern: Optional[str] = None, 
                               class_pattern: Optional[str] = None) -> List[WindowInfo]:
        """查找窗口 - 兼容window子目录版本
        
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
                return True
                
            win32gui.EnumWindows(callback, None)
            return windows
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.WINDOW_ERROR,
                WindowError("查找窗口失败"),
                ErrorContext(
                    error_info=str(e),
                    error_location="WindowManager.find_windows_by_pattern"
                )
            )
            return []
    
    def set_window_pos_static(self, hwnd: int, x: int, y: int, 
                             width: int, height: int) -> bool:
        """设置窗口位置和大小 - 兼容window子目录版本
        
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
                WindowError("设置窗口位置失败"),
                ErrorContext(
                    error_info=str(e),
                    error_location="WindowManager.set_window_pos_static",
                    window_handle=hwnd
                )
            )
            return False
    
    def set_window_foreground_static(self, hwnd: int) -> bool:
        """将窗口置于前台 - 兼容window子目录版本
        
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
                WindowError("设置窗口前台失败"),
                ErrorContext(
                    error_info=str(e),
                    error_location="WindowManager.set_window_foreground_static",
                    window_handle=hwnd
                )
            )
            return False
    
    def is_window_valid_static(self, hwnd: int) -> bool:
        """检查窗口是否有效 - 兼容window子目录版本
        
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
                WindowError("检查窗口有效性失败"),
                ErrorContext(
                    error_info=str(e),
                    error_location="WindowManager.is_window_valid_static",
                    window_handle=hwnd
                )
            )
            return False