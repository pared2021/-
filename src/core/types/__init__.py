"""
统一类型定义模块

本模块提供系统中所有核心数据结构的统一定义，解决多重不兼容定义问题。
"""

from .unified_game_state import UnifiedGameState
from .unified_performance_metrics import UnifiedPerformanceMetrics
from .unified_action_types import UnifiedActionType
from .unified_template_match import UnifiedTemplateMatchResult
from .geometry import Point, Rectangle

__all__ = [
    'Point',
    'Rectangle', 
    'UnifiedGameState',
    'UnifiedPerformanceMetrics',
    'UnifiedActionType',
    'UnifiedTemplateMatchResult'
]