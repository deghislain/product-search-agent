import asyncio
import pytest
import sys
from pathlib import Path
import logging

# Configure logging to show output
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simple format for test output
)
logger = logging.getLogger(__name__)


sys.path.insert(0, str(Path(__file__).parent.parent.parent))


from app.scrapers.craigslist import CraigslistScraper

@pytest.mark.asyncio
async def test_full_workflow():
    """Test complete workflow from search to details."""
    logger.info("="*60)
    logger.info("Craigslist Scraper Integration Test")
    logger.info("="*60)
    
    async with CraigslistScraper() as scraper:
        # Step 1: Search
        logger.info("\n1. Searching for 'iPhone'...")
        results = await scraper.search("iPhone", "sfbay", max_results=5)
        logger.debug(f"   ✓ Found {len(results)} results")
        
        if not results:
            logger.info("   ✗ No results found, test cannot continue")
            return
        
        # Step 2: Display results
        logger.info("\n2. Search Results:")
        for i, product in enumerate(results, 1):
            logger.debug(f"   {i}. {product['title']}")
            logger.debug(f"      Price: ${product['price']}")
            logger.debug(f"      Location: {product['location']}")
            logger.debug(f"      URL: {product['url'][:50]}...")
        
        # Step 3: Get details for first result
        logger.info("\n3. Getting details for first result...")
        details = await scraper.get_product_details(results[0]['url'])
        logger.debug(f"   ✓ Title: {details['title']}")
        logger.debug(f"   ✓ Price: ${details['price']}")
        logger.debug(f"   ✓ Description: {details['description'][:100]}...")
        logger.debug(f"   ✓ Images: {len(details['images'])}")
        logger.debug(f"   ✓ Attributes: {len(details['attributes'])}")
        
        # Step 4: Check availability
        logger.info("\n4. Checking availability...")
        available = await scraper.is_available(results[0]['url'])
        logger.debug(f"   ✓ Listing is {'available' if available else 'not available'}")
        
        # Step 5: Test rate limiting
        logger.info("\n5. Testing rate limiting (making 5 quick requests)...")
        import time
        start = time.time()
        for i in range(5):
            await scraper.search("test", "sfbay", max_results=1)
        elapsed = time.time() - start
        logger.debug(f"   ✓ 5 requests took {elapsed:.2f} seconds")
        logger.debug(f"   ✓ Rate limiting {'working' if elapsed > 1 else 'may not be working'}")
    
    logger.debug("\n" + "="*60)
    logger.info("✅ Integration test complete!")
    logger.info("="*60)


if __name__ == "__main__":
    asyncio.run(test_full_workflow())