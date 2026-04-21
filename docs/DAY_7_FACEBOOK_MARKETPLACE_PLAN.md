# Day 7: Facebook Marketplace Scraper - Detailed Sub-Plan

**Estimated Time:** 6 hours  
**Difficulty:** Intermediate (requires understanding of Selenium and browser automation)

---

## 📋 Overview

Facebook Marketplace requires JavaScript to load content, so we can't use simple HTTP requests like we did with Craigslist. Instead, we'll use **Selenium**, which controls a real web browser to scrape the page.

**Why Selenium?**
- Facebook loads content dynamically with JavaScript
- Simple HTTP requests only get the initial HTML (no product listings)
- Selenium simulates a real user browsing the site

---

## 🎯 Learning Objectives

By the end of this task, you will understand:
1. How to use Selenium WebDriver with Chrome
2. How to implement stealth techniques to avoid detection
3. How to handle dynamic content loading
4. How to extend the BaseScraper for browser-based scraping

---

## 📦 Prerequisites

Before starting, make sure you have:
- ✅ Completed Day 4-6 (Base Scraper and Craigslist Scraper)
- ✅ Python virtual environment activated
- ✅ Basic understanding of async/await in Python
- ✅ Chrome browser installed on your system

---

## 🔧 Sub-Task 1: Install Selenium and ChromeDriver (30 minutes)

### What You'll Do:
Install Selenium and set up ChromeDriver for browser automation.

### Step-by-Step Instructions:

**1.1 Install Selenium Package**
```bash
cd backend
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install selenium webdriver-manager
```

**What these packages do:**
- `selenium`: Controls the web browser programmatically
- `webdriver-manager`: Automatically downloads and manages ChromeDriver

**1.2 Test Selenium Installation**

Create a test file: `backend/app/scrapers/test_selenium_setup.py`

```python
"""Test Selenium setup"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def test_selenium():
    """Test if Selenium can open Chrome"""
    print("Testing Selenium setup...")
    
    # Configure Chrome options
    options = Options()
    options.add_argument('--headless')  # Run without opening browser window
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Create driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Test by opening Google
    driver.get("https://www.google.com")
    print(f"✓ Successfully opened: {driver.title}")
    
    # Cleanup
    driver.quit()
    print("✓ Selenium setup working!")

if __name__ == "__main__":
    test_selenium()
```

**1.3 Run the Test**
```bash
python backend/app/scrapers/test_selenium_setup.py
```

**Expected Output:**
```
Testing Selenium setup...
✓ Successfully opened: Google
✓ Selenium setup working!
```

**Troubleshooting:**
- If Chrome doesn't open: Make sure Chrome browser is installed
- If you get "ChromeDriver not found": webdriver-manager should auto-download it
- If you get permission errors: Try running with `sudo` (Linux/Mac) or as Administrator (Windows)

### ✅ Deliverable:
- Selenium installed and working
- Test script runs successfully

---

## 🔧 Sub-Task 2: Create Facebook Scraper Class Structure (45 minutes)

### What You'll Do:
Create the basic structure of the Facebook Marketplace scraper that inherits from BaseScraper.

### Step-by-Step Instructions:

**2.1 Create the File**

Create: `backend/app/scrapers/facebook_marketplace.py`

```python
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
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from app.scrapers.base import BaseScraper
from app.utils.rate_limiter import RateLimiter


class FacebookMarketplaceScraper(BaseScraper):
    """
    Scraper for Facebook Marketplace.
    
    Uses Selenium WebDriver to handle JavaScript-rendered content.
    Implements stealth techniques to avoid detection.
    
    Example:
        >>> scraper = FacebookMarketplaceScraper()
        >>> results = await scraper.search("iPhone 13", "New York")
        >>> print(f"Found {len(results)} products")
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
        Setup Chrome WebDriver with stealth options.
        
        Configures Chrome to avoid detection as a bot.
        """
        options = Options()
        
        # Basic options
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Stealth options to avoid detection
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Set user agent to look like a real browser
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Create driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Additional stealth JavaScript
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    async def search(self, query: str, location: str, **kwargs) -> List[Dict]:
        """
        Search for products on Facebook Marketplace.
        
        Args:
            query: Search term (e.g., "iPhone 13")
            location: Location to search (e.g., "New York")
            **kwargs: Additional parameters (min_price, max_price, etc.)
        
        Returns:
            List[Dict]: List of product dictionaries
        """
        # TODO: Implement in Sub-Task 3
        pass
    
    async def get_product_details(self, product_url: str) -> Dict:
        """
        Get detailed information about a specific product.
        
        Args:
            product_url: URL of the product listing
        
        Returns:
            Dict: Detailed product information
        """
        # TODO: Implement in Sub-Task 4
        pass
    
    async def is_available(self, product_url: str) -> bool:
        """
        Check if a product listing is still available.
        
        Args:
            product_url: URL of the product listing
        
        Returns:
            bool: True if available, False if removed/sold
        """
        # TODO: Implement in Sub-Task 4
        pass
    
    async def close(self):
        """Close browser and cleanup resources."""
        if self.driver:
            self.driver.quit()
        await super().close()


# Test code
if __name__ == "__main__":
    print("=" * 60)
    print("FacebookMarketplaceScraper Class Created")
    print("=" * 60)
    print("✓ Class structure ready")
    print("✓ Selenium integration prepared")
    print("✓ Stealth options configured")
    print("=" * 60)
```

**2.2 Test the Structure**
```bash
python backend/app/scrapers/facebook_marketplace.py
```

**Expected Output:**
```
============================================================
FacebookMarketplaceScraper Class Created
============================================================
✓ Class structure ready
✓ Selenium integration prepared
✓ Stealth options configured
============================================================
```

### ✅ Deliverable:
- `facebook_marketplace.py` file created
- Class structure inherits from BaseScraper
- Driver setup method configured with stealth options

---

## 🔧 Sub-Task 3: Implement Search Method (90 minutes)

### What You'll Do:
Implement the `search()` method to find products on Facebook Marketplace.

### Key Concepts:

**Understanding Facebook Marketplace URLs:**
- Search URL format: `https://www.facebook.com/marketplace/[location]/search?query=[search_term]`
- Example: `https://www.facebook.com/marketplace/newyork/search?query=iphone`

**How Selenium Works:**
1. Open the URL in a browser
2. Wait for JavaScript to load the content
3. Find HTML elements using CSS selectors or XPath
4. Extract text/attributes from elements

### Step-by-Step Instructions:

**3.1 Update the `search()` method**

Replace the `search()` method in `facebook_marketplace.py`:

```python
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
    
    print(f"Searching Facebook Marketplace: {full_url}")
    
    # Run browser automation in thread pool (Selenium is blocking)
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, self._scrape_search_page, full_url, kwargs.get("max_results", 20))
    
    return results

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
                print(f"Error parsing listing: {e}")
                continue
        
        print(f"✓ Found {len(products)} products")
        return products
        
    except TimeoutException:
        print("⚠ Timeout waiting for listings to load")
        return []
    except Exception as e:
        print(f"✗ Error scraping search page: {e}")
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
        # Wait for content to load
        asyncio.sleep(1)

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
        print(f"Error parsing listing: {e}")
        return None
```

**3.2 Understanding the Code:**

- **`await loop.run_in_executor()`**: Selenium is blocking (not async), so we run it in a thread pool
- **`WebDriverWait`**: Waits for elements to appear (handles dynamic loading)
- **`_scroll_page()`**: Scrolls to trigger lazy loading of more products
- **`_parse_listing()`**: Extracts data from each product card

**3.3 Test the Search Method**

Add this test code at the bottom of `facebook_marketplace.py`:

```python
async def test_search():
    """Test search functionality"""
    print("\n" + "=" * 60)
    print("Testing Facebook Marketplace Search")
    print("=" * 60)
    
    scraper = FacebookMarketplaceScraper(headless=True)
    
    try:
        # Search for iPhone
        results = await scraper.search("iPhone", "newyork", max_results=5)
        
        print(f"\n✓ Found {len(results)} products")
        
        if results:
            print("\nFirst product:")
            print(f"  Title: {results[0]['title']}")
            print(f"  Price: ${results[0]['price']}")
            print(f"  URL: {results[0]['url'][:50]}...")
        
    finally:
        await scraper.close()
    
    print("=" * 60)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_search())
```

**3.4 Run the Test**
```bash
python backend/app/scrapers/facebook_marketplace.py
```

### ⚠️ Important Notes:

**Facebook's Anti-Scraping Measures:**
- Facebook actively blocks scrapers
- You may need to log in to see results
- Selectors change frequently
- Consider using Facebook's official API for production

**For Learning Purposes:**
- This implementation shows the concepts
- In production, you'd need more robust error handling
- Consider using proxies and rotating user agents

### ✅ Deliverable:
- `search()` method implemented
- Can find and parse product listings
- Test runs successfully (even if Facebook blocks some requests)

---

## 🔧 Sub-Task 4: Implement Product Details and Availability (60 minutes)

### What You'll Do:
Implement methods to get detailed product information and check availability.

### Step-by-Step Instructions:

**4.1 Implement `get_product_details()`**

Add this method to `facebook_marketplace.py`:

```python
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
        print(f"Error scraping product page: {e}")
        return {'url': url, 'error': str(e)}
```

**4.2 Implement `is_available()`**

Add this method:

```python
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
        print(f"Error checking availability: {e}")
        return False
```

### ✅ Deliverable:
- `get_product_details()` method implemented
- `is_available()` method implemented
- Both methods handle errors gracefully

---

## 🔧 Sub-Task 5: Write Tests (60 minutes)

### What You'll Do:
Create comprehensive tests for the Facebook scraper.

### Step-by-Step Instructions:

**5.1 Create Test File**

Create: `backend/app/tests/test_facebook_marketplace.py`

```python
"""
Tests for Facebook Marketplace Scraper
"""
import pytest
import asyncio
from app.scrapers.facebook_marketplace import FacebookMarketplaceScraper


@pytest.mark.asyncio
async def test_scraper_initialization():
    """Test that scraper initializes correctly"""
    scraper = FacebookMarketplaceScraper(headless=True)
    
    assert scraper is not None
    assert scraper.base_url == "https://www.facebook.com/marketplace"
    assert scraper.headless == True
    
    await scraper.close()


@pytest.mark.asyncio
async def test_search_returns_list():
    """Test that search returns a list"""
    scraper = FacebookMarketplaceScraper(headless=True)
    
    try:
        results = await scraper.search("test", "newyork", max_results=3)
        assert isinstance(results, list)
    finally:
        await scraper.close()


@pytest.mark.asyncio
async def test_search_result_structure():
    """Test that search results have correct structure"""
    scraper = FacebookMarketplaceScraper(headless=True)
    
    try:
        results = await scraper.search("iPhone", "newyork", max_results=1)
        
        if results:  # Only test if we got results
            product = results[0]
            
            # Check required fields
            assert 'title' in product
            assert 'price' in product
            assert 'url' in product
            assert 'platform' in product
            
            # Check types
            assert isinstance(product['title'], str)
            assert isinstance(product['url'], str)
            assert product['platform'] == 'facebook'
            
    finally:
        await scraper.close()


@pytest.mark.asyncio
async def test_driver_setup():
    """Test that driver sets up correctly"""
    scraper = FacebookMarketplaceScraper(headless=True)
    
    try:
        # Trigger driver setup
        scraper._setup_driver()
        
        assert scraper.driver is not None
        
        # Test that driver can navigate
        scraper.driver.get("https://www.google.com")
        assert "Google" in scraper.driver.title
        
    finally:
        await scraper.close()


@pytest.mark.asyncio
async def test_close_cleanup():
    """Test that close() properly cleans up resources"""
    scraper = FacebookMarketplaceScraper(headless=True)
    scraper._setup_driver()
    
    await scraper.close()
    
    # Driver should be closed
    # Note: Can't easily test this without accessing private state


def test_price_extraction():
    """Test price extraction helper method"""
    scraper = FacebookMarketplaceScraper(headless=True)
    
    # Test various price formats
    assert scraper._extract_price("$100") == 100.0
    assert scraper._extract_price("$1,234.56") == 1234.56
    assert scraper._extract_price("Price: $50") == 50.0
    assert scraper._extract_price("Free") == 0.0
    assert scraper._extract_price("Best offer") is None


def test_text_cleaning():
    """Test text cleaning helper method"""
    scraper = FacebookMarketplaceScraper(headless=True)
    
    assert scraper._clean_text("  Hello   World  ") == "Hello World"
    assert scraper._clean_text("\n  Text\t  ") == "Text"
    assert scraper._clean_text("") == ""


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
```

**5.2 Run Tests**
```bash
cd backend
pytest app/tests/test_facebook_marketplace.py -v
```

**Expected Output:**
```
test_facebook_marketplace.py::test_scraper_initialization PASSED
test_facebook_marketplace.py::test_search_returns_list PASSED
test_facebook_marketplace.py::test_driver_setup PASSED
test_facebook_marketplace.py::test_price_extraction PASSED
test_facebook_marketplace.py::test_text_cleaning PASSED
```

### ✅ Deliverable:
- Test file created with 5+ tests
- All tests pass
- Tests cover initialization, search, and helper methods

---

## 🔧 Sub-Task 6: Add Stealth Enhancements (45 minutes)

### What You'll Do:
Add additional stealth techniques to avoid detection.

### Step-by-Step Instructions:

**6.1 Install Additional Package**
```bash
pip install selenium-stealth
```

**6.2 Update Driver Setup**

Modify the `_setup_driver()` method in `facebook_marketplace.py`:

```python
def _setup_driver(self):
    """
    Setup Chrome WebDriver with advanced stealth options.
    """
    from selenium_stealth import stealth
    
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
    
    # Create driver
    service = Service(ChromeDriverManager().install())
    self.driver = webdriver.Chrome(service=service, options=options)
    
    # Apply selenium-stealth
    stealth(self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
    
    # Additional stealth JavaScript
    self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    print("✓ Stealth driver configured")
```

**6.3 Add Random Delays**

Add this helper method:

```python
import random
import time

def _random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
    """
    Add random delay to mimic human behavior.
    
    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
```

**6.4 Use Delays in Search**

Update the `_scrape_search_page()` method to add delays:

```python
def _scrape_search_page(self, url: str, max_results: int) -> List[Dict]:
    """Scrape search results page with human-like behavior."""
    try:
        # Navigate to search page
        self.driver.get(url)
        self._random_delay(2, 4)  # Wait like a human would
        
        # Wait for listings to load
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='x9f619']")))
        
        # Scroll gradually (more human-like)
        for i in range(3):
            scroll_amount = random.randint(300, 700)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            self._random_delay(1, 2)
        
        # Rest of the method...
```

### ✅ Deliverable:
- selenium-stealth package installed
- Advanced stealth options configured
- Random delays added to mimic human behavior

---

## 📝 Sub-Task 7: Documentation and Integration (30 minutes)

### What You'll Do:
Document your code and prepare it for integration with the rest of the system.

### Step-by-Step Instructions:

**7.1 Add Module Documentation**

At the top of `facebook_marketplace.py`, add comprehensive documentation:

```python
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
```

**7.2 Create README**

Create: `backend/app/scrapers/README_FACEBOOK.md`

```markdown
# Facebook Marketplace Scraper

## Overview
Scrapes product listings from Facebook Marketplace using Selenium WebDriver.

## Requirements
- Python 3.8+
- Chrome browser
- selenium
- webdriver-manager
- selenium-stealth

## Installation
```bash
pip install selenium webdriver-manager selenium-stealth
```

## Usage

### Basic Search
```python
from app.scrapers.facebook_marketplace import FacebookMarketplaceScraper

scraper = FacebookMarketplaceScraper(headless=True)
results = await scraper.search("iPhone", "newyork", max_results=10)
await scraper.close()
```

### With Price Filters
```python
results = await scraper.search(
    "laptop",
    "losangeles",
    min_price=500,
    max_price=1000,
    max_results=20
)
```

### Get Product Details
```python
details = await scraper.get_product_details("https://facebook.com/marketplace/item/...")
print(details['description'])
```

## Limitations
- Facebook may block automated access
- Requires login for some features
- Selectors change frequently
- Rate limiting required

## Troubleshooting

### Chrome not found
Install Chrome browser from https://www.google.com/chrome/

### ChromeDriver issues
webdriver-manager should auto-download, but you can manually install from:
https://chromedriver.chromium.org/

### Timeout errors
Increase wait time in WebDriverWait or check internet connection

## Future Improvements
- Add proxy support
- Implement cookie management for login
- Add more robust selector fallbacks
- Implement retry logic
```

**7.3 Update Main Scrapers __init__.py**

Update `backend/app/scrapers/__init__.py`:

```python
"""
Scrapers Package

Contains all platform-specific scrapers.
"""

from app.scrapers.base import BaseScraper
from app.scrapers.craigslist import CraigslistScraper
from app.scrapers.facebook_marketplace import FacebookMarketplaceScraper

__all__ = [
    'BaseScraper',
    'CraigslistScraper',
    'FacebookMarketplaceScraper',
]
```

### ✅ Deliverable:
- Code fully documented
- README created
- Package __init__.py updated

---

## 🎯 Final Checklist

Before considering Day 7 complete, verify:

- [ ] Selenium and ChromeDriver installed and working
- [ ] FacebookMarketplaceScraper class created
- [ ] Inherits from BaseScraper correctly
- [ ] `search()` method implemented and tested
- [ ] `get_product_details()` method implemented
- [ ] `is_available()` method implemented
- [ ] Stealth techniques configured
- [ ] Tests written and passing (at least 5 tests)
- [ ] Code documented with docstrings
- [ ] README created
- [ ] Can successfully scrape at least one product

---

## 🚨 Common Issues and Solutions

### Issue 1: "ChromeDriver not found"
**Solution:** 
```bash
pip install webdriver-manager
# It will auto-download on first run
```

### Issue 2: "Timeout waiting for elements"
**Solution:**
- Increase WebDriverWait timeout
- Check if Facebook changed their HTML structure
- Try running without headless mode to see what's happening

### Issue 3: "Facebook blocks requests"
**Solution:**
- Add more delays between requests
- Use residential proxies (advanced)
- Consider Facebook's official API

### Issue 4: "Tests fail intermittently"
**Solution:**
- Facebook's HTML changes frequently
- Update CSS selectors
- Add more robust error handling

### Issue 5: "Selenium is slow"
**Solution:**
- This is normal - Selenium runs a real browser
- Use headless mode for better performance
- Consider using lighter alternatives for production

---

## 📚 Additional Resources

**Selenium Documentation:**
- Official Docs: https://selenium-python.readthedocs.io/
- Locating Elements: https://selenium-python.readthedocs.io/locating-elements.html
- Waits: https://selenium-python.readthedocs.io/waits.html

**Web Scraping Best Practices:**
- Respect robots.txt
- Add delays between requests
- Use official APIs when available
- Handle errors gracefully

**Next Steps:**
After completing Day 7, you'll move to Day 8: eBay Scraper, which will be similar but simpler since eBay is more scraper-friendly.

---

## ✅ Success Criteria

Day 7 is complete when:
1. ✅ Selenium installed and configured
2. ✅ FacebookMarketplaceScraper class created
3. ✅ All three abstract methods implemented
4. ✅ Stealth techniques applied
5. ✅ Tests written and passing
6. ✅ Can successfully scrape at least one product
7. ✅ Code documented
8. ✅ Ready for integration with orchestrator

---

**Congratulations!** 🎉

You've now built a browser-based scraper using Selenium! This is a valuable skill for scraping JavaScript-heavy websites.

**What you learned:**
- How to use Selenium WebDriver
- Browser automation techniques
- Stealth methods to avoid detection
- Handling dynamic content
- Async integration with blocking code

**Next:** Day 8 - eBay Scraper (easier than Facebook!)