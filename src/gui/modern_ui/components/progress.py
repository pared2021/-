"""现代化进度条组件"""

from typing import Optional, Union
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QProgressBar,
    QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QPaintEvent, QColor, QLinearGradient, QBrush, QPen

from .base import BaseComponent
from .typography import Typography
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_tokens import ComponentSize, ComponentVariant, design_tokens
from style_generator import style_generator


class ProgressBar(BaseComponent):
    """现代化进度条组件"""
    
    # 进度条信号
    value_changed = pyqtSignal(int)
    finished = pyqtSignal()
    
    def __init__(
        self,
        value: int = 0,
        minimum: int = 0,
        maximum: int = 100,
        size: ComponentSize = ComponentSize.MEDIUM,
        variant: ComponentVariant = ComponentVariant.PRIMARY,
        show_text: bool = True,
        show_percentage: bool = True,
        animated: bool = True,
        striped: bool = False,
        indeterminate: bool = False,
        parent: Optional[QWidget] = None
    ):
        # 进度条特有属性
        self._value = value
        self._minimum = minimum
        self._maximum = maximum
        self._show_text = show_text
        self._show_percentage = show_percentage
        self._animated = animated
        self._striped = striped
        self._indeterminate = indeterminate
        
        # 内部组件
        self._progress_widget: Optional[QProgressBar] = None
        self._text_widget: Optional[Typography] = None
        
        # 布局
        self._main_layout: Optional[QVBoxLayout] = None
        
        # 动画
        self._animation: Optional[QPropertyAnimation] = None
        self._stripe_timer: Optional[QTimer] = None
        self._stripe_offset = 0
        
        super().__init__(size, variant, False, parent)
    
    def setup_ui(self):
        """设置UI"""
        # 主布局
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(design_tokens.get_spacing('1'))
        
        # 创建进度条
        self._setup_progress_bar()
        
        # 创建文本显示
        if self._show_text:
            self._setup_text()
        
        # 设置动画
        if self._animated:
            self._setup_animation()
        
        # 设置条纹动画
        if self._striped:
            self._setup_stripe_animation()
    
    def _setup_progress_bar(self):
        """设置进度条"""
        self._progress_widget = QProgressBar()
        self._progress_widget.setMinimum(self._minimum)
        self._progress_widget.setMaximum(self._maximum)
        self._progress_widget.setValue(self._value)
        
        # 不确定状态
        if self._indeterminate:
            self._progress_widget.setMinimum(0)
            self._progress_widget.setMaximum(0)
        
        # 隐藏默认文本
        self._progress_widget.setTextVisible(False)
        
        self._main_layout.addWidget(self._progress_widget)
    
    def _setup_text(self):
        """设置文本显示"""
        text = self._get_display_text()
        
        self._text_widget = Typography(
            text=text,
            variant='body',
            size='small',
            color='text.secondary'
        )
        self._main_layout.addWidget(self._text_widget)
    
    def _setup_animation(self):
        """设置动画"""
        self._animation = QPropertyAnimation(self._progress_widget, b"value")
        self._animation.setDuration(300)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def _setup_stripe_animation(self):
        """设置条纹动画"""
        self._stripe_timer = QTimer()
        self._stripe_timer.timeout.connect(self._update_stripe)
        self._stripe_timer.start(100)  # 100ms 间隔
    
    def _update_stripe(self):
        """更新条纹偏移"""
        self._stripe_offset = (self._stripe_offset + 1) % 20
        self.update_style()
    
    def _get_display_text(self) -> str:
        """获取显示文本"""
        if self._indeterminate:
            return "处理中..."
        
        if self._show_percentage:
            if self._maximum > self._minimum:
                percentage = int((self._value - self._minimum) / (self._maximum - self._minimum) * 100)
                return f"{percentage}%"
            else:
                return "0%"
        else:
            return f"{self._value}/{self._maximum}"
    
    def setup_connections(self):
        """设置信号连接"""
        if self._progress_widget:
            self._progress_widget.valueChanged.connect(self._handle_value_changed)
    
    def _handle_value_changed(self, value: int):
        """处理值变化"""
        self._value = value
        
        # 更新文本
        if self._text_widget:
            self._text_widget.text = self._get_display_text()
        
        # 发射信号
        self.value_changed.emit(value)
        
        # 检查是否完成
        if value >= self._maximum:
            self.finished.emit()
    
    def update_style(self):
        """更新样式"""
        if not self._progress_widget:
            return
        
        # 生成样式缓存键
        style_key = self._generate_style_key(
            striped=self._striped,
            indeterminate=self._indeterminate,
            stripe_offset=self._stripe_offset if self._striped else 0
        )
        
        # 检查缓存
        cached_style = self._get_cached_style(style_key)
        if cached_style:
            self._progress_widget.setStyleSheet(cached_style)
            return
        
        # 生成新样式
        style = style_generator.generate_progress_style(
            size=self._size,
            variant=self._variant
        )
        
        # 缓存并应用样式
        self._cache_style(style_key, style)
        self._progress_widget.setStyleSheet(style)
    
    # 进度控制方法
    def set_value(self, value: int, animated: bool = None):
        """设置进度值"""
        if animated is None:
            animated = self._animated
        
        if animated and self._animation and not self._indeterminate:
            self._animation.setStartValue(self._progress_widget.value())
            self._animation.setEndValue(value)
            self._animation.start()
        else:
            if self._progress_widget:
                self._progress_widget.setValue(value)
    
    def increment(self, step: int = 1):
        """增加进度"""
        new_value = min(self._value + step, self._maximum)
        self.set_value(new_value)
    
    def decrement(self, step: int = 1):
        """减少进度"""
        new_value = max(self._value - step, self._minimum)
        self.set_value(new_value)
    
    def reset(self):
        """重置进度"""
        self.set_value(self._minimum)
    
    def complete(self):
        """完成进度"""
        self.set_value(self._maximum)
    
    def start_indeterminate(self):
        """开始不确定状态"""
        if not self._indeterminate:
            self._indeterminate = True
            if self._progress_widget:
                self._progress_widget.setMinimum(0)
                self._progress_widget.setMaximum(0)
            if self._text_widget:
                self._text_widget.text = "处理中..."
    
    def stop_indeterminate(self):
        """停止不确定状态"""
        if self._indeterminate:
            self._indeterminate = False
            if self._progress_widget:
                self._progress_widget.setMinimum(self._minimum)
                self._progress_widget.setMaximum(self._maximum)
                self._progress_widget.setValue(self._value)
            if self._text_widget:
                self._text_widget.text = self._get_display_text()
    
    # 属性访问器
    @property
    def value(self) -> int:
        """当前值"""
        return self._value
    
    @value.setter
    def value(self, value: int):
        """设置当前值"""
        self.set_value(value)
    
    @property
    def minimum(self) -> int:
        """最小值"""
        return self._minimum
    
    @minimum.setter
    def minimum(self, value: int):
        """设置最小值"""
        self._minimum = value
        if self._progress_widget and not self._indeterminate:
            self._progress_widget.setMinimum(value)
    
    @property
    def maximum(self) -> int:
        """最大值"""
        return self._maximum
    
    @maximum.setter
    def maximum(self, value: int):
        """设置最大值"""
        self._maximum = value
        if self._progress_widget and not self._indeterminate:
            self._progress_widget.setMaximum(value)
    
    @property
    def percentage(self) -> float:
        """百分比"""
        if self._maximum > self._minimum:
            return (self._value - self._minimum) / (self._maximum - self._minimum) * 100
        return 0.0
    
    @property
    def indeterminate(self) -> bool:
        """是否不确定状态"""
        return self._indeterminate
    
    @indeterminate.setter
    def indeterminate(self, value: bool):
        """设置不确定状态"""
        if value:
            self.start_indeterminate()
        else:
            self.stop_indeterminate()
    
    @property
    def striped(self) -> bool:
        """是否条纹"""
        return self._striped
    
    @striped.setter
    def striped(self, value: bool):
        """设置条纹"""
        if self._striped != value:
            self._striped = value
            if value and not self._stripe_timer:
                self._setup_stripe_animation()
            elif not value and self._stripe_timer:
                self._stripe_timer.stop()
                self._stripe_timer = None
            self.update_style()


class CircularProgress(BaseComponent):
    """圆形进度条"""
    
    # 进度条信号
    value_changed = pyqtSignal(int)
    finished = pyqtSignal()
    
    def __init__(
        self,
        value: int = 0,
        minimum: int = 0,
        maximum: int = 100,
        size: ComponentSize = ComponentSize.MEDIUM,
        variant: ComponentVariant = ComponentVariant.PRIMARY,
        thickness: int = 8,
        show_text: bool = True,
        animated: bool = True,
        parent: Optional[QWidget] = None
    ):
        # 圆形进度条特有属性
        self._value = value
        self._minimum = minimum
        self._maximum = maximum
        self._thickness = thickness
        self._show_text = show_text
        self._animated = animated
        
        # 动画属性
        self._animated_value = value
        self._animation: Optional[QPropertyAnimation] = None
        
        super().__init__(size, variant, False, parent)
        
        # 设置固定尺寸
        self._setup_size()
    
    def _setup_size(self):
        """设置尺寸"""
        size_map = {
            ComponentSize.SMALL: 60,
            ComponentSize.MEDIUM: 80,
            ComponentSize.LARGE: 120
        }
        
        size = size_map.get(self._size, 80)
        self.setFixedSize(size, size)
    
    def setup_ui(self):
        """设置UI"""
        # 设置动画
        if self._animated:
            self._setup_animation()
    
    def _setup_animation(self):
        """设置动画"""
        self._animation = QPropertyAnimation(self, b"animatedValue")
        self._animation.setDuration(500)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def setup_connections(self):
        """设置信号连接"""
        pass
    
    def update_style(self):
        """更新样式"""
        # 圆形进度条使用自定义绘制，不需要样式表
        pass
    
    def paintEvent(self, event: QPaintEvent):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 获取绘制区域
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2 - self._thickness
        
        # 获取颜色
        bg_color = QColor(design_tokens.get_color('surface', 'default'))
        progress_color = QColor(design_tokens.get_color('primary', '500'))
        text_color = QColor(design_tokens.get_color('text', 'primary'))
        
        # 绘制背景圆环
        painter.setPen(QPen(bg_color, self._thickness))
        painter.drawEllipse(center, radius, radius)
        
        # 计算进度角度
        if self._maximum > self._minimum:
            progress = (self._animated_value - self._minimum) / (self._maximum - self._minimum)
        else:
            progress = 0
        
        angle = int(progress * 360 * 16)  # Qt uses 1/16th of a degree
        
        # 绘制进度圆环
        if angle > 0:
            painter.setPen(QPen(progress_color, self._thickness, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawArc(
                center.x() - radius, center.y() - radius,
                radius * 2, radius * 2,
                90 * 16, -angle  # 从顶部开始，顺时针
            )
        
        # 绘制文本
        if self._show_text:
            painter.setPen(text_color)
            font = painter.font()
            font.setPointSize(self._get_font_size())
            painter.setFont(font)
            
            percentage = int(progress * 100)
            text = f"{percentage}%"
            
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
    
    def _get_font_size(self) -> int:
        """获取字体大小"""
        size_map = {
            ComponentSize.SMALL: 10,
            ComponentSize.MEDIUM: 12,
            ComponentSize.LARGE: 16
        }
        return size_map.get(self._size, 12)
    
    # 动画属性
    @pyqtProperty(float)
    def animatedValue(self) -> float:
        """动画值属性"""
        return self._animated_value
    
    @animatedValue.setter
    def animatedValue(self, value: float):
        """设置动画值"""
        self._animated_value = value
        self.update()
    
    # 进度控制方法
    def set_value(self, value: int, animated: bool = None):
        """设置进度值"""
        if animated is None:
            animated = self._animated
        
        old_value = self._value
        self._value = value
        
        if animated and self._animation:
            self._animation.setStartValue(self._animated_value)
            self._animation.setEndValue(value)
            self._animation.start()
        else:
            self._animated_value = value
            self.update()
        
        # 发射信号
        if old_value != value:
            self.value_changed.emit(value)
            
            if value >= self._maximum:
                self.finished.emit()
    
    # 属性访问器
    @property
    def value(self) -> int:
        """当前值"""
        return self._value
    
    @value.setter
    def value(self, value: int):
        """设置当前值"""
        self.set_value(value)
    
    @property
    def minimum(self) -> int:
        """最小值"""
        return self._minimum
    
    @minimum.setter
    def minimum(self, value: int):
        """设置最小值"""
        self._minimum = value
        self.update()
    
    @property
    def maximum(self) -> int:
        """最大值"""
        return self._maximum
    
    @maximum.setter
    def maximum(self, value: int):
        """设置最大值"""
        self._maximum = value
        self.update()
    
    @property
    def percentage(self) -> float:
        """百分比"""
        if self._maximum > self._minimum:
            return (self._value - self._minimum) / (self._maximum - self._minimum) * 100
        return 0.0


class StepProgress(BaseComponent):
    """步骤进度条"""
    
    # 步骤进度条信号
    step_changed = pyqtSignal(int)
    step_clicked = pyqtSignal(int)
    
    def __init__(
        self,
        steps: list[str],
        current_step: int = 0,
        size: ComponentSize = ComponentSize.MEDIUM,
        variant: ComponentVariant = ComponentVariant.PRIMARY,
        clickable: bool = False,
        parent: Optional[QWidget] = None
    ):
        # 步骤进度条特有属性
        self._steps = steps
        self._current_step = current_step
        self._clickable = clickable
        
        # 内部组件
        self._step_widgets: list[QWidget] = []
        self._line_widgets: list[QFrame] = []
        
        # 布局
        self._main_layout: Optional[QHBoxLayout] = None
        
        super().__init__(size, variant, False, parent)
    
    def setup_ui(self):
        """设置UI"""
        # 主布局
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        # 创建步骤
        for i, step_text in enumerate(self._steps):
            # 创建步骤组件
            step_widget = self._create_step_widget(i, step_text)
            self._step_widgets.append(step_widget)
            self._main_layout.addWidget(step_widget)
            
            # 创建连接线（除了最后一个步骤）
            if i < len(self._steps) - 1:
                line_widget = self._create_line_widget(i)
                self._line_widgets.append(line_widget)
                self._main_layout.addWidget(line_widget)
    
    def _create_step_widget(self, index: int, text: str) -> QWidget:
        """创建步骤组件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(design_tokens.get_spacing('1'))
        
        # 步骤圆圈
        circle = QLabel(str(index + 1))
        circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        circle.setFixedSize(32, 32)
        circle.setObjectName(f"step_circle_{index}")
        
        # 步骤文本
        label = Typography(
            text=text,
            variant='body',
            size='small',
            color='text.secondary'
        )
        label.alignment = Qt.AlignmentFlag.AlignCenter
        
        layout.addWidget(circle)
        layout.addWidget(label)
        
        # 点击事件
        if self._clickable:
            def click_handler():
                self.step_clicked.emit(index)
            
            widget.mousePressEvent = lambda event: click_handler()
            widget.setCursor(Qt.CursorShape.PointingHandCursor)
        
        return widget
    
    def _create_line_widget(self, index: int) -> QFrame:
        """创建连接线"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(2)
        line.setObjectName(f"step_line_{index}")
        
        return line
    
    def setup_connections(self):
        """设置信号连接"""
        pass
    
    def update_style(self):
        """更新样式"""
        # 直接使用design_tokens对象获取颜色
        primary_color = design_tokens.get_color('primary', '500')
        surface_color = design_tokens.get_color('background', 'surface')
        text_secondary_color = design_tokens.get_color('text', 'secondary')
        border_color = design_tokens.get_color('border', 'primary')
        
        # 更新步骤样式
        for i, widget in enumerate(self._step_widgets):
            circle = widget.findChild(QLabel)
            if circle:
                if i < self._current_step:
                    # 已完成步骤
                    style = f"""
                    QLabel#{circle.objectName()} {{
                        background-color: {primary_color};
                        color: white;
                        border-radius: 16px;
                        font-weight: bold;
                    }}
                    """
                elif i == self._current_step:
                    # 当前步骤
                    style = f"""
                    QLabel#{circle.objectName()} {{
                        background-color: {primary_color};
                        color: white;
                        border-radius: 16px;
                        font-weight: bold;
                        border: 2px solid {primary_color};
                    }}
                    """
                else:
                    # 未完成步骤
                    style = f"""
                    QLabel#{circle.objectName()} {{
                        background-color: {surface_color};
                        color: {text_secondary_color};
                        border-radius: 16px;
                        border: 2px solid {border_color};
                    }}
                    """
                
                circle.setStyleSheet(style)
        
        # 更新连接线样式
        for i, line in enumerate(self._line_widgets):
            if i < self._current_step:
                # 已完成的连接线
                color = primary_color
            else:
                # 未完成的连接线
                color = border_color
            
            style = f"""
            QFrame#{line.objectName()} {{
                background-color: {color};
                border: none;
            }}
            """
            line.setStyleSheet(style)
    
    # 步骤控制方法
    def set_current_step(self, step: int):
        """设置当前步骤"""
        if 0 <= step < len(self._steps) and step != self._current_step:
            old_step = self._current_step
            self._current_step = step
            self.update_style()
            self.step_changed.emit(step)
    
    def next_step(self):
        """下一步"""
        if self._current_step < len(self._steps) - 1:
            self.set_current_step(self._current_step + 1)
    
    def previous_step(self):
        """上一步"""
        if self._current_step > 0:
            self.set_current_step(self._current_step - 1)
    
    def complete_step(self, step: int):
        """完成指定步骤"""
        if step >= self._current_step:
            self.set_current_step(step + 1)
    
    # 属性访问器
    @property
    def current_step(self) -> int:
        """当前步骤"""
        return self._current_step
    
    @current_step.setter
    def current_step(self, value: int):
        """设置当前步骤"""
        self.set_current_step(value)
    
    @property
    def steps(self) -> list[str]:
        """步骤列表"""
        return self._steps.copy()
    
    @property
    def total_steps(self) -> int:
        """总步骤数"""
        return len(self._steps)
    
    @property
    def is_completed(self) -> bool:
        """是否已完成"""
        return self._current_step >= len(self._steps)
    
    @property
    def progress_percentage(self) -> float:
        """进度百分比"""
        if len(self._steps) == 0:
            return 100.0
        return (self._current_step / len(self._steps)) * 100