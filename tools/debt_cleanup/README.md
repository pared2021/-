# 🧹 技术债务清理工具

这是一个全面的技术债务分析和清理工具包，用于自动化识别、分析和修复代码中的技术债务问题。

## 📋 功能特性

### 🔍 债务分析
- **硬编码导入检测**: 识别直接导入具体实现的问题
- **架构反模式检测**: 发现服务定位器、上帝类等反模式
- **代码重复分析**: 检测重复代码块和相似代码
- **复杂度分析**: 计算圈复杂度和方法长度
- **依赖关系分析**: 分析模块间的耦合度

### 🛠️ 自动化清理
- **重构任务管理**: 自动生成和执行重构计划
- **代码转换**: 自动化代码重构和模式应用
- **导入优化**: 整理和优化import语句
- **接口提取**: 自动提取抽象接口
- **异步化改造**: 将同步代码转换为异步模式

### 📊 进度跟踪
- **实时监控**: 持续监控代码质量指标
- **趋势分析**: 生成质量和性能趋势报告
- **基准对比**: 与基准指标进行对比分析
- **进度可视化**: 清理进度的可视化展示

## 🚀 快速开始

### 安装依赖

```bash
# 安装基础依赖
pip install ast-tools radon coverage psutil

# 可选：安装代码质量工具
pip install pylint flake8 black isort
```

### 基本用法

1. **分析技术债务**
```bash
# 生成JSON格式的债务分析报告
python tools/debt_cleanup/main.py analyze --format json --output debt_report.json

# 生成Markdown格式的报告
python tools/debt_cleanup/main.py analyze --format markdown --output debt_report.md
```

2. **生成清理计划**
```bash
# 生成高优先级任务的清理计划
python tools/debt_cleanup/main.py plan --priority high --output cleanup_plan.json

# 生成完整清理计划
python tools/debt_cleanup/main.py plan --output full_plan.json
```

3. **执行清理任务**
```bash
# 模拟执行（不实际修改文件）
python tools/debt_cleanup/main.py execute --plan cleanup_plan.json --dry-run

# 实际执行清理
python tools/debt_cleanup/main.py execute --plan cleanup_plan.json

# 执行特定任务
python tools/debt_cleanup/main.py execute --tasks task_001,task_002
```

4. **监控进度**
```bash
# 查看当前状态
python tools/debt_cleanup/main.py status

# 生成趋势报告
python tools/debt_cleanup/main.py report --days 7 --output trend_report.md

# 设置基准指标
python tools/debt_cleanup/main.py baseline
```

## 📁 工具组件

### DebtAnalyzer (债务分析器)
负责扫描和分析代码中的技术债务问题。

```python
from debt_analyzer import DebtAnalyzer

analyzer = DebtAnalyzer()
results = analyzer.analyze_project()
print(f"发现 {len(results['issues'])} 个问题")
```

### CleanupManager (清理管理器)
协调和执行技术债务清理任务。

```python
from cleanup_manager import CleanupManager

manager = CleanupManager()
plan = manager.create_cleanup_plan(debt_results)
results = manager.execute_plan(plan)
```

### ProgressTracker (进度跟踪器)
监控清理进度和质量指标变化。

```python
from progress_tracker import ProgressTracker

tracker = ProgressTracker()
tracker.start_monitoring()
tracker.update_task_progress("task_001", "completed", 100.0)
```

## ⚙️ 配置选项

### 分析配置
```python
# 自定义分析参数
config = DebtCleanupConfig()
config.analysis.max_cyclomatic_complexity = 8
config.analysis.max_method_length = 40
config.analysis.exclude_patterns.append("legacy/**")
```

### 清理配置
```python
# 自定义清理行为
config.cleanup.create_backup = True
config.cleanup.dry_run_first = True
config.cleanup.max_workers = 2
```

### 质量阈值
```python
# 设置质量门禁
config.quality_thresholds.min_test_coverage = 85.0
config.quality_thresholds.max_technical_debt_ratio = 15.0
```

## 📊 报告示例

### 债务分析报告
```json
{
  "summary": {
    "total_issues": 156,
    "high_priority": 23,
    "medium_priority": 67,
    "low_priority": 66,
    "estimated_hours": 89.5
  },
  "debt_types": {
    "hardcoded_imports": 45,
    "service_locator": 12,
    "code_duplication": 34,
    "missing_interfaces": 28
  }
}
```

### 清理计划
```json
{
  "plan_id": "cleanup_20250120_001",
  "priority": "high",
  "estimated_hours": 24.5,
  "tasks": [
    {
      "task_id": "task_001",
      "task_type": "remove_hardcoded_imports",
      "priority": "high",
      "estimated_hours": 8.0,
      "target_files": ["src/core/container.py"]
    }
  ]
}
```

## 🔧 高级用法

### 自定义重构规则
```python
# 添加自定义重构模式
from cleanup_manager import RefactoringPattern

class CustomPattern(RefactoringPattern):
    def can_apply(self, code_element):
        # 检查是否可以应用此模式
        return True
    
    def apply(self, code_element):
        # 执行重构
        return modified_code

manager.add_refactoring_pattern(CustomPattern())
```

### 集成CI/CD
```yaml
# GitHub Actions 示例
name: Technical Debt Check
on: [push, pull_request]

jobs:
  debt-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Analyze Technical Debt
        run: |
          python tools/debt_cleanup/main.py analyze --format json --output debt_report.json
          python tools/debt_cleanup/main.py plan --priority high --output plan.json
      - name: Upload Reports
        uses: actions/upload-artifact@v2
        with:
          name: debt-reports
          path: "*.json"
```

### 自定义质量门禁
```python
# 设置质量门禁检查
def quality_gate_check(metrics):
    if metrics['test_coverage'] < 80:
        raise Exception("测试覆盖率不足")
    
    if metrics['technical_debt_ratio'] > 25:
        raise Exception("技术债务比率过高")
    
    if metrics['maintainability_index'] < 60:
        raise Exception("可维护性指数过低")

tracker.add_quality_gate(quality_gate_check)
```

## 📈 最佳实践

### 1. 渐进式清理
- 从高优先级债务开始
- 每次清理后运行完整测试
- 保持小批量、频繁的清理节奏

### 2. 质量监控
- 设置基准指标
- 定期生成趋势报告
- 建立质量门禁机制

### 3. 团队协作
- 制定清理计划和时间表
- 分配清理任务给团队成员
- 定期回顾清理进展

### 4. 持续改进
- 根据项目特点调整配置
- 添加项目特定的检测规则
- 优化清理流程和工具

## 🚨 注意事项

### 安全提醒
- 清理前务必备份代码
- 首次使用建议开启dry-run模式
- 清理后运行完整测试套件
- 重要修改需要代码审查

### 性能考虑
- 大型项目建议分批处理
- 调整并发工作线程数量
- 排除不必要的文件和目录

### 兼容性
- 支持Python 3.7+
- 兼容主流代码编辑器
- 支持Windows/Linux/macOS

## 🤝 贡献指南

欢迎贡献代码和改进建议！

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如果遇到问题或需要帮助：

- 查看 [常见问题](FAQ.md)
- 提交 [Issue](../../issues)
- 参考 [文档](../../docs)

---

**开始清理技术债务，让代码更健康！** 🎯