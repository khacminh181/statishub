"""
Application configuration management using Pydantic settings.
Validates all required environment variables at startup.
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings with environment variable validation."""

    # Supabase
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_key: str = Field(..., description="Supabase anon/service key")

    # Redis
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")

    # Admin
    admin_key: str = Field(..., description="Admin authentication key")

    # Application
    environment: str = Field(default="production", description="Environment: development/staging/production")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Security
    allowed_origins: str = Field(default="*", description="CORS allowed origins (comma-separated)")
    cookie_secure: bool = Field(default=True, description="Use secure cookies (HTTPS only)")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="API requests per minute per key")

    @field_validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level is one of the standard levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()

    @field_validator("environment")
    def validate_environment(cls, v):
        """Validate environment is one of the expected values."""
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"environment must be one of {valid_envs}")
        return v.lower()

    def get_allowed_origins_list(self) -> List[str]:
        """Parse comma-separated origins into a list."""
        if self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
