# 背景
文件名：migration_implementation_20241220_1
创建于：2024-12-20_15:30:00
创建者：Claude
主分支：main
任务分支：task/migration_implementation_20241220_1
Yolo模式：Ask

# 任务描述
立即行动：实施类型统一迁移，将现有代码从多重定义的类型迁移到新的统一类型定义系统。

# 项目概览
游戏自动化系统存在多重类型定义问题，已创建统一类型定义系统，现需要将现有代码迁移到新系统。

⚠️ 警告：永远不要修改此部分 ⚠️
核心RIPER-5协议规则：
- 必须在每个响应开头声明模式
- EXECUTE模式必须100%忠实遵循计划
- REVIEW模式必须标记所有偏差
- 未经明确许可不能在模式间转换
- 代码修改必须完整且可立即运行
⚠️ 警告：永远不要修改此部分 ⚠️

# 分析
通过代码搜索发现以下关键文件仍在使用旧版本类型定义：

## 高优先级迁移文件（核心组件）：
1. `src/gui/main_window.py` - 主窗口，导入多个旧类型
2. `src/services/__init__.py` - 服务模块入口，导出旧GameState
3. `src/viewmodels/main_viewmodel.py` - 主视图模型，使用旧GameState
4. `src/core/__init__.py` - 核心模块，导出旧GameState

## 中优先级迁移文件（服务层）：
1. `src/services/auto_operator.py` - 自动操作器
2. `src/performance/performance_view.py` - 性能视图
3. `src/common/containers.py` - 容器配置
4. `src/models/game_automation_model.py` - 游戏自动化模型
5. `src/models/main_view_model.py` - 主视图模型

## 低优先级迁移文件（游戏适配器）：
1. `src/games/*/` - 各游戏适配器文件
2. `src/gui/dialogs/template_manager_dialog.py` - 模板管理对话框
3. `src/services/automation/auto_controller.py` - 自动控制器

# 提议的解决方案
采用渐进式迁移策略：

## 方案1：核心优先迁移（推荐）
- 优势：快速解决核心冲突，影响面最大
- 劣势：可能暂时破坏部分功能
- 适用：需要快速见效的情况

## 方案2：服务层优先迁移
- 优势：保持UI稳定，逐步迁移
- 劣势：迁移周期较长
- 适用：稳定性要求高的情况

## 方案3：全面并行迁移
- 优势：一次性解决所有问题
- 劣势：风险较高，测试工作量大
- 适用：有充足测试资源的情况

选择方案1：核心优先迁移

# 当前执行步骤："2. 制定详细实施计划"

## 详细实施计划

### 阶段1：核心服务模块迁移（P0优先级）

#### 步骤1：更新服务模块导出
- 文件：`src/services/__init__.py`
- 操作：将 `from .game_state import GameState` 替换为 `from src.core.types import UnifiedGameState as GameState`
- 理由：保持向后兼容性，同时使用统一类型

#### 步骤2：更新核心模块导出
- 文件：`src/core/__init__.py`
- 操作：将 `from .models.game_state import GameState` 替换为 `from .types import UnifiedGameState as GameState`
- 理由：统一核心模块的类型导出

### 阶段2：主要UI组件迁移（P0优先级）

#### 步骤3：更新主窗口导入
- 文件：`src/gui/main_window.py`
- 操作：
  - 替换 `from src.performance.performance_monitor import PerformanceMonitor, PerformanceMetrics` 为 `from src.core.types import UnifiedPerformanceMetrics as PerformanceMetrics`
  - 替换 `from src.services.image_processor import ImageProcessor, TemplateMatchResult` 为 `from src.core.types import UnifiedTemplateMatchResult as TemplateMatchResult`
  - 替换 `from src.services.game_state import GameState` 为 `from src.core.types import UnifiedGameState as GameState`
- 理由：主窗口是核心UI组件，影响整个应用

#### 步骤4：更新主视图模型
- 文件：`src/viewmodels/main_viewmodel.py`
- 操作：替换 `from src.services.game_state import GameState` 为 `from src.core.types import UnifiedGameState as GameState`
- 理由：视图模型是MVVM架构的核心

### 阶段3：业务逻辑组件迁移（P1优先级）

#### 步骤5：更新自动操作器
- 文件：`src/services/auto_operator.py`
- 操作：
  - 替换 `from src.services.game_state import GameState` 为 `from src.core.types import UnifiedGameState as GameState`
  - 替换 `from src.services.image_processor import ImageProcessor, TemplateMatchResult` 为 `from src.core.types import UnifiedTemplateMatchResult as TemplateMatchResult`
- 理由：自动操作器是核心业务逻辑

#### 步骤6：更新性能视图
- 文件：`src/performance/performance_view.py`
- 操作：替换 `from .performance_monitor import PerformanceMonitor, PerformanceMetrics` 为 `from src.core.types import UnifiedPerformanceMetrics as PerformanceMetrics`
- 理由：性能监控是重要功能

#### 步骤7：更新容器配置
- 文件：`src/common/containers.py`
- 操作：替换 `from src.services.game_state import GameState` 为 `from src.core.types import UnifiedGameState as GameState`
- 理由：容器配置影响依赖注入

### 阶段4：模型层迁移（P1优先级）

#### 步骤8：更新游戏自动化模型
- 文件：`src/models/game_automation_model.py`
- 操作：替换 `from src.services.game_state import GameState` 为 `from src.core.types import UnifiedGameState as GameState`
- 理由：模型层是数据处理核心

#### 步骤9：更新主视图模型（models目录）
- 文件：`src/models/main_view_model.py`
- 操作：替换 `from src.services.game_state import GameState` 为 `from src.core.types import UnifiedGameState as GameState`
- 理由：保持模型层一致性

### 验证和测试计划

#### 步骤10：运行基础测试
- 操作：执行 `python -m pytest tests/ -v` 验证基础功能
- 理由：确保迁移不破坏现有功能

#### 步骤11：启动应用测试
- 操作：运行 `python main.py` 验证应用启动
- 理由：确保UI正常工作

#### 步骤12：功能验证测试
- 操作：测试窗口管理、状态识别、性能监控等核心功能
- 理由：确保业务逻辑正常

# 任务进度
[2024-12-20_15:30:00]
- 已修改：.tasks/migration_implementation_20241220_1.md
- 更改：创建迁移实施任务文件
- 原因：制定详细的迁移计划和实施步骤
- 阻碍因素：无
- 状态：未确认

# 最终审查
[待完成]