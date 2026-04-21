# eBay Selenium Scraper Setup Guide

## 📦 Installation

### Step 1: Install Required Packages

```bash
cd backend
pip install undetected-chromedriver selenium
```

Or if using uv:
```bash
cd backend
uv pip install undetected-chromedriver selenium
```

### Step 2: Verify Installation

```bash
python -c "import undetected_chromedriver; import selenium; print('✅ Packages installed successfully')"
```

## 🚀 Usage

### Basic Usage

```python
import asyncio
from app.scrapers.ebay_selenium import EbaySeleniumScraper

async def search_ebay():
    # Create scraper (headless=True for background, False to see browser)
    async with EbaySeleniumScraper(headless=True) as scraper:
        # Search for products
        results = await scraper.search("iPhone 13", max_results=10)
        
        print(f"Found {len(results)} products:")
        for product in results:
            print(f"  - {product['title']}: ${product['price']}")
        
        # Get details for first product
        if results:
            details = await scraper.get_product_details(results[0]['url'])
            print(f"\nDetails: {details['title']}")
            print(f"Condition: {details['condition']}")

asyncio.run(search_ebay())
```

### With Price Filters

```python
results = await scraper.search(
    "laptop",
    min_price=500,
    max_price=1000,
    condition="new",
    max_results=20
)
```

### Check Availability

```python
url = "https://www.ebay.com/itm/123456789"
is_available = await scraper.is_available(url)
print(f"Product available: {is_available}")
```

## 🎯 Advantages Over HTTP Scraper

### ✅ Bypasses Bot Detection
- Uses real Chrome browser
- Executes JavaScript
- Passes browser fingerprinting checks
- No CAPTCHA challenges

### ✅ More Reliable
- Actually loads the page like a real user
- Handles dynamic content
- Works with eBay's current structure

### ❌ Disadvantages
- **Slower** - Takes 3-5 seconds per page
- **More resources** - Needs Chrome browser
- **Headless issues** - Some sites detect headless mode

## 🔧 Configuration Options

### Headless Mode

```python
# Run in background (faster, no window)
scraper = EbaySeleniumScraper(headless=True)

# Show browser window (useful for debugging)
scraper = EbaySeleniumScraper(headless=False)
```

### Custom Rate Limiting

```python
from app.utils.rate_limiter import RateLimiter

# Slower rate limiting (more polite)
rate_limiter = RateLimiter(max_requests=5, time_window=60)
scraper = EbaySeleniumScraper(rate_limiter=rate_limiter)
```

## 🧪 Testing

### Run the Built-in Test

```bash
cd backend
python app/scrapers/ebay_selenium.py
```

This will:
1. Open Chrome browser
2. Search for "iPhone 13"
3. Display first 5 results
4. Get details for first product
5. Check availability

### Run Unit Tests

```bash
cd backend
pytest app/tests/test_ebay_selenium.py -v
```

## 🐛 Troubleshooting

### Issue: "Chrome driver not found"

**Solution:**
```bash
# undetected-chromedriver downloads Chrome automatically
# Just make sure you have internet connection
pip install --upgrade undetected-chromedriver
```

### Issue: "Chrome version mismatch"

**Solution:**
```bash
# Update undetected-chromedriver
pip install --upgrade undetected-chromedriver

# Or specify Chrome version
import undetected_chromedriver as uc
driver = uc.Chrome(version_main=120)  # Use your Chrome version
```

### Issue: Browser opens but nothing happens

**Solution:**
- Check your internet connection
- Try with `headless=False` to see what's happening
- Increase timeout in code

### Issue: Still getting blocked

**Solution:**
- Add random delays between requests
- Use residential proxies
- Rotate user agents
- Consider using eBay API instead

## 📊 Performance Comparison

| Method | Speed | Reliability | Bot Detection |
|--------|-------|-------------|---------------|
| HTTP (httpx) | ⚡ Fast (0.5s) | ❌ Blocked | ❌ Detected |
| Selenium | 🐢 Slow (3-5s) | ✅ Works | ✅ Bypassed |
| eBay API | ⚡ Fast (1s) | ✅ Perfect | ✅ Official |

## 🎓 When to Use Each Method

### Use HTTP Scraper (ebay.py)
- ✅ Testing/development
- ✅ Mock data scenarios
- ✅ When eBay isn't blocking you
- ✅ Learning web scraping basics

### Use Selenium Scraper (ebay_selenium.py)
- ✅ Production scraping
- ✅ When HTTP scraper is blocked
- ✅ Need reliable results
- ✅ Can afford slower speed

### Use eBay API
- ✅ Production applications
- ✅ Need high reliability
- ✅ Legal compliance required
- ✅ Can get API credentials

## 💡 Best Practices

### 1. Respect Rate Limits
```python
# Don't make too many requests
rate_limiter = RateLimiter(max_requests=10, time_window=60)
```

### 2. Add Random Delays
```python
import random
import time

# Between searches
time.sleep(random.uniform(2, 5))
```

### 3. Handle Errors Gracefully
```python
try:
    results = await scraper.search("iPhone")
except Exception as e:
    logger.error(f"Search failed: {e}")
    results = []
```

### 4. Close Resources
```python
# Always use context manager
async with EbaySeleniumScraper() as scraper:
    # Your code here
    pass
# Browser automatically closed
```

### 5. Monitor for Changes
```python
# eBay's HTML structure may change
# Log when parsing fails
if not product:
    logger.warning(f"Failed to parse item: {item}")
```

## 🔄 Switching Between Scrapers

Both scrapers implement the same interface, so you can easily switch:

```python
# Use HTTP scraper
from app.scrapers.ebay import EbayScraper
scraper = EbayScraper()

# Switch to Selenium scraper
from app.scrapers.ebay_selenium import EbaySeleniumScraper
scraper = EbaySeleniumScraper()

# Same methods work for both!
results = await scraper.search("iPhone 13")
```

## 📚 Additional Resources

- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Undetected ChromeDriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
- [eBay Robots.txt](https://www.ebay.com/robots.txt)
- [eBay Developer Program](https://developer.ebay.com/)

## ✅ Next Steps

1. Install the packages
2. Run the test script
3. Try searching for different products
4. Integrate with your product search agent
5. Consider switching to eBay API for production

---

**Happy Scraping! 🚀**