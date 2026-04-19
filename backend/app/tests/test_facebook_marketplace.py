"""
Tests for Facebook Marketplace Scraper

These tests use mocking to test the scraper without requiring actual Selenium/Chrome.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from app.scrapers.facebook_marketplace import FacebookMarketplaceScraper


@pytest.fixture
def mock_driver():
    """Create a mock Selenium driver."""
    driver = Mock()
    driver.get = Mock()
    driver.quit = Mock()
    driver.find_elements = Mock(return_value=[])
    driver.find_element = Mock()
    driver.execute_script = Mock()
    driver.page_source = "<html></html>"
    driver.title = "Facebook Marketplace"
    return driver


@pytest.fixture
def scraper(mock_driver):
    """Create scraper instance with mocked driver."""
    scraper = FacebookMarketplaceScraper(headless=True)
    scraper.driver = mock_driver
    return scraper


@pytest.mark.asyncio
async def test_scraper_initialization():
    """Test that scraper initializes correctly"""
    scraper = FacebookMarketplaceScraper(headless=True)
    
    assert scraper is not None
    assert scraper.base_url == "https://www.facebook.com/marketplace"
    assert scraper.headless == True
    assert scraper.driver is None  # Not initialized until first use
    
    await scraper.close()
    print("\n✅ Scraper initialized correctly")


@pytest.mark.asyncio
async def test_scraper_initialization_not_headless():
    """Test scraper initialization with headless=False."""
    scraper = FacebookMarketplaceScraper(headless=False)
    
    assert scraper.headless == False
    await scraper.close()
    print("\n✅ Non-headless scraper initialized")


def test_setup_driver():
    """Test driver setup with mocked webdriver."""
    scraper = FacebookMarketplaceScraper(headless=True)
    
    # Create a mock stealth function
    mock_stealth_func = Mock()
    
    with patch('app.scrapers.facebook_marketplace.webdriver.Chrome') as mock_chrome:
        # Mock the selenium_stealth module
        with patch('selenium_stealth.stealth', mock_stealth_func):
            mock_driver = Mock()
            mock_driver.execute_cdp_cmd = Mock()
            mock_chrome.return_value = mock_driver
            
            scraper._setup_driver()
            
            assert scraper.driver is not None
            mock_chrome.assert_called_once()
            mock_stealth_func.assert_called_once()
            print("\n✅ Driver setup correctly")


def test_setup_driver_with_stealth():
    """Test driver setup with selenium-stealth available."""
    scraper = FacebookMarketplaceScraper(headless=True)
    
    mock_stealth = Mock()
    
    with patch('app.scrapers.facebook_marketplace.webdriver.Chrome') as mock_chrome:
        with patch.dict('sys.modules', {'selenium_stealth': Mock(stealth=mock_stealth)}):
            mock_driver = Mock()
            mock_driver.execute_cdp_cmd = Mock()
            mock_chrome.return_value = mock_driver
            
            scraper._setup_driver()
            
            assert scraper.driver is not None
            print("\n✅ Driver setup with stealth")


def test_random_delay(scraper):
    """Test random delay function."""
    import time
    start = time.time()
    scraper._random_delay(0.1, 0.2)
    elapsed = time.time() - start
    
    assert 0.1 <= elapsed <= 0.3  # Allow small margin
    print("\n✅ Random delay works")


@pytest.mark.asyncio
async def test_search_basic(scraper, mock_driver):
    """Test basic search functionality with mocked driver."""
    # Mock listing elements
    mock_listing1 = Mock()
    mock_listing1.get_attribute = Mock(return_value="https://facebook.com/marketplace/item/123")
    mock_title1 = Mock()
    mock_title1.text = "iPhone 13 Pro"
    mock_listing1.find_element = Mock(return_value=mock_title1)
    
    mock_listing2 = Mock()
    mock_listing2.get_attribute = Mock(return_value="https://facebook.com/marketplace/item/456")
    mock_title2 = Mock()
    mock_title2.text = "iPhone 13"
    mock_listing2.find_element = Mock(return_value=mock_title2)
    
    mock_driver.find_elements = Mock(return_value=[mock_listing1, mock_listing2])
    
    with patch('app.scrapers.facebook_marketplace.WebDriverWait'):
        with patch.object(scraper, '_scroll_page'):
            with patch.object(scraper, '_random_delay'):
                results = await scraper.search("iPhone", "newyork", max_results=5)
    
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]['title'] == 'iPhone 13 Pro'
    assert results[0]['platform'] == 'facebook'
    print(f"\n✅ Search returned {len(results)} results")


@pytest.mark.asyncio
async def test_search_with_price_filters(scraper, mock_driver):
    """Test search with price filters."""
    mock_driver.find_elements = Mock(return_value=[])
    
    with patch('app.scrapers.facebook_marketplace.WebDriverWait'):
        with patch.object(scraper, '_scroll_page'):
            with patch.object(scraper, '_random_delay'):
                results = await scraper.search(
                    "laptop",
                    "newyork",
                    min_price=500,
                    max_price=1000,
                    max_results=10
                )
    
    assert isinstance(results, list)
    # Verify URL was built with price filters
    call_args = mock_driver.get.call_args[0][0]
    assert "minPrice=500" in call_args
    assert "maxPrice=1000" in call_args
    print("\n✅ Price filters applied correctly")


@pytest.mark.asyncio
async def test_search_timeout(scraper, mock_driver):
    """Test search with timeout exception."""
    with patch('app.scrapers.facebook_marketplace.WebDriverWait', side_effect=TimeoutException):
        with patch.object(scraper, '_random_delay'):
            results = await scraper.search("test", "newyork")
    
    assert results == []
    print("\n✅ Timeout handled correctly")


@pytest.mark.asyncio
async def test_search_exception(scraper, mock_driver):
    """Test search with general exception."""
    mock_driver.get.side_effect = Exception("Network error")
    
    with patch.object(scraper, '_random_delay'):
        results = await scraper.search("test", "newyork")
    
    assert results == []
    print("\n✅ Exception handled correctly")


@pytest.mark.asyncio
async def test_search_initializes_driver():
    """Test that search initializes driver if not already done."""
    scraper = FacebookMarketplaceScraper(headless=True)
    
    with patch.object(scraper, '_setup_driver') as mock_setup:
        with patch('app.scrapers.facebook_marketplace.WebDriverWait', side_effect=TimeoutException):
            with patch.object(scraper, '_random_delay'):
                await scraper.search("test", "newyork")
    
    mock_setup.assert_called_once()
    print("\n✅ Driver initialized on first search")
    await scraper.close()


def test_scroll_page(scraper, mock_driver):
    """Test page scrolling."""
    with patch('app.scrapers.facebook_marketplace.time.sleep'):
        scraper._scroll_page(times=3)
    
    assert mock_driver.execute_script.call_count == 3
    print("\n✅ Page scrolling works")


def test_parse_listing_success(scraper):
    """Test parsing a listing successfully."""
    mock_listing = Mock()
    mock_listing.get_attribute = Mock(return_value="https://facebook.com/marketplace/item/123")
    
    mock_title = Mock()
    mock_title.text = "iPhone 13 Pro"
    
    mock_price = Mock()
    mock_price.text = "$899"
    
    mock_img = Mock()
    mock_img.get_attribute = Mock(return_value="https://example.com/image.jpg")
    
    def find_element_side_effect(by, selector):
        if selector == "span":
            return mock_title
        elif "contains(text(), '$')" in selector:
            return mock_price
        elif selector == "img":
            return mock_img
        raise NoSuchElementException()
    
    mock_listing.find_element = Mock(side_effect=find_element_side_effect)
    
    product = scraper._parse_listing(mock_listing)
    
    assert product is not None
    assert product['title'] == 'iPhone 13 Pro'
    assert product['price'] == 899.0
    assert product['url'] == 'https://facebook.com/marketplace/item/123'
    assert product['platform'] == 'facebook'
    assert product['image_url'] == 'https://example.com/image.jpg'
    print("\n✅ Listing parsed successfully")


def test_parse_listing_no_price(scraper):
    """Test parsing listing without price."""
    mock_listing = Mock()
    mock_listing.get_attribute = Mock(return_value="https://facebook.com/marketplace/item/123")
    
    mock_title = Mock()
    mock_title.text = "Free Item"
    
    def find_element_side_effect(by, selector):
        if selector == "span":
            return mock_title
        raise NoSuchElementException()
    
    mock_listing.find_element = Mock(side_effect=find_element_side_effect)
    
    product = scraper._parse_listing(mock_listing)
    
    assert product is not None
    assert product['price'] is None
    print("\n✅ Listing without price handled")


def test_parse_listing_exception(scraper):
    """Test parsing listing with exception."""
    mock_listing = Mock()
    mock_listing.get_attribute = Mock(side_effect=Exception("Parse error"))
    
    product = scraper._parse_listing(mock_listing)
    
    assert product is None
    print("\n✅ Parse exception handled")


@pytest.mark.asyncio
async def test_get_product_details(scraper, mock_driver):
    """Test getting product details."""
    mock_title = Mock()
    mock_title.text = "iPhone 13 Pro"
    
    mock_price = Mock()
    mock_price.text = "$899"
    
    mock_desc = Mock()
    mock_desc.text = "Great condition iPhone"
    
    mock_location = Mock()
    mock_location.text = "New York, NY"
    
    def find_element_side_effect(by, selector):
        if "x1lliihq" in selector:
            return mock_title
        elif "contains(text(), '$')" in selector:
            return mock_price
        elif "xz9dl7a" in selector:
            return mock_desc
        elif "contains(text(), ',')" in selector:
            return mock_location
        raise NoSuchElementException()
    
    mock_driver.find_element = Mock(side_effect=find_element_side_effect)
    
    with patch('app.scrapers.facebook_marketplace.WebDriverWait'):
        details = await scraper.get_product_details("https://facebook.com/marketplace/item/123")
    
    assert details['title'] == 'iPhone 13 Pro'
    assert details['price'] == 899.0
    assert details['description'] == 'Great condition iPhone'
    assert details['location'] == 'New York, NY'
    print("\n✅ Product details extracted")


@pytest.mark.asyncio
async def test_get_product_details_exception(scraper, mock_driver):
    """Test get_product_details with exception."""
    mock_driver.get.side_effect = Exception("Network error")
    
    details = await scraper.get_product_details("https://facebook.com/marketplace/item/123")
    
    assert 'error' in details
    assert details['error'] == 'Network error'
    print("\n✅ Product details exception handled")


@pytest.mark.asyncio
async def test_get_product_details_initializes_driver():
    """Test that get_product_details initializes driver if needed."""
    scraper = FacebookMarketplaceScraper(headless=True)
    
    with patch.object(scraper, '_setup_driver') as mock_setup:
        with patch('app.scrapers.facebook_marketplace.WebDriverWait', side_effect=TimeoutException):
            await scraper.get_product_details("https://facebook.com/marketplace/item/123")
    
    mock_setup.assert_called_once()
    print("\n✅ Driver initialized for product details")
    await scraper.close()


@pytest.mark.asyncio
async def test_is_available_true(scraper, mock_driver):
    """Test availability check for available listing."""
    mock_driver.page_source = "<html><body>Product available</body></html>"
    
    mock_title = Mock()
    mock_title.text = "iPhone 13"
    mock_driver.find_element = Mock(return_value=mock_title)
    
    with patch('app.scrapers.facebook_marketplace.WebDriverWait'):
        available = await scraper.is_available("https://facebook.com/marketplace/item/123")
    
    assert available is True
    print("\n✅ Available listing detected")


@pytest.mark.asyncio
async def test_is_available_sold(scraper, mock_driver):
    """Test availability check for sold listing."""
    mock_driver.page_source = "<html><body>This item has been sold</body></html>"
    
    mock_title = Mock()
    mock_title.text = "iPhone 13"
    mock_driver.find_element = Mock(return_value=mock_title)
    
    with patch('app.scrapers.facebook_marketplace.WebDriverWait'):
        available = await scraper.is_available("https://facebook.com/marketplace/item/123")
    
    assert available is False
    print("\n✅ Sold listing detected")


@pytest.mark.asyncio
async def test_is_available_no_longer_available(scraper, mock_driver):
    """Test availability check for removed listing."""
    mock_driver.page_source = "<html><body>This listing is no longer available</body></html>"
    
    mock_title = Mock()
    mock_title.text = "iPhone 13"
    mock_driver.find_element = Mock(return_value=mock_title)
    
    with patch('app.scrapers.facebook_marketplace.WebDriverWait'):
        available = await scraper.is_available("https://facebook.com/marketplace/item/123")
    
    assert available is False
    print("\n✅ Removed listing detected")


@pytest.mark.asyncio
async def test_is_available_with_error(scraper, mock_driver):
    """Test availability check when get_product_details returns error."""
    mock_driver.get.side_effect = Exception("Network error")
    
    available = await scraper.is_available("https://facebook.com/marketplace/item/123")
    
    assert available is False
    print("\n✅ Availability error handled")


@pytest.mark.asyncio
async def test_is_available_no_driver():
    """Test availability check when driver is None."""
    scraper = FacebookMarketplaceScraper(headless=True)
    
    with patch.object(scraper, 'get_product_details', return_value={'title': 'Test'}):
        available = await scraper.is_available("https://facebook.com/marketplace/item/123")
    
    assert available is True
    print("\n✅ Availability without driver handled")
    await scraper.close()


@pytest.mark.asyncio
async def test_is_available_exception(scraper, mock_driver):
    """Test availability check with exception."""
    with patch.object(scraper, 'get_product_details', side_effect=Exception("Error")):
        available = await scraper.is_available("https://facebook.com/marketplace/item/123")
    
    assert available is False
    print("\n✅ Availability exception handled")


@pytest.mark.asyncio
async def test_close(scraper, mock_driver):
    """Test closing the scraper."""
    await scraper.close()
    
    mock_driver.quit.assert_called_once()
    print("\n✅ Scraper closed correctly")


@pytest.mark.asyncio
async def test_close_no_driver():
    """Test closing when driver is None."""
    scraper = FacebookMarketplaceScraper(headless=True)
    
    # Should not raise exception
    await scraper.close()
    print("\n✅ Close without driver handled")


def test_price_extraction(scraper):
    """Test price extraction helper method"""
    assert scraper._extract_price("$100") == 100.0
    assert scraper._extract_price("$1,234.56") == 1234.56
    assert scraper._extract_price("Price: $50") == 50.0
    assert scraper._extract_price("Free") == 0.0
    assert scraper._extract_price("Best offer") is None
    print("\n✅ Price extraction works")


def test_text_cleaning(scraper):
    """Test text cleaning helper method"""
    assert scraper._clean_text("  Hello   World  ") == "Hello World"
    assert scraper._clean_text("\n  Text\t  ") == "Text"
    assert scraper._clean_text("") == ""
    print("\n✅ Text cleaning works")


@pytest.mark.asyncio
async def test_scrape_search_page_with_listings(scraper, mock_driver):
    """Test _scrape_search_page with listings."""
    mock_listing = Mock()
    mock_listing.get_attribute = Mock(return_value="https://facebook.com/marketplace/item/123")
    mock_title = Mock()
    mock_title.text = "Test Product"
    mock_listing.find_element = Mock(return_value=mock_title)
    
    mock_driver.find_elements = Mock(return_value=[mock_listing])
    
    with patch('app.scrapers.facebook_marketplace.WebDriverWait'):
        with patch.object(scraper, '_scroll_page'):
            with patch.object(scraper, '_random_delay'):
                results = scraper._scrape_search_page("https://test.com", 10)
    
    assert len(results) == 1
    print("\n✅ _scrape_search_page works")


def test_scrape_product_page_success(scraper, mock_driver):
    """Test _scrape_product_page successfully."""
    mock_title = Mock()
    mock_title.text = "Test Product"
    mock_driver.find_element = Mock(return_value=mock_title)
    
    with patch('app.scrapers.facebook_marketplace.WebDriverWait'):
        details = scraper._scrape_product_page("https://test.com")
    
    assert 'title' in details
    assert details['platform'] == 'facebook'
    print("\n✅ _scrape_product_page works")


def test_setup_driver_without_stealth():
    """Test driver setup when selenium-stealth is not available."""
    scraper = FacebookMarketplaceScraper(headless=True)
    
    with patch('app.scrapers.facebook_marketplace.webdriver.Chrome') as mock_chrome:
        # Simulate ImportError for selenium-stealth
        with patch.dict('sys.modules', {'selenium_stealth': None}):
            mock_driver = Mock()
            mock_driver.execute_cdp_cmd = Mock()
            mock_chrome.return_value = mock_driver
            
            # This should not raise an error even without selenium-stealth
            scraper._setup_driver()
            
            assert scraper.driver is not None
            print("\n✅ Driver setup without stealth (line 108)")


def test_scrape_search_page_parse_error(scraper, mock_driver):
    """Test _scrape_search_page with parsing error."""
    # Create three listings: one good, one that fails, one good
    # This ensures the loop continues after the error
    mock_listing1 = Mock()
    mock_listing1.get_attribute = Mock(return_value="https://facebook.com/marketplace/item/123")
    mock_title1 = Mock()
    mock_title1.text = "Good Product 1"
    mock_listing1.find_element = Mock(return_value=mock_title1)
    
    mock_listing2 = Mock()
    # Make _parse_listing return None for this one
    mock_listing2.get_attribute = Mock(side_effect=Exception("Parse error"))
    
    mock_listing3 = Mock()
    mock_listing3.get_attribute = Mock(return_value="https://facebook.com/marketplace/item/789")
    mock_title3 = Mock()
    mock_title3.text = "Good Product 2"
    mock_listing3.find_element = Mock(return_value=mock_title3)
    
    mock_driver.find_elements = Mock(return_value=[mock_listing1, mock_listing2, mock_listing3])
    
    with patch('app.scrapers.facebook_marketplace.WebDriverWait'):
        with patch.object(scraper, '_scroll_page'):
            with patch.object(scraper, '_random_delay'):
                results = scraper._scrape_search_page("https://test.com", 10)
    
    # Should return two results (the good ones) and skip the bad one
    # This proves the continue statement works (line 214)
    assert len(results) == 2
    assert results[0]['title'] == 'Good Product 1'
    assert results[1]['title'] == 'Good Product 2'
    print("\n✅ Parse error in search handled, loop continues (lines 212-214)")


def test_scrape_product_page_no_title(scraper, mock_driver):
    """Test _scrape_product_page when title element not found."""
    def find_element_side_effect(by, selector):
        raise NoSuchElementException()
    
    mock_driver.find_element = Mock(side_effect=find_element_side_effect)
    
    with patch('app.scrapers.facebook_marketplace.WebDriverWait'):
        details = scraper._scrape_product_page("https://test.com")
    
    assert details['title'] == ""
    print("\n✅ Missing title handled (lines 337-338)")


def test_scrape_product_page_no_price(scraper, mock_driver):
    """Test _scrape_product_page when price element not found."""
    call_count = [0]
    
    def find_element_side_effect(by, selector):
        call_count[0] += 1
        if call_count[0] == 1:  # First call for title
            mock_title = Mock()
            mock_title.text = "Test"
            return mock_title
        # All other calls raise NoSuchElementException
        raise NoSuchElementException()
    
    mock_driver.find_element = Mock(side_effect=find_element_side_effect)
    
    with patch('app.scrapers.facebook_marketplace.WebDriverWait'):
        details = scraper._scrape_product_page("https://test.com")
    
    assert details['price'] is None
    print("\n✅ Missing price handled (lines 345-346)")


def test_scrape_product_page_no_description(scraper, mock_driver):
    """Test _scrape_product_page when description element not found."""
    call_count = [0]
    
    def find_element_side_effect(by, selector):
        call_count[0] += 1
        if call_count[0] <= 2:  # First two calls succeed
            mock_elem = Mock()
            mock_elem.text = "Test"
            return mock_elem
        # Third call (description) raises NoSuchElementException
        raise NoSuchElementException()
    
    mock_driver.find_element = Mock(side_effect=find_element_side_effect)
    
    with patch('app.scrapers.facebook_marketplace.WebDriverWait'):
        details = scraper._scrape_product_page("https://test.com")
    
    assert details['description'] == ""
    print("\n✅ Missing description handled (lines 353-354)")


def test_scrape_product_page_no_location(scraper, mock_driver):
    """Test _scrape_product_page when location element not found."""
    call_count = [0]
    
    def find_element_side_effect(by, selector):
        call_count[0] += 1
        if call_count[0] <= 3:  # First three calls succeed
            mock_elem = Mock()
            mock_elem.text = "Test"
            return mock_elem
        # Fourth call (location) raises NoSuchElementException
        raise NoSuchElementException()
    
    mock_driver.find_element = Mock(side_effect=find_element_side_effect)
    
    with patch('app.scrapers.facebook_marketplace.WebDriverWait'):
        details = scraper._scrape_product_page("https://test.com")
    
    assert details['location'] == ""
    print("\n✅ Missing location handled (lines 361-362)")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])

# Made with Bob