"""
图像识别模块
提供图像匹配和文字识别功能
"""
from typing import Optional, Dict
import logging

import cv2
import easyocr
import numpy as np
from PIL import Image


class ImageRecognition:
    """图像识别类"""

    def __init__(self):
        self.logger = logging.getLogger("ImageRecognition")
        self._ocr = None

    def match_template(
        self, image: np.ndarray, template: np.ndarray, threshold: float = 0.8
    ) -> Optional[Dict]:
        """
        模板匹配

        Args:
            image: 待匹配图像路径或numpy数组
            template: 模板图像路径或numpy数组
            threshold: 匹配阈值

        Returns:
            匹配结果字典，包含位置和置信度
        """
        try:
            # 加载图像
            if isinstance(image, str):
                image = self.load_image(image)
            if isinstance(template, str):
                template = self.load_image(template)

            if image is None or template is None:
                self.logger.error("图像加载失败")
                return None

            # 转换为灰度图
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

            # 模板匹配
            result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val < threshold:
                return None

            # 获取匹配区域
            w, h = template.shape[1], template.shape[0]
            x, y = max_loc

            return {
                "confidence": max_val,
                "position": (x, y),
                "size": (w, h),
                "center": (x + w // 2, y + h // 2),
            }

        except Exception as e:
            self.logger.error("模板匹配失败: %s", e)
            return None

    def load_image(self, path: str) -> np.ndarray:
        return cv2.imread(path)

    def extract_text(self, image: np.ndarray, lang: str = "ch_sim") -> Optional[str]:
        """
        提取图像中的文字

        Args:
            image: 图像路径或numpy数组
            lang: 语言，默认为简体中文

        Returns:
            识别到的文字
        """
        try:
            # 延迟初始化OCR
            if self._ocr is None:
                self._ocr = easyocr.Reader([lang])

            # 加载图像
            if isinstance(image, str):
                image = Image.open(image)
            elif isinstance(image, np.ndarray):
                image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            # 识别文字
            result = self._ocr.readtext(np.array(image))

            # 提取文字
            text = " ".join(item[1] for item in result)
            return text.strip()

        except Exception as e:
            self.logger.error("文字识别失败: %s", e)
            return None
