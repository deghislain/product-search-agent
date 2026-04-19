"""
Craigslist Scraper Test Script

Run this to test your Craigslist scraper with proper diagnostics.
"""

import asyncio
import pytest
import sys, logging
from pathlib import Path
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scrapers.craigslist import CraigslistScraper

@pytest.mark.asyncio
async def test_all():
    """Run all tests in sequence."""
    logger.info("="*60)
    logger.info("Craigslist Scraper Test Suite")
    logger.info("="*60)
    
    # Create scraper once
    scraper = CraigslistScraper()
    
    try:
        # Test 1: Search
        logger.info("\n📋 Test 1: Search for products")
        logger.info("-"*60)
        results = await scraper.search("iPhone", "sfbay", max_results=5)
        
        logger.debug(f"Found {len(results)} products")
        
        if len(results) == 0:
            logger.info("\n⚠️  WARNING: No results found!")
            logger.info("This could mean:")
            logger.info("  1. Craigslist HTML structure changed")
            logger.info("  2. Craigslist is blocking automated requests")
            logger.info("  3. No listings match your search")
            logger.info("\nLet's check the raw HTML...")
            
            # Diagnostic: Check what we actually got
            search_url = scraper._build_search_url("sfbay", "sss", "iPhone", None, None)
            logger.debug(f"\nSearch URL: {search_url}")
            
            response = await scraper._make_request(search_url)
            html_snippet = response.text[:500]
            logger.info(f"\nFirst 500 chars of HTML:")
            logger.debug(html_snippet)
            logger.info("\n" + "="*60)
            
        else:
            logger.info("\n✅ Search successful!")
            for i, product in enumerate(results, 1):
                logger.debug(f"\n{i}. {product['title']}")
                logger.debug(f"   Price: ${product['price']}")
                logger.debug(f"   Location: {product['location']}")
                logger.debug(f"   URL: {product['url'][:60]}...")
        
        # Test 2: Product Details (only if we have results)
        if results:
            logger.info("\n\n📄 Test 2: Get product details")
            logger.info("-"*60)
            url = results[0]['url']
            details = await scraper.get_product_details(url)
            
            logger.debug(f"Title: {details['title']}")
            logger.debug(f"Price: ${details['price']}")
            logger.debug(f"Description: {details['description'][:100]}...")
            logger.debug(f"Images: {len(details['images'])}")
            logger.debug(f"Attributes: {details['attributes']}")
            logger.info("✅ Details retrieved successfully!")
        
        # Test 3: Availability Check
        logger.info("\n\n🔍 Test 3: Check availability")
        logger.info("-"*60)
        
        if results:
            # Test with real listing
            url = results[0]['url']
            available = await scraper.is_available(url)
            logger.debug(f"Real listing available: {available}")
            logger.info("✅ Real listing check successful!")
        
        # Test with fake URL (should return False)
        logger.info("\nTesting with fake URL (should return False)...")
        fake_url = "https://sfbay.craigslist.org/sfc/mob/d/fake-listing/1234567890.html"
        available = await scraper.is_available(fake_url)
        logger.debug(f"Fake listing available: {available}")
        
        if not available:
            logger.info("✅ Fake listing correctly identified as unavailable!")
        else:
            logger.info("⚠️  Unexpected: Fake listing returned as available")
        
    finally:
        # Always close the scraper
        await scraper.close()
        logger.info("\n" + "="*60)
        logger.info("Tests complete!")
        logger.info("="*60)


if __name__ == "__main__":
    asyncio.run(test_all())

# Made with Bob
