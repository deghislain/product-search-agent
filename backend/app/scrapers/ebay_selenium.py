"""
eBay Scraper Module - Selenium Version

This version uses Selenium with undetected-chromedriver to bypass eBay's bot detection.
It's slower than the httpx version but more reliable for eBay scraping.

Installation required:
    pip install undetected-chromedriver selenium
"""
import sys
import logging
from pathlib import Path
import time

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import List, Dict, Optional
from datetime import datetime

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Warning: undetected-chromedriver not installed. Install with: pip install undetected-chromedriver selenium")

from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.utils.rate_limiter import RateLimiter

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EbaySeleniumScraper(BaseScraper):
    """
    Selenium-based scraper for eBay marketplace.
    
    Uses undetected-chromedriver to bypass bot detection.
    Slower than httpx but more reliable for eBay.
    
    Example:
        >>> scraper = EbaySeleniumScraper()
        >>> results = await scraper.search("iPhone 13", max_results=10)
        >>> print(f"Found {len(results)} products")
        >>> await scraper.close()
    """
    
    def __init__(self, rate_limiter: Optional[RateLimiter] = None, headless: bool = True):
        """
        Initialize eBay Selenium scraper.
        
        Args:
            rate_limiter: Optional rate limiter
            headless: Run browser in headless mode (default: True)
        
        Raises:
            ImportError: If selenium/undetected-chromedriver not installed
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Selenium and undetected-chromedriver are required. "
                "Install with: pip install undetected-chromedriver selenium"
            )
        
        super().__init__(rate_limiter)
        self.base_url = "https://www.ebay.com"
        self.headless = headless
        self.driver = None
        self._init_driver()
    
    def _init_driver(self):
        """Initialize the Chrome driver with undetected-chromedriver."""
        try:
            options = uc.ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless=new')
            
            # Additional options to avoid detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            self.driver = uc.Chrome(options=options)
            logger.info("Chrome driver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
    
    async def search(
        self, 
        query: str, 
        location: str = "US",
        **kwargs
    ) -> List[Dict]:
        """
        Search for products on eBay using Selenium.
        
        Args:
            query: Search term (e.g., "iPhone 13", "MacBook Pro")
            location: Country code (e.g., "US", "UK", "CA")
            **kwargs: Additional parameters:
                - min_price: Minimum price filter
                - max_price: Maximum price filter
                - condition: "new" or "used"
                - buy_it_now_only: True to exclude auctions (default: True)
                - max_results: Maximum number of results (default: 100)
        
        Returns:
            List of product dictionaries
        """
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        # Extract optional parameters
        min_price = kwargs.get('min_price')
        max_price = kwargs.get('max_price')
        condition = kwargs.get('condition')
        buy_it_now_only = kwargs.get('buy_it_now_only', True)
        max_results = kwargs.get('max_results', 100)
        
        # Build search URL
        search_url = self._build_search_url(
            query, min_price, max_price, condition, buy_it_now_only
        )
        
        try:
            logger.info(f"Navigating to: {search_url}")
            self.driver.get(search_url)
            
            # Wait for results to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "s-item"))
                )
            except TimeoutException:
                logger.warning("Timeout waiting for search results")
                return []
            
            # Small delay to ensure page is fully loaded
            time.sleep(2)
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract listings
            products = []
            result_items = soup.find_all('li', class_='s-item')
            
            logger.info(f"Found {len(result_items)} items on page")
            
            for item in result_items[:max_results]:
                product = self._parse_search_result(item)
                if product:
                    products.append(product)
            
            logger.info(f"Successfully parsed {len(products)} products for query: {query}")
            return products
            
        except Exception as e:
            logger.error(f"Error searching eBay with Selenium: {e}")
            return []
    
    def _build_search_url(
        self,
        query: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        condition: Optional[str] = None,
        buy_it_now_only: bool = True
    ) -> str:
        """Build eBay search URL with parameters."""
        base = f"{self.base_url}/sch/i.html"
        
        params = {
            '_nkw': query,
            '_sop': '12',  # Sort by: Best Match
        }
        
        if min_price:
            params['_udlo'] = int(min_price)
        if max_price:
            params['_udhi'] = int(max_price)
        
        if condition:
            if condition.lower() == 'new':
                params['LH_ItemCondition'] = '1000'
            elif condition.lower() == 'used':
                params['LH_ItemCondition'] = '3000'
        
        if buy_it_now_only:
            params['LH_BIN'] = '1'
        
        return self._build_url(base, params)
    
    def _parse_search_result(self, item) -> Optional[Dict]:
        """Parse a single search result item."""
        try:
            # Skip sponsored items
            if 'SPONSORED' in item.get_text().upper():
                return None
            
            # Extract title
            title_elem = item.find('div', class_='s-item__title')
            if not title_elem:
                return None
            title = self._clean_text(title_elem.get_text())
            
            # Skip header items
            if title.lower() in ['shop on ebay', 'new listing']:
                return None
            
            # Extract URL
            link_elem = item.find('a', class_='s-item__link')
            if not link_elem or 'href' not in link_elem.attrs:
                return None
            url = link_elem['href']
            
            # Extract item ID
            item_id = None
            if '/itm/' in url:
                item_id = url.split('/itm/')[1].split('?')[0]
            
            # Extract price
            price_elem = item.find('span', class_='s-item__price')
            price = self._extract_price(price_elem.get_text()) if price_elem else None
            
            # Extract location
            location_elem = item.find('span', class_='s-item__location')
            location = self._clean_text(location_elem.get_text()) if location_elem else "Unknown"
            
            # Extract shipping cost
            shipping_elem = item.find('span', class_='s-item__shipping')
            shipping_cost = None
            if shipping_elem:
                shipping_text = shipping_elem.get_text()
                if 'free' in shipping_text.lower():
                    shipping_cost = 0.0
                else:
                    shipping_cost = self._extract_price(shipping_text)
            
            # Extract condition
            condition_elem = item.find('span', class_='SECONDARY_INFO')
            condition = self._clean_text(condition_elem.get_text()) if condition_elem else "Unknown"
            
            # Extract image
            image_elem = item.find('img', class_='s-item__image-img')
            image_url = image_elem['src'] if image_elem and 'src' in image_elem.attrs else None
            
            return {
                'title': title,
                'price': price,
                'url': url,
                'location': location,
                'condition': condition,
                'shipping_cost': shipping_cost,
                'image_url': image_url,
                'item_id': item_id,
                'platform': 'ebay'
            }
            
        except Exception as e:
            logger.error(f"Error parsing search result: {e}")
            return None
    
    async def get_product_details(self, product_url: str) -> Dict:
        """Get detailed information about a specific product."""
        await self.rate_limiter.acquire()
        
        try:
            logger.info(f"Getting details for: {product_url}")
            self.driver.get(product_url)
            
            # Wait for page to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "x-item-title__mainTitle"))
                )
            except TimeoutException:
                logger.warning("Timeout waiting for product details")
                return {'url': product_url, 'error': 'Timeout', 'platform': 'ebay'}
            
            time.sleep(2)
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract title
            title_elem = soup.find('h1', class_='x-item-title__mainTitle')
            title = self._clean_text(title_elem.get_text()) if title_elem else "Unknown"
            
            # Extract price
            price_elem = soup.find('div', class_='x-price-primary')
            price = None
            if price_elem:
                price_span = price_elem.find('span', class_='ux-textspans')
                if price_span:
                    price = self._extract_price(price_span.get_text())
            
            # Extract condition
            condition_elem = soup.find('div', class_='x-item-condition')
            condition = "Unknown"
            if condition_elem:
                condition_span = condition_elem.find('span', class_='ux-textspans')
                if condition_span:
                    condition = self._clean_text(condition_span.get_text())
            
            # Extract description
            description = ""
            desc_elem = soup.find('div', class_='x-item-description')
            if desc_elem:
                description = self._clean_text(desc_elem.get_text())
            
            # Extract images
            images = []
            image_carousel = soup.find('div', class_='ux-image-carousel')
            if image_carousel:
                for img in image_carousel.find_all('img'):
                    if 'src' in img.attrs:
                        images.append(img['src'])
            
            # Extract seller information
            seller_name = "Unknown"
            seller_card = soup.find('div', class_='x-sellercard-atf')
            if seller_card:
                seller_span = seller_card.find('span', class_='ux-textspans')
                if seller_span:
                    seller_name = self._clean_text(seller_span.get_text())
            
            # Extract item specifics
            item_specifics = {}
            specifics_section = soup.find('div', class_='ux-layout-section--itemDetails')
            if specifics_section:
                rows = specifics_section.find_all('div', class_='ux-labels-values')
                for row in rows:
                    label = row.find('span', class_='ux-textspans--BOLD')
                    value = row.find('span', class_='ux-textspans--SECONDARY')
                    if label and value:
                        key = self._clean_text(label.get_text())
                        val = self._clean_text(value.get_text())
                        item_specifics[key] = val
            
            return {
                'title': title,
                'price': price,
                'description': description,
                'condition': condition,
                'images': images,
                'seller_name': seller_name,
                'item_specifics': item_specifics,
                'url': product_url,
                'platform': 'ebay'
            }
            
        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            return {
                'url': product_url,
                'error': str(e),
                'platform': 'ebay'
            }
    
    async def is_available(self, product_url: str) -> bool:
        """Check if an eBay listing is still available."""
        await self.rate_limiter.acquire()
        
        try:
            self.driver.get(product_url)
            time.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Check for "ended" message
            ended_elem = soup.find('div', class_='vi-content-wrapper')
            if ended_elem and 'ended' in ended_elem.get_text().lower():
                return False
            
            # Check if title exists
            title_elem = soup.find('h1', class_='x-item-title__mainTitle')
            if title_elem:
                return True
            
            # Check for error page
            error_elem = soup.find('div', id='error-page')
            if error_elem:
                return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return False
    
    async def close(self):
        """Close the browser and cleanup resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Chrome driver closed")
            except Exception as e:
                logger.error(f"Error closing driver: {e}")
        
        # Also close the httpx client from parent
        await super().close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Test code
if __name__ == "__main__":
    import asyncio
    
    async def test_selenium_scraper():
        """Test the Selenium-based eBay scraper."""
        print("=" * 60)
        print("Testing eBay Selenium Scraper")
        print("=" * 60)
        
        try:
            async with EbaySeleniumScraper(headless=False) as scraper:
                # Test search
                print("\n1. Testing search...")
                results = await scraper.search("iPhone 13", max_results=5)
                print(f"   Found {len(results)} products")
                
                if results:
                    print(f"\n   First result:")
                    print(f"   Title: {results[0]['title']}")
                    print(f"   Price: ${results[0]['price']}")
                    print(f"   URL: {results[0]['url']}")
                    
                    # Test product details
                    print("\n2. Testing product details...")
                    details = await scraper.get_product_details(results[0]['url'])
                    print(f"   Title: {details['title']}")
                    print(f"   Condition: {details['condition']}")
                    print(f"   Images: {len(details.get('images', []))}")
                    
                    # Test availability
                    print("\n3. Testing availability...")
                    available = await scraper.is_available(results[0]['url'])
                    print(f"   Available: {available}")
                
                print("\n" + "=" * 60)
                print("✅ Selenium scraper test complete!")
                print("=" * 60)
                
        except ImportError as e:
            print(f"\n❌ Error: {e}")
            print("\nInstall required packages:")
            print("  pip install undetected-chromedriver selenium")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    asyncio.run(test_selenium_scraper())

# Made with Bob
