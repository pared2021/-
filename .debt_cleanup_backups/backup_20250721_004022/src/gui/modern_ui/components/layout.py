"""现代化布局组件"""

from typing import Optional, Union, List, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QStackedLayout, QSplitter, QScrollArea, QFrame,
    QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QResizeEvent

from .base import BaseComponent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_tokens import design_tokens, ComponentSize


class VBox(BaseComponent):
    """垂直布局容器"""
    
    def __init__(
        self,
        spacing: Optional[int] = None,
        margins: Optional[Union[int, Tuple[int, int, int, int]]] = None,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignTop,
        size: ComponentSize = ComponentSize.MEDIUM,
        parent: Optional[QWidget] = None
    ):
        # 布局属性
        self._spacing = spacing
        self._margins = margins
        self._alignment = alignment
        
        # 内部布局
        self._layout: Optional[QVBoxLayout] = None
        
        super().__init__(size, parent=parent)
    
    def setup_ui(self):
        """设置UI"""
        # 创建垂直布局
        self._layout = QVBoxLayout(self)
        
        # 设置间距
        if self._spacing is not None:
            self._layout.setSpacing(self._spacing)
        else:
            self._layout.setSpacing(design_tokens.get_spacing('3'))
        
        # 设置边距
        if self._margins is not None:
            if isinstance(self._margins, int):
                self._layout.setContentsMargins(self._margins, self._margins, self._margins, self._margins)
            else:
                self._layout.setContentsMargins(*self._margins)
        else:
            margin = design_tokens.get_spacing('3')
            self._layout.setContentsMargins(margin, margin, margin, margin)
        
        # 设置对齐
        self._layout.setAlignment(self._alignment)
    
    def setup_connections(self):
        """设置信号连接"""
        pass
    
    def update_style(self):
        """更新样式"""
        pass
    
    # 布局管理方法
    def add_widget(self, widget: QWidget, stretch: int = 0, alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter):
        """添加组件"""
        if self._layout:
            self._layout.addWidget(widget, stretch, alignment)
    
    def insert_widget(self, index: int, widget: QWidget, stretch: int = 0, alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter):
        """插入组件"""
        if self._layout:
            self._layout.insertWidget(index, widget, stretch, alignment)
    
    def remove_widget(self, widget: QWidget):
        """移除组件"""
        if self._layout:
            self._layout.removeWidget(widget)
            widget.setParent(None)
    
    def add_stretch(self, stretch: int = 1):
        """添加弹性空间"""
        if self._layout:
            self._layout.addStretch(stretch)
    
    def add_spacing(self, size: int):
        """添加固定间距"""
        if self._layout:
            self._layout.addSpacing(size)
    
    def clear(self):
        """清空布局"""
        if self._layout:
            while self._layout.count():
                child = self._layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
    
    # 属性访问器
    @property
    def spacing(self) -> int:
        """间距"""
        return self._layout.spacing() if self._layout else 0
    
    @spacing.setter
    def spacing(self, value: int):
        """设置间距"""
        self._spacing = value
        if self._layout:
            self._layout.setSpacing(value)
    
    def set_spacing(self, value: int):
        """设置间距（方法形式）"""
        self.spacing = value
    
    def set_margins(self, *args):
        """设置边距"""
        if len(args) == 1:
            margin = args[0]
            self._layout.setContentsMargins(margin, margin, margin, margin)
        elif len(args) == 4:
            self._layout.setContentsMargins(*args)
    
    @property
    def count(self) -> int:
        """子组件数量"""
        return self._layout.count() if self._layout else 0


class HBox(BaseComponent):
    """水平布局容器"""
    
    def __init__(
        self,
        spacing: Optional[int] = None,
        margins: Optional[Union[int, Tuple[int, int, int, int]]] = None,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
        size: ComponentSize = ComponentSize.MEDIUM,
        parent: Optional[QWidget] = None
    ):
        # 布局属性
        self._spacing = spacing
        self._margins = margins
        self._alignment = alignment
        
        # 内部布局
        self._layout: Optional[QHBoxLayout] = None
        
        super().__init__(size, parent=parent)
    
    def setup_ui(self):
        """设置UI"""
        # 创建水平布局
        self._layout = QHBoxLayout(self)
        
        # 设置间距
        if self._spacing is not None:
            self._layout.setSpacing(self._spacing)
        else:
            self._layout.setSpacing(design_tokens.get_spacing('3'))
        
        # 设置边距
        if self._margins is not None:
            if isinstance(self._margins, int):
                self._layout.setContentsMargins(self._margins, self._margins, self._margins, self._margins)
            else:
                self._layout.setContentsMargins(*self._margins)
        else:
            margin = design_tokens.get_spacing('3')
            self._layout.setContentsMargins(margin, margin, margin, margin)
        
        # 设置对齐
        self._layout.setAlignment(self._alignment)
    
    def setup_connections(self):
        """设置信号连接"""
        pass
    
    def update_style(self):
        """更新样式"""
        pass
    
    # 布局管理方法
    def add_widget(self, widget: QWidget, stretch: int = 0, alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter):
        """添加组件"""
        if self._layout:
            self._layout.addWidget(widget, stretch, alignment)
    
    def insert_widget(self, index: int, widget: QWidget, stretch: int = 0, alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter):
        """插入组件"""
        if self._layout:
            self._layout.insertWidget(index, widget, stretch, alignment)
    
    def remove_widget(self, widget: QWidget):
        """移除组件"""
        if self._layout:
            self._layout.removeWidget(widget)
            widget.setParent(None)
    
    def add_stretch(self, stretch: int = 1):
        """添加弹性空间"""
        if self._layout:
            self._layout.addStretch(stretch)
    
    def add_spacing(self, size: int):
        """添加固定间距"""
        if self._layout:
            self._layout.addSpacing(size)
    
    def clear(self):
        """清空布局"""
        if self._layout:
            while self._layout.count():
                child = self._layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
    
    # 属性访问器
    @property
    def spacing(self) -> int:
        """间距"""
        return self._layout.spacing() if self._layout else 0
    
    @spacing.setter
    def spacing(self, value: int):
        """设置间距"""
        self._spacing = value
        if self._layout:
            self._layout.setSpacing(value)
    
    def set_spacing(self, value: int):
        """设置间距（方法形式）"""
        self.spacing = value
    
    def set_margins(self, *args):
        """设置边距"""
        if len(args) == 1:
            margin = args[0]
            self._layout.setContentsMargins(margin, margin, margin, margin)
        elif len(args) == 4:
            self._layout.setContentsMargins(*args)
    
    @property
    def count(self) -> int:
        """子组件数量"""
        return self._layout.count() if self._layout else 0


class Grid(BaseComponent):
    """网格布局容器"""
    
    def __init__(
        self,
        rows: Optional[int] = None,
        columns: Optional[int] = None,
        spacing: Optional[int] = None,
        margins: Optional[Union[int, Tuple[int, int, int, int]]] = None,
        size: ComponentSize = ComponentSize.MEDIUM,
        parent: Optional[QWidget] = None
    ):
        # 布局属性
        self._rows = rows
        self._columns = columns
        self._spacing = spacing
        self._margins = margins
        
        # 内部布局
        self._layout: Optional[QGridLayout] = None
        
        super().__init__(size, parent=parent)
    
    def setup_ui(self):
        """设置UI"""
        # 创建网格布局
        self._layout = QGridLayout(self)
        
        # 设置间距
        if self._spacing is not None:
            self._layout.setSpacing(self._spacing)
        else:
            spacing = design_tokens.get_spacing('3')
            self._layout.setSpacing(spacing)
        
        # 设置边距
        if self._margins is not None:
            if isinstance(self._margins, int):
                self._layout.setContentsMargins(self._margins, self._margins, self._margins, self._margins)
            else:
                self._layout.setContentsMargins(*self._margins)
        else:
            margin = design_tokens.get_spacing('3')
            self._layout.setContentsMargins(margin, margin, margin, margin)
    
    def setup_connections(self):
        """设置信号连接"""
        pass
    
    def update_style(self):
        """更新样式"""
        pass
    
    # 布局管理方法
    def add_widget(
        self,
        widget: QWidget,
        row: int,
        column: int,
        row_span: int = 1,
        column_span: int = 1,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter
    ):
        """添加组件到指定位置"""
        if self._layout:
            self._layout.addWidget(widget, row, column, row_span, column_span, alignment)
    
    def remove_widget(self, widget: QWidget):
        """移除组件"""
        if self._layout:
            self._layout.removeWidget(widget)
            widget.setParent(None)
    
    def set_row_stretch(self, row: int, stretch: int):
        """设置行拉伸"""
        if self._layout:
            self._layout.setRowStretch(row, stretch)
    
    def set_column_stretch(self, column: int, stretch: int):
        """设置列拉伸"""
        if self._layout:
            self._layout.setColumnStretch(column, stretch)
    
    def set_row_minimum_height(self, row: int, height: int):
        """设置行最小高度"""
        if self._layout:
            self._layout.setRowMinimumHeight(row, height)
    
    def set_column_minimum_width(self, column: int, width: int):
        """设置列最小宽度"""
        if self._layout:
            self._layout.setColumnMinimumWidth(column, width)
    
    def clear(self):
        """清空布局"""
        if self._layout:
            while self._layout.count():
                child = self._layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
    
    # 属性访问器
    @property
    def row_count(self) -> int:
        """行数"""
        return self._layout.rowCount() if self._layout else 0
    
    @property
    def column_count(self) -> int:
        """列数"""
        return self._layout.columnCount() if self._layout else 0
    
    @property
    def count(self) -> int:
        """子组件数量"""
        return self._layout.count() if self._layout else 0


class Stack(BaseComponent):
    """堆叠布局容器"""
    
    # 堆叠布局信号
    current_changed = pyqtSignal(int)
    
    def __init__(
        self,
        size: ComponentSize = ComponentSize.MEDIUM,
        parent: Optional[QWidget] = None
    ):
        # 内部布局
        self._layout: Optional[QStackedLayout] = None
        self._widgets: List[QWidget] = []
        
        super().__init__(size, parent=parent)
    
    def setup_ui(self):
        """设置UI"""
        # 创建堆叠布局
        self._layout = QStackedLayout(self)
    
    def setup_connections(self):
        """设置信号连接"""
        if self._layout:
            self._layout.currentChanged.connect(self.current_changed.emit)
    
    def update_style(self):
        """更新样式"""
        pass
    
    # 布局管理方法
    def add_widget(self, widget: QWidget) -> int:
        """添加组件"""
        if self._layout:
            index = self._layout.addWidget(widget)
            self._widgets.append(widget)
            return index
        return -1
    
    def insert_widget(self, index: int, widget: QWidget) -> int:
        """插入组件"""
        if self._layout:
            result = self._layout.insertWidget(index, widget)
            self._widgets.insert(index, widget)
            return result
        return -1
    
    def remove_widget(self, widget: QWidget):
        """移除组件"""
        if self._layout and widget in self._widgets:
            self._layout.removeWidget(widget)
            self._widgets.remove(widget)
            widget.setParent(None)
    
    def set_current_index(self, index: int):
        """设置当前索引"""
        if self._layout and 0 <= index < len(self._widgets):
            self._layout.setCurrentIndex(index)
    
    def set_current_widget(self, widget: QWidget):
        """设置当前组件"""
        if self._layout and widget in self._widgets:
            self._layout.setCurrentWidget(widget)
    
    # 属性访问器
    @property
    def current_index(self) -> int:
        """当前索引"""
        return self._layout.currentIndex() if self._layout else -1
    
    @property
    def current_widget(self) -> Optional[QWidget]:
        """当前组件"""
        return self._layout.currentWidget() if self._layout else None
    
    @property
    def count(self) -> int:
        """组件数量"""
        return len(self._widgets)
    
    def widget_at(self, index: int) -> Optional[QWidget]:
        """获取指定索引的组件"""
        if 0 <= index < len(self._widgets):
            return self._widgets[index]
        return None


class Splitter(BaseComponent):
    """分割器容器"""
    
    # 分割器信号
    splitter_moved = pyqtSignal(int, int)
    
    def __init__(
        self,
        orientation: Qt.Orientation = Qt.Orientation.Horizontal,
        sizes: Optional[List[int]] = None,
        collapsible: bool = True,
        size: ComponentSize = ComponentSize.MEDIUM,
        parent: Optional[QWidget] = None
    ):
        # 分割器属性
        self._orientation = orientation
        self._sizes = sizes or []
        self._collapsible = collapsible
        
        # 内部组件
        self._splitter: Optional[QSplitter] = None
        
        super().__init__(size, parent=parent)
    
    def setup_ui(self):
        """设置UI"""
        # 创建分割器
        self._splitter = QSplitter(self._orientation, self)
        self._splitter.setChildrenCollapsible(self._collapsible)
        
        # 设置布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._splitter)
    
    def setup_connections(self):
        """设置信号连接"""
        if self._splitter:
            self._splitter.splitterMoved.connect(self.splitter_moved.emit)
    
    def update_style(self):
        """更新样式"""
        if not self._splitter:
            return
        
        border_color = design_tokens.get_color('border', 'default')
        primary_color = design_tokens.get_color('primary', '500')
        
        style = f"""
        QSplitter::handle {{
            background-color: {border_color};
        }}
        
        QSplitter::handle:horizontal {{
            width: 2px;
            margin: 2px 0;
        }}
        
        QSplitter::handle:vertical {{
            height: 2px;
            margin: 0 2px;
        }}
        
        QSplitter::handle:hover {{
            background-color: {primary_color};
        }}
        """
        
        self._splitter.setStyleSheet(style)
    
    # 分割器管理方法
    def add_widget(self, widget: QWidget):
        """添加组件"""
        if self._splitter:
            self._splitter.addWidget(widget)
            
            # 应用预设尺寸
            if self._sizes and len(self._sizes) == self._splitter.count():
                self._splitter.setSizes(self._sizes)
    
    def insert_widget(self, index: int, widget: QWidget):
        """插入组件"""
        if self._splitter:
            self._splitter.insertWidget(index, widget)
    
    def remove_widget(self, widget: QWidget):
        """移除组件"""
        if self._splitter:
            widget.setParent(None)
    
    def set_sizes(self, sizes: List[int]):
        """设置分割尺寸"""
        if self._splitter:
            self._splitter.setSizes(sizes)
            self._sizes = sizes
    
    def set_stretch_factor(self, index: int, stretch: int):
        """设置拉伸因子"""
        if self._splitter:
            self._splitter.setStretchFactor(index, stretch)
    
    def set_collapsible(self, index: int, collapsible: bool):
        """设置是否可折叠"""
        if self._splitter:
            self._splitter.setCollapsible(index, collapsible)
    
    # 属性访问器
    @property
    def orientation(self) -> Qt.Orientation:
        """方向"""
        return self._orientation
    
    @orientation.setter
    def orientation(self, value: Qt.Orientation):
        """设置方向"""
        self._orientation = value
        if self._splitter:
            self._splitter.setOrientation(value)
    
    @property
    def sizes(self) -> List[int]:
        """分割尺寸"""
        return self._splitter.sizes() if self._splitter else []
    
    @property
    def count(self) -> int:
        """组件数量"""
        return self._splitter.count() if self._splitter else 0


class ScrollArea(BaseComponent):
    """滚动区域容器"""
    
    def __init__(
        self,
        widget: Optional[QWidget] = None,
        horizontal_policy: Qt.ScrollBarPolicy = Qt.ScrollBarPolicy.ScrollBarAsNeeded,
        vertical_policy: Qt.ScrollBarPolicy = Qt.ScrollBarPolicy.ScrollBarAsNeeded,
        widget_resizable: bool = True,
        size: ComponentSize = ComponentSize.MEDIUM,
        parent: Optional[QWidget] = None
    ):
        # 滚动区域属性
        self._content_widget = widget
        self._horizontal_policy = horizontal_policy
        self._vertical_policy = vertical_policy
        self._widget_resizable = widget_resizable
        
        # 内部组件
        self._scroll_area: Optional[QScrollArea] = None
        
        super().__init__(size, parent=parent)
    
    def setup_ui(self):
        """设置UI"""
        # 创建滚动区域
        self._scroll_area = QScrollArea(self)
        self._scroll_area.setHorizontalScrollBarPolicy(self._horizontal_policy)
        self._scroll_area.setVerticalScrollBarPolicy(self._vertical_policy)
        self._scroll_area.setWidgetResizable(self._widget_resizable)
        
        # 设置内容组件
        if self._content_widget:
            self._scroll_area.setWidget(self._content_widget)
        
        # 设置布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._scroll_area)
    
    def setup_connections(self):
        """设置信号连接"""
        pass
    
    def update_style(self):
        """更新样式"""
        if not self._scroll_area:
            return
        
        border_color = design_tokens.get_color('border', 'default')
        background_color = design_tokens.get_color('background', 'default')
        surface_color = design_tokens.get_color('surface', 'default')
        text_secondary_color = design_tokens.get_color('text', 'secondary')
        text_primary_color = design_tokens.get_color('text', 'primary')
        border_radius = design_tokens.get_border_radius('medium')
        
        style = f"""
        QScrollArea {{
            border: 1px solid {border_color};
            border-radius: {border_radius}px;
            background-color: {background_color};
        }}
        
        QScrollBar:vertical {{
            background-color: {surface_color};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {text_secondary_color};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {text_primary_color};
        }}
        
        QScrollBar:horizontal {{
            background-color: {surface_color};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {text_secondary_color};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {text_primary_color};
        }}
        
        QScrollBar::add-line, QScrollBar::sub-line {{
            border: none;
            background: none;
        }}
        """
        
        self._scroll_area.setStyleSheet(style)
    
    # 滚动区域管理方法
    def set_widget(self, widget: QWidget):
        """设置内容组件"""
        if self._scroll_area:
            self._scroll_area.setWidget(widget)
            self._content_widget = widget
    
    def take_widget(self) -> Optional[QWidget]:
        """取出内容组件"""
        if self._scroll_area:
            widget = self._scroll_area.takeWidget()
            self._content_widget = None
            return widget
        return None
    
    def ensure_visible(self, x: int, y: int, x_margin: int = 50, y_margin: int = 50):
        """确保指定位置可见"""
        if self._scroll_area:
            self._scroll_area.ensureVisible(x, y, x_margin, y_margin)
    
    def ensure_widget_visible(self, widget: QWidget, x_margin: int = 50, y_margin: int = 50):
        """确保指定组件可见"""
        if self._scroll_area:
            self._scroll_area.ensureWidgetVisible(widget, x_margin, y_margin)
    
    # 属性访问器
    @property
    def widget(self) -> Optional[QWidget]:
        """内容组件"""
        return self._content_widget
    
    @property
    def viewport(self) -> Optional[QWidget]:
        """视口组件"""
        return self._scroll_area.viewport() if self._scroll_area else None
    
    @property
    def horizontal_scrollbar_policy(self) -> Qt.ScrollBarPolicy:
        """水平滚动条策略"""
        return self._horizontal_policy
    
    @horizontal_scrollbar_policy.setter
    def horizontal_scrollbar_policy(self, value: Qt.ScrollBarPolicy):
        """设置水平滚动条策略"""
        self._horizontal_policy = value
        if self._scroll_area:
            self._scroll_area.setHorizontalScrollBarPolicy(value)
    
    @property
    def vertical_scrollbar_policy(self) -> Qt.ScrollBarPolicy:
        """垂直滚动条策略"""
        return self._vertical_policy
    
    @vertical_scrollbar_policy.setter
    def vertical_scrollbar_policy(self, value: Qt.ScrollBarPolicy):
        """设置垂直滚动条策略"""
        self._vertical_policy = value
        if self._scroll_area:
            self._scroll_area.setVerticalScrollBarPolicy(value)


class ResponsiveContainer(BaseComponent):
    """响应式容器"""
    
    # 响应式信号
    breakpoint_changed = pyqtSignal(str)
    
    def __init__(
        self,
        breakpoints: Optional[dict] = None,
        size: ComponentSize = ComponentSize.MEDIUM,
        parent: Optional[QWidget] = None
    ):
        # 响应式属性
        self._breakpoints = breakpoints or {
            'xs': 0,
            'sm': 576,
            'md': 768,
            'lg': 992,
            'xl': 1200
        }
        self._current_breakpoint = 'xs'
        
        # 内部布局
        self._layout: Optional[QVBoxLayout] = None
        self._content_widgets: dict = {}  # breakpoint -> widget
        
        super().__init__(size, parent=parent)
    
    def setup_ui(self):
        """设置UI"""
        # 创建主布局
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        
        # 初始化断点
        self._update_breakpoint()
    
    def setup_connections(self):
        """设置信号连接"""
        pass
    
    def update_style(self):
        """更新样式"""
        pass
    
    def resizeEvent(self, event: QResizeEvent):
        """窗口大小变化事件"""
        super().resizeEvent(event)
        self._update_breakpoint()
    
    def _update_breakpoint(self):
        """更新断点"""
        width = self.width()
        new_breakpoint = 'xs'
        
        # 找到匹配的断点
        for name, min_width in sorted(self._breakpoints.items(), key=lambda x: x[1], reverse=True):
            if width >= min_width:
                new_breakpoint = name
                break
        
        # 如果断点发生变化
        if new_breakpoint != self._current_breakpoint:
            old_breakpoint = self._current_breakpoint
            self._current_breakpoint = new_breakpoint
            
            # 切换内容
            self._switch_content(old_breakpoint, new_breakpoint)
            
            # 发射信号
            self.breakpoint_changed.emit(new_breakpoint)
    
    def _switch_content(self, old_breakpoint: str, new_breakpoint: str):
        """切换内容"""
        # 隐藏旧内容
        if old_breakpoint in self._content_widgets:
            old_widget = self._content_widgets[old_breakpoint]
            if old_widget:
                old_widget.hide()
        
        # 显示新内容
        if new_breakpoint in self._content_widgets:
            new_widget = self._content_widgets[new_breakpoint]
            if new_widget:
                new_widget.show()
    
    # 响应式管理方法
    def set_content(self, breakpoint: str, widget: QWidget):
        """设置指定断点的内容"""
        # 移除旧内容
        if breakpoint in self._content_widgets:
            old_widget = self._content_widgets[breakpoint]
            if old_widget:
                self._layout.removeWidget(old_widget)
                old_widget.setParent(None)
        
        # 添加新内容
        self._content_widgets[breakpoint] = widget
        self._layout.addWidget(widget)
        
        # 根据当前断点显示/隐藏
        if breakpoint == self._current_breakpoint:
            widget.show()
        else:
            widget.hide()
    
    def remove_content(self, breakpoint: str):
        """移除指定断点的内容"""
        if breakpoint in self._content_widgets:
            widget = self._content_widgets[breakpoint]
            if widget:
                self._layout.removeWidget(widget)
                widget.setParent(None)
            del self._content_widgets[breakpoint]
    
    # 属性访问器
    @property
    def current_breakpoint(self) -> str:
        """当前断点"""
        return self._current_breakpoint
    
    @property
    def breakpoints(self) -> dict:
        """断点配置"""
        return self._breakpoints.copy()
    
    def get_content(self, breakpoint: str) -> Optional[QWidget]:
        """获取指定断点的内容"""
        return self._content_widgets.get(breakpoint)