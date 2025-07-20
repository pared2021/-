#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术债务分析器

自动化分析项目中的技术债务，包括：
- 硬编码导入检测
- 代码重复分析
- 架构反模式识别
- 错误处理一致性检查
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import json


@dataclass
class DebtIssue:
    """技术债务问题"""
    type: str  # 问题类型
    severity: str  # 严重程度: critical, major, minor
    file_path: str  # 文件路径
    line_number: int  # 行号
    description: str  # 问题描述
    suggestion: str  # 修复建议
    estimated_hours: float  # 预估修复时间


@dataclass
class DebtReport:
    """债务分析报告"""
    total_issues: int
    critical_issues: int
    major_issues: int
    minor_issues: int
    estimated_total_hours: float
    issues_by_type: Dict[str, int]
    issues_by_file: Dict[str, int]
    detailed_issues: List[DebtIssue]


class DebtAnalyzer:
    """技术债务分析器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src"
        
        # 问题类型权重
        self.severity_weights = {
            "critical": 3.0,
            "major": 2.0, 
            "minor": 1.0
        }
        
        # 硬编码导入模式
        self.hardcoded_import_patterns = [
            r"from\s+src\.[\w.]+\s+import",
            r"import\s+src\.[\w.]+"
        ]
        
        # 反模式检测规则
        self.antipatterns = {
            "service_locator": r"container\.(get|resolve)\(",
            "god_class": None,  # 需要AST分析
            "long_method": None,  # 需要AST分析
            "duplicate_code": None  # 需要特殊算法
        }
    
    def analyze_project(self) -> DebtReport:
        """分析整个项目的技术债务"""
        issues = []
        
        # 分析所有Python文件
        for py_file in self._get_python_files():
            issues.extend(self._analyze_file(py_file))
        
        # 生成报告
        return self._generate_report(issues)
    
    def _get_python_files(self) -> List[Path]:
        """获取所有Python文件"""
        python_files = []
        
        for root, dirs, files in os.walk(self.src_path):
            # 跳过__pycache__目录
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            
            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def _analyze_file(self, file_path: Path) -> List[DebtIssue]:
        """分析单个文件的技术债务"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            # 检测硬编码导入
            issues.extend(self._detect_hardcoded_imports(file_path, lines))
            
            # 检测反模式
            issues.extend(self._detect_antipatterns(file_path, lines))
            
            # AST分析
            try:
                tree = ast.parse(content)
                issues.extend(self._analyze_ast(file_path, tree))
            except SyntaxError:
                # 语法错误文件跳过AST分析
                pass
                
        except Exception as e:
            # 记录文件读取错误
            issues.append(DebtIssue(
                type="file_error",
                severity="minor",
                file_path=str(file_path),
                line_number=1,
                description=f"文件读取错误: {e}",
                suggestion="检查文件编码和权限",
                estimated_hours=0.1
            ))
        
        return issues
    
    def _detect_hardcoded_imports(self, file_path: Path, lines: List[str]) -> List[DebtIssue]:
        """检测硬编码导入"""
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            for pattern in self.hardcoded_import_patterns:
                if re.search(pattern, line.strip()):
                    issues.append(DebtIssue(
                        type="hardcoded_import",
                        severity="major",
                        file_path=str(file_path),
                        line_number=line_num,
                        description=f"硬编码导入: {line.strip()}",
                        suggestion="使用相对导入或依赖注入",
                        estimated_hours=0.5
                    ))
        
        return issues
    
    def _detect_antipatterns(self, file_path: Path, lines: List[str]) -> List[DebtIssue]:
        """检测架构反模式"""
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            # 检测服务定位器模式
            if re.search(self.antipatterns["service_locator"], line):
                issues.append(DebtIssue(
                    type="service_locator_antipattern",
                    severity="critical",
                    file_path=str(file_path),
                    line_number=line_num,
                    description="使用服务定位器反模式",
                    suggestion="改用依赖注入",
                    estimated_hours=2.0
                ))
        
        return issues
    
    def _analyze_ast(self, file_path: Path, tree: ast.AST) -> List[DebtIssue]:
        """AST分析检测复杂问题"""
        issues = []
        
        class DebtVisitor(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
            
            def visit_FunctionDef(self, node):
                # 检测长方法
                if self._count_lines(node) > 50:
                    self.issues.append(DebtIssue(
                        type="long_method",
                        severity="major",
                        file_path=str(file_path),
                        line_number=node.lineno,
                        description=f"方法过长: {node.name} ({self._count_lines(node)} 行)",
                        suggestion="拆分为多个小方法",
                        estimated_hours=1.5
                    ))
                
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                # 检测上帝类
                method_count = len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                if method_count > 20:
                    self.issues.append(DebtIssue(
                        type="god_class",
                        severity="critical",
                        file_path=str(file_path),
                        line_number=node.lineno,
                        description=f"上帝类: {node.name} ({method_count} 个方法)",
                        suggestion="拆分为多个职责单一的类",
                        estimated_hours=4.0
                    ))
                
                self.generic_visit(node)
            
            def _count_lines(self, node):
                """计算节点的行数"""
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    return node.end_lineno - node.lineno + 1
                return 1
        
        visitor = DebtVisitor()
        visitor.visit(tree)
        issues.extend(visitor.issues)
        
        return issues
    
    def _generate_report(self, issues: List[DebtIssue]) -> DebtReport:
        """生成债务分析报告"""
        total_issues = len(issues)
        critical_issues = len([i for i in issues if i.severity == "critical"])
        major_issues = len([i for i in issues if i.severity == "major"])
        minor_issues = len([i for i in issues if i.severity == "minor"])
        
        estimated_total_hours = sum(i.estimated_hours for i in issues)
        
        issues_by_type = defaultdict(int)
        issues_by_file = defaultdict(int)
        
        for issue in issues:
            issues_by_type[issue.type] += 1
            issues_by_file[issue.file_path] += 1
        
        return DebtReport(
            total_issues=total_issues,
            critical_issues=critical_issues,
            major_issues=major_issues,
            minor_issues=minor_issues,
            estimated_total_hours=estimated_total_hours,
            issues_by_type=dict(issues_by_type),
            issues_by_file=dict(issues_by_file),
            detailed_issues=issues
        )
    
    def export_report(self, report: DebtReport, output_path: str) -> None:
        """导出报告到文件"""
        report_data = {
            "summary": {
                "total_issues": report.total_issues,
                "critical_issues": report.critical_issues,
                "major_issues": report.major_issues,
                "minor_issues": report.minor_issues,
                "estimated_total_hours": report.estimated_total_hours
            },
            "issues_by_type": report.issues_by_type,
            "issues_by_file": report.issues_by_file,
            "detailed_issues": [
                {
                    "type": issue.type,
                    "severity": issue.severity,
                    "file_path": issue.file_path,
                    "line_number": issue.line_number,
                    "description": issue.description,
                    "suggestion": issue.suggestion,
                    "estimated_hours": issue.estimated_hours
                }
                for issue in report.detailed_issues
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    def generate_markdown_report(self, report: DebtReport) -> str:
        """生成Markdown格式的报告"""
        md_content = []
        
        # 标题和摘要
        md_content.append("# 🔍 技术债务分析报告")
        md_content.append("")
        md_content.append("## 📊 问题统计")
        md_content.append("")
        md_content.append(f"- **总问题数**: {report.total_issues}")
        md_content.append(f"- **Critical**: {report.critical_issues} 🔴")
        md_content.append(f"- **Major**: {report.major_issues} 🟡")
        md_content.append(f"- **Minor**: {report.minor_issues} 🟢")
        md_content.append(f"- **预估修复时间**: {report.estimated_total_hours:.1f} 小时")
        md_content.append("")
        
        # 按类型统计
        md_content.append("## 🏷️ 问题类型分布")
        md_content.append("")
        for issue_type, count in sorted(report.issues_by_type.items(), key=lambda x: x[1], reverse=True):
            md_content.append(f"- **{issue_type}**: {count}")
        md_content.append("")
        
        # 最严重的文件
        md_content.append("## 📁 问题最多的文件")
        md_content.append("")
        top_files = sorted(report.issues_by_file.items(), key=lambda x: x[1], reverse=True)[:10]
        for file_path, count in top_files:
            md_content.append(f"- **{file_path}**: {count} 个问题")
        md_content.append("")
        
        # 详细问题列表（仅显示Critical和Major）
        critical_major_issues = [i for i in report.detailed_issues if i.severity in ["critical", "major"]]
        if critical_major_issues:
            md_content.append("## 🚨 关键问题详情")
            md_content.append("")
            
            for issue in critical_major_issues[:20]:  # 限制显示数量
                severity_emoji = "🔴" if issue.severity == "critical" else "🟡"
                md_content.append(f"### {severity_emoji} {issue.type}")
                md_content.append(f"**文件**: {issue.file_path}:{issue.line_number}")
                md_content.append(f"**问题**: {issue.description}")
                md_content.append(f"**建议**: {issue.suggestion}")
                md_content.append(f"**预估时间**: {issue.estimated_hours} 小时")
                md_content.append("")
        
        return "\n".join(md_content)


if __name__ == "__main__":
    # 示例用法
    analyzer = DebtAnalyzer(".")
    report = analyzer.analyze_project()
    
    # 导出JSON报告
    analyzer.export_report(report, "debt_analysis_report.json")
    
    # 生成Markdown报告
    md_report = analyzer.generate_markdown_report(report)
    with open("debt_analysis_report.md", "w", encoding="utf-8") as f:
        f.write(md_report)
    
    print(f"分析完成！发现 {report.total_issues} 个问题，预估修复时间 {report.estimated_total_hours:.1f} 小时")