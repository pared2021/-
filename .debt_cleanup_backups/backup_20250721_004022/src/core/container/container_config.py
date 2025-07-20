"""依赖注入容器配置

这个模块负责配置和初始化依赖注入容器，注册所有服务及其依赖关系。
实现了服务的自动发现和注册，支持不同的生命周期管理。
"""

from typing import Dict, Any, Type, Optional
from pathlib import Path

from .di_container import DIContainer, ContainerBuilder, ServiceLifetime
from ..interfaces.services import (
    IConfigService, ILoggerService, IWindowManagerService,
    IImageProcessorService, IGameAnalyzer, IActionSimulatorService,
    IGameStateService, IAutomationService, IErrorHandler,
    IStateManager, IPerformanceMonitor
)


class ContainerConfiguration:
    """容器配置类"""
    
    def __init__(self):
        self._container: Optional[DIContainer] = None
        self._is_configured = False
    
    def configure_container(self) -> DIContainer:
        """配置并返回依赖注入容器"""
        if self._container is not None and self._is_configured:
            return self._container
        
        builder = ContainerBuilder()
        
        # 注册核心服务（单例）
        self._register_core_services(builder)
        
        # 注册基础服务（单例）
        self._register_basic_services(builder)
        
        # 注册高级服务（单例或作用域）
        self._register_advanced_services(builder)
        
        # 注册工具服务（瞬态）
        self._register_utility_services(builder)
        
        self._container = builder.build()
        self._is_configured = True
        
        return self._container
    
    def _register_core_services(self, builder: ContainerBuilder) -> None:
        """注册核心服务"""
        # 配置服务 - 使用现有的统一配置系统
        builder.add_singleton(
            IConfigService,
            factory=self._create_config_service
        )
        
        # 日志服务
        builder.add_singleton(
            ILoggerService,
            factory=self._create_logger_service
        )
    
    def _register_basic_services(self, builder: ContainerBuilder) -> None:
        """注册基础服务"""
        # 错误处理服务
        builder.add_singleton(
            IErrorHandler,
            factory=self._create_error_handler_service
        )
        
        # 窗口管理服务
        builder.add_singleton(
            IWindowManagerService,
            factory=self._create_window_manager_service
        )
        
        # 图像处理服务
        builder.add_singleton(
            IImageProcessorService,
            factory=self._create_image_processor_service
        )
    
    def _register_advanced_services(self, builder: ContainerBuilder) -> None:
        """注册高级服务"""
        # 游戏分析服务
        builder.add_singleton(
            IGameAnalyzer,
            factory=self._create_game_analyzer_service
        )
        
        # 动作模拟服务
        builder.add_singleton(
            IActionSimulatorService,
            factory=self._create_action_simulator_service
        )
        
        # 游戏状态服务
        builder.add_singleton(
            IGameStateService,
            factory=self._create_game_state_service
        )
        
        # 自动化服务
        builder.add_singleton(
            IAutomationService,
            factory=self._create_automation_service
        )
        
        # 状态管理服务
        builder.add_singleton(
            IStateManager,
            factory=self._create_state_manager_service
        )
    
    def _register_utility_services(self, builder: ContainerBuilder) -> None:
        """注册工具服务"""
        # 性能监控服务
        builder.add_scoped(
            IPerformanceMonitor,
            factory=self._create_performance_monitor_service
        )
    
    # ========================================================================
    # 服务工厂方法
    # ========================================================================
    
    def _create_config_service(self, container: DIContainer) -> IConfigService:
        """创建配置服务"""
        # 导入适配器来包装现有的配置系统
        from ...infrastructure.adapters import ConfigServiceAdapter
        return ConfigServiceAdapter()
    
    def _create_logger_service(self, container: DIContainer) -> ILoggerService:
        """创建日志服务"""
        from ...infrastructure.adapters import LoggerServiceAdapter
        config_service = container.resolve(IConfigService)
        return LoggerServiceAdapter(config_service)
    
    def _create_error_handler_service(self, container: DIContainer) -> IErrorHandler:
        """创建错误处理服务"""
        from ...infrastructure.adapters import ErrorHandlerServiceAdapter
        logger_service = container.resolve(ILoggerService)
        return ErrorHandlerServiceAdapter(logger_service)
    
    def _create_window_manager_service(self, container: DIContainer) -> IWindowManagerService:
        """创建窗口管理服务"""
        from ...infrastructure.adapters import WindowManagerServiceAdapter
        logger_service = container.resolve(ILoggerService)
        config_service = container.resolve(IConfigService)
        error_handler = container.resolve(IErrorHandler)
        return WindowManagerServiceAdapter(logger_service, config_service, error_handler)
    
    def _create_image_processor_service(self, container: DIContainer) -> IImageProcessorService:
        """创建图像处理服务"""
        from ...infrastructure.adapters import ImageProcessorServiceAdapter
        logger_service = container.resolve(ILoggerService)
        config_service = container.resolve(IConfigService)
        error_handler = container.resolve(IErrorHandler)
        return ImageProcessorServiceAdapter(logger_service, config_service, error_handler)
    
    def _create_game_analyzer_service(self, container: DIContainer) -> IGameAnalyzer:
        """创建游戏分析服务"""
        from ...infrastructure.adapters import GameAnalyzerServiceAdapter
        logger_service = container.resolve(ILoggerService)
        image_processor = container.resolve(IImageProcessorService)
        config_service = container.resolve(IConfigService)
        error_handler = container.resolve(IErrorHandler)
        return GameAnalyzerServiceAdapter(logger_service, image_processor, config_service, error_handler)
    
    def _create_action_simulator_service(self, container: DIContainer) -> IActionSimulatorService:
        """创建动作模拟服务"""
        from ...infrastructure.adapters import ActionSimulatorServiceAdapter
        logger_service = container.resolve(ILoggerService)
        window_manager = container.resolve(IWindowManagerService)
        config_service = container.resolve(IConfigService)
        error_handler = container.resolve(IErrorHandler)
        return ActionSimulatorServiceAdapter(logger_service, window_manager, config_service, error_handler)
    
    def _create_game_state_service(self, container: DIContainer) -> IGameStateService:
        """创建游戏状态服务"""
        from ...infrastructure.adapters import GameStateServiceAdapter
        logger_service = container.resolve(ILoggerService)
        game_analyzer = container.resolve(IGameAnalyzer)
        error_handler = container.resolve(IErrorHandler)
        return GameStateServiceAdapter(logger_service, game_analyzer, error_handler)
    
    def _create_automation_service(self, container: DIContainer) -> IAutomationService:
        """创建自动化服务"""
        from ...infrastructure.adapters import AutomationServiceAdapter
        error_handler = container.resolve(IErrorHandler)
        window_manager = container.resolve(IWindowManagerService)
        image_processor = container.resolve(IImageProcessorService)
        action_simulator = container.resolve(IActionSimulatorService)
        game_analyzer = container.resolve(IGameAnalyzer)
        return AutomationServiceAdapter(
            error_handler, window_manager, image_processor, 
            action_simulator, game_analyzer
        )
    
    def _create_state_manager_service(self, container: DIContainer) -> IStateManager:
        """创建状态管理服务"""
        from ...infrastructure.adapters import StateManagerServiceAdapter
        logger_service = container.resolve(ILoggerService)
        config_service = container.resolve(IConfigService)
        return StateManagerServiceAdapter(logger_service, config_service)
    
    def _create_performance_monitor_service(self, container: DIContainer) -> IPerformanceMonitor:
        """创建性能监控服务"""
        from ...infrastructure.adapters import PerformanceMonitorServiceAdapter
        logger_service = container.resolve(ILoggerService)
        return PerformanceMonitorServiceAdapter(logger_service)
    
    def get_container(self) -> Optional[DIContainer]:
        """获取已配置的容器"""
        return self._container
    
    def is_configured(self) -> bool:
        """检查容器是否已配置"""
        return self._is_configured
    
    def reset(self) -> None:
        """重置容器配置"""
        if self._container:
            self._container.clear()
        self._container = None
        self._is_configured = False


# 全局容器配置实例
_container_config = ContainerConfiguration()


def configure_container() -> DIContainer:
    """配置并返回全局容器实例"""
    return _container_config.configure_container()


def get_container() -> Optional[DIContainer]:
    """获取全局容器实例"""
    return _container_config.get_container()


def reset_container() -> None:
    """重置全局容器"""
    _container_config.reset()


def is_container_configured() -> bool:
    """检查全局容器是否已配置"""
    return _container_config.is_configured()


# 便捷的服务解析函数
def resolve_service(service_type: Type) -> Any:
    """解析服务实例"""
    container = get_container()
    if container is None:
        raise RuntimeError("容器尚未配置，请先调用 configure_container()")
    return container.resolve(service_type)


def resolve_config_service() -> IConfigService:
    """解析配置服务"""
    return resolve_service(IConfigService)


def resolve_logger_service() -> ILoggerService:
    """解析日志服务"""
    return resolve_service(ILoggerService)


def resolve_window_manager_service() -> IWindowManagerService:
    """解析窗口管理服务"""
    return resolve_service(IWindowManagerService)


def resolve_image_processor_service() -> IImageProcessorService:
    """解析图像处理服务"""
    return resolve_service(IImageProcessorService)


def resolve_game_analyzer_service() -> IGameAnalyzer:
    """解析游戏分析服务"""
    return resolve_service(IGameAnalyzer)


def resolve_action_simulator_service() -> IActionSimulatorService:
    """解析动作模拟服务"""
    return resolve_service(IActionSimulatorService)


def resolve_game_state_service() -> IGameStateService:
    """解析游戏状态服务"""
    return resolve_service(IGameStateService)


def resolve_automation_service() -> IAutomationService:
    """解析自动化服务"""
    return resolve_service(IAutomationService)


def resolve_error_handler_service() -> IErrorHandler:
    """解析错误处理服务"""
    return resolve_service(IErrorHandler)