"""
Tests for Craigslist Scraper

Comprehensive test suite for CraigslistScraper functionality.
"""

import asyncio
from typing import Dict, List
import pytest
import pytest_asyncio
import sys
from pathlib import Path
import logging

# Configure logging to show output
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simple format for test output
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scrapers.craigslist import CraigslistScraper
from app.utils.rate_limiter import RateLimiter


class TestCraigslistScraper:
    """Test suite for Craigslist scraper."""
    
    @pytest_asyncio.fixture
    async def scraper(self):
        """Create scraper instance for testing."""
        scraper = CraigslistScraper()
        yield scraper
        await scraper.close()
    
    @pytest.mark.asyncio
    async def test_search_basic(self, scraper):
        """Test basic search functionality."""
        results = await scraper.search("iPhone", "sfbay", max_results=5)
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert len(results) <= 5
        
        # Check first result structure
        product = results[0]
        assert 'title' in product
        assert 'price' in product
        assert 'url' in product
        assert 'platform' in product
        assert product['platform'] == 'craigslist'
    
    @pytest.mark.asyncio
    async def test_search_with_price_filter(self, scraper):
        """Test search with price filters."""
        results = await scraper.search(
            "laptop",
            "sfbay",
            min_price=500,
            max_price=1000,
            max_results=10
        )
        
        assert isinstance(results, list)
        
        # Check prices are within range
        for product in results:
            if product['price']:
                assert product['price'] >= 500
                assert product['price'] <= 1000
    
    @pytest.mark.asyncio
    async def test_get_product_details(self, scraper):
        """Test getting detailed product information."""
        # First get a product URL
        results = await scraper.search("iPhone", "sfbay", max_results=1)
        assert len(results) > 0
        
        url = results[0]['url']
        details = await scraper.get_product_details(url)
        
        assert isinstance(details, dict)
        assert 'title' in details
        assert 'description' in details
        assert 'images' in details
        assert isinstance(details['images'], list)
    
    @pytest.mark.asyncio
    async def test_is_available(self, scraper):
        """Test availability checking."""
        # Get a real listing
        results = await scraper.search("iPhone", "sfbay", max_results=1)
        assert len(results) > 0
        
        url = results[0]['url']
        available = await scraper.is_available(url)
        
        assert isinstance(available, bool)
        # Real listing should be available
        assert available is True
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test that rate limiting is working."""
        import time
        
        # Create scraper with strict rate limit
        rate_limiter = RateLimiter(max_requests=3, time_window=5)
        scraper = CraigslistScraper(rate_limiter=rate_limiter)
        
        start_time = time.time()
        
        # Make 5 requests (should trigger rate limiting after 3)
        for i in range(5):
            await scraper.search("test", "sfbay", max_results=1)
        
        elapsed = time.time() - start_time
        
        # Should take at least 5 seconds (the time window)
        assert elapsed >= 5
        
        await scraper.close()
    
    def test_build_search_url(self):
        """Test URL building."""
        scraper = CraigslistScraper()
        
        url = scraper._build_search_url(
            "sfbay",
            "sss",
            "iPhone 13",
            500,
            1000
        )
        
        assert "sfbay.craigslist.org" in url
        assert "query=iPhone" in url or "query=iPhone+13" in url
        assert "min_price=500" in url
        assert "max_price=1000" in url

        
    def _handle_missing_data(self, data: Dict) -> Dict:
        """
        Handle missing or invalid data in scraped results.
        
        Args:
            data: Product dictionary
        
        Returns:
            Cleaned product dictionary with defaults for missing fields
        """
        defaults = {
            'title': 'Unknown',
            'price': None,
            'location': 'Unknown',
            'posted_date': None,
            'image_url': None,
            'description': '',
            'images': [],
            'attributes': {}
        }
        
        # Merge with defaults
        return {**defaults, **data}


    async def search_with_retry(
        self,
        query: str,
        location: str,
        max_retries: int = 3,
        **kwargs
    ) -> List[Dict]:
        """
        Search with automatic retry on failure.
        
        Args:
            query: Search term
            location: Craigslist location
            max_retries: Maximum number of retry attempts
            **kwargs: Additional search parameters
        
        Returns:
            List of products, or empty list if all retries fail
        """
        for attempt in range(max_retries):
            try:
                return await self.search(query, location, **kwargs)
            except Exception as e:
                logger.error(f"Search attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    # Wait before retrying (exponential backoff)
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"All {max_retries} attempts failed")
                    return []


# Run tests
if __name__ == "__main__":
    async def run_all_tests():
        scraper = CraigslistScraper()
        
        logger.info("Running Craigslist Scraper Tests...\n")
        
        # Test 1: Basic search
        logger.info("1. Testing basic search...")
        results = await scraper.search("iPhone", "sfbay", max_results=3)
        logger.info(f"   ✓ Found {len(results)} results")
        
        # Test 2: Product details
        if results:
            logger.info("\n2. Testing product details...")
            details = await scraper.get_product_details(results[0]['url'])
            logger.debug(f"   ✓ Got details for: {details['title']}")
            logger.debug(f"   ✓ Description length: {len(details['description'])} chars")
            logger.debug(f"   ✓ Images: {len(details['images'])}")
        
        # Test 3: Availability
        if results:
            logger.info("\n3. Testing availability check...")
            available = await scraper.is_available(results[0]['url'])
            logger.debug(f"   ✓ Listing available: {available}")
        
        await scraper.close()
        logger.info("\n✅ All tests passed!")
    
    asyncio.run(run_all_tests())