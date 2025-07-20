#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版代码质量检查工具
快速识别项目中的关键技术债务问题
"""

import os
import re
from pathlib import Path
from collections import Counter, defaultdict

def get_python_files(project_root):
    """获取所有Python文件"""
    python_files = []
    for root, dirs, files in os.walk(project_root):
        # 跳过虚拟环境和缓存目录
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.pytest_cache', 'venv', 'env', '.venv'}]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return python_files

def read_file_safe(file_path):
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

def analyze_hardcoded_imports(project_root):
    """分析硬编码导入"""
    issues = []
    patterns = [
        r'from\s+src\.',
        r'import\s+src\.',
        r'sys\.path\.append',
        r'os\.path\.dirname.*__file__'
    ]
    
    for file_path in get_python_files(project_root):
        content = read_file_safe(file_path)
        if not content:
            continue
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                if re.search(pattern, line):
                    issues.append({
                        'file': str(file_path.relative_to(Path(project_root))),
                        'line': line_num,
                        'type': 'hardcoded_import',
                        'severity': 'major',
                        'description': f'硬编码导入: {line.strip()}',
                        'code': line.strip()
                    })
    
    return issues

def analyze_code_complexity(project_root):
    """分析代码复杂度"""
    issues = []
    file_stats = {}
    
    for file_path in get_python_files(project_root):
        content = read_file_safe(file_path)
        if not content:
            continue
        
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        
        # 简单的复杂度指标
        function_count = len([line for line in lines if re.match(r'^\s*def\s+', line)])
        class_count = len([line for line in lines if re.match(r'^\s*class\s+', line)])
        
        # 计算最大嵌套深度
        max_indent = 0
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent // 4)  # 假设4空格缩进
        
        relative_path = str(file_path.relative_to(Path(project_root)))
        file_stats[relative_path] = {
            'lines_of_code': len(non_empty_lines),
            'function_count': function_count,
            'class_count': class_count,
            'max_nesting': max_indent
        }
        
        # 检查复杂度阈值
        if len(non_empty_lines) > 500:
            issues.append({
                'file': relative_path,
                'line': 1,
                'type': 'large_file',
                'severity': 'minor',
                'description': f'文件过大: {len(non_empty_lines)} 行代码',
                'code': ''
            })
        
        if max_indent > 6:
            issues.append({
                'file': relative_path,
                'line': 1,
                'type': 'deep_nesting',
                'severity': 'minor',
                'description': f'嵌套层次过深: {max_indent} 层',
                'code': ''
            })
    
    return issues, file_stats

def analyze_code_duplication(project_root):
    """分析代码重复"""
    issues = []
    line_hashes = defaultdict(list)
    
    for file_path in get_python_files(project_root):
        content = read_file_safe(file_path)
        if not content:
            continue
        
        lines = content.split('\n')
        relative_path = str(file_path.relative_to(Path(project_root)))
        
        for line_num, line in enumerate(lines, 1):
            clean_line = line.strip()
            if clean_line and not clean_line.startswith('#') and len(clean_line) > 20:
                line_hash = hash(clean_line)
                line_hashes[line_hash].append({
                    'file': relative_path,
                    'line': line_num,
                    'content': clean_line
                })
    
    # 查找重复行
    for line_hash, occurrences in line_hashes.items():
        if len(occurrences) > 1:
            for occurrence in occurrences[1:]:  # 跳过第一个
                issues.append({
                    'file': occurrence['file'],
                    'line': occurrence['line'],
                    'type': 'code_duplication',
                    'severity': 'minor',
                    'description': f'重复代码行，共{len(occurrences)}处',
                    'code': occurrence['content'][:80] + '...' if len(occurrence['content']) > 80 else occurrence['content']
                })
    
    return issues

def analyze_error_handling(project_root):
    """分析错误处理"""
    issues = []
    
    for file_path in get_python_files(project_root):
        content = read_file_safe(file_path)
        if not content:
            continue
        
        lines = content.split('\n')
        relative_path = str(file_path.relative_to(Path(project_root)))
        
        in_try_block = False
        try_line = 0
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if stripped.startswith('try:'):
                in_try_block = True
                try_line = line_num
            elif stripped.startswith('except:') and in_try_block:
                issues.append({
                    'file': relative_path,
                    'line': line_num,
                    'type': 'bare_except',
                    'severity': 'major',
                    'description': '使用了裸露的except语句',
                    'code': stripped
                })
                in_try_block = False
            elif stripped.startswith('except ') and in_try_block:
                in_try_block = False
            elif not stripped or not stripped.startswith(' '):
                in_try_block = False
    
    return issues

def generate_report(project_root):
    """生成质量报告"""
    print("🔍 开始代码质量分析...")
    
    # 执行各种分析
    print("📋 分析硬编码导入...")
    hardcoded_issues = analyze_hardcoded_imports(project_root)
    
    print("📊 分析代码复杂度...")
    complexity_issues, file_stats = analyze_code_complexity(project_root)
    
    print("🔄 分析代码重复...")
    duplication_issues = analyze_code_duplication(project_root)
    
    print("⚠️  分析错误处理...")
    error_handling_issues = analyze_error_handling(project_root)
    
    # 合并所有问题
    all_issues = hardcoded_issues + complexity_issues + duplication_issues + error_handling_issues
    
    # 统计信息
    total_files = len(get_python_files(project_root))
    total_lines = sum(stats['lines_of_code'] for stats in file_stats.values())
    
    # 按严重程度统计
    severity_counts = Counter(issue['severity'] for issue in all_issues)
    type_counts = Counter(issue['type'] for issue in all_issues)
    
    # 生成报告
    report_lines = [
        "# 🔍 代码质量分析报告",
        f"\n**分析时间**: {__import__('time').strftime('%Y-%m-%d %H:%M:%S')}",
        f"**项目文件数**: {total_files}",
        f"**代码行数**: {total_lines:,}",
        f"\n## 📊 问题统计",
        f"\n- **总问题数**: {len(all_issues)}",
    ]
    
    # 按严重程度统计
    for severity, count in severity_counts.items():
        emoji = {'critical': '🔴', 'major': '🟡', 'minor': '🟢'}.get(severity, '⚪')
        report_lines.append(f"- **{severity.title()}**: {count} {emoji}")
    
    # 问题类型统计
    report_lines.append("\n## 📋 问题类型分布")
    for issue_type, count in type_counts.most_common():
        report_lines.append(f"- **{issue_type.replace('_', ' ').title()}**: {count}")
    
    # 文件统计
    report_lines.append("\n## 📈 代码统计")
    total_functions = sum(stats['function_count'] for stats in file_stats.values())
    total_classes = sum(stats['class_count'] for stats in file_stats.values())
    avg_file_size = total_lines / total_files if total_files > 0 else 0
    
    report_lines.extend([
        f"- **函数总数**: {total_functions}",
        f"- **类总数**: {total_classes}",
        f"- **平均文件大小**: {avg_file_size:.1f} 行"
    ])
    
    # 关键问题详情
    critical_issues = [issue for issue in all_issues if issue['severity'] in ['critical', 'major']]
    if critical_issues:
        report_lines.append("\n## 🔥 关键问题详情")
        
        for issue in critical_issues[:15]:  # 只显示前15个
            report_lines.extend([
                f"\n### {issue['type'].replace('_', ' ').title()}",
                f"**文件**: `{issue['file']}:{issue['line']}`",
                f"**严重程度**: {issue['severity'].upper()}",
                f"**描述**: {issue['description']}"
            ])
            
            if issue['code']:
                report_lines.append(f"**代码**: `{issue['code']}`")
    
    # 改进建议
    report_lines.extend([
        "\n## 💡 改进建议",
        "\n### 立即行动项"
    ])
    
    if len([i for i in all_issues if i['type'] == 'hardcoded_import']) > 10:
        report_lines.append("1. **重构导入系统**: 消除硬编码导入，使用相对导入")
    
    if len([i for i in all_issues if i['type'] == 'bare_except']) > 0:
        report_lines.append("2. **改进错误处理**: 使用具体的异常类型而不是裸露的except")
    
    if len([i for i in all_issues if i['type'] == 'code_duplication']) > 20:
        report_lines.append("3. **消除代码重复**: 提取公共函数和类")
    
    if avg_file_size > 300:
        report_lines.append("4. **拆分大文件**: 将大文件拆分为更小的模块")
    
    report_lines.extend([
        "\n### 长期改进",
        "1. **建立代码质量门禁**: 在CI/CD中集成代码质量检查",
        "2. **定期重构**: 建立定期的技术债务清理计划",
        "3. **团队培训**: 提升团队的代码质量意识和技能",
        "4. **工具化**: 使用更多自动化工具来维护代码质量"
    ])
    
    # 计算质量评分
    max_score = 100
    penalty = min(len(all_issues) * 2, max_score)  # 每个问题扣2分
    quality_score = max(0, max_score - penalty)
    
    report_lines.extend([
        f"\n## 🎯 质量评分",
        f"\n**总体评分**: {quality_score}/100"
    ])
    
    if quality_score < 50:
        report_lines.append("\n⚠️  **代码质量较差，建议立即开始重构工作**")
    elif quality_score < 70:
        report_lines.append("\n💡 **代码质量中等，建议制定改进计划**")
    else:
        report_lines.append("\n✅ **代码质量良好，继续保持**")
    
    return "\n".join(report_lines), {
        'total_files': total_files,
        'total_lines': total_lines,
        'total_issues': len(all_issues),
        'quality_score': quality_score,
        'severity_counts': dict(severity_counts),
        'type_counts': dict(type_counts)
    }

def main():
    """主函数"""
    import sys
    
    project_root = sys.argv[1] if len(sys.argv) > 1 else '.'
    output_file = None
    
    # 简单的参数解析
    if '-o' in sys.argv:
        idx = sys.argv.index('-o')
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
    
    try:
        report_content, stats = generate_report(project_root)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"📄 报告已保存到: {output_file}")
        else:
            print(report_content)
        
        # 输出简要统计
        print(f"\n📊 分析完成:")
        print(f"   - 文件数: {stats['total_files']}")
        print(f"   - 代码行数: {stats['total_lines']:,}")
        print(f"   - 问题数: {stats['total_issues']}")
        print(f"   - 质量评分: {stats['quality_score']}/100")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()