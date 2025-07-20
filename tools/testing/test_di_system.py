"""简单的依赖注入系统测试

这个脚本用于验证新的依赖注入系统是否正常工作。
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print(f"项目根目录: {project_root}")
print(f"Python版本: {sys.version}")
print("开始测试依赖注入系统...")

try:
    # 测试基本导入
    print("\n1. 测试基本导入...")
    from src.core.interfaces.services import IConfigService, ILoggerService
    print("✓ 接口导入成功")
    
    from src.core.container.di_container import DIContainer
    print("✓ DI容器导入成功")
    
    from src.core.container.container_config import ContainerConfiguration
    print("✓ 容器配置导入成功")
    
    # 测试适配器导入
    print("\n2. 测试适配器导入...")
    from src.infrastructure.adapters import ConfigServiceAdapter, LoggerServiceAdapter
    print("✓ 适配器导入成功")
    
    # 测试容器初始化
    print("\n3. 测试容器初始化...")
    container = DIContainer()
    config = ContainerConfiguration()
    config.configure_container(container)
    print("✓ 容器初始化成功")
    
    # 测试服务解析
    print("\n4. 测试服务解析...")
    config_service = container.resolve(IConfigService)
    print(f"✓ 配置服务解析成功: {type(config_service).__name__}")
    
    logger_service = container.resolve(ILoggerService)
    print(f"✓ 日志服务解析成功: {type(logger_service).__name__}")
    
    # 测试服务功能
    print("\n5. 测试服务功能...")
    
    # 测试配置服务
    config_service.set('test.key', 'test_value')
    value = config_service.get('test.key')
    assert value == 'test_value', f"配置服务测试失败: 期望 'test_value', 实际 '{value}'"
    print("✓ 配置服务功能正常")
    
    # 测试日志服务
    logger_service.info("这是一条测试日志")
    print("✓ 日志服务功能正常")
    
    # 测试便捷函数
    print("\n6. 测试便捷函数...")
    from src.core.container.container_config import resolve_service, get_container
    
    test_config = resolve_service(IConfigService)
    test_logger = resolve_service(ILoggerService)
    test_container = get_container()
    
    print("✓ 便捷函数正常工作")
    
    print("\n" + "="*50)
    print("🎉 所有测试通过！依赖注入系统工作正常！")
    print("="*50)
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()