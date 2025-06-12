"""图像识别工具模块"""
import cv2
import numpy as np
import pytesseract
from PIL import Image
from typing import List, Tuple, Optional, Dict, Any


class ImageRecognition:
    """图像识别工具类"""

    def __init__(self):
        """初始化图像识别工具"""
        self.templates: Dict[str, Image.Image] = {}

    def find_buttons(self, image: Image.Image) -> List[Tuple[int, int, int, int]]:
        """
        在图像中查找按钮。

        Args:
            image: 待分析的图像

        Returns:
            List[Tuple[int, int, int, int]]: 按钮位置列表，每个元素为 (x, y, width, height)
        """
        # 转换为OpenCV格式
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # 边缘检测
        edges = cv2.Canny(gray, 50, 150)

        # 查找轮廓
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        buttons = []
        for contour in contours:
            # 获取矩形边界
            x, y, w, h = cv2.boundingRect(contour)

            # 根据按钮的一般特征筛选
            if w > 20 and h > 10 and w < image.width * 0.8 and h < image.height * 0.5:
                buttons.append((x, y, w, h))

        return buttons

    def find_icons(self, image: Image.Image) -> List[Tuple[int, int, int, int]]:
        """
        在图像中查找图标。

        Args:
            image: 待分析的图像

        Returns:
            List[Tuple[int, int, int, int]]: 图标位置列表，每个元素为 (x, y, width, height)
        """
        # 转换为OpenCV格式
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # 使用SIFT检测特征点
        sift = cv2.SIFT_create()
        keypoints = sift.detect(gray, None)

        icons = []
        for kp in keypoints:
            # 根据特征点的大小和响应值筛选可能的图标
            if kp.size > 10 and kp.response > 0.1:
                x = int(kp.pt[0] - kp.size / 2)
                y = int(kp.pt[1] - kp.size / 2)
                size = int(kp.size)
                icons.append((x, y, size, size))

        return icons

    def find_progress_bars(self, image: Image.Image) -> List[Tuple[int, int, int, int]]:
        """
        在图像中查找进度条。

        Args:
            image: 待分析的图像

        Returns:
            List[Tuple[int, int, int, int]]: 进度条位置列表，每个元素为 (x, y, width, height)
        """
        # 转换为OpenCV格式
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # 边缘检测
        edges = cv2.Canny(gray, 50, 150)

        # 查找轮廓
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        progress_bars = []
        for contour in contours:
            # 获取矩形边界
            x, y, w, h = cv2.boundingRect(contour)

            # 根据进度条的一般特征筛选（宽度远大于高度）
            if w > 3 * h and w > 30:
                progress_bars.append((x, y, w, h))

        return progress_bars

    def extract_text(self, image: Image.Image) -> str:
        """
        从图像中提取文本。

        Args:
            image: 待分析的图像

        Returns:
            str: 提取的文本
        """
        return pytesseract.image_to_string(image)

    def match_template(
        self, image: Image.Image, template: Image.Image, threshold: float = 0.8
    ) -> List[Tuple[int, int]]:
        """
        在图像中匹配模板。

        Args:
            image: 待匹配的图像
            template: 模板图像
            threshold: 匹配阈值，范围[0,1]

        Returns:
            List[Tuple[int, int]]: 匹配位置列表，每个元素为 (x, y)
        """
        # 转换为OpenCV格式
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        template_cv = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2BGR)

        # 模板匹配
        result = cv2.matchTemplate(img_cv, template_cv, cv2.TM_CCOEFF_NORMED)

        # 查找匹配位置
        locations = np.where(result >= threshold)
        matches = list(zip(*locations[::-1]))  # 转换为(x,y)格式

        return matches

    def find_text_regions(self, image: Image.Image) -> List[Tuple[int, int, int, int]]:
        """
        查找图像中可能包含文本的区域。

        Args:
            image: 待分析的图像

        Returns:
            List[Tuple[int, int, int, int]]: 文本区域列表，每个元素为 (x, y, width, height)
        """
        # 转换为OpenCV格式
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # 二值化
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 查找轮廓
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # 根据文本区域的一般特征筛选
            if w > 10 and h > 5 and w / h < 20:
                text_regions.append((x, y, w, h))

        return text_regions

    def detect_motion(
        self, image1: Image.Image, image2: Image.Image
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        检测两帧图像之间的运动区域。

        Args:
            image1: 第一帧图像
            image2: 第二帧图像

        Returns:
            Optional[Tuple[int, int, int, int]]: 运动区域，格式为 (x, y, width, height)，如果没有检测到运动则返回 None
        """
        # 转换为OpenCV格式
        img1_cv = cv2.cvtColor(np.array(image1), cv2.COLOR_RGB2BGR)
        img2_cv = cv2.cvtColor(np.array(image2), cv2.COLOR_RGB2BGR)

        # 转换为灰度图
        gray1 = cv2.cvtColor(img1_cv, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2_cv, cv2.COLOR_BGR2GRAY)

        # 计算差异
        diff = cv2.absdiff(gray1, gray2)

        # 二值化
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        # 查找轮廓
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if contours:
            # 获取最大的运动区域
            max_contour = max(contours, key=cv2.contourArea)
            return cv2.boundingRect(max_contour)

        return None

    def analyze_colors(self, image: Image.Image) -> Dict[str, float]:
        """
        分析图像的主要颜色。

        Args:
            image: 待分析的图像

        Returns:
            Dict[str, float]: 颜色分布，键为颜色名称，值为该颜色占比
        """
        # 转换为OpenCV格式
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # 将图像转换为HSV颜色空间
        hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)

        # 定义主要颜色的HSV范围
        color_ranges = {
            "red": [(0, 50, 50), (10, 255, 255)],
            "yellow": [(20, 50, 50), (35, 255, 255)],
            "green": [(35, 50, 50), (85, 255, 255)],
            "blue": [(85, 50, 50), (130, 255, 255)],
            "purple": [(130, 50, 50), (170, 255, 255)],
        }

        results = {}
        total_pixels = image.width * image.height

        for color_name, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            color_pixels = cv2.countNonZero(mask)
            results[color_name] = color_pixels / total_pixels

        return results
