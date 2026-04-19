"""
eBay Scraper Factory

Factory pattern for creating the appropriate eBay scraper based on configuration.
Provides automatic fallback and flexible scraper selection.
"""
import sys
import logging
from pathlib import Path
from typing import Optional

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scrapers.ebay import EbayScraper
from app.utils.rate_limiter import RateLimiter

# Try to import Selenium scraper
try:
    from app.scrapers.ebay_selenium import EbaySeleniumScraper, SELENIUM_AVAILABLE
except ImportError:
    SELENIUM_AVAILABLE = False
    EbaySeleniumScraper = None

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EbayScraperType:
    """Enum for scraper types."""
    HTTP = "http"
    SELENIUM = "selenium"
    AUTO = "auto"  # Automatically choose best available


def get_ebay_scraper(
    scraper_type: str = EbayScraperType.AUTO,
    headless: bool = True,
    rate_limiter: Optional[RateLimiter] = None,
    fallback_to_http: bool = True
):
    """
    Factory function to get the appropriate eBay scraper.
    
    This function implements the Factory Pattern to create the right scraper
    based on configuration and availability.
    
    Args:
        scraper_type: Type of scraper to use:
            - "selenium": Use Selenium scraper (more reliable, slower)
            - "http": Use HTTP scraper (faster, may be blocked)
            - "auto": Automatically choose best available (default)
        headless: Run browser in headless mode (Selenium only)
        rate_limiter: Optional rate limiter instance
        fallback_to_http: If Selenium unavailable, fallback to HTTP
    
    Returns:
        EbayScraper or EbaySeleniumScraper instance
    
    Raises:
        ImportError: If requested scraper type is not available
    
    Examples:
        >>> # Auto mode (recommended) - uses Selenium if available
        >>> scraper = get_ebay_scraper()
        >>> 
        >>> # Explicitly use Selenium
        >>> scraper = get_ebay_scraper(scraper_type="selenium")
        >>> 
        >>> # Use HTTP scraper (faster but may be blocked)
        >>> scraper = get_ebay_scraper(scraper_type="http")
        >>> 
        >>> # With custom rate limiter
        >>> limiter = RateLimiter(max_requests=5, time_window=60)
        >>> scraper = get_ebay_scraper(rate_limiter=limiter)
    """
    
    # AUTO mode: Choose best available
    if scraper_type == EbayScraperType.AUTO:
        if SELENIUM_AVAILABLE:
            logger.info("Auto mode: Using Selenium scraper (more reliable)")
            return EbaySeleniumScraper(
                rate_limiter=rate_limiter,
                headless=headless
            )
        else:
            logger.warning("Auto mode: Selenium not available, using HTTP scraper")
            return EbayScraper(rate_limiter=rate_limiter)
    
    # SELENIUM mode: Use Selenium scraper
    elif scraper_type == EbayScraperType.SELENIUM:
        if not SELENIUM_AVAILABLE:
            error_msg = (
                "Selenium scraper requested but not available. "
                "Install with: pip install undetected-chromedriver selenium"
            )
            if fallback_to_http:
                logger.warning(f"{error_msg}. Falling back to HTTP scraper.")
                return EbayScraper(rate_limiter=rate_limiter)
            else:
                raise ImportError(error_msg)
        
        logger.info("Using Selenium scraper")
        return EbaySeleniumScraper(
            rate_limiter=rate_limiter,
            headless=headless
        )
    
    # HTTP mode: Use HTTP scraper
    elif scraper_type == EbayScraperType.HTTP:
        logger.info("Using HTTP scraper (may be blocked by eBay)")
        return EbayScraper(rate_limiter=rate_limiter)
    
    else:
        raise ValueError(
            f"Invalid scraper_type: {scraper_type}. "
            f"Must be one of: {EbayScraperType.AUTO}, {EbayScraperType.SELENIUM}, {EbayScraperType.HTTP}"
        )


async def search_ebay_with_fallback(query: str, **kwargs):
    """
    Search eBay with automatic fallback mechanism.
    
    Tries Selenium scraper first (more reliable), automatically falls back
    to HTTP scraper if Selenium fails or is unavailable.
    
    Args:
        query: Search term
        **kwargs: Additional search parameters (min_price, max_price, etc.)
    
    Returns:
        List of product dictionaries
    
    Example:
        >>> results = await search_ebay_with_fallback("iPhone 13", max_results=10)
        >>> print(f"Found {len(results)} products")
    """
    # Try Selenium first
    if SELENIUM_AVAILABLE:
        try:
            logger.info("Attempting search with Selenium scraper...")
            async with EbaySeleniumScraper(headless=True) as scraper:
                results = await scraper.search(query, **kwargs)
                if results:
                    logger.info(f"Selenium scraper succeeded: {len(results)} results")
                    return results
                else:
                    logger.warning("Selenium scraper returned no results")
        except Exception as e:
            logger.warning(f"Selenium scraper failed: {e}")
    else:
        logger.info("Selenium not available, skipping to HTTP scraper")
    
    # Fallback to HTTP scraper
    logger.info("Falling back to HTTP scraper...")
    try:
        async with EbayScraper() as scraper:
            results = await scraper.search(query, **kwargs)
            if results:
                logger.info(f"HTTP scraper succeeded: {len(results)} results")
            else:
                logger.warning("HTTP scraper returned no results (likely blocked)")
            return results
    except Exception as e:
        logger.error(f"HTTP scraper also failed: {e}")
        return []


def get_available_scrapers():
    """
    Get list of available scraper types.
    
    Returns:
        List of available scraper type strings
    
    Example:
        >>> available = get_available_scrapers()
        >>> print(f"Available scrapers: {', '.join(available)}")
    """
    available = [EbayScraperType.HTTP]  # HTTP always available
    
    if SELENIUM_AVAILABLE:
        available.append(EbayScraperType.SELENIUM)
    
    return available


def print_scraper_info():
    """Print information about available scrapers."""
    print("=" * 60)
    print("eBay Scraper Factory - Available Scrapers")
    print("=" * 60)
    print()
    
    print("📦 HTTP Scraper:")
    print("   Status: ✅ Available")
    print("   Speed: ⚡ Fast (0.5s)")
    print("   Reliability: ⚠️  May be blocked by eBay")
    print("   Use for: Testing, mock data, fallback")
    print()
    
    if SELENIUM_AVAILABLE:
        print("📦 Selenium Scraper:")
        print("   Status: ✅ Available")
        print("   Speed: 🐢 Slow (3-5s)")
        print("   Reliability: ✅ Bypasses bot detection")
        print("   Use for: Production, reliable results")
    else:
        print("📦 Selenium Scraper:")
        print("   Status: ❌ Not Available")
        print("   Install: pip install undetected-chromedriver selenium")
    
    print()
    print("=" * 60)
    print("Recommendation: Use AUTO mode for best results")
    print("=" * 60)


# Test code
if __name__ == "__main__":
    import asyncio
    
    async def test_factory():
        """Test the factory pattern."""
        print_scraper_info()
        print()
        
        # Test AUTO mode
        print("Testing AUTO mode...")
        scraper = get_ebay_scraper(scraper_type=EbayScraperType.AUTO)
        print(f"✅ Created: {scraper.__class__.__name__}")
        
        # Test search
        print("\nTesting search...")
        results = await scraper.search("iPhone 13", max_results=3)
        print(f"✅ Found {len(results)} results")
        
        if results:
            print(f"\nFirst result:")
            print(f"  Title: {results[0]['title']}")
            print(f"  Price: ${results[0]['price']}")
        
        await scraper.close()
        
        # Test fallback function
        print("\n" + "=" * 60)
        print("Testing fallback function...")
        results = await search_ebay_with_fallback("laptop", max_results=3)
        print(f"✅ Fallback search found {len(results)} results")
        
        print("\n" + "=" * 60)
        print("✅ Factory pattern test complete!")
        print("=" * 60)
    
    asyncio.run(test_factory())

# Made with Bob
