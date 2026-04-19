"""
    eBay Scraper Module

    Implements scraping functionality for eBay marketplace.
    Focuses on "Buy It Now" listings (not auctions).
"""
import sys
import logging
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.utils.rate_limiter import RateLimiter

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EbayScraper(BaseScraper):
    """
        Scraper for eBay marketplace.

        Focuses on "Buy It Now" listings (fixed price items).
        Does not handle auction-style listings.

        Example:
            >>> scraper = EbayScraper()
            >>> results = await scraper.search("iPhone 13", max_results=10)
            >>> print(f"Found {len(results)} products")
    """

    def __init__(self, rate_limiter: Optional[RateLimiter] = None):
        """
        Initialize eBay scraper.
        
        Args:
            rate_limiter: Optional rate limiter. If not provided,
                            uses default (10 requests per 60 seconds)
        """
        super().__init__(rate_limiter)
        self.base_url = "https://www.ebay.com"
        
        # Override client with eBay-specific settings
        import httpx
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers=self._get_ebay_headers(),
            follow_redirects=True,  # Follow redirects automatically
            max_redirects=5
        )
    
    def _get_ebay_headers(self) -> dict:
        """
        Get eBay-specific headers to avoid bot detection.
        
        Returns:
            Dict of HTTP headers optimized for eBay
        """
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

    async def search(
        self, 
        query: str, 
        location: str = "US",  # Default to United States
        **kwargs
    ) -> List[Dict]:
        """
        Search for products on eBay.
        
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
            List of product dictionaries with keys:
                - title: Product title
                - price: Product price (float)
                - url: Product URL
                - location: Seller location
                - condition: Item condition (New/Used)
                - shipping_cost: Shipping cost (if available)
                - image_url: First image URL
                - item_id: eBay item ID
        
        Example:
            >>> results = await scraper.search("iPhone 13", max_price=800)
            >>> print(results[0]['title'])
            'iPhone 13 Pro 256GB - Unlocked'
        """
        logger.info("************************Searching Ebay for query: %s", query)
        # Extract optional parameters
        min_price = kwargs.get('min_price')
        max_price = kwargs.get('max_price')
        condition = kwargs.get('condition')  # 'new' or 'used'
        buy_it_now_only = kwargs.get('buy_it_now_only', True)
        max_results = kwargs.get('max_results', 100)
        
        # Build search URL
        search_url = self._build_search_url(
            query, min_price, max_price, condition, buy_it_now_only
        )
        
        try:
            # Make request with rate limiting (inherited from BaseScraper)
            response = await self._make_request(search_url)
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract listings
            products = []
            result_items = soup.find_all('li', class_='s-item')
            
            for item in result_items[:max_results]:
                product = self._parse_search_result(item)
                if product:
                    products.append(product)
            
            logger.debug(f"********************************✓ Found {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Error searching eBay: {e}")
            return []

    def _build_search_url(
    self,
        query: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        condition: Optional[str] = None,
        buy_it_now_only: bool = True
    ) -> str:
        """
        Build eBay search URL with parameters.
        
        Args:
            query: Search query
            min_price: Minimum price filter
            max_price: Maximum price filter
            condition: "new" or "used"
            buy_it_now_only: If True, only show Buy It Now listings
        
        Returns:
            Complete search URL
        
        Example:
            >>> url = scraper._build_search_url("iPhone", 500, 1000, "new")
            >>> print(url)
            'https://www.ebay.com/sch/i.html?_nkw=iPhone&_udlo=500&_udhi=1000...'
        """
        # Base search URL
        base = f"{self.base_url}/sch/i.html"
        
        # Build parameters
        params = {
            '_nkw': query,  # Search keyword
            '_sop': '12',   # Sort by: Best Match
        }
        
        # Add price filters
        if min_price:
            params['_udlo'] = int(min_price)  # Lower price
        if max_price:
            params['_udhi'] = int(max_price)  # Upper price
        
        # Add condition filter
        if condition:
            if condition.lower() == 'new':
                params['LH_ItemCondition'] = '1000'  # New
            elif condition.lower() == 'used':
                params['LH_ItemCondition'] = '3000'  # Used
        
        # Buy It Now only (exclude auctions)
        if buy_it_now_only:
            params['LH_BIN'] = '1'  # Buy It Now
        
        # Use inherited _build_url method from BaseScraper
        return self._build_url(base, params)

    def _parse_search_result(self, item) -> Optional[Dict]:
        """
        Parse a single search result item.
        
        Args:
            item: BeautifulSoup element for result item
        
        Returns:
            Dictionary with product info, or None if parsing fails
        """
        try:
            # Skip sponsored items or ads
            if 'SPONSORED' in item.get_text().upper():
                return None
            
            # Extract title
            title_elem = item.find('div', class_='s-item__title')
            if not title_elem:
                return None
            title = self._clean_text(title_elem.get_text())
            
            # Skip "Shop on eBay" header items
            if title.lower() in ['shop on ebay', 'new listing']:
                return None
            
            # Extract URL
            link_elem = item.find('a', class_='s-item__link')
            if not link_elem or 'href' not in link_elem.attrs:
                return None
            url = link_elem['href']
            
            # Extract item ID from URL
            # URL format: https://www.ebay.com/itm/123456789?...
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
        """
        Get detailed information about a specific product.
        
        Args:
            product_url: Full URL to eBay listing
        
        Returns:
            Dictionary with detailed product information:
                - title: Product title
                - price: Product price
                - description: Full description
                - condition: Item condition
                - images: List of image URLs
                - seller_name: Seller's username
                - seller_rating: Seller's feedback score
                - item_specifics: Dict of product attributes
                - url: Product URL
        
        Example:
            >>> details = await scraper.get_product_details("https://www.ebay.com/itm/...")
            >>> print(details['description'])
        """
        try:
            # Make request with rate limiting
            response = await self._make_request(product_url)
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
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
            seller_rating = None
            seller_card = soup.find('div', class_='x-sellercard-atf')
            if seller_card:
                seller_span = seller_card.find('span', class_='ux-textspans')
                if seller_span:
                    seller_name = self._clean_text(seller_span.get_text())
            
            # Extract item specifics (brand, model, color, etc.)
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
                'seller_rating': seller_rating,
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
        """
        Check if an eBay listing is still available.
        
        Args:
            product_url: URL of the listing to check
        
        Returns:
            True if listing is still active, False if removed/sold
        
        Example:
            >>> available = await scraper.is_available("https://www.ebay.com/itm/...")
            >>> if available:
            ...     print("Listing is still active!")
        """
        try:
            # Make request
            response = await self._make_request(product_url)
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for "This listing was ended" message
            ended_elem = soup.find('div', class_='vi-content-wrapper')
            if ended_elem and 'ended' in ended_elem.get_text().lower():
                return False
            
            # Check if title exists (indicates active listing)
            title_elem = soup.find('h1', class_='x-item-title__mainTitle')
            if title_elem:
                return True
            
            # Check for "Item not found" or similar messages
            error_elem = soup.find('div', id='error-page')
            if error_elem:
                return False
            
            # If we can't determine, assume it's not available
            return False
            
        except Exception as e:
            # If request fails (404, etc.), listing is not available
            logger.error(f"Error checking availability: {e}")
            return False


if __name__ == "__main__":
    import asyncio
    
    async def test_search():
        scraper = EbayScraper()
        results = await scraper.search("iPhone 13", max_results=5)
        
        print(f"Found {len(results)} products:")
        for product in results:
            print(f"  - {product['title']}: ${product['price']}")
        
        await scraper.close()
    
    asyncio.run(test_search())

    async def test_details():
        scraper = EbayScraper()
        
        # First get a product URL from search
        results = await scraper.search("iPhone 13", max_results=1)
        if results:
            url = results[0]['url']
            details = await scraper.get_product_details(url)
            
            print(f"Title: {details['title']}")
            print(f"Price: ${details['price']}")
            print(f"Condition: {details['condition']}")
            print(f"Images: {len(details['images'])}")
        
            await scraper.close()

    asyncio.run(test_details())

    async def test_availability():
        scraper = EbayScraper()
        
        # Test with a real listing
        results = await scraper.search("iPhone 13", max_results=1)
        if results:
            url = results[0]['url']
            available = await scraper.is_available(url)
            print(f"Listing available: {available}")
        
        # Test with fake URL (should return False)
        fake_url = "https://www.ebay.com/itm/999999999999"
        available = await scraper.is_available(fake_url)
        print(f"Fake listing available: {available}")  # Should be False
        
        await scraper.close()

    asyncio.run(test_availability())