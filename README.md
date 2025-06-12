# 游戏自动操作工具

基于Python的游戏自动化工具，使用图像识别和强化学习技术实现游戏自动化操作。

## 功能特点

- 多引擎游戏画面捕获系统，自动选择最合适的捕获方式
- 基于OpenCV的图像识别和目标检测
- 智能鼠标键盘操作模拟
- 基于DQN的强化学习模型
- 现代化的PyQt6图形界面
- 模块化设计和依赖注入架构
- 自定义规则系统和决策逻辑
- 状态历史记录和分析功能

## 系统要求

- Python 3.8 或更高版本
- Windows 10/11 系统（目前主要支持Windows平台）
- 最小内存要求：4GB RAM
- 显卡：如使用CUDA加速，需要支持CUDA的NVIDIA显卡

## 快速开始

1. 双击 `start.bat` 文件运行程序
   - 脚本会自动检查Python安装情况
   - 自动创建虚拟环境并安装依赖
   - 确保程序运行在虚拟环境中，避免系统Python环境污染

2. 如需清理环境：
   - 双击 `clean.bat` 文件选择清理模式
   - 模式1: 仅清理虚拟环境和本地缓存文件
   - 模式2: 全面清理，包括检查并清理系统Python环境中的相关库
   - 清理后可以打包整个文件夹进行迁移

3. 系统Python环境清理（根据需要选择以下工具）：
   - **标准版**：双击 `clean_system.bat` 清理系统环境中的冲突库
   - **免管理员版**：双击 `clean_system_noadmin.bat` 在普通权限下尝试清理
   - **管理员版**：右键 `clean_system_admin.bat` 选择"以管理员身份运行"，此工具采用强力清理模式
   - 如果清理后仍有问题，建议重启计算机后再次运行清理工具
   - 清理顺序建议：先尝试标准版 > 如果失败则尝试免管理员版 > 如果都失败则使用管理员版

## 手动安装

如果自动脚本未能正常工作，可以按以下步骤手动安装：

1. 克隆项目代码：
```bash
git clone https://github.com/yourusername/game-automation-tool.git
cd game-automation-tool
```

2. 创建虚拟环境：
```bash
python -m venv venv
venv\Scripts\activate
```

3. 安装依赖包：
```bash
pip install -r requirements.txt
```

4. 运行主程序：
```bash
python src/main.py
```

## 使用说明

1. 在图形界面中：
   - 点击"刷新窗口"获取当前运行的游戏窗口列表
   - 从下拉菜单选择目标游戏窗口
   - 点击"选择窗口"确认选择
   - 调整自动化参数（如速度、分析模式等）
   - 点击"开始"按钮启动自动操作

2. 高级使用：
   - 可在`settings.json`中调整配置参数
   - 可自定义规则和行为模式
   - 状态历史视图可查看运行统计和趋势

## 项目架构

本项目采用MVVM（Model-View-ViewModel）架构模式和依赖注入设计，主要组件如下：

### 架构概览
```
src/
├── main.py                 # 程序入口
├── main_window.py          # 主窗口定义
├── views/                  # 视图层
├── viewmodels/             # 视图模型层
├── models/                 # 数据模型层
├── services/               # 核心服务
│   ├── auto_operator.py    # 自动操作服务
│   ├── window_manager.py   # 窗口管理服务
│   ├── capture_engines.py  # 多引擎捕获系统
│   ├── image_processor.py  # 图像处理服务
│   ├── game_analyzer.py    # 游戏分析服务
│   ├── action_simulator.py # 操作模拟服务
│   ├── game_state.py       # 游戏状态服务
│   ├── dqn_agent.py        # 强化学习代理
│   ├── logger.py           # 日志服务
│   └── config.py           # 配置服务
├── common/                 # 通用组件
│   ├── containers.py       # 依赖注入容器
│   ├── recovery.py         # 错误恢复系统
│   └── system_initializer.py # 系统初始化器
└── resources/              # 资源文件
```

### 核心服务
- **依赖注入容器**: 管理服务依赖和生命周期
- **窗口管理器**: 捕获和操作游戏窗口
- **多引擎捕获系统**: 包含多种捕获引擎，自动选择最合适的捕获方式
  - GDI引擎: 使用Windows GDI进行窗口捕获，适用于大多数应用
  - DXGI引擎: 基于DirectX的游戏画面捕获，适用于全屏游戏
  - MSS引擎: 基于MSS库的屏幕捕获，作为备选方案
  - 进程内存引擎: 基于进程内存的画面获取，作为最终兜底方案
- **图像处理器**: 图像处理和目标识别
- **游戏分析器**: 游戏状态分析和决策
- **动作模拟器**: 模拟鼠标键盘操作
- **自动操作器**: 基于规则的游戏自动化逻辑
- **游戏状态管理**: 管理游戏状态和转换
- **错误恢复系统**: 智能处理错误并实现自动恢复

## 配置文件

主要配置文件位于`settings.json`，包含以下关键配置：

- **window**: 窗口捕获设置
- **image**: 图像处理参数
- **action**: 操作模拟参数
- **analysis**: 游戏分析参数
- **logging**: 日志记录设置

## 开发指南

如需扩展功能，可以：
1. 添加新的游戏分析规则到`game_analyzer.py`
2. 扩展操作规则到`auto_operator.py`
3. 添加新的UI组件到`views/`目录
4. 创建新的捕获引擎到`capture_engines.py`

## 注意事项

- 请确保遵守游戏的服务条款和使用规定
- 建议仅在单人游戏或测试环境中使用
- 自动化操作可能导致高CPU和内存使用
- 对于复杂游戏场景，可能需要调整分析参数

## 许可证

MIT License 