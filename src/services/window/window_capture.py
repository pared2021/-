"""
窗口捕获服务
负责窗口画面的捕获和处理
"""
from typing import Optional, Callable, Tuple
import win32gui
import win32ui
import win32con
import numpy as np
from PIL import Image
import cv2
from core.error_handler import ErrorHandler, ErrorCode, ErrorContext

class WindowCapture:
    """窗口捕获器"""
    
    def __init__(self, error_handler: ErrorHandler):
        """初始化
        
        Args:
            error_handler: 错误处理器
        """
        self.error_handler = error_handler
        self.capture_timer = None
        self.capture_callback = None
        self.is_capturing = False
        
    def capture_window(self, hwnd: int) -> Optional[np.ndarray]:
        """捕获窗口画面
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            Optional[np.ndarray]: 捕获的画面
        """
        try:
            # 获取窗口大小
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            # 创建设备上下文
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # 创建位图对象
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # 复制窗口内容到位图
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
            
            # 转换为numpy数组
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype=np.uint8)
            img.shape = (height, width, 4)
            
            # 转换为BGR格式
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # 清理资源
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            
            return img
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.CAPTURE_ERROR,
                "捕获窗口画面失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="WindowCapture.capture_window"
                )
            )
            return None
            
    def start_capture(self, hwnd: int, callback: Callable[[np.ndarray], None], 
                     interval: int = 100) -> bool:
        """开始持续捕获
        
        Args:
            hwnd: 窗口句柄
            callback: 回调函数
            interval: 捕获间隔(毫秒)
            
        Returns:
            bool: 是否成功
        """
        try:
            if self.is_capturing:
                return False
                
            self.capture_callback = callback
            self.is_capturing = True
            
            def capture():
                if not self.is_capturing:
                    return
                    
                frame = self.capture_window(hwnd)
                if frame is not None and self.capture_callback:
                    self.capture_callback(frame)
                    
            self.capture_timer = QTimer()
            self.capture_timer.timeout.connect(capture)
            self.capture_timer.start(interval)
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.CAPTURE_ERROR,
                "开始捕获失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="WindowCapture.start_capture"
                )
            )
            return False
            
    def stop_capture(self) -> None:
        """停止捕获"""
        self.is_capturing = False
        if self.capture_timer:
            self.capture_timer.stop()
            self.capture_timer = None
        self.capture_callback = None
        
    def get_window_region(self, hwnd: int) -> Optional[Tuple[int, int, int, int]]:
        """获取窗口区域
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            Optional[Tuple[int, int, int, int]]: 窗口区域 (left, top, right, bottom)
        """
        try:
            return win32gui.GetWindowRect(hwnd)
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.CAPTURE_ERROR,
                "获取窗口区域失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="WindowCapture.get_window_region"
                )
            )
            return None 