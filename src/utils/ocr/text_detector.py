"""
文字检测模块
"""
from typing import List, Tuple

import cv2
import numpy as np
import onnxruntime as ort
import pyclipper


class TextDetector:
    def __init__(self, model_path: str, providers: List[str]):
        """
        初始化文字检测器

        Args:
            model_path: 模型路径
            providers: ONNX Runtime执行提供程序列表
        """
        if providers is None:
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        self.session = ort.InferenceSession(model_path, providers=providers)
        self.input_name = self.session.get_inputs()[0].name

    def detect(self, image: np.ndarray) -> List[List[Tuple[int, int]]]:
        """
        检测图像中的文字区域

        Args:
            image: 输入图像(BGR格式)

        Returns:
            List[List[Tuple[int, int]]]: 文字区域坐标点列表
        """
        # 图像预处理
        preprocessed = self._preprocess(image)

        # 模型推理
        score_maps = self.session.run(None, {self.input_name: preprocessed})[0]

        # 后处理获取文本框
        text_boxes = self._postprocess(score_maps[0])

        return text_boxes

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        图像预处理
        """
        # 缩放到固定大小
        h, w = image.shape[:2]
        scale = min(1024 / w, 1024 / h)
        nw = int(w * scale)
        nh = int(h * scale)
        image = cv2.resize(image, (nw, nh))

        # 填充到32的倍数
        pw = (32 - nw % 32) if nw % 32 != 0 else 0
        ph = (32 - nh % 32) if nh % 32 != 0 else 0
        image = cv2.copyMakeBorder(
            image, 0, ph, 0, pw, cv2.BORDER_CONSTANT, value=(114, 114, 114)
        )

        # 转换为浮点数并归一化
        image = image.astype(np.float32) / 255.0

        # 添加batch维度
        image = np.expand_dims(image, axis=0)

        return image

    def _postprocess(
        self,
        score_map: np.ndarray,
        text_threshold: float = 0.3,
        link_threshold: float = 0.15,
        min_size: int = 3,
    ) -> List[List[Tuple[int, int]]]:
        """
        后处理提取文本框
        """
        # 二值化
        binary = score_map > text_threshold

        # 连通域分析
        n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            binary.astype(np.uint8), connectivity=4
        )

        # 提取文本框
        text_boxes = []
        for k in range(1, n_labels):
            size = stats[k, cv2.CC_STAT_AREA]
            if size < min_size:
                continue

            # 获取文本区域掩码
            segmap = np.zeros_like(binary, dtype=np.uint8)
            segmap[labels == k] = 255

            # 获取文本框顶点
            x, y = np.where(segmap > 0)
            coords = np.stack([x, y], axis=-1)

            # 计算凸包
            hull = cv2.convexHull(coords)

            # 膨胀文本框
            expanded = self.unclip(hull)

            # 转换为元组列表
            text_box = [(int(p[0]), int(p[1])) for p in expanded]
            text_boxes.append(text_box)

        return text_boxes

    def unclip(self, box, unclip_ratio=2.0):
        area = cv2.contourArea(box)
        length = cv2.arcLength(box, True)

        # 计算偏移距离
        distance = area * unclip_ratio / length

        # 使用pyclipper进行多边形扩张
        pc = pyclipper.Pyclipper()
        pc.AddPath(
            box.reshape(-1).tolist(), pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON
        )
        expanded = np.array(pc.Execute(distance))

        return expanded
