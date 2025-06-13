from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QImage, QBrush
from .styles import PANEL_STYLE

class DisplayPanel(QWidget):
    """显示面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.detections = {}
    
    def setup_ui(self):
        """设置界面"""
        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("游戏画面")
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                padding: 5px 0;
            }
        """)
        main_layout.addWidget(title_label)
        
        # 游戏画面容器
        display_frame = QFrame()
        display_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-radius: 10px;
                border: 1px solid #333333;
                padding: 5px;
            }
        """)
        display_layout = QVBoxLayout(display_frame)
        display_layout.setContentsMargins(5, 5, 5, 5)
        
        # 游戏画面显示区域
        image_frame = QFrame()
        image_frame.setStyleSheet("""
            QFrame {
                background-color: #0f0f0f;
                border-radius: 5px;
                border: 1px solid #222222;
            }
        """)
        image_layout = QVBoxLayout(image_frame)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        # 游戏画面标签
        self.game_label = QLabel()
        self.game_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.game_label.setMinimumSize(640, 480)
        self.game_label.setStyleSheet("""
            QLabel {
                background-color: #000000;
                border-radius: 5px;
            }
        """)
        
        image_layout.addWidget(self.game_label)
        display_layout.addWidget(image_frame)
        
        # 状态栏
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-radius: 5px;
                padding: 5px;
                max-height: 30px;
            }
        """)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 0, 10, 0)
        
        self.resolution_label = QLabel("分辨率: 未知")
        self.resolution_label.setStyleSheet("color: #aaaaaa;")
        
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setStyleSheet("color: #aaaaaa;")
        
        status_layout.addWidget(self.resolution_label)
        status_layout.addStretch()
        status_layout.addWidget(self.fps_label)
        
        display_layout.addWidget(status_frame)
        
        # 添加到主布局
        main_layout.addWidget(display_frame)
    
    def update_screenshot(self, screenshot):
        """更新截图显示"""
        if screenshot is None:
            return
            
        # 转换为QPixmap
        height, width = screenshot.shape[:2]
        bytes_per_line = 3 * width
        q_image = QImage(screenshot.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        # 保持纵横比缩放到显示区域
        scaled_pixmap = pixmap.scaled(
            self.game_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # 显示截图
        self.game_label.setPixmap(scaled_pixmap)
        
        # 更新分辨率显示
        self.resolution_label.setText(f"分辨率: {width}x{height}")
    
    def update_detections(self, detections):
        """更新检测结果显示"""
        self.detections = detections
        self.update()
    
    def paintEvent(self, event):
        """绘制事件"""
        super().paintEvent(event)
        
        # 如果有检测结果，绘制标记
        if self.detections:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # 绘制物体检测框
            for obj in self.detections.get('objects', []):
                x = obj['x']
                y = obj['y']
                w = obj['width']
                h = obj['height']
                
                # 使用不同的颜色表示不同类型的物体
                if 'class' in obj:
                    if obj['class'] == 'target':
                        color = QColor(0, 255, 0, 200)  # 绿色，目标
                    elif obj['class'] == 'enemy':
                        color = QColor(255, 0, 0, 200)  # 红色，敌人
                    elif obj['class'] == 'item':
                        color = QColor(0, 0, 255, 200)  # 蓝色，物品
                    else:
                        color = QColor(255, 255, 0, 200)  # 黄色，其他
                else:
                    color = QColor(0, 255, 0, 200)  # 默认绿色
                
                # 设置画笔
                pen = QPen(color, 2)
                painter.setPen(pen)
                
                # 绘制矩形框
                painter.drawRect(x, y, w, h)
                
                # 绘制类别标签背景
                label_text = obj.get('class', 'unknown')
                text_width = painter.fontMetrics().horizontalAdvance(label_text) + 10
                text_height = painter.fontMetrics().height() + 5
                
                label_rect = QColor(color)
                label_rect.setAlpha(180)
                painter.setBrush(QBrush(label_rect))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(x, y - text_height, text_width, text_height)
                
                # 绘制文本
                painter.setPen(QPen(Qt.GlobalColor.white))
                painter.drawText(x + 5, y - 5, label_text)
                
                # 如果有置信度，显示置信度
                if 'confidence' in obj:
                    conf_text = f"{obj['confidence']:.2f}"
                    conf_width = painter.fontMetrics().horizontalAdvance(conf_text) + 10
                    
                    conf_rect = QColor(color)
                    conf_rect.setAlpha(180)
                    painter.setBrush(QBrush(conf_rect))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawRect(x + w - conf_width, y - text_height, conf_width, text_height)
                    
                    painter.setPen(QPen(Qt.GlobalColor.white))
                    painter.drawText(x + w - conf_width + 5, y - 5, conf_text)
                
            painter.end()
    
    def set_mouse_events(self, press_handler, move_handler, release_handler):
        """设置鼠标事件处理器"""
        self.game_label.mousePressEvent = press_handler
        self.game_label.mouseMoveEvent = move_handler
        self.game_label.mouseReleaseEvent = release_handler
    
    def update_frame(self, pixmap: QPixmap):
        """更新游戏画面"""
        if pixmap:
            # 保持纵横比缩放到显示区域
            scaled_pixmap = pixmap.scaled(
                self.game_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.game_label.setPixmap(scaled_pixmap)
    
    def update_fps(self, fps):
        """更新FPS显示"""
        self.fps_label.setText(f"FPS: {fps:.1f}")
        # 根据FPS值改变颜色
        if fps >= 30:
            self.fps_label.setStyleSheet("color: #00ff00;")  # 绿色
        elif fps >= 15:
            self.fps_label.setStyleSheet("color: #ffff00;")  # 黄色
        else:
            self.fps_label.setStyleSheet("color: #ff0000;")  # 红色
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        # 如果有当前显示的图像，重新缩放
        if self.game_label.pixmap():
            self.update_frame(self.game_label.pixmap()) 