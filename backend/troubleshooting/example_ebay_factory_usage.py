"""
eBay Scraper Factory - Usage Examples

This file demonstrates how to use the factory pattern to work with eBay scrapers.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.scrapers.ebay_factory import (
    get_ebay_scraper,
    EbayScraperType,
    search_ebay_with_fallback,
    get_available_scrapers,
    print_scraper_info
)


async def example_1_auto_mode():
    """
    Example 1: AUTO mode (Recommended)
    
    Automatically chooses the best available scraper.
    Uses Selenium if available, falls back to HTTP.
    """
    print("\n" + "=" * 60)
    print("Example 1: AUTO Mode (Recommended)")
    print("=" * 60)
    
    # Create scraper in AUTO mode (default)
    async with get_ebay_scraper() as scraper:
        # Search for products
        results = await scraper.search("iPhone 13", max_results=5)
        
        print(f"\nFound {len(results)} products:")
        for i, product in enumerate(results[:3], 1):
            print(f"{i}. {product['title']}")
            print(f"   Price: ${product['price']}")
            print(f"   URL: {product['url'][:60]}...")


async def example_2_explicit_selenium():
    """
    Example 2: Explicitly use Selenium scraper
    
    Use when you need reliable results and have Selenium installed.
    """
    print("\n" + "=" * 60)
    print("Example 2: Explicit Selenium Mode")
    print("=" * 60)
    
    try:
        async with get_ebay_scraper(scraper_type=EbayScraperType.SELENIUM) as scraper:
            results = await scraper.search("laptop", min_price=500, max_price=1000, max_results=5)
            
            print(f"\nFound {len(results)} laptops in price range:")
            for product in results[:3]:
                print(f"- {product['title']}: ${product['price']}")
    
    except ImportError as e:
        print(f"\n⚠️  Selenium not available: {e}")
        print("Install with: pip install undetected-chromedriver selenium")


async def example_3_http_scraper():
    """
    Example 3: Use HTTP scraper
    
    Faster but may be blocked by eBay. Good for testing.
    """
    print("\n" + "=" * 60)
    print("Example 3: HTTP Mode (Fast but may be blocked)")
    print("=" * 60)
    
    async with get_ebay_scraper(scraper_type=EbayScraperType.HTTP) as scraper:
        results = await scraper.search("test", max_results=3)
        
        if results:
            print(f"\n✅ HTTP scraper worked! Found {len(results)} results")
        else:
            print("\n⚠️  HTTP scraper returned no results (likely blocked by eBay)")


async def example_4_with_fallback():
    """
    Example 4: Use fallback function
    
    Automatically tries Selenium first, falls back to HTTP if needed.
    """
    print("\n" + "=" * 60)
    print("Example 4: Automatic Fallback")
    print("=" * 60)
    
    # This function handles fallback automatically
    results = await search_ebay_with_fallback(
        "iPhone 13",
        max_results=5,
        condition="new"
    )
    
    print(f"\nFallback search found {len(results)} results")
    if results:
        print(f"First result: {results[0]['title']}")


async def example_5_get_product_details():
    """
    Example 5: Get detailed product information
    
    Shows how to get full details for a specific product.
    """
    print("\n" + "=" * 60)
    print("Example 5: Get Product Details")
    print("=" * 60)
    
    async with get_ebay_scraper() as scraper:
        # First, search for a product
        results = await scraper.search("iPhone", max_results=1)
        
        if results:
            # Get detailed information
            url = results[0]['url']
            details = await scraper.get_product_details(url)
            
            print(f"\nProduct Details:")
            print(f"Title: {details['title']}")
            print(f"Price: ${details['price']}")
            print(f"Condition: {details['condition']}")
            print(f"Seller: {details.get('seller_name', 'Unknown')}")
            print(f"Images: {len(details.get('images', []))}")
        else:
            print("\n⚠️  No products found to get details for")


async def example_6_check_availability():
    """
    Example 6: Check if a product is still available
    
    Useful for monitoring listings.
    """
    print("\n" + "=" * 60)
    print("Example 6: Check Product Availability")
    print("=" * 60)
    
    async with get_ebay_scraper() as scraper:
        # Search for a product
        results = await scraper.search("iPhone", max_results=1)
        
        if results:
            url = results[0]['url']
            is_available = await scraper.is_available(url)
            
            if is_available:
                print(f"\n✅ Product is still available!")
                print(f"   {results[0]['title']}")
            else:
                print(f"\n❌ Product is no longer available")
        else:
            print("\n⚠️  No products found to check")


async def example_7_custom_rate_limiter():
    """
    Example 7: Use custom rate limiter
    
    Control how fast requests are made.
    """
    print("\n" + "=" * 60)
    print("Example 7: Custom Rate Limiter")
    print("=" * 60)
    
    from app.utils.rate_limiter import RateLimiter
    
    # Create a slower rate limiter (more polite)
    slow_limiter = RateLimiter(max_requests=5, time_window=60)
    
    async with get_ebay_scraper(rate_limiter=slow_limiter) as scraper:
        print("\nUsing slow rate limiter (5 requests per 60 seconds)")
        results = await scraper.search("test", max_results=2)
        print(f"Found {len(results)} results with rate limiting")


def example_8_check_available_scrapers():
    """
    Example 8: Check which scrapers are available
    
    Useful for debugging and configuration.
    """
    print("\n" + "=" * 60)
    print("Example 8: Check Available Scrapers")
    print("=" * 60)
    
    # Print detailed info
    print_scraper_info()
    
    # Get list of available scrapers
    available = get_available_scrapers()
    print(f"\nAvailable scraper types: {', '.join(available)}")


async def example_9_compare_scrapers():
    """
    Example 9: Compare HTTP vs Selenium performance
    
    Shows the speed difference between scrapers.
    """
    print("\n" + "=" * 60)
    print("Example 9: Compare Scraper Performance")
    print("=" * 60)
    
    import time
    
    # Test HTTP scraper
    print("\nTesting HTTP scraper...")
    start = time.time()
    async with get_ebay_scraper(scraper_type=EbayScraperType.HTTP) as scraper:
        results_http = await scraper.search("test", max_results=1)
    http_time = time.time() - start
    
    print(f"HTTP scraper: {http_time:.2f}s, {len(results_http)} results")
    
    # Test Selenium scraper (if available)
    try:
        print("\nTesting Selenium scraper...")
        start = time.time()
        async with get_ebay_scraper(scraper_type=EbayScraperType.SELENIUM) as scraper:
            results_selenium = await scraper.search("test", max_results=1)
        selenium_time = time.time() - start
        
        print(f"Selenium scraper: {selenium_time:.2f}s, {len(results_selenium)} results")
        print(f"\nSelenium is {selenium_time/http_time:.1f}x slower but more reliable")
    
    except ImportError:
        print("\nSelenium scraper not available for comparison")


async def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("eBay Scraper Factory - Usage Examples")
    print("=" * 60)
    
    # Run examples
    example_8_check_available_scrapers()
    
    await example_1_auto_mode()
    await example_2_explicit_selenium()
    await example_3_http_scraper()
    await example_4_with_fallback()
    await example_5_get_product_details()
    await example_6_check_availability()
    await example_7_custom_rate_limiter()
    await example_9_compare_scrapers()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)
    print("\nRecommendation: Use AUTO mode or fallback function for best results")


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
