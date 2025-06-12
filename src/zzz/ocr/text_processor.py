"""
OCR文字处理模块
"""
import cv2
import numpy as np
import onnxruntime as ort
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class TextBox:
    """文字框数据类"""

    text: str
    confidence: float
    box: np.ndarray  # 形状为(4,2)的数组，表示四个角点坐标


class TextProcessor:
    def __init__(
        self, detection_model: str, recognition_model: str, providers: List[str]
    ):
        """
        初始化文字处理器

        Args:
            detection_model: 文字检测模型路径(EAST)
            recognition_model: 文字识别模型路径(CRNN)
            providers: ONNX Runtime执行提供程序列表
        """
        # 创建推理会话
        self.detection_session = ort.InferenceSession(
            detection_model, providers=providers
        )
        self.recognition_session = ort.InferenceSession(
            recognition_model, providers=providers
        )

        # 获取输入输出名称
        self.detection_input = self.detection_session.get_inputs()[0].name
        self.recognition_input = self.recognition_session.get_inputs()[0].name

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        图像预处理

        Args:
            image: 输入图像(1280x720 RGB)

        Returns:
            np.ndarray: 预处理后的图像
        """
        # 调整大小到模型输入尺寸
        resized = cv2.resize(image, (1280, 720))

        # 对比度增强
        lab = cv2.cvtColor(resized, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge((l, a, b))
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)

        # 归一化
        normalized = enhanced.astype(np.float32) / 255.0

        # 添加batch维度
        return np.expand_dims(normalized, axis=0)

    def detect_text_regions(
        self,
        image: np.ndarray,
        score_threshold: float = 0.9,
        nms_threshold: float = 0.2,
    ) -> List[np.ndarray]:
        """
        检测文字区域

        Args:
            image: 预处理后的图像
            score_threshold: 置信度阈值
            nms_threshold: 非极大值抑制阈值

        Returns:
            List[np.ndarray]: 文字区域框列表
        """
        # EAST模型推理
        scores, geometries = self.detection_session.run(
            None, {self.detection_input: image}
        )

        # 解码检测结果
        boxes = []
        confidences = []

        height, width = image.shape[1:3]
        for y in range(0, height, 4):
            for x in range(0, width, 4):
                score = scores[0, y, x]
                if score < score_threshold:
                    continue

                # 解码EAST输出的几何信息
                offset_x = geometries[0, y, x] * 4
                offset_y = geometries[1, y, x] * 4
                h = geometries[2, y, x] * 4
                w = geometries[3, y, x] * 4
                angle = geometries[4, y, x]

                # 计算旋转框的四个角点
                cos_a = np.cos(angle)
                sin_a = np.sin(angle)

                h_w = w / 2
                h_h = h / 2

                x1 = x * 4 + h_w * cos_a - h_h * sin_a + offset_x
                y1 = y * 4 + h_w * sin_a + h_h * cos_a + offset_y

                x3 = x * 4 - h_w * cos_a - h_h * sin_a + offset_x
                y3 = y * 4 - h_w * sin_a + h_h * cos_a + offset_y

                box = np.array([[x1, y1], [x1, y3], [x3, y3], [x3, y1]])
                boxes.append(box)
                confidences.append(score)

        # 非极大值抑制
        indices = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold, nms_threshold)
        return [boxes[i] for i in indices]

    def recognize_text(self, image: np.ndarray, box: np.ndarray) -> Tuple[str, float]:
        """
        识别文字内容

        Args:
            image: 原始图像
            box: 文字区域框

        Returns:
            Tuple[str, float]: (识别的文本, 置信度)
        """
        # 透视变换提取文字区域
        width = int(np.linalg.norm(box[0] - box[1]))
        height = int(np.linalg.norm(box[1] - box[2]))

        src_pts = box.astype(np.float32)
        dst_pts = np.array(
            [[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32
        )

        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped = cv2.warpPerspective(image, M, (width, height))

        # 预处理文字图像
        gray = cv2.cvtColor(warped, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 调整大小到识别模型输入尺寸
        resized = cv2.resize(binary, (100, 32))

        # 归一化并添加维度
        x = resized.astype(np.float32) / 255.0
        x = np.expand_dims(x, axis=0)
        x = np.expand_dims(x, axis=0)

        # CRNN模型推理
        preds = self.recognition_session.run(None, {self.recognition_input: x})[0]

        # 解码预测结果
        text, confidence = self._decode_crnn(preds[0])
        return text, confidence

    def _decode_crnn(self, pred: np.ndarray) -> Tuple[str, float]:
        """
        解码CRNN模型输出
        """
        # 字符集映射
        charset = "0123456789abcdefghijklmnopqrstuvwxyz"

        # 获取每个时间步的最大概率字符
        indices = np.argmax(pred, axis=1)
        probs = np.max(pred, axis=1)

        # 合并重复字符
        last_char = None
        text = []
        confidences = []

        for i, (idx, prob) in enumerate(zip(indices, probs)):
            if idx == 0:  # CTC blank
                continue
            char = charset[idx - 1]
            if char != last_char:
                text.append(char)
                confidences.append(prob)
                last_char = char

        return "".join(text), float(np.mean(confidences))

    def process_image(self, image: np.ndarray) -> List[TextBox]:
        """
        处理图像中的文字

        Args:
            image: 输入图像(1280x720 RGB)

        Returns:
            List[TextBox]: 检测到的文字框列表
        """
        # 预处理图像
        preprocessed = self.preprocess_image(image)

        # 检测文字区域
        boxes = self.detect_text_regions(preprocessed)

        # 识别文字内容
        results = []
        for box in boxes:
            text, confidence = self.recognize_text(image, box)
            if text:  # 过滤空文本
                results.append(TextBox(text=text, confidence=confidence, box=box))

        return results
