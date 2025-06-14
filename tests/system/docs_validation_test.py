#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档系统完整性验证测试

验证第三阶段文档系统完善的成果，确保：
1. 文档文件存在性
2. 文档内容完整性  
3. 交叉引用有效性
4. 格式标准性
5. 示例代码可用性
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple

class DocumentationValidator:
    """文档验证器"""
    
    def __init__(self):
        self.root_path = Path('.')
        self.docs_path = self.root_path / 'docs'
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'errors': [],
            'warnings': []
        }
        
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始文档系统完整性验证...")
        print("=" * 50)
        
        # 1. 文件存在性测试
        self._test_file_existence()
        
        # 2. 内容完整性测试
        self._test_content_completeness()
        
        # 3. 交叉引用测试
        self._test_cross_references()
        
        # 4. 格式标准性测试
        self._test_format_standards()
        
        # 5. 示例代码测试
        self._test_code_examples()
        
        # 6. 文档结构测试
        self._test_document_structure()
        
        # 生成报告并返回成功率
        return self._generate_report()
        
    def _test_file_existence(self):
        """测试文档文件存在性"""
        print("📁 测试文档文件存在性...")
        
        expected_files = [
            'README.md',
            'docs/architecture.md',
            'docs/developer-guide.md', 
            'docs/configuration.md',
            'docs/api/core/unified-game-analyzer.md',
            '第三阶段执行计划.md',
            '第三阶段完成报告.md'
        ]
        
        for file_path in expected_files:
            full_path = self.root_path / file_path
            self._assert_file_exists(full_path, f"核心文档文件: {file_path}")
            
        # 检查目录结构
        expected_dirs = [
            'docs',
            'docs/api',
            'docs/api/core',
            'docs/api/services',
            'docs/api/common',
            'docs/api/ui'
        ]
        
        for dir_path in expected_dirs:
            full_path = self.root_path / dir_path
            self._assert_dir_exists(full_path, f"文档目录: {dir_path}")
            
    def _test_content_completeness(self):
        """测试文档内容完整性"""
        print("📝 测试文档内容完整性...")
        
        # README.md 内容检查
        readme_requirements = [
            "🎮 游戏自动化工具",
            "四层分层架构",
            "🏗️ 架构概览", 
            "📁 目录结构",
            "🚀 快速开始",
            "src/core/",
            "src/services/",
            "src/common/",
            "src/ui/"
        ]
        self._check_content_requirements('README.md', readme_requirements)
        
        # 架构文档内容检查
        architecture_requirements = [
            "架构设计文档",
            "设计理念和原则",
            "分层架构详解",
            "UI 层",
            "Core 层", 
            "Services 层",
            "Common 层",
            "职责分配说明",
            "扩展点和插件机制"
        ]
        self._check_content_requirements('docs/architecture.md', architecture_requirements)
        
        # 开发者指南内容检查
        developer_requirements = [
            "开发者指南",
            "开发环境设置",
            "代码规范和最佳实践",
            "新功能开发流程",
            "调试和测试指南",
            "常见问题解答"
        ]
        self._check_content_requirements('docs/developer-guide.md', developer_requirements)
        
        # 配置指南内容检查
        config_requirements = [
            "配置指南",
            "配置系统概述",
            "配置文件结构", 
            "配置选项详解",
            "配置最佳实践",
            "故障排除"
        ]
        self._check_content_requirements('docs/configuration.md', config_requirements)
        
    def _test_cross_references(self):
        """测试交叉引用有效性"""
        print("🔗 测试文档交叉引用...")
        
        # 收集所有Markdown文件
        md_files = list(self.root_path.glob('**/*.md'))
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                # 查找相对路径引用
                links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                
                for link_text, link_path in links:
                    if link_path.startswith('http'):
                        continue  # 跳过外部链接
                    
                    # 检查相对路径引用
                    if not link_path.startswith('#'):  # 跳过锚点链接
                        referenced_file = md_file.parent / link_path
                        if not referenced_file.exists():
                            self._add_warning(
                                f"在 {md_file.name} 中发现无效引用: {link_path}"
                            )
                            
            except Exception as e:
                self._add_error(f"检查 {md_file.name} 交叉引用时出错: {e}")
                
    def _test_format_standards(self):
        """测试格式标准性"""
        print("📐 测试文档格式标准...")
        
        md_files = [
            'README.md',
            'docs/architecture.md',
            'docs/developer-guide.md',
            'docs/configuration.md'
        ]
        
        for file_path in md_files:
            full_path = self.root_path / file_path
            if not full_path.exists():
                continue
                
            try:
                content = full_path.read_text(encoding='utf-8')
                
                # 检查标题层次
                headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
                if not headings:
                    self._add_warning(f"{file_path} 缺少标题结构")
                    
                # 检查代码块格式
                code_blocks = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
                for lang, code in code_blocks:
                    if lang and lang in ['python', 'json', 'bash']:
                        # 基本语法检查
                        if lang == 'json' and code.strip():
                            try:
                                # 简单的JSON格式检查
                                if code.strip().startswith('{') or code.strip().startswith('['):
                                    json.loads(code)
                            except json.JSONDecodeError:
                                self._add_warning(f"{file_path} 包含格式错误的JSON代码块")
                                
                self._add_pass(f"格式标准检查: {file_path}")
                
            except Exception as e:
                self._add_error(f"检查 {file_path} 格式时出错: {e}")
                
    def _test_code_examples(self):
        """测试示例代码可用性"""
        print("💻 测试示例代码...")
        
        md_files = [
            'docs/architecture.md',
            'docs/developer-guide.md',
            'docs/api/core/unified-game-analyzer.md'
        ]
        
        for file_path in md_files:
            full_path = self.root_path / file_path
            if not full_path.exists():
                continue
                
            try:
                content = full_path.read_text(encoding='utf-8')
                
                # 提取Python代码块
                python_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)
                
                for i, code in enumerate(python_blocks):
                    # 基本语法检查
                    try:
                        compile(code, f'<{file_path}_block_{i}>', 'exec')
                        self._add_pass(f"Python代码块语法检查: {file_path} 块{i+1}")
                    except SyntaxError as e:
                        # 忽略明显的示例代码（包含...或省略符）
                        if '...' not in code and 'import' in code:
                            self._add_warning(
                                f"{file_path} 第{i+1}个Python代码块语法错误: {e}"
                            )
                            
            except Exception as e:
                self._add_error(f"检查 {file_path} 代码示例时出错: {e}")
                
    def _test_document_structure(self):
        """测试文档结构完整性"""
        print("🏗️ 测试文档结构...")
        
        # 检查是否有目录（TOC）
        important_docs = [
            'docs/architecture.md',
            'docs/developer-guide.md',
            'docs/configuration.md'
        ]
        
        for doc_path in important_docs:
            full_path = self.root_path / doc_path
            if not full_path.exists():
                continue
                
            try:
                content = full_path.read_text(encoding='utf-8')
                
                # 检查是否有概述部分
                if '## 概述' not in content and '## 📖 概述' not in content:
                    self._add_warning(f"{doc_path} 缺少概述部分")
                    
                # 检查文档版本信息
                if '文档版本' not in content and '最后更新' not in content:
                    self._add_warning(f"{doc_path} 缺少版本信息")
                    
                # 检查是否有示例
                if 'example' not in content.lower() and '示例' not in content:
                    self._add_warning(f"{doc_path} 可能缺少使用示例")
                    
                self._add_pass(f"文档结构检查: {doc_path}")
                
            except Exception as e:
                self._add_error(f"检查 {doc_path} 结构时出错: {e}")
                
    def _check_content_requirements(self, file_path: str, requirements: List[str]):
        """检查内容需求"""
        full_path = self.root_path / file_path
        if not full_path.exists():
            self._add_error(f"文件不存在: {file_path}")
            return
            
        try:
            content = full_path.read_text(encoding='utf-8')
            missing_content = []
            
            for requirement in requirements:
                if requirement not in content:
                    missing_content.append(requirement)
                    
            if missing_content:
                self._add_warning(
                    f"{file_path} 缺少必要内容: {', '.join(missing_content)}"
                )
            else:
                self._add_pass(f"内容完整性检查: {file_path}")
                
        except Exception as e:
            self._add_error(f"检查 {file_path} 内容时出错: {e}")
            
    def _assert_file_exists(self, file_path: Path, description: str):
        """断言文件存在"""
        if file_path.exists() and file_path.is_file():
            self._add_pass(f"文件存在: {description}")
        else:
            self._add_error(f"文件不存在: {description} - {file_path}")
            
    def _assert_dir_exists(self, dir_path: Path, description: str):
        """断言目录存在"""
        if dir_path.exists() and dir_path.is_dir():
            self._add_pass(f"目录存在: {description}")
        else:
            self._add_error(f"目录不存在: {description} - {dir_path}")
            
    def _add_pass(self, message: str):
        """添加通过的测试"""
        self.results['total_tests'] += 1
        self.results['passed_tests'] += 1
        print(f"  ✅ {message}")
        
    def _add_error(self, message: str):
        """添加错误"""
        self.results['total_tests'] += 1
        self.results['failed_tests'] += 1
        self.results['errors'].append(message)
        print(f"  ❌ {message}")
        
    def _add_warning(self, message: str):
        """添加警告"""
        self.results['warnings'].append(message)
        print(f"  ⚠️  {message}")
        
    def _generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 50)
        print("📊 文档验证测试报告")
        print("=" * 50)
        
        total = self.results['total_tests']
        passed = self.results['passed_tests']
        failed = self.results['failed_tests']
        
        if total > 0:
            success_rate = (passed / total) * 100
        else:
            success_rate = 0
            
        print(f"总测试数: {total}")
        print(f"通过测试: {passed}")
        print(f"失败测试: {failed}")
        print(f"成功率: {success_rate:.1f}%")
        print(f"警告数: {len(self.results['warnings'])}")
        
        # 评估等级
        if success_rate >= 90 and len(self.results['warnings']) <= 5:
            grade = "优秀 🏆"
        elif success_rate >= 80:
            grade = "良好 👍"
        elif success_rate >= 70:
            grade = "合格 ✔️"
        else:
            grade = "需要改进 ⚠️"
            
        print(f"文档质量等级: {grade}")
        
        # 显示错误详情
        if self.results['errors']:
            print(f"\n❌ 错误详情:")
            for error in self.results['errors']:
                print(f"   • {error}")
                
        # 显示警告详情
        if self.results['warnings']:
            print(f"\n⚠️ 警告详情:")
            for warning in self.results['warnings'][:10]:  # 只显示前10个警告
                print(f"   • {warning}")
            if len(self.results['warnings']) > 10:
                print(f"   ... 还有 {len(self.results['warnings']) - 10} 个警告")
                
        # 文档完整性评估
        print(f"\n📚 文档完整性评估:")
        
        expected_files = [
            'README.md',
            'docs/architecture.md', 
            'docs/developer-guide.md',
            'docs/configuration.md',
            'docs/api/core/unified-game-analyzer.md'
        ]
        
        existing_files = sum(1 for f in expected_files if (self.root_path / f).exists())
        completeness = (existing_files / len(expected_files)) * 100
        
        print(f"文档覆盖率: {completeness:.0f}% ({existing_files}/{len(expected_files)})")
        
        # 内容丰富度评估
        total_content_size = 0
        for file_path in expected_files:
            full_path = self.root_path / file_path
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding='utf-8')
                    total_content_size += len(content)
                except:
                    pass
                    
        if total_content_size > 50000:
            content_richness = "非常丰富"
        elif total_content_size > 30000:
            content_richness = "丰富"
        elif total_content_size > 15000:
            content_richness = "适中"
        else:
            content_richness = "较少"
            
        print(f"内容丰富度: {content_richness} (~{total_content_size//1000}k字符)")
        
        # 总体评价
        print(f"\n🎯 总体评价:")
        if success_rate >= 85 and completeness >= 80:
            print("✅ 第三阶段文档系统完善目标已成功达成!")
            print("📚 文档体系完整、结构清晰、内容丰富")
            print("🚀 已为项目的长期发展奠定坚实文档基础")
        elif success_rate >= 70:
            print("👍 文档系统基本完善，还有提升空间")
            print("📝 建议优先解决错误，改进警告提及的问题")
        else:
            print("⚠️ 文档系统需要进一步完善")
            print("🔧 建议重点关注错误修复和内容补充")
            
        return success_rate

def main():
    """主函数"""
    validator = DocumentationValidator()
    success_rate = validator.run_all_tests()
    
    # 返回适当的退出码
    if success_rate >= 70:
        return 0  # 成功
    else:
        return 1  # 需要改进

if __name__ == '__main__':
    import sys
    sys.exit(main())