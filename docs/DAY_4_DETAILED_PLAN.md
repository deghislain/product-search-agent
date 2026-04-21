# Day 4: Base Scraper & Utilities - Detailed Sub-Task Plan

**Total Estimated Time:** 4 hours  
**Difficulty Level:** Beginner-Friendly  
**Goal:** Build the foundation for web scraping by creating utilities and a base scraper interface

---

## 📋 Overview

Day 4 focuses on creating the **building blocks** for your web scrapers. Think of this as building the tools before you build the house. You'll create:

1. **Rate Limiter** - Controls how fast we make requests (prevents getting blocked)
2. **Base Scraper** - A template that all scrapers will follow (keeps code organized)
3. **Text Processing** - Helper functions to clean and process text data

---

## 🎯 Sub-Task 1: Create Rate Limiter (1.5 hours)

### What is a Rate Limiter?
A rate limiter controls how many requests you can make to a website in a given time period. This prevents:
- Getting blocked by websites
- Overloading servers
- Being detected as a bot

### Step 1.1: Create the File Structure (5 minutes)
```bash
# Navigate to backend directory
cd backend

# Create utils directory if it doesn't exist
mkdir -p app/utils

# Create the rate limiter file
touch app/utils/rate_limiter.py
touch app/utils/__init__.py
```

### Step 1.2: Understand the Concept (10 minutes)
**Read this before coding:**

A rate limiter works like a traffic light:
- **Green Light:** You can make a request
- **Red Light:** You must wait before making another request

We'll use a **token bucket algorithm**:
- You have a bucket with tokens
- Each request costs 1 token
- Tokens refill over time
- If no tokens available, you wait

### Step 1.3: Write the Rate Limiter Class (45 minutes)

**Create `app/utils/rate_limiter.py` with this structure:**

```python
import time
import asyncio
from typing import Dict
from datetime import datetime, timedelta

class RateLimiter:
    """
    Controls the rate of requests to prevent overwhelming servers.
    
    Example:
        limiter = RateLimiter(max_requests=10, time_window=60)
        await limiter.acquire()  # Wait if needed, then proceed
    """
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: list = []  # Store timestamps of requests
        
    async def acquire(self):
        """
        Wait if necessary, then allow request to proceed.
        This is the main method you'll call before making requests.
        """
        # TODO: Implement the logic
        pass
    
    def _clean_old_requests(self):
        """Remove requests older than time_window."""
        # TODO: Implement
        pass
    
    def _calculate_wait_time(self) -> float:
        """Calculate how long to wait before next request."""
        # TODO: Implement
        pass
```

**Implementation hints:**
- Use `time.time()` to get current timestamp
- Store request timestamps in `self.requests` list
- Remove old timestamps that are outside the time window
- If at max capacity, calculate wait time until oldest request expires

### Step 1.4: Add Helper Methods (20 minutes)

Add these useful methods:
```python
def get_current_rate(self) -> int:
    """Get number of requests in current window."""
    self._clean_old_requests()
    return len(self.requests)

def is_available(self) -> bool:
    """Check if a request can be made immediately."""
    self._clean_old_requests()
    return len(self.requests) < self.max_requests
```

### Step 1.5: Test Your Rate Limiter (10 minutes)

Create a simple test:
```python
# At the bottom of rate_limiter.py
if __name__ == "__main__":
    async def test():
        limiter = RateLimiter(max_requests=5, time_window=10)
        
        for i in range(10):
            print(f"Request {i+1}...")
            await limiter.acquire()
            print(f"  ✓ Request {i+1} completed")
            print(f"  Current rate: {limiter.get_current_rate()}/5")
    
    asyncio.run(test())
```

Run it:
```bash
python app/utils/rate_limiter.py
```

**Expected output:** First 5 requests should be instant, then you'll see delays.

---

## 🎯 Sub-Task 2: Create Base Scraper Interface (1.5 hours)

### What is a Base Scraper?
A base scraper is like a **template** or **blueprint** that all your scrapers will follow. It ensures:
- All scrapers have the same methods
- Code is consistent and maintainable
- Easy to add new scrapers later

### Step 2.1: Create the File Structure (5 minutes)
```bash
# Create scrapers directory
mkdir -p app/scrapers

# Create files
touch app/scrapers/__init__.py
touch app/scrapers/base.py
```

### Step 2.2: Understand Abstract Base Classes (10 minutes)

**Read this concept:**

Python's `ABC` (Abstract Base Class) lets you create a template that other classes must follow.

```python
from abc import ABC, abstractmethod

class Animal(ABC):  # Template
    @abstractmethod
    def make_sound(self):  # All animals must implement this
        pass

class Dog(Animal):  # Follows template
    def make_sound(self):
        return "Woof!"
```

### Step 2.3: Design the Base Scraper (20 minutes)

**Think about what ALL scrapers need:**
- Search for products
- Get product details
- Check if a listing is still available
- Handle rate limiting
- Handle errors

**Create `app/scrapers/base.py`:**

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import httpx
from app.utils.rate_limiter import RateLimiter

class BaseScraper(ABC):
    """
    Base class for all scrapers.
    All scrapers (Craigslist, eBay, Facebook) will inherit from this.
    """
    
    def __init__(self, rate_limiter: Optional[RateLimiter] = None):
        """
        Initialize scraper.
        
        Args:
            rate_limiter: Optional rate limiter for controlling request rate
        """
        self.rate_limiter = rate_limiter or RateLimiter(max_requests=10, time_window=60)
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers=self._get_default_headers()
        )
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default HTTP headers to look like a real browser."""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
    
    @abstractmethod
    async def search(self, query: str, location: str, **kwargs) -> List[Dict]:
        """
        Search for products. MUST be implemented by each scraper.
        
        Args:
            query: Search term (e.g., "iPhone 13")
            location: Location to search (e.g., "New York")
            **kwargs: Additional platform-specific parameters
            
        Returns:
            List of product dictionaries
        """
        pass
    
    @abstractmethod
    async def get_product_details(self, product_url: str) -> Dict:
        """
        Get detailed information about a product.
        MUST be implemented by each scraper.
        
        Args:
            product_url: URL of the product listing
            
        Returns:
            Dictionary with product details
        """
        pass
    
    @abstractmethod
    async def is_available(self, product_url: str) -> bool:
        """
        Check if a product listing is still available.
        MUST be implemented by each scraper.
        
        Args:
            product_url: URL of the product listing
            
        Returns:
            True if available, False otherwise
        """
        pass
    
    async def close(self):
        """Close HTTP client connection."""
        await self.client.aclose()
```

### Step 2.4: Add Helper Methods (30 minutes)

Add these useful methods that all scrapers can use:

```python
async def _make_request(self, url: str, method: str = "GET", **kwargs) -> httpx.Response:
    """
    Make HTTP request with rate limiting.
    
    Args:
        url: URL to request
        method: HTTP method (GET, POST, etc.)
        **kwargs: Additional arguments for httpx
        
    Returns:
        HTTP response
    """
    await self.rate_limiter.acquire()  # Wait if needed
    
    try:
        response = await self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        raise

def _extract_price(self, price_text: str) -> Optional[float]:
    """
    Extract numeric price from text.
    
    Examples:
        "$1,234.56" -> 1234.56
        "Price: $50" -> 50.0
        "Free" -> 0.0
    """
    # TODO: Implement price extraction logic
    pass

def _clean_text(self, text: str) -> str:
    """Remove extra whitespace and clean text."""
    if not text:
        return ""
    return " ".join(text.split())
```

### Step 2.5: Document Your Code (15 minutes)

Add docstrings explaining:
- What each method does
- What parameters it takes
- What it returns
- Example usage

### Step 2.6: Create a Simple Test (10 minutes)

```python
# At the bottom of base.py
if __name__ == "__main__":
    # This won't run because BaseScraper is abstract
    # But you can test that it's properly structured
    print("✓ BaseScraper class created successfully")
    print("✓ All abstract methods defined")
    print("✓ Helper methods available")
```

---

## 🎯 Sub-Task 3: Create Text Processing Utilities (1 hour)

### What are Text Processing Utilities?
These are helper functions to clean and process text data from websites. Websites have messy data:
- Extra spaces
- HTML entities (`&`, `&nbsp;`)
- Inconsistent formatting
- Special characters

### Step 3.1: Create the File (5 minutes)
```bash
touch app/utils/text_processing.py
```

### Step 3.2: Understand Common Text Issues (10 minutes)

**Examples of messy text:**
```
"  iPhone   13  Pro  "           → "iPhone 13 Pro"
"Price: $1,234.56"               → 1234.56
"Great condition!!!"             → "Great condition"
"& more"                     → "& more"
"IPHONE 13 PRO"                  → "iphone 13 pro"
```

### Step 3.3: Implement Basic Functions (25 minutes)

**Create `app/utils/text_processing.py`:**

```python
import re
import html
from typing import Optional

def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
        
    Example:
        >>> clean_text("  Hello   World  ")
        "Hello World"
    """
    if not text:
        return ""
    
    # Decode HTML entities (& -> &)
    text = html.unescape(text)
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def extract_price(text: str) -> Optional[float]:
    """
    Extract price from text.
    
    Args:
        text: Text containing price
        
    Returns:
        Price as float, or None if not found
        
    Example:
        >>> extract_price("$1,234.56")
        1234.56
    """
    if not text:
        return None
    
    # Remove currency symbols and commas
    text = re.sub(r'[$,]', '', text)
    
    # Find first number (with optional decimal)
    match = re.search(r'\d+\.?\d*', text)
    
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    
    return None

def normalize_text(text: str) -> str:
    """
    Normalize text for comparison (lowercase, remove punctuation).
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
        
    Example:
        >>> normalize_text("iPhone 13 Pro!!!")
        "iphone 13 pro"
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation except spaces
    text = re.sub(r'[^\w\s]', '', text)
    
    # Clean whitespace
    text = " ".join(text.split())
    
    return text
```

### Step 3.4: Add Advanced Functions (15 minutes)

```python
def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].strip() + suffix

def extract_numbers(text: str) -> list:
    """
    Extract all numbers from text.
    
    Args:
        text: Text to search
        
    Returns:
        List of numbers found
        
    Example:
        >>> extract_numbers("iPhone 13 Pro 256GB for $999")
        [13, 256, 999]
    """
    if not text:
        return []
    
    return [int(n) for n in re.findall(r'\d+', text)]
```

### Step 3.5: Write Tests (5 minutes)

```python
if __name__ == "__main__":
    # Test clean_text
    assert clean_text("  Hello   World  ") == "Hello World"
    print("✓ clean_text works")
    
    # Test extract_price
    assert extract_price("$1,234.56") == 1234.56
    assert extract_price("Price: $50") == 50.0
    print("✓ extract_price works")
    
    # Test normalize_text
    assert normalize_text("iPhone 13 Pro!!!") == "iphone 13 pro"
    print("✓ normalize_text works")
    
    print("\n✅ All text processing functions working!")
```

Run tests:
```bash
python app/utils/text_processing.py
```

---

## ✅ Verification Checklist

After completing all sub-tasks, verify:

### Rate Limiter
- [ ] File created: `app/utils/rate_limiter.py`
- [ ] `RateLimiter` class implemented
- [ ] `acquire()` method works
- [ ] Test runs successfully
- [ ] Requests are properly rate-limited

### Base Scraper
- [ ] File created: `app/scrapers/base.py`
- [ ] `BaseScraper` class created with ABC
- [ ] All abstract methods defined (`search`, `get_product_details`, `is_available`)
- [ ] Helper methods implemented
- [ ] Proper documentation added

### Text Processing
- [ ] File created: `app/utils/text_processing.py`
- [ ] `clean_text()` function works
- [ ] `extract_price()` function works
- [ ] `normalize_text()` function works
- [ ] All tests pass

---

## 🧪 Final Integration Test

Create a test file to verify everything works together:

```bash
touch app/tests/test_day4.py
```

```python
import asyncio
from app.utils.rate_limiter import RateLimiter
from app.utils.text_processing import clean_text, extract_price

async def test_day4():
    print("Testing Day 4 Components...\n")
    
    # Test 1: Rate Limiter
    print("1. Testing Rate Limiter...")
    limiter = RateLimiter(max_requests=3, time_window=5)
    for i in range(5):
        await limiter.acquire()
        print(f"   Request {i+1} completed")
    print("   ✓ Rate limiter working\n")
    
    # Test 2: Text Processing
    print("2. Testing Text Processing...")
    messy_text = "  iPhone   13  Pro  "
    clean = clean_text(messy_text)
    print(f"   Cleaned: '{messy_text}' -> '{clean}'")
    
    price = extract_price("$1,234.56")
    print(f"   Price extracted: $1,234.56 -> {price}")
    print("   ✓ Text processing working\n")
    
    print("✅ All Day 4 components working!")

if __name__ == "__main__":
    asyncio.run(test_day4())
```

Run:
```bash
python app/tests/test_day4.py
```

---

## 📚 Key Concepts to Understand

### 1. **Async/Await**
- `async def` creates an asynchronous function
- `await` pauses execution until operation completes
- Allows multiple operations to run concurrently

### 2. **Abstract Base Classes (ABC)**
- Forces child classes to implement specific methods
- Ensures consistency across scrapers
- Prevents instantiation of incomplete classes

### 3. **Rate Limiting**
- Prevents overwhelming servers
- Avoids getting blocked
- Professional web scraping practice

### 4. **Text Processing**
- Cleans messy data from websites
- Normalizes for comparison
- Extracts structured data from unstructured text

---

## 🎓 Learning Resources

- **Python ABC**: https://docs.python.org/3/library/abc.html
- **Async/Await**: https://realpython.com/async-io-python/
- **Regular Expressions**: https://regex101.com/
- **HTTP Requests**: https://www.python-httpx.org/

---

## 🚨 Common Mistakes to Avoid

1. **Forgetting `await`** - Always use `await` with async functions
2. **Not testing** - Test each component as you build it
3. **Hardcoding values** - Use parameters and configuration
4. **Skipping documentation** - Document as you code, not after
5. **Not handling errors** - Add try/except blocks for robustness

---

## 💡 Tips for Success

1. **Take breaks** - Don't rush through all 4 hours at once
2. **Test frequently** - Test after each sub-task
3. **Read error messages** - They tell you exactly what's wrong
4. **Use print statements** - Debug by printing values
5. **Ask questions** - If stuck, ask for help!

---

## 🎯 Next Steps (Day 5)

After completing Day 4, you'll be ready for:
- **Day 5-6**: Implementing the Craigslist scraper using your base scraper
- You'll use the rate limiter to control requests
- You'll use text processing to clean scraped data
- The base scraper will provide the structure

---

## ✨ Congratulations!

Once you complete Day 4, you'll have:
- ✅ A working rate limiter
- ✅ A solid base scraper template
- ✅ Useful text processing utilities
- ✅ The foundation for all future scrapers

**You're building the tools that will make the rest of the project much easier!** 🚀