"""样式生成器 - 基于设计Token生成Qt样式"""

from typing import Dict, List, Optional, Union
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from design_tokens import (
    design_tokens, ComponentSize, ComponentVariant,
    ShadowToken, TypographyToken
)


class StyleGenerator:
    """样式生成器"""
    
    def __init__(self):
        self.tokens = design_tokens
    
    def _format_shadow(self, shadow: ShadowToken) -> str:
        """格式化阴影样式"""
        if shadow.blur_radius == 0:
            return "none"
        
        return f"{shadow.x_offset}px {shadow.y_offset}px {shadow.blur_radius}px {shadow.spread_radius}px {shadow.color}"
    
    def _format_typography(self, typography: TypographyToken) -> Dict[str, str]:
        """格式化字体样式"""
        return {
            'font-family': typography.font_family,
            'font-size': f"{typography.font_size}px",
            'font-weight': str(typography.font_weight),
            'line-height': str(typography.line_height),
            'letter-spacing': f"{typography.letter_spacing}px" if typography.letter_spacing else "normal",
        }
    
    def generate_button_style(
        self,
        variant: ComponentVariant = ComponentVariant.PRIMARY,
        size: ComponentSize = ComponentSize.MEDIUM,
        disabled: bool = False,
        full_width: bool = False
    ) -> str:
        """生成按钮样式"""
        
        # 获取尺寸相关token
        height = self.tokens.get_component_token('button', 'height', size)
        padding = self.tokens.get_component_token('button', 'padding', size)
        font_size = self.tokens.get_component_token('button', 'font_size', size)
        
        # 获取颜色
        if variant == ComponentVariant.PRIMARY:
            bg_color = self.tokens.get_color('primary', '500')
            hover_color = self.tokens.get_color('primary', '400')
            active_color = self.tokens.get_color('primary', '600')
            text_color = self.tokens.get_color('text', 'primary')
        elif variant == ComponentVariant.SUCCESS:
            bg_color = self.tokens.get_color('semantic', 'success')
            hover_color = '#61df76'
            active_color = '#40c057'
            text_color = self.tokens.get_color('text', 'primary')
        elif variant == ComponentVariant.WARNING:
            bg_color = self.tokens.get_color('semantic', 'warning')
            hover_color = '#ffe44b'
            active_color = '#fab005'
            text_color = self.tokens.get_color('text', 'inverse')
        elif variant == ComponentVariant.ERROR:
            bg_color = self.tokens.get_color('semantic', 'error')
            hover_color = '#ff7b7b'
            active_color = '#ee5a52'
            text_color = self.tokens.get_color('text', 'primary')
        elif variant == ComponentVariant.SECONDARY:
            bg_color = self.tokens.get_color('neutral', '600')
            hover_color = self.tokens.get_color('neutral', '500')
            active_color = self.tokens.get_color('neutral', '700')
            text_color = self.tokens.get_color('text', 'primary')
        elif variant == ComponentVariant.GHOST:
            bg_color = 'transparent'
            hover_color = self.tokens.get_color('background', 'surface')
            active_color = self.tokens.get_color('neutral', '800')
            text_color = self.tokens.get_color('primary', '500')
        elif variant == ComponentVariant.OUTLINE:
            bg_color = 'transparent'
            hover_color = self.tokens.get_color('primary', '500')
            active_color = self.tokens.get_color('primary', '600')
            text_color = self.tokens.get_color('primary', '500')
        else:
            bg_color = self.tokens.get_color('primary', '500')
            hover_color = self.tokens.get_color('primary', '400')
            active_color = self.tokens.get_color('primary', '600')
            text_color = self.tokens.get_color('text', 'primary')
        
        # 获取其他样式token
        border_radius = self.tokens.get_border_radius('md')
        shadow = self.tokens.get_shadow('sm')
        animation = self.tokens.get_animation('fast')
        
        # 禁用状态颜色
        disabled_bg = self.tokens.get_color('neutral', '700')
        disabled_text = self.tokens.get_color('text', 'disabled')
        
        # 构建样式
        style = f"""
        QPushButton {{
            background: {bg_color};
            color: {text_color};
            border: {'2px solid ' + self.tokens.get_color('primary', '500') if variant == ComponentVariant.OUTLINE else 'none'};
            border-radius: {border_radius}px;
            padding: {padding}px;
            font-size: {font_size}px;
            font-weight: bold;
            min-height: {height}px;
            {'width: 100%;' if full_width else ''}
            transition: all {animation.duration}ms {animation.easing};
        }}
        
        QPushButton:hover {{
            background: {hover_color};
            {'color: ' + self.tokens.get_color('text', 'primary') + ';' if variant == ComponentVariant.OUTLINE else ''}
            transform: translateY(-1px);
        }}
        
        QPushButton:pressed {{
            background: {active_color};
            transform: translateY(0px);
        }}
        
        QPushButton:disabled {{
            background: {disabled_bg};
            color: {disabled_text};
            border-color: {disabled_bg};
        }}
        """
        
        return style.strip()
    
    def generate_card_style(
        self,
        size: ComponentSize = ComponentSize.MEDIUM,
        elevated: bool = True,
        interactive: bool = False
    ) -> str:
        """生成卡片样式"""
        
        # 获取尺寸相关token
        padding = self.tokens.get_component_token('card', 'padding', size)
        gap = self.tokens.get_component_token('card', 'gap', size)
        
        # 获取颜色
        bg_color = self.tokens.get_color('background', 'surface')
        border_color = self.tokens.get_color('border', 'primary')
        hover_bg = self.tokens.get_color('background', 'overlay')
        hover_border = self.tokens.get_color('border', 'secondary')
        
        # 获取其他样式token
        border_radius = self.tokens.get_border_radius('lg')
        shadow = self.tokens.get_shadow('md' if elevated else 'sm')
        animation = self.tokens.get_animation('normal')
        
        style = f"""
        QFrame.card {{
            background: {bg_color};
            border: 1px solid {border_color};
            border-radius: {border_radius}px;
            padding: {padding}px;
            margin: {gap}px;
        }}
        """
        
        if interactive:
            style += f"""
            QFrame.card:hover {{
                background: {hover_bg};
                border-color: {hover_border};
                transform: translateY(-2px);
                transition: all {animation.duration}ms {animation.easing};
            }}
            """
        
        return style.strip()
    
    def generate_input_style(
        self,
        size: ComponentSize = ComponentSize.MEDIUM,
        variant: ComponentVariant = ComponentVariant.PRIMARY,
        error: bool = False
    ) -> str:
        """生成输入框样式"""
        
        # 获取尺寸相关token
        height = self.tokens.get_component_token('input', 'height', size)
        padding = self.tokens.get_component_token('input', 'padding', size)
        font_size = self.tokens.get_component_token('button', 'font_size', size)
        
        # 获取颜色
        bg_color = self.tokens.get_color('background', 'surface')
        border_color = self.tokens.get_color('border', 'primary')
        focus_border = self.tokens.get_color('border', 'focus')
        error_border = self.tokens.get_color('border', 'error')
        text_color = self.tokens.get_color('text', 'primary')
        placeholder_color = self.tokens.get_color('text', 'tertiary')
        
        # 获取其他样式token
        border_radius = self.tokens.get_border_radius('md')
        shadow = self.tokens.get_shadow('sm')
        focus_shadow = self.tokens.get_shadow('focus')
        animation = self.tokens.get_animation('fast')
        
        current_border = error_border if error else border_color
        
        style = f"""
        QLineEdit, QTextEdit, QComboBox {{
            background: {bg_color};
            border: 2px solid {current_border};
            border-radius: {border_radius}px;
            padding: {padding}px;
            color: {text_color};
            font-size: {font_size}px;
            min-height: {height}px;
            transition: all {animation.duration}ms {animation.easing};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border-color: {focus_border};
            outline: none;
        }}
        
        QLineEdit:hover, QTextEdit:hover, QComboBox:hover {{
            border-color: {self.tokens.get_color('primary', '400')};
        }}
        
        QLineEdit::placeholder {{
            color: {placeholder_color};
        }}
        """
        
        return style.strip()
    
    def generate_progress_style(
        self,
        size: ComponentSize = ComponentSize.MEDIUM,
        variant: ComponentVariant = ComponentVariant.PRIMARY
    ) -> str:
        """生成进度条样式"""
        
        # 获取高度
        height_map = {
            ComponentSize.SMALL: 6,
            ComponentSize.MEDIUM: 8,
            ComponentSize.LARGE: 12,
            ComponentSize.XLARGE: 16,
        }
        height = height_map[size]
        
        # 获取颜色
        if variant == ComponentVariant.PRIMARY:
            fill_color = self.tokens.get_color('primary', '500')
        elif variant == ComponentVariant.SUCCESS:
            fill_color = self.tokens.get_color('semantic', 'success')
        elif variant == ComponentVariant.WARNING:
            fill_color = self.tokens.get_color('semantic', 'warning')
        elif variant == ComponentVariant.ERROR:
            fill_color = self.tokens.get_color('semantic', 'error')
        else:
            fill_color = self.tokens.get_color('primary', '500')
        
        bg_color = self.tokens.get_color('neutral', '800')
        border_color = self.tokens.get_color('border', 'primary')
        text_color = self.tokens.get_color('text', 'primary')
        
        # 获取其他样式token
        border_radius = self.tokens.get_border_radius('md')
        
        style = f"""
        QProgressBar {{
            background: {bg_color};
            border: 1px solid {border_color};
            border-radius: {border_radius}px;
            text-align: center;
            color: {text_color};
            font-weight: bold;
            height: {height}px;
        }}
        
        QProgressBar::chunk {{
            background: {fill_color};
            border-radius: {border_radius - 2}px;
            margin: 1px;
        }}
        """
        
        return style.strip()
    
    def generate_typography_style(
        self,
        category: str,
        variant: str,
        color_category: str = 'text',
        color_variant: str = 'primary'
    ) -> str:
        """生成字体样式"""
        
        typography = self.tokens.get_typography(category, variant)
        color = self.tokens.get_color(color_category, color_variant)
        
        style_dict = self._format_typography(typography)
        style_dict['color'] = color
        
        style_rules = [f"{key}: {value};" for key, value in style_dict.items()]
        return " ".join(style_rules)
    
    def generate_layout_style(
        self,
        spacing: str = '4',
        margin: str = '4'
    ) -> Dict[str, int]:
        """生成布局样式"""
        
        return {
            'spacing': self.tokens.get_spacing(spacing),
            'margin': self.tokens.get_spacing(margin),
            'content_margin': self.tokens.get_spacing('3'),
        }
    
    def generate_global_style(self) -> str:
        """生成全局样式"""
        
        # 获取全局颜色
        bg_primary = self.tokens.get_color('background', 'primary')
        bg_secondary = self.tokens.get_color('background', 'secondary')
        bg_tertiary = self.tokens.get_color('background', 'tertiary')
        text_primary = self.tokens.get_color('text', 'primary')
        
        # 获取字体
        body_font = self.tokens.get_typography('body', 'medium')
        
        style = f"""
        /* 全局样式重置 */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        /* 主窗口样式 */
        QMainWindow {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 {bg_primary}, stop:0.5 {bg_secondary}, stop:1 {bg_tertiary});
            color: {text_primary};
            font-family: {body_font.font_family};
            font-size: {body_font.font_size}px;
        }}
        
        /* 滚动条样式 */
        QScrollBar:vertical {{
            background: {self.tokens.get_color('neutral', '800')};
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background: {self.tokens.get_color('primary', '500')};
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {self.tokens.get_color('primary', '400')};
        }}
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        
        QScrollBar:horizontal {{
            background: {self.tokens.get_color('neutral', '800')};
            height: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {self.tokens.get_color('primary', '500')};
            border-radius: 6px;
            min-width: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {self.tokens.get_color('primary', '400')};
        }}
        
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
        
        /* 工具提示样式 */
        QToolTip {{
            background: {self.tokens.get_color('background', 'overlay')};
            border: 1px solid {self.tokens.get_color('border', 'primary')};
            border-radius: {self.tokens.get_border_radius('md')}px;
            padding: {self.tokens.get_spacing('2')}px {self.tokens.get_spacing('3')}px;
            color: {text_primary};
            font-size: {self.tokens.get_typography('body', 'small').font_size}px;
        }}
        """
        
        return style.strip()
    
    def generate_component_style(
        self,
        component_type: str,
        **kwargs
    ) -> str:
        """生成组件样式的统一入口"""
        
        if component_type == 'button':
            return self.generate_button_style(**kwargs)
        elif component_type == 'card':
            return self.generate_card_style(**kwargs)
        elif component_type == 'input':
            return self.generate_input_style(**kwargs)
        elif component_type == 'progress':
            return self.generate_progress_style(**kwargs)
        else:
            return ""


# 全局样式生成器实例
style_generator = StyleGenerator()