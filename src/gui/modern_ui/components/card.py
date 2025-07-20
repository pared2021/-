"""现代化卡片组件"""

from typing import Optional, List, Union
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont

from .base import BaseComponent
from .button import Button
from .typography import Typography
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_tokens import ComponentSize, ComponentVariant, design_tokens
from style_generator import style_generator


class Card(BaseComponent):
    """现代化卡片组件"""
    
    # 卡片特有信号
    clicked = pyqtSignal()
    header_clicked = pyqtSignal()
    footer_clicked = pyqtSignal()
    
    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        size: ComponentSize = ComponentSize.MEDIUM,
        variant: ComponentVariant = ComponentVariant.PRIMARY,
        elevated: bool = True,
        interactive: bool = False,
        bordered: bool = True,
        hoverable: bool = False,
        loading: bool = False,
        parent: Optional[QWidget] = None
    ):
        # 卡片特有属性
        self._title = title
        self._subtitle = subtitle
        self._elevated = elevated
        self._interactive = interactive
        self._bordered = bordered
        self._hoverable = hoverable
        self._loading = loading
        
        # 内部组件
        self._main_frame: Optional[QFrame] = None
        self._header_widget: Optional[QWidget] = None
        self._content_widget: Optional[QWidget] = None
        self._footer_widget: Optional[QWidget] = None
        self._title_label: Optional[Typography] = None
        self._subtitle_label: Optional[Typography] = None
        
        # 布局
        self._main_layout: Optional[QVBoxLayout] = None
        self._header_layout: Optional[QVBoxLayout] = None
        self._content_layout: Optional[QVBoxLayout] = None
        self._footer_layout: Optional[QHBoxLayout] = None
        
        super().__init__(size, variant, False, parent)
    
    def setup_ui(self):
        """设置UI"""
        # 创建主框架
        self._main_frame = QFrame(self)
        self._main_frame.setObjectName("cardFrame")
        
        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._main_frame)
        
        # 设置卡片内部布局
        self._main_layout = QVBoxLayout(self._main_frame)
        self._setup_spacing()
        
        # 创建各个区域
        self._setup_header()
        self._setup_content()
        self._setup_footer()
        
        # 设置交互性
        if self._interactive:
            self._main_frame.mousePressEvent = self._handle_click
    
    def _setup_spacing(self):
        """设置间距"""
        padding = design_tokens.get_component_token('card', 'padding', self._size)
        gap = design_tokens.get_component_token('card', 'gap', self._size)
        
        if padding:
            if isinstance(padding, tuple) and len(padding) >= 2:
                # 如果是tuple，使用第一个值作为垂直padding，第二个值作为水平padding
                v_padding, h_padding = padding[0], padding[1]
                self._main_layout.setContentsMargins(h_padding, v_padding, h_padding, v_padding)
            elif isinstance(padding, int):
                # 如果是int，四个方向使用相同的padding
                self._main_layout.setContentsMargins(padding, padding, padding, padding)
        if gap:
            self._main_layout.setSpacing(gap)
    
    def _setup_header(self):
        """设置头部"""
        if not self._title and not self._subtitle:
            return
        
        self._header_widget = QWidget()
        self._header_layout = QVBoxLayout(self._header_widget)
        self._header_layout.setContentsMargins(0, 0, 0, 0)
        self._header_layout.setSpacing(design_tokens.get_spacing('1'))
        
        # 标题
        if self._title:
            self._title_label = Typography(
                text=self._title,
                variant='heading',
                size='h5' if self._size == ComponentSize.LARGE else 'h6',
                color='text.primary'
            )
            self._header_layout.addWidget(self._title_label)
        
        # 副标题
        if self._subtitle:
            self._subtitle_label = Typography(
                text=self._subtitle,
                variant='body',
                size='small',
                color='text.secondary'
            )
            self._header_layout.addWidget(self._subtitle_label)
        
        self._main_layout.addWidget(self._header_widget)
    
    def _setup_content(self):
        """设置内容区域"""
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(design_tokens.get_spacing('3'))
        
        self._main_layout.addWidget(self._content_widget)
    
    def _setup_footer(self):
        """设置底部"""
        self._footer_widget = QWidget()
        self._footer_layout = QHBoxLayout(self._footer_widget)
        self._footer_layout.setContentsMargins(0, 0, 0, 0)
        self._footer_layout.setSpacing(design_tokens.get_spacing('2'))
        
        # 默认隐藏，有内容时显示
        self._footer_widget.hide()
        
        self._main_layout.addWidget(self._footer_widget)
    
    def _handle_click(self, event):
        """处理点击事件"""
        if self._interactive and not self._loading:
            self.clicked.emit()
    
    def setup_connections(self):
        """设置信号连接"""
        pass
    
    def update_style(self):
        """更新样式"""
        if not self._main_frame:
            return
        
        # 生成样式缓存键
        style_key = self._generate_style_key(
            elevated=self._elevated,
            interactive=self._interactive,
            bordered=self._bordered,
            hoverable=self._hoverable,
            loading=self._loading
        )
        
        # 检查缓存
        cached_style = self._get_cached_style(style_key)
        if cached_style:
            self._main_frame.setStyleSheet(cached_style)
            return
        
        # 生成新样式
        style = style_generator.generate_card_style(
            elevated=self._elevated
        )
        
        # 添加额外样式
        if not self._bordered:
            style += "\nQFrame#cardFrame { border: none; }"
        
        if self._loading:
            style += self._generate_loading_style()
        
        # 缓存并应用样式
        self._cache_style(style_key, style)
        self._main_frame.setStyleSheet(style)
    
    def _generate_loading_style(self) -> str:
        """生成加载状态样式"""
        return """
        QFrame#cardFrame {
            opacity: 0.6;
        }
        """
    
    # 内容管理方法
    def add_content(self, widget: QWidget):
        """添加内容"""
        if self._content_layout:
            self._content_layout.addWidget(widget)
    
    def insert_content(self, index: int, widget: QWidget):
        """插入内容"""
        if self._content_layout:
            self._content_layout.insertWidget(index, widget)
    
    def remove_content(self, widget: QWidget):
        """移除内容"""
        if self._content_layout:
            self._content_layout.removeWidget(widget)
            widget.setParent(None)
    
    def clear_content(self):
        """清空内容"""
        if self._content_layout:
            while self._content_layout.count():
                child = self._content_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
    
    def add_footer_action(self, button: Button):
        """添加底部操作按钮"""
        if self._footer_layout:
            self._footer_layout.addWidget(button)
            self._footer_widget.show()
    
    def add_footer_spacer(self):
        """添加底部弹性空间"""
        if self._footer_layout:
            self._footer_layout.addStretch()
    
    def clear_footer(self):
        """清空底部"""
        if self._footer_layout:
            while self._footer_layout.count():
                child = self._footer_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            self._footer_widget.hide()
    
    # 属性访问器
    @property
    def title(self) -> str:
        """卡片标题"""
        return self._title
    
    @title.setter
    def title(self, value: str):
        """设置卡片标题"""
        if self._title != value:
            self._title = value
            if self._title_label:
                self._title_label.text = value
            elif value:
                self._setup_header()
    
    @property
    def subtitle(self) -> str:
        """卡片副标题"""
        return self._subtitle
    
    @subtitle.setter
    def subtitle(self, value: str):
        """设置卡片副标题"""
        if self._subtitle != value:
            self._subtitle = value
            if self._subtitle_label:
                self._subtitle_label.text = value
            elif value:
                self._setup_header()
    
    @property
    def elevated(self) -> bool:
        """是否有阴影"""
        return self._elevated
    
    @elevated.setter
    def elevated(self, value: bool):
        """设置阴影"""
        if self._elevated != value:
            self._elevated = value
            self.update_style()
    
    @property
    def interactive(self) -> bool:
        """是否可交互"""
        return self._interactive
    
    @interactive.setter
    def interactive(self, value: bool):
        """设置交互性"""
        if self._interactive != value:
            self._interactive = value
            if value and self._main_frame:
                self._main_frame.mousePressEvent = self._handle_click
            self.update_style()
    
    @property
    def bordered(self) -> bool:
        """是否有边框"""
        return self._bordered
    
    @bordered.setter
    def bordered(self, value: bool):
        """设置边框"""
        if self._bordered != value:
            self._bordered = value
            self.update_style()
    
    @property
    def hoverable(self) -> bool:
        """是否可悬浮"""
        return self._hoverable
    
    @hoverable.setter
    def hoverable(self, value: bool):
        """设置悬浮效果"""
        if self._hoverable != value:
            self._hoverable = value
            self.update_style()
    
    @property
    def loading(self) -> bool:
        """是否加载中"""
        return self._loading
    
    @loading.setter
    def loading(self, value: bool):
        """设置加载状态"""
        if self._loading != value:
            self._loading = value
            self.update_style()


class ImageCard(Card):
    """图片卡片"""
    
    def __init__(
        self,
        image: Optional[QPixmap] = None,
        title: str = "",
        subtitle: str = "",
        size: ComponentSize = ComponentSize.MEDIUM,
        parent: Optional[QWidget] = None
    ):
        self._image = image
        self._image_label: Optional[QLabel] = None
        
        super().__init__(
            title=title,
            subtitle=subtitle,
            size=size,
            parent=parent
        )
    
    def setup_ui(self):
        """设置UI"""
        super().setup_ui()
        
        if self._image:
            self._setup_image()
    
    def _setup_image(self):
        """设置图片"""
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setScaledContents(True)
        
        if self._image:
            if isinstance(self._image, str):
                # 如果是字符串路径，加载为QPixmap
                from PyQt6.QtGui import QPixmap
                pixmap = QPixmap(self._image)
                if not pixmap.isNull():
                    self._image_label.setPixmap(pixmap)
            elif hasattr(self._image, 'isNull'):
                # 确保是QPixmap对象
                self._image_label.setPixmap(self._image)
        
        # 插入到内容区域顶部
        if self._content_layout:
            self._content_layout.insertWidget(0, self._image_label)
    
    @property
    def image(self) -> Optional[QPixmap]:
        """卡片图片"""
        return self._image
    
    @image.setter
    def image(self, value):
        """设置卡片图片"""
        self._image = value
        if self._image_label:
            if value:
                if isinstance(value, str):
                    # 如果是字符串路径，加载为QPixmap
                    from PyQt6.QtGui import QPixmap
                    pixmap = QPixmap(value)
                    if not pixmap.isNull():
                        self._image_label.setPixmap(pixmap)
                    else:
                        self._image_label.clear()
                elif hasattr(value, 'isNull'):
                    self._image_label.setPixmap(value)
                else:
                    self._image_label.clear()
            else:
                self._image_label.clear()
        elif value:
            self._setup_image()


class StatCard(Card):
    """统计卡片"""
    
    def __init__(
        self,
        title: str,
        value: str,
        change: Optional[str] = None,
        trend: Optional[str] = None,  # 'up', 'down', 'neutral'
        size: ComponentSize = ComponentSize.MEDIUM,
        parent: Optional[QWidget] = None
    ):
        self._value = value
        self._change = change
        self._trend = trend
        
        self._value_label: Optional[Typography] = None
        self._change_label: Optional[Typography] = None
        
        super().__init__(
            title=title,
            size=size,
            parent=parent
        )
    
    def setup_ui(self):
        """设置UI"""
        super().setup_ui()
        
        # 数值显示
        self._value_label = Typography(
            text=self._value,
            variant='heading',
            size='h3' if self._size == ComponentSize.LARGE else 'h4',
            color='text.primary'
        )
        self.add_content(self._value_label)
        
        # 变化显示
        if self._change:
            color = 'semantic.success' if self._trend == 'up' else \
                   'semantic.error' if self._trend == 'down' else \
                   'text.secondary'
            
            self._change_label = Typography(
                text=self._change,
                variant='body',
                size='small',
                color=color
            )
            self.add_content(self._change_label)
    
    @property
    def value(self) -> str:
        """统计值"""
        return self._value
    
    @value.setter
    def value(self, value: str):
        """设置统计值"""
        self._value = value
        if self._value_label:
            self._value_label.text = value
    
    @property
    def change(self) -> Optional[str]:
        """变化值"""
        return self._change
    
    @change.setter
    def change(self, value: Optional[str]):
        """设置变化值"""
        self._change = value
        if self._change_label:
            self._change_label.text = value or ""
    
    @property
    def trend(self) -> Optional[str]:
        """趋势"""
        return self._trend
    
    @trend.setter
    def trend(self, value: Optional[str]):
        """设置趋势"""
        self._trend = value
        if self._change_label:
            color = 'semantic.success' if value == 'up' else \
                   'semantic.error' if value == 'down' else \
                   'text.secondary'
            self._change_label.color = color