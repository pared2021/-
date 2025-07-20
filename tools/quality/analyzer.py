#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码质量分析工具
自动化识别技术债务、架构问题和代码质量指标
"""

import os
import ast
import re
import json
import time
from typing import Dict, List, Tuple, Set, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, Counter
import subprocess
import sys

# ============================================================================
# 数据结构定义
# ============================================================================

@dataclass
class CodeIssue:
    """代码问题数据类"""
    file_path: str
    line_number: int
    issue_type: str
    severity: str  # 'critical', 'major', 'minor'
    description: str
    suggestion: str
    code_snippet: str

@dataclass
class DependencyInfo:
    """依赖信息"""
    from_module: str
    to_module: str
    import_type: str  # 'absolute', 'relative', 'hardcoded'
    line_number: int
    is_circular: bool = False

@dataclass
class ComplexityMetrics:
    """复杂度指标"""
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    function_count: int
    class_count: int
    nesting_depth: int

@dataclass
class QualityReport:
    """质量报告"""
    timestamp: str
    total_files: int
    total_lines: int
    issues: List[CodeIssue]
    dependencies: List[DependencyInfo]
    complexity_metrics: Dict[str, ComplexityMetrics]
    technical_debt_score: float
    maintainability_index: float
    test_coverage: float
    summary: Dict[str, Any]

# ============================================================================
# 代码分析器基类
# ============================================================================

class BaseAnalyzer:
    """分析器基类"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues: List[CodeIssue] = []
        self.dependencies: List[DependencyInfo] = []
    
    def analyze(self) -> List[CodeIssue]:
        """执行分析"""
        raise NotImplementedError
    
    def _get_python_files(self) -> List[Path]:
        """获取所有Python文件"""
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # 跳过虚拟环境和缓存目录
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.pytest_cache', 'venv', 'env', '.venv'}]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def _read_file_safe(self, file_path: Path) -> Optional[str]:
        """安全读取文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (UnicodeDecodeError, FileNotFoundError):
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    return f.read()
            except Exception:
                return None
    
    def _create_issue(self, file_path: str, line_number: int, issue_type: str, 
                     severity: str, description: str, suggestion: str, 
                     code_snippet: str = "") -> CodeIssue:
        """创建代码问题"""
        return CodeIssue(
            file_path=file_path,
            line_number=line_number,
            issue_type=issue_type,
            severity=severity,
            description=description,
            suggestion=suggestion,
            code_snippet=code_snippet
        )

# ============================================================================
# 硬编码导入分析器
# ============================================================================

class HardcodedImportAnalyzer(BaseAnalyzer):
    """硬编码导入分析器"""
    
    def __init__(self, project_root: str):
        super().__init__(project_root)
        self.hardcoded_patterns = [
            r'from\s+src\.',
            r'import\s+src\.',
            r'sys\.path\.append',
            r'os\.path\.dirname.*__file__'
        ]
    
    def analyze(self) -> List[CodeIssue]:
        """分析硬编码导入"""
        issues = []
        
        for file_path in self._get_python_files():
            content = self._read_file_safe(file_path)
            if not content:
                continue
            
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                for pattern in self.hardcoded_patterns:
                    if re.search(pattern, line):
                        issues.append(self._create_issue(
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=line_num,
                            issue_type="hardcoded_import",
                            severity="major",
                            description=f"硬编码导入: {line.strip()}",
                            suggestion="使用相对导入或配置化的模块路径",
                            code_snippet=line.strip()
                        ))
        
        return issues

# ============================================================================
# 依赖分析器
# ============================================================================

class DependencyAnalyzer(BaseAnalyzer):
    """依赖关系分析器"""
    
    def analyze(self) -> Tuple[List[DependencyInfo], List[CodeIssue]]:
        """分析依赖关系"""
        dependencies = []
        issues = []
        module_imports = defaultdict(set)
        
        for file_path in self._get_python_files():
            content = self._read_file_safe(file_path)
            if not content:
                continue
            
            try:
                tree = ast.parse(content)
                module_name = self._get_module_name(file_path)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        dep_info = self._extract_dependency_info(node, file_path, module_name)
                        if dep_info:
                            dependencies.append(dep_info)
                            module_imports[module_name].add(dep_info.to_module)
                            
            except SyntaxError as e:
                issues.append(self._create_issue(
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=e.lineno or 0,
                    issue_type="syntax_error",
                    severity="critical",
                    description=f"语法错误: {e.msg}",
                    suggestion="修复语法错误"
                ))
        
        # 检测循环依赖
        circular_deps = self._detect_circular_dependencies(module_imports)
        for dep in dependencies:
            if (dep.from_module, dep.to_module) in circular_deps:
                dep.is_circular = True
                issues.append(self._create_issue(
                    file_path=dep.from_module,
                    line_number=dep.line_number,
                    issue_type="circular_dependency",
                    severity="major",
                    description=f"循环依赖: {dep.from_module} -> {dep.to_module}",
                    suggestion="重构代码以消除循环依赖"
                ))
        
        return dependencies, issues
    
    def _get_module_name(self, file_path: Path) -> str:
        """获取模块名"""
        relative_path = file_path.relative_to(self.project_root)
        return str(relative_path).replace(os.sep, '.').replace('.py', '')
    
    def _extract_dependency_info(self, node: ast.AST, file_path: Path, module_name: str) -> Optional[DependencyInfo]:
        """提取依赖信息"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                return DependencyInfo(
                    from_module=module_name,
                    to_module=alias.name,
                    import_type="absolute",
                    line_number=node.lineno
                )
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                import_type = "relative" if node.level > 0 else "absolute"
                if node.module.startswith('src.'):
                    import_type = "hardcoded"
                
                return DependencyInfo(
                    from_module=module_name,
                    to_module=node.module,
                    import_type=import_type,
                    line_number=node.lineno
                )
        
        return None
    
    def _detect_circular_dependencies(self, module_imports: Dict[str, Set[str]]) -> Set[Tuple[str, str]]:
        """检测循环依赖"""
        circular = set()
        
        def has_path(start: str, end: str, visited: Set[str]) -> bool:
            if start == end:
                return True
            if start in visited:
                return False
            
            visited.add(start)
            for neighbor in module_imports.get(start, set()):
                if has_path(neighbor, end, visited.copy()):
                    return True
            return False
        
        for module in module_imports:
            for imported in module_imports[module]:
                if has_path(imported, module, set()):
                    circular.add((module, imported))
        
        return circular

# ============================================================================
# 复杂度分析器
# ============================================================================

class ComplexityAnalyzer(BaseAnalyzer):
    """复杂度分析器"""
    
    def analyze(self) -> Tuple[Dict[str, ComplexityMetrics], List[CodeIssue]]:
        """分析代码复杂度"""
        metrics = {}
        issues = []
        
        for file_path in self._get_python_files():
            content = self._read_file_safe(file_path)
            if not content:
                continue
            
            try:
                tree = ast.parse(content)
                file_metrics = self._calculate_file_metrics(tree, content)
                relative_path = str(file_path.relative_to(self.project_root))
                metrics[relative_path] = file_metrics
                
                # 检查复杂度阈值
                if file_metrics.cyclomatic_complexity > 10:
                    issues.append(self._create_issue(
                        file_path=relative_path,
                        line_number=1,
                        issue_type="high_complexity",
                        severity="major",
                        description=f"圈复杂度过高: {file_metrics.cyclomatic_complexity}",
                        suggestion="考虑拆分函数或类以降低复杂度"
                    ))
                
                if file_metrics.nesting_depth > 4:
                    issues.append(self._create_issue(
                        file_path=relative_path,
                        line_number=1,
                        issue_type="deep_nesting",
                        severity="minor",
                        description=f"嵌套层次过深: {file_metrics.nesting_depth}",
                        suggestion="使用早期返回或提取函数来减少嵌套"
                    ))
                
            except SyntaxError:
                continue
        
        return metrics, issues
    
    def _calculate_file_metrics(self, tree: ast.AST, content: str) -> ComplexityMetrics:
        """计算文件指标"""
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        
        function_count = 0
        class_count = 0
        max_nesting = 0
        total_complexity = 1  # 基础复杂度
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_count += 1
                total_complexity += self._calculate_cyclomatic_complexity(node)
            elif isinstance(node, ast.ClassDef):
                class_count += 1
            
            # 计算嵌套深度
            nesting = self._calculate_nesting_depth(node)
            max_nesting = max(max_nesting, nesting)
        
        return ComplexityMetrics(
            cyclomatic_complexity=total_complexity,
            cognitive_complexity=total_complexity,  # 简化实现
            lines_of_code=len(non_empty_lines),
            function_count=function_count,
            class_count=class_count,
            nesting_depth=max_nesting
        )
    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """计算圈复杂度"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _calculate_nesting_depth(self, node: ast.AST) -> int:
        """计算嵌套深度"""
        if not hasattr(node, 'body'):
            return 0
        
        max_depth = 0
        for child in getattr(node, 'body', []):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.Try)):
                depth = 1 + self._calculate_nesting_depth(child)
                max_depth = max(max_depth, depth)
        
        return max_depth

# ============================================================================
# 代码重复分析器
# ============================================================================

class DuplicationAnalyzer(BaseAnalyzer):
    """代码重复分析器"""
    
    def __init__(self, project_root: str, min_lines: int = 5):
        super().__init__(project_root)
        self.min_lines = min_lines
    
    def analyze(self) -> List[CodeIssue]:
        """分析代码重复"""
        issues = []
        code_blocks = self._extract_code_blocks()
        duplicates = self._find_duplicates(code_blocks)
        
        for duplicate_group in duplicates:
            if len(duplicate_group) > 1:
                for block in duplicate_group[1:]:  # 跳过第一个，其他都是重复
                    issues.append(self._create_issue(
                        file_path=block['file'],
                        line_number=block['start_line'],
                        issue_type="code_duplication",
                        severity="minor",
                        description=f"代码重复，共{len(duplicate_group)}处",
                        suggestion="提取公共函数或类来消除重复",
                        code_snippet=block['content'][:100] + "..."
                    ))
        
        return issues
    
    def _extract_code_blocks(self) -> List[Dict[str, Any]]:
        """提取代码块"""
        blocks = []
        
        for file_path in self._get_python_files():
            content = self._read_file_safe(file_path)
            if not content:
                continue
            
            lines = content.split('\n')
            for i in range(len(lines) - self.min_lines + 1):
                block_lines = lines[i:i + self.min_lines]
                # 过滤空行和注释
                meaningful_lines = [line.strip() for line in block_lines 
                                  if line.strip() and not line.strip().startswith('#')]
                
                if len(meaningful_lines) >= self.min_lines:
                    blocks.append({
                        'file': str(file_path.relative_to(self.project_root)),
                        'start_line': i + 1,
                        'content': '\n'.join(meaningful_lines),
                        'hash': hash('\n'.join(meaningful_lines))
                    })
        
        return blocks
    
    def _find_duplicates(self, blocks: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """查找重复代码块"""
        hash_groups = defaultdict(list)
        
        for block in blocks:
            hash_groups[block['hash']].append(block)
        
        return [group for group in hash_groups.values() if len(group) > 1]

# ============================================================================
# 测试覆盖率分析器
# ============================================================================

class TestCoverageAnalyzer:
    """测试覆盖率分析器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
    
    def analyze(self) -> float:
        """分析测试覆盖率"""
        try:
            # 尝试运行coverage
            result = subprocess.run(
                [sys.executable, '-m', 'coverage', 'run', '-m', 'pytest'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                # 获取覆盖率报告
                coverage_result = subprocess.run(
                    [sys.executable, '-m', 'coverage', 'report', '--format=json'],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                
                if coverage_result.returncode == 0:
                    coverage_data = json.loads(coverage_result.stdout)
                    return coverage_data.get('totals', {}).get('percent_covered', 0.0)
            
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass
        
        # 如果无法获取实际覆盖率，估算测试文件比例
        return self._estimate_test_coverage()
    
    def _estimate_test_coverage(self) -> float:
        """估算测试覆盖率"""
        total_files = 0
        test_files = 0
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.pytest_cache'}]
            
            for file in files:
                if file.endswith('.py'):
                    total_files += 1
                    if 'test' in file.lower() or 'test' in root.lower():
                        test_files += 1
        
        return (test_files / total_files * 100) if total_files > 0 else 0.0

# ============================================================================
# 主分析器
# ============================================================================

class CodeQualityAnalyzer:
    """代码质量分析器主类"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.analyzers = {
            'hardcoded_imports': HardcodedImportAnalyzer(project_root),
            'dependencies': DependencyAnalyzer(project_root),
            'complexity': ComplexityAnalyzer(project_root),
            'duplication': DuplicationAnalyzer(project_root),
            'test_coverage': TestCoverageAnalyzer(project_root)
        }
    
    def analyze(self) -> QualityReport:
        """执行完整的代码质量分析"""
        print("🔍 开始代码质量分析...")
        start_time = time.time()
        
        all_issues = []
        all_dependencies = []
        complexity_metrics = {}
        
        # 1. 硬编码导入分析
        print("📋 分析硬编码导入...")
        hardcoded_issues = self.analyzers['hardcoded_imports'].analyze()
        all_issues.extend(hardcoded_issues)
        
        # 2. 依赖关系分析
        print("🔗 分析依赖关系...")
        dependencies, dep_issues = self.analyzers['dependencies'].analyze()
        all_dependencies.extend(dependencies)
        all_issues.extend(dep_issues)
        
        # 3. 复杂度分析
        print("📊 分析代码复杂度...")
        complexity_metrics, complexity_issues = self.analyzers['complexity'].analyze()
        all_issues.extend(complexity_issues)
        
        # 4. 代码重复分析
        print("🔄 分析代码重复...")
        duplication_issues = self.analyzers['duplication'].analyze()
        all_issues.extend(duplication_issues)
        
        # 5. 测试覆盖率分析
        print("🧪 分析测试覆盖率...")
        test_coverage = self.analyzers['test_coverage'].analyze()
        
        # 计算质量指标
        technical_debt_score = self._calculate_technical_debt_score(all_issues)
        maintainability_index = self._calculate_maintainability_index(
            complexity_metrics, len(all_issues), test_coverage
        )
        
        # 统计信息
        total_files = len(list(self.project_root.rglob('*.py')))
        total_lines = sum(metrics.lines_of_code for metrics in complexity_metrics.values())
        
        analysis_time = time.time() - start_time
        print(f"✅ 分析完成，耗时 {analysis_time:.2f} 秒")
        
        return QualityReport(
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
            total_files=total_files,
            total_lines=total_lines,
            issues=all_issues,
            dependencies=all_dependencies,
            complexity_metrics=complexity_metrics,
            technical_debt_score=technical_debt_score,
            maintainability_index=maintainability_index,
            test_coverage=test_coverage,
            summary=self._generate_summary(all_issues, dependencies, complexity_metrics)
        )
    
    def _calculate_technical_debt_score(self, issues: List[CodeIssue]) -> float:
        """计算技术债务评分"""
        severity_weights = {'critical': 10, 'major': 5, 'minor': 1}
        total_weight = sum(severity_weights.get(issue.severity, 1) for issue in issues)
        
        # 归一化到0-100分，分数越低表示债务越多
        max_possible_score = 100
        debt_penalty = min(total_weight, max_possible_score)
        
        return max(0, max_possible_score - debt_penalty)
    
    def _calculate_maintainability_index(self, complexity_metrics: Dict[str, ComplexityMetrics], 
                                       issue_count: int, test_coverage: float) -> float:
        """计算可维护性指数"""
        if not complexity_metrics:
            return 0.0
        
        # 平均复杂度
        avg_complexity = sum(m.cyclomatic_complexity for m in complexity_metrics.values()) / len(complexity_metrics)
        
        # 可维护性指数公式（简化版）
        # MI = 171 - 5.2 * ln(Halstead Volume) - 0.23 * (Cyclomatic Complexity) - 16.2 * ln(Lines of Code)
        # 这里使用简化公式
        complexity_factor = max(0, 100 - avg_complexity * 5)
        issue_factor = max(0, 100 - issue_count)
        coverage_factor = test_coverage
        
        return (complexity_factor + issue_factor + coverage_factor) / 3
    
    def _generate_summary(self, issues: List[CodeIssue], dependencies: List[DependencyInfo], 
                         complexity_metrics: Dict[str, ComplexityMetrics]) -> Dict[str, Any]:
        """生成分析摘要"""
        issue_counts = Counter(issue.issue_type for issue in issues)
        severity_counts = Counter(issue.severity for issue in issues)
        
        circular_deps = sum(1 for dep in dependencies if dep.is_circular)
        hardcoded_imports = sum(1 for dep in dependencies if dep.import_type == 'hardcoded')
        
        return {
            'total_issues': len(issues),
            'issue_types': dict(issue_counts),
            'severity_distribution': dict(severity_counts),
            'circular_dependencies': circular_deps,
            'hardcoded_imports': hardcoded_imports,
            'average_complexity': sum(m.cyclomatic_complexity for m in complexity_metrics.values()) / len(complexity_metrics) if complexity_metrics else 0,
            'total_functions': sum(m.function_count for m in complexity_metrics.values()),
            'total_classes': sum(m.class_count for m in complexity_metrics.values())
        }
    
    def generate_report(self, report: QualityReport, output_file: str = None) -> str:
        """生成分析报告"""
        report_content = self._format_report(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"📄 报告已保存到: {output_file}")
        
        return report_content
    
    def _format_report(self, report: QualityReport) -> str:
        """格式化报告"""
        lines = [
            "# 🔍 代码质量分析报告",
            f"\n**分析时间**: {report.timestamp}",
            f"**项目文件数**: {report.total_files}",
            f"**代码行数**: {report.total_lines:,}",
            f"\n## 📊 质量指标",
            f"\n- **技术债务评分**: {report.technical_debt_score:.1f}/100",
            f"- **可维护性指数**: {report.maintainability_index:.1f}/100",
            f"- **测试覆盖率**: {report.test_coverage:.1f}%",
            f"\n## 🚨 问题统计",
            f"\n- **总问题数**: {len(report.issues)}",
        ]
        
        # 按严重程度统计
        severity_counts = Counter(issue.severity for issue in report.issues)
        for severity, count in severity_counts.items():
            emoji = {'critical': '🔴', 'major': '🟡', 'minor': '🟢'}.get(severity, '⚪')
            lines.append(f"- **{severity.title()}**: {count} {emoji}")
        
        # 问题类型统计
        lines.append("\n## 📋 问题类型分布")
        issue_types = Counter(issue.issue_type for issue in report.issues)
        for issue_type, count in issue_types.most_common():
            lines.append(f"- **{issue_type.replace('_', ' ').title()}**: {count}")
        
        # 复杂度统计
        if report.complexity_metrics:
            lines.append("\n## 📈 复杂度分析")
            avg_complexity = sum(m.cyclomatic_complexity for m in report.complexity_metrics.values()) / len(report.complexity_metrics)
            total_functions = sum(m.function_count for m in report.complexity_metrics.values())
            total_classes = sum(m.class_count for m in report.complexity_metrics.values())
            
            lines.extend([
                f"- **平均圈复杂度**: {avg_complexity:.1f}",
                f"- **函数总数**: {total_functions}",
                f"- **类总数**: {total_classes}"
            ])
        
        # 依赖关系统计
        lines.append("\n## 🔗 依赖关系分析")
        circular_deps = sum(1 for dep in report.dependencies if dep.is_circular)
        hardcoded_imports = sum(1 for dep in report.dependencies if dep.import_type == 'hardcoded')
        
        lines.extend([
            f"- **总依赖数**: {len(report.dependencies)}",
            f"- **循环依赖**: {circular_deps}",
            f"- **硬编码导入**: {hardcoded_imports}"
        ])
        
        # 详细问题列表（只显示前20个最严重的问题）
        critical_issues = [issue for issue in report.issues if issue.severity == 'critical']
        major_issues = [issue for issue in report.issues if issue.severity == 'major']
        
        if critical_issues or major_issues:
            lines.append("\n## 🔥 关键问题详情")
            
            for issue in (critical_issues + major_issues)[:20]:
                lines.extend([
                    f"\n### {issue.issue_type.replace('_', ' ').title()}",
                    f"**文件**: `{issue.file_path}:{issue.line_number}`",
                    f"**严重程度**: {issue.severity.upper()}",
                    f"**描述**: {issue.description}",
                    f"**建议**: {issue.suggestion}"
                ])
                
                if issue.code_snippet:
                    lines.append(f"**代码片段**:\n```python\n{issue.code_snippet}\n```")
        
        # 改进建议
        lines.extend([
            "\n## 💡 改进建议",
            "\n### 立即行动项",
        ])
        
        if critical_issues:
            lines.append("1. **修复关键问题**: 优先处理所有critical级别的问题")
        
        if hardcoded_imports > 10:
            lines.append("2. **重构导入系统**: 消除硬编码导入，使用相对导入")
        
        if circular_deps > 0:
            lines.append("3. **解决循环依赖**: 重构代码架构以消除循环依赖")
        
        if report.test_coverage < 50:
            lines.append("4. **提升测试覆盖率**: 编写更多单元测试和集成测试")
        
        lines.extend([
            "\n### 长期改进",
            "1. **建立代码质量门禁**: 在CI/CD中集成代码质量检查",
            "2. **定期重构**: 建立定期的技术债务清理计划",
            "3. **团队培训**: 提升团队的代码质量意识和技能",
            "4. **工具化**: 使用更多自动化工具来维护代码质量"
        ])
        
        return "\n".join(lines)

# ============================================================================
# 命令行接口
# ============================================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='代码质量分析工具')
    parser.add_argument('project_root', nargs='?', default='.', help='项目根目录')
    parser.add_argument('-o', '--output', help='输出报告文件路径')
    parser.add_argument('--json', action='store_true', help='输出JSON格式报告')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    try:
        analyzer = CodeQualityAnalyzer(args.project_root)
        report = analyzer.analyze()
        
        if args.json:
            # 输出JSON格式
            json_data = {
                'timestamp': report.timestamp,
                'metrics': {
                    'technical_debt_score': report.technical_debt_score,
                    'maintainability_index': report.maintainability_index,
                    'test_coverage': report.test_coverage,
                    'total_files': report.total_files,
                    'total_lines': report.total_lines
                },
                'issues': [asdict(issue) for issue in report.issues],
                'summary': report.summary
            }
            
            output_content = json.dumps(json_data, ensure_ascii=False, indent=2)
        else:
            # 输出Markdown格式
            output_content = analyzer.generate_report(report)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_content)
            print(f"📄 报告已保存到: {args.output}")
        else:
            print(output_content)
        
        # 输出简要统计
        print(f"\n📊 分析完成:")
        print(f"   - 文件数: {report.total_files}")
        print(f"   - 代码行数: {report.total_lines:,}")
        print(f"   - 问题数: {len(report.issues)}")
        print(f"   - 技术债务评分: {report.technical_debt_score:.1f}/100")
        print(f"   - 可维护性指数: {report.maintainability_index:.1f}/100")
        print(f"   - 测试覆盖率: {report.test_coverage:.1f}%")
        
        # 根据评分给出建议
        if report.technical_debt_score < 50:
            print("\n⚠️  技术债务较高，建议立即开始重构工作")
        elif report.technical_debt_score < 70:
            print("\n💡 技术债务中等，建议制定改进计划")
        else:
            print("\n✅ 代码质量良好，继续保持")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()