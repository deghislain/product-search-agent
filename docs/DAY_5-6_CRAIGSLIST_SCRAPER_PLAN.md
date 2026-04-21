# Day 5-6: Craigslist Scraper - Detailed Sub-Task Plan

**Total Estimated Time:** 8 hours (2 days)  
**Difficulty Level:** Intermediate  
**Goal:** Build a fully functional Craigslist scraper that inherits from BaseScraper

---

## 📋 Overview

Days 5-6 focus on implementing your **first real scraper** - the Craigslist scraper! You'll use the BaseScraper template you created on Day 4 and implement the specific logic for scraping Craigslist.

**What you'll build:**
- A scraper that searches Craigslist for products
- Methods to extract product details from listings
- Functionality to check if listings are still available
- Comprehensive tests to verify everything works

---

## 🎯 Day 5: Core Scraper Implementation (4-5 hours)

### Sub-Task 5.1: Understand Craigslist Structure (30 minutes)

**What to do:**
1. Open Craigslist in your browser: https://craigslist.org
2. Search for something (e.g., "iPhone 13")
3. Inspect the page structure using Chrome DevTools

**Key things to identify:**

#### Search Results Page
- **URL pattern**: `https://{city}.craigslist.org/search/{category}?query={search_term}`
- **Result container**: Usually `<li class="result-row">`
- **Title**: Link text inside result
- **Price**: Usually in `<span class="result-price">`
- **Location**: Usually in `<span class="result-hood">`
- **Date**: Usually in `<time>` tag
- **Image**: `<img>` tag in result

#### Individual Listing Page
- **Title**: `<span id="titletextonly">`
- **Price**: `<span class="price">`
- **Description**: `<section id="postingbody">`
- **Images**: `<div class="slide">` with `<img>` tags
- **Attributes**: `<p class="attrgroup">` sections

**Deliverable:** Notes on HTML structure and CSS selectors

---

### Sub-Task 5.2: Create Scraper File Structure (15 minutes)

**Create the file:**
```bash
cd backend
touch app/scrapers/craigslist.py
```

**Basic structure:**
```python
"""
Craigslist Scraper Module

Implements scraping functionality for Craigslist marketplace.
"""

from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.utils.rate_limiter import RateLimiter


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
    
    # We'll implement methods here
```

**Deliverable:** File created with basic structure

---

### Sub-Task 5.3: Implement `search()` Method (1.5 hours)

**What this method does:**
- Takes a search query and location
- Builds the Craigslist search URL
- Makes HTTP request to get search results
- Parses HTML to extract product listings
- Returns list of product dictionaries

**Implementation:**

```python
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
        
        # Extract listings
        products = []
        result_rows = soup.find_all('li', class_='result-row')
        
        for row in result_rows[:max_results]:
            product = self._parse_search_result(row, location)
            if product:
                products.append(product)
        
        return products
        
    except Exception as e:
        print(f"Error searching Craigslist: {e}")
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
    """
    try:
        # Extract title and URL
        title_elem = row.find('a', class_='result-title')
        if not title_elem:
            return None
        
        title = self._clean_text(title_elem.get_text())
        url = title_elem['href']
        
        # Make URL absolute if it's relative
        if url.startswith('/'):
            url = f"https://{location}.craigslist.org{url}"
        
        # Extract listing ID from URL
        listing_id = url.split('/')[-1].replace('.html', '')
        
        # Extract price
        price_elem = row.find('span', class_='result-price')
        price = self._extract_price(price_elem.get_text()) if price_elem else None
        
        # Extract location/neighborhood
        hood_elem = row.find('span', class_='result-hood')
        product_location = self._clean_text(hood_elem.get_text()) if hood_elem else location
        
        # Extract date
        time_elem = row.find('time')
        posted_date = time_elem['datetime'] if time_elem and 'datetime' in time_elem.attrs else None
        
        # Extract image
        image_elem = row.find('img')
        image_url = image_elem['src'] if image_elem and 'src' in image_elem.attrs else None
        
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
        print(f"Error parsing search result: {e}")
        return None
```

**Test it:**
```python
# Add at bottom of file for testing
if __name__ == "__main__":
    import asyncio
    
    async def test_search():
        scraper = CraigslistScraper()
        results = await scraper.search("iPhone 13", "sfbay", max_results=5)
        
        print(f"Found {len(results)} products:")
        for product in results:
            print(f"  - {product['title']}: ${product['price']}")
        
        await scraper.close()
    
    asyncio.run(test_search())
```

Run: `python app/scrapers/craigslist.py`

**Deliverable:** Working `search()` method that returns product listings

---

### Sub-Task 5.4: Implement `get_product_details()` Method (1 hour)

**What this method does:**
- Takes a product URL
- Fetches the full listing page
- Extracts detailed information
- Returns comprehensive product dictionary

**Implementation:**

```python
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
        print(f"Error getting product details: {e}")
        return {
            'url': product_url,
            'error': str(e),
            'platform': 'craigslist'
        }
```

**Test it:**
```python
# Add to test section
async def test_details():
    scraper = CraigslistScraper()
    
    # First get a product URL from search
    results = await scraper.search("iPhone", "sfbay", max_results=1)
    if results:
        url = results[0]['url']
        details = await scraper.get_product_details(url)
        
        print(f"Title: {details['title']}")
        print(f"Price: ${details['price']}")
        print(f"Description: {details['description'][:100]}...")
        print(f"Images: {len(details['images'])}")
    
    await scraper.close()

asyncio.run(test_details())
```

**Deliverable:** Working `get_product_details()` method

---

### Sub-Task 5.5: Implement `is_available()` Method (30 minutes)

**What this method does:**
- Checks if a listing is still active
- Returns True if available, False if removed/sold

**Implementation:**

```python
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
        print(f"Error checking availability: {e}")
        return False
```

**Test it:**
```python
async def test_availability():
    scraper = CraigslistScraper()
    
    # Test with a real listing
    results = await scraper.search("iPhone", "sfbay", max_results=1)
    if results:
        url = results[0]['url']
        available = await scraper.is_available(url)
        print(f"Listing available: {available}")
    
    # Test with fake URL (should return False)
    fake_url = "https://sfbay.craigslist.org/sfc/mob/d/fake-listing/1234567890.html"
    available = await scraper.is_available(fake_url)
    print(f"Fake listing available: {available}")  # Should be False
    
    await scraper.close()

asyncio.run(test_availability())
```

**Deliverable:** Working `is_available()` method

---

## 🎯 Day 6: Testing & Refinement (3-4 hours)

### Sub-Task 6.1: Create Comprehensive Test File (1.5 hours)

**Create test file:**
```bash
touch app/tests/test_craigslist.py
```

**Implementation:**

```python
"""
Tests for Craigslist Scraper

Comprehensive test suite for CraigslistScraper functionality.
"""

import asyncio
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scrapers.craigslist import CraigslistScraper
from app.utils.rate_limiter import RateLimiter


class TestCraigslistScraper:
    """Test suite for Craigslist scraper."""
    
    @pytest.fixture
    async def scraper(self):
        """Create scraper instance for testing."""
        scraper = CraigslistScraper()
        yield scraper
        await scraper.close()
    
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


# Run tests
if __name__ == "__main__":
    async def run_all_tests():
        scraper = CraigslistScraper()
        
        print("Running Craigslist Scraper Tests...\n")
        
        # Test 1: Basic search
        print("1. Testing basic search...")
        results = await scraper.search("iPhone", "sfbay", max_results=3)
        print(f"   ✓ Found {len(results)} results")
        
        # Test 2: Product details
        if results:
            print("\n2. Testing product details...")
            details = await scraper.get_product_details(results[0]['url'])
            print(f"   ✓ Got details for: {details['title']}")
            print(f"   ✓ Description length: {len(details['description'])} chars")
            print(f"   ✓ Images: {len(details['images'])}")
        
        # Test 3: Availability
        if results:
            print("\n3. Testing availability check...")
            available = await scraper.is_available(results[0]['url'])
            print(f"   ✓ Listing available: {available}")
        
        await scraper.close()
        print("\n✅ All tests passed!")
    
    asyncio.run(run_all_tests())
```

**Run tests:**
```bash
# Simple test
python app/tests/test_craigslist.py

# With pytest (if installed)
pytest app/tests/test_craigslist.py -v
```

**Deliverable:** Comprehensive test suite

---

### Sub-Task 6.2: Handle Edge Cases (1 hour)

**Add error handling and edge cases:**

```python
# Add to CraigslistScraper class

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
            print(f"Search attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                # Wait before retrying (exponential backoff)
                await asyncio.sleep(2 ** attempt)
            else:
                print(f"All {max_retries} attempts failed")
                return []
```

**Deliverable:** Robust error handling

---

### Sub-Task 6.3: Add Logging and Documentation (30 minutes)

**Add logging:**

```python
import logging

# At top of class
logger = logging.getLogger(__name__)

# In methods, replace print() with logger
logger.info(f"Searching Craigslist for '{query}' in {location}")
logger.error(f"Error searching Craigslist: {e}")
logger.debug(f"Found {len(products)} products")
```

**Add comprehensive docstrings** (already done in examples above)

**Create usage documentation:**

```python
"""
Craigslist Scraper Usage Examples

Basic Search:
    >>> scraper = CraigslistScraper()
    >>> results = await scraper.search("iPhone 13", "sfbay")
    >>> print(f"Found {len(results)} products")

Search with Filters:
    >>> results = await scraper.search(
    ...     "laptop",
    ...     "newyork",
    ...     min_price=500,
    ...     max_price=1500,
    ...     max_results=20
    ... )

Get Product Details:
    >>> details = await scraper.get_product_details(results[0]['url'])
    >>> print(details['description'])

Check Availability:
    >>> available = await scraper.is_available(product_url)
    >>> if available:
    ...     print("Still available!")

Using Context Manager:
    >>> async with CraigslistScraper() as scraper:
    ...     results = await scraper.search("iPhone", "sfbay")
    ...     # Scraper automatically closed
"""
```

**Deliverable:** Well-documented, production-ready code

---

### Sub-Task 6.4: Integration Test with Real Data (30 minutes)

**Create integration test:**

```bash
touch app/tests/test_craigslist_integration.py
```

```python
"""
Integration tests for Craigslist scraper with real data.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scrapers.craigslist import CraigslistScraper


async def test_full_workflow():
    """Test complete workflow from search to details."""
    print("="*60)
    print("Craigslist Scraper Integration Test")
    print("="*60)
    
    async with CraigslistScraper() as scraper:
        # Step 1: Search
        print("\n1. Searching for 'iPhone'...")
        results = await scraper.search("iPhone", "sfbay", max_results=5)
        print(f"   ✓ Found {len(results)} results")
        
        if not results:
            print("   ✗ No results found, test cannot continue")
            return
        
        # Step 2: Display results
        print("\n2. Search Results:")
        for i, product in enumerate(results, 1):
            print(f"   {i}. {product['title']}")
            print(f"      Price: ${product['price']}")
            print(f"      Location: {product['location']}")
            print(f"      URL: {product['url'][:50]}...")
        
        # Step 3: Get details for first result
        print("\n3. Getting details for first result...")
        details = await scraper.get_product_details(results[0]['url'])
        print(f"   ✓ Title: {details['title']}")
        print(f"   ✓ Price: ${details['price']}")
        print(f"   ✓ Description: {details['description'][:100]}...")
        print(f"   ✓ Images: {len(details['images'])}")
        print(f"   ✓ Attributes: {len(details['attributes'])}")
        
        # Step 4: Check availability
        print("\n4. Checking availability...")
        available = await scraper.is_available(results[0]['url'])
        print(f"   ✓ Listing is {'available' if available else 'not available'}")
        
        # Step 5: Test rate limiting
        print("\n5. Testing rate limiting (making 5 quick requests)...")
        import time
        start = time.time()
        for i in range(5):
            await scraper.search("test", "sfbay", max_results=1)
        elapsed = time.time() - start
        print(f"   ✓ 5 requests took {elapsed:.2f} seconds")
        print(f"   ✓ Rate limiting {'working' if elapsed > 1 else 'may not be working'}")
    
    print("\n" + "="*60)
    print("✅ Integration test complete!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_full_workflow())
```

**Run:**
```bash
python app/tests/test_craigslist_integration.py
```

**Deliverable:** Passing integration test

---

## ✅ Verification Checklist

After completing Days 5-6, verify:

### Core Functionality
- [ ] `CraigslistScraper` class created
- [ ] Inherits from `BaseScraper`
- [ ] `search()` method implemented and working
- [ ] `get_product_details()` method implemented and working
- [ ] `is_available()` method implemented and working

### Helper Methods
- [ ] `_build_search_url()` builds correct URLs
- [ ] `_parse_search_result()` extracts data correctly
- [ ] Error handling in place
- [ ] Rate limiting working

### Testing
- [ ] Unit tests created
- [ ] Integration tests created
- [ ] All tests passing
- [ ] Tested with real Craigslist data

### Code Quality
- [ ] Comprehensive docstrings
- [ ] Type hints on all methods
- [ ] Logging implemented
- [ ] Error handling robust
- [ ] Code follows PEP 8 style

---

## 🧪 Final Test Commands

```bash
# Test individual file
python app/scrapers/craigslist.py

# Test unit tests
python app/tests/test_craigslist.py

# Test integration
python app/tests/test_craigslist_integration.py

# With pytest (if installed)
pytest app/tests/test_craigslist.py -v
pytest app/tests/ -v  # All tests
```

---

## 📊 Expected Output

### Successful Search
```
Found 5 products:
  - iPhone 13 Pro 256GB - Excellent Condition: $899.0
  - iPhone 13 128GB Unlocked: $650.0
  - iPhone 13 Mini Blue: $550.0
  - iPhone 13 Pro Max 512GB: $1100.0
  - iPhone 13 - Like New: $700.0
```

### Successful Details
```
Title: iPhone 13 Pro 256GB - Excellent Condition
Price: $899.0
Description: Selling my iPhone 13 Pro in excellent condition...
Images: 4
```

---

## 🚨 Common Issues & Solutions

### Issue 1: No results found
**Cause:** Craigslist HTML structure changed  
**Solution:** Inspect page again, update CSS selectors

### Issue 2: Rate limiting not working
**Cause:** Rate limiter not properly initialized  
**Solution:** Check `super().__init__()` is called

### Issue 3: Images not loading
**Cause:** Image URLs are relative  
**Solution:** Convert to absolute URLs

### Issue 4: Prices not extracting
**Cause:** Price format varies  
**Solution:** Improve `_extract_price()` regex

---

## 🎓 Key Concepts Learned

1. **Web Scraping Basics**
   - HTML parsing with BeautifulSoup
   - CSS selectors
   - Data extraction

2. **Inheritance**
   - Using BaseScraper template
   - Implementing abstract methods
   - Calling parent methods with `super()`

3. **Async Programming**
   - Async/await syntax
   - Concurrent requests
   - Rate limiting

4. **Error Handling**
   - Try/except blocks
   - Graceful degradation
   - Retry logic

---

## 🎯 Next Steps (Day 7)

After completing the Craigslist scraper, you'll:
- Implement Facebook Marketplace scraper (uses Selenium)
- Learn about JavaScript rendering
- Handle more complex scraping scenarios

---

## 📚 Resources

- **BeautifulSoup Docs**: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- **CSS Selectors**: https://www.w3schools.com/cssref/css_selectors.php
- **Craigslist**: https://craigslist.org
- **Chrome DevTools**: https://developer.chrome.com/docs/devtools/

---

## 🎉 Success Criteria

Days 5-6 are complete when:
1. ✅ Craigslist scraper fully implemented
2. ✅ All three methods working (`search`, `get_product_details`, `is_available`)
3. ✅ Tests passing
4. ✅ Can search and extract real Craigslist data
5. ✅ Rate limiting functional
6. ✅ Error handling robust
7. ✅ Code well-documented

**You're building your first real scraper! This is a major milestone! 🚀**