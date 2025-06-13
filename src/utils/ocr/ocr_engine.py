"""OCR引擎模块"""
from typing import List, Tuple, Union, Optional

import cv2
import numpy as np
from PIL import Image

from .text_detector import TextDetector
from .text_recognizer import TextRecognizer


class OCREngine:
    """OCR引擎类"""

    def __init__(self, detector_path: str, recognizer_path: str) -> None:
        """
        初始化OCR引擎

        Args:
            detector_path: 检测器模型路径
            recognizer_path: 识别器模型路径
        """
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        self.detector = TextDetector(detector_path, providers=providers)
        self.recognizer = TextRecognizer(recognizer_path, providers=providers)

    def detect(
        self, image: Union[str, np.ndarray, Image.Image]
    ) -> List[Tuple[int, int, int, int]]:
        """
        检测文本区域

        Args:
            image: 输入图像

        Returns:
            List[Tuple[int, int, int, int]]: 文本区域列表，每个元素为(x, y, w, h)
        """
        # 转换图像格式
        if isinstance(image, str):
            image = cv2.imread(image)
        elif isinstance(image, Image.Image):
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # 检测文本区域
        boxes = self.detector.detect(image)

        # 转换为整数坐标
        result = []
        for box in boxes:
            x1, y1 = box[0]
            x2, y2 = box[2]
            result.append(
                (
                    int(min(x1, x2)),
                    int(min(y1, y2)),
                    int(abs(x2 - x1)),
                    int(abs(y2 - y1)),
                )
            )

        return result

    def recognize(
        self,
        image: Union[str, np.ndarray, Image.Image],
        boxes: Optional[List[Tuple[int, int, int, int]]] = None,
    ) -> List[str]:
        """
        识别文本内容

        Args:
            image: 输入图像
            boxes: 文本区域列表，None表示识别整个图像

        Returns:
            List[str]: 识别结果列表
        """
        # 转换图像格式
        if isinstance(image, str):
            image = cv2.imread(image)
        elif isinstance(image, Image.Image):
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # 如果未指定文本区域，则检测文本区域
        if boxes is None:
            boxes = self.detect(image)

        # 裁剪并识别每个文本区域
        results = []
        for box in boxes:
            x, y, w, h = box
            roi = image[y : y + h, x : x + w]
            text = self.recognizer.recognize(roi)
            results.append(text)

        return results

    def ocr(
        self, image: Union[str, np.ndarray, Image.Image]
    ) -> List[Tuple[str, Tuple[int, int, int, int]]]:
        """
        执行OCR（检测+识别）

        Args:
            image: 输入图像

        Returns:
            List[Tuple[str, Tuple[int, int, int, int]]]: OCR结果列表，每个元素为(文本内容, 文本区域)
        """
        # 检测文本区域
        boxes = self.detect(image)

        # 识别文本内容
        texts = self.recognize(image, boxes)

        # 组合结果
        return list(zip(texts, boxes))

    def _convert_to_numpy(self, image: Union[str, Image.Image]) -> np.ndarray:
        if isinstance(image, str):
            return cv2.imread(image)
        elif isinstance(image, Image.Image):
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    def detect_and_recognize(
        self, image: Union[str, np.ndarray, Image.Image]
    ) -> List[str]:
        """
        检测并识别图像中的文字
        """
        # 统一转换为numpy数组
        if isinstance(image, (str, Image.Image)):
            image = self._convert_to_numpy(image)

        # 类型断言确保后续处理安全
        assert isinstance(
            image, np.ndarray
        ), "Input must be numpy array after conversion"

        # 检测文本区域
        boxes = self.detector.detect(image)
        results = []

        # 识别每个文本区域
        for box in boxes:
            roi = image[
                int(box[0][1]) : int(box[2][1]), int(box[0][0]) : int(box[2][0])
            ]
            text = self.recognizer.recognize(roi)[0][0]
            results.append(text)

        return results
