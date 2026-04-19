import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import sys
from pathlib import Path
# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.services.email_service import EmailService
from app.models.product import Product
from app.models.search_request import SearchRequest

@pytest.fixture
def mock_config():
    """Create mock configuration for testing"""
    config = Mock()
    config.SMTP_HOST = "smtp.gmail.com"
    config.SMTP_PORT = 587
    config.SMTP_USERNAME = "test@example.com"
    config.SMTP_PASSWORD = "test_password"
    config.EMAIL_FROM = "test@example.com"
    config.EMAIL_FROM_NAME = "Test Product Search Agent"
    config.ENABLE_EMAIL_NOTIFICATIONS = True
    return config


@pytest.fixture
def email_service(mock_config):
    """Create email service for testing"""
    return EmailService(mock_config)


@pytest.fixture
def mock_product():
    """Create mock product for testing"""
    product = Mock(spec=Product)
    product.id = 1
    product.title = "Test Product"
    product.price = 99.99
    product.platform = "craigslist"
    product.match_score = 85.5
    product.url = "https://example.com/product/1"
    product.created_at = datetime(2024, 1, 15, 10, 30, 0)
    return product


@pytest.fixture
def mock_search_request():
    """Create mock search request for testing"""
    search_request = Mock(spec=SearchRequest)
    search_request.id = 1
    search_request.query = "laptop"
    search_request.product_name = "Gaming Laptop"
    search_request.budget = 1500.00
    search_request.platforms = "craigslist,ebay,facebook"
    search_request.search_interval = 2
    search_request.created_at = datetime(2024, 1, 15, 9, 0, 0)
    return search_request


def test_email_service_initialization(mock_config):
    """Test that email service initializes correctly"""
    service = EmailService(mock_config)
    assert service.config == mock_config
    assert service.template_env is not None


def test_template_rendering_match_notification(email_service, mock_product, mock_search_request):
    """Test that match notification template renders correctly"""
    template = email_service.template_env.get_template("emails/match_notification.html")
    
    context = {
        "search_query": mock_search_request.query,
        "product": {
            "title": mock_product.title,
            "price": f"{mock_product.price:.2f}",
            "platform": mock_product.platform.capitalize(),
            "match_score": f"{mock_product.match_score:.1f}",
            "url": mock_product.url,
            "created_at": mock_product.created_at
        }
    }
    
    html_content = template.render(**context)
    
    # Assert output contains expected content
    assert "New Match Found!" in html_content
    assert mock_search_request.query in html_content
    assert mock_product.title in html_content
    assert "99.99" in html_content
    assert "Craigslist" in html_content
    assert "85.5%" in html_content


def test_template_rendering_daily_digest(email_service, mock_product, mock_search_request):
    """Test that daily digest template renders correctly"""
    template = email_service.template_env.get_template("emails/daily_digest.html")
    
    context = {
        "date": datetime.now(),
        "matches": [{
            "search_query": mock_search_request.query,
            "product": {
                "title": mock_product.title,
                "price": f"{mock_product.price:.2f}",
                "platform": mock_product.platform.capitalize(),
                "match_score": f"{mock_product.match_score:.1f}",
                "url": mock_product.url
            }
        }]
    }
    
    html_content = template.render(**context)
    
    # Assert output contains expected content
    assert "Daily Digest" in html_content
    assert mock_product.title in html_content
    assert "99.99" in html_content


def test_template_rendering_search_started(email_service, mock_search_request):
    """Test that search started template renders correctly"""
    template = email_service.template_env.get_template("emails/search_started.html")
    
    context = {
        "search_request": {
            "product_name": mock_search_request.product_name,
            "budget": f"{mock_search_request.budget:.2f}",
            "platforms": ["Craigslist", "Ebay", "Facebook"],
            "search_interval": mock_search_request.search_interval,
            "created_at": mock_search_request.created_at
        }
    }
    
    html_content = template.render(**context)
    
    # Assert output contains expected content
    assert "Search Started!" in html_content
    assert mock_search_request.product_name in html_content
    assert "1500.00" in html_content


@pytest.mark.asyncio
@patch('app.services.email_service.SMTP')
async def test_send_email_success(mock_smtp_class, email_service):
    """Test email sending with mocked SMTP"""
    # Create mock SMTP instance
    mock_smtp_instance = AsyncMock()
    mock_smtp_class.return_value.__aenter__.return_value = mock_smtp_instance
    
    # Call send_email
    await email_service.send_email(
        to_email="recipient@example.com",
        subject="Test Subject",
        html_content="<h1>Test Content</h1>"
    )
    
    # Assert SMTP methods were called correctly
    mock_smtp_instance.login.assert_called_once_with(
        email_service.config.SMTP_USERNAME,
        email_service.config.SMTP_PASSWORD
    )
    mock_smtp_instance.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_email_notifications_disabled(email_service):
    """Test that email is not sent when notifications are disabled"""
    email_service.config.ENABLE_EMAIL_NOTIFICATIONS = False
    
    # Should return early without raising exception
    await email_service.send_email(
        to_email="recipient@example.com",
        subject="Test Subject",
        html_content="<h1>Test Content</h1>"
    )
    # No exception means test passed


@pytest.mark.asyncio
async def test_send_email_missing_credentials(email_service):
    """Test that email sending fails with missing credentials"""
    email_service.config.SMTP_USERNAME = ""
    
    with pytest.raises(ValueError, match="SMTP credentials not configured"):
        await email_service.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            html_content="<h1>Test Content</h1>"
        )


@pytest.mark.asyncio
async def test_send_email_missing_from_address(email_service):
    """Test that email sending fails with missing FROM address"""
    email_service.config.EMAIL_FROM = ""
    
    with pytest.raises(ValueError, match="EMAIL_FROM not configured"):
        await email_service.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            html_content="<h1>Test Content</h1>"
        )


@pytest.mark.asyncio
@patch('app.services.email_service.SMTP')
async def test_send_match_notification(mock_smtp_class, email_service, mock_product, mock_search_request):
    """Test match notification email"""
    # Mock SMTP
    mock_smtp_instance = AsyncMock()
    mock_smtp_class.return_value.__aenter__.return_value = mock_smtp_instance
    
    # Call send_match_notification
    await email_service.send_match_notification(
        email="recipient@example.com",
        product=mock_product,
        search_request=mock_search_request
    )
    
    # Assert email was sent
    mock_smtp_instance.send_message.assert_called_once()
    
    # Get the call arguments
    call_args = mock_smtp_instance.send_message.call_args
    message = call_args[0][0]
    
    # Assert subject contains product title
    assert "New Match Found" in message["Subject"]
    assert mock_product.title[:50] in message["Subject"]


@pytest.mark.asyncio
@patch('app.services.email_service.SMTP')
async def test_send_daily_digest_with_matches(mock_smtp_class, email_service, mock_product, mock_search_request):
    """Test daily digest email with matches"""
    # Mock SMTP
    mock_smtp_instance = AsyncMock()
    mock_smtp_class.return_value.__aenter__.return_value = mock_smtp_instance
    
    # Create matches list
    matches = [
        {
            'product': mock_product,
            'search_request': mock_search_request
        }
    ]
    
    # Call send_daily_digest
    await email_service.send_daily_digest(
        email="recipient@example.com",
        matches=matches
    )
    
    # Assert email was sent
    mock_smtp_instance.send_message.assert_called_once()
    
    # Get the call arguments
    call_args = mock_smtp_instance.send_message.call_args
    message = call_args[0][0]
    
    # Assert subject contains match count
    assert "Daily Digest" in message["Subject"]
    assert "1 New Match Found" in message["Subject"]


@pytest.mark.asyncio
@patch('app.services.email_service.SMTP')
async def test_send_daily_digest_no_matches(mock_smtp_class, email_service):
    """Test daily digest email with no matches"""
    # Mock SMTP
    mock_smtp_instance = AsyncMock()
    mock_smtp_class.return_value.__aenter__.return_value = mock_smtp_instance
    
    # Call send_daily_digest with empty list
    await email_service.send_daily_digest(
        email="recipient@example.com",
        matches=[]
    )
    
    # Assert email was sent
    mock_smtp_instance.send_message.assert_called_once()
    
    # Get the call arguments
    call_args = mock_smtp_instance.send_message.call_args
    message = call_args[0][0]
    
    # Assert subject indicates no matches
    assert "Daily Digest" in message["Subject"]
    assert "No New Matches Today" in message["Subject"]


@pytest.mark.asyncio
@patch('app.services.email_service.SMTP')
async def test_send_daily_digest_multiple_matches(mock_smtp_class, email_service, mock_product, mock_search_request):
    """Test daily digest email with multiple matches"""
    # Mock SMTP
    mock_smtp_instance = AsyncMock()
    mock_smtp_class.return_value.__aenter__.return_value = mock_smtp_instance
    
    # Create multiple matches
    matches = [
        {'product': mock_product, 'search_request': mock_search_request},
        {'product': mock_product, 'search_request': mock_search_request},
        {'product': mock_product, 'search_request': mock_search_request}
    ]
    
    # Call send_daily_digest
    await email_service.send_daily_digest(
        email="recipient@example.com",
        matches=matches
    )
    
    # Assert email was sent
    mock_smtp_instance.send_message.assert_called_once()
    
    # Get the call arguments
    call_args = mock_smtp_instance.send_message.call_args
    message = call_args[0][0]
    
    # Assert subject contains correct count with plural
    assert "3 New Matches Found" in message["Subject"]


@pytest.mark.asyncio
@patch('app.services.email_service.SMTP')
async def test_send_search_started(mock_smtp_class, email_service, mock_search_request):
    """Test search started confirmation email"""
    # Mock SMTP
    mock_smtp_instance = AsyncMock()
    mock_smtp_class.return_value.__aenter__.return_value = mock_smtp_instance
    
    # Call send_search_started
    await email_service.send_search_started(
        email="recipient@example.com",
        search_request=mock_search_request
    )
    
    # Assert email was sent
    mock_smtp_instance.send_message.assert_called_once()
    
    # Get the call arguments
    call_args = mock_smtp_instance.send_message.call_args
    message = call_args[0][0]
    
    # Assert subject contains product name
    assert "Search Started" in message["Subject"]
    assert mock_search_request.product_name in message["Subject"]


@pytest.mark.asyncio
@patch('app.services.email_service.SMTP')
async def test_send_email_smtp_error(mock_smtp_class, email_service):
    """Test email sending handles SMTP errors"""
    # Mock SMTP to raise an exception
    mock_smtp_instance = AsyncMock()
    mock_smtp_instance.login.side_effect = Exception("SMTP connection failed")
    mock_smtp_class.return_value.__aenter__.return_value = mock_smtp_instance
    
    # Should raise exception
    with pytest.raises(Exception, match="Failed to send email"):
        await email_service.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            html_content="<h1>Test Content</h1>"
        )


@pytest.mark.asyncio
@patch('app.services.email_service.SMTP')
async def test_send_match_notification_error_handling(mock_smtp_class, email_service, mock_product, mock_search_request):
    """Test match notification handles errors gracefully"""
    # Mock SMTP to raise an exception
    mock_smtp_instance = AsyncMock()
    mock_smtp_instance.send_message.side_effect = Exception("Send failed")
    mock_smtp_class.return_value.__aenter__.return_value = mock_smtp_instance
    
    # Should raise exception with context
    with pytest.raises(Exception, match="Failed to send match notification"):
        await email_service.send_match_notification(
            email="recipient@example.com",
            product=mock_product,
            search_request=mock_search_request
        )


@pytest.mark.asyncio
@patch('app.services.email_service.SMTP')
async def test_send_daily_digest_error_handling(mock_smtp_class, email_service, mock_product, mock_search_request):
    """Test daily digest handles errors gracefully"""
    # Mock SMTP to raise an exception
    mock_smtp_instance = AsyncMock()
    mock_smtp_instance.send_message.side_effect = Exception("Send failed")
    mock_smtp_class.return_value.__aenter__.return_value = mock_smtp_instance
    
    # Create matches list
    matches = [
        {
            'product': mock_product,
            'search_request': mock_search_request
        }
    ]
    
    # Should raise exception with context
    with pytest.raises(Exception, match="Failed to send daily digest"):
        await email_service.send_daily_digest(
            email="recipient@example.com",
            matches=matches
        )


@pytest.mark.asyncio
@patch('app.services.email_service.SMTP')
async def test_send_search_started_error_handling(mock_smtp_class, email_service, mock_search_request):
    """Test search started handles errors gracefully"""
    # Mock SMTP to raise an exception
    mock_smtp_instance = AsyncMock()
    mock_smtp_instance.send_message.side_effect = Exception("Send failed")
    mock_smtp_class.return_value.__aenter__.return_value = mock_smtp_instance
    
    # Should raise exception with context
    with pytest.raises(Exception, match="Failed to send search started confirmation"):
        await email_service.send_search_started(
            email="recipient@example.com",
            search_request=mock_search_request
        )


# ============================================================================
# prepare_daily_digest_data Tests
# ============================================================================

@pytest.mark.asyncio
async def test_prepare_daily_digest_data_with_matches(email_service):
    """Test prepare_daily_digest_data with matches in last 24 hours."""
    # Mock database session
    mock_db = Mock()
    
    # Mock search execution
    mock_execution = Mock()
    mock_execution.search_request_id = 1
    
    # Mock products (matches from last 24 hours)
    mock_product1 = Mock()
    mock_product1.id = 1
    mock_product1.title = "Product 1"
    mock_product1.price = 100.0
    mock_product1.platform = "craigslist"
    mock_product1.is_match = True
    mock_product1.created_at = datetime.now()
    mock_product1.search_execution = mock_execution
    
    mock_product2 = Mock()
    mock_product2.id = 2
    mock_product2.title = "Product 2"
    mock_product2.price = 200.0
    mock_product2.platform = "ebay"
    mock_product2.is_match = True
    mock_product2.created_at = datetime.now()
    mock_product2.search_execution = mock_execution
    
    # Mock email preference
    mock_pref = Mock()
    mock_pref.email_address = "user@example.com"
    mock_pref.search_request_id = 1
    mock_pref.include_in_digest = True
    mock_pref.search_request = Mock()
    mock_pref.search_request.product_name = "Test Product"
    
    # Setup query mocks
    product_query = Mock()
    product_query.filter.return_value.all.return_value = [mock_product1, mock_product2]
    
    pref_query = Mock()
    pref_query.filter.return_value.all.return_value = [mock_pref]
    
    # Mock db.query to return different queries based on model
    def query_side_effect(model):
        from app.models.product import Product
        from app.models.email_preference import EmailPreference
        if model == Product:
            return product_query
        elif model == EmailPreference:
            return pref_query
        return Mock()
    
    mock_db.query.side_effect = query_side_effect
    
    # Call the method
    result = await email_service.prepare_daily_digest_data(mock_db)
    
    # Verify result
    assert "user@example.com" in result
    assert len(result["user@example.com"]) == 2
    assert result["user@example.com"][0]['product'] == mock_product1
    assert result["user@example.com"][1]['product'] == mock_product2


@pytest.mark.asyncio
async def test_prepare_daily_digest_data_no_matches(email_service):
    """Test prepare_daily_digest_data with no matches in last 24 hours."""
    # Mock database session
    mock_db = Mock()
    
    # Mock email preference
    mock_pref = Mock()
    mock_pref.email_address = "user@example.com"
    mock_pref.search_request_id = 1
    mock_pref.include_in_digest = True
    
    # Setup query mocks - no products
    product_query = Mock()
    product_query.filter.return_value.all.return_value = []
    
    pref_query = Mock()
    pref_query.filter.return_value.all.return_value = [mock_pref]
    
    # Mock db.query
    def query_side_effect(model):
        from app.models.product import Product
        from app.models.email_preference import EmailPreference
        if model == Product:
            return product_query
        elif model == EmailPreference:
            return pref_query
        return Mock()
    
    mock_db.query.side_effect = query_side_effect
    
    # Call the method
    result = await email_service.prepare_daily_digest_data(mock_db)
    
    # Verify result is empty
    assert result == {}


@pytest.mark.asyncio
async def test_prepare_daily_digest_data_no_digest_enabled(email_service):
    """Test prepare_daily_digest_data when no users have digest enabled."""
    # Mock database session
    mock_db = Mock()
    
    # Mock products exist but no preferences
    mock_product = Mock()
    mock_product.is_match = True
    mock_product.created_at = datetime.now()
    
    # Setup query mocks
    product_query = Mock()
    product_query.filter.return_value.all.return_value = [mock_product]
    
    pref_query = Mock()
    pref_query.filter.return_value.all.return_value = []  # No preferences
    
    # Mock db.query
    def query_side_effect(model):
        from app.models.product import Product
        from app.models.email_preference import EmailPreference
        if model == Product:
            return product_query
        elif model == EmailPreference:
            return pref_query
        return Mock()
    
    mock_db.query.side_effect = query_side_effect
    
    # Call the method
    result = await email_service.prepare_daily_digest_data(mock_db)
    
    # Verify result is empty
    assert result == {}


@pytest.mark.asyncio
async def test_prepare_daily_digest_data_multiple_users(email_service):
    """Test prepare_daily_digest_data with multiple users."""
    # Mock database session
    mock_db = Mock()
    
    # Mock search executions
    mock_execution1 = Mock()
    mock_execution1.search_request_id = 1
    
    mock_execution2 = Mock()
    mock_execution2.search_request_id = 2
    
    # Mock products for different search requests
    mock_product1 = Mock()
    mock_product1.id = 1
    mock_product1.is_match = True
    mock_product1.created_at = datetime.now()
    mock_product1.search_execution = mock_execution1
    
    mock_product2 = Mock()
    mock_product2.id = 2
    mock_product2.is_match = True
    mock_product2.created_at = datetime.now()
    mock_product2.search_execution = mock_execution2
    
    # Mock email preferences for different users
    mock_pref1 = Mock()
    mock_pref1.email_address = "user1@example.com"
    mock_pref1.search_request_id = 1
    mock_pref1.include_in_digest = True
    mock_pref1.search_request = Mock()
    
    mock_pref2 = Mock()
    mock_pref2.email_address = "user2@example.com"
    mock_pref2.search_request_id = 2
    mock_pref2.include_in_digest = True
    mock_pref2.search_request = Mock()
    
    # Setup query mocks
    product_query = Mock()
    product_query.filter.return_value.all.return_value = [mock_product1, mock_product2]
    
    pref_query = Mock()
    pref_query.filter.return_value.all.return_value = [mock_pref1, mock_pref2]
    
    # Mock db.query
    def query_side_effect(model):
        from app.models.product import Product
        from app.models.email_preference import EmailPreference
        if model == Product:
            return product_query
        elif model == EmailPreference:
            return pref_query
        return Mock()
    
    mock_db.query.side_effect = query_side_effect
    
    # Call the method
    result = await email_service.prepare_daily_digest_data(mock_db)
    
    # Verify result
    assert "user1@example.com" in result
    assert "user2@example.com" in result
    assert len(result["user1@example.com"]) == 1
    assert len(result["user2@example.com"]) == 1
    assert result["user1@example.com"][0]['product'] == mock_product1
    assert result["user2@example.com"][0]['product'] == mock_product2


@pytest.mark.asyncio
async def test_prepare_daily_digest_data_same_user_multiple_searches(email_service):
    """Test prepare_daily_digest_data when same user has multiple search requests."""
    # Mock database session
    mock_db = Mock()
    
    # Mock search executions
    mock_execution1 = Mock()
    mock_execution1.search_request_id = 1
    
    mock_execution2 = Mock()
    mock_execution2.search_request_id = 2
    
    # Mock products for different search requests
    mock_product1 = Mock()
    mock_product1.id = 1
    mock_product1.is_match = True
    mock_product1.created_at = datetime.now()
    mock_product1.search_execution = mock_execution1
    
    mock_product2 = Mock()
    mock_product2.id = 2
    mock_product2.is_match = True
    mock_product2.created_at = datetime.now()
    mock_product2.search_execution = mock_execution2
    
    # Mock email preferences - same email for both search requests
    mock_pref1 = Mock()
    mock_pref1.email_address = "user@example.com"
    mock_pref1.search_request_id = 1
    mock_pref1.include_in_digest = True
    mock_pref1.search_request = Mock()
    
    mock_pref2 = Mock()
    mock_pref2.email_address = "user@example.com"  # Same email
    mock_pref2.search_request_id = 2
    mock_pref2.include_in_digest = True
    mock_pref2.search_request = Mock()
    
    # Setup query mocks
    product_query = Mock()
    product_query.filter.return_value.all.return_value = [mock_product1, mock_product2]
    
    pref_query = Mock()
    pref_query.filter.return_value.all.return_value = [mock_pref1, mock_pref2]
    
    # Mock db.query
    def query_side_effect(model):
        from app.models.product import Product
        from app.models.email_preference import EmailPreference
        if model == Product:
            return product_query
        elif model == EmailPreference:
            return pref_query
        return Mock()
    
    mock_db.query.side_effect = query_side_effect
    
    # Call the method
    result = await email_service.prepare_daily_digest_data(mock_db)
    
    # Verify result - should have both products for same email
    assert "user@example.com" in result
    assert len(result["user@example.com"]) == 2
    assert result["user@example.com"][0]['product'] == mock_product1
    assert result["user@example.com"][1]['product'] == mock_product2