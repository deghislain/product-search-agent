"""
Craigslist Scraper Module

Implements scraping functionality for Craigslist marketplace.
"""
import sys, logging
from pathlib import Path

# Add parent directory to Python path so we can import 'app' module
# This allows the script to find the 'app' package when run directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.utils.rate_limiter import RateLimiter

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



class CraigslistScraper(BaseScraper):
    """
    Scraper for Craigslist marketplace.
    
    Inherits from BaseScraper and implements platform-specific logic
    for searching and extracting product information from Craigslist.
    
    Example:
        >>> scraper = CraigslistScraper()
        >>> results = await scraper.search("iPhone 13", "newyork")
        >>> print(f"Found {len(results)} products")
    """
    
    def __init__(self, rate_limiter: Optional[RateLimiter] = None):
        """
        Initialize Craigslist scraper.
        
        Args:
            rate_limiter: Optional rate limiter. If not provided,
                         uses default (10 requests per 60 seconds)
        """
        super().__init__(rate_limiter)
        self.base_url = "https://craigslist.org"
    
    async def search(
        self, 
        query: str, 
        location: str = "sfbay",  # Default to San Francisco Bay Area
        **kwargs
    ) -> List[Dict]:
        """
        Search for products on Craigslist.
        
        Args:
            query: Search term (e.g., "iPhone 13", "MacBook Pro")
            location: Craigslist site location (e.g., "sfbay", "newyork", "losangeles")
            **kwargs: Additional parameters:
                - category: Craigslist category (default: "sss" for all for sale)
                - min_price: Minimum price filter
                - max_price: Maximum price filter
                - max_results: Maximum number of results to return (default: 100)
        
        Returns:
            List of product dictionaries with keys:
                - title: Product title
                - price: Product price (float)
                - url: Product URL
                - location: Product location
                - posted_date: When listing was posted
                - image_url: First image URL (if available)
                - listing_id: Craigslist listing ID
        
        Example:
            >>> results = await scraper.search("iPhone 13", "newyork", max_price=800)
            >>> print(results[0]['title'])
            'iPhone 13 Pro 256GB - Excellent Condition'
        """
        logger.info("************************Searching Craigslist for query: %s", query)
        # Extract optional parameters
        category = kwargs.get('category', 'sss')  # 'sss' = all for sale
        min_price = kwargs.get('min_price')
        max_price = kwargs.get('max_price')
        max_results = kwargs.get('max_results', 100)
        
        # Build search URL
        search_url = self._build_search_url(
            location, category, query, min_price, max_price
        )
        
        try:
            # Make request with rate limiting (inherited from BaseScraper)
            response = await self._make_request(search_url)
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract listings - NEW STRUCTURE (2026)
            products = []
            # Try new structure first
            result_rows = soup.find_all('li', class_='cl-static-search-result')
            
            # Fallback to old structure if new one not found
            if not result_rows:
                result_rows = soup.find_all('li', class_='result-row')
            
            for row in result_rows[:max_results]:
                product = self._parse_search_result(row, location)
                if product:
                    products.append(product)
            
            logger.debug(f"***********************************✓ Found {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Error searching Craigslist: {e}")
            return []


    def _build_search_url(
        self,
        location: str,
        category: str,
        query: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> str:
        """
        Build Craigslist search URL with parameters.
        
        Args:
            location: Craigslist site (e.g., "sfbay", "newyork")
            category: Category code (e.g., "sss" for all for sale)
            query: Search query
            min_price: Minimum price filter
            max_price: Maximum price filter
        
        Returns:
            Complete search URL
        
        Example:
            >>> url = scraper._build_search_url("sfbay", "sss", "iPhone", 500, 1000)
            >>> print(url)
            'https://sfbay.craigslist.org/search/sss?query=iPhone&min_price=500&max_price=1000'
        """
        # Base URL for location
        base = f"https://{location}.craigslist.org/search/{category}"
        
        # Build parameters
        params = {'query': query}
        
        if min_price:
            params['min_price'] = int(min_price)
        if max_price:
            params['max_price'] = int(max_price)
        
        # Use inherited _build_url method from BaseScraper
        return self._build_url(base, params)


    def _parse_search_result(self, row, location: str) -> Optional[Dict]:
        """
        Parse a single search result row.
        
        Args:
            row: BeautifulSoup element for result row
            location: Craigslist location
        
        Returns:
            Dictionary with product info, or None if parsing fails
        
        Note:
            Updated for new Craigslist HTML structure (2026):
            - Uses <li class="cl-static-search-result">
            - Title in <div class="title">
            - Price in <div class="price">
            - Location in <div class="location">
            - Images are NOT in search results, must fetch from detail page
        """
        try:
            # NEW STRUCTURE: Find the link element (contains all info)
            link_elem = row.find('a')
            if not link_elem:
                return None
            
            # Extract URL
            url = link_elem.get('href', '')
            if not url:
                return None
            
            # Make URL absolute if it's relative
            if url.startswith('/'):
                url = f"https://{location}.craigslist.org{url}"
            
            # Extract listing ID from URL
            listing_id = url.split('/')[-1].replace('.html', '')
            
            # NEW STRUCTURE: Extract title from div.title
            title_elem = row.find('div', class_='title')
            if not title_elem:
                return None
            title = self._clean_text(title_elem.get_text())
            
            # NEW STRUCTURE: Extract price from div.price
            price_elem = row.find('div', class_='price')
            price = self._extract_price(price_elem.get_text()) if price_elem else None
            
            # NEW STRUCTURE: Extract location from div.location
            location_elem = row.find('div', class_='location')
            product_location = self._clean_text(location_elem.get_text()) if location_elem else location
            
            # Extract date (if available - may not be in new structure)
            time_elem = row.find('time')
            posted_date = time_elem['datetime'] if time_elem and 'datetime' in time_elem.attrs else None
            
            # NOTE: Images are NOT available in search results on new Craigslist
            # They must be fetched from the detail page
            # For now, set to None - can be fetched later if needed
            image_url = None
            
            return {
                'title': title,
                'price': price,
                'url': url,
                'location': product_location,
                'posted_date': posted_date,
                'image_url': image_url,
                'listing_id': listing_id,
                'platform': 'craigslist'
            }
            
        except Exception as e:
            logger.error(f"Error parsing search result: {e}")
            return None
    
    async def get_first_image_url(self, product_url: str) -> Optional[str]:
        """
        Fetch the first image URL from a product detail page.
        
        Args:
            product_url: Full URL to Craigslist listing
            
        Returns:
            First image URL if found, None otherwise
            
        Note:
            This is a lightweight method to fetch just the first image
            without parsing all product details.
        """
        try:
            response = await self._make_request(product_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for images in the gallery
            # Craigslist uses <img> tags with class "slide" or in div with id "thumbs"
            img_elem = soup.find('img', class_='slide')
            if img_elem and 'src' in img_elem.attrs:
                return img_elem['src']
            
            # Fallback: look for any image in the gallery div
            gallery = soup.find('div', class_='gallery')
            if gallery:
                img_elem = gallery.find('img')
                if img_elem and 'src' in img_elem.attrs:
                    return img_elem['src']
            
            return None
            
        except Exception as e:
            logger.debug(f"Could not fetch image from {product_url}: {e}")
            return None
    
    async def get_product_details(self, product_url: str) -> Dict:
        """
        Get detailed information about a specific product.
        
        Args:
            product_url: Full URL to Craigslist listing
        
        Returns:
            Dictionary with detailed product information:
                - title: Product title
                - price: Product price
                - description: Full description
                - location: Product location
                - posted_date: When posted
                - images: List of image URLs
                - attributes: Dict of product attributes
                - seller_info: Seller information (if available)
                - url: Product URL
        
        Example:
            >>> details = await scraper.get_product_details("https://sfbay.craigslist.org/...")
            >>> print(details['description'])
        """
        try:
            # Make request with rate limiting
            response = await self._make_request(product_url)
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title_elem = soup.find('span', id='titletextonly')
            title = self._clean_text(title_elem.get_text()) if title_elem else "Unknown"
            
            # Extract price
            price_elem = soup.find('span', class_='price')
            price = self._extract_price(price_elem.get_text()) if price_elem else None
            
            # Extract description
            desc_elem = soup.find('section', id='postingbody')
            description = ""
            if desc_elem:
                # Remove "QR Code Link to This Post" text
                for qr in desc_elem.find_all('div', class_='print-qrcode-container'):
                    qr.decompose()
                description = self._clean_text(desc_elem.get_text())
            
            # Extract images
            images = []
            image_container = soup.find('div', class_='slide')
            if image_container:
                for img in image_container.find_all('img'):
                    if 'src' in img.attrs:
                        images.append(img['src'])
            
            # Extract attributes (condition, make, model, etc.)
            attributes = {}
            attr_groups = soup.find_all('p', class_='attrgroup')
            for group in attr_groups:
                for span in group.find_all('span'):
                    text = span.get_text().strip()
                    if ':' in text:
                        key, value = text.split(':', 1)
                        attributes[key.strip()] = value.strip()
                    else:
                        # Some attributes don't have colons (like "excellent condition")
                        attributes[text] = True
            
            # Extract location
            location = "Unknown"
            map_elem = soup.find('div', class_='mapaddress')
            if map_elem:
                location = self._clean_text(map_elem.get_text())
            
            # Extract posted date
            posted_date = None
            time_elem = soup.find('time')
            if time_elem and 'datetime' in time_elem.attrs:
                posted_date = time_elem['datetime']
            
            return {
                'title': title,
                'price': price,
                'description': description,
                'location': location,
                'posted_date': posted_date,
                'images': images,
                'attributes': attributes,
                'url': product_url,
                'platform': 'craigslist'
            }
            
        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            return {
                'url': product_url,
                'error': str(e),
                'platform': 'craigslist'
            }
    async def is_available(self, product_url: str) -> bool:
        """
        Check if a Craigslist listing is still available.
        
        Args:
            product_url: URL of the listing to check
        
        Returns:
            True if listing is still active, False if removed/sold
        
        Example:
            >>> available = await scraper.is_available("https://sfbay.craigslist.org/...")
            >>> if available:
            ...     print("Listing is still active!")
        """
        try:
            # Make request
            response = await self._make_request(product_url)
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for "This posting has been deleted" message
            deleted_elem = soup.find('div', class_='removed')
            if deleted_elem:
                return False
            
            # Check if title exists (indicates active listing)
            title_elem = soup.find('span', id='titletextonly')
            if title_elem:
                return True
            
            # If we can't determine, assume it's not available
            return False
            
        except Exception as e:
            # If request fails (404, etc.), listing is not available
            logger.error(f"Error checking availability: {e}")
            return False

            

if __name__ == "__main__":
    import asyncio
    
    async def test_search():
        scraper = CraigslistScraper()
        results = await scraper.search("Apple iPhone 13 Pro 5G", "sfbay", max_results=5)
        
        logger.debug(f"Found {len(results)} products:")
        for product in results:
            logger.debug(f"  - {product['title']}: ${product['price']}")
        
        await scraper.close()
    
    asyncio.run(test_search())

    async def test_details():
        scraper = CraigslistScraper()
        
        # First get a product URL from search
        results = await scraper.search("iPhone", "sfbay", max_results=1)
        if results:
            url = results[0]['url']
            details = await scraper.get_product_details(url)
            
            logger.debug(f"Title: {details['title']}")
            logger.debug(f"Price: ${details['price']}")
            logger.debug(f"Description: {details['description'][:100]}...")
            logger.debug(f"Images: {len(details['images'])}")
        
        await scraper.close()

    asyncio.run(test_details())
    
    async def test_availability():
        scraper = CraigslistScraper()
        
        # Test with a real listing
        results = await scraper.search("iPhone", "sfbay", max_results=1)
        if results:
            url = results[0]['url']
            available = await scraper.is_available(url)
            logger.debug(f"Listing available: {available}")
        
        # Test with fake URL (should return False)
        fake_url = "https://sfbay.craigslist.org/sfc/mob/d/fake-listing/1234567890.html"
        available = await scraper.is_available(fake_url)
        logger.debug(f"Fake listing available: {available}")  # Should be False
        
        await scraper.close()

    asyncio.run(test_availability())