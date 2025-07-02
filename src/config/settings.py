"""
应用配置管理
使用Pydantic Settings实现类型安全的配置管理
支持环境变量和多环境配置
"""

import os
from enum import Enum
from functools import lru_cache
from typing import List, Optional, Union

from pydantic import BaseModel, Field, PostgresDsn, RedisDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """环境枚举"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseConfig(BaseModel):
    """数据库配置"""
    url: PostgresDsn
    pool_size: int = Field(default=20, ge=1, le=100)
    max_overflow: int = Field(default=30, ge=0, le=200)
    pool_timeout: int = Field(default=30, ge=1, le=300)
    pool_recycle: int = Field(default=3600, ge=300, le=86400)
    echo: bool = Field(default=False)
    echo_pool: bool = Field(default=False)


class RedisConfig(BaseModel):
    """Redis缓存配置"""
    url: RedisDsn
    password: Optional[str] = None
    db: int = Field(default=0, ge=0, le=15)
    max_connections: int = Field(default=50, ge=1, le=1000)
    socket_timeout: float = Field(default=5.0, ge=1.0, le=60.0)
    socket_keepalive: bool = Field(default=True)
    socket_keepalive_options: dict = Field(default_factory=dict)


class SecurityConfig(BaseModel):
    """安全配置"""
    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_hours: int = Field(default=24, ge=1, le=168)
    refresh_token_expiration_days: int = Field(default=30, ge=1, le=365)
    password_min_length: int = Field(default=8, ge=6, le=128)
    api_key_length: int = Field(default=32, ge=16, le=64)
    bcrypt_rounds: int = Field(default=12, ge=10, le=16)
    session_timeout_minutes: int = Field(default=30, ge=5, le=1440)


class OpenAIConfig(BaseModel):
    """OpenAI配置"""
    api_key: str = Field(min_length=1)
    base_url: Optional[str] = None
    organization: Optional[str] = None
    timeout: float = Field(default=60.0, ge=1.0, le=300.0)
    max_retries: int = Field(default=3, ge=0, le=10)
    default_model: str = Field(default="gpt-4o-mini")
    embedding_model: str = Field(default="text-embedding-ada-002")


class MonitoringConfig(BaseModel):
    """监控配置"""
    enable_metrics: bool = Field(default=True)
    enable_tracing: bool = Field(default=True)
    enable_profiling: bool = Field(default=False)
    metrics_port: int = Field(default=9090, ge=1024, le=65535)
    prometheus_endpoint: str = Field(default="/metrics")
    sentry_dsn: Optional[str] = None
    sentry_sample_rate: float = Field(default=1.0, ge=0.0, le=1.0)


class Settings(BaseSettings):
    """主配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore"
    )
    
    # 基础配置
    APP_NAME: str = Field(default="游戏自动化平台")
    APP_VERSION: str = Field(default="2.0.0")
    DESCRIPTION: str = Field(default="基于AI的现代化游戏自动化平台")
    
    # 环境配置
    ENVIRONMENT: Environment = Field(default=Environment.DEVELOPMENT)
    DEBUG: bool = Field(default=False)
    TESTING: bool = Field(default=False)
    
    # 服务器配置
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000, ge=1, le=65535)
    WORKERS: int = Field(default=1, ge=1, le=32)
    RELOAD: bool = Field(default=False)
    
    # 日志配置
    LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO)
    LOG_FORMAT: str = Field(default="json")
    LOG_FILE: Optional[str] = None
    LOG_ROTATION: str = Field(default="1 day")
    LOG_RETENTION: str = Field(default="30 days")
    
    # 数据库配置
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql://gameauto:gameauto_pass@localhost:5432/gameauto"
    )
    DATABASE_POOL_SIZE: int = Field(default=20, ge=1, le=100)
    DATABASE_MAX_OVERFLOW: int = Field(default=30, ge=0, le=200)
    DATABASE_POOL_TIMEOUT: int = Field(default=30, ge=1, le=300)
    DATABASE_POOL_RECYCLE: int = Field(default=3600, ge=300, le=86400)
    DATABASE_ECHO: bool = Field(default=False)
    
    # Redis配置
    REDIS_URL: RedisDsn = Field(default="redis://localhost:6379/0")
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = Field(default=0, ge=0, le=15)
    REDIS_MAX_CONNECTIONS: int = Field(default=50, ge=1, le=1000)
    
    # 安全配置
    JWT_SECRET: str = Field(default="your-super-secret-jwt-key-change-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRATION_HOURS: int = Field(default=24, ge=1, le=168)
    BCRYPT_ROUNDS: int = Field(default=12, ge=10, le=16)
    
    # OpenAI配置
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_ORGANIZATION: Optional[str] = None
    OPENAI_TIMEOUT: float = Field(default=60.0, ge=1.0, le=300.0)
    OPENAI_MAX_RETRIES: int = Field(default=3, ge=0, le=10)
    OPENAI_DEFAULT_MODEL: str = Field(default="gpt-4o-mini")
    
    # CORS配置
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]
    )
    CORS_ORIGINS_REGEX: Optional[str] = None
    CORS_HEADERS: List[str] = Field(
        default=["Content-Type", "Authorization", "X-Requested-With"]
    )
    CORS_METHODS: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # 可信主机
    TRUSTED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1", "*.gameauto.com"]
    )
    
    # 限流配置
    RATE_LIMIT_REQUESTS: int = Field(default=100, ge=1, le=10000)
    RATE_LIMIT_WINDOW: int = Field(default=60, ge=1, le=3600)
    RATE_LIMIT_REDIS_URL: Optional[str] = None
    
    # 监控配置
    ENABLE_METRICS: bool = Field(default=True)
    ENABLE_TRACING: bool = Field(default=True)
    ENABLE_PROFILING: bool = Field(default=False)
    METRICS_PORT: int = Field(default=9090, ge=1024, le=65535)
    SENTRY_DSN: Optional[str] = None
    SENTRY_SAMPLE_RATE: float = Field(default=1.0, ge=0.0, le=1.0)
    
    # 游戏自动化配置
    GAME_SCREENSHOT_INTERVAL: float = Field(default=0.5, ge=0.1, le=5.0)
    GAME_ACTION_DELAY: float = Field(default=0.1, ge=0.01, le=2.0)
    GAME_WINDOW_TITLE_PATTERNS: List[str] = Field(
        default=["明日方舟", "原神", "崩坏：星穹铁道", "绝区零"]
    )
    GAME_TEMPLATE_MATCH_THRESHOLD: float = Field(default=0.8, ge=0.1, le=1.0)
    GAME_OCR_CONFIDENCE_THRESHOLD: float = Field(default=0.7, ge=0.1, le=1.0)
    
    # 文件存储配置
    UPLOAD_MAX_SIZE: int = Field(default=10 * 1024 * 1024, ge=1024, le=100 * 1024 * 1024)  # 10MB
    UPLOAD_ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]
    )
    SCREENSHOTS_DIR: str = Field(default="screenshots")
    LOGS_DIR: str = Field(default="logs")
    TEMPLATES_DIR: str = Field(default="templates")
    DATA_DIR: str = Field(default="data")
    
    @validator("ENVIRONMENT", pre=True)
    def validate_environment(cls, v):
        """验证环境变量"""
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @validator("LOG_LEVEL", pre=True)
    def validate_log_level(cls, v):
        """验证日志级别"""
        if isinstance(v, str):
            return LogLevel(v.upper())
        return v
    
    @validator("JWT_SECRET")
    def validate_jwt_secret(cls, v):
        """验证JWT密钥强度"""
        if len(v) < 32:
            raise ValueError("JWT密钥长度至少32个字符")
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def validate_cors_origins(cls, v):
        """验证CORS来源"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("TRUSTED_HOSTS", pre=True) 
    def validate_trusted_hosts(cls, v):
        """验证可信主机"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @property
    def database_config(self) -> DatabaseConfig:
        """数据库配置对象"""
        return DatabaseConfig(
            url=self.DATABASE_URL,
            pool_size=self.DATABASE_POOL_SIZE,
            max_overflow=self.DATABASE_MAX_OVERFLOW,
            pool_timeout=self.DATABASE_POOL_TIMEOUT,
            pool_recycle=self.DATABASE_POOL_RECYCLE,
            echo=self.DATABASE_ECHO
        )
    
    @property
    def redis_config(self) -> RedisConfig:
        """Redis配置对象"""
        return RedisConfig(
            url=self.REDIS_URL,
            password=self.REDIS_PASSWORD,
            db=self.REDIS_DB,
            max_connections=self.REDIS_MAX_CONNECTIONS
        )
    
    @property
    def security_config(self) -> SecurityConfig:
        """安全配置对象"""
        return SecurityConfig(
            jwt_secret=self.JWT_SECRET,
            jwt_algorithm=self.JWT_ALGORITHM,
            jwt_expiration_hours=self.JWT_EXPIRATION_HOURS,
            bcrypt_rounds=self.BCRYPT_ROUNDS
        )
    
    @property
    def openai_config(self) -> OpenAIConfig:
        """OpenAI配置对象"""
        return OpenAIConfig(
            api_key=self.OPENAI_API_KEY,
            base_url=self.OPENAI_BASE_URL,
            organization=self.OPENAI_ORGANIZATION,
            timeout=self.OPENAI_TIMEOUT,
            max_retries=self.OPENAI_MAX_RETRIES,
            default_model=self.OPENAI_DEFAULT_MODEL
        )
    
    @property
    def monitoring_config(self) -> MonitoringConfig:
        """监控配置对象"""
        return MonitoringConfig(
            enable_metrics=self.ENABLE_METRICS,
            enable_tracing=self.ENABLE_TRACING,
            enable_profiling=self.ENABLE_PROFILING,
            metrics_port=self.METRICS_PORT,
            sentry_dsn=self.SENTRY_DSN,
            sentry_sample_rate=self.SENTRY_SAMPLE_RATE
        )
    
    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.ENVIRONMENT == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.ENVIRONMENT == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.ENVIRONMENT == Environment.TESTING or self.TESTING


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置实例（单例）
    使用lru_cache确保配置只加载一次
    """
    return Settings()


# 导出常用配置对象
settings = get_settings()

__all__ = [
    "Settings",
    "Environment", 
    "LogLevel",
    "DatabaseConfig",
    "RedisConfig", 
    "SecurityConfig",
    "OpenAIConfig",
    "MonitoringConfig",
    "get_settings",
    "settings"
] 