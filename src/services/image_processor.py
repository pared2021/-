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
from ..common.error_types import ErrorCode, ImageProcessingError, ErrorContext
from dataclasses import dataclass
from .error_handler import ErrorHandler

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
            # 验证输入图像
            if not self.validate_image_data(image):
                return None
                
            if template_name not in self.templates:
                return None
                
            template = self.templates[template_name]
            
            # 安全转换为灰度图
            def _convert_to_gray(img):
                if len(img.shape) == 3:
                    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                return img
            
            gray_image = self.safe_image_operation(_convert_to_gray, image)
            if gray_image is None:
                return None
                
            # 模板匹配
            result = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED)
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
                    ErrorCode.TEMPLATE_MATCH_ERROR,
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
            # 验证输入数据
            if not self.validate_image_data(frame):
                self.logger.warning("分析的画面数据无效")
                return {}
            
            # 获取图像尺寸
            height, width = frame.shape[:2]
            
            # 安全执行各项分析
            dominant_colors = self.safe_image_operation(self._get_dominant_colors, frame)
            brightness = self._calculate_brightness_safe(frame)
            edges = self.safe_image_operation(self._detect_edges, frame)
            
            # 创建基本状态字典
            state = {
                "timestamp": self.get_current_timestamp(),
                "frame_size": (width, height),
                "dominant_colors": dominant_colors if dominant_colors is not None else [],
                "brightness": brightness,
                "edges": edges is not None
            }
            
            return state
            
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.IMAGE_ANALYSIS_ERROR,
                    "分析游戏画面失败",
                    ErrorContext(
                        source="ImageProcessor.analyze_frame",
                        details=str(e)
                    )
                )
            )
            return {}
    
    def _calculate_brightness_safe(self, frame: np.ndarray) -> float:
        """安全计算图像亮度
        
        Args:
            frame: 输入图像
            
        Returns:
            float: 亮度值，失败时返回0.0
        """
        try:
            if not self.validate_image_data(frame):
                return 0.0
            
            # 转换为灰度图
            if frame.ndim == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
                
            # 计算平均亮度
            return float(np.mean(gray))
            
        except Exception as e:
            self.logger.error(f"安全计算亮度失败: {e}")
            return 0.0
    
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
    
    def validate_image_data(self, data: Any) -> bool:
        """验证图像数据的有效性
        
        Args:
            data: 待验证的数据
            
        Returns:
            bool: 数据是否有效
        """
        try:
            # 检查是否为None
            if data is None:
                return False
            
            # 检查是否为布尔值（错误返回）
            if isinstance(data, bool):
                self.logger.warning(f"图像数据为布尔值: {data}")
                return False
            
            # 检查是否为numpy数组
            if not isinstance(data, np.ndarray):
                self.logger.warning(f"图像数据类型错误: {type(data)}, 期望np.ndarray")
                return False
            
            # 检查数组维度
            if data.ndim not in [2, 3]:
                self.logger.warning(f"图像数组维度错误: {data.ndim}, 期望2或3维")
                return False
            
            # 检查数组大小
            if data.size == 0:
                self.logger.warning("图像数组为空")
                return False
            
            # 检查图像尺寸合理性
            if data.shape[0] < 1 or data.shape[1] < 1:
                self.logger.warning(f"图像尺寸无效: {data.shape}")
                return False
            
            # 如果是3维数组，检查通道数
            if data.ndim == 3 and data.shape[2] not in [1, 3, 4]:
                self.logger.warning(f"图像通道数错误: {data.shape[2]}, 期望1、3或4")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证图像数据时发生错误: {e}")
            return False
    
    def safe_image_operation(self, operation: callable, *args) -> Optional[np.ndarray]:
        """安全执行图像操作
        
        Args:
            operation: 图像操作函数
            *args: 操作参数
            
        Returns:
            Optional[np.ndarray]: 处理结果，失败时返回None
        """
        try:
            # 验证输入图像
            if args and not self.validate_image_data(args[0]):
                return None
            
            # 执行操作
            result = operation(*args)
            
            # 验证输出结果
            if not self.validate_image_data(result):
                self.logger.warning("图像操作返回无效结果")
                return None
            
            return result
            
        except Exception as e:
            self.logger.error(f"安全图像操作失败: {e}")
            return None
    
    def process_image(self, image: np.ndarray) -> Optional[np.ndarray]:
        """处理图像"""
        try:
            # 使用验证方法检查输入
            if not self.validate_image_data(image):
                self.error_handler.handle_error(
                    ImageProcessingError(
                        ErrorCode.IMAGE_PROCESSING_FAILED,
                        "无效的图像数据",
                        ErrorContext(
                            source="ImageProcessor.process_image",
                            details="输入图像验证失败"
                        )
                    )
                )
                return None
                
            # 使用安全操作进行图像预处理
            def _process_operation(img):
                processed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                processed = cv2.GaussianBlur(processed, (5, 5), 0)
                return processed
            
            result = self.safe_image_operation(_process_operation, image)
            
            if result is None:
                self.error_handler.handle_error(
                    ImageProcessingError(
                        ErrorCode.IMAGE_PROCESSING_FAILED,
                        "图像处理操作失败",
                        ErrorContext(
                            source="ImageProcessor.process_image",
                            details="安全图像操作返回None"
                        )
                    )
                )
            
            return result
            
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

    # === 来自vision模块的特化功能 ===
    
    def find_contours(self, image: np.ndarray, min_area: int = 100) -> List[np.ndarray]:
        """查找轮廓 - 从vision模块迁移
        
        Args:
            image: 输入图像
            min_area: 最小面积
            
        Returns:
            List[np.ndarray]: 轮廓列表
        """
        try:
            # 查找轮廓
            contours, _ = cv2.findContours(
                image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # 过滤小轮廓
            filtered_contours = [
                cnt for cnt in contours 
                if cv2.contourArea(cnt) > min_area
            ]
            
            return filtered_contours
            
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.IMAGE_ERROR,
                    "查找轮廓失败",
                    ErrorContext(
                        error_info=str(e),
                        error_location="ImageProcessor.find_contours"
                    )
                )
            )
            return []
    
    def find_circles(self, image: np.ndarray, 
                    min_radius: int = 10,
                    max_radius: int = 100) -> List[Tuple[int, int, int]]:
        """查找圆形 - 从vision模块迁移
        
        Args:
            image: 输入图像
            min_radius: 最小半径
            max_radius: 最大半径
            
        Returns:
            List[Tuple[int, int, int]]: 圆形列表 (x, y, radius)
        """
        try:
            # 查找圆形
            circles = cv2.HoughCircles(
                image, cv2.HOUGH_GRADIENT, 1, 20,
                param1=50, param2=30,
                minRadius=min_radius, maxRadius=max_radius
            )
            
            if circles is None:
                return []
                
            # 转换为整数坐标
            circles = np.uint16(np.around(circles))
            return [(x, y, r) for x, y, r in circles[0, :]]
            
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.IMAGE_ERROR,
                    "查找圆形失败",
                    ErrorContext(
                        error_info=str(e),
                        error_location="ImageProcessor.find_circles"
                    )
                )
            )
            return []
    
    def find_lines(self, image: np.ndarray,
                  min_length: int = 100) -> List[Tuple[int, int, int, int]]:
        """查找直线 - 从vision模块迁移
        
        Args:
            image: 输入图像
            min_length: 最小长度
            
        Returns:
            List[Tuple[int, int, int, int]]: 直线列表 (x1, y1, x2, y2)
        """
        try:
            # 查找直线
            lines = cv2.HoughLinesP(
                image, 1, np.pi/180, 100,
                minLineLength=min_length, maxLineGap=10
            )
            
            if lines is None:
                return []
                
            return [(x1, y1, x2, y2) for x1, y1, x2, y2 in lines[:, 0]]
            
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.IMAGE_ERROR,
                    "查找直线失败",
                    ErrorContext(
                        error_info=str(e),
                        error_location="ImageProcessor.find_lines"
                    )
                )
            )
            return []
    
    def find_corners(self, image: np.ndarray,
                    max_corners: int = 100,
                    quality_level: float = 0.01,
                    min_distance: int = 10) -> List[Tuple[int, int]]:
        """查找角点 - 从vision模块迁移
        
        Args:
            image: 输入图像
            max_corners: 最大角点数
            quality_level: 质量等级
            min_distance: 最小距离
            
        Returns:
            List[Tuple[int, int]]: 角点列表 (x, y)
        """
        try:
            # 查找角点
            corners = cv2.goodFeaturesToTrack(
                image, max_corners, quality_level, min_distance
            )
            
            if corners is None:
                return []
                
            # 转换为整数坐标
            corners = np.int0(corners)
            return [(x, y) for x, y in corners.reshape(-1, 2)]
            
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.IMAGE_ERROR,
                    "查找角点失败",
                    ErrorContext(
                        error_info=str(e),
                        error_location="ImageProcessor.find_corners"
                    )
                )
            )
            return []
    
    def save_debug_image(self, image: np.ndarray, 
                        filename: str,
                        debug_dir: str = "debug") -> bool:
        """保存调试图像 - 从vision模块迁移
        
        Args:
            image: 输入图像
            filename: 文件名
            debug_dir: 调试目录
            
        Returns:
            bool: 是否成功
        """
        try:
            # 创建调试目录
            import os
            os.makedirs(debug_dir, exist_ok=True)
            
            # 保存图像
            filepath = os.path.join(debug_dir, f"{filename}.png")
            cv2.imwrite(filepath, image)
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.IMAGE_ERROR,
                    "保存调试图像失败",
                    ErrorContext(
                        error_info=str(e),
                        error_location="ImageProcessor.save_debug_image"
                    )
                )
            )
            return False
    
    def preprocess_image_advanced(self, image: np.ndarray) -> Optional[np.ndarray]:
        """高级图像预处理 - 从vision模块迁移
        
        Args:
            image: 输入图像
            
        Returns:
            Optional[np.ndarray]: 处理后的图像
        """
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 高斯模糊
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # 自适应阈值
            thresh = cv2.adaptiveThreshold(
                blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            return thresh
            
        except Exception as e:
            self.error_handler.handle_error(
                ImageProcessingError(
                    ErrorCode.IMAGE_ERROR,
                    "高级图像预处理失败",
                    ErrorContext(
                        error_info=str(e),
                        error_location="ImageProcessor.preprocess_image_advanced"
                    )
                )
            )
            return None