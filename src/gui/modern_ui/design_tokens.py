"""设计Token系统 - 统一的设计语言基础"""

from typing import Dict, Any, Union
from dataclasses import dataclass
from enum import Enum


class ThemeMode(Enum):
    """主题模式"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class ComponentSize(Enum):
    """组件尺寸"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    XLARGE = "xlarge"


class ComponentVariant(Enum):
    """组件变体"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    GHOST = "ghost"
    OUTLINE = "outline"


@dataclass
class ColorToken:
    """颜色Token"""
    value: str
    description: str = ""
    accessibility_contrast: float = 0.0


@dataclass
class SpacingToken:
    """间距Token"""
    value: int
    rem_value: float
    description: str = ""


@dataclass
class TypographyToken:
    """字体Token"""
    font_family: str
    font_size: int
    font_weight: Union[int, str]
    line_height: float
    letter_spacing: float = 0.0
    description: str = ""


@dataclass
class ShadowToken:
    """阴影Token"""
    x_offset: int
    y_offset: int
    blur_radius: int
    spread_radius: int = 0
    color: str = "rgba(0, 0, 0, 0.1)"
    description: str = ""


@dataclass
class BorderRadiusToken:
    """圆角Token"""
    value: int
    description: str = ""


@dataclass
class AnimationToken:
    """动画Token"""
    duration: int  # 毫秒
    easing: str
    description: str = ""


class DesignTokens:
    """设计Token管理器"""
    
    def __init__(self, theme_mode: ThemeMode = ThemeMode.DARK):
        self.theme_mode = theme_mode
        self._init_tokens()
    
    def _init_tokens(self):
        """初始化所有Token"""
        self._init_color_tokens()
        self._init_spacing_tokens()
        self._init_typography_tokens()
        self._init_shadow_tokens()
        self._init_border_radius_tokens()
        self._init_animation_tokens()
        self._init_component_tokens()
    
    def _init_color_tokens(self):
        """初始化颜色Token"""
        if self.theme_mode == ThemeMode.DARK:
            self.colors = {
                # 主色调
                'primary': {
                    '50': ColorToken('#e3f2fd', '主色调最浅', 21.0),
                    '100': ColorToken('#bbdefb', '主色调很浅', 16.0),
                    '200': ColorToken('#90caf9', '主色调浅', 12.0),
                    '300': ColorToken('#64b5f6', '主色调中浅', 9.0),
                    '400': ColorToken('#42a5f5', '主色调中', 7.0),
                    '500': ColorToken('#4a90e2', '主色调标准', 5.5),
                    '600': ColorToken('#357abd', '主色调中深', 4.5),
                    '700': ColorToken('#1976d2', '主色调深', 3.5),
                    '800': ColorToken('#1565c0', '主色调很深', 3.0),
                    '900': ColorToken('#0d47a1', '主色调最深', 2.5),
                },
                
                # 语义色彩
                'semantic': {
                    'success': ColorToken('#51cf66', '成功状态', 4.5),
                    'warning': ColorToken('#ffd43b', '警告状态', 1.5),
                    'error': ColorToken('#ff6b6b', '错误状态', 4.5),
                    'info': ColorToken('#74c0fc', '信息状态', 4.5),
                },
                
                # 中性色
                'neutral': {
                    '0': ColorToken('#ffffff', '纯白', 21.0),
                    '50': ColorToken('#f8fafc', '极浅灰', 20.0),
                    '100': ColorToken('#f1f5f9', '很浅灰', 18.0),
                    '200': ColorToken('#e2e8f0', '浅灰', 15.0),
                    '300': ColorToken('#cbd5e1', '中浅灰', 12.0),
                    '400': ColorToken('#94a3b8', '中灰', 8.0),
                    '500': ColorToken('#64748b', '标准灰', 5.5),
                    '600': ColorToken('#475569', '中深灰', 4.5),
                    '700': ColorToken('#334155', '深灰', 3.5),
                    '800': ColorToken('#1e293b', '很深灰', 2.5),
                    '900': ColorToken('#0f172a', '极深灰', 1.5),
                },
                
                # 背景色
                'background': {
                    'primary': ColorToken('#1a1a2e', '主背景'),
                    'secondary': ColorToken('#16213e', '次背景'),
                    'tertiary': ColorToken('#0f3460', '第三背景'),
                    'surface': ColorToken('rgba(26, 26, 46, 0.8)', '表面'),
                    'overlay': ColorToken('rgba(26, 26, 46, 0.95)', '遮罩'),
                },
                
                # 文本色
                'text': {
                    'primary': ColorToken('#ffffff', '主文本'),
                    'secondary': ColorToken('rgba(255, 255, 255, 0.8)', '次文本'),
                    'tertiary': ColorToken('rgba(255, 255, 255, 0.6)', '第三文本'),
                    'disabled': ColorToken('rgba(255, 255, 255, 0.4)', '禁用文本'),
                    'inverse': ColorToken('#1a1a2e', '反色文本'),
                },
                
                # 边框色
                'border': {
                    'primary': ColorToken('rgba(74, 144, 226, 0.3)', '主边框'),
                    'secondary': ColorToken('rgba(74, 144, 226, 0.5)', '次边框'),
                    'focus': ColorToken('#74c0fc', '焦点边框'),
                    'error': ColorToken('#ff6b6b', '错误边框'),
                    'success': ColorToken('#51cf66', '成功边框'),
                },
            }
    
    def _init_spacing_tokens(self):
        """初始化间距Token"""
        base_unit = 4  # 4px基础单位
        
        self.spacing = {
            '0': SpacingToken(0, 0, '无间距'),
            '1': SpacingToken(base_unit, 0.25, '极小间距'),
            '2': SpacingToken(base_unit * 2, 0.5, '很小间距'),
            '3': SpacingToken(base_unit * 3, 0.75, '小间距'),
            '4': SpacingToken(base_unit * 4, 1.0, '标准间距'),
            '5': SpacingToken(base_unit * 5, 1.25, '中间距'),
            '6': SpacingToken(base_unit * 6, 1.5, '大间距'),
            '8': SpacingToken(base_unit * 8, 2.0, '很大间距'),
            '10': SpacingToken(base_unit * 10, 2.5, '极大间距'),
            '12': SpacingToken(base_unit * 12, 3.0, '超大间距'),
            '16': SpacingToken(base_unit * 16, 4.0, '巨大间距'),
            '20': SpacingToken(base_unit * 20, 5.0, '超巨大间距'),
            '24': SpacingToken(base_unit * 24, 6.0, '最大间距'),
        }
    
    def _init_typography_tokens(self):
        """初始化字体Token"""
        self.typography = {
            # 标题字体
            'heading': {
                'h1': TypographyToken('Microsoft YaHei', 32, 'bold', 1.2, 0, '主标题'),
                'h2': TypographyToken('Microsoft YaHei', 24, 'bold', 1.3, 0, '二级标题'),
                'h3': TypographyToken('Microsoft YaHei', 20, 'bold', 1.4, 0, '三级标题'),
                'h4': TypographyToken('Microsoft YaHei', 18, 'bold', 1.4, 0, '四级标题'),
                'h5': TypographyToken('Microsoft YaHei', 16, 'bold', 1.5, 0, '五级标题'),
                'h6': TypographyToken('Microsoft YaHei', 14, 'bold', 1.5, 0, '六级标题'),
            },
            
            # 正文字体
            'body': {
                'large': TypographyToken('Microsoft YaHei', 16, 'normal', 1.6, 0, '大正文'),
                'medium': TypographyToken('Microsoft YaHei', 14, 'normal', 1.5, 0, '中正文'),
                'small': TypographyToken('Microsoft YaHei', 12, 'normal', 1.4, 0, '小正文'),
                'xs': TypographyToken('Microsoft YaHei', 10, 'normal', 1.3, 0, '极小正文'),
            },
            
            # 特殊字体
            'special': {
                'code': TypographyToken('Consolas, Monaco, monospace', 13, 'normal', 1.4, 0, '代码字体'),
                'caption': TypographyToken('Microsoft YaHei', 11, 'normal', 1.3, 0.5, '说明文字'),
                'overline': TypographyToken('Microsoft YaHei', 10, 'bold', 1.2, 1.5, '上标文字'),
            },
        }
    
    def _init_shadow_tokens(self):
        """初始化阴影Token"""
        self.shadows = {
            'none': ShadowToken(0, 0, 0, 0, 'transparent', '无阴影'),
            'sm': ShadowToken(0, 1, 2, 0, 'rgba(0, 0, 0, 0.05)', '小阴影'),
            'md': ShadowToken(0, 2, 4, 0, 'rgba(0, 0, 0, 0.1)', '中阴影'),
            'lg': ShadowToken(0, 4, 8, 0, 'rgba(0, 0, 0, 0.15)', '大阴影'),
            'xl': ShadowToken(0, 8, 16, 0, 'rgba(0, 0, 0, 0.2)', '超大阴影'),
            'glow': ShadowToken(0, 0, 20, 0, 'rgba(74, 144, 226, 0.3)', '发光效果'),
            'focus': ShadowToken(0, 0, 0, 3, 'rgba(74, 144, 226, 0.5)', '焦点阴影'),
        }
    
    def _init_border_radius_tokens(self):
        """初始化圆角Token"""
        self.border_radius = {
            'none': BorderRadiusToken(0, '无圆角'),
            'sm': BorderRadiusToken(4, '小圆角'),
            'md': BorderRadiusToken(8, '中圆角'),
            'lg': BorderRadiusToken(12, '大圆角'),
            'xl': BorderRadiusToken(16, '超大圆角'),
            'full': BorderRadiusToken(9999, '完全圆角'),
        }
    
    def _init_animation_tokens(self):
        """初始化动画Token"""
        self.animations = {
            'fast': AnimationToken(150, 'ease-out', '快速动画'),
            'normal': AnimationToken(250, 'ease-in-out', '标准动画'),
            'slow': AnimationToken(350, 'ease-in', '慢速动画'),
            'bounce': AnimationToken(500, 'cubic-bezier(0.68, -0.55, 0.265, 1.55)', '弹跳动画'),
            'smooth': AnimationToken(300, 'cubic-bezier(0.4, 0, 0.2, 1)', '平滑动画'),
        }
    
    def _init_component_tokens(self):
        """初始化组件Token"""
        self.components = {
            # 按钮尺寸
            'button': {
                'height': {
                    ComponentSize.SMALL: 32,
                    ComponentSize.MEDIUM: 40,
                    ComponentSize.LARGE: 48,
                    ComponentSize.XLARGE: 56,
                },
                'padding': {
                    ComponentSize.SMALL: (8, 16),
                    ComponentSize.MEDIUM: (12, 24),
                    ComponentSize.LARGE: (16, 32),
                    ComponentSize.XLARGE: (20, 40),
                },
                'font_size': {
                    ComponentSize.SMALL: 12,
                    ComponentSize.MEDIUM: 14,
                    ComponentSize.LARGE: 16,
                    ComponentSize.XLARGE: 18,
                },
            },
            
            # 输入框尺寸
            'input': {
                'height': {
                    ComponentSize.SMALL: 32,
                    ComponentSize.MEDIUM: 40,
                    ComponentSize.LARGE: 48,
                    ComponentSize.XLARGE: 56,
                },
                'padding': {
                    ComponentSize.SMALL: (8, 12),
                    ComponentSize.MEDIUM: (12, 16),
                    ComponentSize.LARGE: (16, 20),
                    ComponentSize.XLARGE: (20, 24),
                },
            },
            
            # 卡片间距
            'card': {
                'padding': {
                    ComponentSize.SMALL: 12,
                    ComponentSize.MEDIUM: 16,
                    ComponentSize.LARGE: 20,
                    ComponentSize.XLARGE: 24,
                },
                'gap': {
                    ComponentSize.SMALL: 8,
                    ComponentSize.MEDIUM: 12,
                    ComponentSize.LARGE: 16,
                    ComponentSize.XLARGE: 20,
                },
            },
        }
    
    def get_color(self, category: str, key: str) -> str:
        """获取颜色值"""
        try:
            return self.colors[category][key].value
        except KeyError:
            return '#ffffff'  # 默认白色
    
    def get_spacing(self, key: str) -> int:
        """获取间距值"""
        try:
            return self.spacing[key].value
        except KeyError:
            return 16  # 默认间距
    
    def get_typography(self, category: str, key: str) -> TypographyToken:
        """获取字体Token"""
        try:
            return self.typography[category][key]
        except KeyError:
            return self.typography['body']['medium']  # 默认字体
    
    def get_shadow(self, key: str) -> ShadowToken:
        """获取阴影Token"""
        try:
            return self.shadows[key]
        except KeyError:
            return self.shadows['none']  # 默认无阴影
    
    def get_border_radius(self, key: str) -> int:
        """获取圆角值"""
        try:
            return self.border_radius[key].value
        except KeyError:
            return 8  # 默认圆角
    
    def get_animation(self, key: str) -> AnimationToken:
        """获取动画Token"""
        try:
            return self.animations[key]
        except KeyError:
            return self.animations['normal']  # 默认动画
    
    def get_component_token(self, component: str, property: str, size: ComponentSize) -> Any:
        """获取组件Token"""
        try:
            return self.components[component][property][size]
        except KeyError:
            return None
    
    def switch_theme(self, theme_mode: ThemeMode):
        """切换主题"""
        self.theme_mode = theme_mode
        self._init_tokens()


# 全局设计Token实例
design_tokens = DesignTokens(ThemeMode.DARK)