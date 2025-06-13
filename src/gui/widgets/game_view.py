"""
游戏画面显示组件
用于显示游戏窗口的实时画面
"""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import numpy as np
import cv2
from typing import Optional

class GameView(QLabel):
    """游戏画面显示组件
    
    用于显示游戏窗口的实时画面，支持：
    1. 自动缩放以适应显示区域
    2. 多种图像格式的转换
    3. 错误处理和状态显示
    """
    
    def __init__(self, parent=None):
        """初始化游戏画面显示组件
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.setObjectName("gameView")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(640, 480)
        self.setStyleSheet("""
            QLabel#gameView {
                background-color: #000000;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 4px;
            }
        """)
        self.setText("等待游戏画面...")
        
    def update_frame(self, frame: Optional[np.ndarray]):
        """更新画面
        
        Args:
            frame: 游戏画面数据，可以是None
        """
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
            
    def resizeEvent(self, event):
        """重写大小改变事件，保持图像比例
        
        Args:
            event: 大小改变事件
        """
        super().resizeEvent(event)
        if self.pixmap():
            scaled_pixmap = self.pixmap().scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap) 