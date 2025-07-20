"""现代依赖注入容器实现

这个模块实现了一个现代的依赖注入容器，用于替代传统的服务定位器模式。
主要特性：
- 类型安全的依赖注入
- 生命周期管理（单例、瞬态、作用域）
- 自动依赖解析
- 循环依赖检测
- 装饰器支持
"""

from abc import ABC, abstractmethod
from typing import (
    TypeVar, Generic, Type, Dict, Any, Optional, Callable, 
    List, Set, Union, get_type_hints, get_origin, get_args
)
from enum import Enum
from dataclasses import dataclass
from functools import wraps
import inspect
import threading
from contextlib import contextmanager


T = TypeVar('T')


class ServiceLifetime(Enum):
    """服务生命周期枚举"""
    SINGLETON = "singleton"  # 单例模式
    TRANSIENT = "transient"  # 瞬态模式
    SCOPED = "scoped"       # 作用域模式


@dataclass
class ServiceDescriptor:
    """服务描述符"""
    service_type: Type
    implementation_type: Optional[Type] = None
    factory: Optional[Callable] = None
    instance: Optional[Any] = None
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    dependencies: Optional[List[Type]] = None


class DependencyResolutionError(Exception):
    """依赖解析错误"""
    pass


class CircularDependencyError(DependencyResolutionError):
    """循环依赖错误"""
    pass


class ServiceNotRegisteredError(DependencyResolutionError):
    """服务未注册错误"""
    pass


class DIContainer:
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._instances: Dict[Type, Any] = {}
        self._scoped_instances: Dict[str, Dict[Type, Any]] = {}
        self._resolution_stack: Set[Type] = set()
        self._lock = threading.RLock()
        self._current_scope: Optional[str] = None
    
    def register_singleton(self, service_type: Type[T], 
                          implementation_type: Optional[Type[T]] = None,
                          factory: Optional[Callable[[], T]] = None,
                          instance: Optional[T] = None) -> 'DIContainer':
        """注册单例服务"""
        return self._register_service(
            service_type, implementation_type, factory, instance, ServiceLifetime.SINGLETON
        )
    
    def register_transient(self, service_type: Type[T],
                          implementation_type: Optional[Type[T]] = None,
                          factory: Optional[Callable[[], T]] = None) -> 'DIContainer':
        """注册瞬态服务"""
        return self._register_service(
            service_type, implementation_type, factory, None, ServiceLifetime.TRANSIENT
        )
    
    def register_scoped(self, service_type: Type[T],
                       implementation_type: Optional[Type[T]] = None,
                       factory: Optional[Callable[[], T]] = None) -> 'DIContainer':
        """注册作用域服务"""
        return self._register_service(
            service_type, implementation_type, factory, None, ServiceLifetime.SCOPED
        )
    
    def _register_service(self, service_type: Type[T],
                         implementation_type: Optional[Type[T]],
                         factory: Optional[Callable[[], T]],
                         instance: Optional[T],
                         lifetime: ServiceLifetime) -> 'DIContainer':
        """内部服务注册方法"""
        with self._lock:
            # 验证注册参数
            if sum(x is not None for x in [implementation_type, factory, instance]) != 1:
                raise ValueError("必须提供且仅提供一个：implementation_type、factory 或 instance")
            
            # 分析依赖关系
            dependencies = None
            if implementation_type:
                dependencies = self._analyze_dependencies(implementation_type)
            elif factory:
                dependencies = self._analyze_factory_dependencies(factory)
            
            descriptor = ServiceDescriptor(
                service_type=service_type,
                implementation_type=implementation_type,
                factory=factory,
                instance=instance,
                lifetime=lifetime,
                dependencies=dependencies
            )
            
            self._services[service_type] = descriptor
            
            # 如果是单例且提供了实例，直接存储
            if lifetime == ServiceLifetime.SINGLETON and instance is not None:
                self._instances[service_type] = instance
            
            return self
    
    def resolve(self, service_type: Type[T]) -> T:
        """解析服务实例"""
        with self._lock:
            return self._resolve_internal(service_type)
    
    def _resolve_internal(self, service_type: Type[T]) -> T:
        """内部解析方法"""
        # 检查循环依赖
        if service_type in self._resolution_stack:
            cycle = list(self._resolution_stack) + [service_type]
            raise CircularDependencyError(f"检测到循环依赖: {' -> '.join(t.__name__ for t in cycle)}")
        
        # 检查服务是否已注册
        if service_type not in self._services:
            raise ServiceNotRegisteredError(f"服务 {service_type.__name__} 未注册")
        
        descriptor = self._services[service_type]
        
        # 根据生命周期返回实例
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            return self._get_singleton_instance(service_type, descriptor)
        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            return self._get_scoped_instance(service_type, descriptor)
        else:  # TRANSIENT
            return self._create_instance(service_type, descriptor)
    
    def _get_singleton_instance(self, service_type: Type[T], descriptor: ServiceDescriptor) -> T:
        """获取单例实例"""
        if service_type in self._instances:
            return self._instances[service_type]
        
        instance = self._create_instance(service_type, descriptor)
        self._instances[service_type] = instance
        return instance
    
    def _get_scoped_instance(self, service_type: Type[T], descriptor: ServiceDescriptor) -> T:
        """获取作用域实例"""
        if self._current_scope is None:
            raise DependencyResolutionError("尝试解析作用域服务，但当前没有活动作用域")
        
        scope_instances = self._scoped_instances.get(self._current_scope, {})
        if service_type in scope_instances:
            return scope_instances[service_type]
        
        instance = self._create_instance(service_type, descriptor)
        
        if self._current_scope not in self._scoped_instances:
            self._scoped_instances[self._current_scope] = {}
        self._scoped_instances[self._current_scope][service_type] = instance
        
        return instance
    
    def _create_instance(self, service_type: Type[T], descriptor: ServiceDescriptor) -> T:
        """创建服务实例"""
        self._resolution_stack.add(service_type)
        
        try:
            if descriptor.instance is not None:
                return descriptor.instance
            elif descriptor.factory is not None:
                return self._invoke_factory(descriptor.factory)
            elif descriptor.implementation_type is not None:
                return self._create_from_type(descriptor.implementation_type)
            else:
                raise DependencyResolutionError(f"无法创建服务 {service_type.__name__} 的实例")
        finally:
            self._resolution_stack.discard(service_type)
    
    def _invoke_factory(self, factory: Callable) -> Any:
        """调用工厂方法"""
        sig = inspect.signature(factory)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                dependency = self._resolve_internal(param.annotation)
                kwargs[param_name] = dependency
        
        return factory(**kwargs)
    
    def _create_from_type(self, implementation_type: Type[T]) -> T:
        """从类型创建实例"""
        constructor = implementation_type.__init__
        sig = inspect.signature(constructor)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            if param.annotation != inspect.Parameter.empty:
                dependency = self._resolve_internal(param.annotation)
                kwargs[param_name] = dependency
        
        return implementation_type(**kwargs)
    
    def _analyze_dependencies(self, implementation_type: Type) -> List[Type]:
        """分析类型的依赖关系"""
        dependencies = []
        
        try:
            sig = inspect.signature(implementation_type.__init__)
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                if param.annotation != inspect.Parameter.empty:
                    dependencies.append(param.annotation)
        except (ValueError, TypeError):
            # 无法分析签名，返回空依赖列表
            pass
        
        return dependencies
    
    def _analyze_factory_dependencies(self, factory: Callable) -> List[Type]:
        """分析工厂方法的依赖关系"""
        dependencies = []
        
        try:
            sig = inspect.signature(factory)
            for param_name, param in sig.parameters.items():
                if param.annotation != inspect.Parameter.empty:
                    dependencies.append(param.annotation)
        except (ValueError, TypeError):
            # 无法分析签名，返回空依赖列表
            pass
        
        return dependencies
    
    @contextmanager
    def create_scope(self, scope_name: str = None):
        """创建作用域上下文"""
        if scope_name is None:
            scope_name = f"scope_{id(threading.current_thread())}"
        
        old_scope = self._current_scope
        self._current_scope = scope_name
        
        try:
            yield
        finally:
            # 清理作用域实例
            if scope_name in self._scoped_instances:
                del self._scoped_instances[scope_name]
            self._current_scope = old_scope
    
    def is_registered(self, service_type: Type) -> bool:
        """检查服务是否已注册"""
        return service_type in self._services
    
    def get_service_info(self, service_type: Type) -> Optional[ServiceDescriptor]:
        """获取服务信息"""
        return self._services.get(service_type)
    
    def get_all_services(self) -> Dict[Type, ServiceDescriptor]:
        """获取所有已注册的服务"""
        return self._services.copy()
    
    def clear(self):
        """清空容器"""
        with self._lock:
            self._services.clear()
            self._instances.clear()
            self._scoped_instances.clear()
            self._resolution_stack.clear()


class ContainerBuilder:
    """容器构建器"""
    
    def __init__(self):
        self._container = DIContainer()
    
    def add_singleton(self, service_type: Type[T],
                     implementation_type: Optional[Type[T]] = None,
                     factory: Optional[Callable[[], T]] = None,
                     instance: Optional[T] = None) -> 'ContainerBuilder':
        """添加单例服务"""
        self._container.register_singleton(service_type, implementation_type, factory, instance)
        return self
    
    def add_transient(self, service_type: Type[T],
                     implementation_type: Optional[Type[T]] = None,
                     factory: Optional[Callable[[], T]] = None) -> 'ContainerBuilder':
        """添加瞬态服务"""
        self._container.register_transient(service_type, implementation_type, factory)
        return self
    
    def add_scoped(self, service_type: Type[T],
                  implementation_type: Optional[Type[T]] = None,
                  factory: Optional[Callable[[], T]] = None) -> 'ContainerBuilder':
        """添加作用域服务"""
        self._container.register_scoped(service_type, implementation_type, factory)
        return self
    
    def build(self) -> DIContainer:
        """构建容器"""
        return self._container


# 装饰器支持
def injectable(lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT):
    """标记类为可注入的装饰器"""
    def decorator(cls):
        cls._di_lifetime = lifetime
        return cls
    return decorator


def inject(service_type: Type[T]):
    """依赖注入装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 这里需要访问当前容器实例
            # 在实际使用中，可以通过全局容器或上下文获取
            pass
        return wrapper
    return decorator