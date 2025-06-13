#!/usr/bin/env python3
"""
目录重构验证测试
验证重构后的目录结构和功能完整性
"""

import os
import sys
import importlib.util
from pathlib import Path

def test_directory_structure():
    """测试目录结构"""
    print("🔍 测试目录结构...")
    
    expected_dirs = [
        'src/core',
        'src/core/analyzers',
        'src/core/engines', 
        'src/core/executors',
        'src/core/collectors',
        'src/core/models',
        'src/core/automation',
        'src/ui',
        'src/ui/windows',
        'src/ui/widgets',
        'src/ui/panels',
        'src/ui/components',
        'src/ui/managers',
        'src/ui/viewmodels',
        'src/ui/styles',
        'src/ui/editors',
        'src/utils',
        'src/utils/performance',
        'src/utils/ocr',
        'src/utils/macro',
        'src/utils/recorders',
        'src/services',
        'src/common',
        'src/legacy',
        'src/resources',
        'src/tests'
    ]
    
    missing_dirs = []
    for directory in expected_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
    
    if missing_dirs:
        print(f"❌ 缺少目录: {missing_dirs}")
        return False
    
    print("✅ 目录结构测试通过")
    return True

def test_file_migrations():
    """测试文件迁移"""
    print("🔍 测试文件迁移...")
    
    expected_files = [
        # Core files
        'src/core/engines/decision_engine.py',
        'src/core/executors/action_executor.py',
        'src/core/collectors/screen_collector.py',
        'src/core/analyzers/image_recognition.py',
        'src/core/executors/input_controller.py',
        'src/core/models/state_history_model.py',
        'src/core/automation/game_base.py',
        
        # UI files
        'src/ui/viewmodels/game_automation_model.py',
        'src/ui/viewmodels/main_view_model.py',
        'src/ui/editors/config_editor.py',
        'src/ui/editors/script_editor.py',
        'src/ui/styles/styles.py',
        
        # Utils files
        'src/utils/recorders/operation_recorder.py',
        
        # Legacy backup
        'src/legacy/simple_config_manager.py'
    ]
    
    missing_files = []
    for file_path in expected_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 缺少文件: {missing_files}")
        return False
    
    print("✅ 文件迁移测试通过")
    return True

def test_old_directories_removed():
    """测试旧目录是否已删除"""
    print("🔍 测试旧目录清理...")
    
    old_dirs = [
        'src/engine',
        'src/executor',
        'src/collector',
        'src/models',
        'src/games',
        'src/gui',
        'src/views',
        'src/viewmodels',
        'src/editor',
        'src/performance',
        'src/onnxocr',
        'src/macro'
    ]
    
    remaining_dirs = []
    for directory in old_dirs:
        if os.path.exists(directory):
            remaining_dirs.append(directory)
    
    if remaining_dirs:
        print(f"❌ 仍存在旧目录: {remaining_dirs}")
        return False
    
    print("✅ 旧目录清理测试通过")
    return True

def test_imports():
    """测试导入功能"""
    print("🔍 测试关键文件导入...")
    
    # 修复导入路径问题：添加src目录到路径并使用相对导入
    src_dir = os.path.abspath('src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    test_imports = [
        ('services.config', 'Config'),
        ('common.container', 'DIContainer'),
        ('core.unified_game_analyzer', 'UnifiedGameAnalyzer'),
    ]
    
    failed_imports = []
    
    for module_path, class_name in test_imports:
        try:            
            module = importlib.import_module(module_path)
            if hasattr(module, class_name):
                print(f"  ✅ 成功导入 {module_path}.{class_name}")
            else:
                print(f"  ❌ {module_path} 中找不到 {class_name}")
                failed_imports.append(f"{module_path}.{class_name}")
        except Exception as e:
            print(f"  ❌ 导入失败 {module_path}: {str(e)}")
            failed_imports.append(f"{module_path}: {str(e)}")
    
    if failed_imports:
        print(f"❌ 导入测试失败: {failed_imports}")
        return False
    
    print("✅ 导入测试通过")
    return True

def test_init_files():
    """测试__init__.py文件"""
    print("🔍 测试__init__.py文件...")
    
    required_init_files = [
        'src/core/__init__.py',
        'src/core/analyzers/__init__.py',
        'src/core/engines/__init__.py',
        'src/core/executors/__init__.py',
        'src/core/collectors/__init__.py',
        'src/core/models/__init__.py',
        'src/core/automation/__init__.py',
        'src/ui/__init__.py',
        'src/ui/windows/__init__.py',
        'src/ui/widgets/__init__.py',
        'src/ui/panels/__init__.py',
        'src/ui/components/__init__.py',
        'src/ui/managers/__init__.py',
        'src/ui/viewmodels/__init__.py',
        'src/ui/styles/__init__.py',
        'src/ui/editors/__init__.py',
        'src/utils/__init__.py',
        'src/utils/performance/__init__.py',
        'src/utils/ocr/__init__.py',
        'src/utils/macro/__init__.py',
        'src/utils/recorders/__init__.py'
    ]
    
    missing_init_files = []
    for init_file in required_init_files:
        if not os.path.exists(init_file):
            missing_init_files.append(init_file)
    
    if missing_init_files:
        print(f"❌ 缺少__init__.py文件: {missing_init_files}")
        return False
    
    print("✅ __init__.py文件测试通过")
    return True

def test_structure_simplification():
    """测试结构简化效果"""
    print("🔍 测试结构简化效果...")
    
    # 统计主目录数量
    main_dirs = [d for d in os.listdir('src') if os.path.isdir(f'src/{d}') and not d.startswith('.') and d != '__pycache__']
    
    expected_main_dirs = [
        'core', 'services', 'ui', 'utils', 
        'common', 'legacy', 'resources', 'tests', 
        'logs', 'zzz'  # logs和zzz是已存在的，暂时保留
    ]
    
    print(f"  主目录数量: {len(main_dirs)}")
    print(f"  主目录: {sorted(main_dirs)}")
    
    if len(main_dirs) <= 10:  # 期望减少到10个以内
        print("✅ 目录数量简化成功")
        return True
    else:
        print(f"❌ 目录数量仍然过多: {len(main_dirs)} > 10")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始目录重构验证测试...")
    print("=" * 50)
    
    tests = [
        test_directory_structure,
        test_file_migrations,
        test_old_directories_removed,
        test_init_files,
        test_structure_simplification,
        test_imports,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试异常: {test.__name__}: {e}")
            failed += 1
        print("-" * 30)
    
    print("📊 测试结果总结:")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📈 成功率: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 所有测试通过！目录重构成功！")
        print("✅ 目录结构清晰简洁")
        print("✅ 文件迁移完整")
        print("✅ 旧目录清理干净")
        print("✅ 导入功能正常")
        return True
    else:
        print(f"\n⚠️  有 {failed} 项测试失败，需要进一步修复")
        return False

if __name__ == "__main__":
    # 确保在项目根目录运行
    if not os.path.exists('src/main.py'):
        print("❌ 请在项目根目录运行此测试")
        sys.exit(1)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)