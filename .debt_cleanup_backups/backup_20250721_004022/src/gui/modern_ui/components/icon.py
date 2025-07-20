"""现代化图标组件"""

from typing import Optional, Union, Dict, Any
from PyQt6.QtWidgets import QLabel, QWidget, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QColor, QFont, QFontMetrics
from PyQt6.QtSvgWidgets import QSvgWidget

from .base import BaseComponent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_tokens import design_tokens, ComponentSize


class Icon(BaseComponent):
    """现代化图标组件"""
    
    # 图标信号
    clicked = pyqtSignal()
    
    def __init__(
        self,
        icon: Union[str, QIcon, QPixmap] = "",
        icon_type: str = "material",  # material, fontawesome, custom, svg
        icon_size: Union[int, QSize] = 24,
        color: str = "text.primary",
        clickable: bool = False,
        rotation: float = 0.0,
        opacity: float = 1.0,
        component_size: ComponentSize = ComponentSize.MEDIUM,
        parent: Optional[QWidget] = None
    ):
        # 图标属性
        self._icon = icon
        self._icon_type = icon_type
        self._icon_size = icon_size if isinstance(icon_size, QSize) else QSize(icon_size, icon_size)
        self._color = color
        self._clickable = clickable
        self._rotation = rotation
        self._opacity = opacity
        
        # 内部组件
        self._widget: Optional[QWidget] = None
        self._rotation_animation: Optional[QPropertyAnimation] = None
        
        # 图标缓存
        self._icon_cache: Dict[str, Any] = {}
        
        super().__init__(size=component_size, parent=parent)
    
    def setup_ui(self):
        """设置UI"""
        # 根据图标类型创建组件
        if self._icon_type == "svg" and isinstance(self._icon, str):
            self._widget = QSvgWidget(self._icon, self)
        else:
            if self._clickable:
                self._widget = QPushButton(self)
                self._widget.setFlat(True)
                self._widget.setStyleSheet("QPushButton { border: none; background: transparent; }")
            else:
                self._widget = QLabel(self)
                self._widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 设置大小
        self._widget.setFixedSize(self._icon_size)
        
        # 设置图标
        self._update_icon()
        
        # 设置点击状态
        if self._clickable:
            self._widget.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def setup_connections(self):
        """设置信号连接"""
        if self._clickable and isinstance(self._widget, QPushButton):
            self._widget.clicked.connect(self.clicked.emit)
        elif self._clickable and isinstance(self._widget, QLabel):
            # 为QLabel添加点击事件
            self._widget.mousePressEvent = lambda event: self.clicked.emit()
    
    def _update_icon(self):
        """更新图标"""
        if not self._widget:
            return
        
        # 生成缓存键
        cache_key = self._generate_icon_cache_key()
        
        # 检查缓存
        if cache_key in self._icon_cache:
            cached_icon = self._icon_cache[cache_key]
            self._apply_icon(cached_icon)
            return
        
        # 生成新图标
        icon_data = self._generate_icon()
        
        # 缓存图标
        self._icon_cache[cache_key] = icon_data
        
        # 应用图标
        self._apply_icon(icon_data)
    
    def _generate_icon_cache_key(self) -> str:
        """生成图标缓存键"""
        return f"{self._icon}_{self._icon_type}_{self._icon_size.width()}x{self._icon_size.height()}_{self._color}_{self._rotation}_{self._opacity}"
    
    def _generate_icon(self) -> Dict[str, Any]:
        """生成图标数据"""
        if self._icon_type == "material":
            return self._generate_material_icon()
        elif self._icon_type == "fontawesome":
            return self._generate_fontawesome_icon()
        elif self._icon_type == "custom":
            return self._generate_custom_icon()
        elif self._icon_type == "svg":
            return self._generate_svg_icon()
        else:
            return self._generate_default_icon()
    
    def _generate_material_icon(self) -> Dict[str, Any]:
        """生成Material图标"""
        # Material Icons字体图标
        if isinstance(self._icon, str):
            # 创建字体图标
            font = QFont("Material Icons")
            font.setPixelSize(min(self._icon_size.width(), self._icon_size.height()))
            
            # 获取颜色
            color = self._get_color()
            
            # 创建像素图
            pixmap = QPixmap(self._icon_size)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            painter.setFont(font)
            painter.setPen(QColor(color))
            painter.setOpacity(self._opacity)
            
            # 绘制图标文字
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, self._icon)
            
            # 应用旋转
            if self._rotation != 0:
                transform = painter.transform()
                transform.rotate(self._rotation)
                painter.setTransform(transform)
            
            painter.end()
            
            return {'type': 'pixmap', 'data': pixmap}
        
        return self._generate_default_icon()
    
    def _generate_fontawesome_icon(self) -> Dict[str, Any]:
        """生成FontAwesome图标"""
        # FontAwesome字体图标
        if isinstance(self._icon, str):
            # 创建字体图标
            font = QFont("Font Awesome 5 Free")
            font.setPixelSize(min(self._icon_size.width(), self._icon_size.height()))
            
            # 获取颜色
            color = self._get_color()
            
            # 创建像素图
            pixmap = QPixmap(self._icon_size)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            painter.setFont(font)
            painter.setPen(QColor(color))
            painter.setOpacity(self._opacity)
            
            # 绘制图标文字
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, self._icon)
            
            # 应用旋转
            if self._rotation != 0:
                transform = painter.transform()
                transform.rotate(self._rotation)
                painter.setTransform(transform)
            
            painter.end()
            
            return {'type': 'pixmap', 'data': pixmap}
        
        return self._generate_default_icon()
    
    def _generate_custom_icon(self) -> Dict[str, Any]:
        """生成自定义图标"""
        if isinstance(self._icon, QIcon):
            return {'type': 'qicon', 'data': self._icon}
        elif isinstance(self._icon, QPixmap):
            return {'type': 'pixmap', 'data': self._icon}
        elif isinstance(self._icon, str):
            # 尝试从文件加载
            try:
                pixmap = QPixmap(self._icon)
                if not pixmap.isNull():
                    # 缩放到指定大小
                    scaled_pixmap = pixmap.scaled(
                        self._icon_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    return {'type': 'pixmap', 'data': scaled_pixmap}
            except Exception:
                pass
        
        return self._generate_default_icon()
    
    def _generate_svg_icon(self) -> Dict[str, Any]:
        """生成SVG图标"""
        if isinstance(self._icon, str):
            return {'type': 'svg', 'data': self._icon}
        
        return self._generate_default_icon()
    
    def _generate_default_icon(self) -> Dict[str, Any]:
        """生成默认图标"""
        # 创建一个简单的占位符图标
        pixmap = QPixmap(self._icon_size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setOpacity(self._opacity)
        
        # 绘制一个简单的圆形
        color = self._get_color()
        painter.setPen(QColor(color))
        painter.setBrush(QColor(color))
        
        margin = min(self._icon_size.width(), self._icon_size.height()) // 4
        painter.drawEllipse(
            margin, margin,
            self._icon_size.width() - 2 * margin,
            self._icon_size.height() - 2 * margin
        )
        
        painter.end()
        
        return {'type': 'pixmap', 'data': pixmap}
    
    def _apply_icon(self, icon_data: Dict[str, Any]):
        """应用图标"""
        if not self._widget:
            return
        
        icon_type = icon_data['type']
        data = icon_data['data']
        
        if icon_type == 'svg' and isinstance(self._widget, QSvgWidget):
            # SVG组件直接加载
            if isinstance(data, str):
                self._widget.load(data)
        elif isinstance(self._widget, QPushButton):
            # 按钮组件
            if icon_type == 'qicon':
                self._widget.setIcon(data)
                self._widget.setIconSize(self._icon_size)
            elif icon_type == 'pixmap':
                self._widget.setIcon(QIcon(data))
                self._widget.setIconSize(self._icon_size)
        elif isinstance(self._widget, QLabel):
            # 标签组件
            if icon_type == 'pixmap':
                self._widget.setPixmap(data)
            elif icon_type == 'qicon':
                pixmap = data.pixmap(self._icon_size)
                self._widget.setPixmap(pixmap)
    
    def _get_color(self) -> str:
        """获取颜色"""
        # 解析颜色路径
        color_parts = self._color.split('.')
        
        if len(color_parts) == 2:
            category, name = color_parts
            return design_tokens.get_color(category, name)
        
        # 默认颜色
        return design_tokens.get_color('text', 'primary')
    
    def update_style(self):
        """更新样式"""
        self._update_icon()
    
    def resizeEvent(self, event):
        """窗口大小变化事件"""
        super().resizeEvent(event)
        if self._widget:
            self._widget.setGeometry(self.rect())
    
    # 动画方法
    def rotate_to(self, angle: float, duration: int = 300):
        """旋转到指定角度"""
        if self._rotation_animation:
            self._rotation_animation.stop()
        
        self._rotation_animation = QPropertyAnimation(self, b"rotation")
        self._rotation_animation.setDuration(duration)
        self._rotation_animation.setStartValue(self._rotation)
        self._rotation_animation.setEndValue(angle)
        self._rotation_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._rotation_animation.start()
    
    def spin(self, duration: int = 1000, loops: int = -1):
        """旋转动画"""
        if self._rotation_animation:
            self._rotation_animation.stop()
        
        self._rotation_animation = QPropertyAnimation(self, b"rotation")
        self._rotation_animation.setDuration(duration)
        self._rotation_animation.setStartValue(0)
        self._rotation_animation.setEndValue(360)
        self._rotation_animation.setLoopCount(loops)
        self._rotation_animation.start()
    
    def stop_animation(self):
        """停止动画"""
        if self._rotation_animation:
            self._rotation_animation.stop()
    
    # 属性访问器
    @property
    def icon(self) -> Union[str, QIcon, QPixmap]:
        """图标"""
        return self._icon
    
    @icon.setter
    def icon(self, value: Union[str, QIcon, QPixmap]):
        """设置图标"""
        if self._icon != value:
            self._icon = value
            self._update_icon()
    
    @property
    def icon_type(self) -> str:
        """图标类型"""
        return self._icon_type
    
    @icon_type.setter
    def icon_type(self, value: str):
        """设置图标类型"""
        if self._icon_type != value:
            self._icon_type = value
            self._update_icon()
    
    @property
    def icon_size(self) -> QSize:
        """图标大小"""
        return self._icon_size

    @icon_size.setter
    def icon_size(self, value: Union[int, QSize]):
        """设置图标大小"""
        new_size = value if isinstance(value, QSize) else QSize(value, value)
        if self._icon_size != new_size:
            self._icon_size = new_size
            if self._widget:
                self._widget.setFixedSize(new_size)
            self._update_icon()
    
    @property
    def color(self) -> str:
        """图标颜色"""
        return self._color
    
    @color.setter
    def color(self, value: str):
        """设置图标颜色"""
        if self._color != value:
            self._color = value
            self._update_icon()
    
    @property
    def clickable(self) -> bool:
        """是否可点击"""
        return self._clickable
    
    @clickable.setter
    def clickable(self, value: bool):
        """设置是否可点击"""
        if self._clickable != value:
            self._clickable = value
            # 重新创建组件
            self.setup_ui()
            self.setup_connections()
    
    @property
    def rotation(self) -> float:
        """旋转角度"""
        return self._rotation
    
    @rotation.setter
    def rotation(self, value: float):
        """设置旋转角度"""
        if self._rotation != value:
            self._rotation = value
            self._update_icon()
    
    @property
    def opacity(self) -> float:
        """透明度"""
        return self._opacity
    
    @opacity.setter
    def opacity(self, value: float):
        """设置透明度"""
        value = max(0.0, min(1.0, value))
        if self._opacity != value:
            self._opacity = value
            self._update_icon()


class MaterialIcon(Icon):
    """Material Design图标"""
    
    def __init__(
        self,
        name: str,
        icon_size: Union[int, QSize] = 24,
        color: str = "text.primary",
        clickable: bool = False,
        parent: Optional[QWidget] = None
    ):
        super().__init__(
            icon=name,
            icon_type="material",
            icon_size=icon_size,
            color=color,
            clickable=clickable,
            component_size=ComponentSize.MEDIUM,
            parent=parent
        )


class FontAwesomeIcon(Icon):
    """FontAwesome图标"""
    
    def __init__(
        self,
        name: str,
        icon_size: Union[int, QSize] = 24,
        color: str = "text.primary",
        clickable: bool = False,
        parent: Optional[QWidget] = None
    ):
        super().__init__(
            icon=name,
            icon_type="fontawesome",
            icon_size=icon_size,
            color=color,
            clickable=clickable,
            component_size=ComponentSize.MEDIUM,
            parent=parent
        )


class SvgIcon(Icon):
    """SVG图标"""
    
    def __init__(
        self,
        path: str,
        icon_size: Union[int, QSize] = 24,
        color: str = "text.primary",
        clickable: bool = False,
        parent: Optional[QWidget] = None
    ):
        super().__init__(
            icon=path,
            icon_type="svg",
            icon_size=icon_size,
            color=color,
            clickable=clickable,
            component_size=ComponentSize.MEDIUM,
            parent=parent
        )


class IconButton(Icon):
    """图标按钮"""
    
    def __init__(
        self,
        icon: Union[str, QIcon, QPixmap],
        icon_type: str = "material",
        icon_size: Union[int, QSize] = 32,
        color: str = "text.primary",
        parent: Optional[QWidget] = None
    ):
        super().__init__(
            icon=icon,
            icon_type=icon_type,
            icon_size=icon_size,
            color=color,
            clickable=True,
            component_size=ComponentSize.MEDIUM,
            parent=parent
        )


class LoadingIcon(Icon):
    """加载图标"""
    
    def __init__(
        self,
        icon_size: Union[int, QSize] = 24,
        color: str = "text.primary",
        speed: int = 1000,
        parent: Optional[QWidget] = None
    ):
        # 使用旋转的圆形作为加载图标
        super().__init__(
            icon="refresh",  # 或者使用自定义的加载图标
            icon_type="material",
            icon_size=icon_size,
            color=color,
            clickable=False,
            component_size=ComponentSize.MEDIUM,
            parent=parent
        )
        
        self._speed = speed
        self._is_loading = False
    
    def start_loading(self):
        """开始加载动画"""
        if not self._is_loading:
            self._is_loading = True
            self.spin(duration=self._speed, loops=-1)
    
    def stop_loading(self):
        """停止加载动画"""
        if self._is_loading:
            self._is_loading = False
            self.stop_animation()
            self.rotation = 0
    
    @property
    def is_loading(self) -> bool:
        """是否正在加载"""
        return self._is_loading
    
    @property
    def speed(self) -> int:
        """加载速度"""
        return self._speed
    
    @speed.setter
    def speed(self, value: int):
        """设置加载速度"""
        if self._speed != value:
            self._speed = value
            if self._is_loading:
                self.stop_loading()
                self.start_loading()