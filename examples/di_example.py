"""依赖注入系统使用示例

这个示例展示了如何使用新的依赖注入系统来获取和使用各种服务。
演示了Clean Architecture和依赖倒置原则的实际应用。
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ..src.core.container.container_config import get_container, resolve_service
from ..src.core.interfaces.services import (
    IConfigService, ILoggerService, IErrorHandler,
    IWindowManagerService, IImageProcessorService,
    IGameAnalyzer, IActionSimulatorService,
    IGameStateService, IAutomationService,
    IStateManager, IPerformanceMonitor
)


def demonstrate_config_service():
    """演示配置服务的使用"""
    print("\n=== 配置服务演示 ===")
    
    config_service = resolve_service(IConfigService)
    
    # 设置一些配置
    config_service.set('app.name', 'Game Automation')
    config_service.set('app.version', '2.0.0')
    config_service.set('debug.enabled', True)
    
    # 读取配置
    app_name = config_service.get('app.name', 'Unknown')
    app_version = config_service.get('app.version', '1.0.0')
    debug_enabled = config_service.get('debug.enabled', False)
    
    print(f"应用名称: {app_name}")
    print(f"应用版本: {app_version}")
    print(f"调试模式: {debug_enabled}")
    
    # 检查配置是否存在
    if config_service.has('app.name'):
        print("✓ 应用名称配置存在")
    
    # 获取所有配置
    all_config = config_service.get_all()
    print(f"总配置项数量: {len(all_config)}")


def demonstrate_logger_service():
    """演示日志服务的使用"""
    print("\n=== 日志服务演示 ===")
    
    logger_service = resolve_service(ILoggerService)
    
    # 记录不同级别的日志
    logger_service.info("这是一条信息日志")
    logger_service.warning("这是一条警告日志")
    logger_service.error("这是一条错误日志")
    logger_service.debug("这是一条调试日志")
    
    # 记录带上下文的日志
    logger_service.info("用户操作", user_id=123, action="click", target="button")
    
    # 记录性能日志
    logger_service.log_performance("image_processing", 0.15, {"width": 1920, "height": 1080})
    
    print("✓ 日志记录完成")


def demonstrate_error_handler():
    """演示错误处理服务的使用"""
    print("\n=== 错误处理服务演示 ===")
    
    error_handler = resolve_service(IErrorHandler)
    
    # 模拟一个错误
    try:
        raise ValueError("这是一个示例错误")
    except Exception as e:
        error_handler.handle_error(e, {
            'operation': 'demonstrate_error_handler',
            'user_action': 'testing_error_handling'
        })
    
    # 安全执行一个可能出错的操作
    def risky_operation():
        if True:  # 模拟错误条件
            raise RuntimeError("操作失败")
        return "成功"
    
    result = error_handler.safe_execute(risky_operation, default_value="默认值")
    print(f"安全执行结果: {result}")
    
    print("✓ 错误处理演示完成")


def demonstrate_window_manager():
    """演示窗口管理服务的使用"""
    print("\n=== 窗口管理服务演示 ===")
    
    window_manager = resolve_service(IWindowManagerService)
    
    # 查找窗口
    windows = window_manager.find_windows("记事本")
    print(f"找到 {len(windows)} 个记事本窗口")
    
    # 获取活动窗口
    active_window = window_manager.get_active_window()
    if active_window:
        print(f"当前活动窗口: {active_window.title}")
        print(f"窗口位置: ({active_window.x}, {active_window.y})")
        print(f"窗口大小: {active_window.width} x {active_window.height}")
    
    print("✓ 窗口管理演示完成")


def demonstrate_image_processor():
    """演示图像处理服务的使用"""
    print("\n=== 图像处理服务演示 ===")
    
    image_processor = resolve_service(IImageProcessorService)
    
    # 创建一个简单的测试图像（如果有的话）
    try:
        import numpy as np
        
        # 创建一个100x100的测试图像
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[25:75, 25:75] = [255, 0, 0]  # 红色方块
        
        # 获取图像信息
        info = image_processor.get_image_info(test_image)
        print(f"测试图像信息: {info}")
        
        # 调整图像大小
        resized = image_processor.resize_image(test_image, 50, 50)
        resized_info = image_processor.get_image_info(resized)
        print(f"调整后图像信息: {resized_info}")
        
        # 转换为灰度
        gray = image_processor.convert_to_grayscale(test_image)
        gray_info = image_processor.get_image_info(gray)
        print(f"灰度图像信息: {gray_info}")
        
        print("✓ 图像处理演示完成")
        
    except ImportError:
        print("⚠ 未安装numpy，跳过图像处理演示")


def demonstrate_state_manager():
    """演示状态管理服务的使用"""
    print("\n=== 状态管理服务演示 ===")
    
    state_manager = resolve_service(IStateManager)
    
    # 添加状态
    state_manager.add_state('idle')
    state_manager.add_state('working')
    state_manager.add_state('paused')
    
    # 添加转换
    state_manager.add_transition('idle', 'working', 'start')
    state_manager.add_transition('working', 'paused', 'pause')
    state_manager.add_transition('paused', 'working', 'resume')
    state_manager.add_transition('working', 'idle', 'stop')
    state_manager.add_transition('paused', 'idle', 'stop')
    
    # 获取当前状态
    current_state = state_manager.get_current_state()
    print(f"当前状态: {current_state}")
    
    # 执行状态转换
    if state_manager.set_state('idle'):
        print("✓ 设置为空闲状态")
    
    if state_manager.trigger_transition('start'):
        print("✓ 触发开始转换")
        print(f"新状态: {state_manager.get_current_state()}")
    
    # 获取可用触发器
    triggers = state_manager.get_available_triggers()
    print(f"可用触发器: {triggers}")
    
    # 获取所有状态
    all_states = state_manager.get_states()
    print(f"所有状态: {all_states}")
    
    print("✓ 状态管理演示完成")


def demonstrate_performance_monitor():
    """演示性能监控服务的使用"""
    print("\n=== 性能监控服务演示 ===")
    
    performance_monitor = resolve_service(IPerformanceMonitor)
    
    # 获取当前性能指标
    current_metrics = performance_monitor.get_current_metrics()
    print("当前性能指标:")
    for key, value in current_metrics.items():
        if isinstance(value, (int, float)):
            if 'percent' in key:
                print(f"  {key}: {value:.1f}%")
            elif 'memory' in key and 'mb' in key:
                print(f"  {key}: {value:.1f} MB")
            elif 'bytes' in key:
                print(f"  {key}: {value / (1024*1024):.1f} MB")
            else:
                print(f"  {key}: {value}")
    
    # 获取性能摘要
    summary = performance_monitor.get_performance_summary()
    monitoring_status = summary.get('monitoring_status', {})
    print(f"\n监控状态: {'运行中' if monitoring_status.get('is_monitoring') else '已停止'}")
    print(f"总样本数: {monitoring_status.get('total_samples', 0)}")
    
    print("✓ 性能监控演示完成")


def main():
    """主函数"""
    print("游戏自动化系统 - 依赖注入演示")
    print("=" * 50)
    
    try:
        # 初始化容器
        container = get_container()
        if not container:
            print("❌ 无法初始化依赖注入容器")
            return
        
        print("✓ 依赖注入容器初始化成功")
        
        # 演示各个服务
        demonstrate_config_service()
        demonstrate_logger_service()
        demonstrate_error_handler()
        demonstrate_window_manager()
        demonstrate_image_processor()
        demonstrate_state_manager()
        demonstrate_performance_monitor()
        
        print("\n" + "=" * 50)
        print("✓ 所有服务演示完成")
        print("\n新的依赖注入系统已成功集成到游戏自动化项目中！")
        print("现在可以使用 resolve_service() 函数来获取任何服务实例。")
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()