# 背景
文件名：2025-01-25_1_remove_unnecessary_docker_fastapi.md
创建于：2025-01-25_15:30:00
创建者：Claude
主分支：main
任务分支：task/remove_unnecessary_docker_fastapi_2025-01-25_1
Yolo模式：Ask

# 任务描述
移除项目中不必要的Docker容器化配置和过度复杂的FastAPI微服务架构，简化项目为专注于桌面游戏自动化的核心功能。

# 项目概览
这是一个Windows桌面游戏自动化工具，主要功能包括：
- 游戏窗口捕获和图像识别
- 鼠标键盘自动化操作  
- PyQt6/PySide6图形界面
- 支持明日方舟、原神等游戏的自动化

项目当前存在过度工程化问题，引入了不匹配的企业级微服务架构。

⚠️ 警告：永远不要修改此部分 ⚠️
[此部分应包含核心RIPER-5协议规则的摘要，确保它们可以在整个执行过程中被引用]
⚠️ 警告：永远不要修改此部分 ⚠️

# 分析
## 技术冲突分析
1. **桌面应用特性冲突**：项目大量使用pyautogui、win32gui、pygetwindow等需要直接访问宿主机硬件的库，容器化会隔离这些关键的系统访问能力
2. **实际启动验证**：项目实际使用start.bat -> python run_in_venv.py -> python main.py启动，完全没有用到Docker
3. **Windows特定依赖**：项目深度依赖Windows API，不适合容器化
4. **过度复杂的微服务架构**：单用户桌面工具不需要PostgreSQL、Redis、Nginx、监控等企业级组件

## 可删除组件
- Docker配置文件：docker-compose.yml、Dockerfile、.dockerignore
- FastAPI微服务架构（可选择性保留简化版本）
- 企业级依赖：PostgreSQL、Redis、监控栈等
- 相关的配置和文档

# 提议的解决方案
## 方案A：完全移除Docker和简化FastAPI
- 删除所有Docker相关文件
- 保留基础FastAPI功能，移除企业级依赖
- 大幅简化requirements.txt
- 更新文档说明

## 方案B：完全移除Docker和FastAPI
- 删除所有Docker和FastAPI相关文件
- 专注于桌面应用核心功能
- 最大化简化项目结构

推荐方案A，保留基础API功能以备未来扩展需要。

# 当前执行步骤："3. 创建详细实施计划"

# 任务进度
[2025-01-25_15:30:00]
- 已创建：task/remove_unnecessary_docker_fastapi_2025-01-25_1分支
- 更改：创建任务文件
- 原因：开始项目简化重构
- 阻碍因素：无
- 状态：成功

[2025-01-25_16:15:00]
- 已修改：docker-compose.yml, Dockerfile, .dockerignore, STARTUP_GUIDE.md, requirements.txt, README.md, src/main.py
- 更改：完全移除Docker配置，简化依赖架构，更新文档说明
- 原因：移除过度复杂的微服务架构，专注桌面自动化核心功能
- 阻碍因素：无
- 状态：未确认

## 详细变更列表：
### 删除的文件：
- docker-compose.yml（已备份至legacy/docker_removed/）
- Dockerfile（已备份至legacy/docker_removed/）
- STARTUP_GUIDE.md（已备份至legacy/docker_removed/）

### 重构的文件：
- requirements.txt：移除117个依赖 → 约20个核心依赖
- README.md：更新架构说明，简化启动方式
- src/main.py：简化依赖检查逻辑

### 核心改进：
- 专注桌面自动化功能
- 移除PostgreSQL、Redis、监控栈等企业级组件
- 保留基础FastAPI功能（可选）
- 大幅提升启动速度和维护性

# 最终审查
[完成后的总结] 