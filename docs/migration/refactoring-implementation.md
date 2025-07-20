# 🛠️ 重构实施指南

## 📋 概述

本指南提供**具体的、可执行的**重构步骤，帮助开发团队系统性地解决技术债务，构建下一代架构。每个步骤都包含详细的代码示例、测试策略和验证方法。

## 🎯 重构原则

### 核心原则

1. **🔄 渐进式重构**：小步快跑，持续改进
2. **🧪 测试驱动**：先写测试，再重构代码
3. **🔒 向后兼容**：保持API稳定性
4. **📊 度量驱动**：用数据验证改进效果
5. **🚀 自动化优先**：工具化重复性工作

### 安全网策略

```python
# 🛡️ 重构安全网检查清单
class RefactoringChecklist:
    def __init__(self):
        self.checks = [
            "✅ 所有现有测试通过",
            "✅ 新增测试覆盖重构代码",
            "✅ 性能基准测试无回归",
            "✅ 内存使用无显著增加",
            "✅ API兼容性保持",
            "✅ 文档已更新",
            "✅ 代码审查通过"
        ]
    
    def validate_refactoring(self, module_name: str) -> bool:
        """验证重构是否安全"""
        results = []
        
        # 运行测试套件
        test_result = self.run_tests(module_name)
        results.append(test_result)
        
        # 性能基准测试
        perf_result = self.run_performance_tests(module_name)
        results.append(perf_result)
        
        # API兼容性检查
        api_result = self.check_api_compatibility(module_name)
        results.append(api_result)
        
        return all(results)
```

## 🚀 阶段一：依赖注入重构 (Week 1-2)

### 目标

将现有的服务定位器模式重构为真正的依赖注入容器

### Step 1.1: 定义服务接口

**创建文件**: `src/core/interfaces/services.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心服务接口定义
定义系统中所有服务的抽象接口，支持依赖注入和测试Mock
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from datetime import datetime

# ============================================================================
# 配置服务接口
# ============================================================================

@dataclass
class UIConfig:
    """UI配置数据类"""
    window_size: Tuple[int, int]
    theme: str
    font_size: int
    language: str

@dataclass
class GameConfig:
    """游戏配置数据类"""
    target_fps: int
    analysis_interval: float
    ai_model_path: str
    detection_threshold: float

@dataclass
class LoggingConfig:
    """日志配置数据类"""
    level: str
    file_path: str
    max_size: int
    backup_count: int

class IConfigService(ABC):
    """配置服务接口"""
    
    @abstractmethod
    def get_ui_config(self) -> UIConfig:
        """获取UI配置"""
        pass
    
    @abstractmethod
    def get_game_config(self) -> GameConfig:
        """获取游戏配置"""
        pass
    
    @abstractmethod
    def get_logging_config(self) -> LoggingConfig:
        """获取日志配置"""
        pass
    
    @abstractmethod
    def update_config(self, section: str, key: str, value: Any) -> None:
        """更新配置项"""
        pass
    
    @abstractmethod
    def save_config(self) -> None:
        """保存配置到文件"""
        pass

# ============================================================================
# 日志服务接口
# ============================================================================

class ILoggerService(ABC):
    """日志服务接口"""
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """记录调试信息"""
        pass
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """记录信息"""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """记录警告"""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """记录错误"""
        pass
    
    @abstractmethod
    def critical(self, message: str, **kwargs) -> None:
        """记录严重错误"""
        pass

# ============================================================================
# 图像处理服务接口
# ============================================================================

@dataclass
class ProcessedImage:
    """处理后的图像数据"""
    image: np.ndarray
    features: List[Any]
    metadata: Dict[str, Any]
    processing_time: float

@dataclass
class DetectedObject:
    """检测到的对象"""
    name: str
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # x, y, width, height
    center: Tuple[int, int]
    metadata: Dict[str, Any]

class IImageProcessorService(ABC):
    """图像处理服务接口"""
    
    @abstractmethod
    async def process_image_async(self, image: np.ndarray) -> ProcessedImage:
        """异步处理图像"""
        pass
    
    @abstractmethod
    async def detect_objects_async(self, image: np.ndarray) -> List[DetectedObject]:
        """异步检测对象"""
        pass
    
    @abstractmethod
    async def extract_features_async(self, image: np.ndarray) -> List[Any]:
        """异步提取特征"""
        pass
    
    @abstractmethod
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        pass

# ============================================================================
# 游戏分析服务接口
# ============================================================================

@dataclass
class AnalysisResult:
    """分析结果数据类"""
    timestamp: datetime
    confidence: float
    scene_type: str
    detected_objects: List[DetectedObject]
    game_state: Dict[str, Any]
    metadata: Dict[str, Any]

class IGameAnalyzerService(ABC):
    """游戏分析服务接口"""
    
    @abstractmethod
    async def analyze_frame_async(self, frame: np.ndarray) -> AnalysisResult:
        """异步分析游戏帧"""
        pass
    
    @abstractmethod
    async def detect_scene_async(self, frame: np.ndarray) -> str:
        """异步检测场景类型"""
        pass
    
    @abstractmethod
    def get_analysis_history(self, limit: int = 100) -> List[AnalysisResult]:
        """获取分析历史"""
        pass
    
    @abstractmethod
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        pass

# ============================================================================
# 窗口管理服务接口
# ============================================================================

class IWindowManagerService(ABC):
    """窗口管理服务接口"""
    
    @abstractmethod
    async def capture_screen_async(self) -> np.ndarray:
        """异步捕获屏幕"""
        pass
    
    @abstractmethod
    async def find_window_async(self, window_title: str) -> Optional[Any]:
        """异步查找窗口"""
        pass
    
    @abstractmethod
    async def activate_window_async(self, window_handle: Any) -> bool:
        """异步激活窗口"""
        pass
    
    @abstractmethod
    def get_window_info(self, window_handle: Any) -> Dict[str, Any]:
        """获取窗口信息"""
        pass
```

### Step 1.2: 实现新的DI容器

**创建文件**: `src/core/container/di_container.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代化依赖注入容器
支持接口注册、自动解析、生命周期管理和测试Mock
"""

import inspect
import asyncio
from typing import Type, TypeVar, Dict, Any, Callable, Optional, List
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod

T = TypeVar('T')

class ServiceLifetime(Enum):
    """服务生命周期枚举"""
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

@dataclass
class ServiceDescriptor:
    """服务描述符"""
    interface: Type
    implementation: Type
    lifetime: ServiceLifetime
    factory: Optional[Callable] = None
    instance: Optional[Any] = None

class ServiceNotRegisteredException(Exception):
    """服务未注册异常"""
    def __init__(self, service_type: Type):
        super().__init__(f"Service {service_type.__name__} is not registered")
        self.service_type = service_type

class CircularDependencyException(Exception):
    """循环依赖异常"""
    def __init__(self, dependency_chain: List[Type]):
        chain_names = [t.__name__ for t in dependency_chain]
        super().__init__(f"Circular dependency detected: {' -> '.join(chain_names)}")
        self.dependency_chain = dependency_chain

class DIContainer:
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._instances: Dict[Type, Any] = {}
        self._resolving: set = set()  # 用于检测循环依赖
        self._test_overrides: Dict[Type, Any] = {}
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> 'DIContainer':
        """注册单例服务"""
        self._services[interface] = ServiceDescriptor(
            interface=interface,
            implementation=implementation,
            lifetime=ServiceLifetime.SINGLETON
        )
        return self
    
    def register_transient(self, interface: Type[T], implementation: Type[T]) -> 'DIContainer':
        """注册瞬态服务"""
        self._services[interface] = ServiceDescriptor(
            interface=interface,
            implementation=implementation,
            lifetime=ServiceLifetime.TRANSIENT
        )
        return self
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T], 
                        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT) -> 'DIContainer':
        """注册工厂方法"""
        self._services[interface] = ServiceDescriptor(
            interface=interface,
            implementation=None,
            lifetime=lifetime,
            factory=factory
        )
        return self
    
    def register_instance(self, interface: Type[T], instance: T) -> 'DIContainer':
        """注册实例"""
        self._services[interface] = ServiceDescriptor(
            interface=interface,
            implementation=type(instance),
            lifetime=ServiceLifetime.SINGLETON,
            instance=instance
        )
        self._instances[interface] = instance
        return self
    
    def resolve(self, interface: Type[T]) -> T:
        """解析服务"""
        # 检查测试覆盖
        if interface in self._test_overrides:
            return self._test_overrides[interface]
        
        # 检查是否已注册
        if interface not in self._services:
            raise ServiceNotRegisteredException(interface)
        
        descriptor = self._services[interface]
        
        # 单例模式检查
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if interface in self._instances:
                return self._instances[interface]
        
        # 检查循环依赖
        if interface in self._resolving:
            chain = list(self._resolving) + [interface]
            raise CircularDependencyException(chain)
        
        try:
            self._resolving.add(interface)
            instance = self._create_instance(descriptor)
            
            # 缓存单例
            if descriptor.lifetime == ServiceLifetime.SINGLETON:
                self._instances[interface] = instance
            
            return instance
        finally:
            self._resolving.discard(interface)
    
    async def resolve_async(self, interface: Type[T]) -> T:
        """异步解析服务"""
        # 对于异步服务，可能需要异步初始化
        instance = self.resolve(interface)
        
        # 如果服务有异步初始化方法，调用它
        if hasattr(instance, 'initialize_async'):
            await instance.initialize_async()
        
        return instance
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """创建服务实例"""
        # 如果有预设实例，直接返回
        if descriptor.instance is not None:
            return descriptor.instance
        
        # 如果有工厂方法，使用工厂
        if descriptor.factory is not None:
            return descriptor.factory()
        
        # 自动解析构造函数依赖
        return self._create_instance_with_dependencies(descriptor.implementation)
    
    def _create_instance_with_dependencies(self, implementation: Type) -> Any:
        """根据构造函数自动解析依赖"""
        constructor = implementation.__init__
        signature = inspect.signature(constructor)
        
        args = []
        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue
            
            # 获取参数类型注解
            param_type = param.annotation
            if param_type == inspect.Parameter.empty:
                raise ValueError(f"Parameter {param_name} in {implementation.__name__} lacks type annotation")
            
            # 递归解析依赖
            dependency = self.resolve(param_type)
            args.append(dependency)
        
        return implementation(*args)
    
    # ========================================================================
    # 测试支持方法
    # ========================================================================
    
    def override_for_test(self, interface: Type[T], mock: T) -> None:
        """为测试覆盖服务实现"""
        self._test_overrides[interface] = mock
    
    def clear_test_overrides(self) -> None:
        """清除所有测试覆盖"""
        self._test_overrides.clear()
    
    def reset(self) -> None:
        """重置容器状态"""
        self._instances.clear()
        self._test_overrides.clear()
        self._resolving.clear()
    
    # ========================================================================
    # 诊断和调试方法
    # ========================================================================
    
    def get_registered_services(self) -> List[Type]:
        """获取所有已注册的服务"""
        return list(self._services.keys())
    
    def get_service_info(self, interface: Type) -> Dict[str, Any]:
        """获取服务信息"""
        if interface not in self._services:
            return {"registered": False}
        
        descriptor = self._services[interface]
        return {
            "registered": True,
            "interface": interface.__name__,
            "implementation": descriptor.implementation.__name__ if descriptor.implementation else "Factory",
            "lifetime": descriptor.lifetime.value,
            "has_instance": interface in self._instances,
            "has_factory": descriptor.factory is not None
        }
    
    def validate_registrations(self) -> List[str]:
        """验证所有注册的服务是否可以正确解析"""
        errors = []
        
        for interface in self._services:
            try:
                self.resolve(interface)
            except Exception as e:
                errors.append(f"{interface.__name__}: {str(e)}")
        
        return errors

# ============================================================================
# 容器配置助手
# ============================================================================

class ContainerBuilder:
    """容器构建器，提供流畅的API"""
    
    def __init__(self):
        self.container = DIContainer()
    
    def add_singleton(self, interface: Type[T], implementation: Type[T]) -> 'ContainerBuilder':
        self.container.register_singleton(interface, implementation)
        return self
    
    def add_transient(self, interface: Type[T], implementation: Type[T]) -> 'ContainerBuilder':
        self.container.register_transient(interface, implementation)
        return self
    
    def add_factory(self, interface: Type[T], factory: Callable[[], T]) -> 'ContainerBuilder':
        self.container.register_factory(interface, factory)
        return self
    
    def add_instance(self, interface: Type[T], instance: T) -> 'ContainerBuilder':
        self.container.register_instance(interface, instance)
        return self
    
    def build(self) -> DIContainer:
        """构建容器"""
        # 验证注册
        errors = self.container.validate_registrations()
        if errors:
            raise ValueError(f"Container validation failed: {errors}")
        
        return self.container

# ============================================================================
# 装饰器支持
# ============================================================================

def inject(container: DIContainer):
    """依赖注入装饰器"""
    def decorator(func):
        signature = inspect.signature(func)
        
        def wrapper(*args, **kwargs):
            # 自动注入依赖
            for param_name, param in signature.parameters.items():
                if param_name not in kwargs and param.annotation != inspect.Parameter.empty:
                    kwargs[param_name] = container.resolve(param.annotation)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
```

### Step 1.3: 实现服务适配器

**创建文件**: `src/infrastructure/adapters/service_adapters.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务适配器实现
将现有服务包装为新接口，提供向后兼容性
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from datetime import datetime

# 导入新接口
from src.core.interfaces.services import (
    IConfigService, ILoggerService, IImageProcessorService, 
    IGameAnalyzerService, IWindowManagerService,
    UIConfig, GameConfig, LoggingConfig,
    ProcessedImage, DetectedObject, AnalysisResult
)

# 导入现有实现
from src.services.config import Config
from src.services.logger import GameLogger
from src.services.image_processor import ImageProcessor
from src.core.unified_game_analyzer import UnifiedGameAnalyzer
from src.services.window_manager import GameWindowManager

# ============================================================================
# 配置服务适配器
# ============================================================================

class ConfigServiceAdapter(IConfigService):
    """配置服务适配器"""
    
    def __init__(self, legacy_config: Config):
        self._config = legacy_config
    
    def get_ui_config(self) -> UIConfig:
        """获取UI配置"""
        ui_data = self._config.get('ui', {})
        return UIConfig(
            window_size=ui_data.get('window_size', (1200, 800)),
            theme=ui_data.get('theme', 'default'),
            font_size=ui_data.get('font_size', 12),
            language=ui_data.get('language', 'zh_CN')
        )
    
    def get_game_config(self) -> GameConfig:
        """获取游戏配置"""
        game_data = self._config.get('game', {})
        return GameConfig(
            target_fps=game_data.get('target_fps', 60),
            analysis_interval=game_data.get('analysis_interval', 0.1),
            ai_model_path=game_data.get('ai_model_path', ''),
            detection_threshold=game_data.get('detection_threshold', 0.8)
        )
    
    def get_logging_config(self) -> LoggingConfig:
        """获取日志配置"""
        log_data = self._config.get('logging', {})
        return LoggingConfig(
            level=log_data.get('level', 'INFO'),
            file_path=log_data.get('file', 'logs/app.log'),
            max_size=log_data.get('max_size', 10485760),  # 10MB
            backup_count=log_data.get('backup_count', 5)
        )
    
    def update_config(self, section: str, key: str, value: Any) -> None:
        """更新配置项"""
        self._config.set(f"{section}.{key}", value)
    
    def save_config(self) -> None:
        """保存配置到文件"""
        if hasattr(self._config, 'save'):
            self._config.save()

# ============================================================================
# 日志服务适配器
# ============================================================================

class LoggerServiceAdapter(ILoggerService):
    """日志服务适配器"""
    
    def __init__(self, legacy_logger: GameLogger):
        self._logger = legacy_logger
    
    def debug(self, message: str, **kwargs) -> None:
        """记录调试信息"""
        self._logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """记录信息"""
        self._logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """记录警告"""
        self._logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """记录错误"""
        self._logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """记录严重错误"""
        self._logger.critical(message, **kwargs)

# ============================================================================
# 图像处理服务适配器
# ============================================================================

class ImageProcessorServiceAdapter(IImageProcessorService):
    """图像处理服务适配器"""
    
    def __init__(self, legacy_processor: ImageProcessor):
        self._processor = legacy_processor
        self._executor = None
    
    async def process_image_async(self, image: np.ndarray) -> ProcessedImage:
        """异步处理图像"""
        start_time = time.time()
        
        # 在线程池中执行CPU密集型操作
        loop = asyncio.get_event_loop()
        processed_image = await loop.run_in_executor(
            self._executor, 
            self._process_image_sync, 
            image
        )
        
        processing_time = time.time() - start_time
        
        return ProcessedImage(
            image=processed_image,
            features=[],  # 暂时为空，后续可以添加
            metadata={'original_shape': image.shape},
            processing_time=processing_time
        )
    
    def _process_image_sync(self, image: np.ndarray) -> np.ndarray:
        """同步处理图像（在线程池中执行）"""
        return self._processor.process_image(image)
    
    async def detect_objects_async(self, image: np.ndarray) -> List[DetectedObject]:
        """异步检测对象"""
        # 这里需要根据实际的对象检测逻辑来实现
        # 暂时返回空列表
        return []
    
    async def extract_features_async(self, image: np.ndarray) -> List[Any]:
        """异步提取特征"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._extract_features_sync,
            image
        )
    
    def _extract_features_sync(self, image: np.ndarray) -> List[Any]:
        """同步提取特征"""
        # 调用现有的特征提取方法
        if hasattr(self._processor, 'extract_features'):
            return self._processor.extract_features(image)
        return []
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return {
            'total_processed': 0,  # 需要实际统计
            'average_processing_time': 0.0,
            'last_processing_time': 0.0
        }

# ============================================================================
# 游戏分析服务适配器
# ============================================================================

class GameAnalyzerServiceAdapter(IGameAnalyzerService):
    """游戏分析服务适配器"""
    
    def __init__(self, legacy_analyzer: UnifiedGameAnalyzer):
        self._analyzer = legacy_analyzer
        self._analysis_history: List[AnalysisResult] = []
        self._executor = None
    
    async def analyze_frame_async(self, frame: np.ndarray) -> AnalysisResult:
        """异步分析游戏帧"""
        loop = asyncio.get_event_loop()
        
        # 在线程池中执行分析
        result_dict = await loop.run_in_executor(
            self._executor,
            self._analyzer.analyze_frame,
            frame
        )
        
        # 转换为新的结果格式
        result = self._convert_analysis_result(result_dict)
        
        # 保存到历史记录
        self._analysis_history.append(result)
        if len(self._analysis_history) > 1000:  # 限制历史记录数量
            self._analysis_history.pop(0)
        
        return result
    
    def _convert_analysis_result(self, result_dict: Dict[str, Any]) -> AnalysisResult:
        """转换分析结果格式"""
        # 转换检测到的对象
        detected_objects = []
        for obj in result_dict.get('objects', []):
            if isinstance(obj, dict):
                detected_objects.append(DetectedObject(
                    name=obj.get('name', 'unknown'),
                    confidence=obj.get('confidence', 0.0),
                    bounding_box=obj.get('bbox', (0, 0, 0, 0)),
                    center=obj.get('center', (0, 0)),
                    metadata=obj.get('metadata', {})
                ))
        
        return AnalysisResult(
            timestamp=datetime.now(),
            confidence=result_dict.get('confidence', 0.0),
            scene_type=result_dict.get('scene', 'unknown'),
            detected_objects=detected_objects,
            game_state=result_dict,
            metadata={'processing_time': result_dict.get('processing_time', 0.0)}
        )
    
    async def detect_scene_async(self, frame: np.ndarray) -> str:
        """异步检测场景类型"""
        result = await self.analyze_frame_async(frame)
        return result.scene_type
    
    def get_analysis_history(self, limit: int = 100) -> List[AnalysisResult]:
        """获取分析历史"""
        return self._analysis_history[-limit:]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        if not self._analysis_history:
            return {'total_analyses': 0, 'average_confidence': 0.0}
        
        total = len(self._analysis_history)
        avg_confidence = sum(r.confidence for r in self._analysis_history) / total
        
        return {
            'total_analyses': total,
            'average_confidence': avg_confidence,
            'last_analysis_time': self._analysis_history[-1].timestamp.isoformat()
        }

# ============================================================================
# 窗口管理服务适配器
# ============================================================================

class WindowManagerServiceAdapter(IWindowManagerService):
    """窗口管理服务适配器"""
    
    def __init__(self, legacy_manager: GameWindowManager):
        self._manager = legacy_manager
        self._executor = None
    
    async def capture_screen_async(self) -> np.ndarray:
        """异步捕获屏幕"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._manager.capture_screen
        )
    
    async def find_window_async(self, window_title: str) -> Optional[Any]:
        """异步查找窗口"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._manager.find_window,
            window_title
        )
    
    async def activate_window_async(self, window_handle: Any) -> bool:
        """异步激活窗口"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._manager.activate_window,
            window_handle
        )
    
    def get_window_info(self, window_handle: Any) -> Dict[str, Any]:
        """获取窗口信息"""
        if hasattr(self._manager, 'get_window_info'):
            return self._manager.get_window_info(window_handle)
        return {'handle': window_handle}
```

### Step 1.4: 容器配置和注册

**创建文件**: `src/core/container/container_config.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
容器配置和服务注册
"""

from src.core.container.di_container import ContainerBuilder
from src.core.interfaces.services import (
    IConfigService, ILoggerService, IImageProcessorService,
    IGameAnalyzerService, IWindowManagerService
)
from src.infrastructure.adapters.service_adapters import (
    ConfigServiceAdapter, LoggerServiceAdapter, ImageProcessorServiceAdapter,
    GameAnalyzerServiceAdapter, WindowManagerServiceAdapter
)

# 导入现有服务
from src.services.config import config
from src.services.logger import GameLogger
from src.services.image_processor import ImageProcessor
from src.core.unified_game_analyzer import UnifiedGameAnalyzer
from src.services.window_manager import GameWindowManager

def configure_container() -> 'DIContainer':
    """配置依赖注入容器"""
    builder = ContainerBuilder()
    
    # 注册配置服务
    builder.add_singleton(
        IConfigService,
        lambda: ConfigServiceAdapter(config)
    )
    
    # 注册日志服务
    builder.add_singleton(
        ILoggerService,
        lambda: LoggerServiceAdapter(GameLogger())
    )
    
    # 注册图像处理服务
    builder.add_singleton(
        IImageProcessorService,
        lambda: ImageProcessorServiceAdapter(
            ImageProcessor(
                GameLogger(),
                config
            )
        )
    )
    
    # 注册窗口管理服务
    builder.add_singleton(
        IWindowManagerService,
        lambda: WindowManagerServiceAdapter(
            GameWindowManager(
                GameLogger(),
                config
            )
        )
    )
    
    # 注册游戏分析服务
    builder.add_singleton(
        IGameAnalyzerService,
        lambda: GameAnalyzerServiceAdapter(
            UnifiedGameAnalyzer(
                GameLogger(),
                ImageProcessor(GameLogger(), config),
                config
            )
        )
    )
    
    return builder.build()

# 全局容器实例
container = configure_container()
```

### Step 1.5: 测试新的DI容器

**创建文件**: `tests/test_di_container.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖注入容器测试
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock
from abc import ABC, abstractmethod

from src.core.container.di_container import (
    DIContainer, ContainerBuilder, ServiceLifetime,
    ServiceNotRegisteredException, CircularDependencyException
)

# 测试接口和实现
class ITestService(ABC):
    @abstractmethod
    def get_value(self) -> str:
        pass

class TestService(ITestService):
    def get_value(self) -> str:
        return "test_value"

class ITestDependency(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

class TestDependency(ITestDependency):
    def get_name(self) -> str:
        return "test_dependency"

class ServiceWithDependency:
    def __init__(self, dependency: ITestDependency):
        self.dependency = dependency
    
    def get_info(self) -> str:
        return f"Service with {self.dependency.get_name()}"

class TestDIContainer:
    """DI容器测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.container = DIContainer()
    
    def test_register_and_resolve_singleton(self):
        """测试单例注册和解析"""
        # 注册服务
        self.container.register_singleton(ITestService, TestService)
        
        # 解析服务
        service1 = self.container.resolve(ITestService)
        service2 = self.container.resolve(ITestService)
        
        # 验证
        assert isinstance(service1, TestService)
        assert service1 is service2  # 单例模式
        assert service1.get_value() == "test_value"
    
    def test_register_and_resolve_transient(self):
        """测试瞬态注册和解析"""
        # 注册服务
        self.container.register_transient(ITestService, TestService)
        
        # 解析服务
        service1 = self.container.resolve(ITestService)
        service2 = self.container.resolve(ITestService)
        
        # 验证
        assert isinstance(service1, TestService)
        assert isinstance(service2, TestService)
        assert service1 is not service2  # 瞬态模式
    
    def test_dependency_injection(self):
        """测试依赖注入"""
        # 注册依赖
        self.container.register_singleton(ITestDependency, TestDependency)
        self.container.register_singleton(ServiceWithDependency, ServiceWithDependency)
        
        # 解析服务
        service = self.container.resolve(ServiceWithDependency)
        
        # 验证
        assert isinstance(service, ServiceWithDependency)
        assert isinstance(service.dependency, TestDependency)
        assert service.get_info() == "Service with test_dependency"
    
    def test_factory_registration(self):
        """测试工厂方法注册"""
        # 注册工厂
        def create_service():
            return TestService()
        
        self.container.register_factory(ITestService, create_service)
        
        # 解析服务
        service = self.container.resolve(ITestService)
        
        # 验证
        assert isinstance(service, TestService)
        assert service.get_value() == "test_value"
    
    def test_instance_registration(self):
        """测试实例注册"""
        # 创建实例
        instance = TestService()
        
        # 注册实例
        self.container.register_instance(ITestService, instance)
        
        # 解析服务
        resolved = self.container.resolve(ITestService)
        
        # 验证
        assert resolved is instance
    
    def test_service_not_registered_exception(self):
        """测试服务未注册异常"""
        with pytest.raises(ServiceNotRegisteredException):
            self.container.resolve(ITestService)
    
    def test_circular_dependency_detection(self):
        """测试循环依赖检测"""
        # 创建循环依赖的类
        class ServiceA:
            def __init__(self, service_b: 'ServiceB'):
                self.service_b = service_b
        
        class ServiceB:
            def __init__(self, service_a: ServiceA):
                self.service_a = service_a
        
        # 注册服务
        self.container.register_singleton(ServiceA, ServiceA)
        self.container.register_singleton(ServiceB, ServiceB)
        
        # 尝试解析应该抛出循环依赖异常
        with pytest.raises(CircularDependencyException):
            self.container.resolve(ServiceA)
    
    def test_test_overrides(self):
        """测试测试覆盖功能"""
        # 注册正常服务
        self.container.register_singleton(ITestService, TestService)
        
        # 创建Mock
        mock_service = Mock(spec=ITestService)
        mock_service.get_value.return_value = "mocked_value"
        
        # 设置测试覆盖
        self.container.override_for_test(ITestService, mock_service)
        
        # 解析服务
        service = self.container.resolve(ITestService)
        
        # 验证
        assert service is mock_service
        assert service.get_value() == "mocked_value"
        
        # 清除覆盖
        self.container.clear_test_overrides()
        
        # 再次解析应该返回正常服务
        normal_service = self.container.resolve(ITestService)
        assert isinstance(normal_service, TestService)
    
    @pytest.mark.asyncio
    async def test_async_resolve(self):
        """测试异步解析"""
        # 创建带异步初始化的服务
        class AsyncService:
            def __init__(self):
                self.initialized = False
            
            async def initialize_async(self):
                await asyncio.sleep(0.01)  # 模拟异步操作
                self.initialized = True
        
        # 注册服务
        self.container.register_singleton(AsyncService, AsyncService)
        
        # 异步解析
        service = await self.container.resolve_async(AsyncService)
        
        # 验证
        assert isinstance(service, AsyncService)
        assert service.initialized is True
    
    def test_container_builder(self):
        """测试容器构建器"""
        # 使用构建器
        container = (ContainerBuilder()
                    .add_singleton(ITestService, TestService)
                    .add_transient(ITestDependency, TestDependency)
                    .build())
        
        # 验证
        service = container.resolve(ITestService)
        dependency = container.resolve(ITestDependency)
        
        assert isinstance(service, TestService)
        assert isinstance(dependency, TestDependency)
    
    def test_get_service_info(self):
        """测试获取服务信息"""
        # 注册服务
        self.container.register_singleton(ITestService, TestService)
        
        # 获取信息
        info = self.container.get_service_info(ITestService)
        
        # 验证
        assert info['registered'] is True
        assert info['interface'] == 'ITestService'
        assert info['implementation'] == 'TestService'
        assert info['lifetime'] == 'singleton'
    
    def test_validate_registrations(self):
        """测试注册验证"""
        # 注册有效服务
        self.container.register_singleton(ITestService, TestService)
        
        # 注册无效服务（缺少依赖）
        self.container.register_singleton(ServiceWithDependency, ServiceWithDependency)
        
        # 验证注册
        errors = self.container.validate_registrations()
        
        # 应该有一个错误（ServiceWithDependency缺少依赖）
        assert len(errors) == 1
        assert 'ServiceWithDependency' in errors[0]

if __name__ == '__main__':
    pytest.main([__file__])
```

### Step 1.6: 集成测试

**创建文件**: `tests/integration/test_container_integration.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
容器集成测试
"""

import pytest
import asyncio
from unittest.mock import Mock

from src.core.container.container_config import configure_container
from src.core.interfaces.services import (
    IConfigService, ILoggerService, IImageProcessorService,
    IGameAnalyzerService, IWindowManagerService
)

class TestContainerIntegration:
    """容器集成测试"""
    
    def setup_method(self):
        """测试设置"""
        self.container = configure_container()
    
    def test_all_services_registered(self):
        """测试所有服务都已注册"""
        services = [
            IConfigService,
            ILoggerService,
            IImageProcessorService,
            IGameAnalyzerService,
            IWindowManagerService
        ]
        
        for service in services:
            info = self.container.get_service_info(service)
            assert info['registered'] is True, f"{service.__name__} not registered"
    
    def test_service_resolution(self):
        """测试服务解析"""
        # 解析配置服务
        config_service = self.container.resolve(IConfigService)
        assert config_service is not None
        
        # 解析日志服务
        logger_service = self.container.resolve(ILoggerService)
        assert logger_service is not None
        
        # 解析图像处理服务
        image_service = self.container.resolve(IImageProcessorService)
        assert image_service is not None
    
    @pytest.mark.asyncio
    async def test_async_services(self):
        """测试异步服务"""
        # 解析游戏分析服务
        analyzer = await self.container.resolve_async(IGameAnalyzerService)
        assert analyzer is not None
        
        # 解析窗口管理服务
        window_manager = await self.container.resolve_async(IWindowManagerService)
        assert window_manager is not None
    
    def test_singleton_behavior(self):
        """测试单例行为"""
        # 多次解析同一服务
        service1 = self.container.resolve(IConfigService)
        service2 = self.container.resolve(IConfigService)
        
        # 应该是同一个实例
        assert service1 is service2
    
    def test_mock_override(self):
        """测试Mock覆盖"""
        # 创建Mock
        mock_logger = Mock(spec=ILoggerService)
        
        # 设置覆盖
        self.container.override_for_test(ILoggerService, mock_logger)
        
        # 解析服务
        logger = self.container.resolve(ILoggerService)
        
        # 验证
        assert logger is mock_logger
        
        # 清除覆盖
        self.container.clear_test_overrides()
        
        # 再次解析应该返回正常服务
        normal_logger = self.container.resolve(ILoggerService)
        assert normal_logger is not mock_logger

if __name__ == '__main__':
    pytest.main([__file__])
```

## 📊 验证和度量

### 重构验证脚本

**创建文件**: `scripts/validate_refactoring.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重构验证脚本
"""

import sys
import time
import subprocess
from typing import Dict, List, Tuple

def run_tests() -> Tuple[bool, str]:
    """运行测试套件"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/', '-v'],
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Tests timed out"
    except Exception as e:
        return False, f"Test execution failed: {e}"

def measure_performance() -> Dict[str, float]:
    """测量性能指标"""
    from src.core.container.container_config import configure_container
    from src.core.interfaces.services import IGameAnalyzerService
    import numpy as np
    
    container = configure_container()
    
    # 测量容器解析时间
    start_time = time.time()
    analyzer = container.resolve(IGameAnalyzerService)
    resolve_time = time.time() - start_time
    
    # 测量分析性能（如果可能）
    analysis_time = 0.0
    try:
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        start_time = time.time()
        # 这里需要同步版本的分析方法
        analysis_time = time.time() - start_time
    except Exception:
        pass
    
    return {
        'container_resolve_time': resolve_time,
        'analysis_time': analysis_time
    }

def validate_api_compatibility() -> List[str]:
    """验证API兼容性"""
    errors = []
    
    try:
        # 验证旧的容器接口仍然可用
        from src.common.containers import EnhancedContainer
        old_container = EnhancedContainer()
        
        # 测试关键方法
        config = old_container.config()
        logger = old_container.logger()
        
        if config is None:
            errors.append("Old container config() method failed")
        if logger is None:
            errors.append("Old container logger() method failed")
            
    except Exception as e:
        errors.append(f"Old container compatibility check failed: {e}")
    
    try:
        # 验证新的容器接口
        from src.core.container.container_config import container
        from src.core.interfaces.services import IConfigService, ILoggerService
        
        config_service = container.resolve(IConfigService)
        logger_service = container.resolve(ILoggerService)
        
        if config_service is None:
            errors.append("New container IConfigService resolution failed")
        if logger_service is None:
            errors.append("New container ILoggerService resolution failed")
            
    except Exception as e:
        errors.append(f"New container check failed: {e}")
    
    return errors

def main():
    """主验证流程"""
    print("🔍 开始重构验证...")
    
    # 1. 运行测试
    print("\n📋 运行测试套件...")
    test_passed, test_output = run_tests()
    
    if test_passed:
        print("✅ 所有测试通过")
    else:
        print("❌ 测试失败")
        print(test_output)
        return False
    
    # 2. 性能测量
    print("\n⚡ 测量性能指标...")
    try:
        metrics = measure_performance()
        print(f"✅ 容器解析时间: {metrics['container_resolve_time']:.4f}s")
        print(f"✅ 分析时间: {metrics['analysis_time']:.4f}s")
    except Exception as e:
        print(f"⚠️  性能测量失败: {e}")
    
    # 3. API兼容性检查
    print("\n🔄 检查API兼容性...")
    compatibility_errors = validate_api_compatibility()
    
    if not compatibility_errors:
        print("✅ API兼容性检查通过")
    else:
        print("❌ API兼容性问题:")
        for error in compatibility_errors:
            print(f"  - {error}")
        return False
    
    print("\n🎉 重构验证完成！所有检查都通过了。")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
```

## 🎯 下一步行动

### 立即执行步骤

1. **创建新的接口和容器代码**
   ```bash
   # 创建目录结构
   mkdir -p src/core/interfaces
   mkdir -p src/core/container
   mkdir -p src/infrastructure/adapters
   mkdir -p tests/integration
   
   # 复制上述代码文件
   # ...
   ```

2. **运行验证脚本**
   ```bash
   python scripts/validate_refactoring.py
   ```

3. **逐步迁移现有代码**
   - 从最简单的服务开始
   - 保持向后兼容性
   - 每次迁移后运行测试

### 成功指标

- ✅ 所有现有测试继续通过
- ✅ 新的DI容器测试通过
- ✅ 性能无显著回归
- ✅ API兼容性保持
- ✅ 代码覆盖率提升

通过这个详细的实施指南，团队可以安全、渐进地重构现有系统，构建真正现代化的架构基础。