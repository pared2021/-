# syntax=docker/dockerfile:1

# ================================
# 开发阶段 - 包含开发工具
# ================================
FROM python:3.11-slim AS development

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    pkg-config \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libglib2.0-dev \
    libgtk-3-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制开发依赖文件
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# ================================
# 构建阶段 - 安装生产依赖
# ================================
FROM development AS builder

# 复制生产依赖文件
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 创建虚拟环境并安装依赖
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# ================================
# 生产阶段 - 最小化镜像
# ================================
FROM python:3.11-slim AS production

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    zlib1g \
    libjpeg62-turbo \
    libpng16-16 \
    libglib2.0-0 \
    libgtk-3-0 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 创建非root用户
RUN groupadd -r gameauto && useradd --no-log-init -r -g gameauto gameauto

# 复制应用代码
COPY --chown=gameauto:gameauto src/ ./src/
COPY --chown=gameauto:gameauto config.json ./
COPY --chown=gameauto:gameauto settings.json ./
COPY --chown=gameauto:gameauto pyproject.toml ./

# 创建必要的目录
RUN mkdir -p logs screenshots templates data && \
    chown -R gameauto:gameauto logs screenshots templates data

# 切换到非root用户
USER gameauto

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"] 