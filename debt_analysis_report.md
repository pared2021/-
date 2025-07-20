# 🔍 技术债务分析报告

## 📊 问题统计

- **总问题数**: 407
- **Critical**: 58 🔴
- **Major**: 349 🟡
- **Minor**: 0 🟢
- **预估修复时间**: 443.5 小时

## 🏷️ 问题类型分布

- **hardcoded_import**: 256
- **long_method**: 93
- **god_class**: 30
- **service_locator_antipattern**: 28

## 📁 问题最多的文件

- **src\gui\main_window.py**: 59 个问题
- **src\core\container\container_config.py**: 28 个问题
- **src\models\game_automation_model.py**: 19 个问题
- **src\main.py**: 12 个问题
- **src\common\containers.py**: 12 个问题
- **src\gui\dialogs\automation_manager_dialog.py**: 12 个问题
- **src\application\containers\main_container.py**: 11 个问题
- **src\services\error_handler.py**: 11 个问题
- **src\gui\dialogs\template_manager_dialog.py**: 10 个问题
- **src\gui\modern_ui\components\demo.py**: 10 个问题

## 🚨 关键问题详情

### 🟡 hardcoded_import
**文件**: src\main.py:15
**问题**: 硬编码导入: from src.common.app_config import init_application_metadata, setup_application_properties
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时

### 🟡 hardcoded_import
**文件**: src\main.py:16
**问题**: 硬编码导入: from src.services.config import config, get_config
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时

### 🟡 hardcoded_import
**文件**: src\main.py:234
**问题**: 硬编码导入: from src.gui.main_window import MainWindow
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时

### 🟡 hardcoded_import
**文件**: src\main.py:237
**问题**: 硬编码导入: from src.application.containers.main_container import MainContainer
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时

### 🟡 hardcoded_import
**文件**: src\main.py:251
**问题**: 硬编码导入: from src.gui.modern_ui.modern_main_window import ModernMainWindow
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时

### 🟡 hardcoded_import
**文件**: src\main.py:254
**问题**: 硬编码导入: from src.application.containers.main_container import MainContainer
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时

### 🟡 hardcoded_import
**文件**: src\main.py:289
**问题**: 硬编码导入: from src.common.module_manager import get_module_manager
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时

### 🟡 hardcoded_import
**文件**: src\main.py:314
**问题**: 硬编码导入: from src.cli.main import CLIApp
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时

### 🟡 hardcoded_import
**文件**: src\main.py:447
**问题**: 硬编码导入: from src.common.module_manager import initialize_module_manager
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时

### 🟡 long_method
**文件**: src\main.py:71
**问题**: 方法过长: check_dependencies (55 行)
**建议**: 拆分为多个小方法
**预估时间**: 1.5 小时

### 🟡 long_method
**文件**: src\main.py:239
**问题**: 方法过长: start_modern_gui_app (68 行)
**建议**: 拆分为多个小方法
**预估时间**: 1.5 小时

### 🟡 long_method
**文件**: src\main.py:390
**问题**: 方法过长: main (132 行)
**建议**: 拆分为多个小方法
**预估时间**: 1.5 小时

### 🟡 hardcoded_import
**文件**: src\application\containers\main_container.py:10
**问题**: 硬编码导入: from src.core.interfaces.services import IGameAnalyzer, IAutomationService, IStateManager
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时

### 🟡 hardcoded_import
**文件**: src\application\containers\main_container.py:11
**问题**: 硬编码导入: from src.core.interfaces.repositories import IConfigRepository, ITemplateRepository
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时

### 🟡 hardcoded_import
**文件**: src\application\containers\main_container.py:12
**问题**: 硬编码导入: from src.core.interfaces.adapters import IWindowAdapter, IInputAdapter
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时

### 🟡 hardcoded_import
**文件**: src\application\containers\main_container.py:14
**问题**: 硬编码导入: from src.infrastructure.services.game_analyzer_service import GameAnalyzerService
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时

### 🟡 hardcoded_import
**文件**: src\application\containers\main_container.py:15
**问题**: 硬编码导入: from src.infrastructure.services.automation_service import AutomationService
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时

### 🟡 hardcoded_import
**文件**: src\application\containers\main_container.py:16
**问题**: 硬编码导入: from src.infrastructure.services.state_manager_service import StateManagerService
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时

### 🟡 hardcoded_import
**文件**: src\application\containers\main_container.py:17
**问题**: 硬编码导入: from src.infrastructure.repositories.config_repository import ConfigRepository
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时

### 🟡 hardcoded_import
**文件**: src\application\containers\main_container.py:18
**问题**: 硬编码导入: from src.infrastructure.repositories.template_repository import TemplateRepository
**建议**: 使用相对导入或依赖注入
**预估时间**: 0.5 小时
