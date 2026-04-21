# Extensible Scraper Architecture & Kijiji Integration

## Overview
This document outlines the extensible scraper architecture that makes it easy to add new marketplace platforms, and provides a complete implementation guide for adding Kijiji.ca support.

---

## 🎯 Architecture Goals

1. **Easy to Add New Scrapers**: Plug-and-play architecture
2. **No Authentication Required**: Focus on public marketplaces
3. **Consistent Interface**: All scrapers follow the same pattern
4. **Automatic Registration**: New scrapers are automatically discovered
5. **Graceful Degradation**: System continues if one scraper fails

---

## 📐 Base Scraper Architecture

### 1. Base Scraper Interface

**File:** `backend/app/scrapers/base.py`

```python
"""
Base scraper interface that all marketplace scrapers must implement.
This ensures consistency and makes it easy to add new platforms.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

class BaseScraper(ABC):
    """
    Abstract base class for all marketplace scrapers.
    
    All scrapers must implement:
    - search(): Search for products
    - get_product_details(): Get detailed product information
    - is_available(): Check if scraper is operational
    
    Optional methods:
    - validate_location(): Validate location format
    - get_categories(): Get available categories
    """
    
    # Platform identifier (must be unique)
    PLATFORM_NAME: str = "unknown"
    
    # Whether this scraper requires authentication
    REQUIRES_AUTH: bool = False
    
    # Rate limit (requests per minute)
    RATE_LIMIT: int = 10
    
    def __init__(self):
        self.logger = logging.getLogger(f"scraper.{self.PLATFORM_NAME}")
        self._setup()
    
    def _setup(self):
        """Setup scraper (override if needed)"""
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        max_price: float,
        location: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search for products matching criteria.
        
        Args:
            query: Search query (e.g., "iPhone 13")
            max_price: Maximum price
            location: Location string (format varies by platform)
            **kwargs: Additional platform-specific parameters
            
        Returns:
            List of product dictionaries with standardized fields:
            {
                'title': str,
                'description': str,
                'price': float,
                'url': str,
                'image_url': str (optional),
                'location': str (optional),
                'posted_date': datetime (optional),
                'platform': str
            }
        """
        pass
    
    @abstractmethod
    async def get_product_details(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific product.
        
        Args:
            url: Product URL
            
        Returns:
            Product dictionary with detailed information
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the scraper is currently operational.
        
        Returns:
            True if scraper can be used, False otherwise
        """
        pass
    
    def validate_location(self, location: str) -> bool:
        """
        Validate location format (override if needed).
        
        Args:
            location: Location string
            
        Returns:
            True if valid, False otherwise
        """
        return True
    
    def get_categories(self) -> List[str]:
        """
        Get available categories (override if needed).
        
        Returns:
            List of category names
        """
        return ["general"]
    
    def normalize_price(self, price_str: str) -> float:
        """
        Normalize price string to float.
        
        Args:
            price_str: Price string (e.g., "$1,234.56", "1234.56 CAD")
            
        Returns:
            Price as float
        """
        import re
        # Remove currency symbols and commas
        cleaned = re.sub(r'[^\d.]', '', price_str)
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(platform={self.PLATFORM_NAME})>"
```

---

## 🔌 Scraper Registry (Auto-Discovery)

**File:** `backend/app/scrapers/registry.py`

```python
"""
Scraper registry for automatic discovery and management of all scrapers.
"""

from typing import Dict, List, Type
import importlib
import pkgutil
from .base import BaseScraper
import logging

logger = logging.getLogger(__name__)

class ScraperRegistry:
    """
    Registry for managing all available scrapers.
    Automatically discovers and registers scrapers.
    """
    
    def __init__(self):
        self._scrapers: Dict[str, Type[BaseScraper]] = {}
        self._instances: Dict[str, BaseScraper] = {}
    
    def register(self, scraper_class: Type[BaseScraper]):
        """
        Register a scraper class.
        
        Args:
            scraper_class: Scraper class (must inherit from BaseScraper)
        """
        if not issubclass(scraper_class, BaseScraper):
            raise ValueError(f"{scraper_class} must inherit from BaseScraper")
        
        platform_name = scraper_class.PLATFORM_NAME
        if platform_name == "unknown":
            logger.warning(f"Scraper {scraper_class.__name__} has no PLATFORM_NAME")
            return
        
        self._scrapers[platform_name] = scraper_class
        logger.info(f"Registered scraper: {platform_name}")
    
    def get_scraper(self, platform_name: str) -> BaseScraper:
        """
        Get scraper instance by platform name.
        
        Args:
            platform_name: Platform identifier
            
        Returns:
            Scraper instance
        """
        if platform_name not in self._instances:
            if platform_name not in self._scrapers:
                raise ValueError(f"Unknown platform: {platform_name}")
            
            scraper_class = self._scrapers[platform_name]
            self._instances[platform_name] = scraper_class()
        
        return self._instances[platform_name]
    
    def get_all_scrapers(self) -> List[BaseScraper]:
        """
        Get all registered scraper instances.
        
        Returns:
            List of scraper instances
        """
        return [self.get_scraper(name) for name in self._scrapers.keys()]
    
    def get_available_scrapers(self) -> List[BaseScraper]:
        """
        Get only operational scrapers.
        
        Returns:
            List of available scraper instances
        """
        return [s for s in self.get_all_scrapers() if s.is_available()]
    
    def list_platforms(self) -> List[str]:
        """
        List all registered platform names.
        
        Returns:
            List of platform names
        """
        return list(self._scrapers.keys())
    
    def auto_discover(self):
        """
        Automatically discover and register all scrapers in the scrapers package.
        """
        import app.scrapers as scrapers_package
        
        # Get the package path
        package_path = scrapers_package.__path__
        
        # Iterate through all modules in the package
        for importer, modname, ispkg in pkgutil.iter_modules(package_path):
            if modname in ['base', 'registry', '__init__', 'utils']:
                continue
            
            try:
                # Import the module
                module = importlib.import_module(f'app.scrapers.{modname}')
                
                # Find all classes that inherit from BaseScraper
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseScraper) and 
                        attr is not BaseScraper):
                        self.register(attr)
            
            except Exception as e:
                logger.error(f"Failed to load scraper module {modname}: {e}")

# Global registry instance
registry = ScraperRegistry()

def get_registry() -> ScraperRegistry:
    """Get the global scraper registry."""
    return registry
```

---

## 🍁 Kijiji.ca Scraper Implementation

### Research Summary

**Kijiji.ca** is a Canadian classified ads platform (owned by eBay):
- ✅ **No authentication required** for browsing
- ✅ **Public search available**
- ✅ **Similar structure to Craigslist**
- ✅ **Location-based search** (by province/city)
- ✅ **Category support**

**URL Structure:**
```
https://www.kijiji.ca/b-{category}/{location}/{query}/k0c{category_id}l{location_id}
```

### Implementation

**File:** `backend/app/scrapers/kijiji.py`

```python
"""
Kijiji.ca scraper implementation.

Kijiji is a Canadian classified ads platform (owned by eBay).
No authentication required for public listings.

URL Structure:
https://www.kijiji.ca/b-{category}/{location}/{query}/k0c{category_id}l{location_id}

Example:
https://www.kijiji.ca/b-cars-vehicles/city-of-toronto/toyota-camry/k0c27l1700273
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
from datetime import datetime
import re
from urllib.parse import urljoin, quote_plus

from .base import BaseScraper
from ..utils.rate_limiter import RateLimiter

class KijijiScraper(BaseScraper):
    """
    Kijiji.ca scraper for Canadian classified ads.
    
    Supports:
    - Location-based search (provinces and cities)
    - Category filtering
    - Price range filtering
    - No authentication required
    """
    
    PLATFORM_NAME = "kijiji"
    REQUIRES_AUTH = False
    RATE_LIMIT = 10  # requests per minute
    
    BASE_URL = "https://www.kijiji.ca"
    SEARCH_PATH = "/b-{category}/{location}/{query}/k0c{category_id}l{location_id}"
    
    # Major Canadian cities with their location IDs
    LOCATIONS = {
        # Ontario
        "toronto": {"id": "1700273", "name": "City of Toronto"},
        "ottawa": {"id": "1700185", "name": "Ottawa"},
        "hamilton": {"id": "1700072", "name": "Hamilton"},
        "london": {"id": "1700214", "name": "London"},
        "kitchener": {"id": "1700212", "name": "Kitchener / Waterloo"},
        
        # Quebec
        "montreal": {"id": "1700281", "name": "City of Montreal"},
        "quebec-city": {"id": "1700124", "name": "Ville de Québec"},
        
        # British Columbia
        "vancouver": {"id": "1700287", "name": "Vancouver"},
        "victoria": {"id": "1700173", "name": "Victoria"},
        
        # Alberta
        "calgary": {"id": "1700199", "name": "Calgary"},
        "edmonton": {"id": "1700203", "name": "Edmonton"},
        
        # Manitoba
        "winnipeg": {"id": "1700192", "name": "Winnipeg"},
        
        # Saskatchewan
        "saskatoon": {"id": "1700197", "name": "Saskatoon"},
        "regina": {"id": "1700196", "name": "Regina"},
        
        # Nova Scotia
        "halifax": {"id": "1700321", "name": "Halifax"},
        
        # Default (all of Canada)
        "canada": {"id": "0", "name": "Canada"}
    }
    
    # Category mappings
    CATEGORIES = {
        "cars": {"id": "27", "slug": "cars-vehicles"},
        "electronics": {"id": "132", "slug": "electronics"},
        "furniture": {"id": "235", "slug": "furniture"},
        "appliances": {"id": "107", "slug": "appliances"},
        "phones": {"id": "132", "slug": "cell-phones"},
        "computers": {"id": "16", "slug": "computers"},
        "general": {"id": "0", "slug": "search"}
    }
    
    def _setup(self):
        """Setup HTTP client and rate limiter."""
        self.rate_limiter = RateLimiter(requests_per_minute=self.RATE_LIMIT)
        self.client = httpx.AsyncClient(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-CA,en-US;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            },
            timeout=30.0,
            follow_redirects=True
        )
    
    async def search(
        self,
        query: str,
        max_price: float,
        location: Optional[str] = None,
        category: str = "general",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search Kijiji for products matching criteria.
        
        Args:
            query: Search query (e.g., "iPhone 13")
            max_price: Maximum price in CAD
            location: City name (e.g., "toronto", "montreal")
            category: Product category
            **kwargs: Additional parameters
            
        Returns:
            List of product dictionaries
        """
        await self.rate_limiter.wait()
        
        # Normalize location
        location_key = (location or "canada").lower().replace(" ", "-")
        if location_key not in self.LOCATIONS:
            self.logger.warning(f"Unknown location: {location}, using 'canada'")
            location_key = "canada"
        
        location_data = self.LOCATIONS[location_key]
        
        # Get category info
        category_info = self.CATEGORIES.get(category, self.CATEGORIES["general"])
        
        # Build search URL
        search_url = self._build_search_url(
            query=query,
            location_slug=location_data["name"].lower().replace(" ", "-"),
            location_id=location_data["id"],
            category_slug=category_info["slug"],
            category_id=category_info["id"],
            max_price=max_price
        )
        
        try:
            self.logger.info(f"Searching Kijiji: {search_url}")
            response = await self.client.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            products = []
            
            # Parse search results
            # Kijiji uses different selectors than Craigslist
            listings = soup.select("div.search-item")
            
            for listing in listings:
                try:
                    product = self._parse_listing(listing)
                    if product and product["price"] <= max_price:
                        products.append(product)
                except Exception as e:
                    self.logger.warning(f"Failed to parse listing: {e}")
                    continue
            
            self.logger.info(f"Found {len(products)} products on Kijiji")
            return products
            
        except httpx.HTTPError as e:
            self.logger.error(f"Kijiji search failed: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error in Kijiji search: {e}")
            return []
    
    def _build_search_url(
        self,
        query: str,
        location_slug: str,
        location_id: str,
        category_slug: str,
        category_id: str,
        max_price: float
    ) -> str:
        """Build Kijiji search URL."""
        # Encode query
        encoded_query = quote_plus(query)
        
        # Build base URL
        if category_id == "0":
            # General search
            url = f"{self.BASE_URL}/b-{location_slug}/{encoded_query}/k0l{location_id}"
        else:
            # Category search
            url = f"{self.BASE_URL}/b-{category_slug}/{location_slug}/{encoded_query}/k0c{category_id}l{location_id}"
        
        # Add price filter
        url += f"?price-type=FIXED__max:{int(max_price)}"
        
        return url
    
    def _parse_listing(self, listing: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """
        Parse a single Kijiji listing.
        
        Args:
            listing: BeautifulSoup element for the listing
            
        Returns:
            Product dictionary or None
        """
        try:
            # Extract title and URL
            title_elem = listing.select_one("a.title")
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            url = urljoin(self.BASE_URL, title_elem.get("href", ""))
            
            # Extract price
            price_elem = listing.select_one("div.price")
            if not price_elem:
                return None
            
            price_text = price_elem.get_text(strip=True)
            price = self.normalize_price(price_text)
            
            if price == 0:
                # Skip "Please Contact" or free items
                return None
            
            # Extract description
            description_elem = listing.select_one("div.description")
            description = description_elem.get_text(strip=True) if description_elem else ""
            
            # Extract image
            image_elem = listing.select_one("img.image")
            image_url = image_elem.get("src", "") if image_elem else None
            
            # Extract location
            location_elem = listing.select_one("div.location span")
            location = location_elem.get_text(strip=True) if location_elem else None
            
            # Extract posted date
            date_elem = listing.select_one("span.date-posted")
            posted_date = self._parse_date(date_elem.get_text(strip=True)) if date_elem else None
            
            return {
                "title": title,
                "description": description,
                "price": price,
                "url": url,
                "image_url": image_url,
                "location": location,
                "posted_date": posted_date,
                "platform": self.PLATFORM_NAME
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing listing: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse Kijiji date string.
        
        Examples:
        - "< 2 hours ago"
        - "Yesterday"
        - "2 days ago"
        - "12/25/2023"
        """
        from datetime import timedelta
        
        date_str = date_str.lower().strip()
        now = datetime.now()
        
        try:
            if "hour" in date_str or "minute" in date_str:
                # Recent posting
                return now
            elif "yesterday" in date_str:
                return now - timedelta(days=1)
            elif "day" in date_str:
                # Extract number of days
                match = re.search(r'(\d+)\s*day', date_str)
                if match:
                    days = int(match.group(1))
                    return now - timedelta(days=days)
            else:
                # Try to parse as date
                return datetime.strptime(date_str, "%m/%d/%Y")
        except:
            return None
    
    async def get_product_details(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific product.
        
        Args:
            url: Product URL
            
        Returns:
            Product dictionary with detailed information
        """
        await self.rate_limiter.wait()
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract detailed information
            title_elem = soup.select_one("h1.title-2323565163")
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            price_elem = soup.select_one("span.currentPrice-2872355490")
            price_text = price_elem.get_text(strip=True) if price_elem else "0"
            price = self.normalize_price(price_text)
            
            description_elem = soup.select_one("div.descriptionContainer-3261352004")
            description = description_elem.get_text(strip=True) if description_elem else ""
            
            # Extract images
            image_elems = soup.select("img.heroImageBackground-1048496645")
            image_url = image_elems[0].get("src") if image_elems else None
            
            # Extract location
            location_elem = soup.select_one("span.address-3617944557")
            location = location_elem.get_text(strip=True) if location_elem else None
            
            # Extract posted date
            date_elem = soup.select_one("time")
            posted_date = self._parse_date(date_elem.get_text(strip=True)) if date_elem else None
            
            return {
                "title": title,
                "description": description,
                "price": price,
                "url": url,
                "image_url": image_url,
                "location": location,
                "posted_date": posted_date,
                "platform": self.PLATFORM_NAME
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get Kijiji product details: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        Check if Kijiji scraper is operational.
        
        Returns:
            True if available
        """
        # Could add a health check here
        return True
    
    def validate_location(self, location: str) -> bool:
        """
        Validate location format.
        
        Args:
            location: Location string
            
        Returns:
            True if valid
        """
        location_key = location.lower().replace(" ", "-")
        return location_key in self.LOCATIONS
    
    def get_categories(self) -> List[str]:
        """
        Get available categories.
        
        Returns:
            List of category names
        """
        return list(self.CATEGORIES.keys())
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
```

---

## 🔧 Updated Orchestrator Integration

**File:** `backend/app/core/orchestrator.py` (Update)

```python
"""
Search orchestrator that coordinates all scrapers.
Automatically uses all registered scrapers.
"""

from typing import List, Dict, Any
import asyncio
from app.scrapers.registry import get_registry
from app.models import SearchRequest, Product
import logging

logger = logging.getLogger(__name__)

class SearchOrchestrator:
    """
    Orchestrates search operations across all registered scrapers.
    """
    
    def __init__(self):
        self.registry = get_registry()
        # Auto-discover all scrapers
        self.registry.auto_discover()
        logger.info(f"Loaded scrapers: {self.registry.list_platforms()}")
    
    async def execute_search(
        self,
        search_request: SearchRequest
    ) -> List[Product]:
        """
        Execute search across all available scrapers.
        
        Args:
            search_request: Search request with criteria
            
        Returns:
            List of products found across all platforms
        """
        # Get all available scrapers
        scrapers = self.registry.get_available_scrapers()
        
        logger.info(f"Executing search across {len(scrapers)} platforms")
        
        # Run searches concurrently
        tasks = [
            self._search_platform(scraper, search_request)
            for scraper in scrapers
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results and filter out errors
        all_products = []
        for result in results:
            if isinstance(result, list):
                all_products.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraper failed: {result}")
        
        logger.info(f"Found {len(all_products)} total products")
        return all_products
    
    async def _search_platform(
        self,
        scraper,
        search_request: SearchRequest
    ) -> List[Product]:
        """
        Search a single platform.
        
        Args:
            scraper: Scraper instance
            search_request: Search criteria
            
        Returns:
            List of products from this platform
        """
        try:
            logger.info(f"Searching {scraper.PLATFORM_NAME}...")
            
            products_data = await scraper.search(
                query=search_request.product_name,
                max_price=search_request.budget,
                location=search_request.location
            )
            
            # Convert to Product models
            products = [
                Product(**data, search_request_id=search_request.id)
                for data in products_data
            ]
            
            logger.info(f"Found {len(products)} products on {scraper.PLATFORM_NAME}")
            return products
            
        except Exception as e:
            logger.error(f"Error searching {scraper.PLATFORM_NAME}: {e}")
            return []
```

---

## 📝 Adding a New Scraper - Quick Guide

### Step 1: Create Scraper File

Create `backend/app/scrapers/your_platform.py`:

```python
from .base import BaseScraper

class YourPlatformScraper(BaseScraper):
    PLATFORM_NAME = "your_platform"
    REQUIRES_AUTH = False
    RATE_LIMIT = 10
    
    async def search(self, query, max_price, location=None, **kwargs):
        # Implement search logic
        return []
    
    async def get_product_details(self, url):
        # Implement details fetching
        return None
    
    def is_available(self):
        return True
```

### Step 2: That's It!

The scraper will be automatically discovered and registered when the application starts. No configuration needed!

---

## 🧪 Testing New Scrapers

**File:** `backend/app/scrapers/test_kijiji.py`

```python
"""
Test script for Kijiji scraper.
"""

import asyncio
from app.scrapers.kijiji import KijijiScraper

async def test_kijiji():
    """Test Kijiji scraper functionality."""
    scraper = KijijiScraper()
    
    print("Testing Kijiji scraper...")
    print(f"Platform: {scraper.PLATFORM_NAME}")
    print(f"Available: {scraper.is_available()}")
    print(f"Categories: {scraper.get_categories()}")
    
    # Test search
    print("\nSearching for 'iPhone 13' in Toronto...")
    products = await scraper.search(
        query="iPhone 13",
        max_price=800.0,
        location="toronto"
    )
    
    print(f"Found {len(products)} products")
    
    # Display first few results
    for i, product in enumerate(products[:3], 1):
        print(f"\n{i}. {product['title']}")
        print(f"   Price: ${product['price']:.2f}")
        print(f"   Location: {product.get('location', 'N/A')}")
        print(f"   URL: {product['url']}")
    
    await scraper.close()

if __name__ == "__main__":
    asyncio.run(test_kijiji())
```

---

## 📊 Benefits of This Architecture

### 1. **Zero Configuration**
- Drop a new scraper file in the `scrapers/` directory
- It's automatically discovered and used
- No need to update configuration files

### 2. **Consistent Interface**
- All scrapers follow the same pattern
- Easy to understand and maintain
- Predictable behavior

### 3. **Graceful Degradation**
- If one scraper fails, others continue
- System remains operational
- Errors are logged but don't crash the app

### 4. **Easy Testing**
- Each scraper can be tested independently
- Mock scrapers for unit tests
- Integration tests work automatically

### 5. **Extensibility**
- Add new scrapers without touching existing code
- Support for platform-specific features via kwargs
- Easy to add authentication if needed later

---

## 🌍 Supported Platforms

After adding Kijiji, the system will support:

1. **Craigslist** (US) - No auth required
2. **Facebook Marketplace** (Global) - No auth required (with Selenium)
3. **eBay** (Global) - No auth required
4. **Kijiji** (Canada) - No auth required ✨ NEW
5. **Generic Scraper** - For any other site

---

## 🚀 Next Steps

1. **Implement Kijiji scraper** using the code above
2. **Test thoroughly** with different queries and locations
3. **Update documentation** to mention Kijiji support
4. **Consider adding more Canadian platforms**:
   - Facebook Marketplace Canada
   - Autotrader.ca (cars)
   - Realtor.ca (real estate)

---

## 📚 Resources

- [Kijiji.ca](https://www.kijiji.ca)
- [Web Scraping Best Practices](https://www.scrapehero.com/web-scraping-best-practices/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

---

**The architecture is now fully extensible and Kijiji-ready! 🎉**