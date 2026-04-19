"""
Test script to verify configuration module is working correctly.

Run this script to test the configuration system:
    python test_config.py
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.config import settings, get_settings


def test_configuration():
    """Test the configuration module."""
    print("=" * 80)
    print("Product Search Agent - Configuration Test")
    print("=" * 80)
    print()
    
    # Test basic settings
    print("📋 Application Settings:")
    print(f"  App Name: {settings.app_name}")
    print(f"  Version: {settings.app_version}")
    print(f"  Environment: {settings.environment}")
    print(f"  Debug Mode: {settings.debug}")
    print(f"  Log Level: {settings.log_level}")
    print()
    
    # Test server settings
    print("🖥️  Server Configuration:")
    print(f"  Host: {settings.host}")
    print(f"  Port: {settings.port}")
    print(f"  Workers: {settings.workers}")
    print()
    
    # Test database settings
    print("💾 Database Settings:")
    print(f"  Database URL: {settings.database_url}")
    print(f"  Echo SQL: {settings.database_echo}")
    print()
    
    # Test search configuration
    print("🔍 Search Configuration:")
    print(f"  Search Interval: {settings.search_interval_hours} hours")
    print(f"  Max Concurrent Searches: {settings.max_concurrent_searches}")
    print(f"  Default Match Threshold: {settings.match_threshold_default}%")
    print(f"  Max Results Per Platform: {settings.max_results_per_platform}")
    print()
    
    # Test scraper settings
    print("🕷️  Scraper Settings:")
    print(f"  Craigslist City: {settings.craigslist_default_city}")
    print(f"  Craigslist Rate Limit: {settings.craigslist_rate_limit} req/min")
    print(f"  Facebook Rate Limit: {settings.facebook_rate_limit} req/min")
    print(f"  eBay Rate Limit: {settings.ebay_rate_limit} req/min")
    print()
    
    # Test Selenium settings
    print("🌐 Selenium Configuration:")
    print(f"  Headless Mode: {settings.selenium_headless}")
    print(f"  Timeout: {settings.selenium_timeout}s")
    print(f"  Implicit Wait: {settings.selenium_implicit_wait}s")
    print()
    
    # Test CORS settings
    print("🔒 CORS Settings:")
    print(f"  Allowed Origins: {', '.join(settings.cors_origins)}")
    print(f"  Allow Credentials: {settings.cors_allow_credentials}")
    print()
    
    # Test WebSocket settings
    print("🔌 WebSocket Settings:")
    print(f"  Heartbeat Interval: {settings.websocket_heartbeat_interval}s")
    print(f"  Max Connections: {settings.websocket_max_connections}")
    print()
    
    # Test email settings
    print("📧 Email Notification Settings:")
    print(f"  Enabled: {settings.enable_email_notifications}")
    if settings.enable_email_notifications:
        print(f"  SMTP Host: {settings.email_smtp_host}")
        print(f"  SMTP Port: {settings.email_smtp_port}")
        print(f"  From Address: {settings.email_from}")
        print(f"  Daily Digest Time: {settings.email_daily_digest_time}")
    print()
    
    # Test helper methods
    print("🛠️  Helper Methods:")
    print(f"  Is Production: {settings.is_production()}")
    print(f"  Is Development: {settings.is_development()}")
    print()
    
    # Test get_settings function
    print("✅ Testing get_settings() function:")
    settings_instance = get_settings()
    print(f"  Settings instance retrieved: {settings_instance.app_name}")
    print()
    
    # Test CORS config helper
    print("🔧 CORS Configuration Dictionary:")
    cors_config = settings.get_cors_config()
    for key, value in cors_config.items():
        print(f"  {key}: {value}")
    print()
    
    print("=" * 80)
    print("✅ Configuration module is working correctly!")
    print("=" * 80)
    print()
    print("💡 Tips:")
    print("  - Create a .env file in the backend directory to override defaults")
    print("  - Copy .env.example to .env and customize your settings")
    print("  - Environment variables take precedence over .env file")
    print()


if __name__ == "__main__":
    try:
        test_configuration()
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
