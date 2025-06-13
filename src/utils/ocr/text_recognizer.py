"""
文字识别模块
"""
from typing import Tuple, List

import cv2
import numpy as np
import onnxruntime as ort


class TextRecognizer:
    def __init__(self, model_path: str, providers: List[str]):
        """
        初始化文字识别器

        Args:
            model_path: 模型路径
            providers: ONNX Runtime执行提供程序列表
        """
        self.session = ort.InferenceSession(model_path, providers=providers)
        self.input_name = self.session.get_inputs()[0].name

        # 字符集映射
        self.characters = self._load_characters()

    def recognize(self, image: np.ndarray) -> Tuple[str, float]:
        """
        识别文本图像中的文字

        Args:
            image: 输入图像(BGR格式)

        Returns:
            Tuple[str, float]: (识别的文本, 置信度)
        """
        # 图像预处理
        preprocessed = self._preprocess(image)

        # 模型推理
        pred = self.session.run(None, {self.input_name: preprocessed})[0]

        # 解码输出
        text, confidence = self._decode(pred[0])

        return text, confidence

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        图像预处理
        """
        # 转灰度图
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 调整大小到固定高度
        h, w = image.shape
        new_h = 32
        new_w = int(w * (new_h / h))
        image = cv2.resize(image, (new_w, new_h))

        # 归一化
        image = image.astype(np.float32) / 255.0
        image = (image - 0.5) / 0.5

        # 添加通道和batch维度
        image = np.expand_dims(image, axis=0)
        image = np.expand_dims(image, axis=0)

        return image

    def _decode(self, pred: np.ndarray) -> Tuple[str, float]:
        """
        解码模型输出

        Args:
            pred: 模型输出的概率分布

        Returns:
            Tuple[str, float]: (识别的文本, 置信度)
        """
        # 获取每个时间步的最大概率字符索引
        indices = np.argmax(pred, axis=1)

        # 去重和去除blank
        text = []
        for i, idx in enumerate(indices):
            if idx == 0:  # blank
                continue
            if i > 0 and idx == indices[i - 1]:  # 重复字符
                continue
            text.append(self.characters[idx])

        # 计算置信度
        confidences = [pred[i, idx] for i, idx in enumerate(indices)]
        confidence = float(np.mean(confidences))

        return "".join(text), confidence

    def _load_characters(self) -> List[str]:
        """
        加载字符集
        """
        # 这里使用简单的ASCII字符集作为示例
        # 实际应用中应该加载完整的中文字符集
        chars = [""]  # blank
        chars.extend([chr(i) for i in range(32, 127)])  # ASCII可打印字符
        return chars
