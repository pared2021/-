from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import numpy as np
import cv2

class GameView(QLabel):
    """游戏画面显示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(640, 480)
        self.setStyleSheet("background-color: black;")
        self.setText("等待游戏画面...")
        
    def update_frame(self, frame: np.ndarray):
        """更新画面"""
        if frame is None:
            self.setText("无法获取游戏画面")
            return
            
        # 如果收到布尔值或其他非数组类型，处理错误
        if not isinstance(frame, np.ndarray):
            self.setText(f"画面格式错误: {type(frame)}")
            return
            
        if frame.size == 0:
            self.setText("画面数据为空")
            return
            
        try:
            # 确保图像是RGB格式 (OpenCV使用BGR)
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # 转换BGR到RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                # 尝试处理其他类型的图像
                if len(frame.shape) == 2:  # 灰度图
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
                elif len(frame.shape) == 3 and frame.shape[2] == 4:  # BGRA
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
                else:
                    rgb_frame = frame  # 直接使用，可能会出现颜色问题
                
            # 转换图像为Qt图像
            height, width = rgb_frame.shape[:2]
            bytes_per_line = 3 * width
            q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            # 缩放图像以适应标签大小
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
        except Exception as e:
            self.setText(f"处理图像时出错: {str(e)}") 