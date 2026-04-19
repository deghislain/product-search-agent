"""
Facebook Marketplace Scraper Module

Implements scraping functionality for Facebook Marketplace using Selenium.
Facebook requires JavaScript rendering, so we use a real browser.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import List, Dict, Optional
from datetime import datetime
import asyncio
import time, logging
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from app.scrapers.base import BaseScraper
from app.utils.rate_limiter import RateLimiter

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FacebookMarketplaceScraper(BaseScraper):
    """
    Facebook Marketplace Scraper Module

    This module implements web scraping for Facebook Marketplace using Selenium WebDriver.

    Key Features:
    - JavaScript rendering support via Selenium
    - Stealth techniques to avoid detection
    - Rate limiting to prevent blocking
    - Async/await support for integration with FastAPI

    Usage Example:
        >>> scraper = FacebookMarketplaceScraper(headless=True)
        >>> results = await scraper.search("iPhone 13", "newyork")
        >>> print(f"Found {len(results)} products")
        >>> await scraper.close()

    Important Notes:
    - Facebook actively blocks scrapers
    - Selectors may change frequently
    - Consider using Facebook's official API for production
    - This implementation is for educational purposes

    Author: [Your Name]
    Date: 2024-01-15
    """
    
    def __init__(self, rate_limiter: Optional[RateLimiter] = None, headless: bool = True):
        """
        Initialize Facebook Marketplace scraper.
        
        Args:
            rate_limiter: Optional rate limiter for controlling request rate
            headless: If True, run browser without GUI (faster, uses less resources)
        """
        super().__init__(rate_limiter)
        self.base_url = "https://www.facebook.com/marketplace"
        self.headless = headless
        self.driver = None
    
    def _setup_driver(self):
        """
        Setup Chrome WebDriver with advanced stealth options.
        """
        options = Options()
        
        # Basic options
        if self.headless:
            options.add_argument('--headless=new')  # New headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Stealth options
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Realistic user agent
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Create driver using Selenium Manager (automatic driver management)
        self.driver = webdriver.Chrome(options=options)
        
        # Apply selenium-stealth (if available)
        try:
            from selenium_stealth import stealth
            stealth(self.driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True)
        except ImportError:
            # selenium-stealth not installed, skip it
            pass
        
        # Additional stealth JavaScript
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        print("✓ Stealth driver configured")

    async def search(self, query: str, location: str = "newyork", **kwargs) -> List[Dict]:
        """
        Search for products on Facebook Marketplace.
        
        Args:
            query: Search term (e.g., "iPhone 13")
            location: Location slug (e.g., "newyork", "losangeles")
            **kwargs: Additional parameters:
                - min_price: Minimum price filter
                - max_price: Maximum price filter
                - max_results: Maximum number of results to return (default: 20)
        
        Returns:
            List[Dict]: List of product dictionaries with keys:
                - title: Product title
                - price: Product price (float)
                - url: Product URL
                - location: Product location
                - posted_date: When listing was posted
                - image_url: Product image URL (optional)
        """
        logger.info("************************Searching Facebook for query: %s", query)
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        # Setup driver if not already done
        if not self.driver:
            self._setup_driver()
        
        # Build search URL
        search_url = f"{self.base_url}/{location}/search"
        params = {"query": query}
        
        # Add price filters if provided
        if "min_price" in kwargs:
            params["minPrice"] = kwargs["min_price"]
        if "max_price" in kwargs:
            params["maxPrice"] = kwargs["max_price"]
        
        # Build full URL with parameters
        full_url = search_url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        logger.info(f"Searching Facebook Marketplace: {full_url}")
        
        # Run browser automation in thread pool (Selenium is blocking)
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, self._scrape_search_page, full_url, kwargs.get("max_results", 20))
        
        return results

    def _random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """
        Add random delay to mimic human behavior.
        
        Args:
            min_seconds: Minimum delay in seconds
            max_seconds: Maximum delay in seconds
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def _scrape_search_page(self, url: str, max_results: int) -> List[Dict]:
        """
        Scrape search results page (blocking method run in thread pool).
        
        Args:
            url: Search URL
            max_results: Maximum number of results to return
        
        Returns:
            List[Dict]: List of products
        """
        try:
            # Navigate to search page
            self.driver.get(url)
            self._random_delay(2, 4)  # Wait like a human would
            
            # Wait for listings to load (Facebook uses dynamic loading)
            # Wait up to 10 seconds for at least one listing to appear
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='x9f619']")))
            
            # Scroll to load more results
            self._scroll_page(times=3)
            
            # Find all product listings
            # Note: Facebook's HTML structure changes frequently
            # These selectors may need updating
            listings = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='x9f619'] a[href*='/marketplace/item/']")
            
            products = []
            for listing in listings[:max_results]:
                try:
                    product = self._parse_listing(listing)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.error(f"Error parsing listing: {e}")
                    continue
            
            logger.debug(f"✓ Found {len(products)} products")
            return products
            
        except TimeoutException:
            logger.error("⚠ Timeout waiting for listings to load")
            return []
        except Exception as e:
            logger.error(f"✗ Error scraping search page: {e}")
            return []
    def _scroll_page(self, times: int = 3):
        """
        Scroll page to trigger lazy loading of more results.
        
        Args:
            times: Number of times to scroll
        """
        for i in range(times):
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait for content to load (blocking sleep since this is a blocking method)
            time.sleep(1)

    def _parse_listing(self, listing_element) -> Optional[Dict]:
        """
        Parse a single listing element into a product dictionary.
        
        Args:
            listing_element: Selenium WebElement for the listing
        
        Returns:
            Optional[Dict]: Product dictionary or None if parsing fails
        """
        try:
            # Extract URL
            url = listing_element.get_attribute('href')
            
            # Extract title (usually in a span or div inside the link)
            title_element = listing_element.find_element(By.CSS_SELECTOR, "span")
            title = self._clean_text(title_element.text)
            
            # Extract price (look for text with $ symbol)
            price_text = None
            try:
                price_element = listing_element.find_element(By.XPATH, ".//span[contains(text(), '$')]")
                price_text = price_element.text
            except NoSuchElementException:
                pass
            
            price = self._extract_price(price_text) if price_text else None
            
            # Extract image URL
            image_url = None
            try:
                img_element = listing_element.find_element(By.TAG_NAME, "img")
                image_url = img_element.get_attribute('src')
            except NoSuchElementException:
                pass
            
            # Build product dictionary
            product = {
                'title': title,
                'price': price,
                'url': url,
                'location': 'Facebook Marketplace',  # Location is in the search context
                'posted_date': datetime.now().strftime("%Y-%m-%d"),
                'image_url': image_url,
                'platform': 'facebook'
            }
            
            return product
            
        except Exception as e:
            logger.error(f"Error parsing listing: {e}")
            return None

    
    async def get_product_details(self, product_url: str) -> Dict:
        """
        Get detailed information about a specific product.
        
        Args:
            product_url: URL of the product listing
        
        Returns:
            Dict: Detailed product information
        """
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        # Setup driver if needed
        if not self.driver:
            self._setup_driver()
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        details = await loop.run_in_executor(None, self._scrape_product_page, product_url)
        
        return details

    def _scrape_product_page(self, url: str) -> Dict:
        """
        Scrape product details page (blocking method).
        
        Args:
            url: Product URL
        
        Returns:
            Dict: Product details
        """
        try:
            self.driver.get(url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Extract title
            title = ""
            try:
                title_element = self.driver.find_element(By.CSS_SELECTOR, "span[class*='x1lliihq']")
                title = self._clean_text(title_element.text)
            except NoSuchElementException:
                pass
            
            # Extract price
            price = None
            try:
                price_element = self.driver.find_element(By.XPATH, "//span[contains(text(), '$')]")
                price = self._extract_price(price_element.text)
            except NoSuchElementException:
                pass
            
            # Extract description
            description = ""
            try:
                desc_element = self.driver.find_element(By.CSS_SELECTOR, "div[class*='xz9dl7a']")
                description = self._clean_text(desc_element.text)
            except NoSuchElementException:
                pass
            
            # Extract location
            location = ""
            try:
                location_element = self.driver.find_element(By.XPATH, "//span[contains(text(), ',')]")
                location = self._clean_text(location_element.text)
            except NoSuchElementException:
                pass
            
            # Build details dictionary
            details = {
                'title': title,
                'price': price,
                'description': description,
                'location': location,
                'url': url,
                'posted_date': datetime.now().strftime("%Y-%m-%d"),
                'platform': 'facebook'
            }
            
            return details
            
        except Exception as e:
            logger.error(f"Error scraping product page: {e}")
            return {'url': url, 'error': str(e)}

    
    async def is_available(self, product_url: str) -> bool:
        """
        Check if a product listing is still available.
        
        Args:
            product_url: URL of the product listing
        
        Returns:
            bool: True if available, False if removed/sold
        """
        try:
            # Get product details
            details = await self.get_product_details(product_url)
            
            # If we got details without error, it's available
            # In reality, you'd check for "sold" or "unavailable" text
            if 'error' in details:
                return False
            
            # Check if page contains "sold" or "no longer available"
            if not self.driver:
                return True
            
            page_text = self.driver.page_source.lower()
            unavailable_keywords = ['sold', 'no longer available', 'removed', 'deleted']
            
            for keyword in unavailable_keywords:
                if keyword in page_text:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return False

    async def close(self):
        """Close browser and cleanup resources."""
        if self.driver:
            self.driver.quit()
        await super().close()

   
    


# Test code
if __name__ == "__main__":
    logger.info("FacebookMarketplaceScraper Class Created")
    logger.info("=" * 60)
    async def test_search():
        """Test search functionality"""
        logger.info("\n" + "=" * 60)
        logger.info("Testing Facebook Marketplace Search")
        logger.info("=" * 60)
        
        scraper = FacebookMarketplaceScraper(headless=True)
        
        try:
            # Search for iPhone
            results = await scraper.search("iPhone", "newyork", max_results=5)
            
            logger.debug(f"\n✓ Found {len(results)} products")
            
            if results:
                logger.info("\nFirst product:")
                logger.debug(f"  Title: {results[0]['title']}")
                logger.debug(f"  Price: ${results[0]['price']}")
                logger.debug(f"  URL: {results[0]['url'][:50]}...")
            
        finally:
            await scraper.close()
        
        logger.info("=" * 60)

    asyncio.run(test_search())

    async def test_get_product_details():
        """Test Get Product details functionality"""
        logger.info("\n" + "=" * 60)
        logger.info("Testing Facebook Marketplace Get Product Details")
        logger.info("=" * 60)
        
        scraper = FacebookMarketplaceScraper(headless=True)
        
        try:
            # Search for iPhone
            results = await scraper.search("iPhone", "newyork", max_results=5)
            
            if results:
                url = results[0]['url']
                details = await scraper.get_product_details(url)
                
                logger.debug(f"Title: {details['title']}")
                logger.debug(f"Price: ${details['price']}")
                logger.debug(f"Description: {details['description'][:100]}...")
                
            
        finally:
            await scraper.close()
        
        logger.info("=" * 60)

    asyncio.run(test_get_product_details())

    async def test_availability():
        """Test Is Available functionality"""
        logger.info("\n" + "=" * 60)
        logger.info("Testing Facebook Marketplace Is Available functionality")
        logger.info("=" * 60)
        scraper = FacebookMarketplaceScraper(headless=True)
        # Test with a real listing
        results = await scraper.search("iPhone", "sfbay", max_results=1)
        if results:
            url = results[0]['url']
            available = await scraper.is_available(url)
            logger.debug(f"Listing available: {available}")
        
        # Test with fake URL (should return False)
        fake_url = "https://sfbay.craigslist.org/sfc/mob/d/fake-listing/1234567890.html"
        available = await scraper.is_available(fake_url)
        logger.info(f"Fake listing available: {available}")  # Should be False
    
        await scraper.close()

    asyncio.run(test_availability())
