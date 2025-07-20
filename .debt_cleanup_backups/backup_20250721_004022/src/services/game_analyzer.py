#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏分析器兼容性模块
为了保持向后兼容性，这个模块重新导出统一游戏分析器
"""

# 导入统一游戏分析器
from src.core.unified_game_analyzer import UnifiedGameAnalyzer

# 为了兼容性，创建别名
GameAnalyzer = UnifiedGameAnalyzer

# 导出
__all__ = ['GameAnalyzer', 'UnifiedGameAnalyzer']