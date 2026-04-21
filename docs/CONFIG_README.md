# Configuration Module Documentation

## Overview

The configuration module (`app/config.py`) provides centralized, type-safe configuration management for the Product Search Agent application using Pydantic Settings.

## Features

- ✅ **Type-safe**: All settings are validated at startup
- ✅ **Environment variables**: Automatic loading from `.env` file
- ✅ **Sensible defaults**: Works out of the box for development
- ✅ **Organized**: Settings grouped by functionality
- ✅ **Validated**: Input validation with helpful error messages
- ✅ **Singleton pattern**: One settings instance for the entire app

## Quick Start

### 1. Install Dependencies

The configuration module requires:
- `pydantic-settings>=2.0.0`
- `python-dotenv>=1.0.0`

These are already included in `pyproject.toml`.

### 2. Create Environment File

Copy the example environment file:

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your specific settings.

### 3. Use in Your Code

```python
from app.config import settings

# Access any setting
print(settings.app_name)
print(settings.database_url)
print(settings.search_interval_hours)
```

## Configuration Groups

### Application Settings

Basic application information and behavior:

```python
settings.app_name              # "Product Search Agent"
settings.app_version           # "1.0.0"
settings.debug                 # False
settings.log_level             # "INFO"
settings.environment           # "development"
```

### Server Configuration

Web server settings:

```python
settings.host                  # "0.0.0.0"
settings.port                  # 8000
settings.workers               # 1
settings.reload                # True (dev only)
```

### Database Settings

Database connection configuration:

```python
settings.database_url          # "sqlite:///./product_search.db"
settings.database_echo         # False
```

### Search Configuration

Search behavior and limits:

```python
settings.search_interval_hours        # 2
settings.max_concurrent_searches      # 5
settings.match_threshold_default      # 70.0
settings.max_results_per_platform     # 20
settings.search_timeout_seconds       # 300
```

### Scraper Settings

Platform-specific scraper configuration:

```python
# Craigslist
settings.craigslist_default_city      # "boston"
settings.craigslist_rate_limit        # 10

# Facebook Marketplace
settings.facebook_rate_limit          # 5

# eBay
settings.ebay_rate_limit              # 10
```

### Selenium Configuration

For JavaScript-heavy sites (Facebook Marketplace):

```python
settings.selenium_headless            # True
settings.selenium_timeout             # 30
settings.selenium_implicit_wait       # 10
```

### CORS Settings

Cross-Origin Resource Sharing configuration:

```python
settings.cors_origins                 # ["http://localhost:3000", ...]
settings.cors_allow_credentials       # True
settings.cors_allow_methods           # ["*"]
settings.cors_allow_headers           # ["*"]
```

### WebSocket Settings

Real-time communication configuration:

```python
settings.websocket_heartbeat_interval # 30
settings.websocket_max_connections    # 100
```

### Email Settings

Email notification configuration (optional):

```python
settings.enable_email_notifications   # False
settings.email_smtp_host              # "smtp.gmail.com"
settings.email_smtp_port              # 587
settings.email_from                   # ""
settings.email_password               # ""
settings.email_daily_digest_time      # "09:00"
```

## Usage Examples

### Basic Usage

```python
from app.config import settings

# Access settings directly
database_url = settings.database_url
search_interval = settings.search_interval_hours

# Use helper methods
if settings.is_production():
    # Production-specific logic
    pass
```

### FastAPI Dependency Injection

```python
from fastapi import Depends, FastAPI
from app.config import get_settings, Settings

app = FastAPI()

@app.get("/info")
def get_app_info(settings: Settings = Depends(get_settings)):
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }
```

### Database Connection

```python
from sqlalchemy import create_engine
from app.config import settings

engine = create_engine(
    settings.get_database_url(),
    echo=settings.database_echo
)
```

### CORS Configuration

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    **settings.get_cors_config()
)
```

### Conditional Logic

```python
from app.config import settings

# Development vs Production
if settings.is_development():
    # Enable debug features
    logging.basicConfig(level=logging.DEBUG)
else:
    # Production optimizations
    logging.basicConfig(level=logging.INFO)

# Feature flags
if settings.enable_email_notifications:
    # Setup email service
    pass
```

## Environment Variables

All settings can be overridden via environment variables. The variable name is the uppercase version of the setting name.

### Example

```bash
# In .env file or environment
APP_NAME="My Custom Name"
DEBUG=true
SEARCH_INTERVAL_HOURS=4
DATABASE_URL=postgresql://user:pass@localhost/db
```

### Precedence

1. Environment variables (highest priority)
2. `.env` file
3. Default values in code (lowest priority)

## Validation

The configuration module includes validation for:

- **Log Level**: Must be DEBUG, INFO, WARNING, ERROR, or CRITICAL
- **Environment**: Must be development, staging, or production
- **Numeric Ranges**: Values like `search_interval_hours` have min/max constraints
- **CORS Origins**: Can be provided as comma-separated string or list

### Example Validation Error

```python
# Invalid log level
LOG_LEVEL=INVALID  # Raises ValidationError
```

## Helper Methods

### `is_production()`

Check if running in production:

```python
if settings.is_production():
    # Production-only code
    pass
```

### `is_development()`

Check if running in development:

```python
if settings.is_development():
    # Development-only code
    pass
```

### `get_database_url()`

Get the database connection URL:

```python
db_url = settings.get_database_url()
```

### `get_cors_config()`

Get CORS configuration as a dictionary:

```python
cors_config = settings.get_cors_config()
# Returns: {"allow_origins": [...], "allow_credentials": True, ...}
```

## Testing

### Test Configuration Loading

```bash
cd backend
python test_config.py
```

This will display all loaded configuration values and verify the module is working correctly.

### Unit Testing

```python
from app.config import Settings

def test_custom_settings():
    # Create settings with custom values
    test_settings = Settings(
        app_name="Test App",
        debug=True,
        search_interval_hours=1
    )
    
    assert test_settings.app_name == "Test App"
    assert test_settings.debug is True
    assert test_settings.search_interval_hours == 1
```

## Best Practices

### 1. Never Commit `.env` Files

Add to `.gitignore`:

```
.env
*.env
!.env.example
```

### 2. Use Environment-Specific Settings

```bash
# Development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_ECHO=true

# Production
DEBUG=false
LOG_LEVEL=INFO
DATABASE_ECHO=false
```

### 3. Validate on Startup

The settings are validated when the module is imported, so any configuration errors will be caught immediately on application startup.

### 4. Use Type Hints

```python
from app.config import Settings

def my_function(settings: Settings):
    # IDE will provide autocomplete
    interval = settings.search_interval_hours
```

### 5. Don't Modify Settings at Runtime

Settings should be read-only after initialization. If you need to change settings, restart the application.

## Troubleshooting

### Issue: Settings Not Loading from .env

**Solution**: Ensure `.env` file is in the `backend` directory (same level as `app/`).

### Issue: Validation Error on Startup

**Solution**: Check the error message for which setting is invalid and fix it in your `.env` file.

### Issue: Environment Variable Not Working

**Solution**: Ensure the variable name is uppercase and matches the setting name (e.g., `SEARCH_INTERVAL_HOURS`).

### Issue: CORS Origins Not Parsing

**Solution**: Provide as comma-separated string: `CORS_ORIGINS=http://localhost:3000,http://localhost:5173`

## Advanced Usage

### Custom Settings Class

For testing or special cases:

```python
from app.config import Settings

custom_settings = Settings(
    database_url="sqlite:///:memory:",
    debug=True
)
```

### Reload Settings

```python
from app.config import reload_settings

# Reload from environment
new_settings = reload_settings()
```

## Security Considerations

1. **Never commit sensitive data**: Use `.env` for secrets
2. **Use app passwords**: For email, use Gmail app passwords, not your main password
3. **Restrict CORS origins**: In production, specify exact origins
4. **Enable rate limiting**: Protect your API from abuse
5. **Use HTTPS**: In production, always use HTTPS

## Migration Guide

### From Hardcoded Values

**Before:**
```python
DATABASE_URL = "sqlite:///./product_search.db"
SEARCH_INTERVAL = 2
```

**After:**
```python
from app.config import settings

database_url = settings.database_url
search_interval = settings.search_interval_hours
```

### From Environment Variables

**Before:**
```python
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./product_search.db")
```

**After:**
```python
from app.config import settings
database_url = settings.database_url
```

## Support

For issues or questions about the configuration module:

1. Check this documentation
2. Review `.env.example` for all available settings
3. Run `python test_config.py` to verify configuration
4. Check the implementation in `app/config.py`

## Changelog

### Version 1.0.0
- Initial configuration module
- Support for all application settings
- Environment variable loading
- Validation and type safety
- Helper methods and utilities