"""
窗口管理工具
"""
import win32gui
import win32con
import win32ui
import numpy as np
from typing import Optional, Tuple, Dict


class WindowManager:
    @staticmethod
    def find_window(title: str) -> Optional[int]:
        """
        查找指定标题的窗口

        Args:
            title: 窗口标题

        Returns:
            Optional[int]: 窗口句柄
        """
        return win32gui.FindWindow(None, title)

    @staticmethod
    def get_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
        """
        获取窗口位置和大小

        Args:
            hwnd: 窗口句柄

        Returns:
            Tuple[int, int, int, int]: (左, 上, 右, 下)
        """
        return win32gui.GetWindowRect(hwnd)

    @staticmethod
    def activate_window(hwnd: int):
        """
        激活窗口

        Args:
            hwnd: 窗口句柄
        """
        if win32gui.IsIconic(hwnd):  # 如果窗口最小化
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)

    @staticmethod
    def get_window_state(hwnd: int) -> Dict:
        """
        获取窗口状态

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

    def capture_window(self, hwnd: int) -> Optional[np.ndarray]:
        """
        捕获窗口截图

        Args:
            hwnd: 窗口句柄

        Returns:
            Optional[np.ndarray]: 窗口截图数据
        """
        try:
            # 获取窗口大小
            left, top, right, bottom = self.get_window_rect(hwnd)
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
            print(f"截图失败: {e}")
            return None
