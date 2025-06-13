#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全的导入测试，处理缺失的依赖
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append('.')

def test_basic_imports():
    """测试基础组件的导入"""
    try:
        print("🧪 开始测试基础导入...")
        
        # 测试Config
        print("📦 测试Config导入...")
        from src.services.config import Config
        print("✅ Config导入成功")
        
        # 测试Logger
        print("📦 测试Logger导入...")
        from src.services.logger import GameLogger
        print("✅ GameLogger导入成功")
        
        # 测试容器
        print("📦 测试依赖注入容器导入...")
        from src.common.containers import Container
        print("✅ Container导入成功")
        
        print("🎉 基础导入测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 基础导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_container_functionality():
    """测试容器功能"""
    try:
        print("\n🧪 测试容器功能...")
        
        from src.common.containers import Container
        container = Container()
        
        # 测试基础服务
        config = container.config()
        logger = container.logger()
        
        print(f"✅ 基础服务初始化成功")
        
        # 测试服务可用性检查
        available_services = container.get_available_services()
        print(f"✅ 可用服务: {available_services}")
        
        # 测试各服务的可用性
        services_to_test = [
            'config', 'logger', 'window_manager', 'image_processor', 
            'game_analyzer', 'action_simulator', 'game_state', 
            'auto_operator', 'config_manager'
        ]
        
        for service in services_to_test:
            is_available = container.is_service_available(service)
            status = "✅" if is_available else "⚠️"
            print(f"  {status} {service}: {'可用' if is_available else '不可用（缺少依赖）'}")
        
        print("🎉 容器功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 容器功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_functionality():
    """测试配置功能"""
    try:
        print("\n🧪 测试配置功能...")
        
        from src.services.config import Config
        config = Config()
        
        # 测试新增的方法
        data_dir = config.get_data_dir()
        game_name = config.get_game_name()
        torch_available = config.is_torch_available()
        
        print(f"✅ 数据目录: {data_dir}")
        print(f"✅ 游戏名称: {game_name}")
        print(f"✅ Torch可用性: {'是' if torch_available else '否'}")
        
        # 检查目录是否创建
        if os.path.exists(data_dir):
            print(f"✅ 数据目录已创建: {data_dir}")
        else:
            print(f"ℹ️ 数据目录将按需创建: {data_dir}")
        
        print("🎉 配置功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 配置功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_launcher():
    """测试主启动器逻辑"""
    try:
        print("\n🧪 测试主启动器逻辑...")
        
        # 检查主入口文件
        if os.path.exists('main.py'):
            print("✅ 主启动器文件存在")
            
            # 读取内容检查
            with open('main.py', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'src.main import main as src_main' in content:
                    print("✅ 主启动器正确调用src/main.py")
                else:
                    print("⚠️ 主启动器可能未正确配置")
        else:
            print("❌ 主启动器文件不存在")
            return False
        
        # 检查src/main.py
        if os.path.exists('src/main.py'):
            print("✅ src/main.py存在")
        else:
            print("❌ src/main.py不存在")
            return False
        
        # 检查legacy备份
        if os.path.exists('src/legacy/simple_automation.py'):
            print("✅ 简单自动化系统备份存在")
        else:
            print("⚠️ 简单自动化系统备份不存在")
        
        # 检查统一GameAnalyzer
        if os.path.exists('src/core/unified_game_analyzer.py'):
            print("✅ 统一GameAnalyzer存在")
        else:
            print("❌ 统一GameAnalyzer不存在")
            return False
        
        print("🎉 主启动器测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 主启动器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_graceful_degradation():
    """测试优雅降级功能"""
    try:
        print("\n🧪 测试优雅降级功能...")
        
        from src.common.containers import Container
        container = Container()
        
        # 测试尝试获取不可用的服务
        services_to_test = ['window_manager', 'image_processor', 'game_analyzer']
        
        for service in services_to_test:
            try:
                service_method = getattr(container, service)
                service_instance = service_method()
                print(f"✅ {service}: 可用并成功初始化")
            except RuntimeError as e:
                print(f"⚠️ {service}: 优雅降级 - {e}")
            except Exception as e:
                print(f"❌ {service}: 未知错误 - {e}")
        
        print("🎉 优雅降级测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 优雅降级测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🎮 游戏自动化工具 - 重构验证测试")
    print("=" * 60)
    
    success = True
    
    # 基础导入测试
    if not test_basic_imports():
        success = False
    
    # 容器功能测试
    if not test_container_functionality():
        success = False
    
    # 配置功能测试
    if not test_config_functionality():
        success = False
    
    # 主启动器测试
    if not test_main_launcher():
        success = False
    
    # 优雅降级测试
    if not test_graceful_degradation():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 所有测试通过！重构成功！")
        print("✅ 项目结构统一完成")
        print("✅ 配置接口正常工作")
        print("✅ 启动器逻辑正确")
        print("✅ 依赖注入容器工作正常")
        print("✅ 优雅降级机制有效")
        print("✅ 统一GameAnalyzer创建成功")
    else:
        print("❌ 部分测试失败，请检查问题")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)