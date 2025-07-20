"""基础组件类 - 所有组件的基类"""

from abc import ABC, ABCMeta, abstractmethod
from typing import Optional, Dict, Any, Union
from PyQt6.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtSignal, QRect, QTimer
from PyQt6.QtGui import QColor

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from design_tokens import design_tokens, ComponentSize, ComponentVariant
from style_generator import StyleGenerator


class ComponentMeta(type(QWidget), ABCMeta):
    """解决QWidget和ABC元类冲突的自定义元类"""
    pass


class BaseComponent(QWidget, ABC, metaclass=ComponentMeta):
    """基础组件类"""
    
    # 通用信号
    size_changed = pyqtSignal(ComponentSize)
    variant_changed = pyqtSignal(ComponentVariant)
    theme_changed = pyqtSignal()
    
    def __init__(
        self,
        size: ComponentSize = ComponentSize.MEDIUM,
        variant: ComponentVariant = ComponentVariant.PRIMARY,
        disabled: bool = False,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        
        # 组件属性
        self._size = size
        self._variant = variant
        self._disabled = disabled
        self._animated = True
        self._shadow_enabled = True
        
        # 动画对象
        self._animations: Dict[str, QPropertyAnimation] = {}
        
        # 样式缓存
        self._style_cache: Dict[str, str] = {}
        
        # 初始化组件
        self._init_component()
    
    def _init_component(self):
        """初始化组件"""
        self._setup_base_properties()
        self._setup_animations()
        self._apply_base_style()
        self._setup_shadow()
        
        # 子类实现具体初始化
        self.setup_ui()
        self.setup_connections()
        self.update_style()
    
    def _setup_base_properties(self):
        """设置基础属性"""
        self.setEnabled(not self._disabled)
        
        # 设置对象名称用于样式选择器
        class_name = self.__class__.__name__.lower()
        variant_str = self._variant.value if hasattr(self._variant, 'value') else str(self._variant)
        size_str = self._size.value if hasattr(self._size, 'value') else str(self._size)
        self.setObjectName(f"{class_name}_{variant_str}_{size_str}")
    
    def _setup_animations(self):
        """设置动画"""
        if not self._animated:
            return
        
        # 悬浮动画
        self._animations['hover'] = QPropertyAnimation(self, b"geometry")
        self._animations['hover'].setDuration(design_tokens.get_animation('fast').duration)
        self._animations['hover'].setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 点击动画
        self._animations['press'] = QPropertyAnimation(self, b"geometry")
        self._animations['press'].setDuration(design_tokens.get_animation('fast').duration)
        self._animations['press'].setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def _apply_base_style(self):
        """应用基础样式"""
        # 子类可以重写此方法来应用特定样式
        pass
    
    def _setup_shadow(self):
        """设置阴影效果"""
        if not self._shadow_enabled:
            return
        
        shadow_token = design_tokens.get_shadow('sm')
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(shadow_token.blur_radius)
        shadow.setColor(QColor(shadow_token.color))
        shadow.setOffset(shadow_token.x_offset, shadow_token.y_offset)
        self.setGraphicsEffect(shadow)
    
    @abstractmethod
    def setup_ui(self):
        """设置UI - 子类必须实现"""
        pass
    
    def setup_connections(self):
        """设置信号连接 - 子类可以重写"""
        pass
    
    @abstractmethod
    def update_style(self):
        """更新样式 - 子类必须实现"""
        pass
    
    # 属性访问器
    @property
    def size(self) -> ComponentSize:
        """组件尺寸"""
        return self._size
    
    @size.setter
    def size(self, value: ComponentSize):
        """设置组件尺寸"""
        if self._size != value:
            self._size = value
            self._invalidate_style_cache()
            self.update_style()
            self.size_changed.emit(value)
    
    @property
    def variant(self) -> ComponentVariant:
        """组件变体"""
        return self._variant
    
    @variant.setter
    def variant(self, value: ComponentVariant):
        """设置组件变体"""
        if self._variant != value:
            self._variant = value
            self._invalidate_style_cache()
            self.update_style()
            self.variant_changed.emit(value)
    
    @property
    def disabled(self) -> bool:
        """是否禁用"""
        return self._disabled
    
    @disabled.setter
    def disabled(self, value: bool):
        """设置禁用状态"""
        if self._disabled != value:
            self._disabled = value
            self.setEnabled(not value)
            self.update_style()
    
    @property
    def animated(self) -> bool:
        """是否启用动画"""
        return self._animated
    
    @animated.setter
    def animated(self, value: bool):
        """设置动画启用状态"""
        self._animated = value
        if value:
            self._setup_animations()
        else:
            self._clear_animations()
    
    @property
    def shadow_enabled(self) -> bool:
        """是否启用阴影"""
        return self._shadow_enabled
    
    @shadow_enabled.setter
    def shadow_enabled(self, value: bool):
        """设置阴影启用状态"""
        self._shadow_enabled = value
        if value:
            self._setup_shadow()
        else:
            self.setGraphicsEffect(None)
    
    # 样式管理
    def _get_cached_style(self, key: str) -> Optional[str]:
        """获取缓存的样式"""
        return self._style_cache.get(key)
    
    def _cache_style(self, key: str, style: str):
        """缓存样式"""
        self._style_cache[key] = style
    
    def _invalidate_style_cache(self):
        """清空样式缓存"""
        self._style_cache.clear()
    
    def _generate_style_key(self, **kwargs) -> str:
        """生成样式缓存键"""
        size_str = self._size.value if hasattr(self._size, 'value') else str(self._size)
        variant_str = self._variant.value if hasattr(self._variant, 'value') else str(self._variant)
        key_parts = [
            f"size_{size_str}",
            f"variant_{variant_str}",
            f"disabled_{self._disabled}",
        ]
        
        for k, v in kwargs.items():
            key_parts.append(f"{k}_{v}")
        
        return "_".join(key_parts)
    
    # 动画方法
    def _clear_animations(self):
        """清除所有动画"""
        for animation in list(self._animations.values()):
            try:
                if animation is not None:
                    animation.stop()
            except RuntimeError:
                # QPropertyAnimation已被Qt删除，忽略错误
                pass
        self._animations.clear()
    
    def _animate_hover_enter(self):
        """悬浮进入动画"""
        if not self._animated or 'hover' not in self._animations:
            return
        
        current_rect = self.geometry()
        target_rect = QRect(
            current_rect.x(),
            current_rect.y() - 2,
            current_rect.width(),
            current_rect.height()
        )
        
        animation = self._animations['hover']
        animation.setStartValue(current_rect)
        animation.setEndValue(target_rect)
        animation.start()
    
    def _animate_hover_leave(self):
        """悬浮离开动画"""
        if not self._animated or 'hover' not in self._animations:
            return
        
        current_rect = self.geometry()
        target_rect = QRect(
            current_rect.x(),
            current_rect.y() + 2,
            current_rect.width(),
            current_rect.height()
        )
        
        animation = self._animations['hover']
        animation.setStartValue(current_rect)
        animation.setEndValue(target_rect)
        animation.start()
    
    def _animate_press(self):
        """按压动画"""
        if not self._animated or 'press' not in self._animations:
            return
        
        current_rect = self.geometry()
        target_rect = QRect(
            current_rect.x(),
            current_rect.y() + 1,
            current_rect.width(),
            current_rect.height()
        )
        
        animation = self._animations['press']
        animation.setStartValue(current_rect)
        animation.setEndValue(target_rect)
        animation.start()
    
    def _animate_release(self):
        """释放动画"""
        if not self._animated or 'press' not in self._animations:
            return
        
        current_rect = self.geometry()
        target_rect = QRect(
            current_rect.x(),
            current_rect.y() - 1,
            current_rect.width(),
            current_rect.height()
        )
        
        animation = self._animations['press']
        animation.setStartValue(current_rect)
        animation.setEndValue(target_rect)
        animation.start()
    
    # 事件处理
    def enterEvent(self, event):
        """鼠标进入事件"""
        super().enterEvent(event)
        self._animate_hover_enter()
        self._update_shadow_on_hover(True)
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        super().leaveEvent(event)
        self._animate_hover_leave()
        self._update_shadow_on_hover(False)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        super().mousePressEvent(event)
        self._animate_press()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        super().mouseReleaseEvent(event)
        self._animate_release()
    
    def _update_shadow_on_hover(self, hovered: bool):
        """更新悬浮时的阴影效果"""
        if not self._shadow_enabled or not self.graphicsEffect():
            return
        
        shadow = self.graphicsEffect()
        if isinstance(shadow, QGraphicsDropShadowEffect):
            if hovered:
                shadow.setBlurRadius(shadow.blurRadius() + 5)
                shadow.setOffset(shadow.xOffset(), shadow.yOffset() + 2)
            else:
                shadow_token = design_tokens.get_shadow('sm')
                shadow.setBlurRadius(shadow_token.blur_radius)
                shadow.setOffset(shadow_token.x_offset, shadow_token.y_offset)
    
    # 工具方法
    def set_custom_property(self, name: str, value: Any):
        """设置自定义属性"""
        self.setProperty(name, value)
        self.update_style()
    
    def get_custom_property(self, name: str, default: Any = None) -> Any:
        """获取自定义属性"""
        return self.property(name) or default
    
    def apply_style_sheet(self, style: str):
        """应用样式表"""
        self.setStyleSheet(style)
    
    def get_design_token(self, category: str, key: str) -> Any:
        """获取设计token"""
        if category == 'color':
            parts = key.split('.')
            if len(parts) == 2:
                return design_tokens.get_color(parts[0], parts[1])
        elif category == 'spacing':
            return design_tokens.get_spacing(key)
        elif category == 'typography':
            parts = key.split('.')
            if len(parts) == 2:
                return design_tokens.get_typography(parts[0], parts[1])
        elif category == 'shadow':
            return design_tokens.get_shadow(key)
        elif category == 'border_radius':
            return design_tokens.get_border_radius(key)
        elif category == 'animation':
            return design_tokens.get_animation(key)
        
        return None
    
    def refresh_theme(self):
        """刷新主题"""
        self._invalidate_style_cache()
        self.update_style()
        self._setup_shadow()
        self.theme_changed.emit()
    
    def __del__(self):
        """析构函数"""
        self._clear_animations()