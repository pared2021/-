"""
屏幕采集器模块
"""
import concurrent.futures
from dataclasses import dataclass
from typing import Optional, Union, List, Callable, Any, Tuple, Dict

import cv2
import numpy as np
import pyautogui
import win32con
import win32gui
import win32ui
from PIL import Image

from ..image_recognition import ImageRecognition


@dataclass
class Resource:
    """资源类，用于管理需要清理的资源"""

    name: str
    cleanup_func: Callable[..., None]
    args: Tuple[Any, ...] = ()
    kwargs: Dict[str, Any] = None

    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}

    def cleanup(self):
        """清理资源"""
        if self.cleanup_func:
            self.cleanup_func(*self.args, **self.kwargs)


class ScreenCollectorError(Exception):
    """屏幕采集相关错误"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ScreenCollector:  # 保持两个空行
    def __init__(self, timeout: float = 5.0) -> None:
        """
        初始化屏幕采集器

        Args:
            timeout: 超时时间，单位秒
        """
        self.timeout = timeout
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.image_recognition = ImageRecognition()
        self.prev_frame: Optional[np.ndarray] = None
        self.window_cache: Dict[int, Tuple[int, int, int, int]] = {}
        self.window_handles: Dict[int, Any] = {}

    def cleanup(self) -> None:
        """清理资源"""
        self._executor.shutdown(wait=False)

    def capture_screen(self, region: Optional[tuple] = None) -> Optional[Image.Image]:
        """
        截取屏幕

        Args:
            region: 截图区域，格式为(left, top, width, height)

        Returns:
            PIL.Image: 截图结果

        Raises:
            TimeoutError: 操作超时时抛出
            ScreenCollectorError: 截图失败时抛出
        """
        try:
            future = self._executor.submit(self._capture_screen_impl, region)
            return future.result(timeout=self.timeout)
        except TimeoutError as exc:
            raise TimeoutError("截图操作超时") from exc
        except Exception as e:
            raise ScreenCollectorError(f"截图失败: {str(e)}") from e

    def _capture_screen_impl(self, region: Optional[tuple] = None) -> Image.Image:
        """截图的具体实现"""
        try:
            image = pyautogui.screenshot(region=region)
            return image
        except Exception as exc:
            raise TimeoutError("截图操作超时") from exc

    def capture_window(self, hwnd: int) -> Optional[Image.Image]:
        """
        截取指定窗口

        Args:
            hwnd: 窗口句柄

        Returns:
            PIL.Image: 截图结果

        Raises:
            TimeoutError: 操作超时时抛出
            ScreenCollectorError: 截图失败时抛出
        """
        try:
            im = self._capture_window_impl(hwnd)
            if im is None:
                raise ScreenCollectorError("Failed to capture window")
            assert isinstance(im, Image.Image), "Capture must return PIL Image"
            return im
        except TimeoutError as exc:
            raise TimeoutError("窗口截图操作超时") from exc
        except Exception as e:
            raise ScreenCollectorError(f"窗口截图失败: {str(e)}") from e

    def _capture_window_impl(self, hwnd: int) -> Image.Image:
        """窗口截图的具体实现"""
        try:
            # 获取窗口大小
            left, top, right, bot = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bot - top

            # 创建设备上下文
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            # 创建位图对象
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            # 复制窗口内容到位图
            result = saveDC.BitBlt(
                (0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY
            )
            if result is None:
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                im = Image.frombuffer(
                    "RGB",
                    (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
                    bmpstr,
                    "raw",
                    "BGRX",
                    0,
                    1,
                )
            else:
                im = None

            # 清理资源
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            return im
        except Exception as exc:
            raise TimeoutError("窗口截图操作超时") from exc

    def find_template(
        self, screen: Image.Image, template: Image.Image, threshold: float = 0.8
    ) -> Optional[tuple]:
        """
        模板匹配

        Args:
            screen: 屏幕截图
            template: 模板图片
            threshold: 匹配阈值

        Returns:
            Tuple[int, int]: 匹配位置的左上角坐标

        Raises:
            TimeoutError: 操作超时时抛出
            ScreenCollectorError: 匹配失败时抛出
        """
        try:
            future = self._executor.submit(
                self._find_template_impl, screen, template, threshold
            )
            return future.result(timeout=self.timeout)
        except TimeoutError as exc:
            raise TimeoutError("模板匹配操作超时") from exc
        except Exception as e:
            raise ScreenCollectorError(f"模板匹配失败: {str(e)}") from e

    def _find_template_impl(
        self, screen: Image.Image, template: Image.Image, threshold: float
    ) -> Optional[tuple]:
        """模板匹配的具体实现"""
        try:
            screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
            template_cv = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2BGR)

            result = cv2.matchTemplate(screen_cv, template_cv, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                return max_loc
            return None
        except Exception as exc:
            raise TimeoutError("模板匹配操作超时") from exc

    def find_text(self, screen: Image.Image) -> Optional[str]:
        """
        文字识别

        Args:
            screen: 屏幕截图

        Returns:
            str: 识别出的文字

        Raises:
            TimeoutError: 操作超时时抛出
            ScreenCollectorError: 识别失败时抛出
        """
        try:
            future = self._executor.submit(self._find_text_impl, screen)
            return future.result(timeout=self.timeout)
        except TimeoutError as exc:
            raise TimeoutError("文字识别操作超时") from exc
        except Exception as e:
            raise ScreenCollectorError(f"文字识别失败: {str(e)}") from e

    def _find_text_impl(self, screen: Image.Image) -> Optional[str]:
        """文字识别的具体实现"""
        try:
            screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
            text = self.image_recognition.extract_text(screen_cv)
            return text
        except Exception as exc:
            raise TimeoutError("文字识别操作超时") from exc

    def find_color(
        self, screen: Image.Image, color: tuple, tolerance: int = 0
    ) -> Optional[tuple]:
        """
        颜色查找

        Args:
            screen: 屏幕截图
            color: 目标颜色，格式为(R,G,B)
            tolerance: 容差值

        Returns:
            Tuple[int, int]: 匹配位置的坐标

        Raises:
            TimeoutError: 操作超时时抛出
            ScreenCollectorError: 查找失败时抛出
        """
        try:
            future = self._executor.submit(
                self._find_color_impl, screen, color, tolerance
            )
            return future.result(timeout=self.timeout)
        except TimeoutError as exc:
            raise TimeoutError("颜色查找操作超时") from exc
        except Exception as e:
            raise ScreenCollectorError(f"颜色查找失败: {str(e)}") from e

    def _find_color_impl(
        self, screen: Image.Image, color: tuple, tolerance: int
    ) -> Optional[tuple]:
        """颜色查找的具体实现"""
        try:
            # 转换为numpy数组
            img_array = np.array(screen)

            # 创建颜色掩码
            mask = np.all(
                (img_array >= np.array(color) - tolerance)
                & (img_array <= np.array(color) + tolerance),
                axis=2,
            )

            # 查找匹配位置
            y_coords, x_coords = np.where(mask)
            if len(x_coords) > 0 and len(y_coords) > 0:
                # 返回第一个匹配位置
                return (int(x_coords[0]), int(y_coords[0]))

            return None
        except Exception as exc:
            raise TimeoutError("颜色查找操作超时") from exc

    def find_motion(
        self, screen: Image.Image, threshold: float = 30, ratio_threshold: float = 0.1
    ) -> Optional[bool]:
        """
        运动检测

        Args:
            screen: 当前屏幕截图
            threshold: 像素差异阈值
            ratio_threshold: 运动像素比例阈值

        Returns:
            bool: 是否检测到运动

        Raises:
            TimeoutError: 操作超时时抛出
            ScreenCollectorError: 检测失败时抛出
        """
        try:
            future = self._executor.submit(
                self._find_motion_impl, screen, threshold, ratio_threshold
            )
            return future.result(timeout=self.timeout)
        except TimeoutError as exc:
            raise TimeoutError("运动检测操作超时") from exc
        except Exception as e:
            raise ScreenCollectorError(f"运动检测失败: {str(e)}") from e

    def _find_motion_impl(
        self, screen: Image.Image, threshold: float, ratio_threshold: float
    ) -> bool:
        """运动检测的具体实现"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2GRAY)

            # 计算帧差
            if self.prev_frame is None:
                self.prev_frame = gray
                return False

            frame_diff = cv2.absdiff(self.prev_frame, gray)
            self.prev_frame = gray

            # 二值化
            thresh = cv2.threshold(frame_diff, threshold, 255, cv2.THRESH_BINARY)[1]

            # 计算运动像素比例
            motion_ratio = np.sum(thresh) / (thresh.shape[0] * thresh.shape[1] * 255)

            return motion_ratio > ratio_threshold
        except Exception as exc:
            raise TimeoutError("运动检测操作超时") from exc

    def find_image(
        self,
        source: Union[str, Image.Image, np.ndarray],
        template: Union[str, Image.Image, np.ndarray],
        threshold: float = 0.8,
    ) -> Optional[tuple]:
        """
        在图像中查找模板图像

        Args:
            source: 源图像
            template: 模板图像
            threshold: 匹配阈值

        Returns:
            Tuple[int, int]: 匹配位置的中心点坐标

        Raises:
            ScreenCollectorError: 查找失败时抛出
        """
        try:
            # 转换图像格式
            if isinstance(source, str):
                source = cv2.imread(source)
            elif isinstance(source, Image.Image):
                source = cv2.cvtColor(np.array(source), cv2.COLOR_RGB2BGR)

            if isinstance(template, str):
                template = cv2.imread(template)
            elif isinstance(template, Image.Image):
                template = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2BGR)

            # 执行模板匹配
            result = cv2.matchTemplate(source, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val < threshold:
                return None

            # 计算中心点坐标
            template_height, template_width = template.shape[:2]
            center_x = max_loc[0] + template_width // 2
            center_y = max_loc[1] + template_height // 2

            return (center_x, center_y)

        except Exception as e:
            raise ScreenCollectorError(f"查找图像失败: {str(e)}") from e

    def find_all_images(
        self,
        source: Union[str, Image.Image, np.ndarray],
        template: Union[str, Image.Image, np.ndarray],
        threshold: float = 0.8,
    ) -> List[tuple]:
        """
        在图像中查找所有匹配的模板图像

        Args:
            source: 源图像
            template: 模板图像
            threshold: 匹配阈值

        Returns:
            List[Tuple[int, int]]: 所有匹配位置的中心点坐标列表

        Raises:
            ScreenCollectorError: 查找失败时抛出
        """
        try:
            # 转换图像格式
            if isinstance(source, str):
                source = cv2.imread(source)
            elif isinstance(source, Image.Image):
                source = cv2.cvtColor(np.array(source), cv2.COLOR_RGB2BGR)

            if isinstance(template, str):
                template = cv2.imread(template)
            elif isinstance(template, Image.Image):
                template = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2BGR)

            # 执行模板匹配
            result = cv2.matchTemplate(source, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)

            # 获取模板尺寸
            template_height, template_width = template.shape[:2]

            # 计算所有匹配点的中心坐标
            points: List[tuple] = []
            for pt in zip(*locations[::-1]):
                center_x = pt[0] + template_width // 2
                center_y = pt[1] + template_height // 2
                points.append((center_x, center_y))

            return points

        except Exception as e:
            raise ScreenCollectorError(f"查找所有图像失败: {str(e)}") from e

    def new_method(self):
        pass  # 无尾随空格
