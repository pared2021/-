"""现代化排版组件"""

from typing import Optional, Union
from PyQt6.QtWidgets import QLabel, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QFontMetrics, QPalette

from .base import BaseComponent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_tokens import design_tokens, ComponentSize


class Typography(BaseComponent):
    """现代化排版组件"""
    
    # 排版信号
    text_changed = pyqtSignal(str)
    link_activated = pyqtSignal(str)
    
    def __init__(
        self,
        text: str = "",
        variant: str = "body",  # heading, body, caption, overline
        size: str = "medium",  # h1-h6 for heading, small/medium/large for others
        weight: str = "normal",  # light, normal, medium, bold
        color: str = "text.primary",  # design token color path
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
        word_wrap: bool = True,
        selectable: bool = False,
        rich_text: bool = False,
        max_lines: Optional[int] = None,
        component_size: ComponentSize = ComponentSize.MEDIUM,
        parent: Optional[QWidget] = None
    ):
        # 排版属性
        self._text = text
        self._variant = variant
        self._size = size
        self._weight = weight
        self._color = color
        self._alignment = alignment
        self._word_wrap = word_wrap
        self._selectable = selectable
        self._rich_text = rich_text
        self._max_lines = max_lines
        
        # 内部组件
        self._label: Optional[QLabel] = None
        
        super().__init__(component_size, parent=parent)
    
    def setup_ui(self):
        """设置UI"""
        # 创建标签
        self._label = QLabel(self._text, self)
        
        # 设置文本格式
        if self._rich_text:
            self._label.setTextFormat(Qt.TextFormat.RichText)
        else:
            self._label.setTextFormat(Qt.TextFormat.PlainText)
        
        # 设置对齐
        self._label.setAlignment(self._alignment)
        
        # 设置换行
        self._label.setWordWrap(self._word_wrap)
        
        # 设置选择性
        if self._selectable:
            self._label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse |
                Qt.TextInteractionFlag.TextSelectableByKeyboard
            )
        
        # 设置链接
        if self._rich_text:
            self._label.setOpenExternalLinks(False)
            self._label.setTextInteractionFlags(
                self._label.textInteractionFlags() |
                Qt.TextInteractionFlag.LinksAccessibleByMouse
            )
        
        # 设置布局
        self._label.setGeometry(self.rect())
    
    def setup_connections(self):
        """设置信号连接"""
        if self._label:
            if self._rich_text:
                self._label.linkActivated.connect(self.link_activated.emit)
    
    def update_style(self):
        """更新样式"""
        if not self._label:
            return
        
        # 生成样式缓存键
        style_key = self._generate_style_key(
            variant=self._variant,
            size=self._size,
            weight=self._weight,
            color=self._color,
            max_lines=self._max_lines
        )
        
        # 检查缓存
        cached_style = self._get_cached_style(style_key)
        if cached_style:
            self._apply_cached_style(cached_style)
            return
        
        # 生成新样式
        font = self._generate_font()
        color = self._generate_color()
        style_sheet = self._generate_style_sheet()
        
        style_data = {
            'font': font,
            'color': color,
            'style_sheet': style_sheet
        }
        
        # 缓存并应用样式
        self._cache_style(style_key, style_data)
        self._apply_cached_style(style_data)
    
    def _generate_font(self) -> QFont:
        """生成字体"""
        # 根据文本类型获取字体配置
        if self._variant == "heading":
            font_token = design_tokens.get_typography('heading', self._size)
        elif self._variant in ['body', 'caption', 'overline']:
            font_token = design_tokens.get_typography('body', 'medium')
        else:
            font_token = design_tokens.get_typography('body', 'medium')
        
        # 创建字体
        font = QFont(font_token.font_family)
        font.setPointSize(font_token.font_size)
        
        # 设置字体粗细
        if isinstance(font_token.font_weight, str):
            if font_token.font_weight == "bold":
                font.setBold(True)
            else:
                font.setBold(False)
        else:
            font.setWeight(font_token.font_weight)
        
        # 特殊样式
        if self._variant == "overline":
            font.setCapitalization(QFont.Capitalization.AllUppercase)
            font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
        
        return font
    
    def _generate_color(self) -> str:
        """生成颜色"""
        # 解析颜色路径
        if '.' in self._color:
            category, key = self._color.split('.', 1)
            return design_tokens.get_color(category, key)
        else:
            return design_tokens.get_color('text', 'primary')
    
    def _generate_style_sheet(self) -> str:
        """生成样式表"""
        color = self._generate_color()
        
        style = f"""
        QLabel {{
            color: {color};
        }}
        """
        
        # 最大行数限制
        if self._max_lines:
            # 注意：Qt的QLabel不直接支持max-lines，这里只是示例
            # 实际实现可能需要自定义绘制或使用QTextEdit
            pass
        
        return style
    
    def _apply_cached_style(self, style_data: dict):
        """应用缓存的样式"""
        if self._label:
            self._label.setFont(style_data['font'])
            self._label.setStyleSheet(style_data['style_sheet'])
    
    def resizeEvent(self, event):
        """窗口大小变化事件"""
        super().resizeEvent(event)
        if self._label:
            self._label.setGeometry(self.rect())
    
    # 文本管理方法
    def set_text(self, text: str):
        """设置文本"""
        if self._text != text:
            self._text = text
            if self._label:
                self._label.setText(text)
            self.text_changed.emit(text)
    
    def append_text(self, text: str):
        """追加文本"""
        new_text = self._text + text
        self.set_text(new_text)
    
    def clear_text(self):
        """清空文本"""
        self.set_text("")
    
    def get_text_width(self) -> int:
        """获取文本宽度"""
        if self._label:
            font_metrics = QFontMetrics(self._label.font())
            return font_metrics.horizontalAdvance(self._text)
        return 0
    
    def get_text_height(self) -> int:
        """获取文本高度"""
        if self._label:
            font_metrics = QFontMetrics(self._label.font())
            return font_metrics.height()
        return 0
    
    def elide_text(self, width: int, mode: Qt.TextElideMode = Qt.TextElideMode.ElideRight) -> str:
        """省略文本"""
        if self._label:
            font_metrics = QFontMetrics(self._label.font())
            return font_metrics.elidedText(self._text, mode, width)
        return self._text
    
    # 属性访问器
    @property
    def text(self) -> str:
        """文本内容"""
        return self._text
    
    @text.setter
    def text(self, value: str):
        """设置文本内容"""
        self.set_text(value)
    
    @property
    def variant(self) -> str:
        """文本变体"""
        return self._variant
    
    @variant.setter
    def variant(self, value: str):
        """设置文本变体"""
        if self._variant != value:
            self._variant = value
            self.update_style()
    
    @property
    def size(self) -> str:
        """文本大小"""
        return self._size
    
    @size.setter
    def size(self, value: str):
        """设置文本大小"""
        if self._size != value:
            self._size = value
            self.update_style()
    
    @property
    def weight(self) -> str:
        """字体粗细"""
        return self._weight
    
    @weight.setter
    def weight(self, value: str):
        """设置字体粗细"""
        if self._weight != value:
            self._weight = value
            self.update_style()
    
    @property
    def color(self) -> str:
        """文本颜色"""
        return self._color
    
    @color.setter
    def color(self, value: str):
        """设置文本颜色"""
        if self._color != value:
            self._color = value
            self.update_style()
    
    @property
    def alignment(self) -> Qt.AlignmentFlag:
        """文本对齐"""
        return self._alignment
    
    @alignment.setter
    def alignment(self, value: Qt.AlignmentFlag):
        """设置文本对齐"""
        if self._alignment != value:
            self._alignment = value
            if self._label:
                self._label.setAlignment(value)
    
    @property
    def word_wrap(self) -> bool:
        """是否换行"""
        return self._word_wrap
    
    @word_wrap.setter
    def word_wrap(self, value: bool):
        """设置是否换行"""
        if self._word_wrap != value:
            self._word_wrap = value
            if self._label:
                self._label.setWordWrap(value)
    
    @property
    def selectable(self) -> bool:
        """是否可选择"""
        return self._selectable
    
    @selectable.setter
    def selectable(self, value: bool):
        """设置是否可选择"""
        if self._selectable != value:
            self._selectable = value
            if self._label:
                if value:
                    self._label.setTextInteractionFlags(
                        Qt.TextInteractionFlag.TextSelectableByMouse |
                        Qt.TextInteractionFlag.TextSelectableByKeyboard
                    )
                else:
                    self._label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
    
    @property
    def rich_text(self) -> bool:
        """是否富文本"""
        return self._rich_text
    
    @rich_text.setter
    def rich_text(self, value: bool):
        """设置是否富文本"""
        if self._rich_text != value:
            self._rich_text = value
            if self._label:
                if value:
                    self._label.setTextFormat(Qt.TextFormat.RichText)
                    self._label.setOpenExternalLinks(False)
                    self._label.setTextInteractionFlags(
                        self._label.textInteractionFlags() |
                        Qt.TextInteractionFlag.LinksAccessibleByMouse
                    )
                else:
                    self._label.setTextFormat(Qt.TextFormat.PlainText)
    
    @property
    def max_lines(self) -> Optional[int]:
        """最大行数"""
        return self._max_lines
    
    @max_lines.setter
    def max_lines(self, value: Optional[int]):
        """设置最大行数"""
        if self._max_lines != value:
            self._max_lines = value
            self.update_style()


class Heading(Typography):
    """标题组件"""
    
    def __init__(
        self,
        text: str = "",
        level: int = 1,  # 1-6
        color: str = "text.primary",
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
        parent: Optional[QWidget] = None
    ):
        # 确保级别在有效范围内
        level = max(1, min(6, level))
        size = f"h{level}"
        
        super().__init__(
            text=text,
            variant="heading",
            size=size,
            weight="bold" if level <= 3 else "medium",
            color=color,
            alignment=alignment,
            parent=parent
        )
        
        self._level = level
    
    @property
    def level(self) -> int:
        """标题级别"""
        return self._level
    
    @level.setter
    def level(self, value: int):
        """设置标题级别"""
        value = max(1, min(6, value))
        if self._level != value:
            self._level = value
            self.size = f"h{value}"
            self.weight = "bold" if value <= 3 else "medium"


class Body(Typography):
    """正文组件"""
    
    def __init__(
        self,
        text: str = "",
        size: str = "medium",
        color: str = "text.primary",
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
        parent: Optional[QWidget] = None
    ):
        super().__init__(
            text=text,
            variant="body",
            size=size,
            weight="normal",
            color=color,
            alignment=alignment,
            parent=parent
        )


class Caption(Typography):
    """说明文字组件"""
    
    def __init__(
        self,
        text: str = "",
        color: str = "text.secondary",
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
        parent: Optional[QWidget] = None
    ):
        super().__init__(
            text=text,
            variant="caption",
            size="small",
            weight="normal",
            color=color,
            alignment=alignment,
            parent=parent
        )


class Overline(Typography):
    """上标文字组件"""
    
    def __init__(
        self,
        text: str = "",
        color: str = "text.secondary",
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
        parent: Optional[QWidget] = None
    ):
        super().__init__(
            text=text,
            variant="overline",
            size="small",
            weight="medium",
            color=color,
            alignment=alignment,
            parent=parent
        )


class Link(Typography):
    """链接组件"""
    
    # 链接信号
    clicked = pyqtSignal()
    
    def __init__(
        self,
        text: str = "",
        url: str = "",
        size: str = "medium",
        color: str = "text.primary",
        underline: bool = True,
        parent: Optional[QWidget] = None
    ):
        self._url = url
        self._underline = underline
        
        # 如果有URL，使用富文本格式
        if url:
            display_text = f'<a href="{url}">{text}</a>'
            rich_text = True
        else:
            display_text = text
            rich_text = False
        
        super().__init__(
            text=display_text,
            variant="body",
            size=size,
            color=color,
            rich_text=rich_text,
            parent=parent
        )
    
    def setup_connections(self):
        """设置信号连接"""
        super().setup_connections()
        
        # 连接链接点击信号
        self.link_activated.connect(self._handle_link_clicked)
        
        # 如果没有URL，设置鼠标点击事件
        if not self._url and self._label:
            self._label.mousePressEvent = self._handle_mouse_click
    
    def _handle_link_clicked(self, url: str):
        """处理链接点击"""
        self.clicked.emit()
    
    def _handle_mouse_click(self, event):
        """处理鼠标点击"""
        self.clicked.emit()
    
    def update_style(self):
        """更新样式"""
        super().update_style()
        
        if self._label and not self._rich_text:
            # 为非富文本链接添加样式
            current_style = self._label.styleSheet()
            
            link_style = """
            QLabel {
                color: #0066cc;
            }
            QLabel:hover {
                color: #004499;
            }
            """
            
            if self._underline:
                link_style += """
                QLabel {
                    text-decoration: underline;
                }
                """
            
            self._label.setStyleSheet(current_style + link_style)
            self._label.setCursor(Qt.CursorShape.PointingHandCursor)
    
    @property
    def url(self) -> str:
        """链接URL"""
        return self._url
    
    @url.setter
    def url(self, value: str):
        """设置链接URL"""
        if self._url != value:
            self._url = value
            
            # 更新文本格式
            if value:
                display_text = f'<a href="{value}">{self._text}</a>'
                self.rich_text = True
                self.text = display_text
            else:
                self.rich_text = False
                # 提取纯文本
                if '<a' in self._text:
                    import re
                    match = re.search(r'>([^<]+)<', self._text)
                    if match:
                        self.text = match.group(1)
    
    @property
    def underline(self) -> bool:
        """是否下划线"""
        return self._underline
    
    @underline.setter
    def underline(self, value: bool):
        """设置是否下划线"""
        if self._underline != value:
            self._underline = value
            self.update_style()