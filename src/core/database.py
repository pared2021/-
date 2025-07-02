"""
数据库管理模块
提供异步数据库连接和会话管理
"""

import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[sessionmaker] = None
        self._connected = False
    
    async def connect(self) -> None:
        """连接数据库"""
        if self._connected:
            logger.warning("数据库已连接")
            return
        
        try:
            # 创建异步引擎
            self.engine = create_async_engine(
                str(settings.DATABASE_URL),
                echo=settings.DATABASE_ECHO,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                pool_timeout=settings.DATABASE_POOL_TIMEOUT,
                pool_recycle=settings.DATABASE_POOL_RECYCLE,
                poolclass=StaticPool if "sqlite" in str(settings.DATABASE_URL) else None,
            )
            
            # 创建会话工厂
            self.session_factory = sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                autoflush=False,
                autocommit=False,
            )
            
            self._connected = True
            logger.info("数据库连接成功")
            
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    async def disconnect(self) -> None:
        """断开数据库连接"""
        if not self._connected:
            logger.warning("数据库未连接")
            return
        
        try:
            if self.engine:
                await self.engine.dispose()
                self.engine = None
            
            self.session_factory = None
            self._connected = False
            
            logger.info("数据库连接已关闭")
            
        except Exception as e:
            logger.error(f"数据库断开失败: {e}")
            raise
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话"""
        if not self._connected or not self.session_factory:
            raise RuntimeError("数据库未连接")
        
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """数据库健康检查"""
        if not self._connected:
            return False
        
        try:
            async with self.get_session() as session:
                result = await session.execute("SELECT 1")
                await result.fetchone()
            return True
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected


# 全局数据库管理器实例
database_manager = DatabaseManager()


__all__ = [
    "DatabaseManager",
    "database_manager"
] 