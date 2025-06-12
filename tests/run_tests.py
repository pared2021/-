"""测试运行脚本"""
import unittest
import sys
import os
import argparse

# 获取当前脚本所在的目录路径
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
PROJECT_ROOT = os.path.abspath(os.path.join(TESTS_DIR, '..'))

# 将项目根目录添加到系统路径
sys.path.append(PROJECT_ROOT)

def ensure_directories_exist():
    """确保必要的目录结构存在"""
    directories = [
        os.path.join(PROJECT_ROOT, 'templates'),
        os.path.join(PROJECT_ROOT, 'logs'),
        os.path.join(PROJECT_ROOT, 'models'),
        os.path.join(PROJECT_ROOT, 'data'),
        os.path.join(PROJECT_ROOT, 'screenshots')
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            print(f"确保目录存在: {os.path.basename(directory)}")
            os.makedirs(directory, exist_ok=True)

def run_tests(test_type="all"):
    """
    运行指定类型的测试
    
    Args:
        test_type: 要运行的测试类型，可选值为 "all"、"unit"、"integration"、"functional"、"performance"
        
    Returns:
        bool: 测试是否全部通过
    """
    # 确保必要的目录存在
    ensure_directories_exist()
    
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    if test_type == "all" or test_type == "unit":
        unit_tests_path = os.path.join(TESTS_DIR, "unit")
        try:
            # 仅搜索services目录下、不包含test_logger.py的测试
            services_path = os.path.join(unit_tests_path, "services")
            for file in os.listdir(services_path):
                if file.startswith("test_") and file.endswith(".py") and file != "test_logger.py":
                    file_path = os.path.join(services_path, file)
                    module_name = f"unit.services.{file[:-3]}"  # 去掉.py扩展名
                    tests = test_loader.loadTestsFromName(module_name)
                    test_suite.addTests(tests)
        except Exception as e:
            print(f"加载单元测试失败: {e}")
        
    if test_type == "all" or test_type == "integration":
        integration_tests_path = os.path.join(TESTS_DIR, "integration")
        try:
            integration_tests = test_loader.discover(integration_tests_path, pattern="test_*.py", top_level_dir=TESTS_DIR)
            test_suite.addTests(integration_tests)
        except Exception as e:
            print(f"加载集成测试失败: {e}")
        
    if test_type == "all" or test_type == "functional":
        functional_tests_path = os.path.join(TESTS_DIR, "functional")
        try:
            # 在functional测试中，排除性能测试
            if test_type != "performance":
                functional_tests = test_loader.discover(functional_tests_path, pattern="test_functional.py", top_level_dir=TESTS_DIR)
                test_suite.addTests(functional_tests)
        except Exception as e:
            print(f"加载功能测试失败: {e}")
        
    if test_type == "all" or test_type == "performance":
        performance_tests_path = os.path.join(TESTS_DIR, "functional")
        try:
            performance_tests = test_loader.discover(performance_tests_path, pattern="test_performance.py", top_level_dir=TESTS_DIR)
            test_suite.addTests(performance_tests)
        except Exception as e:
            print(f"加载性能测试失败: {e}")
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_results = test_runner.run(test_suite)
    
    if test_results.wasSuccessful():
        print("全部测试通过！")
        return True
    else:
        print(f"测试失败: {len(test_results.failures)} 个失败, {len(test_results.errors)} 个错误")
        return False

if __name__ == "__main__":
    # 创建参数解析器
    parser = argparse.ArgumentParser(description="运行游戏自动操作工具的测试")
    parser.add_argument("--type", choices=["all", "unit", "integration", "functional", "performance"], 
                        default="all", help="要运行的测试类型")
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 运行测试
    print(f"运行 {args.type} 测试...")
    success = run_tests(args.type)
    
    # 设置退出代码
    sys.exit(0 if success else 1)