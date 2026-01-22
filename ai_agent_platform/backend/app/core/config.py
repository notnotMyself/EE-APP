"""Core configuration for the application."""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "AI Agent Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Claude API (支持Auth Token或API Key)
    ANTHROPIC_AUTH_TOKEN: str = ""  # 优先使用Auth Token
    ANTHROPIC_API_KEY: str = ""  # 备用API Key
    ANTHROPIC_BASE_URL: str = ""  # 自定义Base URL
    ANTHROPIC_MODEL: str = "saas/claude-sonnet-4.5"

    # Agent SDK
    AGENT_BASE_PATH: str = Field(
        default="../../backend/agents",
        description="Agent workspace 基础路径"
    )

    # Gemini API (用于封面图生成)
    GEMINI_API_KEY: str = ""
    ENABLE_AI_COVER_GENERATION: bool = False  # 默认关闭，需要配置 API Key 后开启

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS - 开发环境允许所有来源，生产环境应配置具体域名
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
