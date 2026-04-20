"""
Configuration module for Product Search Agent.

This module provides centralized configuration management using Pydantic Settings.
All settings can be overridden via environment variables or .env file.
"""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    
    All settings have sensible defaults for development.
    Override via environment variables or .env file in production.
    """
    
    # ============================================================================
    # Application Settings
    # ============================================================================
    app_name: str = Field(
        default="Product Search Agent",
        description="Application name"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    environment: str = Field(
        default="development",
        description="Environment (development, staging, production)"
    )
    
    # ============================================================================
    # Server Configuration
    # ============================================================================
    host: str = Field(
        default="0.0.0.0",
        description="Server host"
    )
    port: int = Field(
        default=8000,
        description="Server port"
    )
    workers: int = Field(
        default=1,
        description="Number of worker processes"
    )
    reload: bool = Field(
        default=True,
        description="Enable auto-reload (development only)"
    )
    
    # ============================================================================
    # Database Settings
    # ============================================================================
    database_url: str = Field(
        default="sqlite:///./product_search.db",
        description="Database connection URL"
    )
    database_echo: bool = Field(
        default=False,
        description="Echo SQL queries to console"
    )
    
    # ============================================================================
    # Redis Configuration (Optional - for caching)
    # ============================================================================
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    redis_enabled: bool = Field(
        default=False,
        description="Enable Redis caching"
    )
    
    # ============================================================================
    # Search Configuration
    # ============================================================================
    search_interval_hours: int = Field(
        default=2,
        description="Interval between automatic searches (in hours)",
        ge=1,
        le=24
    )
    max_concurrent_searches: int = Field(
        default=5,
        description="Maximum number of concurrent search operations",
        ge=1,
        le=20
    )
    match_threshold_default: float = Field(
        default=70.0,
        description="Default matching threshold percentage",
        ge=0.0,
        le=100.0
    )
    max_results_per_platform: int = Field(
        default=20,
        description="Maximum results to fetch per platform",
        ge=1,
        le=100
    )
    search_timeout_seconds: int = Field(
        default=300,
        description="Timeout for search operations (in seconds)",
        ge=30,
        le=600
    )
    
    # ============================================================================
    # Scraper Settings
    # ============================================================================
    
    # Craigslist
    craigslist_default_city: str = Field(
        default="boston",
        description="Default Craigslist city for searches"
    )
    craigslist_rate_limit: int = Field(
        default=10,
        description="Requests per minute for Craigslist",
        ge=1,
        le=60
    )
    
    # Facebook Marketplace
    facebook_rate_limit: int = Field(
        default=5,
        description="Requests per minute for Facebook Marketplace",
        ge=1,
        le=30
    )
    
    # eBay
    ebay_rate_limit: int = Field(
        default=10,
        description="Requests per minute for eBay",
        ge=1,
        le=60
    )
    
    # ============================================================================
    # Selenium Configuration (for Facebook Marketplace)
    # ============================================================================
    selenium_headless: bool = Field(
        default=True,
        description="Run Selenium in headless mode"
    )
    selenium_timeout: int = Field(
        default=30,
        description="Selenium page load timeout (in seconds)",
        ge=10,
        le=120
    )
    selenium_implicit_wait: int = Field(
        default=10,
        description="Selenium implicit wait time (in seconds)",
        ge=5,
        le=60
    )
    
    # ============================================================================
    # Rate Limiting
    # ============================================================================
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable API rate limiting"
    )
    rate_limit_requests_per_minute: int = Field(
        default=60,
        description="API requests per minute per client",
        ge=10,
        le=1000
    )

    # ============================================================================
    # Email Configuration
    # ============================================================================
    SMTP_HOST: str = Field(
        default="smtp.gmail.com",
        description="SMTP server host"
    )
    SMTP_PORT: int = Field(
        default=587,
        description="SMTP server port",
        ge=1,
        le=65535
    )
    SMTP_USERNAME: str = Field(
        default="",
        description="Gmail address for SMTP authentication"
    )
    SMTP_PASSWORD: str = Field(
        default="",
        description="Gmail App Password (16 characters)"
    )
    EMAIL_FROM: str = Field(
        default="",
        description="Sender email address (usually same as SMTP_USERNAME)"
    )
    EMAIL_FROM_NAME: str = Field(
        default="Product Search Agent",
        description="Sender display name"
    )
    ENABLE_EMAIL_NOTIFICATIONS: bool = Field(
        default=True,
        description="Enable email notifications"
    )
    DAILY_DIGEST_TIME: str = Field(
        default="09:00",
        description="Time to send daily digest (HH:MM format)"
    )
    
    # ============================================================================
    # CORS Settings
    # ============================================================================
    cors_origins: str | List[str] = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Allowed CORS origins (comma-separated string or list)"
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )
    cors_allow_methods: List[str] = Field(
        default=["*"],
        description="Allowed HTTP methods"
    )
    cors_allow_headers: List[str] = Field(
        default=["*"],
        description="Allowed HTTP headers"
    )
    
    # ============================================================================
    # WebSocket Settings
    # ============================================================================
    websocket_heartbeat_interval: int = Field(
        default=30,
        description="WebSocket heartbeat interval (in seconds)",
        ge=10,
        le=120
    )
    websocket_max_connections: int = Field(
        default=100,
        description="Maximum concurrent WebSocket connections",
        ge=10,
        le=1000
    )
    
    # ============================================================================
    # Email Notification Settings (Optional)
    # ============================================================================
    enable_email_notifications: bool = Field(
        default=False,
        description="Enable email notifications"
    )
    email_smtp_host: str = Field(
        default="smtp.gmail.com",
        description="SMTP server host"
    )
    email_smtp_port: int = Field(
        default=587,
        description="SMTP server port",
        ge=1,
        le=65535
    )
    email_use_tls: bool = Field(
        default=True,
        description="Use TLS for email"
    )
    email_from: str = Field(
        default="",
        description="Sender email address"
    )
    email_password: str = Field(
        default="",
        description="Email account password or app password"
    )
    email_daily_digest_time: str = Field(
        default="09:00",
        description="Time to send daily digest (HH:MM format)"
    )
    
    # ============================================================================
    # Monitoring & Logging
    # ============================================================================
    sentry_dsn: str = Field(
        default="",
        description="Sentry DSN for error tracking"
    )
    enable_metrics: bool = Field(
        default=False,
        description="Enable metrics collection"
    )
    
    # ============================================================================
    # Validators
    # ============================================================================
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"log_level must be one of {allowed_levels}")
        return v_upper
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the allowed values."""
        allowed_envs = ['development', 'staging', 'production']
        v_lower = v.lower()
        if v_lower not in allowed_envs:
            raise ValueError(f"environment must be one of {allowed_envs}")
        return v_lower
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        # Handle None or empty string
        if v is None or v == '':
            return "http://localhost:3000,http://localhost:5173"
        
        # Handle string (comma-separated) - return as-is for now
        if isinstance(v, str):
            # If it's already a comma-separated string, return it
            if ',' in v:
                return v
            # If it's a single origin, return it
            return v if v.strip() else "http://localhost:3000,http://localhost:5173"
        
        # Handle list - convert to comma-separated string
        if isinstance(v, list):
            return ','.join(v) if v else "http://localhost:3000,http://localhost:5173"
        
        # Fallback to default
        return "http://localhost:3000,http://localhost:5173"
    
    @field_validator('cors_origins', mode='after')
    @classmethod
    def convert_cors_origins_to_list(cls, v):
        """Convert CORS origins string to list after validation."""
        if isinstance(v, str):
            origins = [origin.strip() for origin in v.split(',') if origin.strip()]
            return origins if origins else ["http://localhost:3000", "http://localhost:5173"]
        return v
    
    # ============================================================================
    # Pydantic Settings Configuration
    # ============================================================================
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env
    )
    
    # ============================================================================
    # Helper Methods
    # ============================================================================
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
    
    def get_database_url(self) -> str:
        """Get the database URL."""
        return self.database_url
    
    def get_cors_config(self) -> dict:
        """Get CORS configuration as a dictionary."""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": self.cors_allow_credentials,
            "allow_methods": self.cors_allow_methods,
            "allow_headers": self.cors_allow_headers,
        }


# ============================================================================
# Singleton Instance
# ============================================================================

# Create a single instance of settings to be imported throughout the application
settings = Settings()


# ============================================================================
# Convenience Functions
# ============================================================================

def get_settings() -> Settings:
    """
    Get the application settings instance.
    
    This function can be used as a FastAPI dependency.
    
    Returns:
        Settings: The application settings instance
    
    Example:
        ```python
        from fastapi import Depends
        from app.config import get_settings, Settings
        
        @app.get("/info")
        def get_info(settings: Settings = Depends(get_settings)):
            return {"app_name": settings.app_name}
        ```
    """
    return settings


def reload_settings() -> Settings:
    """
    Reload settings from environment variables.
    
    Useful for testing or when environment variables change.
    
    Returns:
        Settings: A new settings instance
    """
    return Settings()

    
  