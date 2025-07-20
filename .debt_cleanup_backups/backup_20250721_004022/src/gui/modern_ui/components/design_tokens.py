#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设计令牌系统
定义统一的设计规范，包括颜色、间距、字体、阴影等
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


class ComponentSize(Enum):
    """组件尺寸枚举"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    XLARGE = "xlarge"


class ComponentVariant(Enum):
    """组件变体枚举"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"
    LIGHT = "light"
    DARK = "dark"


class ComponentState(Enum):
    """组件状态枚举"""
    DEFAULT = "default"
    HOVER = "hover"
    ACTIVE = "active"
    FOCUS = "focus"
    DISABLED = "disabled"


@dataclass
class ColorToken:
    """颜色令牌"""
    name: str
    value: str
    description: str = ""


@dataclass
class SpacingToken:
    """间距令牌"""
    name: str
    value: int
    description: str = ""


@dataclass
class FontToken:
    """字体令牌"""
    name: str
    family: str
    size: int
    weight: int
    line_height: float
    description: str = ""


@dataclass
class ShadowToken:
    """阴影令牌"""
    name: str
    x_offset: int
    y_offset: int
    blur_radius: int
    spread: int
    color: str
    description: str = ""


@dataclass
class RadiusToken:
    """圆角令牌"""
    name: str
    value: int
    description: str = ""


@dataclass
class AnimationToken:
    """动画令牌"""
    name: str
    duration: int
    easing: str
    description: str = ""


@dataclass
class TypographyToken:
    """字体排版令牌"""
    font_family: str
    font_size: int
    font_weight: int
    line_height: float
    description: str = ""


class DesignTokens:
    """设计令牌管理器"""
    
    def __init__(self):
        self._init_color_tokens()
        self._init_spacing_tokens()
        self._init_font_tokens()
        self._init_shadow_tokens()
        self._init_radius_tokens()
        self._init_animation_tokens()
    
    def _init_color_tokens(self):
        """初始化颜色令牌"""
        self.colors = {
            # 主色调
            "primary": {
                "50": "#e3f2fd",
                "100": "#bbdefb",
                "200": "#90caf9",
                "300": "#64b5f6",
                "400": "#42a5f5",
                "500": "#2196f3",  # 主色
                "600": "#1e88e5",
                "700": "#1976d2",
                "800": "#1565c0",
                "900": "#0d47a1"
            },
            # 次要色调
            "secondary": {
                "50": "#f3e5f5",
                "100": "#e1bee7",
                "200": "#ce93d8",
                "300": "#ba68c8",
                "400": "#ab47bc",
                "500": "#9c27b0",  # 次要色
                "600": "#8e24aa",
                "700": "#7b1fa2",
                "800": "#6a1b9a",
                "900": "#4a148c"
            },
            # 语义色彩
            "semantic": {
                "success": "#4caf50",
                "warning": "#ff9800",
                "danger": "#f44336",
                "info": "#2196f3"
            },
            # 中性色彩
            "neutral": {
                "50": "#fafafa",
                "100": "#f5f5f5",
                "200": "#eeeeee",
                "300": "#e0e0e0",
                "400": "#bdbdbd",
                "500": "#9e9e9e",
                "600": "#757575",
                "700": "#616161",
                "800": "#424242",
                "900": "#212121"
            },
            # 背景色彩
            "background": {
                "primary": "#ffffff",
                "secondary": "#f8f9fa",
                "tertiary": "#e9ecef"
            },
            # 文本色彩
            "text": {
                "primary": "#212529",
                "secondary": "#6c757d",
                "disabled": "#adb5bd",
                "inverse": "#ffffff"
            },
            # 边框色彩
            "border": {
                "light": "#e9ecef",
                "medium": "#dee2e6",
                "dark": "#adb5bd"
            }
        }
    
    def _init_spacing_tokens(self):
        """初始化间距令牌"""
        self.spacing = {
            "xs": 4,
            "sm": 8,
            "md": 16,
            "lg": 24,
            "xl": 32,
            "2xl": 48,
            "3xl": 64
        }
    
    def _init_font_tokens(self):
        """初始化字体令牌"""
        self.fonts = {
            "family": {
                "primary": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                "monospace": "'Consolas', 'Monaco', 'Courier New', monospace"
            },
            "size": {
                "xs": 12,
                "sm": 14,
                "md": 16,
                "lg": 18,
                "xl": 20,
                "2xl": 24,
                "3xl": 30,
                "4xl": 36,
                "5xl": 48
            },
            "weight": {
                "light": 300,
                "normal": 400,
                "medium": 500,
                "semibold": 600,
                "bold": 700
            },
            "line_height": {
                "tight": 1.2,
                "normal": 1.5,
                "relaxed": 1.8
            }
        }
    
    def _init_shadow_tokens(self):
        """初始化阴影令牌"""
        self.shadows = {
            "none": ShadowToken("none", 0, 0, 0, 0, "rgba(0, 0, 0, 0)"),
            "sm": ShadowToken("sm", 0, 1, 2, 0, "rgba(0, 0, 0, 0.05)"),
            "md": ShadowToken("md", 0, 4, 6, 0, "rgba(0, 0, 0, 0.1)"),
            "lg": ShadowToken("lg", 0, 10, 15, 0, "rgba(0, 0, 0, 0.1)"),
            "xl": ShadowToken("xl", 0, 20, 25, 0, "rgba(0, 0, 0, 0.1)"),
            "2xl": ShadowToken("2xl", 0, 25, 50, 0, "rgba(0, 0, 0, 0.25)"),
            "inner": ShadowToken("inner", 0, 2, 4, 0, "rgba(0, 0, 0, 0.06)")
        }
    
    def _init_radius_tokens(self):
        """初始化圆角令牌"""
        self.radius = {
            "none": 0,
            "sm": 2,
            "md": 4,
            "lg": 8,
            "xl": 12,
            "2xl": 16,
            "3xl": 24,
            "full": 9999
        }
    
    def _init_animation_tokens(self):
        """初始化动画令牌"""
        self.animations = {
            "duration": {
                "fast": 150,
                "normal": 300,
                "slow": 500
            },
            "easing": {
                "ease": "ease",
                "ease_in": "ease-in",
                "ease_out": "ease-out",
                "ease_in_out": "ease-in-out",
                "linear": "linear"
            }
        }
    
    def get_color(self, category: str, key: str) -> str:
        """获取颜色值"""
        try:
            return self.colors[category][key]
        except KeyError:
            return "#000000"  # 默认黑色
    
    def get_spacing(self, key: str) -> int:
        """获取间距值"""
        return self.spacing.get(key, 16)  # 默认16px
    
    def get_font_size(self, key: str) -> int:
        """获取字体大小"""
        return self.fonts["size"].get(key, 16)  # 默认16px
    
    def get_font_weight(self, key: str) -> int:
        """获取字体粗细"""
        return self.fonts["weight"].get(key, 400)  # 默认normal
    
    def get_shadow(self, key: str) -> ShadowToken:
        """获取阴影令牌"""
        return self.shadows.get(key, self.shadows["none"])
    
    def get_radius(self, key: str) -> int:
        """获取圆角值"""
        return self.radius.get(key, 4)  # 默认4px
    
    def get_animation_duration(self, key: str) -> int:
        """获取动画时长"""
        return self.animations["duration"].get(key, 300)  # 默认300ms
    
    def get_animation_easing(self, key: str) -> str:
        """获取动画缓动函数"""
        return self.animations["easing"].get(key, "ease")
    
    def get_animation(self, key: str) -> 'AnimationToken':
        """获取动画令牌"""
        duration = self.get_animation_duration(key)
        easing = self.get_animation_easing(key)
        return AnimationToken(key, duration, easing)
    
    def get_typography(self, category: str, key: str) -> 'TypographyToken':
        """获取字体令牌"""
        # 简单的字体配置映射
        font_configs = {
            'heading': {
                'h1': {'family': 'Microsoft YaHei', 'size': 32, 'weight': 700, 'line_height': 1.2},
                'h2': {'family': 'Microsoft YaHei', 'size': 24, 'weight': 700, 'line_height': 1.3},
                'h3': {'family': 'Microsoft YaHei', 'size': 20, 'weight': 700, 'line_height': 1.4},
                'h4': {'family': 'Microsoft YaHei', 'size': 18, 'weight': 600, 'line_height': 1.4},
                'h5': {'family': 'Microsoft YaHei', 'size': 16, 'weight': 600, 'line_height': 1.5},
                'h6': {'family': 'Microsoft YaHei', 'size': 14, 'weight': 600, 'line_height': 1.5},
            },
            'body': {
                'large': {'family': 'Microsoft YaHei', 'size': 16, 'weight': 400, 'line_height': 1.6},
                'medium': {'family': 'Microsoft YaHei', 'size': 14, 'weight': 400, 'line_height': 1.5},
                'small': {'family': 'Microsoft YaHei', 'size': 12, 'weight': 400, 'line_height': 1.4},
            }
        }
        
        config = font_configs.get(category, {}).get(key, font_configs['body']['medium'])
        return TypographyToken(
            font_family=config['family'],
            font_size=config['size'],
            font_weight=config['weight'],
            line_height=config['line_height']
        )
    
    def get_component_token(self, component: str, property: str, size: ComponentSize) -> Any:
        """获取组件令牌"""
        # 组件配置映射
        component_configs = {
            'button': {
                'height': {
                    ComponentSize.SMALL: 32,
                    ComponentSize.MEDIUM: 40,
                    ComponentSize.LARGE: 48,
                },
                'padding': {
                    ComponentSize.SMALL: (8, 16),
                    ComponentSize.MEDIUM: (12, 24),
                    ComponentSize.LARGE: (16, 32),
                },
                'font_size': {
                    ComponentSize.SMALL: 12,
                    ComponentSize.MEDIUM: 14,
                    ComponentSize.LARGE: 16,
                },
            },
            'input': {
                 'height': {
                     ComponentSize.SMALL: 32,
                     ComponentSize.MEDIUM: 40,
                     ComponentSize.LARGE: 48,
                 },
                 'padding': {
                     ComponentSize.SMALL: (8, 12),
                     ComponentSize.MEDIUM: (12, 16),
                     ComponentSize.LARGE: (16, 20),
                 },
             },
             'card': {
                 'padding': {
                     ComponentSize.SMALL: (12, 16),
                     ComponentSize.MEDIUM: (16, 20),
                     ComponentSize.LARGE: (20, 24),
                 },
                 'gap': {
                     ComponentSize.SMALL: 8,
                     ComponentSize.MEDIUM: 12,
                     ComponentSize.LARGE: 16,
                 },
             },
        }
        
        try:
            return component_configs[component][property][size]
        except KeyError:
            # 返回默认值
            if property == 'height':
                return 40
            elif property == 'padding':
                return (12, 16)
            elif property == 'font_size':
                return 14
            else:
                return None
    
    def get_component_colors(self, variant: ComponentVariant, state: ComponentState = ComponentState.DEFAULT) -> Dict[str, str]:
        """获取组件颜色配置"""
        color_map = {
            ComponentVariant.PRIMARY: {
                ComponentState.DEFAULT: {
                    "background": self.get_color("primary", "500"),
                    "text": self.get_color("text", "inverse"),
                    "border": self.get_color("primary", "500")
                },
                ComponentState.HOVER: {
                    "background": self.get_color("primary", "600"),
                    "text": self.get_color("text", "inverse"),
                    "border": self.get_color("primary", "600")
                },
                ComponentState.ACTIVE: {
                    "background": self.get_color("primary", "700"),
                    "text": self.get_color("text", "inverse"),
                    "border": self.get_color("primary", "700")
                },
                ComponentState.DISABLED: {
                    "background": self.get_color("neutral", "300"),
                    "text": self.get_color("text", "disabled"),
                    "border": self.get_color("neutral", "300")
                }
            },
            ComponentVariant.SECONDARY: {
                ComponentState.DEFAULT: {
                    "background": self.get_color("background", "primary"),
                    "text": self.get_color("primary", "500"),
                    "border": self.get_color("primary", "500")
                },
                ComponentState.HOVER: {
                    "background": self.get_color("primary", "50"),
                    "text": self.get_color("primary", "600"),
                    "border": self.get_color("primary", "600")
                },
                ComponentState.ACTIVE: {
                    "background": self.get_color("primary", "100"),
                    "text": self.get_color("primary", "700"),
                    "border": self.get_color("primary", "700")
                },
                ComponentState.DISABLED: {
                    "background": self.get_color("background", "primary"),
                    "text": self.get_color("text", "disabled"),
                    "border": self.get_color("neutral", "300")
                }
            },
            ComponentVariant.SUCCESS: {
                ComponentState.DEFAULT: {
                    "background": self.get_color("semantic", "success"),
                    "text": self.get_color("text", "inverse"),
                    "border": self.get_color("semantic", "success")
                }
            },
            ComponentVariant.WARNING: {
                ComponentState.DEFAULT: {
                    "background": self.get_color("semantic", "warning"),
                    "text": self.get_color("text", "inverse"),
                    "border": self.get_color("semantic", "warning")
                }
            },
            ComponentVariant.DANGER: {
                ComponentState.DEFAULT: {
                    "background": self.get_color("semantic", "danger"),
                    "text": self.get_color("text", "inverse"),
                    "border": self.get_color("semantic", "danger")
                }
            }
        }
        
        return color_map.get(variant, {}).get(state, {
            "background": self.get_color("neutral", "500"),
            "text": self.get_color("text", "inverse"),
            "border": self.get_color("neutral", "500")
        })
    
    def get_component_size_config(self, size: ComponentSize) -> Dict[str, Any]:
        """获取组件尺寸配置"""
        size_map = {
            ComponentSize.SMALL: {
                "height": 32,
                "padding_x": self.get_spacing("sm"),
                "padding_y": self.get_spacing("xs"),
                "font_size": self.get_font_size("sm"),
                "border_radius": self.get_radius("sm")
            },
            ComponentSize.MEDIUM: {
                "height": 40,
                "padding_x": self.get_spacing("md"),
                "padding_y": self.get_spacing("sm"),
                "font_size": self.get_font_size("md"),
                "border_radius": self.get_radius("md")
            },
            ComponentSize.LARGE: {
                "height": 48,
                "padding_x": self.get_spacing("lg"),
                "padding_y": self.get_spacing("md"),
                "font_size": self.get_font_size("lg"),
                "border_radius": self.get_radius("lg")
            },
            ComponentSize.XLARGE: {
                "height": 56,
                "padding_x": self.get_spacing("xl"),
                "padding_y": self.get_spacing("lg"),
                "font_size": self.get_font_size("xl"),
                "border_radius": self.get_radius("xl")
            }
        }
        
        return size_map.get(size, size_map[ComponentSize.MEDIUM])


# 全局设计令牌实例
design_tokens = DesignTokens()