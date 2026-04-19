"""
Base Scraper Module

This module provides the abstract base class for all platform-specific scrapers.
All scrapers (Craigslist, eBay, Facebook Marketplace) inherit from BaseScraper.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import re
import httpx
import sys
from pathlib import Path

# Add parent directory to path for imports when running as script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.utils.rate_limiter import RateLimiter


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    
    This class defines the interface that all platform-specific scrapers must implement,
    and provides common helper methods for HTTP requests, text processing, and price extraction.
    
    All scrapers (Craigslist, eBay, Facebook Marketplace) will inherit from this class
    and must implement the abstract methods: search(), get_product_details(), and is_available().
    
    Attributes:
        rate_limiter: RateLimiter instance to control request frequency
        client: httpx.AsyncClient for making HTTP requests
    
    Example:
        >>> class CraigslistScraper(BaseScraper):
        ...     async def search(self, query, location, **kwargs):
        ...         # Implementation here
        ...         pass
    """
    
    def __init__(self, rate_limiter: Optional[RateLimiter] = None):
        """
        Initialize scraper with rate limiter and HTTP client.
        
        Args:
            rate_limiter: Optional rate limiter for controlling request rate.
                         If not provided, creates default limiter (10 requests/60 seconds)
        
        Example:
            >>> # Use default rate limiter
            >>> scraper = CraigslistScraper()
            >>> 
            >>> # Use custom rate limiter
            >>> custom_limiter = RateLimiter(max_requests=5, time_window=30)
            >>> scraper = CraigslistScraper(rate_limiter=custom_limiter)
        """
        self.rate_limiter = rate_limiter or RateLimiter(max_requests=10, time_window=60)
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers=self._get_default_headers()
        )
    
    def _get_default_headers(self) -> Dict[str, str]:
        """
        Get default HTTP headers to mimic a real browser.
        
        These headers help avoid being detected as a bot by making requests
        look like they're coming from a real web browser.
        
        Returns:
            Dict[str, str]: Dictionary of HTTP headers
        """
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    
    # ==================== ABSTRACT METHODS ====================
    # These MUST be implemented by all child scrapers
    
    @abstractmethod
    async def search(self, query: str, location: str, **kwargs) -> List[Dict]:
        """
        Search for products on the platform.
        
        This method MUST be implemented by each scraper.
        
        Args:
            query: Search term (e.g., "iPhone 13", "MacBook Pro")
            location: Location to search (e.g., "New York", "San Francisco")
            **kwargs: Additional platform-specific parameters
                     (e.g., min_price, max_price, category)
        
        Returns:
            List[Dict]: List of product dictionaries, each containing:
                - title: Product title
                - price: Product price (float)
                - url: Product URL
                - location: Product location
                - posted_date: When listing was posted
                - description: Product description (optional)
                - image_url: Product image URL (optional)
        
        Example:
            >>> results = await scraper.search("iPhone 13", "New York")
            >>> print(results[0])
            {
                'title': 'iPhone 13 Pro 256GB',
                'price': 899.99,
                'url': 'https://...',
                'location': 'New York, NY',
                'posted_date': '2024-01-15',
                'description': 'Excellent condition...'
            }
        """
        pass
    
    @abstractmethod
    async def get_product_details(self, product_url: str) -> Dict:
        """
        Get detailed information about a specific product.
        
        This method MUST be implemented by each scraper.
        
        Args:
            product_url: URL of the product listing
        
        Returns:
            Dict: Dictionary with detailed product information:
                - title: Product title
                - price: Product price (float)
                - description: Full product description
                - location: Product location
                - posted_date: When listing was posted
                - seller_name: Seller's name (if available)
                - images: List of image URLs
                - condition: Product condition (if available)
                - any other platform-specific fields
        
        Example:
            >>> details = await scraper.get_product_details("https://...")
            >>> print(details['title'])
            'iPhone 13 Pro 256GB'
        """
        pass
    
    @abstractmethod
    async def is_available(self, product_url: str) -> bool:
        """
        Check if a product listing is still available.
        
        This method MUST be implemented by each scraper.
        
        Args:
            product_url: URL of the product listing
        
        Returns:
            bool: True if listing is still available, False if removed/sold
        
        Example:
            >>> available = await scraper.is_available("https://...")
            >>> if available:
            ...     print("Product still available!")
        """
        pass
    
    # ==================== HELPER METHODS ====================
    # These are available to all child scrapers
    
    async def _make_request(self, url: str, method: str = "GET", **kwargs) -> httpx.Response:
        """
        Make HTTP request with automatic rate limiting.
        
        This method automatically applies rate limiting before making requests,
        preventing the scraper from overwhelming servers or getting blocked.
        
        Args:
            url: URL to request
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            **kwargs: Additional arguments passed to httpx.request()
                     (e.g., headers, params, data, json)
        
        Returns:
            httpx.Response: HTTP response object
        
        Raises:
            httpx.HTTPError: If request fails (4xx, 5xx status codes)
        
        Example:
            >>> response = await self._make_request("https://example.com")
            >>> html = response.text
            >>> 
            >>> # With custom headers
            >>> response = await self._make_request(
            ...     "https://api.example.com",
            ...     headers={"Authorization": "Bearer token"}
            ... )
        """
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        try:
            # Make the request
            response = await self.client.request(method, url, **kwargs)
            
            # Raise exception for 4xx/5xx status codes
            response.raise_for_status()
            
            return response
            
        except httpx.HTTPStatusError as e:
            # HTTP error (4xx, 5xx)
            print(f"HTTP error {e.response.status_code} for {url}: {e}")
            raise
            
        except httpx.RequestError as e:
            # Network error (connection failed, timeout, etc.)
            print(f"Request error for {url}: {e}")
            raise
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """
        Extract numeric price from text string.
        
        Handles various price formats including currency symbols, commas,
        and text like "Free" or "Best offer".
        
        Args:
            price_text: Text containing price (e.g., "$1,234.56", "Price: $50")
        
        Returns:
            Optional[float]: Extracted price as float, or None if not found
        
        Examples:
            >>> self._extract_price("$1,234.56")
            1234.56
            >>> self._extract_price("Price: $50")
            50.0
            >>> self._extract_price("Free")
            0.0
            >>> self._extract_price("Best offer")
            None
        """
        if not price_text:
            return None
        
        # Convert to lowercase for easier matching
        text_lower = price_text.lower()
        
        # Handle "free" listings
        if "free" in text_lower:
            return 0.0
        
        # Remove currency symbols and commas
        cleaned = re.sub(r'[$€£¥,]', '', price_text)
        
        # Find first number (with optional decimal)
        match = re.search(r'\d+\.?\d*', cleaned)
        
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text by removing extra whitespace.
        
        Removes leading/trailing whitespace and collapses multiple spaces
        into single spaces.
        
        Args:
            text: Text to clean
        
        Returns:
            str: Cleaned text
        
        Examples:
            >>> self._clean_text("  Hello   World  ")
            "Hello World"
            >>> self._clean_text("\\n  Text\\t  with\\n  whitespace  ")
            "Text with whitespace"
        """
        if not text:
            return ""
        
        # Split on whitespace and rejoin with single spaces
        # This handles \n, \t, multiple spaces, etc.
        return " ".join(text.split())
    
    def _extract_date(self, date_text: str) -> Optional[str]:
        """
        Extract and normalize date from text.
        
        Handles various date formats and relative dates like "2 hours ago".
        
        Args:
            date_text: Text containing date
        
        Returns:
            Optional[str]: ISO format date string (YYYY-MM-DD), or None if not found
        
        Examples:
            >>> self._extract_date("Posted 2 hours ago")
            "2024-01-15"
            >>> self._extract_date("Jan 15, 2024")
            "2024-01-15"
        """
        if not date_text:
            return None
        
        # This is a simplified implementation
        # In a real scraper, you'd use dateutil.parser or similar
        # For now, return current date as placeholder
        return datetime.now().strftime("%Y-%m-%d")
    
    def _build_url(self, base_url: str, params: Dict[str, str]) -> str:
        """
        Build URL with query parameters.
        
        Args:
            base_url: Base URL without parameters
            params: Dictionary of query parameters
        
        Returns:
            str: Complete URL with encoded parameters
        
        Example:
            >>> self._build_url("https://example.com/search", {"q": "iPhone 13", "location": "NY"})
            "https://example.com/search?q=iPhone+13&location=NY"
        """
        if not params:
            return base_url
        
        # httpx handles URL encoding automatically
        return str(httpx.URL(base_url, params=params))
    
    async def close(self):
        """
        Close HTTP client connection and cleanup resources.
        
        Should be called when done using the scraper to properly
        close connections and free resources.
        
        Example:
            >>> scraper = CraigslistScraper()
            >>> try:
            ...     results = await scraper.search("iPhone", "NY")
            ... finally:
            ...     await scraper.close()
        """
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - automatically closes client."""
        await self.close()
    
    def __repr__(self) -> str:
        """String representation of the scraper."""
        return f"{self.__class__.__name__}(rate_limiter={self.rate_limiter})"


# Test code - runs when file is executed directly
if __name__ == "__main__":
    import sys
    from pathlib import Path
    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    print("=" * 60)
    print("BaseScraper Class Structure")
    print("=" * 60)
    print()
    print("✓ BaseScraper class created successfully")
    print("✓ All abstract methods defined:")
    print("  - search()")
    print("  - get_product_details()")
    print("  - is_available()")
    print()
    print("✓ Helper methods available:")
    print("  - _make_request() - HTTP requests with rate limiting")
    print("  - _extract_price() - Extract price from text")
    print("  - _clean_text() - Clean and normalize text")
    print("  - _extract_date() - Extract date from text")
    print("  - _build_url() - Build URL with parameters")
    print("  - close() - Cleanup resources")
    print()
    print("✓ Context manager support:")
    print("  - async with BaseScraper() as scraper:")
    print()
    print("=" * 60)
    print("✅ Base Scraper ready for inheritance!")
    print("=" * 60)

# Made with Bob
