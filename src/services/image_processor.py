import cv2
import numpy as np
import os
import time
import datetime
from typing import Dict, List, Tuple, Optional, Any
from PyQt6.QtCore import QObject, pyqtSignal
from .config import Config
from .logger import GameLogger

class ImageProcessor(QObject):
    """图像处理类，负责图像识别和处理"""
    
    # 定义信号
    processing_started = pyqtSignal()  # 处理开始信号
    processing_finished = pyqtSignal()  # 处理完成信号
    template_matched = pyqtSignal(str, list)  # 模板匹配信号
    detection_updated = pyqtSignal(dict)  # 检测更新信号
    
    def __init__(self, logger: GameLogger, config: Config):
        """初始化图像处理器
        
        Args:
            logger: 日志对象
            config: 配置对象
        """
        super().__init__()
        self.config = config
        self.logger = logger
        self.templates = {}
        
        self.logger.info("图像处理器初始化完成")
    
    def load_templates(self, templates_path: str):
        """加载模板图像
        
        Args:
            templates_path: 模板图像路径
        """
        if not os.path.exists(templates_path):
            self.logger.error(f"模板路径不存在: {templates_path}")
            raise FileNotFoundError(f"模板路径不存在: {templates_path}")
        
        self.logger.info(f"开始加载模板: {templates_path}")
        for filename in os.listdir(templates_path):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                name = os.path.splitext(filename)[0]
                path = os.path.join(templates_path, filename)
                self.templates[name] = cv2.imread(path)
                self.logger.debug(f"加载模板: {name}")
        
        self.logger.info(f"模板加载完成，共{len(self.templates)}个")
    
    def match_template(self, image: np.ndarray, template_name: str, 
                      threshold: float = None) -> List[Tuple[int, int]]:
        """模板匹配
        
        Args:
            image: 输入图像
            template_name: 模板名称
            threshold: 匹配阈值
            
        Returns:
            匹配位置列表，每个位置为(x, y)元组
        """
        if template_name not in self.templates:
            self.logger.error(f"模板不存在: {template_name}")
            return []
            
        threshold = threshold or self.config.image_processor.template_match_threshold
        self.logger.debug(f"开始模板匹配: {template_name}, 阈值: {threshold}")
        
        try:
            template = self.templates[template_name]
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)
            
            matches = []
            for pt in zip(*locations[::-1]):
                matches.append(pt)
                
            self.logger.debug(f"模板匹配完成，找到{len(matches)}个匹配")
            self.template_matched.emit(template_name, matches)
            return matches
        except Exception as e:
            self.logger.error(f"模板匹配失败: {e}")
            return []
    
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
            return matches[0]
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
                results[template_name] = matches
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
            self.logger.error(f"颜色检测失败: {e}")
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
            self.logger.error(f"分析游戏画面失败: {str(e)}")
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
            self.logger.error(f"获取主要颜色失败: {str(e)}")
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
            self.logger.error(f"计算亮度失败: {str(e)}")
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
            self.logger.error(f"检测边缘失败: {str(e)}")
            return np.zeros_like(frame[:, :, 0]) 