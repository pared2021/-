#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
样式生成器
基于设计令牌生成QSS样式
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, Any, Optional
from design_tokens import DesignTokens, ComponentSize, ComponentVariant, ComponentState


class StyleGenerator:
    """样式生成器"""
    
    def __init__(self, design_tokens: Optional[DesignTokens] = None):
        self.design_tokens = design_tokens or DesignTokens()
    
    def generate_button_style(self, 
                            variant: ComponentVariant = ComponentVariant.PRIMARY,
                            size: ComponentSize = ComponentSize.MEDIUM,
                            disabled: bool = False) -> str:
        """生成按钮样式"""
        state = ComponentState.DISABLED if disabled else ComponentState.DEFAULT
        colors = self.design_tokens.get_component_colors(variant, state)
        size_config = self.design_tokens.get_component_size_config(size)
        
        hover_colors = self.design_tokens.get_component_colors(variant, ComponentState.HOVER)
        active_colors = self.design_tokens.get_component_colors(variant, ComponentState.ACTIVE)
        
        return f"""
        QPushButton {{
            background-color: {colors['background']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: {size_config['border_radius']}px;
            padding: {size_config['padding_y']}px {size_config['padding_x']}px;
            font-size: {size_config['font_size']}px;
            font-weight: {self.design_tokens.get_font_weight('medium')};
            min-height: {size_config['height']}px;
            outline: none;
        }}
        
        QPushButton:hover {{
            background-color: {hover_colors['background']};
            color: {hover_colors['text']};
            border-color: {hover_colors['border']};
        }}
        
        QPushButton:pressed {{
            background-color: {active_colors['background']};
            color: {active_colors['text']};
            border-color: {active_colors['border']};
        }}
        
        QPushButton:disabled {{
            background-color: {self.design_tokens.get_color('neutral', '300')};
            color: {self.design_tokens.get_color('text', 'disabled')};
            border-color: {self.design_tokens.get_color('neutral', '300')};
        }}
        """
    
    def generate_card_style(self, elevated: bool = True) -> str:
        """生成卡片样式"""
        shadow = self.design_tokens.get_shadow('md') if elevated else 'none'
        
        return f"""
        QFrame {{
            background-color: {self.design_tokens.get_color('background', 'primary')};
            border: 1px solid {self.design_tokens.get_color('border', 'light')};
            border-radius: {self.design_tokens.get_radius('lg')}px;
            padding: {self.design_tokens.get_spacing('lg')}px;
        }}
        
        QFrame:hover {{
            border-color: {self.design_tokens.get_color('border', 'medium')};
        }}
        """
    
    def generate_input_style(self, 
                           size: ComponentSize = ComponentSize.MEDIUM,
                           error: bool = False) -> str:
        """生成输入框样式"""
        size_config = self.design_tokens.get_component_size_config(size)
        border_color = self.design_tokens.get_color('semantic', 'danger') if error else self.design_tokens.get_color('border', 'medium')
        
        return f"""
        QLineEdit {{
            background-color: {self.design_tokens.get_color('background', 'primary')};
            color: {self.design_tokens.get_color('text', 'primary')};
            border: 1px solid {border_color};
            border-radius: {size_config['border_radius']}px;
            padding: {size_config['padding_y']}px {size_config['padding_x']}px;
            font-size: {size_config['font_size']}px;
            min-height: {size_config['height']}px;
        }}
        
        QLineEdit:focus {{
            border-color: {self.design_tokens.get_color('primary', '500')};
            outline: none;
        }}
        
        QLineEdit:disabled {{
            background-color: {self.design_tokens.get_color('neutral', '100')};
            color: {self.design_tokens.get_color('text', 'disabled')};
            border-color: {self.design_tokens.get_color('neutral', '300')};
        }}
        
        QSpinBox {{
            background-color: {self.design_tokens.get_color('background', 'primary')};
            color: {self.design_tokens.get_color('text', 'primary')};
            border: 1px solid {border_color};
            border-radius: {size_config['border_radius']}px;
            padding: {size_config['padding_y']}px {size_config['padding_x']}px;
            font-size: {size_config['font_size']}px;
            min-height: {size_config['height']}px;
        }}
        
        QSpinBox:focus {{
            border-color: {self.design_tokens.get_color('primary', '500')};
        }}
        """
    
    def generate_progress_style(self, 
                              variant: ComponentVariant = ComponentVariant.PRIMARY,
                              size: ComponentSize = ComponentSize.MEDIUM) -> str:
        """生成进度条样式"""
        colors = self.design_tokens.get_component_colors(variant)
        size_config = self.design_tokens.get_component_size_config(size)
        
        height_map = {
            ComponentSize.SMALL: 4,
            ComponentSize.MEDIUM: 8,
            ComponentSize.LARGE: 12,
            ComponentSize.XLARGE: 16
        }
        
        height = height_map.get(size, 8)
        
        return f"""
        QProgressBar {{
            background-color: {self.design_tokens.get_color('neutral', '200')};
            border: none;
            border-radius: {height // 2}px;
            text-align: center;
            height: {height}px;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['background']};
            border-radius: {height // 2}px;
        }}
        """
    
    def generate_typography_style(self, 
                                variant: str = "body",
                                size: str = "md") -> str:
        """生成排版样式"""
        font_size = self.design_tokens.get_font_size(size)
        
        weight_map = {
            "heading": "bold",
            "body": "normal",
            "caption": "normal",
            "link": "medium"
        }
        
        color_map = {
            "heading": self.design_tokens.get_color('text', 'primary'),
            "body": self.design_tokens.get_color('text', 'primary'),
            "caption": self.design_tokens.get_color('text', 'secondary'),
            "link": self.design_tokens.get_color('primary', '500')
        }
        
        weight = self.design_tokens.get_font_weight(weight_map.get(variant, "normal"))
        color = color_map.get(variant, self.design_tokens.get_color('text', 'primary'))
        
        return f"""
        QLabel {{
            color: {color};
            font-size: {font_size}px;
            font-weight: {weight};
            font-family: {self.design_tokens.fonts['family']['primary']};
            line-height: {self.design_tokens.fonts['line_height']['normal']};
        }}
        """
    
    def generate_icon_style(self, size: int = 24) -> str:
        """生成图标样式"""
        return f"""
        QLabel {{
            color: {self.design_tokens.get_color('text', 'primary')};
            font-size: {size}px;
            min-width: {size}px;
            max-width: {size}px;
            min-height: {size}px;
            max-height: {size}px;
        }}
        """
    
    def generate_layout_style(self) -> str:
        """生成布局样式"""
        return f"""
        QWidget {{
            background-color: transparent;
        }}
        
        QScrollArea {{
            background-color: {self.design_tokens.get_color('background', 'primary')};
            border: none;
        }}
        
        QScrollBar:vertical {{
            background-color: {self.design_tokens.get_color('neutral', '100')};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {self.design_tokens.get_color('neutral', '400')};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {self.design_tokens.get_color('neutral', '500')};
        }}
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        """
    
    def generate_global_style(self) -> str:
        """生成全局样式"""
        return f"""
        * {{
            font-family: {self.design_tokens.fonts['family']['primary']};
        }}
        
        QMainWindow {{
            background-color: {self.design_tokens.get_color('background', 'secondary')};
            color: {self.design_tokens.get_color('text', 'primary')};
        }}
        
        QWidget {{
            background-color: transparent;
            color: {self.design_tokens.get_color('text', 'primary')};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {self.design_tokens.get_color('border', 'light')};
            background-color: {self.design_tokens.get_color('background', 'primary')};
            border-radius: {self.design_tokens.get_radius('md')}px;
        }}
        
        QTabBar::tab {{
            background-color: {self.design_tokens.get_color('background', 'secondary')};
            color: {self.design_tokens.get_color('text', 'secondary')};
            padding: {self.design_tokens.get_spacing('sm')}px {self.design_tokens.get_spacing('md')}px;
            margin-right: 2px;
            border-top-left-radius: {self.design_tokens.get_radius('md')}px;
            border-top-right-radius: {self.design_tokens.get_radius('md')}px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {self.design_tokens.get_color('background', 'primary')};
            color: {self.design_tokens.get_color('text', 'primary')};
            border-bottom: 2px solid {self.design_tokens.get_color('primary', '500')};
        }}
        
        QTabBar::tab:hover {{
            background-color: {self.design_tokens.get_color('neutral', '100')};
        }}
        
        QFrame {{
            border: none;
        }}
        
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        QScrollBar:vertical {{
            background-color: {self.design_tokens.get_color('neutral', '100')};
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {self.design_tokens.get_color('neutral', '400')};
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {self.design_tokens.get_color('neutral', '500')};
        }}
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
            height: 0;
        }}
        
        QScrollBar:horizontal {{
            background-color: {self.design_tokens.get_color('neutral', '100')};
            height: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {self.design_tokens.get_color('neutral', '400')};
            border-radius: 6px;
            min-width: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {self.design_tokens.get_color('neutral', '500')};
        }}
        
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
            width: 0;
        }}
        """
    
    def generate_theme_style(self, theme: str = "light") -> str:
        """生成主题样式"""
        if theme == "dark":
            # 暗色主题
            return f"""
            QMainWindow {{
                background-color: #1a1a1a;
                color: #ffffff;
            }}
            
            QWidget {{
                background-color: transparent;
                color: #ffffff;
            }}
            
            QFrame {{
                background-color: #2d2d2d;
                border: 1px solid #404040;
            }}
            
            QLineEdit {{
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #404040;
            }}
            
            QPushButton {{
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #606060;
            }}
            
            QPushButton:hover {{
                background-color: #505050;
            }}
            """
        else:
            # 亮色主题（默认）
            return self.generate_global_style()


# 创建全局样式生成器实例
style_generator = StyleGenerator()