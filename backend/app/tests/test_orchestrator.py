"""
Tests for Search Orchestrator
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone

from app.core.orchestrator import SearchOrchestrator
from app.models.search_request import SearchRequest
from app.models.search_execution import SearchExecution
from app.models.product import Product



@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock()


@pytest.fixture
def sample_search_request():
    """Sample search request for testing."""
    return SearchRequest(
        id=1,
        product_name="iPhone 13",
        product_description="Good condition",
        budget=500.0,
        location="Boston, MA",
        search_craigslist=True,
        search_ebay=True,
        search_facebook=False
    )


@pytest.fixture
def orchestrator(mock_db):
    """Create orchestrator instance."""
    return SearchOrchestrator(mock_db)

def test_get_active_platforms_all_enabled(orchestrator, sample_search_request):
    """Test getting platforms when all are enabled."""
    sample_search_request.search_craigslist = True
    sample_search_request.search_ebay = True
    sample_search_request.search_facebook = True
    
    platforms = orchestrator._get_active_platforms(sample_search_request)
    
    assert len(platforms) == 3
    assert 'craigslist' in platforms
    assert 'ebay' in platforms
    assert 'facebook' in platforms

def test_get_active_platforms_partial(orchestrator, sample_search_request):
    """Test getting platforms when only some are enabled."""
    sample_search_request.search_craigslist = True
    sample_search_request.search_ebay = False
    sample_search_request.search_facebook = True
    
    platforms = orchestrator._get_active_platforms(sample_search_request)
    
    assert len(platforms) == 2
    assert 'craigslist' in platforms
    assert 'facebook' in platforms
    assert 'ebay' not in platforms

@pytest.mark.asyncio
async def test_execute_search_success(orchestrator, sample_search_request, mock_db):
    """Test successful search execution."""
    # Mock scraper responses
    mock_products = [
        {
            'platform': 'craigslist',
            'external_id': 'cl123',
            'title': 'iPhone 13 Pro',
            'price': 450.0,
            'url': 'https://example.com/1'
        },
        {
            'platform': 'ebay',
            'external_id': 'eb456',
            'title': 'iPhone 13',
            'price': 480.0,
            'url': 'https://example.com/2'
        }
    ]
    
    # Mock the scraper methods
    with patch.object(
        orchestrator, 
        '_search_all_platforms', 
        new=AsyncMock(return_value=mock_products)
    ):
        with patch.object(
            orchestrator, 
            '_match_products', 
            return_value=mock_products
        ):
            with patch.object(orchestrator, '_save_products'):
                execution = await orchestrator.execute_search(sample_search_request)
    
    # Verify execution was created and completed
    assert execution.status == 'completed'
    assert execution.products_found == 2


@pytest.mark.asyncio
async def test_execute_search_with_error(orchestrator, sample_search_request, mock_db):
    """Test search execution handles errors gracefully."""
    # Mock a scraper failure
    with patch.object(
        orchestrator, 
        '_search_all_platforms', 
        new=AsyncMock(side_effect=Exception("Scraper failed"))
    ):
        execution = await orchestrator.execute_search(sample_search_request)
    
    # Verify execution failed gracefully
    assert execution.status == 'failed'
    assert 'Scraper failed' in execution.error_message

@pytest.mark.asyncio
async def test_search_platform_retries_on_failure(orchestrator, sample_search_request):
    """Test that platform search retries on failure."""
    # Mock scraper that fails twice then succeeds
    mock_scraper = Mock()
    mock_scraper.search = AsyncMock(
        side_effect=[
            Exception("Network error"),
            Exception("Timeout"),
            [{'title': 'Product 1'}]  # Success on third try
        ]
    )
    
    orchestrator.scrapers['craigslist'] = mock_scraper
    
    # Execute search
    results = await orchestrator._search_platform(
        sample_search_request, 
        'craigslist'
    )
    
    # Verify it retried and eventually succeeded
    assert len(results) == 1
    assert mock_scraper.search.call_count == 3

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_search_workflow(mock_db):
    """
    Integration test: Complete search workflow.
    
    This test:
    1. Creates a search request
    2. Runs orchestrator with mocked scrapers
    3. Verifies products are saved to database
    4. Checks execution record
    """
    # Step 1: Create search request with ID
    search_request = SearchRequest(
        id=1,
        product_name="Test Product",
        budget=100.0,
        location="Test City",
        search_craigslist=True,
        search_ebay=False,
        search_facebook=False
    )
    
    # Mock the database operations
    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.query = Mock()
    
    # Step 2: Run orchestrator with mocked scrapers
    orchestrator = SearchOrchestrator(mock_db)
    
    # Mock scraper responses - return Product dictionaries (without external_id)
    mock_products = [
        {
            'platform': 'craigslist',
            'title': 'Test Product 1',
            'description': 'A test product',
            'price': 50.0,
            'url': 'https://example.com/1',
            'image_url': 'https://example.com/img1.jpg',
            'location': 'Test City',
            'posted_date': datetime.now(timezone.utc),
            'is_available': True,
            'match_score': 90.0
        },
        {
            'platform': 'craigslist',
            'title': 'Test Product 2',
            'description': 'Another test product',
            'price': 75.0,
            'url': 'https://example.com/2',
            'image_url': 'https://example.com/img2.jpg',
            'location': 'Test City',
            'posted_date': datetime.now(timezone.utc),
            'is_available': True,
            'match_score': 85.0
        }
    ]
    
    # Mock the internal methods
    with patch.object(
        orchestrator,
        '_search_all_platforms',
        new=AsyncMock(return_value=mock_products)
    ):
        with patch.object(
            orchestrator,
            '_match_products',
            return_value=mock_products
        ):
            # Mock database query to return no existing products
            mock_db.query.return_value.filter.return_value.first.return_value = None
            
            execution = await orchestrator.execute_search(search_request)
    
    # Step 3: Verify execution completed
    assert execution.status == 'completed'
    assert execution.products_found > 0
    assert execution.products_found == 2
    
    # Step 4: Verify database operations were called
    assert mock_db.add.call_count >= 1  # At least execution was added
    assert mock_db.commit.call_count >= 1

@pytest.mark.asyncio
async def test_save_products_creates_new(orchestrator, mock_db):
    """Test saving new products to database."""
    products = [
        {
            'platform': 'craigslist',
            'external_id': 'test123',
            'title': 'Test Product',
            'price': 50.0,
            'url': 'https://example.com',
            'is_available': True,
            'match_score': 85.0
        }
    ]
    
    # Mock database query to return no existing products
    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_db.refresh = Mock()  # Mock refresh method
    
    # Mock the notification method to avoid validation errors
    with patch.object(orchestrator, '_notify_match_found', new=AsyncMock()):
        # Call with all required parameters (now async)
        await orchestrator._save_products(
            products=products,
            execution_id=1,
            search_request_id="test-search-123"
        )
    
    # Verify product was added
    mock_db.add.assert_called_once()
    # Commit is called twice: once for the product, once after refresh
    assert mock_db.commit.call_count >= 1

@pytest.mark.asyncio
async def test_save_products_updates_existing(orchestrator, mock_db):
    """Test updating existing products."""
    # Mock existing product
    existing_product = Mock()
    existing_product.price = 100.0
    mock_db.query.return_value.filter.return_value.first.return_value = existing_product
    
    products = [
        {
            'platform': 'craigslist',
            'external_id': 'test123',
            'title': 'Test Product',
            'price': 75.0,  # Price changed
            'url': 'https://example.com',
            'is_available': True,
            'match_score': 90.0
        }
    ]
    
    # Mock the notification method (not called for existing products)
    with patch.object(orchestrator, '_notify_match_found', new=AsyncMock()):
        # Call with all required parameters (now async)
        await orchestrator._save_products(
            products=products,
            execution_id=1,
            search_request_id="test-search-123"
        )
    
    # Verify product was updated, not added
    assert existing_product.price == 75.0
    mock_db.add.assert_not_called()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_search_all_platforms_with_exception(orchestrator, sample_search_request):
    """Test _search_all_platforms handles exceptions from individual platforms."""
    # Mock one scraper that succeeds and one that fails
    mock_scraper_success = Mock()
    mock_scraper_success.search = AsyncMock(return_value=[{'title': 'Product 1'}])
    
    mock_scraper_fail = Mock()
    mock_scraper_fail.search = AsyncMock(side_effect=Exception("Platform error"))
    
    orchestrator.scrapers['craigslist'] = mock_scraper_success
    orchestrator.scrapers['ebay'] = mock_scraper_fail
    
    # Execute search on both platforms
    results = await orchestrator._search_all_platforms(
        sample_search_request,
        ['craigslist', 'ebay']
    )
    
    # Should return results from successful platform only
    assert len(results) == 1
    assert results[0]['title'] == 'Product 1'

@pytest.mark.asyncio
async def test_search_platform_all_retries_exhausted(orchestrator, sample_search_request):
    """Test that platform search raises exception after all retries fail."""
    # Mock scraper that always fails
    mock_scraper = Mock()
    mock_scraper.search = AsyncMock(side_effect=Exception("Network error"))
    
    orchestrator.scrapers['craigslist'] = mock_scraper
    
    # Execute search - should raise exception after 3 retries
    with pytest.raises(Exception, match="Network error"):
        await orchestrator._search_platform(sample_search_request, 'craigslist')
    
    # Verify it tried 3 times
    assert mock_scraper.search.call_count == 3

def test_match_products(orchestrator, sample_search_request):
    """Test _match_products method."""
    # Mock products
    mock_products = [
        {'title': 'iPhone 13', 'price': 400.0},
        {'title': 'iPhone 13 Pro', 'price': 450.0}
    ]
    
    # Mock the matching engine
    with patch.object(
        orchestrator.matching_engine,
        'find_matches',
        return_value=mock_products
    ) as mock_find_matches:
        result = orchestrator._match_products(sample_search_request, mock_products)
        
        # Verify matching engine was called
        mock_find_matches.assert_called_once_with(
            products=mock_products,
            search_request=sample_search_request
        )
        
        # Verify result
        assert result == mock_products

def test_get_active_platforms_none_enabled(orchestrator, sample_search_request):
    """Test getting platforms when none are enabled."""
    sample_search_request.search_craigslist = False
    sample_search_request.search_ebay = False
    sample_search_request.search_facebook = False
    
    platforms = orchestrator._get_active_platforms(sample_search_request)
    
    assert len(platforms) == 0
    assert platforms == []

@pytest.mark.asyncio
async def test_save_products_with_optional_fields(orchestrator, mock_db):
    """Test saving products with all optional fields populated."""
    products = [
        {
            'platform': 'ebay',
            'title': 'Complete Product',
            'description': 'Full description',
            'price': 100.0,
            'url': 'https://example.com/complete',
            'image_url': 'https://example.com/image.jpg',
            'location': 'New York, NY',
            'posted_date': datetime.now(timezone.utc),
            'is_available': True,
            'match_score': 95.0
        }
    ]
    
    # Mock database query to return no existing products
    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_db.refresh = Mock()
    
    # Mock the notification method
    with patch.object(orchestrator, '_notify_match_found', new=AsyncMock()):
        await orchestrator._save_products(
            products=products,
            execution_id=1,
            search_request_id="test-search-123"
        )
    
    # Verify product was added with all fields
    mock_db.add.assert_called_once()
    assert mock_db.commit.call_count >= 1

@pytest.mark.asyncio
async def test_save_products_with_minimal_fields(orchestrator, mock_db):
    """Test saving products with only required fields."""
    products = [
        {
            'platform': 'craigslist',
            'title': 'Minimal Product',
            'price': 50.0,
            'url': 'https://example.com/minimal'
        }
    ]
    
    # Mock database query to return no existing products
    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_db.refresh = Mock()
    
    # Mock the notification method
    with patch.object(orchestrator, '_notify_match_found', new=AsyncMock()):
        await orchestrator._save_products(
            products=products,
            execution_id=1,
            search_request_id="test-search-123"
        )
    
    # Verify product was added
    mock_db.add.assert_called_once()
    assert mock_db.commit.call_count >= 1

@pytest.mark.asyncio
async def test_search_platform_success_first_try(orchestrator, sample_search_request):
    """Test platform search succeeds on first attempt."""
    mock_scraper = Mock()
    mock_scraper.search = AsyncMock(return_value=[
        {'title': 'Product 1'},
        {'title': 'Product 2'}
    ])
    
    orchestrator.scrapers['ebay'] = mock_scraper
    
    results = await orchestrator._search_platform(sample_search_request, 'ebay')
    
    # Should succeed on first try
    assert len(results) == 2
    assert mock_scraper.search.call_count == 1

@pytest.mark.asyncio
async def test_save_products_empty_list(orchestrator, mock_db):
    """Test saving empty product list."""
    # Mock the notification method (won't be called for empty list)
    with patch.object(orchestrator, '_notify_match_found', new=AsyncMock()):
        await orchestrator._save_products(
            products=[],
            execution_id=1,
            search_request_id="test-search-123"
        )
    
    # Should not add anything
    mock_db.add.assert_not_called()
    # Commit might not be called for empty list
    # (depends on implementation)

@pytest.mark.asyncio
async def test_search_all_platforms_empty_platform_list(orchestrator, sample_search_request):
    """Test searching with empty platform list."""
    results = await orchestrator._search_all_platforms(sample_search_request, [])
    
    # Should return empty list
    assert results == []

