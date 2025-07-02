"""
中间件模块
包含安全、日志、限流和指标收集中间件
"""

import time
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 添加安全头
        response = await call_next(request)
        
        # 安全响应头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 记录请求信息
        logger.info(
            f"请求开始: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            }
        )
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录响应信息
        logger.info(
            f"请求完成: {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time,
                "client_ip": request.client.host if request.client else None
            }
        )
        
        # 添加处理时间头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """指标收集中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.request_duration_sum = 0.0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 计数请求
        self.request_count += 1
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        duration = time.time() - start_time
        self.request_duration_sum += duration
        
        # TODO: 发送指标到监控系统
        # 这里可以集成Prometheus等监控系统
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.requests = {}  # 简单的内存限流，生产环境应使用Redis
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 获取客户端IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 简单的内存限流实现
        current_time = time.time()
        
        # 清理过期记录
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < 60  # 1分钟窗口
            ]
        else:
            self.requests[client_ip] = []
        
        # 检查限流
        if len(self.requests[client_ip]) >= 100:  # 每分钟100次请求
            logger.warning(f"限流触发: {client_ip}")
            return Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=429,
                headers={"Content-Type": "application/json"}
            )
        
        # 记录请求
        self.requests[client_ip].append(current_time)
        
        return await call_next(request)


__all__ = [
    "SecurityMiddleware",
    "LoggingMiddleware", 
    "MetricsMiddleware",
    "RateLimitMiddleware"
] 