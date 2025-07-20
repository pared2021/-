"""适配器模块

这个包包含了各种适配器实现，用于将现有系统适配到新的接口定义。
使用适配器模式来保持向后兼容性，同时支持新的依赖注入架构。
"""

# 导入所有适配器类
from .config_adapter import ConfigServiceAdapter
from .logger_adapter import LoggerServiceAdapter
from .error_handler_adapter import ErrorHandlerServiceAdapter
from .window_manager_adapter import WindowManagerServiceAdapter
from .image_processor_adapter import ImageProcessorServiceAdapter
from .game_analyzer_adapter import GameAnalyzerServiceAdapter
from .action_simulator_adapter import ActionSimulatorServiceAdapter
from .game_state_adapter import GameStateServiceAdapter
from .automation_adapter import AutomationServiceAdapter
from .state_manager_adapter import StateManagerServiceAdapter
from .performance_monitor_adapter import PerformanceMonitorServiceAdapter
from .legacy_window_adapter import LegacyWindowAdapter, get_legacy_window_adapter

# 导出所有适配器类
__all__ = [
    'ConfigServiceAdapter',
    'LoggerServiceAdapter', 
    'ErrorHandlerServiceAdapter',
    'WindowManagerServiceAdapter',
    'ImageProcessorServiceAdapter',
    'GameAnalyzerServiceAdapter',
    'ActionSimulatorServiceAdapter',
    'GameStateServiceAdapter',
    'AutomationServiceAdapter',
    'StateManagerServiceAdapter',
    'PerformanceMonitorServiceAdapter',
    'LegacyWindowAdapter',
    'get_legacy_window_adapter'
]