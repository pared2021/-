# 🚀 游戏自动化平台启动指南

## 📋 系统要求

- **Python**: 3.11+
- **操作系统**: Windows 10/11 (推荐)
- **内存**: 4GB+ (推荐8GB+)
- **硬盘**: 2GB+ 可用空间

## 🛠️ 快速启动

### 1. 安装依赖
```bash
# 安装生产依赖
pip install -r requirements.txt

# 开发环境额外安装
pip install -r requirements-dev.txt
```

### 2. 环境配置
复制并配置环境变量：
```bash
# 复制环境模板
cp .env.template .env

# 编辑配置文件
notepad .env
```

**重要配置项**：
- `OPENAI_API_KEY`: OpenAI API密钥 (用于AI Agent功能)
- `DATABASE_URL`: PostgreSQL数据库连接
- `REDIS_URL`: Redis缓存连接

### 3. 启动服务

#### 🐳 Docker方式 (推荐)
```bash
# 启动完整服务栈
docker-compose up -d

# 开发环境
docker-compose --profile dev up -d

# 包含监控
docker-compose --profile monitoring up -d
```

#### 🐍 直接Python方式
```bash
# 启动FastAPI服务器
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# 或者直接运行
python src/api/main.py
```

## 🌐 访问服务

启动成功后可以访问：

- **API文档**: http://localhost:8000/docs
- **API首页**: http://localhost:8000/
- **健康检查**: http://localhost:8000/health
- **监控面板**: http://localhost:3000 (Grafana, 如果启用)

## 🔍 验证安装

运行内置验证脚本：
```bash
python -c "from src.api.main import app; print('✅ 应用启动成功!')"
```

## 📊 核心架构

### 🏗️ 微服务架构
- **API服务** (FastAPI): RESTful API和WebSocket
- **数据库** (PostgreSQL): 持久化存储
- **缓存** (Redis): 高性能缓存
- **AI Agent**: 智能决策系统

### 🛣️ 主要API路由
```
GET  /health              # 健康检查
GET  /api/v1/games/       # 游戏管理
POST /api/v1/vision/      # 视觉处理
POST /api/v1/automation/  # 自动化控制
POST /api/v1/auth/        # 认证授权
```

## 🎮 支持的游戏

- **明日方舟** (Arknights)
- **原神** (Genshin Impact) 
- **崩坏：星穹铁道** (Honkai: Star Rail)
- **绝区零** (Zenless Zone Zero)

## 🔧 开发模式

### 启动开发服务器
```bash
# 自动重载模式
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 调试模式
python -m debugpy --listen 5678 --wait-for-client src/api/main.py
```

### 运行测试
```bash
# 单元测试
pytest tests/

# 覆盖率测试
pytest --cov=src tests/
```

## 🐛 故障排除

### 常见问题

**1. 模块导入错误**
```bash
# 确保在项目根目录运行
cd /path/to/project
python -m uvicorn src.api.main:app
```

**2. 端口占用**
```bash
# 检查端口使用
netstat -an | findstr :8000

# 或更改端口
uvicorn src.api.main:app --port 8001
```

**3. 依赖问题**
```bash
# 重新安装依赖
pip install --force-reinstall -r requirements.txt
```

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# Docker日志
docker-compose logs -f app
```

## 📚 更多资源

- **API文档**: http://localhost:8000/docs
- **项目文档**: `docs/` 目录
- **架构说明**: `docs/architecture.md`
- **开发指南**: `docs/developer-guide.md`

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

---

**🎉 现在您的游戏自动化平台已准备就绪！开始您的AI驱动游戏自动化之旅吧！** 