"""
Test script for email providers (SendGrid and Mailgun).

This script helps you test your email configuration before deploying.

Usage:
    pytest backend/app/tests/test_email_providers.py
    
Or run as standalone script:
    python backend/app/tests/test_email_providers.py --email your@email.com
"""

import asyncio
import sys
import os
from pathlib import Path
import pytest
from unittest.mock import Mock, patch, AsyncMock

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


from app.config import settings
from app.services.email_service_http import EmailServiceHTTP
from app.services.email_service import get_email_service


@pytest.mark.asyncio
async def test_email_service():
    """Test the configured email service (pytest version)"""
    
    print("\n" + "=" * 70)
    print("Email Service Configuration Test")
    print("=" * 70)
    print()
    
    # Display current configuration
    print("Current Configuration:")
    print(f"  EMAIL_PROVIDER: {settings.EMAIL_PROVIDER}")
    print(f"  ENABLE_EMAIL_NOTIFICATIONS: {settings.ENABLE_EMAIL_NOTIFICATIONS}")
    print(f"  EMAIL_FROM: {settings.EMAIL_FROM}")
    print(f"  EMAIL_FROM_NAME: {settings.EMAIL_FROM_NAME}")
    print()
    
    # Check which providers are configured
    has_sendgrid = bool(settings.SENDGRID_API_KEY)
    has_mailgun = bool(settings.MAILGUN_API_KEY and settings.MAILGUN_DOMAIN)
    has_smtp = bool(settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
    
    print("Available Providers:")
    print(f"  SendGrid: {'✓ Configured' if has_sendgrid else '✗ Not configured'}")
    if has_sendgrid:
        print(f"    API Key: {settings.SENDGRID_API_KEY[:10]}...{settings.SENDGRID_API_KEY[-4:]}")
    
    print(f"  Mailgun: {'✓ Configured' if has_mailgun else '✗ Not configured'}")
    if has_mailgun:
        print(f"    API Key: {settings.MAILGUN_API_KEY[:10]}...{settings.MAILGUN_API_KEY[-4:]}")
        print(f"    Domain: {settings.MAILGUN_DOMAIN}")
    
    print(f"  SMTP: {'✓ Configured' if has_smtp else '✗ Not configured'}")
    if has_smtp:
        print(f"    Host: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        print(f"    Username: {settings.SMTP_USERNAME}")
    print()
    
    # Check if any provider is configured
    if not (has_sendgrid or has_mailgun or has_smtp):
        print("❌ ERROR: No email provider configured!")
        print()
        print("Please configure at least one provider in your .env file:")
        print("  - SendGrid: Set SENDGRID_API_KEY")
        print("  - Mailgun: Set MAILGUN_API_KEY and MAILGUN_DOMAIN")
        print("  - SMTP: Set SMTP_USERNAME and SMTP_PASSWORD")
        pytest.skip("No email provider configured")
        return
    
    # Get email service
    try:
        service = get_email_service(settings)
        print(f"✓ Email service initialized: {service.__class__.__name__}")
        print()
        assert service is not None, "Email service should be initialized"
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize email service: {e}")
        pytest.fail(f"Failed to initialize email service: {e}")


@pytest.mark.asyncio
async def test_email_service_send(monkeypatch):
    """Test sending email with mocked HTTP calls"""
    
    # Skip if no provider is configured
    has_sendgrid = bool(settings.SENDGRID_API_KEY)
    has_mailgun = bool(settings.MAILGUN_API_KEY and settings.MAILGUN_DOMAIN)
    has_smtp = bool(settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
    
    if not (has_sendgrid or has_mailgun or has_smtp):
        pytest.skip("No email provider configured")
    
    # Mock httpx.AsyncClient for HTTP providers
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "success"}
    
    async def mock_post(*args, **kwargs):
        return mock_response
    
    # Get email service
    service = get_email_service(settings)
    
    # Mock the HTTP client if using HTTP-based service
    if isinstance(service, EmailServiceHTTP):
        with patch('httpx.AsyncClient.post', new=mock_post):
            # Test sending email
            await service.send_email(
                to_email="test@example.com",
                subject="Test Email",
                html_content="<p>Test content</p>"
            )
    else:
        # For SMTP, we'll skip actual sending in tests
        pytest.skip("SMTP testing requires different mocking approach")
    
    print("✓ Email service send test passed")


# Standalone script functionality
async def interactive_test():
    """Interactive test for manual testing"""
    
    print("=" * 70)
    print("Email Service Configuration Test")
    print("=" * 70)
    print()
    
    # Display current configuration
    print("Current Configuration:")
    print(f"  EMAIL_PROVIDER: {settings.EMAIL_PROVIDER}")
    print(f"  ENABLE_EMAIL_NOTIFICATIONS: {settings.ENABLE_EMAIL_NOTIFICATIONS}")
    print(f"  EMAIL_FROM: {settings.EMAIL_FROM}")
    print(f"  EMAIL_FROM_NAME: {settings.EMAIL_FROM_NAME}")
    print()
    
    # Check which providers are configured
    has_sendgrid = bool(settings.SENDGRID_API_KEY)
    has_mailgun = bool(settings.MAILGUN_API_KEY and settings.MAILGUN_DOMAIN)
    has_smtp = bool(settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
    
    print("Available Providers:")
    print(f"  SendGrid: {'✓ Configured' if has_sendgrid else '✗ Not configured'}")
    if has_sendgrid:
        print(f"    API Key: {settings.SENDGRID_API_KEY[:10]}...{settings.SENDGRID_API_KEY[-4:]}")
    
    print(f"  Mailgun: {'✓ Configured' if has_mailgun else '✗ Not configured'}")
    if has_mailgun:
        print(f"    API Key: {settings.MAILGUN_API_KEY[:10]}...{settings.MAILGUN_API_KEY[-4:]}")
        print(f"    Domain: {settings.MAILGUN_DOMAIN}")
    
    print(f"  SMTP: {'✓ Configured' if has_smtp else '✗ Not configured'}")
    if has_smtp:
        print(f"    Host: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        print(f"    Username: {settings.SMTP_USERNAME}")
    print()
    
    # Check if any provider is configured
    if not (has_sendgrid or has_mailgun or has_smtp):
        print("❌ ERROR: No email provider configured!")
        print()
        print("Please configure at least one provider in your .env file:")
        print("  - SendGrid: Set SENDGRID_API_KEY")
        print("  - Mailgun: Set MAILGUN_API_KEY and MAILGUN_DOMAIN")
        print("  - SMTP: Set SMTP_USERNAME and SMTP_PASSWORD")
        return False
    
    # Get email service
    try:
        service = get_email_service(settings)
        print(f"✓ Email service initialized: {service.__class__.__name__}")
        print()
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize email service: {e}")
        return False
    
    # Prompt for test email
    print("=" * 70)
    
    # Check for command line argument
    test_email = None
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == '--email' and i + 1 < len(sys.argv):
                test_email = sys.argv[i + 1]
                break
    
    if not test_email:
        test_email = input("Enter email address to send test email to: ").strip()
    
    if not test_email or '@' not in test_email:
        print("❌ Invalid email address")
        return False
    
    print()
    print(f"Sending test email to: {test_email}")
    print("Please wait...")
    print()
    
    # Send test email
    try:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; 
                          padding: 15px; border-radius: 5px; margin: 20px 0; }
                .info { background: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; 
                       padding: 15px; border-radius: 5px; margin: 20px 0; }
                .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Email Service Test</h1>
                    <p>Product Search Agent</p>
                </div>
                <div class="content">
                    <div class="success">
                        <strong>✓ Success!</strong> Your email service is working correctly.
                    </div>
                    
                    <h2>Configuration Details</h2>
                    <div class="info">
                        <p><strong>Provider:</strong> """ + ("SendGrid" if has_sendgrid else "Mailgun" if has_mailgun else "SMTP") + """</p>
                        <p><strong>From:</strong> """ + settings.EMAIL_FROM + """</p>
                        <p><strong>From Name:</strong> """ + settings.EMAIL_FROM_NAME + """</p>
                    </div>
                    
                    <h2>What's Next?</h2>
                    <p>Your email notifications are ready to use! The Product Search Agent will send you:</p>
                    <ul>
                        <li><strong>Match Notifications</strong> - When products match your search criteria</li>
                        <li><strong>Search Started</strong> - Confirmation when you create a new search</li>
                        <li><strong>Daily Digest</strong> - Summary of all matches (9:00 AM daily)</li>
                    </ul>
                    
                    <div class="footer">
                        <p>This is a test email from Product Search Agent</p>
                        <p>If you received this email, your configuration is correct!</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        await service.send_email(
            to_email=test_email,
            subject="✓ Email Service Test - Product Search Agent",
            html_content=html_content
        )
        
        print("=" * 70)
        print("✓ SUCCESS! Test email sent successfully!")
        print("=" * 70)
        print()
        print("Check your inbox for the test email.")
        print("If you don't see it, check your spam folder.")
        print()
        
        if has_sendgrid:
            print("SendGrid Activity Feed:")
            print("  https://app.sendgrid.com/email_activity")
        
        if has_mailgun:
            print("Mailgun Logs:")
            print("  https://app.mailgun.com/app/logs")
        
        print()
        return True
        
    except Exception as e:
        print("=" * 70)
        print("❌ ERROR: Failed to send test email")
        print("=" * 70)
        print()
        print(f"Error details: {str(e)}")
        print()
        print("Common issues:")
        print("  1. Invalid API key - Check your credentials")
        print("  2. Unverified sender - Verify your email in provider settings")
        print("  3. Sandbox mode (Mailgun) - Add recipient to authorized list")
        print("  4. Network issues - Check your internet connection")
        print()
        return False


async def main():
    """Main function for standalone execution"""
    try:
        success = await interactive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Run as standalone script
    asyncio.run(main())

# Made with Bob
