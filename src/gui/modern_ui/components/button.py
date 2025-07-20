"""现代化按钮组件"""

from typing import Optional, Callable
from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QFont

from .base import BaseComponent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_tokens import ComponentSize, ComponentVariant, design_tokens
from style_generator import style_generator


class Button(BaseComponent):
    """现代化按钮组件"""
    
    # 按钮特有信号
    clicked = pyqtSignal()
    pressed = pyqtSignal()
    released = pyqtSignal()
    
    def __init__(
        self,
        text: str = "",
        icon: Optional[QIcon] = None,
        size: ComponentSize = ComponentSize.MEDIUM,
        variant: ComponentVariant = ComponentVariant.PRIMARY,
        full_width: bool = False,
        loading: bool = False,
        disabled: bool = False,
        on_click: Optional[Callable] = None,
        parent: Optional = None
    ):
        # 按钮特有属性
        self._text = text
        self._icon = icon
        self._full_width = full_width
        self._loading = loading
        self._on_click = on_click
        
        # 内部组件
        self._button: Optional[QPushButton] = None
        self._icon_label: Optional[QLabel] = None
        self._text_label: Optional[QLabel] = None
        
        super().__init__(size, variant, disabled, parent)
    
    def setup_ui(self):
        """设置UI"""
        # 创建主按钮
        self._button = QPushButton(self)
        
        # 设置布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._button)
        
        # 设置按钮内容
        self._setup_button_content()
        
        # 设置尺寸
        self._update_size()
    
    def _setup_button_content(self):
        """设置按钮内容"""
        if self._icon and self._text:
            # 图标 + 文字
            self._setup_icon_text_button()
        elif self._icon:
            # 仅图标
            self._button.setIcon(self._icon)
        else:
            # 仅文字
            self._button.setText(self._text)
    
    def _setup_icon_text_button(self):
        """设置图标+文字按钮"""
        # 创建内部布局
        button_layout = QHBoxLayout(self._button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 获取间距
        spacing = design_tokens.get_spacing('2')
        button_layout.setSpacing(spacing)
        
        # 图标标签
        if self._icon:
            self._icon_label = QLabel()
            self._icon_label.setPixmap(self._icon.pixmap(16, 16))  # 默认图标尺寸
            self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button_layout.addWidget(self._icon_label)
        
        # 文字标签
        if self._text:
            self._text_label = QLabel(self._text)
            self._text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button_layout.addWidget(self._text_label)
    
    def _update_size(self):
        """更新尺寸"""
        # 获取尺寸token
        height = design_tokens.get_component_token('button', 'height', self._size)
        padding = design_tokens.get_component_token('button', 'padding', self._size)
        font_size = design_tokens.get_component_token('button', 'font_size', self._size)
        
        if height:
            self.setFixedHeight(height)
        
        # 设置字体大小
        if font_size:
            font = QFont()
            font.setPointSize(font_size)
            font.setBold(True)
            self._button.setFont(font)
            
            if self._text_label:
                self._text_label.setFont(font)
        
        # 设置全宽
        if self._full_width:
            self.setSizePolicy(
                self.sizePolicy().horizontalPolicy(),
                self.sizePolicy().verticalPolicy()
            )
    
    def setup_connections(self):
        """设置信号连接"""
        if self._button:
            self._button.clicked.connect(self._handle_click)
            self._button.pressed.connect(self.pressed.emit)
            self._button.released.connect(self.released.emit)
    
    def _handle_click(self):
        """处理点击事件"""
        if self._loading or self._disabled:
            return
        
        self.clicked.emit()
        
        if self._on_click:
            self._on_click()
    
    def update_style(self):
        """更新样式"""
        if not self._button:
            return
        
        # 生成样式缓存键
        style_key = self._generate_style_key(
            full_width=self._full_width,
            loading=self._loading
        )
        
        # 检查缓存
        cached_style = self._get_cached_style(style_key)
        if cached_style:
            self._button.setStyleSheet(cached_style)
            return
        
        # 生成新样式
        style = style_generator.generate_button_style(
            variant=self._variant,
            size=self._size,
            disabled=self._disabled
        )
        
        # 添加加载状态样式
        if self._loading:
            style += self._generate_loading_style()
        
        # 缓存并应用样式
        self._cache_style(style_key, style)
        self._button.setStyleSheet(style)
    
    def _generate_loading_style(self) -> str:
        """生成加载状态样式"""
        return """
        QPushButton {
            opacity: 0.7;
        }
        QPushButton:hover {
            opacity: 0.7;
        }
        """
    
    # 属性访问器
    @property
    def text(self) -> str:
        """按钮文字"""
        return self._text
    
    @text.setter
    def text(self, value: str):
        """设置按钮文字"""
        if self._text != value:
            self._text = value
            if self._button:
                if self._text_label:
                    self._text_label.setText(value)
                else:
                    self._button.setText(value)
    
    @property
    def icon(self) -> Optional[QIcon]:
        """按钮图标"""
        return self._icon
    
    @icon.setter
    def icon(self, value: Optional[QIcon]):
        """设置按钮图标"""
        if self._icon != value:
            self._icon = value
            if self._button:
                if self._icon_label and value:
                    self._icon_label.setPixmap(value.pixmap(16, 16))
                elif not self._icon_label:
                    self._button.setIcon(value or QIcon())
    
    @property
    def full_width(self) -> bool:
        """是否全宽"""
        return self._full_width
    
    @full_width.setter
    def full_width(self, value: bool):
        """设置全宽"""
        if self._full_width != value:
            self._full_width = value
            self._update_size()
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
            if self._button:
                self._button.setEnabled(not value)
            self.update_style()
    
    @property
    def on_click(self) -> Optional[Callable]:
        """点击回调"""
        return self._on_click
    
    @on_click.setter
    def on_click(self, value: Optional[Callable]):
        """设置点击回调"""
        self._on_click = value
    
    # 公共方法
    def click(self):
        """程序化点击"""
        if self._button and not self._loading and not self._disabled:
            self._button.click()
    
    def set_shortcut(self, shortcut: str):
        """设置快捷键"""
        if self._button:
            self._button.setShortcut(shortcut)
    
    def set_tooltip(self, tooltip: str):
        """设置工具提示"""
        self.setToolTip(tooltip)
        if self._button:
            self._button.setToolTip(tooltip)
    
    def set_focus(self):
        """设置焦点"""
        if self._button:
            self._button.setFocus()
    
    def start_loading(self):
        """开始加载"""
        self.loading = True
    
    def stop_loading(self):
        """停止加载"""
        self.loading = False
    
    def toggle_loading(self):
        """切换加载状态"""
        self.loading = not self.loading


class IconButton(Button):
    """图标按钮 - 仅显示图标的按钮"""
    
    def __init__(
        self,
        icon: QIcon,
        size: ComponentSize = ComponentSize.MEDIUM,
        variant: ComponentVariant = ComponentVariant.PRIMARY,
        disabled: bool = False,
        on_click: Optional[Callable] = None,
        parent: Optional = None
    ):
        super().__init__(
            text="",
            icon=icon,
            size=size,
            variant=variant,
            disabled=disabled,
            on_click=on_click,
            parent=parent
        )
        
        # 设置为正方形
        self._make_square()
    
    def _make_square(self):
        """设置为正方形"""
        height = design_tokens.get_component_token('button', 'height', self._size)
        if height:
            self.setFixedSize(height, height)


class TextButton(Button):
    """文字按钮 - 仅显示文字的按钮"""
    
    def __init__(
        self,
        text: str,
        size: ComponentSize = ComponentSize.MEDIUM,
        variant: ComponentVariant = ComponentVariant.PRIMARY,
        full_width: bool = False,
        disabled: bool = False,
        on_click: Optional[Callable] = None,
        parent: Optional = None
    ):
        super().__init__(
            text=text,
            icon=None,
            size=size,
            variant=variant,
            full_width=full_width,
            disabled=disabled,
            on_click=on_click,
            parent=parent
        )


class LinkButton(Button):
    """链接按钮 - 看起来像链接的按钮"""
    
    def __init__(
        self,
        text: str,
        size: ComponentSize = ComponentSize.MEDIUM,
        disabled: bool = False,
        on_click: Optional[Callable] = None,
        parent: Optional = None
    ):
        super().__init__(
            text=text,
            icon=None,
            size=size,
            variant=ComponentVariant.SECONDARY,
            disabled=disabled,
            on_click=on_click,
            parent=parent
        )
        
        # 禁用阴影和动画
        self.shadow_enabled = False
        self.animated = False
    
    def update_style(self):
        """更新样式 - 链接样式"""
        if not self._button:
            return
        
        text_color = design_tokens.get_color('primary', '500')
        hover_color = design_tokens.get_color('primary', '400')
        
        style = f"""
        QPushButton {{
            background: transparent;
            border: none;
            color: {text_color};
            text-decoration: underline;
            padding: 4px 8px;
        }}
        
        QPushButton:hover {{
            color: {hover_color};
        }}
        
        QPushButton:pressed {{
            color: {design_tokens.get_color('primary', '600')};
        }}
        
        QPushButton:disabled {{
            color: {design_tokens.get_color('text', 'disabled')};
            text-decoration: none;
        }}
        """
        
        self._button.setStyleSheet(style)