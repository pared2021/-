"""
图像处理服务
负责图像的分析、处理和模板匹配
"""
import cv2
import numpy as np
import os
import time
import datetime
from typing import Dict, List, Tuple, Optional, Any
from PyQt6.QtCore import QObject, pyqtSignal
from .config import Config
from .logger import GameLogger
from src.common.error_types import ErrorCode, ImageProcessingError, ErrorContext
from dataclasses import dataclass
from src.services.error_handler import ErrorHandler

@dataclass
class TemplateMatchResult:
    """模板匹配结果"""
    location: Tuple[int, int]
    confidence: float
    template_name: str
    template_size: Tuple[int, int]

class ImageProcessor(QObject):
    """图像处理类，负责图像识别和处理"""
    
    # 定义信号
    processing_started = pyqtSignal()  # 处理开始信号
    processing_finished = pyqtSignal()  # 处理完成信号
    template_matched = pyqtSignal(str, list)  # 模板匹配信号
    detection_updated = pyqtSignal(dict)  # 检测更新信号
    
    def __init__(self, logger: GameLogger, config: Config, error_handler: ErrorHandler):
        """初始化图像处理器
        
        Args:
            logger: 日志对象
            config: 配置对象
            error_handler: 错误处理对象
        """
        super().__init__()
        self.config = config
        self.logger = logger
        self.error_handler = error_handler
        self.templates: Dict[str, np.ndarray] = {}
        self.template_configs: Dict[str, Dict] = {}
        self.is_initialized = False
        
        self.logger.info("图像处理器初始化完成")
    
    def initialize(self) -> bool:
        """初始化图像处理器"""
        try:
            self.is_initialized = True
            return True
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.IMAGE_PROCESSOR_INIT_FAILED,
                    "图像处理器初始化失败",
                    ErrorContext(
                        source="ImageProcessor.initialize",
                        details=str(e)
                    )
                )
            )
            return False
    
    def load_template(self, name: str, image: np.ndarray, config: Dict = None) -> bool:
        """加载模板
        
        Args:
            name: 模板名称
            image: 模板图像
            config: 模板配置
            
        Returns:
            bool: 是否成功
        """
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
            self.templates[name] = image
            self.template_configs[name] = config or {}
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.IMAGE_ERROR,
                    "加载模板失败",
                    ErrorContext(
                        error_info=str(e),
                        error_location="ImageProcessor.load_template",
                        template_name=name
                    )
                )
            )
            return False
            
    def load_template_from_file(self, name: str, file_path: str, config: Dict = None) -> bool:
        """从文件加载模板
        
        Args:
            name: 模板名称
            file_path: 模板文件路径
            config: 模板配置
            
        Returns:
            bool: 是否成功
        """
        try:
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"无法读取模板文件: {file_path}")
                
            return self.load_template(name, image, config)
            
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.IMAGE_ERROR,
                    "从文件加载模板失败",
                    ErrorContext(
                        error_info=str(e),
                        error_location="ImageProcessor.load_template_from_file",
                        template_name=name,
                        file_path=file_path
                    )
                )
            )
            return False
    
    def match_template(self, image: np.ndarray, template_name: str, threshold: float = 0.8) -> Optional[TemplateMatchResult]:
        """匹配模板
        
        Args:
            image: 待匹配图像
            template_name: 模板名称
            threshold: 匹配阈值
            
        Returns:
            Optional[TemplateMatchResult]: 匹配结果
        """
        try:
            if template_name not in self.templates:
                return None
                
            template = self.templates[template_name]
            
            # 转换为灰度图
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
            # 模板匹配
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                return TemplateMatchResult(
                    location=max_loc,
                    confidence=max_val,
                    template_name=template_name,
                    template_size=template.shape[::-1]
                )
            return None
            
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.IMAGE_ERROR,
                    "模板匹配失败",
                    ErrorContext(
                        error_info=str(e),
                        error_location="ImageProcessor.match_template",
                        template_name=template_name
                    )
                )
            )
            return None
            
    def match_all_templates(self, image: np.ndarray, threshold: float = 0.8) -> List[TemplateMatchResult]:
        """匹配所有模板
        
        Args:
            image: 待匹配图像
            threshold: 匹配阈值
            
        Returns:
            List[TemplateMatchResult]: 匹配结果列表
        """
        results = []
        for template_name in self.templates:
            result = self.match_template(image, template_name, threshold)
            if result:
                results.append(result)
        return results
    
    def find_template(self, image: np.ndarray, template_name: str, 
                     threshold: float = None) -> Optional[Tuple[int, int]]:
        """查找模板位置
        
        Args:
            image: 输入图像
            template_name: 模板名称
            threshold: 匹配阈值
            
        Returns:
            最佳匹配位置，如果未找到则返回None
        """
        matches = self.match_template(image, template_name, threshold)
        if matches:
            return matches.location
        return None
    
    def find_all_templates(self, image: np.ndarray, threshold: float = None) -> Dict[str, List[Tuple[int, int]]]:
        """查找所有模板位置
        
        Args:
            image: 输入图像
            threshold: 匹配阈值
            
        Returns:
            模板位置字典，键为模板名，值为位置列表
        """
        results = {}
        for template_name in self.templates:
            matches = self.match_template(image, template_name, threshold)
            if matches:
                results[template_name] = [matches.location]
        return results
    
    def color_detect(self, image: np.ndarray, lower_color: Tuple[int, int, int], 
                    upper_color: Tuple[int, int, int]) -> List[Tuple[int, int, int, int]]:
        """颜色检测
        
        Args:
            image: 输入图像
            lower_color: 颜色下限
            upper_color: 颜色上限
            
        Returns:
            检测到的区域列表，每个区域为(x, y, w, h)元组
        """
        try:
            # 转换为HSV颜色空间
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 创建掩码
            mask = cv2.inRange(hsv, np.array(lower_color), np.array(upper_color))
            
            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 提取边界框
            boxes = []
            for contour in contours:
                # 过滤掉过小的区域
                if cv2.contourArea(contour) < 100:
                    continue
                    
                # 获取边界框
                x, y, w, h = cv2.boundingRect(contour)
                boxes.append((x, y, w, h))
                
            return boxes
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.COLOR_DETECTION_FAILED,
                    "颜色检测失败",
                    ErrorContext(
                        source="ImageProcessor.color_detect",
                        details=str(e)
                    )
                )
            )
            return []
            
    def get_current_timestamp(self) -> float:
        """获取当前时间戳"""
        return time.time()
        
    def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """分析游戏画面，提取基本特征
        
        Args:
            frame: 游戏画面
            
        Returns:
            包含图像特征的状态字典
        """
        try:
            if frame is None:
                self.logger.warning("分析的画面为空")
                return {}
            
            # 获取图像尺寸
            height, width = frame.shape[:2]
            
            # 创建基本状态字典
            state = {
                "timestamp": self.get_current_timestamp(),
                "frame_size": (width, height),
                "dominant_colors": self._get_dominant_colors(frame),
                "brightness": self._calculate_brightness(frame),
                "edges": self._detect_edges(frame)
            }
            
            return state
            
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.ANALYSIS_FAILED,
                    "分析游戏画面失败",
                    ErrorContext(
                        source="ImageProcessor.analyze_frame",
                        details=str(e)
                    )
                )
            )
            return {}
    
    def _get_dominant_colors(self, frame: np.ndarray, n_colors: int = 5) -> List[Tuple[int, int, int]]:
        """获取图像中主要颜色
        
        Args:
            frame: 输入图像
            n_colors: 返回的主要颜色数量
            
        Returns:
            主要颜色列表，每个颜色为BGR格式
        """
        try:
            # 将图像转换为浮点型并归一化
            pixels = frame.reshape(-1, 3).astype(np.float32)
            
            # 使用K-means聚类获取主要颜色
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            _, labels, centers = cv2.kmeans(pixels, n_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # 将颜色中心转换为整数并排序
            centers = centers.astype(np.uint8)
            colors = [(int(c[0]), int(c[1]), int(c[2])) for c in centers]
            
            return colors
            
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.DOMINANT_COLOR_DETECTION_FAILED,
                    "获取主要颜色失败",
                    ErrorContext(
                        source="ImageProcessor._get_dominant_colors",
                        details=str(e)
                    )
                )
            )
            return []
    
    def _calculate_brightness(self, frame: np.ndarray) -> float:
        """计算图像亮度
        
        Args:
            frame: 输入图像
            
        Returns:
            亮度值，范围0-255
        """
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 计算平均亮度
            return float(np.mean(gray))
            
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.BRIGHTNESS_CALCULATION_FAILED,
                    "计算亮度失败",
                    ErrorContext(
                        source="ImageProcessor._calculate_brightness",
                        details=str(e)
                    )
                )
            )
            return 0.0
    
    def _detect_edges(self, frame: np.ndarray) -> np.ndarray:
        """检测图像边缘
        
        Args:
            frame: 输入图像
            
        Returns:
            边缘图像
        """
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 使用Canny算法检测边缘
            edges = cv2.Canny(gray, 50, 150)
            return edges
            
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.EDGE_DETECTION_FAILED,
                    "检测边缘失败",
                    ErrorContext(
                        source="ImageProcessor._detect_edges",
                        details=str(e)
                    )
                )
            )
            return np.zeros_like(frame[:, :, 0])
    
    def process_image(self, image: np.ndarray) -> Optional[np.ndarray]:
        """处理图像"""
        try:
            if image is None or not isinstance(image, np.ndarray):
                self.error_handler.handle_error(
                    ImageProcessingError(
                        ErrorCode.INVALID_IMAGE,
                        "无效的图像数据",
                        ErrorContext(
                            source="ImageProcessor.process_image",
                            details="image is None or not numpy array"
                        )
                    )
                )
                return None
                
            # 图像预处理
            processed = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            processed = cv2.GaussianBlur(processed, (5, 5), 0)
            
            return processed
            
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.IMAGE_PROCESSING_FAILED,
                    "图像处理失败",
                    ErrorContext(
                        source="ImageProcessor.process_image",
                        details=str(e)
                    )
                )
            )
            return None
    
    def cleanup(self) -> None:
        """清理资源"""
        self.templates.clear()
        self.template_configs.clear()
        self.is_initialized = False 