"""
Tests for eBay Selenium Scraper

These tests use mocking to test the scraper without requiring actual Selenium/Chrome.
"""
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup

# Create comprehensive mocks for selenium and undetected_chromedriver
mock_uc = MagicMock()
mock_uc.Chrome = MagicMock
mock_uc.ChromeOptions = MagicMock

mock_selenium = MagicMock()
mock_by = MagicMock()
mock_by.CLASS_NAME = "class name"
mock_wait = MagicMock()
mock_ec = MagicMock()
mock_exceptions = MagicMock()

# Create TimeoutException class
class TimeoutException(Exception):
    pass

class NoSuchElementException(Exception):
    pass

mock_exceptions.TimeoutException = TimeoutException
mock_exceptions.NoSuchElementException = NoSuchElementException

# Set up the mock modules
sys.modules['undetected_chromedriver'] = mock_uc
sys.modules['selenium.webdriver.common.by'] = mock_by
sys.modules['selenium.webdriver.support.ui'] = mock_wait
sys.modules['selenium.webdriver.support'] = MagicMock()
sys.modules['selenium.webdriver.support'].expected_conditions = mock_ec
sys.modules['selenium.common.exceptions'] = mock_exceptions

# Now import the module
from app.utils.rate_limiter import RateLimiter

# Import with mocked selenium
import app.scrapers.ebay_selenium as selenium_module
selenium_module.SELENIUM_AVAILABLE = True
selenium_module.uc = mock_uc
selenium_module.TimeoutException = TimeoutException
selenium_module.NoSuchElementException = NoSuchElementException

from app.scrapers.ebay_selenium import EbaySeleniumScraper


@pytest.fixture
def mock_driver():
    """Create a mock Chrome driver."""
    driver = Mock()
    driver.get = Mock()
    driver.page_source = "<html></html>"
    driver.quit = Mock()
    return driver


@pytest.fixture
def scraper(mock_driver, monkeypatch):
    """Create Selenium scraper instance with mocked driver."""
    # Mock the Chrome driver initialization
    with patch('app.scrapers.ebay_selenium.uc.Chrome', return_value=mock_driver):
        with patch('app.scrapers.ebay_selenium.uc.ChromeOptions'):
            scraper = EbaySeleniumScraper(headless=True)
            return scraper


def test_scraper_initialization(scraper, mock_driver):
    """Test that Selenium scraper initializes correctly."""
    assert scraper is not None
    assert scraper.base_url == "https://www.ebay.com"
    assert scraper.driver is not None
    assert scraper.headless is True
    print("\n✅ Scraper initialized correctly")


def test_scraper_initialization_not_headless(mock_driver):
    """Test scraper initialization with headless=False."""
    with patch('app.scrapers.ebay_selenium.uc.Chrome', return_value=mock_driver):
        with patch('app.scrapers.ebay_selenium.uc.ChromeOptions'):
            scraper = EbaySeleniumScraper(headless=False)
            assert scraper.headless is False
            print("\n✅ Non-headless scraper initialized")


def test_scraper_initialization_without_selenium(monkeypatch):
    """Test that ImportError is raised when Selenium not available."""
    monkeypatch.setattr(selenium_module, 'SELENIUM_AVAILABLE', False)
    
    with pytest.raises(ImportError) as exc_info:
        EbaySeleniumScraper()
    
    assert "undetected-chromedriver" in str(exc_info.value)
    print("\n✅ ImportError raised correctly when Selenium unavailable")
    
    # Restore for other tests
    monkeypatch.setattr(selenium_module, 'SELENIUM_AVAILABLE', True)


def test_init_driver_failure(mock_driver, monkeypatch):
    """Test driver initialization failure."""
    def raise_error(*args, **kwargs):
        raise Exception("Driver init failed")
    
    with patch('app.scrapers.ebay_selenium.uc.Chrome', side_effect=raise_error):
        with patch('app.scrapers.ebay_selenium.uc.ChromeOptions'):
            with pytest.raises(Exception) as exc_info:
                EbaySeleniumScraper()
            assert "Driver init failed" in str(exc_info.value)
    
    print("\n✅ Driver initialization failure handled")


@pytest.mark.asyncio
async def test_search_basic(scraper, mock_driver):
    """Test basic search functionality with mocked Selenium."""
    # Mock HTML response
    mock_html = """
    <html>
        <li class="s-item">
            <a class="s-item__link" href="https://www.ebay.com/itm/123456789">
                <div class="s-item__title">iPhone 13 Pro 256GB</div>
            </a>
            <span class="s-item__price">$899.99</span>
            <span class="s-item__location">United States</span>
            <span class="s-item__shipping">Free shipping</span>
            <span class="SECONDARY_INFO">Brand New</span>
            <img class="s-item__image-img" src="https://example.com/image.jpg">
        </li>
        <li class="s-item">
            <a class="s-item__link" href="https://www.ebay.com/itm/987654321">
                <div class="s-item__title">iPhone 13 128GB</div>
            </a>
            <span class="s-item__price">$699.99</span>
        </li>
    </html>
    """
    
    mock_driver.page_source = mock_html
    
    # Mock WebDriverWait
    with patch('app.scrapers.ebay_selenium.WebDriverWait'):
        with patch('app.scrapers.ebay_selenium.time.sleep'):
            results = await scraper.search("iPhone 13", max_results=5)
    
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]['title'] == 'iPhone 13 Pro 256GB'
    assert results[0]['price'] == 899.99
    assert results[0]['platform'] == 'ebay'
    
    print(f"\n✅ Found {len(results)} products")


@pytest.mark.asyncio
async def test_search_with_price_filter(scraper, mock_driver):
    """Test search with price filters."""
    mock_html = """
    <html>
        <li class="s-item">
            <a class="s-item__link" href="https://www.ebay.com/itm/111">
                <div class="s-item__title">Laptop 1</div>
            </a>
            <span class="s-item__price">$750.00</span>
        </li>
    </html>
    """
    mock_driver.page_source = mock_html
    
    with patch('app.scrapers.ebay_selenium.WebDriverWait'):
        with patch('app.scrapers.ebay_selenium.time.sleep'):
            results = await scraper.search("laptop", min_price=500, max_price=1000, max_results=10)
    
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]['price'] == 750.0
    print(f"\n✅ Price filter test passed")


@pytest.mark.asyncio
async def test_search_timeout(scraper, mock_driver):
    """Test search with timeout."""
    with patch('app.scrapers.ebay_selenium.WebDriverWait', side_effect=TimeoutException):
        with patch('app.scrapers.ebay_selenium.time.sleep'):
            results = await scraper.search("test")
    
    assert results == []
    print("\n✅ Timeout handled correctly")


@pytest.mark.asyncio
async def test_search_exception(scraper, mock_driver):
    """Test search with exception."""
    mock_driver.get.side_effect = Exception("Network error")
    
    results = await scraper.search("test")
    
    assert results == []
    print("\n✅ Exception handled correctly")


@pytest.mark.asyncio
async def test_get_product_details(scraper, mock_driver):
    """Test getting product details."""
    mock_html = """
    <html>
        <h1 class="x-item-title__mainTitle">Test Product</h1>
        <div class="x-price-primary">
            <span class="ux-textspans">$500.00</span>
        </div>
        <div class="x-item-condition">
            <span class="ux-textspans">New</span>
        </div>
        <div class="x-item-description">Great product</div>
        <div class="ux-image-carousel">
            <img src="https://example.com/img1.jpg">
            <img src="https://example.com/img2.jpg">
        </div>
        <div class="x-sellercard-atf">
            <span class="ux-textspans">TestSeller</span>
        </div>
        <div class="ux-layout-section--itemDetails">
            <div class="ux-labels-values">
                <span class="ux-textspans--BOLD">Brand</span>
                <span class="ux-textspans--SECONDARY">Apple</span>
            </div>
        </div>
    </html>
    """
    mock_driver.page_source = mock_html
    
    with patch('app.scrapers.ebay_selenium.WebDriverWait'):
        with patch('app.scrapers.ebay_selenium.time.sleep'):
            details = await scraper.get_product_details("https://www.ebay.com/itm/123")
    
    assert details['title'] == 'Test Product'
    assert details['price'] == 500.0
    assert details['condition'] == 'New'
    assert details['description'] == 'Great product'
    assert len(details['images']) == 2
    assert details['seller_name'] == 'TestSeller'
    assert 'Brand' in details['item_specifics']
    print("\n✅ Product details extracted correctly")


@pytest.mark.asyncio
async def test_get_product_details_timeout(scraper, mock_driver):
    """Test product details with timeout."""
    with patch('app.scrapers.ebay_selenium.WebDriverWait', side_effect=TimeoutException):
        details = await scraper.get_product_details("https://www.ebay.com/itm/123")
    
    assert 'error' in details
    assert details['error'] == 'Timeout'
    print("\n✅ Product details timeout handled")


@pytest.mark.asyncio
async def test_get_product_details_exception(scraper, mock_driver):
    """Test product details with exception."""
    mock_driver.get.side_effect = Exception("Page load error")
    
    details = await scraper.get_product_details("https://www.ebay.com/itm/123")
    
    assert 'error' in details
    print("\n✅ Product details exception handled")


@pytest.mark.asyncio
async def test_is_available_true(scraper, mock_driver):
    """Test availability check for available listing."""
    mock_html = """
    <html>
        <h1 class="x-item-title__mainTitle">Available Product</h1>
    </html>
    """
    mock_driver.page_source = mock_html
    
    with patch('app.scrapers.ebay_selenium.time.sleep'):
        available = await scraper.is_available("https://www.ebay.com/itm/123")
    
    assert available is True
    print("\n✅ Available listing detected")


@pytest.mark.asyncio
async def test_is_available_ended(scraper, mock_driver):
    """Test availability check for ended listing."""
    mock_html = """
    <html>
        <div class="vi-content-wrapper">This listing has ended</div>
    </html>
    """
    mock_driver.page_source = mock_html
    
    with patch('app.scrapers.ebay_selenium.time.sleep'):
        available = await scraper.is_available("https://www.ebay.com/itm/123")
    
    assert available is False
    print("\n✅ Ended listing detected")


@pytest.mark.asyncio
async def test_is_available_error_page(scraper, mock_driver):
    """Test availability check for error page."""
    mock_html = """
    <html>
        <div id="error-page">Page not found</div>
    </html>
    """
    mock_driver.page_source = mock_html
    
    with patch('app.scrapers.ebay_selenium.time.sleep'):
        available = await scraper.is_available("https://www.ebay.com/itm/123")
    
    assert available is False
    print("\n✅ Error page detected")


@pytest.mark.asyncio
async def test_is_available_exception(scraper, mock_driver):
    """Test availability check with exception."""
    mock_driver.get.side_effect = Exception("Network error")
    
    available = await scraper.is_available("https://www.ebay.com/itm/123")
    
    assert available is False
    print("\n✅ Availability exception handled")


@pytest.mark.asyncio
async def test_is_available_no_indicators(scraper, mock_driver):
    """Test availability check when no clear indicators exist."""
    # HTML with no title, no error page, no ended message
    mock_html = """
    <html>
        <body>
            <div>Some random content</div>
        </body>
    </html>
    """
    mock_driver.page_source = mock_html
    
    with patch('app.scrapers.ebay_selenium.time.sleep'):
        available = await scraper.is_available("https://www.ebay.com/itm/123")
    
    assert available is False
    print("\n✅ No indicators case handled (line 399)")


@pytest.mark.asyncio
async def test_close(scraper, mock_driver):
    """Test closing the scraper."""
    await scraper.close()
    
    mock_driver.quit.assert_called_once()
    print("\n✅ Scraper closed correctly")


@pytest.mark.asyncio
async def test_close_with_exception(scraper, mock_driver):
    """Test closing with exception."""
    mock_driver.quit.side_effect = Exception("Close error")
    
    # Should not raise exception
    await scraper.close()
    print("\n✅ Close exception handled")


@pytest.mark.asyncio
async def test_context_manager(mock_driver):
    """Test async context manager."""
    with patch('app.scrapers.ebay_selenium.uc.Chrome', return_value=mock_driver):
        with patch('app.scrapers.ebay_selenium.uc.ChromeOptions'):
            async with EbaySeleniumScraper(headless=True) as scraper:
                assert scraper is not None
    
    mock_driver.quit.assert_called()
    print("\n✅ Context manager works correctly")


def test_build_search_url(scraper):
    """Test URL building."""
    url = scraper._build_search_url(
        "iPhone 13",
        min_price=500,
        max_price=1000,
        condition="new",
        buy_it_now_only=True
    )
    
    assert "ebay.com" in url
    assert "iPhone" in url or "iPhone+13" in url
    assert "_udlo=500" in url
    assert "_udhi=1000" in url
    assert "LH_BIN=1" in url
    assert "LH_ItemCondition=1000" in url
    print(f"\n✅ URL built correctly")


def test_build_search_url_used_condition(scraper):
    """Test URL building with used condition."""
    url = scraper._build_search_url("laptop", condition="used")
    
    assert "LH_ItemCondition=3000" in url
    print("\n✅ Used condition URL built correctly")


def test_build_search_url_no_buy_it_now(scraper):
    """Test URL building without buy it now."""
    url = scraper._build_search_url("test", buy_it_now_only=False)
    
    assert "LH_BIN" not in url
    print("\n✅ URL without buy-it-now built correctly")


def test_parse_search_result_with_mock_data(scraper):
    """Test parsing with mock eBay HTML structure."""
    mock_html = """
    <li class="s-item">
        <a class="s-item__link" href="https://www.ebay.com/itm/123456789">
            <div class="s-item__title">iPhone 13 Pro 256GB - Unlocked</div>
        </a>
        <span class="s-item__price">$899.99</span>
        <span class="s-item__location">From United States</span>
        <span class="s-item__shipping">Free shipping</span>
        <span class="SECONDARY_INFO">Brand New</span>
        <img class="s-item__image-img" src="https://example.com/image.jpg">
    </li>
    """
    
    soup = BeautifulSoup(mock_html, 'html.parser')
    item = soup.find('li', class_='s-item')
    result = scraper._parse_search_result(item)
    
    assert result is not None
    assert result['title'] == 'iPhone 13 Pro 256GB - Unlocked'
    assert result['price'] == 899.99
    assert result['url'] == 'https://www.ebay.com/itm/123456789'
    assert result['location'] == 'From United States'
    assert result['shipping_cost'] == 0.0
    assert result['condition'] == 'Brand New'
    assert result['item_id'] == '123456789'
    assert result['platform'] == 'ebay'
    print("\n✅ Mock data parsed correctly")


def test_parse_search_result_sponsored(scraper):
    """Test that sponsored items are skipped."""
    mock_html = """
    <li class="s-item">
        <div>SPONSORED</div>
        <a class="s-item__link" href="https://www.ebay.com/itm/123">
            <div class="s-item__title">Sponsored Product</div>
        </a>
    </li>
    """
    
    soup = BeautifulSoup(mock_html, 'html.parser')
    item = soup.find('li', class_='s-item')
    result = scraper._parse_search_result(item)
    
    assert result is None
    print("\n✅ Sponsored items skipped")


def test_parse_search_result_no_title(scraper):
    """Test parsing with missing title."""
    mock_html = """
    <li class="s-item">
        <a class="s-item__link" href="https://www.ebay.com/itm/123"></a>
    </li>
    """
    
    soup = BeautifulSoup(mock_html, 'html.parser')
    item = soup.find('li', class_='s-item')
    result = scraper._parse_search_result(item)
    
    assert result is None
    print("\n✅ Missing title handled")


def test_parse_search_result_no_href(scraper):
    """Test parsing when link element has no href attribute."""
    mock_html = """
    <li class="s-item">
        <div class="s-item__title">Test Product</div>
        <a class="s-item__link">No href here</a>
    </li>
    """
    
    soup = BeautifulSoup(mock_html, 'html.parser')
    item = soup.find('li', class_='s-item')
    result = scraper._parse_search_result(item)
    
    assert result is None
    print("\n✅ Missing href handled (line 227)")


def test_parse_search_result_header_item(scraper):
    """Test that header items are skipped."""
    mock_html = """
    <li class="s-item">
        <div class="s-item__title">Shop on eBay</div>
    </li>
    """
    
    soup = BeautifulSoup(mock_html, 'html.parser')
    item = soup.find('li', class_='s-item')
    result = scraper._parse_search_result(item)
    
    assert result is None
    print("\n✅ Header items skipped")


def test_parse_search_result_with_paid_shipping(scraper):
    """Test parsing with paid shipping."""
    mock_html = """
    <li class="s-item">
        <a class="s-item__link" href="https://www.ebay.com/itm/123">
            <div class="s-item__title">Test Product</div>
        </a>
        <span class="s-item__price">$100.00</span>
        <span class="s-item__shipping">+$15.50 shipping</span>
    </li>
    """
    
    soup = BeautifulSoup(mock_html, 'html.parser')
    item = soup.find('li', class_='s-item')
    result = scraper._parse_search_result(item)
    
    assert result is not None
    assert result['shipping_cost'] == 15.50
    print("\n✅ Paid shipping parsed correctly")


def test_parse_search_result_exception(scraper):
    """Test parsing with exception."""
    # Create malformed HTML that will cause an exception
    mock_html = "<li class='s-item'></li>"
    
    soup = BeautifulSoup(mock_html, 'html.parser')
    item = soup.find('li', class_='s-item')
    
    # Mock to raise exception
    with patch.object(item, 'find', side_effect=Exception("Parse error")):
        result = scraper._parse_search_result(item)
    
    assert result is None
    print("\n✅ Parse exception handled")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])

# Made with Bob
