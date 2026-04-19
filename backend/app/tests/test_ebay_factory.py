"""
Tests for eBay Scraper Factory

Tests the factory pattern implementation for eBay scrapers.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from app.scrapers.ebay_factory import (
    get_ebay_scraper,
    EbayScraperType,
    get_available_scrapers,
    search_ebay_with_fallback,
    SELENIUM_AVAILABLE
)
from app.scrapers.ebay import EbayScraper

# Try to import Selenium scraper
try:
    from app.scrapers.ebay_selenium import EbaySeleniumScraper
except ImportError:
    EbaySeleniumScraper = None


def test_get_available_scrapers():
    """Test getting list of available scrapers."""
    available = get_available_scrapers()
    
    assert isinstance(available, list)
    assert EbayScraperType.HTTP in available
    
    if SELENIUM_AVAILABLE:
        assert EbayScraperType.SELENIUM in available
    
    print(f"\n✅ Available scrapers: {', '.join(available)}")


def test_factory_http_mode():
    """Test factory in HTTP mode."""
    scraper = get_ebay_scraper(scraper_type=EbayScraperType.HTTP)
    
    assert scraper is not None
    assert isinstance(scraper, EbayScraper)
    assert scraper.base_url == "https://www.ebay.com"
    
    print("\n✅ HTTP scraper created successfully")


@pytest.mark.skipif(not SELENIUM_AVAILABLE, reason="Selenium not installed")
def test_factory_selenium_mode():
    """Test factory in Selenium mode."""
    scraper = get_ebay_scraper(scraper_type=EbayScraperType.SELENIUM)
    
    assert scraper is not None
    assert EbaySeleniumScraper is not None
    assert isinstance(scraper, EbaySeleniumScraper)
    assert scraper.base_url == "https://www.ebay.com"
    assert scraper.driver is not None
    
    # Cleanup
    scraper.driver.quit()
    
    print("\n✅ Selenium scraper created successfully")


def test_factory_auto_mode():
    """Test factory in AUTO mode."""
    scraper = get_ebay_scraper(scraper_type=EbayScraperType.AUTO)
    
    assert scraper is not None
    assert scraper.base_url == "https://www.ebay.com"
    
    # Should be Selenium if available, otherwise HTTP
    if SELENIUM_AVAILABLE:
        assert EbaySeleniumScraper is not None
        assert isinstance(scraper, EbaySeleniumScraper)
        scraper.driver.quit()
        print("\n✅ AUTO mode chose Selenium scraper")
    else:
        assert isinstance(scraper, EbayScraper)
        print("\n✅ AUTO mode chose HTTP scraper (Selenium not available)")


def test_factory_default_is_auto():
    """Test that default mode is AUTO."""
    scraper = get_ebay_scraper()  # No scraper_type specified
    
    assert scraper is not None
    
    if SELENIUM_AVAILABLE and EbaySeleniumScraper:
        assert isinstance(scraper, EbaySeleniumScraper)
        scraper.driver.quit()
    else:
        assert isinstance(scraper, EbayScraper)
    
    print("\n✅ Default mode works correctly")


def test_factory_with_custom_rate_limiter():
    """Test factory with custom rate limiter."""
    from app.utils.rate_limiter import RateLimiter
    
    custom_limiter = RateLimiter(max_requests=5, time_window=30)
    scraper = get_ebay_scraper(
        scraper_type=EbayScraperType.HTTP,
        rate_limiter=custom_limiter
    )
    
    assert scraper is not None
    assert scraper.rate_limiter is custom_limiter
    
    print("\n✅ Custom rate limiter applied successfully")


def test_factory_invalid_type():
    """Test factory with invalid scraper type."""
    with pytest.raises(ValueError) as exc_info:
        get_ebay_scraper(scraper_type="invalid_type")
    
    assert "Invalid scraper_type" in str(exc_info.value)
    print("\n✅ Invalid type raises ValueError correctly")


@pytest.mark.skipif(SELENIUM_AVAILABLE, reason="Test only when Selenium not available")
def test_factory_selenium_fallback():
    """Test fallback to HTTP when Selenium requested but not available."""
    scraper = get_ebay_scraper(
        scraper_type=EbayScraperType.SELENIUM,
        fallback_to_http=True
    )
    
    # Should fallback to HTTP scraper
    assert isinstance(scraper, EbayScraper)
    print("\n✅ Fallback to HTTP works when Selenium unavailable")


@pytest.mark.skipif(SELENIUM_AVAILABLE, reason="Test only when Selenium not available")
def test_factory_selenium_no_fallback():
    """Test error when Selenium requested but not available and no fallback."""
    with pytest.raises(ImportError) as exc_info:
        get_ebay_scraper(
            scraper_type=EbayScraperType.SELENIUM,
            fallback_to_http=False
        )
    
    assert "not available" in str(exc_info.value)
    print("\n✅ ImportError raised correctly when no fallback")


@pytest.mark.asyncio
async def test_search_with_fallback():
    """Test the fallback search function."""
    results = await search_ebay_with_fallback("test", max_results=1)
    
    # Should return a list (may be empty if blocked)
    assert isinstance(results, list)
    print(f"\n✅ Fallback search returned {len(results)} results")


@pytest.mark.asyncio
@pytest.mark.skipif(not SELENIUM_AVAILABLE, reason="Selenium not installed")
@pytest.mark.slow
async def test_factory_selenium_search():
    """Test actual search with Selenium scraper from factory."""
    scraper = get_ebay_scraper(scraper_type=EbayScraperType.SELENIUM, headless=True)
    
    try:
        results = await scraper.search("iPhone", max_results=3)
        
        assert isinstance(results, list)
        # Selenium should return results
        assert len(results) > 0, "Selenium scraper should return results"
        
        print(f"\n✅ Selenium scraper search found {len(results)} results")
        
    finally:
        await scraper.close()


@pytest.mark.asyncio
async def test_factory_http_search():
    """Test search with HTTP scraper from factory."""
    scraper = get_ebay_scraper(scraper_type=EbayScraperType.HTTP)
    
    try:
        results = await scraper.search("test", max_results=1)
        
        # HTTP scraper may return empty results (blocked)
        assert isinstance(results, list)
        print(f"\n✅ HTTP scraper search returned {len(results)} results")
        
    finally:
        await scraper.close()


def test_build_url_consistency():
    """Test that both scrapers build URLs consistently."""
    http_scraper = get_ebay_scraper(scraper_type=EbayScraperType.HTTP)
    
    http_url = http_scraper._build_search_url(
        "iPhone 13",
        min_price=500,
        max_price=1000,
        condition="new"
    )
    
    assert "ebay.com" in http_url
    assert "iPhone" in http_url or "iPhone+13" in http_url
    assert "_udlo=500" in http_url
    assert "_udhi=1000" in http_url
    
    if SELENIUM_AVAILABLE:
        selenium_scraper = get_ebay_scraper(scraper_type=EbayScraperType.SELENIUM)
        
        selenium_url = selenium_scraper._build_search_url(
            "iPhone 13",
            min_price=500,
            max_price=1000,
            condition="new"
        )
        
        # URLs should be identical
        assert http_url == selenium_url
        
        selenium_scraper.driver.quit()
        print("\n✅ Both scrapers build identical URLs")
    else:
        print("\n✅ HTTP scraper builds URLs correctly")


def test_print_scraper_info(capsys):
    """Test the print_scraper_info function."""
    from app.scrapers.ebay_factory import print_scraper_info
    
    print_scraper_info()
    
    captured = capsys.readouterr()
    assert "eBay Scraper Factory" in captured.out
    assert "HTTP Scraper" in captured.out
    assert "Available" in captured.out
    
    if SELENIUM_AVAILABLE:
        assert "Selenium Scraper" in captured.out
        assert "✅ Available" in captured.out
    else:
        assert "❌ Not Available" in captured.out
    
    print("\n✅ print_scraper_info works correctly")


@pytest.mark.asyncio
async def test_search_with_fallback_http_only(monkeypatch):
    """Test fallback function when only HTTP is available."""
    # Mock SELENIUM_AVAILABLE to False
    import app.scrapers.ebay_factory as factory_module
    original_selenium = factory_module.SELENIUM_AVAILABLE
    
    try:
        monkeypatch.setattr(factory_module, 'SELENIUM_AVAILABLE', False)
        
        results = await search_ebay_with_fallback("test", max_results=1)
        
        assert isinstance(results, list)
        print("\n✅ Fallback with HTTP only works")
    finally:
        # Restore original value
        monkeypatch.setattr(factory_module, 'SELENIUM_AVAILABLE', original_selenium)


@pytest.mark.asyncio
async def test_search_with_fallback_selenium_fails(monkeypatch):
    """Test fallback when Selenium is available but fails."""
    import app.scrapers.ebay_factory as factory_module
    
    if not SELENIUM_AVAILABLE:
        pytest.skip("Selenium not available")
    
    # Mock EbaySeleniumScraper to raise an exception
    original_selenium_scraper = factory_module.EbaySeleniumScraper
    
    class MockFailingScraper:
        def __init__(self, *args, **kwargs):
            pass
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, *args):
            pass
        
        async def search(self, *args, **kwargs):
            raise Exception("Selenium failed")
    
    try:
        monkeypatch.setattr(factory_module, 'EbaySeleniumScraper', MockFailingScraper)
        
        results = await search_ebay_with_fallback("test", max_results=1)
        
        # Should fallback to HTTP
        assert isinstance(results, list)
        print("\n✅ Fallback from Selenium to HTTP works")
    finally:
        monkeypatch.setattr(factory_module, 'EbaySeleniumScraper', original_selenium_scraper)


@pytest.mark.asyncio
async def test_search_with_fallback_selenium_no_results(monkeypatch):
    """Test fallback when Selenium returns no results."""
    import app.scrapers.ebay_factory as factory_module
    
    if not SELENIUM_AVAILABLE:
        pytest.skip("Selenium not available")
    
    original_selenium_scraper = factory_module.EbaySeleniumScraper
    
    class MockEmptyResultsScraper:
        def __init__(self, *args, **kwargs):
            pass
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, *args):
            pass
        
        async def search(self, *args, **kwargs):
            return []  # No results
    
    try:
        monkeypatch.setattr(factory_module, 'EbaySeleniumScraper', MockEmptyResultsScraper)
        
        results = await search_ebay_with_fallback("test", max_results=1)
        
        # Should fallback to HTTP
        assert isinstance(results, list)
        print("\n✅ Fallback when Selenium returns no results works")
    finally:
        monkeypatch.setattr(factory_module, 'EbaySeleniumScraper', original_selenium_scraper)


@pytest.mark.asyncio
async def test_search_with_fallback_both_fail(monkeypatch):
    """Test fallback when both scrapers fail."""
    import app.scrapers.ebay_factory as factory_module
    
    original_http_scraper = factory_module.EbayScraper
    
    class MockFailingScraper:
        def __init__(self, *args, **kwargs):
            pass
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, *args):
            pass
        
        async def search(self, *args, **kwargs):
            raise Exception("Scraper failed")
    
    try:
        monkeypatch.setattr(factory_module, 'EbayScraper', MockFailingScraper)
        
        results = await search_ebay_with_fallback("test", max_results=1)
        
        # Should return empty list
        assert results == []
        print("\n✅ Returns empty list when both scrapers fail")
    finally:
        monkeypatch.setattr(factory_module, 'EbayScraper', original_http_scraper)


def test_factory_with_selenium_available(monkeypatch):
    """Test factory behavior when Selenium is available."""
    import app.scrapers.ebay_factory as factory_module
    
    if SELENIUM_AVAILABLE:
        # Test that AUTO mode uses Selenium
        scraper = get_ebay_scraper(scraper_type=EbayScraperType.AUTO)
        assert EbaySeleniumScraper is not None
        assert isinstance(scraper, EbaySeleniumScraper)
        scraper.driver.quit()
        
        # Test available scrapers includes Selenium
        available = get_available_scrapers()
        assert EbayScraperType.SELENIUM in available
        
        print("\n✅ Factory works correctly with Selenium available")
    else:
        pytest.skip("Selenium not available")


def test_factory_selenium_mode_with_headless_false():
    """Test Selenium scraper creation with headless=False."""
    if not SELENIUM_AVAILABLE:
        pytest.skip("Selenium not available")
    
    scraper = get_ebay_scraper(
        scraper_type=EbayScraperType.SELENIUM,
        headless=False
    )
    
    assert scraper is not None
    assert isinstance(scraper, EbaySeleniumScraper)
    
    # Cleanup
    scraper.driver.quit()
    
    print("\n✅ Selenium scraper with headless=False works")


def test_factory_auto_mode_with_selenium_mocked(monkeypatch):
    """Test AUTO mode when Selenium is available (mocked)."""
    import app.scrapers.ebay_factory as factory_module
    
    # Create a mock Selenium scraper
    class MockSeleniumScraper:
        base_url = "https://www.ebay.com"
        driver = None
        
        def __init__(self, rate_limiter=None, headless=True):
            self.rate_limiter = rate_limiter
            self.headless = headless
    
    # Mock SELENIUM_AVAILABLE to True
    monkeypatch.setattr(factory_module, 'SELENIUM_AVAILABLE', True)
    monkeypatch.setattr(factory_module, 'EbaySeleniumScraper', MockSeleniumScraper)
    
    # Test AUTO mode
    scraper = get_ebay_scraper(scraper_type=EbayScraperType.AUTO)
    
    assert isinstance(scraper, MockSeleniumScraper)
    print("\n✅ AUTO mode with mocked Selenium works")


def test_factory_selenium_mode_with_selenium_mocked(monkeypatch):
    """Test SELENIUM mode when Selenium is available (mocked)."""
    import app.scrapers.ebay_factory as factory_module
    
    class MockSeleniumScraper:
        base_url = "https://www.ebay.com"
        driver = None
        
        def __init__(self, rate_limiter=None, headless=True):
            self.rate_limiter = rate_limiter
            self.headless = headless
    
    monkeypatch.setattr(factory_module, 'SELENIUM_AVAILABLE', True)
    monkeypatch.setattr(factory_module, 'EbaySeleniumScraper', MockSeleniumScraper)
    
    # Test SELENIUM mode
    scraper = get_ebay_scraper(scraper_type=EbayScraperType.SELENIUM)
    
    assert isinstance(scraper, MockSeleniumScraper)
    print("\n✅ SELENIUM mode with mocked Selenium works")


def test_get_available_scrapers_with_selenium_mocked(monkeypatch):
    """Test get_available_scrapers when Selenium is available (mocked)."""
    import app.scrapers.ebay_factory as factory_module
    
    # Mock SELENIUM_AVAILABLE to True
    monkeypatch.setattr(factory_module, 'SELENIUM_AVAILABLE', True)
    
    available = get_available_scrapers()
    
    assert EbayScraperType.HTTP in available
    assert EbayScraperType.SELENIUM in available
    print("\n✅ get_available_scrapers with mocked Selenium works")


def test_print_scraper_info_with_selenium_mocked(monkeypatch, capsys):
    """Test print_scraper_info when Selenium is available (mocked)."""
    import app.scrapers.ebay_factory as factory_module
    from app.scrapers.ebay_factory import print_scraper_info
    
    # Mock SELENIUM_AVAILABLE to True
    monkeypatch.setattr(factory_module, 'SELENIUM_AVAILABLE', True)
    
    print_scraper_info()
    
    captured = capsys.readouterr()
    assert "Selenium Scraper" in captured.out
    assert "✅ Available" in captured.out
    assert "Bypasses bot detection" in captured.out
    print("\n✅ print_scraper_info with mocked Selenium works")


@pytest.mark.asyncio
async def test_search_with_fallback_selenium_success(monkeypatch):
    """Test fallback function when Selenium succeeds (mocked)."""
    import app.scrapers.ebay_factory as factory_module
    
    class MockSeleniumScraper:
        def __init__(self, *args, **kwargs):
            pass
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, *args):
            pass
        
        async def search(self, *args, **kwargs):
            return [{"title": "Test Product", "price": 100}]
    
    monkeypatch.setattr(factory_module, 'SELENIUM_AVAILABLE', True)
    monkeypatch.setattr(factory_module, 'EbaySeleniumScraper', MockSeleniumScraper)
    
    results = await search_ebay_with_fallback("test", max_results=1)
    
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["title"] == "Test Product"
    print("\n✅ Fallback with successful Selenium works")


@pytest.mark.asyncio
async def test_search_with_fallback_http_success(monkeypatch):
    """Test fallback function when HTTP succeeds."""
    import app.scrapers.ebay_factory as factory_module
    
    class MockHTTPScraper:
        def __init__(self, *args, **kwargs):
            pass
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, *args):
            pass
        
        async def search(self, *args, **kwargs):
            return [{"title": "HTTP Product", "price": 200}]
    
    # Mock SELENIUM_AVAILABLE to False so it goes straight to HTTP
    monkeypatch.setattr(factory_module, 'SELENIUM_AVAILABLE', False)
    monkeypatch.setattr(factory_module, 'EbayScraper', MockHTTPScraper)
    
    results = await search_ebay_with_fallback("test", max_results=1)
    
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["title"] == "HTTP Product"
    print("\n✅ Fallback with successful HTTP works")


def test_import_error_handling(monkeypatch):
    """Test that import error for Selenium is handled correctly."""
    # This tests lines 21-23 by simulating the import error scenario
    # We can't directly test the import block, but we can verify the behavior
    # when SELENIUM_AVAILABLE is False
    
    import app.scrapers.ebay_factory as factory_module
    
    # Ensure SELENIUM_AVAILABLE is False
    monkeypatch.setattr(factory_module, 'SELENIUM_AVAILABLE', False)
    monkeypatch.setattr(factory_module, 'EbaySeleniumScraper', None)
    
    # Verify that get_available_scrapers doesn't include Selenium
    available = get_available_scrapers()
    assert EbayScraperType.SELENIUM not in available
    assert EbayScraperType.HTTP in available
    
    # Verify that AUTO mode falls back to HTTP
    scraper = get_ebay_scraper(scraper_type=EbayScraperType.AUTO)
    assert isinstance(scraper, EbayScraper)
    
    print("\n✅ Import error handling works correctly")


@pytest.mark.asyncio
async def test_search_with_fallback_selenium_empty_then_http(monkeypatch):
    """Test fallback when Selenium returns empty results, then HTTP succeeds."""
    import app.scrapers.ebay_factory as factory_module
    
    class MockSeleniumScraperEmpty:
        def __init__(self, *args, **kwargs):
            pass
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, *args):
            pass
        
        async def search(self, *args, **kwargs):
            return []  # Empty results
    
    class MockHTTPScraperSuccess:
        def __init__(self, *args, **kwargs):
            pass
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, *args):
            pass
        
        async def search(self, *args, **kwargs):
            return [{"title": "HTTP Product", "price": 100}]
    
    monkeypatch.setattr(factory_module, 'SELENIUM_AVAILABLE', True)
    monkeypatch.setattr(factory_module, 'EbaySeleniumScraper', MockSeleniumScraperEmpty)
    monkeypatch.setattr(factory_module, 'EbayScraper', MockHTTPScraperSuccess)
    
    results = await search_ebay_with_fallback("test", max_results=1)
    
    # Should fallback to HTTP and get results
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["title"] == "HTTP Product"
    print("\n✅ Fallback from empty Selenium to successful HTTP works")


@pytest.mark.asyncio
async def test_search_with_fallback_selenium_exception(monkeypatch):
    """Test fallback when Selenium raises an exception."""
    import app.scrapers.ebay_factory as factory_module
    
    class MockSeleniumScraperException:
        def __init__(self, *args, **kwargs):
            pass
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, *args):
            pass
        
        async def search(self, *args, **kwargs):
            raise Exception("Selenium search failed")
    
    class MockHTTPScraperSuccess:
        def __init__(self, *args, **kwargs):
            pass
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, *args):
            pass
        
        async def search(self, *args, **kwargs):
            return [{"title": "HTTP Fallback", "price": 150}]
    
    monkeypatch.setattr(factory_module, 'SELENIUM_AVAILABLE', True)
    monkeypatch.setattr(factory_module, 'EbaySeleniumScraper', MockSeleniumScraperException)
    monkeypatch.setattr(factory_module, 'EbayScraper', MockHTTPScraperSuccess)
    
    results = await search_ebay_with_fallback("test", max_results=1)
    
    # Should catch exception and fallback to HTTP
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["title"] == "HTTP Fallback"
    print("\n✅ Fallback from Selenium exception to HTTP works")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])

# Made with Bob
