"""
FastAPI应用主入口文件
遵循最佳实践配置，支持微服务架构
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.routers import (
    auth_router,
    games_router,
    vision_router,
    automation_router,
    health_router,
    websocket_router
)
from src.core.config import get_settings
from src.core.container import get_container
from src.core.database import database_manager
from src.core.exceptions import GameAutomationException
from src.core.logging import setup_logging
from src.core.middleware import (
    LoggingMiddleware,
    MetricsMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware
)


# 设置日志
setup_logging()
logger = logging.getLogger(__name__)

# 获取配置
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚀 启动游戏自动化服务...")
    
    try:
        # 初始化依赖注入容器
        container = get_container()
        await container.init_resources()
        
        # 初始化数据库连接
        await database_manager.connect()
        
        # 初始化缓存连接
        cache_service = container.cache_service()
        await cache_service.connect()
        
        # 初始化AI Agent系统
        agent_service = container.agent_service()
        await agent_service.initialize()
        
        logger.info("✅ 服务启动完成")
        yield
        
    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        raise
    finally:
        # 清理资源
        logger.info("🔄 正在关闭服务...")
        
        try:
            await database_manager.disconnect()
            cache_service = container.cache_service()
            await cache_service.disconnect()
            await container.shutdown()
            logger.info("✅ 服务关闭完成")
        except Exception as e:
            logger.error(f"❌ 服务关闭异常: {e}")


def create_application() -> FastAPI:
    """创建FastAPI应用实例"""
    
    # 根据环境配置OpenAPI文档
    app_configs: Dict[str, Any] = {
        "title": "游戏自动化平台 API",
        "description": """
        ## 🎮 现代化游戏自动化平台

        ### 功能特性
        - 🤖 AI智能决策系统
        - 🔍 高精度图像识别
        - ⚡ 实时动作执行
        - 📊 性能监控
        - 🔐 安全认证

        ### 支持的游戏
        - 明日方舟 (Arknights)
        - 原神 (Genshin Impact)
        - 崩坏：星穹铁道 (Honkai: Star Rail)
        - 绝区零 (Zenless Zone Zero)
        """,
        "version": settings.APP_VERSION,
        "contact": {
            "name": "游戏自动化团队",
            "email": "support@gameauto.com"
        },
        "license_info": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        },
        "lifespan": lifespan
    }
    
    # 在生产环境隐藏文档
    if settings.ENVIRONMENT == "production":
        app_configs.update({
            "openapi_url": None,
            "docs_url": None,
            "redoc_url": None
        })
    
    app = FastAPI(**app_configs)
    
    # 注册中间件
    setup_middleware(app)
    
    # 注册路由
    setup_routers(app)
    
    # 注册异常处理器
    setup_exception_handlers(app)
    
    return app


def setup_middleware(app: FastAPI) -> None:
    """配置中间件"""
    
    # 安全中间件
    app.add_middleware(SecurityMiddleware)
    
    # 可信主机中间件
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.TRUSTED_HOSTS
    )
    
    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_origin_regex=settings.CORS_ORIGINS_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=settings.CORS_HEADERS,
    )
    
    # 限流中间件
    app.add_middleware(RateLimitMiddleware)
    
    # 指标收集中间件
    app.add_middleware(MetricsMiddleware)
    
    # 请求日志中间件
    app.add_middleware(LoggingMiddleware)


def setup_routers(app: FastAPI) -> None:
    """配置路由"""
    
    # API v1 路由
    API_V1_PREFIX = "/api/v1"
    
    # 健康检查路由 (无前缀)
    app.include_router(health_router, tags=["健康检查"])
    
    # 认证路由
    app.include_router(
        auth_router,
        prefix=f"{API_V1_PREFIX}/auth",
        tags=["认证授权"]
    )
    
    # 游戏管理路由
    app.include_router(
        games_router,
        prefix=f"{API_V1_PREFIX}/games",
        tags=["游戏管理"]
    )
    
    # 视觉处理路由
    app.include_router(
        vision_router,
        prefix=f"{API_V1_PREFIX}/vision",
        tags=["视觉处理"]
    )
    
    # 自动化控制路由
    app.include_router(
        automation_router,
        prefix=f"{API_V1_PREFIX}/automation",
        tags=["自动化控制"]
    )
    
    # WebSocket路由
    app.include_router(
        websocket_router,
        prefix="/ws",
        tags=["实时通信"]
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """配置异常处理器"""
    
    @app.exception_handler(GameAutomationException)
    async def game_automation_exception_handler(
        request: Request, 
        exc: GameAutomationException
    ) -> JSONResponse:
        """处理自定义业务异常"""
        logger.error(f"业务异常: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": exc.__class__.__name__,
                    "message": exc.message,
                    "code": exc.error_code,
                    "details": exc.details
                },
                "timestamp": exc.timestamp.isoformat(),
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, 
        exc: HTTPException
    ) -> JSONResponse:
        """处理HTTP异常"""
        logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "HTTPException",
                    "message": exc.detail,
                    "code": exc.status_code
                },
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, 
        exc: RequestValidationError
    ) -> JSONResponse:
        """处理请求验证异常"""
        logger.warning(f"请求验证失败: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "type": "ValidationError",
                    "message": "请求数据验证失败",
                    "details": exc.errors()
                },
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, 
        exc: Exception
    ) -> JSONResponse:
        """处理未捕获的异常"""
        logger.error(f"未处理异常: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "type": "InternalServerError",
                    "message": "服务器内部错误" if settings.ENVIRONMENT == "production" else str(exc)
                },
                "path": str(request.url.path)
            }
        )


# 创建应用实例
app = create_application()


@app.get("/", include_in_schema=False)
async def root():
    """根路径重定向到文档"""
    return JSONResponse({
        "message": "🎮 游戏自动化平台 API",
        "version": settings.APP_VERSION,
        "docs_url": "/docs" if settings.ENVIRONMENT != "production" else None,
        "health_check": "/health"
    })


if __name__ == "__main__":
    import sys
    from pathlib import Path
    import uvicorn
    
    # 添加项目根目录到Python路径
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    # 开发环境启动配置
    uvicorn.run(
        app,  # 直接传递app对象而不是字符串
        host="0.0.0.0",
        port=8000,
        reload=False,  # 直接运行时禁用reload
        log_level="info"
    ) 