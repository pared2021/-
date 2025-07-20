#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一游戏分析器
融合传统图像处理和深度学习方法，提供完整的游戏分析功能
"""

import json
import logging
import os
import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import cv2
import numpy as np

# 可选的深度学习支持
try:
    import torch
    from torchvision import models, transforms
    from PIL import Image
    DEEP_LEARNING_AVAILABLE = True
except ImportError:
    DEEP_LEARNING_AVAILABLE = False

# 修复导入路径
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.logger import GameLogger
from src.services.image_processor import ImageProcessor
from src.services.config import Config


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


class UnifiedGameAnalyzer:
    """统一游戏分析器，融合传统图像处理和深度学习方法"""
    
    def __init__(self, logger: GameLogger, image_processor: ImageProcessor, config: Config, game_name: str = "default"):
        """
        初始化统一游戏分析器
        
        Args:
            logger: 日志服务
            image_processor: 图像处理服务
            config: 配置服务
            game_name: 游戏名称
        """
        self.logger = logger
        self.image_processor = image_processor
        self.config = config
        self.game_name = game_name
        
        # 传统图像处理组件
        self.ui_elements: Dict[str, UIElement] = {}
        self.scenes: Dict[str, SceneFeature] = {}
        self.analysis_results: Dict = {}
        
        # 创建特征检测器
        self.feature_detector = self._create_feature_detector()
        self.feature_matcher = cv2.BFMatcher(cv2.NORM_L2)
        
        # 深度学习组件（可选）
        self.model = None
        self.transform = None
        self.custom_classifier = None
        self.class_names = []
        
        # 初始化深度学习模型
        self._init_deep_learning()
        
        # 数据目录
        self.data_dir = os.path.join(config.get_data_dir(), "analyzer_data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 加载已有数据
        self._load_data()
        
        self.logger.info(f"统一游戏分析器初始化完成 (游戏: {game_name})")
    
    def _create_feature_detector(self):
        """创建特征检测器"""
        try:
            return cv2.SIFT.create()
        except AttributeError:
            try:
                return cv2.SIFT_create()
            except AttributeError:
                self.logger.warning("SIFT不可用，使用ORB作为替代")
                return cv2.ORB_create()
    
    def _init_deep_learning(self):
        """初始化深度学习组件"""
        if not DEEP_LEARNING_AVAILABLE:
            self.logger.warning("深度学习库不可用，将仅使用传统图像处理方法")
            return
        
        try:
            # 加载预训练的ResNet模型
            self.logger.info("加载预训练的ResNet模型")
            self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            self.model.eval()
            
            # 图像预处理
            self.transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                  std=[0.229, 0.224, 0.225])
            ])
            
            self.logger.info("深度学习模型初始化成功")
        except Exception as e:
            self.logger.error(f"深度学习模型初始化失败: {e}")
            self.model = None
    
    def analyze_frame(self, frame: Optional[np.ndarray]) -> Dict[str, Any]:
        """
        分析游戏画面帧 - 主要分析入口
        
        Args:
            frame: 游戏画面帧数据
            
        Returns:
            Dict[str, Any]: 完整的游戏状态分析结果
        """
        try:
            # 输入验证和预处理
            processed_frame = self._preprocess_frame(frame)
            if processed_frame is None:
                return self._get_default_state()
            
            # 基础状态
            state = self._get_default_state()
            state["screen_size"] = processed_frame.shape[:2][::-1]  # 宽高
            state["timestamp"] = self.image_processor.get_current_timestamp()
            
            # 传统图像处理分析
            traditional_results = self._analyze_traditional(processed_frame)
            
            # 深度学习分析（如果可用）
            if self.model is not None:
                deep_learning_results = self._analyze_deep_learning(processed_frame)
                # 合并结果
                state.update(deep_learning_results)
            
            # 合并传统分析结果
            state.update(traditional_results)
            
            self.logger.debug("游戏画面分析完成")
            return state
            
        except Exception as e:
            self.logger.error(f"分析游戏画面失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return self._get_default_state()
    
    def _preprocess_frame(self, frame: Optional[np.ndarray]) -> Optional[np.ndarray]:
        """预处理帧数据"""
        if frame is None:
            self.logger.warning("帧数据为空")
            return None
        
        if isinstance(frame, bool):
            self.logger.warning(f"帧数据类型错误: {type(frame)}")
            return None
        
        if not isinstance(frame, np.ndarray):
            try:
                frame = np.array(frame)
                self.logger.debug("成功转换帧数据为numpy数组")
            except Exception as e:
                self.logger.error(f"转换帧数据失败: {e}")
                return None
        
        if frame.size == 0:
            self.logger.warning("帧数据为空数组")
            return None
        
        if len(frame.shape) != 3:
            self.logger.warning(f"帧数据维度错误: {frame.shape}")
            return None
        
        # 通道数检查和转换
        if frame.shape[2] != 3:
            try:
                if frame.shape[2] == 4:  # RGBA/BGRA
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                elif frame.shape[2] == 1:  # 灰度图
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                else:
                    self.logger.warning(f"无法处理的通道数: {frame.shape[2]}")
                    return None
            except Exception as e:
                self.logger.warning(f"通道转换失败: {e}")
                return None
        
        # 检查图像内容
        if np.all(frame == 0) or np.all(frame == 255):
            self.logger.warning("帧数据异常（全黑或全白）")
            return None
        
        return frame
    
    def _get_default_state(self) -> Dict[str, Any]:
        """获取默认状态"""
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "screen_size": (0, 0),
            "scene": None,
            "ui_elements": {},
            "buttons": [],
            "enemies": [],
            "items": [],
            "dialog_open": False,
            "health": 100,
            "mana": 100,
            "position": (0, 0),
            "objects": [],
            "motion_detected": False,
            "features_extracted": False
        }
    
    def _analyze_traditional(self, frame: np.ndarray) -> Dict[str, Any]:
        """传统图像处理分析"""
        results = {}
        
        try:
            # 场景检测
            scene = self._detect_scene(frame)
            if scene:
                results["scene"] = scene
            
            # UI元素检测
            ui_elements = self._detect_ui_elements(frame)
            if ui_elements:
                results["ui_elements"] = ui_elements
            
            # 特征提取
            results["features_extracted"] = True
            
        except Exception as e:
            self.logger.error(f"传统分析失败: {e}")
        
        return results
    
    def _analyze_deep_learning(self, frame: np.ndarray) -> Dict[str, Any]:
        """深度学习分析"""
        results = {}
        
        try:
            # 按钮检测
            buttons = self._detect_buttons(frame)
            if buttons:
                results["buttons"] = buttons
            
            # 敌人检测
            enemies = self._detect_enemies(frame)
            if enemies:
                results["enemies"] = enemies
            
            # 物品检测
            items = self._detect_items(frame)
            if items:
                results["items"] = items
            
            # 对话框检测
            dialog_info = self._detect_dialog(frame)
            if dialog_info:
                results["dialog_open"] = True
                results["dialog"] = dialog_info
            
            # 生命值和法力值检测
            health, mana = self._detect_health_mana(frame)
            if health is not None:
                results["health"] = health
            if mana is not None:
                results["mana"] = mana
            
            # 玩家位置检测
            position = self._detect_player_position(frame)
            if position:
                results["position"] = position
            
        except Exception as e:
            self.logger.error(f"深度学习分析失败: {e}")
        
        return results
    
    # ============= 传统图像处理方法 =============
    
    def _detect_scene(self, screenshot: np.ndarray) -> Optional[str]:
        """检测当前场景"""
        try:
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
                for match_pair in matches:
                    if len(match_pair) == 2:
                        m, n = match_pair
                        if m.distance < 0.75 * n.distance:
                            good_matches.append(m)

                if len(matches) > 0:
                    score = len(good_matches) / len(matches)
                    if score > best_score and score > 0.3:
                        best_score = score
                        best_match = name

            return best_match
        except Exception as e:
            self.logger.error(f"场景检测失败: {e}")
            return None
    
    def _detect_ui_elements(self, screenshot: np.ndarray) -> Dict[str, Dict]:
        """检测UI元素"""
        results = {}
        
        try:
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
        except Exception as e:
            self.logger.error(f"UI元素检测失败: {e}")
        
        return results
    
    # ============= 深度学习方法 =============
    
    def _detect_buttons(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """检测按钮"""
        try:
            buttons = []
            
            # 简单颜色检测示例
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_blue = np.array([100, 50, 50])
            upper_blue = np.array([140, 255, 255])
            mask = cv2.inRange(hsv, lower_blue, upper_blue)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                if cv2.contourArea(contour) < 500:
                    continue
                    
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w // 2
                center_y = y + h // 2
                
                buttons.append({
                    "position": (center_x, center_y),
                    "size": (w, h),
                    "type": "button",
                    "confidence": 0.8
                })
                
            return buttons
        except Exception as e:
            self.logger.error(f"按钮检测失败: {e}")
            return []
    
    def _detect_enemies(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """检测敌人"""
        try:
            enemies = []
            
            # 红色检测示例
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = cv2.bitwise_or(mask1, mask2)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                if cv2.contourArea(contour) < 300:
                    continue
                    
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w // 2
                center_y = y + h // 2
                
                enemies.append({
                    "position": (center_x, center_y),
                    "size": (w, h),
                    "type": "enemy",
                    "health": 100,
                    "distance": self._calculate_distance(
                        (center_x, center_y), 
                        (frame.shape[1] // 2, frame.shape[0] // 2)
                    )
                })
            
            enemies.sort(key=lambda x: x["distance"])
            return enemies
        except Exception as e:
            self.logger.error(f"敌人检测失败: {e}")
            return []
    
    def _detect_items(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """检测物品"""
        try:
            items = []
            
            # 黄色检测示例
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_yellow = np.array([20, 100, 100])
            upper_yellow = np.array([30, 255, 255])
            mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                if cv2.contourArea(contour) < 100:
                    continue
                    
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w // 2
                center_y = y + h // 2
                
                items.append({
                    "position": (center_x, center_y),
                    "size": (w, h),
                    "type": "item",
                    "value": "unknown",
                    "distance": self._calculate_distance(
                        (center_x, center_y), 
                        (frame.shape[1] // 2, frame.shape[0] // 2)
                    )
                })
            
            items.sort(key=lambda x: x["distance"])
            return items
        except Exception as e:
            self.logger.error(f"物品检测失败: {e}")
            return []
    
    def _detect_dialog(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """检测对话框"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
            
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                if cv2.contourArea(contour) < 10000:
                    continue
                    
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                
                if 1.5 < aspect_ratio < 4:
                    close_button_x = x + w - 20
                    close_button_y = y + 20
                    
                    return {
                        "position": (x, y),
                        "size": (w, h),
                        "close_button": {
                            "position": (close_button_x, close_button_y),
                            "size": (20, 20)
                        }
                    }
            
            return None
        except Exception as e:
            self.logger.error(f"对话框检测失败: {e}")
            return None
    
    def _detect_health_mana(self, frame: np.ndarray) -> Tuple[Optional[float], Optional[float]]:
        """检测生命值和法力值"""
        try:
            height, width = frame.shape[:2]
            
            # 生命条区域
            health_roi = frame[height - 50:height - 40, 10:210]
            # 法力条区域
            mana_roi = frame[height - 30:height - 20, 10:210]
            
            # 检测红色（生命）
            hsv_health = cv2.cvtColor(health_roi, cv2.COLOR_BGR2HSV)
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            
            mask1 = cv2.inRange(hsv_health, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv_health, lower_red2, upper_red2)
            health_mask = cv2.bitwise_or(mask1, mask2)
            
            # 检测蓝色（法力）
            hsv_mana = cv2.cvtColor(mana_roi, cv2.COLOR_BGR2HSV)
            lower_blue = np.array([100, 50, 50])
            upper_blue = np.array([140, 255, 255])
            mana_mask = cv2.inRange(hsv_mana, lower_blue, upper_blue)
            
            # 计算填充比例
            health_fill = np.sum(health_mask > 0) / (health_roi.shape[0] * health_roi.shape[1])
            mana_fill = np.sum(mana_mask > 0) / (mana_roi.shape[0] * mana_roi.shape[1])
            
            health = min(100, max(0, health_fill * 100))
            mana = min(100, max(0, mana_fill * 100))
            
            return health, mana
        except Exception as e:
            self.logger.error(f"生命值法力值检测失败: {e}")
            return None, None
    
    def _detect_player_position(self, frame: np.ndarray) -> Tuple[int, int]:
        """检测玩家位置"""
        try:
            height, width = frame.shape[:2]
            return (width // 2, height // 2)
        except Exception as e:
            self.logger.error(f"玩家位置检测失败: {e}")
            return (0, 0)
    
    def _calculate_distance(self, point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
        """计算两点间距离"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    # ============= 学习和训练方法 =============
    
    def collect_ui_samples(self, screenshot: np.ndarray, roi: Tuple[int, int, int, int], 
                          name: str, num_samples: int = 10) -> None:
        """收集UI元素样本"""
        try:
            x, y, w, h = roi
            sample = screenshot[y:y + h, x:x + w]

            sample_dir = os.path.join(self.data_dir, self.game_name, "ui_samples", name)
            os.makedirs(sample_dir, exist_ok=True)

            cv2.imwrite(
                os.path.join(sample_dir, f"{len(os.listdir(sample_dir))}.png"), 
                sample
            )
            self.logger.info(f"收集UI样本: {name}")
        except Exception as e:
            self.logger.error(f"收集UI样本失败: {e}")
    
    def learn_ui_element(self, name: str, threshold: float = 0.8) -> Optional[UIElement]:
        """学习UI元素特征"""
        try:
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

            # 计算点击偏移
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
            self.logger.info(f"学习UI元素完成: {name}")
            return element
        except Exception as e:
            self.logger.error(f"学习UI元素失败: {e}")
            return None
    
    # ============= 数据管理方法 =============
    
    def save_data(self) -> None:
        """保存分析数据"""
        try:
            data_path = os.path.join(self.data_dir, self.game_name)
            os.makedirs(data_path, exist_ok=True)

            # 保存UI元素
            self._save_ui_elements(data_path)
            
            # 保存场景数据
            self._save_scenes(data_path)
            
            self.logger.info("分析数据保存完成")
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
    
    def _save_ui_elements(self, data_path: str):
        """保存UI元素数据"""
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

        with open(os.path.join(data_path, "ui_elements.json"), "w", encoding="utf-8") as f:
            json.dump(ui_data, f, indent=4, ensure_ascii=False)
    
    def _save_scenes(self, data_path: str):
        """保存场景数据"""
        scene_data = {}
        for name, scene in self.scenes.items():
            scene_path = os.path.join(data_path, "scenes")
            os.makedirs(scene_path, exist_ok=True)

            # 保存参考图像
            cv2.imwrite(
                os.path.join(scene_path, f"{name}_reference.png"), 
                scene.reference_image
            )

            # 保存特征数据
            np.save(
                os.path.join(scene_path, f"{name}_features.npy"), 
                scene.features[0]
            )

        with open(os.path.join(data_path, "scenes.json"), "w", encoding="utf-8") as f:
            json.dump(scene_data, f, indent=4, ensure_ascii=False)
    
    def _load_data(self) -> None:
        """加载分析数据"""
        try:
            data_path = os.path.join(self.data_dir, self.game_name)
            
            # 加载UI元素
            self._load_ui_elements(data_path)
            
            # 加载场景数据
            self._load_scenes(data_path)
            
            self.logger.info("分析数据加载完成")
        except Exception as e:
            self.logger.error(f"加载数据失败: {e}")
    
    def _load_ui_elements(self, data_path: str):
        """加载UI元素数据"""
        ui_elements_file = os.path.join(data_path, "ui_elements.json")
        if not os.path.exists(ui_elements_file):
            return

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
    
    def _load_scenes(self, data_path: str):
        """加载场景数据"""
        scenes_file = os.path.join(data_path, "scenes.json")
        if not os.path.exists(scenes_file):
            return

        scene_path = os.path.join(data_path, "scenes")
        if not os.path.exists(scene_path):
            return

        for file in os.listdir(scene_path):
            if file.endswith("_reference.png"):
                name = file[:-14]  # 移除"_reference.png"

                reference = cv2.imread(os.path.join(scene_path, file))
                features_file = os.path.join(scene_path, f"{name}_features.npy")
                
                if os.path.exists(features_file):
                    features = np.load(features_file)

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
    
    # ============= 兼容性方法 =============
    
    def analyze_screenshot(self, screenshot: np.ndarray) -> Dict:
        """兼容旧接口的截图分析方法"""
        return self.analyze_frame(screenshot)
    
    def extract_features(self, frame: np.ndarray) -> np.ndarray:
        """提取图像特征（深度学习）"""
        if self.model is None or self.transform is None:
            return np.array([])
        
        try:
            img_tensor = self.transform(frame)
            img_tensor = img_tensor.unsqueeze(0)
            
            with torch.no_grad():
                features = self.model(img_tensor)
                
            return features.numpy()
        except Exception as e:
            self.logger.error(f"特征提取失败: {e}")
            return np.array([])