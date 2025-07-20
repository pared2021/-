"""现代化输入组件"""

from typing import Optional, Union, Callable
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit,
    QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QRadioButton, QSlider, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QValidator, QIntValidator, QDoubleValidator, QRegularExpressionValidator

from .base import BaseComponent
from .typography import Typography
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_tokens import ComponentSize, ComponentVariant, design_tokens
from style_generator import style_generator


class Input(BaseComponent):
    """现代化输入框组件"""
    
    # 输入框信号
    value_changed = pyqtSignal(str)
    focus_in = pyqtSignal()
    focus_out = pyqtSignal()
    enter_pressed = pyqtSignal()
    
    def __init__(
        self,
        placeholder: str = "",
        value: str = "",
        label: str = "",
        helper_text: str = "",
        error_text: str = "",
        size: ComponentSize = ComponentSize.MEDIUM,
        variant: ComponentVariant = ComponentVariant.PRIMARY,
        multiline: bool = False,
        password: bool = False,
        readonly: bool = False,
        required: bool = False,
        validator: Optional[QValidator] = None,
        max_length: Optional[int] = None,
        debounce_ms: int = 300,
        parent: Optional[QWidget] = None
    ):
        # 输入框特有属性
        self._placeholder = placeholder
        self._value = value
        self._label = label
        self._helper_text = helper_text
        self._error_text = error_text
        self._multiline = multiline
        self._password = password
        self._readonly = readonly
        self._required = required
        self._validator = validator
        self._max_length = max_length
        self._debounce_ms = debounce_ms
        
        # 状态
        self._has_error = bool(error_text)
        self._is_focused = False
        
        # 内部组件
        self._label_widget: Optional[Typography] = None
        self._input_widget: Optional[Union[QLineEdit, QTextEdit]] = None
        self._helper_widget: Optional[Typography] = None
        self._error_widget: Optional[Typography] = None
        
        # 布局
        self._main_layout: Optional[QVBoxLayout] = None
        
        # 防抖定时器
        self._debounce_timer: Optional[QTimer] = None
        
        super().__init__(size, variant, False, parent)
    
    def setup_ui(self):
        """设置UI"""
        # 主布局
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(design_tokens.get_spacing('1'))
        
        # 设置各个部分
        self._setup_label()
        self._setup_input()
        self._setup_helper()
        
        # 设置防抖定时器
        if self._debounce_ms > 0:
            self._setup_debounce()
    
    def _setup_label(self):
        """设置标签"""
        if not self._label:
            return
        
        label_text = self._label
        if self._required:
            label_text += " *"
        
        self._label_widget = Typography(
            text=label_text,
            variant='body',
            size='small',
            color='text.primary'
        )
        self._main_layout.addWidget(self._label_widget)
    
    def _setup_input(self):
        """设置输入框"""
        if self._multiline:
            self._input_widget = QTextEdit()
            self._input_widget.setPlainText(self._value)
            if self._placeholder:
                self._input_widget.setPlaceholderText(self._placeholder)
        else:
            self._input_widget = QLineEdit()
            self._input_widget.setText(self._value)
            if self._placeholder:
                self._input_widget.setPlaceholderText(self._placeholder)
            
            # 密码模式
            if self._password:
                self._input_widget.setEchoMode(QLineEdit.EchoMode.Password)
        
        # 通用设置
        self._input_widget.setReadOnly(self._readonly)
        
        # 验证器
        if self._validator and isinstance(self._input_widget, QLineEdit):
            self._input_widget.setValidator(self._validator)
        
        # 最大长度
        if self._max_length:
            if isinstance(self._input_widget, QLineEdit):
                self._input_widget.setMaxLength(self._max_length)
        
        self._main_layout.addWidget(self._input_widget)
    
    def _setup_helper(self):
        """设置帮助文本"""
        # 错误文本优先
        if self._error_text:
            self._error_widget = Typography(
                text=self._error_text,
                variant='body',
                size='small',
                color='semantic.error'
            )
            self._main_layout.addWidget(self._error_widget)
        elif self._helper_text:
            self._helper_widget = Typography(
                text=self._helper_text,
                variant='body',
                size='small',
                color='text.secondary'
            )
            self._main_layout.addWidget(self._helper_widget)
    
    def _setup_debounce(self):
        """设置防抖"""
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._emit_value_changed)
    
    def _emit_value_changed(self):
        """发射值变化信号"""
        current_value = self.value
        if current_value != self._value:
            self._value = current_value
            self.value_changed.emit(current_value)
    
    def _handle_text_changed(self):
        """处理文本变化"""
        if self._debounce_timer:
            self._debounce_timer.start(self._debounce_ms)
        else:
            self._emit_value_changed()
    
    def _handle_focus_in(self):
        """处理获得焦点"""
        self._is_focused = True
        self.focus_in.emit()
        self.update_style()
    
    def _handle_focus_out(self):
        """处理失去焦点"""
        self._is_focused = False
        self.focus_out.emit()
        self.update_style()
    
    def _handle_return_pressed(self):
        """处理回车键"""
        self.enter_pressed.emit()
    
    def setup_connections(self):
        """设置信号连接"""
        if isinstance(self._input_widget, QLineEdit):
            self._input_widget.textChanged.connect(self._handle_text_changed)
            self._input_widget.returnPressed.connect(self._handle_return_pressed)
        elif isinstance(self._input_widget, QTextEdit):
            self._input_widget.textChanged.connect(self._handle_text_changed)
        
        # 焦点事件需要重写事件处理器
        if self._input_widget:
            original_focus_in = self._input_widget.focusInEvent
            original_focus_out = self._input_widget.focusOutEvent
            
            def focus_in_event(event):
                original_focus_in(event)
                self._handle_focus_in()
            
            def focus_out_event(event):
                original_focus_out(event)
                self._handle_focus_out()
            
            self._input_widget.focusInEvent = focus_in_event
            self._input_widget.focusOutEvent = focus_out_event
    
    def update_style(self):
        """更新样式"""
        if not self._input_widget:
            return
        
        # 生成样式缓存键
        style_key = self._generate_style_key(
            has_error=self._has_error,
            is_focused=self._is_focused,
            readonly=self._readonly,
            multiline=self._multiline
        )
        
        # 检查缓存
        cached_style = self._get_cached_style(style_key)
        if cached_style:
            self._input_widget.setStyleSheet(cached_style)
            return
        
        # 生成新样式
        style = style_generator.generate_input_style(
            size=self._size,
            error=self._has_error
        )
        
        # 缓存并应用样式
        self._cache_style(style_key, style)
        self._input_widget.setStyleSheet(style)
    
    # 验证方法
    def validate(self) -> bool:
        """验证输入"""
        current_value = self.value
        
        # 必填验证
        if self._required and not current_value.strip():
            self.set_error("此字段为必填项")
            return False
        
        # 验证器验证
        if self._validator and isinstance(self._input_widget, QLineEdit):
            state, _, _ = self._validator.validate(current_value, 0)
            if state != QValidator.State.Acceptable:
                self.set_error("输入格式不正确")
                return False
        
        # 清除错误
        self.clear_error()
        return True
    
    def set_error(self, error_text: str):
        """设置错误状态"""
        self._error_text = error_text
        self._has_error = True
        
        # 更新错误显示
        if self._error_widget:
            self._error_widget.text = error_text
        elif self._helper_widget:
            # 隐藏帮助文本，显示错误文本
            self._helper_widget.hide()
            self._error_widget = Typography(
                text=error_text,
                variant='body',
                size='small',
                color='semantic.error'
            )
            self._main_layout.addWidget(self._error_widget)
        else:
            # 创建错误文本
            self._error_widget = Typography(
                text=error_text,
                variant='body',
                size='small',
                color='semantic.error'
            )
            self._main_layout.addWidget(self._error_widget)
        
        self.update_style()
    
    def clear_error(self):
        """清除错误状态"""
        self._error_text = ""
        self._has_error = False
        
        # 隐藏错误文本
        if self._error_widget:
            self._error_widget.hide()
            self._error_widget.deleteLater()
            self._error_widget = None
        
        # 显示帮助文本
        if self._helper_text and self._helper_widget:
            self._helper_widget.show()
        
        self.update_style()
    
    # 属性访问器
    @property
    def value(self) -> str:
        """输入值"""
        if not self._input_widget:
            return self._value
        
        if isinstance(self._input_widget, QLineEdit):
            return self._input_widget.text()
        elif isinstance(self._input_widget, QTextEdit):
            return self._input_widget.toPlainText()
        return ""
    
    @value.setter
    def value(self, value: str):
        """设置输入值"""
        self._value = value
        if self._input_widget:
            if isinstance(self._input_widget, QLineEdit):
                self._input_widget.setText(value)
            elif isinstance(self._input_widget, QTextEdit):
                self._input_widget.setPlainText(value)
    
    @property
    def placeholder(self) -> str:
        """占位符"""
        return self._placeholder
    
    @placeholder.setter
    def placeholder(self, value: str):
        """设置占位符"""
        self._placeholder = value
        if self._input_widget:
            self._input_widget.setPlaceholderText(value)
    
    @property
    def readonly(self) -> bool:
        """是否只读"""
        return self._readonly
    
    @readonly.setter
    def readonly(self, value: bool):
        """设置只读状态"""
        if self._readonly != value:
            self._readonly = value
            if self._input_widget:
                self._input_widget.setReadOnly(value)
            self.update_style()
    
    @property
    def has_error(self) -> bool:
        """是否有错误"""
        return self._has_error
    
    def focus(self):
        """设置焦点"""
        if self._input_widget:
            self._input_widget.setFocus()
    
    def select_all(self):
        """选择全部文本"""
        if isinstance(self._input_widget, QLineEdit):
            self._input_widget.selectAll()
        elif isinstance(self._input_widget, QTextEdit):
            self._input_widget.selectAll()
    
    def clear(self):
        """清空输入"""
        if self._input_widget:
            if isinstance(self._input_widget, QLineEdit):
                self._input_widget.clear()
            elif isinstance(self._input_widget, QTextEdit):
                self._input_widget.clear()


class NumberInput(Input):
    """数字输入框"""
    
    def __init__(
        self,
        value: Union[int, float] = 0,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        step: Union[int, float] = 1,
        decimals: int = 0,
        size: ComponentSize = ComponentSize.MEDIUM,
        parent: Optional[QWidget] = None
    ):
        self._min_value = min_value
        self._max_value = max_value
        self._step = step
        self._decimals = decimals
        
        # 设置验证器
        if decimals > 0:
            validator = QDoubleValidator()
            if min_value is not None:
                validator.setBottom(float(min_value))
            if max_value is not None:
                validator.setTop(float(max_value))
            validator.setDecimals(decimals)
        else:
            validator = QIntValidator()
            if min_value is not None:
                validator.setBottom(int(min_value))
            if max_value is not None:
                validator.setTop(int(max_value))
        
        super().__init__(
            value=str(value),
            validator=validator,
            size=size,
            parent=parent
        )
    
    @property
    def numeric_value(self) -> Union[int, float]:
        """数字值"""
        try:
            if self._decimals > 0:
                return float(self.value)
            else:
                return int(self.value)
        except ValueError:
            return 0
    
    @numeric_value.setter
    def numeric_value(self, value: Union[int, float]):
        """设置数字值"""
        if self._decimals > 0:
            self.value = f"{float(value):.{self._decimals}f}"
        else:
            self.value = str(int(value))


class SearchInput(Input):
    """搜索输入框"""
    
    # 搜索信号
    search_requested = pyqtSignal(str)
    
    def __init__(
        self,
        placeholder: str = "搜索...",
        size: ComponentSize = ComponentSize.MEDIUM,
        parent: Optional[QWidget] = None
    ):
        super().__init__(
            placeholder=placeholder,
            size=size,
            debounce_ms=500,  # 搜索防抖时间更长
            parent=parent
        )
    
    def setup_connections(self):
        """设置信号连接"""
        super().setup_connections()
        
        # 连接搜索信号
        self.value_changed.connect(self.search_requested.emit)
        self.enter_pressed.connect(lambda: self.search_requested.emit(self.value))


class PasswordInput(Input):
    """密码输入框"""
    
    def __init__(
        self,
        placeholder: str = "请输入密码",
        show_strength: bool = True,
        size: ComponentSize = ComponentSize.MEDIUM,
        parent: Optional[QWidget] = None
    ):
        self._show_strength = show_strength
        self._strength_widget: Optional[Typography] = None
        
        super().__init__(
            placeholder=placeholder,
            password=True,
            size=size,
            parent=parent
        )
    
    def setup_ui(self):
        """设置UI"""
        super().setup_ui()
        
        if self._show_strength:
            self._setup_strength_indicator()
    
    def _setup_strength_indicator(self):
        """设置密码强度指示器"""
        self._strength_widget = Typography(
            text="密码强度: 弱",
            variant='body',
            size='small',
            color='text.secondary'
        )
        self._main_layout.addWidget(self._strength_widget)
    
    def setup_connections(self):
        """设置信号连接"""
        super().setup_connections()
        
        if self._show_strength:
            self.value_changed.connect(self._update_strength)
    
    def _update_strength(self, password: str):
        """更新密码强度"""
        if not self._strength_widget:
            return
        
        strength = self._calculate_strength(password)
        
        if strength < 2:
            text = "密码强度: 弱"
            color = 'semantic.error'
        elif strength < 4:
            text = "密码强度: 中"
            color = 'semantic.warning'
        else:
            text = "密码强度: 强"
            color = 'semantic.success'
        
        self._strength_widget.text = text
        self._strength_widget.color = color
    
    def _calculate_strength(self, password: str) -> int:
        """计算密码强度"""
        strength = 0
        
        if len(password) >= 8:
            strength += 1
        if any(c.islower() for c in password):
            strength += 1
        if any(c.isupper() for c in password):
            strength += 1
        if any(c.isdigit() for c in password):
            strength += 1
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            strength += 1
        
        return strength