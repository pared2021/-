#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
债务清理配置

定义清理规则、阈值和参数配置。
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AnalysisConfig:
    """分析配置"""
    # 文件过滤
    include_patterns: List[str]
    exclude_patterns: List[str]
    max_file_size: int  # KB
    
    # 复杂度阈值
    max_cyclomatic_complexity: int
    max_method_length: int
    max_class_length: int
    max_file_length: int
    
    # 重复代码检测
    min_duplicate_lines: int
    duplicate_similarity_threshold: float
    
    # 导入分析
    max_import_depth: int
    circular_import_detection: bool


@dataclass
class CleanupConfig:
    """清理配置"""
    # 备份设置
    create_backup: bool
    backup_directory: str
    
    # 安全设置
    dry_run_first: bool
    require_tests: bool
    max_changes_per_file: int
    
    # 重构设置
    auto_format_code: bool
    update_imports: bool
    remove_unused_imports: bool
    
    # 并发设置
    max_workers: int
    batch_size: int


@dataclass
class QualityThresholds:
    """质量阈值"""
    min_test_coverage: float
    max_technical_debt_ratio: float
    min_maintainability_index: float
    max_duplicate_code_ratio: float
    max_complexity_per_method: int
    max_lines_per_method: int
    max_methods_per_class: int
    max_classes_per_file: int


class DebtCleanupConfig:
    """债务清理配置管理器"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file
        self._load_default_config()
        
        if config_file and Path(config_file).exists():
            self._load_config_file(config_file)
    
    def _load_default_config(self) -> None:
        """加载默认配置"""
        
        # 分析配置
        self.analysis = AnalysisConfig(
            include_patterns=[
                "*.py",
                "src/**/*.py",
                "tests/**/*.py"
            ],
            exclude_patterns=[
                "__pycache__/**",
                ".venv/**",
                "venv/**",
                "env/**",
                "build/**",
                "dist/**",
                "*.egg-info/**",
                "migrations/**",
                "**/migrations/**"
            ],
            max_file_size=1024,  # 1MB
            max_cyclomatic_complexity=10,
            max_method_length=50,
            max_class_length=500,
            max_file_length=1000,
            min_duplicate_lines=6,
            duplicate_similarity_threshold=0.8,
            max_import_depth=5,
            circular_import_detection=True
        )
        
        # 清理配置
        self.cleanup = CleanupConfig(
            create_backup=True,
            backup_directory=".debt_cleanup_backup",
            dry_run_first=True,
            require_tests=True,
            max_changes_per_file=100,
            auto_format_code=True,
            update_imports=True,
            remove_unused_imports=True,
            max_workers=4,
            batch_size=10
        )
        
        # 质量阈值
        self.quality_thresholds = QualityThresholds(
            min_test_coverage=80.0,
            max_technical_debt_ratio=20.0,
            min_maintainability_index=60.0,
            max_duplicate_code_ratio=10.0,
            max_complexity_per_method=10,
            max_lines_per_method=50,
            max_methods_per_class=20,
            max_classes_per_file=3
        )
        
        # 债务类型权重
        self.debt_weights = {
            "hardcoded_imports": 0.9,      # 硬编码导入 - 高权重
            "service_locator": 0.8,        # 服务定位器反模式 - 高权重
            "synchronous_blocking": 0.8,   # 同步阻塞 - 高权重
            "config_inconsistency": 0.6,   # 配置不一致 - 中权重
            "error_handling": 0.6,         # 错误处理 - 中权重
            "missing_interfaces": 0.5,     # 缺乏接口 - 中权重
            "code_duplication": 0.4,       # 代码重复 - 低权重
            "missing_documentation": 0.3   # 缺乏文档 - 低权重
        }
        
        # 清理任务优先级
        self.task_priorities = {
            "remove_hardcoded_imports": "high",
            "refactor_service_locator": "high",
            "implement_async_patterns": "high",
            "unify_config_system": "medium",
            "standardize_error_handling": "medium",
            "extract_interfaces": "medium",
            "eliminate_code_duplication": "low",
            "add_documentation": "low",
            "improve_test_coverage": "medium"
        }
        
        # 重构模式配置
        self.refactoring_patterns = {
            "extract_method": {
                "enabled": True,
                "min_lines": 10,
                "max_complexity": 5
            },
            "extract_class": {
                "enabled": True,
                "min_methods": 5,
                "max_cohesion": 0.3
            },
            "move_method": {
                "enabled": True,
                "min_coupling": 0.7
            },
            "introduce_parameter_object": {
                "enabled": True,
                "min_parameters": 4
            },
            "replace_magic_number": {
                "enabled": True,
                "exclude_common": [0, 1, -1, 2, 10, 100, 1000]
            }
        }
        
        # 代码质量规则
        self.quality_rules = {
            "naming_conventions": {
                "class_name_pattern": r"^[A-Z][a-zA-Z0-9]*$",
                "method_name_pattern": r"^[a-z_][a-z0-9_]*$",
                "variable_name_pattern": r"^[a-z_][a-z0-9_]*$",
                "constant_name_pattern": r"^[A-Z_][A-Z0-9_]*$"
            },
            "documentation_requirements": {
                "require_class_docstring": True,
                "require_method_docstring": True,
                "require_module_docstring": True,
                "min_docstring_length": 10
            },
            "import_organization": {
                "group_imports": True,
                "sort_imports": True,
                "separate_third_party": True,
                "max_imports_per_line": 1
            },
            "error_handling": {
                "require_specific_exceptions": True,
                "avoid_bare_except": True,
                "require_exception_logging": True
            }
        }
        
        # 测试要求
        self.test_requirements = {
            "min_coverage_per_file": 70.0,
            "require_unit_tests": True,
            "require_integration_tests": False,
            "test_naming_pattern": r"^test_.*$",
            "mock_external_dependencies": True
        }
        
        # 性能优化配置
        self.performance_config = {
            "enable_caching": True,
            "cache_size_limit": 1000,
            "enable_lazy_loading": True,
            "optimize_imports": True,
            "remove_dead_code": True
        }
        
        # 安全配置
        self.security_config = {
            "scan_for_secrets": True,
            "check_sql_injection": True,
            "validate_input_sanitization": True,
            "require_https": True,
            "check_dependency_vulnerabilities": True
        }
    
    def _load_config_file(self, config_file: str) -> None:
        """从文件加载配置"""
        # 这里可以实现从JSON/YAML文件加载配置的逻辑
        pass
    
    def get_debt_priority(self, debt_type: str) -> str:
        """获取债务类型的优先级"""
        weight = self.debt_weights.get(debt_type, 0.5)
        
        if weight >= 0.7:
            return "high"
        elif weight >= 0.5:
            return "medium"
        else:
            return "low"
    
    def get_task_config(self, task_type: str) -> Dict[str, Any]:
        """获取任务配置"""
        base_config = {
            "priority": self.task_priorities.get(task_type, "medium"),
            "require_backup": self.cleanup.create_backup,
            "dry_run_first": self.cleanup.dry_run_first,
            "auto_format": self.cleanup.auto_format_code
        }
        
        # 特定任务的配置
        task_specific = {
            "remove_hardcoded_imports": {
                "update_imports": True,
                "remove_unused": True,
                "organize_imports": True
            },
            "refactor_service_locator": {
                "extract_interfaces": True,
                "use_dependency_injection": True,
                "create_factories": True
            },
            "implement_async_patterns": {
                "convert_to_async": True,
                "add_await_keywords": True,
                "update_function_signatures": True
            },
            "eliminate_code_duplication": {
                "extract_common_methods": True,
                "create_utility_classes": True,
                "use_inheritance": False
            }
        }
        
        base_config.update(task_specific.get(task_type, {}))
        return base_config
    
    def is_file_included(self, file_path: str) -> bool:
        """检查文件是否应该被包含在分析中"""
        path = Path(file_path)
        
        # 检查文件大小
        try:
            if path.stat().st_size > self.analysis.max_file_size * 1024:
                return False
        except OSError:
            return False
        
        # 检查包含模式
        included = False
        for pattern in self.analysis.include_patterns:
            if path.match(pattern):
                included = True
                break
        
        if not included:
            return False
        
        # 检查排除模式
        for pattern in self.analysis.exclude_patterns:
            if path.match(pattern):
                return False
        
        return True
    
    def get_quality_gate_config(self) -> Dict[str, Any]:
        """获取质量门禁配置"""
        return {
            "min_test_coverage": self.quality_thresholds.min_test_coverage,
            "max_complexity": self.analysis.max_cyclomatic_complexity,
            "max_debt_ratio": self.quality_thresholds.max_technical_debt_ratio,
            "min_maintainability": self.quality_thresholds.min_maintainability_index,
            "max_duplicate_ratio": self.quality_thresholds.max_duplicate_code_ratio,
            "require_documentation": self.quality_rules["documentation_requirements"]["require_class_docstring"],
            "security_checks": self.security_config["scan_for_secrets"]
        }
    
    def export_config(self, output_file: str) -> None:
        """导出配置到文件"""
        import json
        
        config_data = {
            "analysis": self.analysis.__dict__,
            "cleanup": self.cleanup.__dict__,
            "quality_thresholds": self.quality_thresholds.__dict__,
            "debt_weights": self.debt_weights,
            "task_priorities": self.task_priorities,
            "refactoring_patterns": self.refactoring_patterns,
            "quality_rules": self.quality_rules,
            "test_requirements": self.test_requirements,
            "performance_config": self.performance_config,
            "security_config": self.security_config
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)


# 全局配置实例
default_config = DebtCleanupConfig()


# 预定义的配置模板
CONFIG_TEMPLATES = {
    "strict": {
        "quality_thresholds": {
            "min_test_coverage": 90.0,
            "max_technical_debt_ratio": 10.0,
            "min_maintainability_index": 80.0,
            "max_duplicate_code_ratio": 5.0
        },
        "analysis": {
            "max_cyclomatic_complexity": 5,
            "max_method_length": 30,
            "max_class_length": 300
        }
    },
    "moderate": {
        "quality_thresholds": {
            "min_test_coverage": 70.0,
            "max_technical_debt_ratio": 25.0,
            "min_maintainability_index": 60.0,
            "max_duplicate_code_ratio": 15.0
        },
        "analysis": {
            "max_cyclomatic_complexity": 10,
            "max_method_length": 50,
            "max_class_length": 500
        }
    },
    "lenient": {
        "quality_thresholds": {
            "min_test_coverage": 50.0,
            "max_technical_debt_ratio": 40.0,
            "min_maintainability_index": 40.0,
            "max_duplicate_code_ratio": 25.0
        },
        "analysis": {
            "max_cyclomatic_complexity": 15,
            "max_method_length": 100,
            "max_class_length": 1000
        }
    }
}


def create_config_from_template(template_name: str) -> DebtCleanupConfig:
    """从模板创建配置"""
    if template_name not in CONFIG_TEMPLATES:
        raise ValueError(f"未知的配置模板: {template_name}")
    
    config = DebtCleanupConfig()
    template = CONFIG_TEMPLATES[template_name]
    
    # 应用模板配置
    for section, values in template.items():
        if hasattr(config, section):
            section_obj = getattr(config, section)
            for key, value in values.items():
                if hasattr(section_obj, key):
                    setattr(section_obj, key, value)
    
    return config


if __name__ == "__main__":
    # 示例用法
    config = DebtCleanupConfig()
    
    # 导出默认配置
    config.export_config("default_config.json")
    
    # 创建严格配置
    strict_config = create_config_from_template("strict")
    strict_config.export_config("strict_config.json")
    
    print("配置文件已生成")