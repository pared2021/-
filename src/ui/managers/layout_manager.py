from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedWidget, QWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup, QPoint, QRect

class LayoutManager:
    """布局管理器"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.main_layout = None
        self.content_layout = None
        self.stacked_widget = None
        self.current_animation = None
        self.animation_duration = 300  # 动画持续时间（毫秒）
        
    def setup_layout(self):
        """设置主布局"""
        # 创建主布局
        self.main_layout = QVBoxLayout(self.parent.central_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建内容区布局
        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(0)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加导航栏
        self.content_layout.addWidget(self.parent.nav_bar)
        
        # 创建堆叠部件
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("""
            QStackedWidget {
                background-color: #2d2d2d;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        
        # 添加面板
        self.stacked_widget.addWidget(self.parent.window_panel)
        self.stacked_widget.addWidget(self.parent.region_panel)
        self.stacked_widget.addWidget(self.parent.template_panel)
        self.stacked_widget.addWidget(self.parent.settings_panel)
        
        self.content_layout.addWidget(self.stacked_widget)
        self.main_layout.addLayout(self.content_layout)
        
    def switch_panel(self, index):
        """切换面板"""
        if self.stacked_widget.currentIndex() == index:
            return
        
        # 如果有动画正在运行，终止它
        if self.current_animation and self.current_animation.state() == QPropertyAnimation.State.Running:
            self.current_animation.stop()
            
        # 更新按钮状态
        for i, btn in enumerate(self.parent.nav_buttons):
            btn.setChecked(i == index)
            
        # 获取当前面板和目标面板
        current_widget = self.stacked_widget.currentWidget()
        target_widget = self.stacked_widget.widget(index)
        
        # 如果要显示的面板可见，则使用淡入淡出动画
        self.stacked_widget.setCurrentIndex(index)
        
        # 创建淡入动画
        fade_in_animation = QPropertyAnimation(target_widget, b"windowOpacity")
        fade_in_animation.setDuration(self.animation_duration)
        fade_in_animation.setStartValue(0.3)
        fade_in_animation.setEndValue(1.0)
        fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 创建缩放动画
        scale_animation = QPropertyAnimation(target_widget, b"geometry")
        scale_animation.setDuration(self.animation_duration)
        target_geometry = target_widget.geometry()
        scale_animation.setStartValue(QRect(
            int(target_geometry.x() + target_geometry.width() * 0.05),
            int(target_geometry.y() + target_geometry.height() * 0.05),
            int(target_geometry.width() * 0.9),
            int(target_geometry.height() * 0.9)
        ))
        scale_animation.setEndValue(target_geometry)
        scale_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 创建并行动画组
        animation_group = QParallelAnimationGroup()
        animation_group.addAnimation(fade_in_animation)
        animation_group.addAnimation(scale_animation)
        
        # 开始动画
        self.current_animation = animation_group
        animation_group.start()
        
        # 更新状态栏
        self.parent.statusBar().showMessage(f"切换到{self.parent.nav_buttons[index].toolTip()}", 2000) 