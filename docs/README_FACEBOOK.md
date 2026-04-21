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