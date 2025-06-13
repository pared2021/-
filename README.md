# 🎮 游戏自动化工具

> 基于现代化分层架构的Python游戏自动化工具，集成图像识别、强化学习和智能决策技术

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Architecture](https://img.shields.io/badge/Architecture-四层分层-green.svg)](#架构概览)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 功能特点

### 🏗️ 现代化架构
- **四层分层架构**: Core/Services/Common/UI，职责清晰，易于维护
- **智能依赖注入**: 自动管理组件依赖和生命周期
- **优雅错误处理**: 分层异常体系，智能恢复机制
- **高度模块化**: 100%职责纯度，支持独立开发和测试

### 🎯 核心功能
- **统一游戏分析器**: 融合传统图像处理和深度学习技术
- **多引擎画面捕获**: 自动选择最合适的捕获方式（GDI/DXGI/MSS）
- **智能动作模拟**: 高精度鼠标键盘操作，支持随机化
- **强化学习决策**: 基于DQN的智能游戏策略
- **实时状态监控**: 游戏状态分析和历史记录
- **错误自动恢复**: 智能检测问题并自动修复

### 🖥️ 用户体验
- **现代化UI**: 基于PyQt6的响应式图形界面
- **快速启动**: 一键启动脚本，自动环境配置
- **配置灵活**: 支持JSON配置和运行时调整
- **开发友好**: 完整的文档和清晰的代码结构

## 🏗️ 架构概览

本项目采用现代化的**四层分层架构**，经过系统性重构优化：

```
┌─────────────────────────────────────────┐
│                UI 层                    │  🖥️ 用户界面
│  ┌─────────────────────────────────────┐│
│  │     windows │ widgets │ panels     ││  界面组件
│  │  viewmodels │ styles  │ editors    ││  交互逻辑
│  └─────────────────────────────────────┘│
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│               Core 层                   │  🎯 核心业务逻辑
│  ┌─────────────────────────────────────┐│
│  │   analyzers │ engines  │ executors ││  业务组件
│  │  collectors │ models   │ automation││  数据和逻辑
│  └─────────────────────────────────────┘│
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│             Services 层                 │  🔧 基础服务
│  ┌─────────────────────────────────────┐│
│  │    config   │ logger  │  window    ││  技术服务
│  │image_processor│action_simulator     ││  基础功能
│  └─────────────────────────────────────┘│
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│             Common 层                   │  🔗 通用基础设施
│  ┌─────────────────────────────────────┐│
│  │ container │ recovery │ exceptions  ││  基础设施
│  │initializer│ monitor  │ app_utils   ││  系统支持
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

### 依赖关系
```
UI → Core → Services → Common
     ↑       ↑
   Models  Utils
```

## 📁 目录结构

经过重构优化的清晰目录结构：

```
📦 游戏自动化工具/
├── 📁 src/                     # 源代码根目录
│   ├── 📁 core/                # 🎯 核心业务逻辑层
│   │   ├── 📄 unified_game_analyzer.py  # 统一游戏分析器
│   │   ├── 📄 task_system.py            # 任务系统
│   │   ├── 📄 state_machine.py          # 状态机
│   │   ├── 📁 analyzers/               # 分析器组件
│   │   ├── 📁 engines/                 # 决策引擎（含DQN）
│   │   ├── 📁 executors/               # 执行器组件
│   │   ├── 📁 collectors/              # 数据收集器
│   │   ├── 📁 models/                  # 业务数据模型
│   │   └── 📁 automation/              # 自动化逻辑
│   ├── 📁 services/            # 🔧 基础服务层
│   │   ├── 📄 config.py                # 配置管理服务
│   │   ├── 📄 logger.py                # 日志记录服务
│   │   ├── 📄 window_manager.py        # 窗口管理服务
│   │   ├── 📄 image_processor.py       # 图像处理服务
│   │   ├── 📄 action_simulator.py      # 动作模拟服务
│   │   ├── 📄 template_collector.py    # 模板收集服务
│   │   ├── 📄 capture_engines.py       # 多引擎捕获系统
│   │   └── 📄 game_analyzer.py         # 游戏分析适配器
│   ├── 📁 common/              # 🔗 通用基础设施层
│   │   ├── 📄 containers.py            # 依赖注入容器
│   │   ├── 📄 recovery.py              # 错误恢复机制
│   │   ├── 📄 system_initializer.py    # 系统初始化器
│   │   ├── 📄 exceptions.py            # 通用异常基类
│   │   ├── 📄 error_handler.py         # 错误处理器
│   │   └── 📄 monitor.py               # 系统监控
│   ├── 📁 ui/                  # 🖥️ 用户界面层
│   │   ├── 📁 windows/                 # 窗口组件
│   │   ├── 📁 widgets/                 # 控件组件
│   │   ├── 📁 panels/                  # 面板组件
│   │   ├── 📁 viewmodels/              # 视图模型
│   │   ├── 📁 styles/                  # 界面样式
│   │   └── 📁 editors/                 # 编辑器组件
│   ├── 📁 utils/               # 🛠️ 工具函数
│   │   ├── 📁 performance/             # 性能优化工具
│   │   ├── 📁 ocr/                     # OCR识别工具
│   │   └── 📁 recorders/               # 操作录制工具
│   ├── 📁 legacy/              # 📦 向后兼容
│   ├── 📁 resources/           # 📁 资源文件
│   ├── 📁 tests/               # 🧪 测试代码
│   └── 📄 main.py              # 程序主入口
├── 📄 start.bat                # 🚀 一键启动脚本
├── 📄 clean.bat                # 🧹 环境清理脚本
├── 📄 requirements.txt         # 📋 Python依赖
├── 📄 README.md               # 📖 项目说明
└── 📄 settings.json           # ⚙️ 配置文件
```

## 🚀 快速开始

### 方式一：一键启动（推荐）

1. **运行启动脚本**：
   ```bash
   # Windows
   双击 start.bat
   
   # 或手动执行
   start.bat
   ```

2. **脚本自动处理**：
   - ✅ 检查Python环境
   - ✅ 创建虚拟环境
   - ✅ 安装项目依赖
   - ✅ 启动主程序

### 方式二：手动安装

1. **克隆项目**：
   ```bash
   git clone https://github.com/yourusername/game-automation-tool.git
   cd game-automation-tool
   ```

2. **创建虚拟环境**：
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

4. **启动程序**：
   ```bash
   python src/main.py
   ```

## 💡 使用示例

### 基本使用流程

1. **选择游戏窗口**：
   ```
   启动程序 → 点击"刷新窗口" → 选择目标游戏 → 确认选择
   ```

2. **配置自动化参数**：
   ```
   调整分析模式 → 设置操作速度 → 配置检测阈值
   ```

3. **开始自动化**：
   ```
   点击"开始" → 实时监控状态 → 查看执行结果
   ```

### 高级配置

编辑 `settings.json` 自定义配置：

```json
{
  "window": {
    "screenshot_interval": 0.1,
    "activation_delay": 0.5
  },
  "analysis": {
    "confidence_threshold": 0.8,
    "detection_mode": "unified"
  },
  "automation": {
    "speed_factor": 1.0,
    "random_delay": true
  }
}
```

## 🔧 核心组件详解

### 统一游戏分析器
```python
from src.core.unified_game_analyzer import UnifiedGameAnalyzer

# 自动检测最佳分析技术
analyzer = UnifiedGameAnalyzer(
    logger=logger,
    image_processor=image_processor,
    config=config
)

# 分析游戏画面
result = analyzer.analyze_frame(frame)
```

### 智能依赖注入
```python
from src.common.containers import DIContainer

# 容器自动管理所有依赖
container = DIContainer()
container.initialize()

# 获取任何服务
game_analyzer = container.get('GameAnalyzer')
window_manager = container.get('GameWindowManager')
```

### 错误恢复机制
```python
from src.common.recovery import RecoveryManager

# 自动错误恢复
recovery = RecoveryManager(logger)
recovery.add_default_handlers()

# 智能处理异常
try:
    # 可能出错的操作
    risky_operation()
except Exception as e:
    recovery.handle_error(e)  # 自动恢复
```

## 🔧 系统要求

### 运行环境
- **Python**: 3.8+ （推荐 3.9+）
- **操作系统**: Windows 10/11 （主要支持平台）
- **内存**: 最小 4GB RAM （推荐 8GB+）
- **显卡**: 可选CUDA支持的NVIDIA显卡（加速推理）

### Python依赖
```
# 核心依赖
opencv-python>=4.5.0
numpy>=1.20.0
PyQt6>=6.0.0

# 可选依赖（智能检测）
torch>=1.9.0  # 深度学习（可选）
torchvision   # 计算机视觉（可选）
```

## 🤝 开发指南

### 添加新功能

1. **核心业务逻辑** → `src/core/`
   ```python
   # 添加新的游戏分析规则
   src/core/analyzers/my_analyzer.py
   ```

2. **基础服务** → `src/services/`
   ```python
   # 添加新的技术服务
   src/services/my_service.py
   ```

3. **UI组件** → `src/ui/`
   ```python
   # 添加新的界面组件
   src/ui/widgets/my_widget.py
   ```

### 代码规范

- **分层原则**: 遵循UI→Core→Services→Common的依赖方向
- **职责单一**: 每个组件只负责一个明确的职责
- **接口清晰**: 使用依赖注入和清晰的接口定义
- **错误处理**: 使用分层异常体系和恢复机制

### 测试运行

```bash
# 运行架构验证测试
python src/tests/directory_refactor_test.py

# 运行职责分配测试  
python src/tests/service_responsibility_test.py

# 运行功能测试
python src/tests/functional_test.py
```

## 📚 文档资源

- **架构设计**: [docs/architecture.md](docs/architecture.md)
- **开发者指南**: [docs/developer-guide.md](docs/developer-guide.md)
- **API文档**: [docs/api/](docs/api/)
- **配置指南**: [docs/configuration.md](docs/configuration.md)

## 🎯 重构成果

经过系统性重构，项目实现了：

### 架构优化
- ✅ **目录简化**: 20+个分散目录 → 10个清晰主目录
- ✅ **职责纯度**: 各层达到100%职责单一性
- ✅ **代码重复**: 消除80%+的重复实现
- ✅ **依赖关系**: 建立清晰的单向依赖流

### 开发体验
- ✅ **查找功能**: 明确知道功能在哪个层次
- ✅ **添加功能**: 清楚应该在哪里添加代码  
- ✅ **问题定位**: 快速找到对应的责任层次
- ✅ **团队协作**: 职责边界清晰，减少冲突

## ⚠️ 注意事项

### 使用须知
- 🎮 请遵守游戏服务条款和使用规定
- 🧪 建议在单人游戏或测试环境中使用
- 💻 自动化可能导致较高的CPU和内存使用
- ⚙️ 复杂场景可能需要调整分析参数

### 环境清理
如遇到环境问题，可使用清理脚本：
```bash
clean.bat              # 清理虚拟环境
clean_system.bat       # 清理系统Python环境
clean_system_admin.bat # 管理员权限深度清理
```

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

<div align="center">

**🚀 从意大利面条式代码到现代化分层架构的华丽转变！**

[![GitHub](https://img.shields.io/badge/GitHub-项目主页-blue?logo=github)](https://github.com/yourusername/game-automation-tool)
[![Docs](https://img.shields.io/badge/Docs-文档中心-green?logo=gitbook)](docs/)
[![Support](https://img.shields.io/badge/Support-技术支持-orange?logo=stackoverflow)](https://github.com/yourusername/game-automation-tool/issues)

</div> 