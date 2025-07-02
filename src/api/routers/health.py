"""
健康检查路由
提供系统状态监控和依赖服务检查
"""

import asyncio
import logging
import time
from typing import Dict, Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.core.container import get_container
from src.core.database import database_manager
from src.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    timestamp: float
    version: str
    environment: str
    services: Dict[str, Any]
    uptime: float


class ServiceStatus(BaseModel):
    """服务状态模型"""
    status: str
    response_time_ms: float
    details: Dict[str, Any] = {}


async def check_database() -> ServiceStatus:
    """检查数据库连接状态"""
    start_time = time.time()
    
    try:
        # 执行简单查询测试连接
        async with database_manager.get_session() as session:
            result = await session.execute("SELECT 1")
            await result.fetchone()
        
        response_time = (time.time() - start_time) * 1000
        return ServiceStatus(
            status="healthy",
            response_time_ms=round(response_time, 2),
            details={
                "url": str(database_manager.engine.url).replace(
                    database_manager.engine.url.password, "***"
                ) if database_manager.engine.url.password else str(database_manager.engine.url),
                "pool_size": database_manager.engine.pool.size(),
                "checked_out": database_manager.engine.pool.checkedout()
            }
        )
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"数据库健康检查失败: {e}")
        return ServiceStatus(
            status="unhealthy",
            response_time_ms=round(response_time, 2),
            details={"error": str(e)}
        )


async def check_redis() -> ServiceStatus:
    """检查Redis连接状态"""
    start_time = time.time()
    
    try:
        container = get_container()
        cache_service = container.cache_service()
        
        # 测试Redis连接
        await cache_service.ping()
        
        response_time = (time.time() - start_time) * 1000
        return ServiceStatus(
            status="healthy",
            response_time_ms=round(response_time, 2),
            details={
                "url": cache_service.get_connection_info()
            }
        )
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"Redis健康检查失败: {e}")
        return ServiceStatus(
            status="unhealthy",
            response_time_ms=round(response_time, 2),
            details={"error": str(e)}
        )


async def check_ai_agents() -> ServiceStatus:
    """检查AI Agent系统状态"""
    start_time = time.time()
    
    try:
        container = get_container()
        agent_service = container.agent_service()
        
        # 检查Agent服务状态
        agent_status = await agent_service.health_check()
        
        response_time = (time.time() - start_time) * 1000
        return ServiceStatus(
            status="healthy" if agent_status["available"] else "degraded",
            response_time_ms=round(response_time, 2),
            details=agent_status
        )
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"AI Agent健康检查失败: {e}")
        return ServiceStatus(
            status="unhealthy",
            response_time_ms=round(response_time, 2),
            details={"error": str(e)}
        )


async def check_vision_service() -> ServiceStatus:
    """检查视觉服务状态"""
    start_time = time.time()
    
    try:
        container = get_container()
        vision_service = container.vision_service()
        
        # 检查视觉服务状态
        vision_status = await vision_service.health_check()
        
        response_time = (time.time() - start_time) * 1000
        return ServiceStatus(
            status="healthy" if vision_status["available"] else "degraded",
            response_time_ms=round(response_time, 2),
            details=vision_status
        )
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"视觉服务健康检查失败: {e}")
        return ServiceStatus(
            status="unhealthy",
            response_time_ms=round(response_time, 2),
            details={"error": str(e)}
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="系统健康检查",
    description="检查系统及所有依赖服务的健康状态"
)
async def health_check() -> HealthResponse:
    """
    系统健康检查端点
    
    返回系统整体状态和各个服务的详细状态信息
    """
    start_time = time.time()
    
    # 并行检查所有服务
    db_check, redis_check, ai_check, vision_check = await asyncio.gather(
        check_database(),
        check_redis(),
        check_ai_agents(),
        check_vision_service(),
        return_exceptions=True
    )
    
    # 处理异常
    services = {}
    
    if isinstance(db_check, Exception):
        services["database"] = ServiceStatus(
            status="error",
            response_time_ms=0,
            details={"error": str(db_check)}
        )
    else:
        services["database"] = db_check
    
    if isinstance(redis_check, Exception):
        services["redis"] = ServiceStatus(
            status="error", 
            response_time_ms=0,
            details={"error": str(redis_check)}
        )
    else:
        services["redis"] = redis_check
    
    if isinstance(ai_check, Exception):
        services["ai_agents"] = ServiceStatus(
            status="error",
            response_time_ms=0,
            details={"error": str(ai_check)}
        )
    else:
        services["ai_agents"] = ai_check
    
    if isinstance(vision_check, Exception):
        services["vision"] = ServiceStatus(
            status="error",
            response_time_ms=0,
            details={"error": str(vision_check)}
        )
    else:
        services["vision"] = vision_check
    
    # 计算总体状态
    statuses = [service.status for service in services.values()]
    if "unhealthy" in statuses or "error" in statuses:
        overall_status = "unhealthy"
    elif "degraded" in statuses:
        overall_status = "degraded"
    else:
        overall_status = "healthy"
    
    return HealthResponse(
        status=overall_status,
        timestamp=time.time(),
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        services={name: service.dict() for name, service in services.items()},
        uptime=time.time() - start_time
    )


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    summary="存活检查",
    description="简单的存活检查，用于负载均衡器检测"
)
async def liveness_check():
    """
    存活检查端点
    
    用于Kubernetes liveness probe或负载均衡器检测
    """
    return {"status": "alive", "timestamp": time.time()}


@router.get(
    "/health/ready", 
    status_code=status.HTTP_200_OK,
    summary="就绪检查",
    description="检查服务是否准备好接收流量"
)
async def readiness_check():
    """
    就绪检查端点
    
    用于Kubernetes readiness probe，检查关键服务是否可用
    """
    try:
        # 检查关键服务
        db_task = asyncio.create_task(check_database())
        redis_task = asyncio.create_task(check_redis())
        
        db_result, redis_result = await asyncio.gather(
            db_task, redis_task, return_exceptions=True
        )
        
        # 如果关键服务不可用则返回503
        if (isinstance(db_result, Exception) or db_result.status == "unhealthy" or
            isinstance(redis_result, Exception) or redis_result.status == "unhealthy"):
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "not_ready", "timestamp": time.time()}
            )
        
        return {"status": "ready", "timestamp": time.time()}
        
    except Exception as e:
        logger.error(f"就绪检查失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "error": str(e), "timestamp": time.time()}
        ) 