"""
图像处理服务
负责基础图像处理功能
"""
from typing import Optional, Tuple, List
import cv2
import numpy as np
from core.error_handler import ErrorHandler, ErrorCode, ErrorContext
import os

class ImageProcessor:
    """图像处理器"""
    
    def __init__(self, error_handler: ErrorHandler):
        """初始化
        
        Args:
            error_handler: 错误处理器
        """
        self.error_handler = error_handler
        
    def preprocess_image(self, image: np.ndarray) -> Optional[np.ndarray]:
        """预处理图像
        
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
                ErrorCode.IMAGE_ERROR,
                "图像预处理失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="ImageProcessor.preprocess_image"
                )
            )
            return None
            
    def find_contours(self, image: np.ndarray, 
                     min_area: int = 100) -> List[np.ndarray]:
        """查找轮廓
        
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
                ErrorCode.IMAGE_ERROR,
                "查找轮廓失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="ImageProcessor.find_contours"
                )
            )
            return []
            
    def find_circles(self, image: np.ndarray, 
                    min_radius: int = 10,
                    max_radius: int = 100) -> List[Tuple[int, int, int]]:
        """查找圆形
        
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
                ErrorCode.IMAGE_ERROR,
                "查找圆形失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="ImageProcessor.find_circles"
                )
            )
            return []
            
    def find_lines(self, image: np.ndarray,
                  min_length: int = 100) -> List[Tuple[int, int, int, int]]:
        """查找直线
        
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
                ErrorCode.IMAGE_ERROR,
                "查找直线失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="ImageProcessor.find_lines"
                )
            )
            return []
            
    def find_corners(self, image: np.ndarray,
                    max_corners: int = 100,
                    quality_level: float = 0.01,
                    min_distance: int = 10) -> List[Tuple[int, int]]:
        """查找角点
        
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
                ErrorCode.IMAGE_ERROR,
                "查找角点失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="ImageProcessor.find_corners"
                )
            )
            return []
            
    def save_debug_image(self, image: np.ndarray, 
                        filename: str,
                        debug_dir: str = "debug") -> bool:
        """保存调试图像
        
        Args:
            image: 输入图像
            filename: 文件名
            debug_dir: 调试目录
            
        Returns:
            bool: 是否成功
        """
        try:
            # 创建调试目录
            os.makedirs(debug_dir, exist_ok=True)
            
            # 保存图像
            filepath = os.path.join(debug_dir, f"{filename}.png")
            cv2.imwrite(filepath, image)
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.IMAGE_ERROR,
                "保存调试图像失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="ImageProcessor.save_debug_image"
                )
            )
            return False 