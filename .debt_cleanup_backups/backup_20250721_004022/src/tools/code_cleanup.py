"""
代码清理工具
帮助标识和重构冗余代码
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple


class CodeCleanupTool:
    """代码清理工具"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.redundant_patterns = {
            'duplicate_imports': [],
            'unused_imports': [],
            'duplicate_classes': [],
            'duplicate_functions': [],
            'dead_code': []
        }
    
    def analyze_redundant_services(self) -> Dict[str, List[str]]:
        """分析冗余服务"""
        redundant_services = {
            'game_analyzers': [
                'src/services/game_analyzer.py',
                'src/services/game_state_analyzer.py', 
                'src/core/unified_game_analyzer.py',
                'src/legacy/original_game_analyzer_services.py'
            ],
            'window_managers': [
                'src/services/window_manager.py',
                'src/legacy/removed/window/window_manager_zzz.py',
                'src/legacy/removed/window/window_manager_subdir.py'
            ],
            'error_handlers': [
                'src/services/error_handler.py',
                'src/legacy/removed/error/error_handler_core.py'
            ],
            'config_managers': [
                'src/services/config.py',
                'src/legacy/removed/config/config_manager.py',
                'src/legacy/removed/config/config_manager_zzz.py'
            ]
        }
        
        # 验证文件是否存在
        existing_services = {}
        for category, files in redundant_services.items():
            existing_files = []
            for file_path in files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    existing_files.append(file_path)
            if existing_files:
                existing_services[category] = existing_files
        
        return existing_services
    
    def find_duplicate_ui_components(self) -> Dict[str, List[str]]:
        """查找重复的UI组件"""
        ui_patterns = {
            'main_windows': [
                'src/main_window.py',
                'src/gui/main_window.py'
            ],
            'control_panels': [
                'src/gui/widgets/control_panel.py',
                'src/views/panels/control_panel.py'
            ],
            'ui_directories': [
                'src/gui/',
                'src/views/', 
                'src/ui/'
            ]
        }
        
        existing_components = {}
        for category, paths in ui_patterns.items():
            existing_paths = []
            for path in paths:
                full_path = self.project_root / path
                if full_path.exists():
                    existing_paths.append(path)
            if existing_paths:
                existing_components[category] = existing_paths
        
        return existing_components
    
    def identify_unused_imports(self, file_path: str) -> List[str]:
        """识别未使用的导入"""
        try:
            with open(self.project_root / file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的未使用导入检测
            import_pattern = r'^from\s+(\S+)\s+import\s+(.+)$'
            imports = re.findall(import_pattern, content, re.MULTILINE)
            
            unused_imports = []
            for module, imports_str in imports:
                import_names = [name.strip() for name in imports_str.split(',')]
                for import_name in import_names:
                    # 检查是否在代码中使用
                    if import_name not in content.replace(f'import {import_name}', ''):
                        unused_imports.append(f'from {module} import {import_name}')
            
            return unused_imports
        except Exception as e:
            print(f"分析文件 {file_path} 时出错: {e}")
            return []
    
    def generate_cleanup_report(self) -> str:
        """生成清理报告"""
        report = "# 代码清理报告\n\n"
        
        # 分析冗余服务
        redundant_services = self.analyze_redundant_services()
        if redundant_services:
            report += "## 冗余服务\n\n"
            for category, files in redundant_services.items():
                report += f"### {category}\n"
                for file_path in files:
                    report += f"- {file_path}\n"
                report += "\n"
        
        # 分析重复UI组件
        duplicate_ui = self.find_duplicate_ui_components()
        if duplicate_ui:
            report += "## 重复UI组件\n\n"
            for category, paths in duplicate_ui.items():
                report += f"### {category}\n"
                for path in paths:
                    report += f"- {path}\n"
                report += "\n"
        
        # 清理建议
        report += "## 清理建议\n\n"
        report += "1. **服务整合**: 将冗余的游戏分析器整合到新的GameAnalyzerService中\n"
        report += "2. **UI统一**: 统一UI组件到src/gui/目录下\n"
        report += "3. **配置整合**: 使用统一的配置系统\n"
        report += "4. **遗留代码**: 将不再使用的代码移动到src/legacy/removed/目录\n"
        report += "5. **依赖清理**: 移除未使用的导入和依赖\n\n"
        
        return report
    
    def suggest_refactoring_actions(self) -> List[Dict[str, str]]:
        """建议重构操作"""
        actions = [
            {
                'action': 'consolidate_game_analyzers',
                'description': '整合游戏分析器到统一服务',
                'files': ['src/services/game_analyzer.py', 'src/services/game_state_analyzer.py'],
                'target': 'src/infrastructure/services/game_analyzer_service.py'
            },
            {
                'action': 'unify_ui_structure',
                'description': '统一UI结构',
                'files': ['src/views/', 'src/ui/'],
                'target': 'src/gui/'
            },
            {
                'action': 'remove_duplicate_main_windows',
                'description': '移除重复的主窗口',
                'files': ['src/main_window.py'],
                'target': 'src/gui/main_window.py'
            },
            {
                'action': 'consolidate_config_systems',
                'description': '整合配置系统',
                'files': ['src/legacy/removed/config/'],
                'target': 'src/services/config.py'
            }
        ]
        
        return actions


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    cleanup_tool = CodeCleanupTool(str(project_root))
    
    # 生成清理报告
    report = cleanup_tool.generate_cleanup_report()
    print(report)
    
    # 建议重构操作
    actions = cleanup_tool.suggest_refactoring_actions()
    print("## 建议的重构操作\n")
    for action in actions:
        print(f"**{action['action']}**: {action['description']}")
        print(f"  文件: {action['files']}")
        print(f"  目标: {action['target']}\n")


if __name__ == "__main__":
    main() 