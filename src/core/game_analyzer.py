# -*- coding: utf-8 -*-
"""
游戏分析器
负责分析游戏画面和状态
"""
import json
import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import datetime

import cv2
import numpy as np


@dataclass
class UIElement:
    """UI元素信息"""

    name: str
    template: np.ndarray  # 模板图像
    mask: Optional[np.ndarray]  # 掩码
    threshold: float  # 匹配阈值
    click_offset: Tuple[int, int]  # 点击偏移


@dataclass
class SceneFeature:
    """场景特征"""

    name: str
    features: List[np.ndarray]  # 特征描述子
    keypoints: List[cv2.KeyPoint]  # 关键点
    reference_image: np.ndarray  # 参考图像


class GameAnalyzer:
    def __init__(self, game_name: str, data_dir: str):
        """
        初始化游戏分析器

        Args:
            game_name: 游戏名称
            data_dir: 数据目录
        """
        self.game_name = game_name
        self.data_dir = data_dir
        self.ui_elements: Dict[str, UIElement] = {}
        self.scenes: Dict[str, SceneFeature] = {}
        self.analysis_results: Dict = {}
        self.logger = logging.getLogger(__name__)

        # 创建特征检测器
        self.feature_detector = self.create_feature_detector()
        self.feature_matcher = cv2.BFMatcher(cv2.NORM_L2)

        # 加载已有数据
        self._load_data()

    def create_feature_detector(self) -> cv2.FeatureDetector:
        """创建特征检测器"""
        try:
            return cv2.SIFT.create()
        except AttributeError:
            return cv2.SIFT_create()

    def collect_ui_samples(
        self,
        screenshot: np.ndarray,
        roi: Tuple[int, int, int, int],
        name: str,
        num_samples: int = 10,
    ) -> None:
        """
        收集UI元素样本

        Args:
            screenshot: 游戏截图
            roi: 感兴趣区域 (x, y, w, h)
            name: 元素名称
            num_samples: 样本数量
        """
        x, y, w, h = roi
        sample = screenshot[y : y + h, x : x + w]

        # 保存样本
        sample_dir = os.path.join(self.data_dir, self.game_name, "ui_samples", name)
        os.makedirs(sample_dir, exist_ok=True)

        cv2.imwrite(
            os.path.join(sample_dir, f"{len(os.listdir(sample_dir))}.png"), sample
        )

    def learn_ui_element(
        self, name: str, threshold: float = 0.8
    ) -> Optional[UIElement]:
        """
        学习UI元素特征

        Args:
            name: 元素名称
            threshold: 匹配阈值

        Returns:
            Optional[UIElement]: 学习到的UI元素
        """
        sample_dir = os.path.join(self.data_dir, self.game_name, "ui_samples", name)
        if not os.path.exists(sample_dir):
            return None

        samples = []
        for file in os.listdir(sample_dir):
            if file.endswith(".png"):
                sample = cv2.imread(os.path.join(sample_dir, file))
                if sample is not None:
                    samples.append(sample)

        if not samples:
            return None

        # 计算平均模板
        template = np.mean(samples, axis=0).astype(np.uint8)

        # 计算掩码
        std = np.std(samples, axis=0)
        mask = (std < 30).astype(np.uint8) * 255

        # 计算点击偏移（默认中心）
        h, w = template.shape[:2]
        click_offset = (w // 2, h // 2)

        element = UIElement(
            name=name,
            template=template,
            mask=mask,
            threshold=threshold,
            click_offset=click_offset,
        )

        self.ui_elements[name] = element
        return element

    def collect_scene_sample(self, screenshot: np.ndarray, name: str) -> None:
        """
        收集场景样本

        Args:
            screenshot: 游戏截图
            name: 场景名称
        """
        # 提取特征
        keypoints, features = self.feature_detector.detectAndCompute(
            cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY), None
        )

        if features is None:
            return

        scene = SceneFeature(
            name=name,
            features=[features],
            keypoints=[keypoints],
            reference_image=screenshot,
        )

        self.scenes[name] = scene

    def analyze_screenshot(self, screenshot: np.ndarray) -> Dict:
        """
        分析游戏截图

        Args:
            screenshot: 游戏截图

        Returns:
            Dict: 分析结果
        """
        results = {
            "scene": self._detect_scene(screenshot),
            "ui_elements": self._detect_ui_elements(screenshot),
        }
        return results

    def _detect_scene(self, screenshot: np.ndarray) -> Optional[str]:
        """
        检测当前场景
        """
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        keypoints, features = self.feature_detector.detectAndCompute(gray, None)

        if features is None:
            return None

        best_match = None
        best_score = 0

        for name, scene in self.scenes.items():
            # 特征匹配
            matches = self.feature_matcher.knnMatch(features, scene.features[0], k=2)

            # 应用比率测试
            good_matches = []
            for m, n in matches:
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)

            score = len(good_matches) / len(matches)
            if score > best_score and score > 0.3:
                best_score = score
                best_match = name

        return best_match

    def _detect_ui_elements(self, screenshot: np.ndarray) -> Dict[str, Dict]:
        """
        检测UI元素
        """
        results = {}

        for name, element in self.ui_elements.items():
            # 模板匹配
            result = cv2.matchTemplate(
                screenshot, element.template, cv2.TM_CCORR_NORMED, mask=element.mask
            )

            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= element.threshold:
                x, y = max_loc
                w, h = element.template.shape[1::-1]

                results[name] = {
                    "position": (x, y, w, h),
                    "confidence": float(max_val),
                    "click_position": (
                        x + element.click_offset[0],
                        y + element.click_offset[1],
                    ),
                }

        return results

    def save_data(self) -> None:
        """保存分析数据"""
        data_path = os.path.join(self.data_dir, self.game_name)
        os.makedirs(data_path, exist_ok=True)

        # 保存UI元素
        ui_data = {}
        for name, element in self.ui_elements.items():
            ui_path = os.path.join(data_path, "ui_elements")
            os.makedirs(ui_path, exist_ok=True)

            # 保存模板图像
            cv2.imwrite(os.path.join(ui_path, f"{name}_template.png"), element.template)

            # 保存掩码
            if element.mask is not None:
                cv2.imwrite(os.path.join(ui_path, f"{name}_mask.png"), element.mask)

            ui_data[name] = {
                "threshold": element.threshold,
                "click_offset": element.click_offset,
            }

        with open(
            os.path.join(data_path, "ui_elements.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(ui_data, f, indent=4, ensure_ascii=False)

        # 保存场景数据
        scene_data = {}
        for name, scene in self.scenes.items():
            scene_path = os.path.join(data_path, "scenes")
            os.makedirs(scene_path, exist_ok=True)

            # 保存参考图像
            cv2.imwrite(
                os.path.join(scene_path, f"{name}_reference.png"), scene.reference_image
            )

            # 保存特征数据
            np.save(os.path.join(scene_path, f"{name}_features.npy"), scene.features[0])

        with open(os.path.join(data_path, "scenes.json"), "w", encoding="utf-8") as f:
            json.dump(scene_data, f, indent=4, ensure_ascii=False)

    def _load_data(self) -> None:
        """加载分析数据"""
        data_path = os.path.join(self.data_dir, self.game_name)

        # 加载UI元素
        ui_elements_file = os.path.join(data_path, "ui_elements.json")
        if os.path.exists(ui_elements_file):
            with open(ui_elements_file, "r", encoding="utf-8") as f:
                ui_data = json.load(f)

            ui_path = os.path.join(data_path, "ui_elements")
            for name, data in ui_data.items():
                template = cv2.imread(os.path.join(ui_path, f"{name}_template.png"))

                mask_file = os.path.join(ui_path, f"{name}_mask.png")
                mask = cv2.imread(mask_file) if os.path.exists(mask_file) else None

                if template is not None:
                    self.ui_elements[name] = UIElement(
                        name=name,
                        template=template,
                        mask=mask,
                        threshold=data["threshold"],
                        click_offset=tuple(data["click_offset"]),
                    )

        # 加载场景数据
        scenes_file = os.path.join(data_path, "scenes.json")
        if os.path.exists(scenes_file):
            scene_path = os.path.join(data_path, "scenes")

            for file in os.listdir(scene_path):
                if file.endswith("_reference.png"):
                    name = file[:-14]  # 移除"_reference.png"

                    reference = cv2.imread(os.path.join(scene_path, file))

                    features = np.load(os.path.join(scene_path, f"{name}_features.npy"))

                    if reference is not None and features is not None:
                        keypoints = self.feature_detector.detect(
                            cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
                        )

                        self.scenes[name] = SceneFeature(
                            name=name,
                            features=[features],
                            keypoints=[keypoints],
                            reference_image=reference,
                        )

    def save_analysis_result(self, result: Dict, filepath: str) -> bool:
        """保存分析结果到文件"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error("保存分析结果失败: %s", e)
            return False

    def load_analysis_result(self, filepath: str) -> Optional[Dict]:
        """从文件加载分析结果"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error("加载分析结果失败: %s", e)
            return None

    def export_analysis_report(self, filepath: str) -> bool:
        """导出分析报告"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                # 写入报告头部
                f.write("游戏分析报告\n")
                f.write("=" * 20 + "\n\n")

                # 写入基本信息
                f.write("基本信息:\n")
                f.write("-" * 10 + "\n")
                f.write(
                    f"分析时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                f.write(f"游戏名称: {self.game_name}\n\n")

                # 写入分析结果
                f.write("分析结果:\n")
                f.write("-" * 10 + "\n")
                for key, value in self.analysis_results.items():
                    f.write(f"{key}: {value}\n")

            return True

        except Exception as e:
            self.logger.error("导出分析报告失败: %s", e)
            return False

    def find_template(
        self, image: np.ndarray, template: np.ndarray, threshold: float = 0.8
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        在图像中查找模板

        Args:
            image: 源图像
            template: 模板图像
            threshold: 匹配阈值

        Returns:
            Optional[Tuple[int, int, int, int]]: 匹配区域(x, y, w, h)，未找到返回None
        """
        try:
            # 执行模板匹配
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val < threshold:
                return None

            # 获取模板大小
            h, w = template.shape[:2]

            # 返回匹配区域
            return (max_loc[0], max_loc[1], w, h)

        except Exception as e:
            self.logger.error("模板匹配失败: %s", str(e))
            return None

    def find_all_templates(
        self, image: np.ndarray, template: np.ndarray, threshold: float = 0.8
    ) -> List[Tuple[int, int, int, int]]:
        """
        在图像中查找所有匹配的模板

        Args:
            image: 源图像
            template: 模板图像
            threshold: 匹配阈值

        Returns:
            List[Tuple[int, int, int, int]]: 所有匹配区域的列表
        """
        try:
            # 执行模板匹配
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)

            # 获取模板大小
            h, w = template.shape[:2]

            # 返回所有匹配区域
            return [(int(x), int(y), w, h) for x, y in zip(*locations[::-1])]

        except Exception as e:
            self.logger.error("查找所有模板失败: %s", str(e))
            return []

    def detect_motion(
        self, frame1: np.ndarray, frame2: np.ndarray, threshold: int = 25
    ) -> float:
        """
        检测两帧之间的运动

        Args:
            frame1: 第一帧
            frame2: 第二帧
            threshold: 差异阈值

        Returns:
            float: 运动比例(0-1)
        """
        try:
            # 转换为灰度图
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

            # 计算差异
            diff = cv2.absdiff(gray1, gray2)

            # 应用阈值
            _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)

            # 计算运动比例
            total_pixels = thresh.shape[0] * thresh.shape[1]
            motion_pixels = np.count_nonzero(thresh)

            return float(motion_pixels) / total_pixels

        except Exception as e:
            self.logger.error("运动检测失败: %s", str(e))
            return 0.0

    def detect_features(
        self, image: np.ndarray
    ) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """
        检测图像特征点

        Args:
            image: 输入图像

        Returns:
            Tuple[List[cv2.KeyPoint], np.ndarray]: 特征点和描述符
        """
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # 检测特征点
            keypoints, descriptors = self.feature_detector.detectAndCompute(gray, None)

            return keypoints, descriptors

        except Exception as e:
            self.logger.error("特征检测失败: %s", str(e))
            return [], np.array([])

    def calculate_similarity(self, region1: np.ndarray, region2: np.ndarray) -> float:
        """计算两个区域的相似度"""
        # 添加类型断言确保输入为numpy数组
        assert isinstance(region1, np.ndarray), "region1 must be numpy array"
        assert isinstance(region2, np.ndarray), "region2 must be numpy array"

        # 统一转换为BGR格式
        if region1.shape[-1] == 4:
            region1 = cv2.cvtColor(region1, cv2.COLOR_BGRA2BGR)
        if region2.shape[-1] == 4:
            region2 = cv2.cvtColor(region2, cv2.COLOR_BGRA2BGR)

        try:
            # 转换为灰度图
            gray1 = cv2.cvtColor(region1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(region2, cv2.COLOR_BGR2GRAY)

            # 计算相似度
            similarity = float(
                cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)[0][0]
            )
            return similarity
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"计算相似度失败: {str(e)}")
            return 0.0
