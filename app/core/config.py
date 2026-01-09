"""
Application configuration management using Pydantic settings.
Validates all required environment variables at startup.
"""

import os
import re
from typing import List, Optional
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
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_ssl: bool = Field(default=False, description="Use SSL for Redis connection")

    # Admin
    admin_key: str = Field(
        ..., min_length=16, description="Admin authentication key (min 16 chars)"
    )

    @field_validator("admin_key")
    def validate_admin_key(cls, v):
        """Validate admin key meets security requirements."""
        if len(v) < 16:
            raise ValueError("admin_key must be at least 16 characters long")
        # In production, require more complexity
        if os.getenv("ENVIRONMENT", "production") == "production":
            has_upper = bool(re.search(r"[A-Z]", v))
            has_lower = bool(re.search(r"[a-z]", v))
            has_digit = bool(re.search(r"\d", v))
            if not (has_upper and has_lower and has_digit):
                raise ValueError(
                    "admin_key must contain uppercase, lowercase, and numeric characters in production"
                )
        return v

    # Application
    environment: str = Field(
        default="production", description="Environment: development/staging/production"
    )
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
