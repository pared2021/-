# 🔍 代码质量分析报告

**分析时间**: 2025-07-19 22:45:39
**项目文件数**: 171
**代码行数**: 29,101

## 📊 问题统计

- **总问题数**: 4422
- **Major**: 328 🟡
- **Minor**: 4094 🟢

## 📋 问题类型分布
- **Code Duplication**: 4054
- **Hardcoded Import**: 328
- **Deep Nesting**: 33
- **Large File**: 7

## 📈 代码统计
- **函数总数**: 1952
- **类总数**: 288
- **平均文件大小**: 170.2 行

## 🔥 关键问题详情

### Hardcoded Import
**文件**: `main.py:15`
**严重程度**: MAJOR
**描述**: 硬编码导入: project_root = os.path.dirname(os.path.abspath(__file__))
**代码**: `project_root = os.path.dirname(os.path.abspath(__file__))`

### Hardcoded Import
**文件**: `main.py:34`
**严重程度**: MAJOR
**描述**: 硬编码导入: from src.main import main as src_main
**代码**: `from src.main import main as src_main`

### Hardcoded Import
**文件**: `test_import.py:22`
**严重程度**: MAJOR
**描述**: 硬编码导入: from src.common import module_types
**代码**: `from src.common import module_types`

### Hardcoded Import
**文件**: `test_import.py:36`
**严重程度**: MAJOR
**描述**: 硬编码导入: from src.common.module_manager import initialize_module_manager
**代码**: `from src.common.module_manager import initialize_module_manager`

### Hardcoded Import
**文件**: `scripts\run_in_venv.py:43`
**严重程度**: MAJOR
**描述**: 硬编码导入: current_dir = os.path.dirname(os.path.abspath(__file__))
**代码**: `current_dir = os.path.dirname(os.path.abspath(__file__))`

### Hardcoded Import
**文件**: `scripts\run_in_venv.py:70`
**严重程度**: MAJOR
**描述**: 硬编码导入: current_dir = os.path.dirname(os.path.abspath(__file__))
**代码**: `current_dir = os.path.dirname(os.path.abspath(__file__))`

### Hardcoded Import
**文件**: `src\main.py:15`
**严重程度**: MAJOR
**描述**: 硬编码导入: from src.common.app_config import init_application_metadata, setup_application_properties
**代码**: `from src.common.app_config import init_application_metadata, setup_application_properties`

### Hardcoded Import
**文件**: `src\main.py:16`
**严重程度**: MAJOR
**描述**: 硬编码导入: from src.services.config import config, get_config
**代码**: `from src.services.config import config, get_config`

### Hardcoded Import
**文件**: `src\main.py:234`
**严重程度**: MAJOR
**描述**: 硬编码导入: from src.gui.main_window import MainWindow
**代码**: `from src.gui.main_window import MainWindow`

### Hardcoded Import
**文件**: `src\main.py:237`
**严重程度**: MAJOR
**描述**: 硬编码导入: from src.application.containers.main_container import MainContainer
**代码**: `from src.application.containers.main_container import MainContainer`

### Hardcoded Import
**文件**: `src\main.py:272`
**严重程度**: MAJOR
**描述**: 硬编码导入: from src.common.module_manager import get_module_manager
**代码**: `from src.common.module_manager import get_module_manager`

### Hardcoded Import
**文件**: `src\main.py:297`
**严重程度**: MAJOR
**描述**: 硬编码导入: from src.cli.main import CLIApp
**代码**: `from src.cli.main import CLIApp`

### Hardcoded Import
**文件**: `src\main.py:426`
**严重程度**: MAJOR
**描述**: 硬编码导入: from src.common.module_manager import initialize_module_manager
**代码**: `from src.common.module_manager import initialize_module_manager`

### Hardcoded Import
**文件**: `src\application\containers\main_container.py:10`
**严重程度**: MAJOR
**描述**: 硬编码导入: from src.core.interfaces.services import IGameAnalyzer, IAutomationService, IStateManager
**代码**: `from src.core.interfaces.services import IGameAnalyzer, IAutomationService, IStateManager`

### Hardcoded Import
**文件**: `src\application\containers\main_container.py:11`
**严重程度**: MAJOR
**描述**: 硬编码导入: from src.core.interfaces.repositories import IConfigRepository, ITemplateRepository
**代码**: `from src.core.interfaces.repositories import IConfigRepository, ITemplateRepository`

## 💡 改进建议

### 立即行动项
1. **重构导入系统**: 消除硬编码导入，使用相对导入
3. **消除代码重复**: 提取公共函数和类

### 长期改进
1. **建立代码质量门禁**: 在CI/CD中集成代码质量检查
2. **定期重构**: 建立定期的技术债务清理计划
3. **团队培训**: 提升团队的代码质量意识和技能
4. **工具化**: 使用更多自动化工具来维护代码质量

## 🎯 质量评分

**总体评分**: 0/100

⚠️  **代码质量较差，建议立即开始重构工作**