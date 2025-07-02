"""
依赖注入容器
管理应用服务的依赖关系和生命周期
支持异步初始化和资源清理
"""

import asyncio
import logging
from typing import Any, Dict, Optional, Type, TypeVar, Callable
from abc import ABC, abstractmethod
from functools import lru_cache

from src.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

T = TypeVar('T')


class ServiceLifecycle(ABC):
    """服务生命周期接口"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """初始化服务"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """关闭服务"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        pass


class DIContainer:
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._lifecycle_services: list[ServiceLifecycle] = []
        self._initialized = False
    
    def register_singleton(self, service_type: Type[T], instance: T) -> None:
        """注册单例服务"""
        service_name = service_type.__name__
        self._singletons[service_name] = instance
        logger.debug(f"已注册单例服务: {service_name}")
    
    def register_factory(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """注册工厂服务"""
        service_name = service_type.__name__
        self._factories[service_name] = factory
        logger.debug(f"已注册工厂服务: {service_name}")
    
    def register_service(self, service_name: str, service_instance: Any) -> None:
        """注册命名服务"""
        self._services[service_name] = service_instance
        if isinstance(service_instance, ServiceLifecycle):
            self._lifecycle_services.append(service_instance)
        logger.debug(f"已注册服务: {service_name}")
    
    def get_service(self, service_type: Type[T]) -> T:
        """获取服务实例"""
        service_name = service_type.__name__
        
        # 检查单例
        if service_name in self._singletons:
            return self._singletons[service_name]
        
        # 检查工厂
        if service_name in self._factories:
            instance = self._factories[service_name]()
            self._singletons[service_name] = instance  # 缓存为单例
            return instance
        
        raise ValueError(f"服务未注册: {service_name}")
    
    def get_named_service(self, service_name: str) -> Any:
        """获取命名服务"""
        if service_name in self._services:
            return self._services[service_name]
        raise ValueError(f"命名服务未注册: {service_name}")
    
    async def init_resources(self) -> None:
        """初始化所有资源"""
        if self._initialized:
            logger.warning("容器已经初始化")
            return
        
        logger.info("开始初始化依赖注入容器...")
        
        try:
            # 并行初始化所有生命周期服务
            if self._lifecycle_services:
                await asyncio.gather(
                    *[service.initialize() for service in self._lifecycle_services]
                )
            
            self._initialized = True
            logger.info("依赖注入容器初始化完成")
            
        except Exception as e:
            logger.error(f"容器初始化失败: {e}")
            raise
    
    async def shutdown(self) -> None:
        """关闭所有资源"""
        if not self._initialized:
            logger.warning("容器未初始化，无需关闭")
            return
        
        logger.info("开始关闭依赖注入容器...")
        
        try:
            # 并行关闭所有生命周期服务
            if self._lifecycle_services:
                await asyncio.gather(
                    *[service.shutdown() for service in self._lifecycle_services],
                    return_exceptions=True
                )
            
            # 清理容器
            self._services.clear()
            self._singletons.clear()
            self._lifecycle_services.clear()
            self._initialized = False
            
            logger.info("依赖注入容器关闭完成")
            
        except Exception as e:
            logger.error(f"容器关闭失败: {e}")
            raise
    
    async def health_check_all(self) -> Dict[str, Any]:
        """检查所有服务的健康状态"""
        health_results = {}
        
        for service in self._lifecycle_services:
            service_name = service.__class__.__name__
            try:
                health_status = await service.health_check()
                health_results[service_name] = health_status
            except Exception as e:
                health_results[service_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return health_results
    
    # 服务访问器方法
    def database_service(self):
        """获取数据库服务"""
        return self.get_named_service("database_service")
    
    def cache_service(self):
        """获取缓存服务"""
        return self.get_named_service("cache_service")
    
    def agent_service(self):
        """获取AI Agent服务"""
        return self.get_named_service("agent_service")
    
    def vision_service(self):
        """获取视觉处理服务"""
        return self.get_named_service("vision_service")
    
    def game_service(self):
        """获取游戏管理服务"""
        return self.get_named_service("game_service")
    
    def automation_service(self):
        """获取自动化服务"""
        return self.get_named_service("automation_service")


# 占位服务实现（临时）
class PlaceholderService(ServiceLifecycle):
    """占位服务，用于开发阶段"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.is_available = False
    
    async def initialize(self) -> None:
        """初始化占位服务"""
        logger.info(f"初始化占位服务: {self.service_name}")
        self.is_available = True
    
    async def shutdown(self) -> None:
        """关闭占位服务"""
        logger.info(f"关闭占位服务: {self.service_name}")
        self.is_available = False
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy" if self.is_available else "unhealthy",
            "available": self.is_available,
            "service_type": "placeholder",
            "message": f"占位服务 {self.service_name} 运行中"
        }
    
    async def ping(self) -> bool:
        """连接测试"""
        return self.is_available
    
    def get_connection_info(self) -> str:
        """获取连接信息"""
        return f"placeholder://{self.service_name}"


def create_container() -> DIContainer:
    """创建配置好的容器实例"""
    container = DIContainer()
    
    # 注册占位服务（开发阶段）
    container.register_service("database_service", PlaceholderService("database"))
    container.register_service("cache_service", PlaceholderService("cache"))
    container.register_service("agent_service", PlaceholderService("ai_agents"))
    container.register_service("vision_service", PlaceholderService("vision"))
    container.register_service("game_service", PlaceholderService("game"))
    container.register_service("automation_service", PlaceholderService("automation"))
    
    logger.info("依赖注入容器创建完成（使用占位服务）")
    return container


# 全局容器实例
_container: Optional[DIContainer] = None


@lru_cache()
def get_container() -> DIContainer:
    """获取全局容器实例（单例）"""
    global _container
    if _container is None:
        _container = create_container()
    return _container


__all__ = [
    "ServiceLifecycle",
    "DIContainer", 
    "PlaceholderService",
    "create_container",
    "get_container"
] 