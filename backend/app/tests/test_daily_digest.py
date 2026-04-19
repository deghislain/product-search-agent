import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.email_service import EmailService
from app.models.product import Product
from app.models.email_preference import EmailPreference
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
def mock_db():
    """Create mock database session"""
    return Mock()


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
    product.created_at = datetime.now()
    product.is_match = True
    return product


@pytest.fixture
def mock_search_request():
    """Create mock search request for testing"""
    search_request = Mock(spec=SearchRequest)
    search_request.id = 1
    search_request.product_name = "Test Product"
    search_request.query = "test product"
    search_request.location = "Test City"
    search_request.max_price = 150.0
    return search_request


@pytest.mark.asyncio
async def test_prepare_digest_data_with_matches(email_service, mock_db):
    """Test digest data preparation with matches"""
    # Mock search execution
    mock_execution = Mock()
    mock_execution.search_request_id = 1
    
    # Mock recent matches
    mock_product = Mock(spec=Product)
    mock_product.created_at = datetime.now()
    mock_product.is_match = True
    mock_product.title = "Test Product"
    mock_product.search_execution = mock_execution
    
    # Mock email preferences
    mock_pref = Mock(spec=EmailPreference)
    mock_pref.email_address = "user@example.com"
    mock_pref.include_in_digest = True
    mock_pref.search_request_id = 1
    mock_pref.search_request = Mock()
    mock_pref.search_request.product_name = "Test Product"
    
    # Setup query mocks
    product_query = Mock()
    product_query.filter.return_value.all.return_value = [mock_product]
    
    pref_query = Mock()
    pref_query.filter.return_value.all.return_value = [mock_pref]
    
    # Mock db.query to return different queries based on model
    def query_side_effect(model):
        if model == Product:
            return product_query
        elif model == EmailPreference:
            return pref_query
        return Mock()
    
    mock_db.query.side_effect = query_side_effect
    
    # Call method
    digest_data = await email_service.prepare_daily_digest_data(mock_db)
    
    # Assertions
    assert len(digest_data) > 0
    assert "user@example.com" in digest_data
    assert len(digest_data["user@example.com"]) == 1
    assert digest_data["user@example.com"][0]['product'] == mock_product


@pytest.mark.asyncio
async def test_prepare_digest_data_no_matches(email_service, mock_db):
    """Test digest data preparation with no matches"""
    # Mock empty results
    mock_db.query.return_value.filter.return_value.all.return_value = []
    
    # Call method
    digest_data = await email_service.prepare_daily_digest_data(mock_db)
    
    # Should return empty dict
    assert len(digest_data) == 0


@pytest.mark.asyncio
@patch('app.services.email_service.SMTP')
async def test_send_daily_digest_integration(
    mock_smtp_class,
    email_service,
    mock_product,
    mock_search_request
):
    """Test sending daily digest end-to-end"""
    # Mock SMTP
    mock_smtp_instance = AsyncMock()
    mock_smtp_class.return_value.__aenter__.return_value = mock_smtp_instance
    
    # Prepare matches
    matches = [
        {
            'product': mock_product,
            'search_request': mock_search_request
        }
    ]
    
    # Send digest
    await email_service.send_daily_digest(
        email="user@example.com",
        matches=matches
    )
    
    # Verify email was sent
    mock_smtp_instance.send_message.assert_called_once()


# ============================================================================
# Digest API Routes Tests
# ============================================================================

from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.api.routes import digest

# Create test app
test_app = FastAPI()
test_app.include_router(digest.router)
client = TestClient(test_app)


@pytest.mark.asyncio
async def test_send_digest_now_endpoint(mock_db):
    """Test POST /api/digest/send-now endpoint"""
    with patch('app.api.routes.digest.EmailService') as mock_email_service_class:
        with patch('app.api.routes.digest.get_db', return_value=mock_db):
            # Mock email service
            mock_service = Mock()
            mock_service.prepare_daily_digest_data = AsyncMock(return_value={})
            mock_email_service_class.return_value = mock_service
            
            # Call endpoint
            response = client.post("/api/digest/send-now")
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "background" in data["message"].lower()


@pytest.mark.asyncio
async def test_preview_digest_endpoint_with_matches(mock_db):
    """Test GET /api/digest/preview endpoint with matches"""
    with patch('app.api.routes.digest.EmailService') as mock_email_service_class:
        with patch('app.api.routes.digest.get_db', return_value=mock_db):
            # Mock product and search request
            mock_product = Mock()
            mock_product.title = "Test Product"
            mock_product.price = 99.99
            
            mock_search_req = Mock()
            mock_search_req.query = "test query"
            
            # Mock digest data
            mock_digest_data = {
                "user@example.com": [
                    {
                        'product': mock_product,
                        'search_request': mock_search_req
                    }
                ]
            }
            
            # Mock email service
            mock_service = Mock()
            mock_service.prepare_daily_digest_data = AsyncMock(return_value=mock_digest_data)
            mock_email_service_class.return_value = mock_service
            
            # Call endpoint
            response = client.get("/api/digest/preview")
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["total_recipients"] == 1
            assert len(data["recipients"]) == 1
            assert data["recipients"][0]["email"] == "user@example.com"
            assert data["recipients"][0]["match_count"] == 1


@pytest.mark.asyncio
async def test_preview_digest_endpoint_no_matches(mock_db):
    """Test GET /api/digest/preview endpoint with no matches"""
    with patch('app.api.routes.digest.EmailService') as mock_email_service_class:
        with patch('app.api.routes.digest.get_db', return_value=mock_db):
            # Mock empty digest data
            mock_service = Mock()
            mock_service.prepare_daily_digest_data = AsyncMock(return_value={})
            mock_email_service_class.return_value = mock_service
            
            # Call endpoint
            response = client.get("/api/digest/preview")
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["total_recipients"] == 0
            assert len(data["recipients"]) == 0


@pytest.mark.asyncio
async def test_send_digest_task_success():
    """Test send_digest_task background task"""
    # Mock email service
    mock_service = Mock()
    mock_service.prepare_daily_digest_data = AsyncMock(return_value={
        "user@example.com": [{"product": Mock(), "search_request": Mock()}]
    })
    mock_service.send_daily_digest = AsyncMock()
    
    # Mock database
    mock_db = Mock()
    
    # Call task
    await digest.send_digest_task(mock_service, mock_db)
    
    # Verify calls
    mock_service.prepare_daily_digest_data.assert_called_once_with(mock_db)
    mock_service.send_daily_digest.assert_called_once()


@pytest.mark.asyncio
async def test_send_digest_task_with_exception():
    """Test send_digest_task handles exceptions"""
    # Mock email service that raises exception
    mock_service = Mock()
    mock_service.prepare_daily_digest_data = AsyncMock(side_effect=Exception("Test error"))
    
    # Mock database
    mock_db = Mock()
    
    # Call task - should not raise exception
    await digest.send_digest_task(mock_service, mock_db)
    
    # Verify prepare was called
    mock_service.prepare_daily_digest_data.assert_called_once_with(mock_db)


@pytest.mark.asyncio
async def test_preview_digest_with_multiple_matches(mock_db):
    """Test preview endpoint with multiple matches per user"""
    with patch('app.api.routes.digest.EmailService') as mock_email_service_class:
        with patch('app.api.routes.digest.get_db', return_value=mock_db):
            # Create multiple mock products
            matches = []
            for i in range(10):
                mock_product = Mock()
                mock_product.title = f"Product {i}"
                mock_product.price = 100.0 + i
                
                mock_search_req = Mock()
                mock_search_req.query = f"query {i}"
                
                matches.append({
                    'product': mock_product,
                    'search_request': mock_search_req
                })
            
            # Mock digest data
            mock_digest_data = {"user@example.com": matches}
            
            # Mock email service
            mock_service = Mock()
            mock_service.prepare_daily_digest_data = AsyncMock(return_value=mock_digest_data)
            mock_email_service_class.return_value = mock_service
            
            # Call endpoint
            response = client.get("/api/digest/preview")
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["total_recipients"] == 1
            assert data["recipients"][0]["match_count"] == 10
            # Should only show first 5 matches
            assert len(data["recipients"][0]["matches"]) == 5