"""统一窗口管理器模块

这个模块提供了统一的窗口管理接口，解决了原有系统中多重WindowInfo定义冲突、
数据流混乱和架构层次混乱的问题。

主要组件:
- UnifiedWindowManager: 统一的窗口管理器实现
- WindowManagerFactory: 窗口管理器工厂
- LegacyWindowAdapter: 向后兼容适配器

使用示例:
    # 使用工厂创建窗口管理器
    from src.infrastructure.window_manager import get_window_manager
    
    window_manager = get_window_manager()
    windows = window_manager.get_window_list()
    
    # 或者使用遗留适配器进行平滑迁移
    from src.infrastructure.adapters.legacy_window_adapter import get_legacy_window_adapter
    
    adapter = get_legacy_window_adapter()
    window_list = adapter.get_window_list()
"""

from .unified_window_manager import UnifiedWindowManager
from .window_manager_factory import WindowManagerFactory, get_window_manager_factory

# 导出主要接口
__all__ = [
    'UnifiedWindowManager',
    'WindowManagerFactory', 
    'get_window_manager_factory',
    'get_window_manager'
]

# 便捷函数
def get_window_manager(config=None):
    """获取窗口管理器实例
    
    Args:
        config: 可选的配置字典
        
    Returns:
        UnifiedWindowManager: 窗口管理器实例
    """
    factory = get_window_manager_factory()
    return factory.create_window_manager(config or {})