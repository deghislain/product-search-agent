# Project Structure & Implementation Guide

## Complete Project Structure

```
product-search-agent/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI application entry point
│   │   ├── config.py                    # Configuration management
│   │   ├── database.py                  # Database connection and operations
│   │   ├── dependencies.py              # FastAPI dependencies
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── search_request.py        # SearchRequest model
│   │   │   ├── product.py               # Product model
│   │   │   ├── search_execution.py      # SearchExecution modelecho "venv/\n*.pyc\n.env\nnode_modules/\n*.db" > .gitignore
│   │   │   └── notification.py          # Notification model
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── search_request.py        # Pydantic schemas for API
│   │   │   ├── product.py
│   │   │   ├── search_execution.py
│   │   │   └── notification.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── search_requests.py   # Search request endpoints
│   │   │   │   ├── products.py          # Product endpoints
│   │   │   │   ├── notifications.py     # Notification endpoints
│   │   │   │   ├── health.py            # Health check endpoints
│   │   │   │   └── websocket.py         # WebSocket endpoint
│   │   │   └── deps.py                  # Route dependencies
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py          # Search orchestrator
│   │   │   ├── scheduler.py             # APScheduler setup
│   │   │   ├── matching.py              # Matching engine
│   │   │   └── notification_service.py  # Notification service
│   │   │
│   │   ├── scrapers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # Base scraper interface
│   │   │   ├── craigslist.py            # Craigslist scraper
│   │   │   ├── facebook_marketplace.py  # Facebook scraper
│   │   │   ├── ebay.py                  # eBay scraper
│   │   │   ├── generic.py               # Generic scraper
│   │   │   └── utils.py                 # Scraper utilities
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── text_processing.py       # Text matching utilities
│   │   │   ├── rate_limiter.py          # Rate limiting
│   │   │   ├── logger.py                # Logging configuration
│   │   │   └── validators.py            # Input validation
│   │   │
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_scrapers.py
│   │       ├── test_matching.py
│   │       ├── test_api.py
│   │       └── conftest.py
│   │
│   ├── alembic/                         # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── README.md
│
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   │
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchRequestForm.tsx    # Create/edit search form
│   │   │   ├── SearchRequestList.tsx    # List of active searches
│   │   │   ├── ProductCard.tsx          # Product display card
│   │   │   ├── MatchNotification.tsx    # Match notification component
│   │   │   ├── SearchHistory.tsx        # Search execution history
│   │   │   └── SettingsPanel.tsx        # Settings configuration
│   │   │
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx            # Main dashboard
│   │   │   ├── SearchDetails.tsx        # Search request details
│   │   │   ├── Matches.tsx              # All matches view
│   │   │   └── Settings.tsx             # Settings page
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts                   # API client
│   │   │   ├── websocket.ts             # WebSocket client
│   │   │   └── storage.ts               # Local storage utilities
│   │   │
│   │   ├── hooks/
│   │   │   ├── useSearchRequests.ts     # Search requests hook
│   │   │   ├── useProducts.ts           # Products hook
│   │   │   ├── useNotifications.ts      # Notifications hook
│   │   │   └── useWebSocket.ts          # WebSocket hook
│   │   │
│   │   ├── types/
│   │   │   ├── search.ts                # TypeScript types
│   │   │   ├── product.ts
│   │   │   └── notification.ts
│   │   │
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── vite-env.d.ts
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── README.md
│
├── docker-compose.yml
├── .gitignore
├── README.md
└── LICENSE
```

---

## Detailed Scraper Implementations

### 1. Craigslist Scraper

**Implementation Strategy:**
- Use BeautifulSoup4 for HTML parsing
- Support RSS feeds for recent listings
- Location-based search with city codes
- No authentication required

**Code Structure:**

```python
# backend/app/scrapers/craigslist.py

import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime
from .base import BaseScraper
from ..models.product import Product
from ..utils.rate_limiter import RateLimiter

class CraigslistScraper(BaseScraper):
    """
    Craigslist scraper implementation.
    
    URL Structure:
    https://{city}.craigslist.org/search/{category}?query={query}&max_price={price}
    
    Example:
    https://boston.craigslist.org/search/cta?query=toyota+camry&max_price=6000
    """
    
    BASE_URL = "https://{city}.craigslist.org"
    SEARCH_PATH = "/search/{category}"
    
    # Category codes
    CATEGORIES = {
        "cars": "cta",
        "electronics": "ela",
        "furniture": "fua",
        "general": "sss"
    }
    
    def __init__(self, city: str = "boston"):
        self.city = city
        self.rate_limiter = RateLimiter(requests_per_minute=10)
        self.client = httpx.AsyncClient(
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            },
            timeout=30.0
        )
    
    async def search(
        self,
        query: str,
        max_price: float,
        location: Optional[str] = None,
        category: str = "general"
    ) -> List[Product]:
        """
        Search Craigslist for products matching criteria.
        
        Args:
            query: Search query (e.g., "toyota camry")
            max_price: Maximum price
            location: City code (e.g., "boston", "newyork")
            category: Product category
            
        Returns:
            List of Product objects
        """
        await self.rate_limiter.wait()
        
        city = location or self.city
        category_code = self.CATEGORIES.get(category, "sss")
        
        # Build search URL
        search_url = f"{self.BASE_URL.format(city=city)}{self.SEARCH_PATH.format(category=category_code)}"
        params = {
            "query": query,
            "max_price": int(max_price),
            "sort": "date",  # Sort by newest first
            "searchNearby": 1  # Include nearby areas
        }
        
        try:
            response = await self.client.get(search_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            products = []
            
            # Parse search results
            for item in soup.select("li.result-row"):
                try:
                    product = self._parse_listing(item, city)
                    if product and product.price <= max_price:
                        products.append(product)
                except Exception as e:
                    self.logger.warning(f"Failed to parse listing: {e}")
                    continue
            
            return products
            
        except httpx.HTTPError as e:
            self.logger.error(f"Craigslist search failed: {e}")
            return []
    
    def _parse_listing(self, item: BeautifulSoup, city: str) -> Optional[Product]:
        """Parse a single Craigslist listing."""
        
        # Extract title and URL
        title_elem = item.select_one("a.result-title")
        if not title_elem:
            return None
        
        title = title_elem.get_text(strip=True)
        url = title_elem["href"]
        
        # Make URL absolute if relative
        if url.startswith("/"):
            url = f"{self.BASE_URL.format(city=city)}{url}"
        
        # Extract price
        price_elem = item.select_one("span.result-price")
        if not price_elem:
            return None
        
        price_text = price_elem.get_text(strip=True).replace("$", "").replace(",", "")
        try:
            price = float(price_text)
        except ValueError:
            return None
        
        # Extract location
        location_elem = item.select_one("span.result-hood")
        location = location_elem.get_text(strip=True) if location_elem else city
        
        # Extract image
        image_elem = item.select_one("a.result-image")
        image_url = image_elem["data-ids"].split(",")[0].split(":")[1] if image_elem and "data-ids" in image_elem.attrs else None
        if image_url:
            image_url = f"https://images.craigslist.org/{image_url}_300x300.jpg"
        
        # Extract posting date
        time_elem = item.select_one("time.result-date")
        posted_date = datetime.fromisoformat(time_elem["datetime"]) if time_elem else None
        
        return Product(
            title=title,
            price=price,
            url=url,
            image_url=image_url,
            platform="craigslist",
            location=location,
            posted_date=posted_date
        )
    
    async def get_product_details(self, url: str) -> Optional[Product]:
        """Fetch detailed information for a specific listing."""
        await self.rate_limiter.wait()
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract description
            description_elem = soup.select_one("#postingbody")
            description = description_elem.get_text(strip=True) if description_elem else None
            
            # Extract additional images
            image_elems = soup.select("div.slide img")
            images = [img["src"] for img in image_elems if "src" in img.attrs]
            
            return {
                "description": description,
                "images": images
            }
            
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to fetch product details: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if Craigslist is accessible."""
        try:
            response = httpx.get(
                self.BASE_URL.format(city=self.city),
                timeout=5.0
            )
            return response.status_code == 200
        except:
            return False
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
```

### 2. Facebook Marketplace Scraper

**Implementation Strategy:**
- Use Selenium with headless Chrome
- Handle JavaScript-rendered content
- Implement stealth techniques to avoid detection
- Location-based search

**Code Structure:**

```python
# backend/app/scrapers/facebook_marketplace.py

import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import List, Optional
from datetime import datetime
from .base import BaseScraper
from ..models.product import Product
from ..utils.rate_limiter import RateLimiter

class FacebookMarketplaceScraper(BaseScraper):
    """
    Facebook Marketplace scraper using Selenium.
    
    URL Structure:
    https://www.facebook.com/marketplace/{location}/search?query={query}&maxPrice={price}
    
    Note: Facebook Marketplace requires JavaScript rendering, so we use Selenium.
    """
    
    BASE_URL = "https://www.facebook.com/marketplace"
    
    def __init__(self):
        self.rate_limiter = RateLimiter(requests_per_minute=5)
        self.driver = None
    
    def _init_driver(self):
        """Initialize Selenium WebDriver with stealth options."""
        if self.driver:
            return
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
        
        # Stealth options
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Execute stealth JavaScript
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
    
    async def search(
        self,
        query: str,
        max_price: float,
        location: Optional[str] = None,
        category: str = "general"
    ) -> List[Product]:
        """
        Search Facebook Marketplace for products.
        
        Args:
            query: Search query
            max_price: Maximum price
            location: Location code (e.g., "boston")
            category: Product category
            
        Returns:
            List of Product objects
        """
        await self.rate_limiter.wait()
        
        self._init_driver()
        
        # Build search URL
        location_code = location or "boston"
        search_url = f"{self.BASE_URL}/{location_code}/search"
        params = f"?query={query.replace(' ', '%20')}&maxPrice={int(max_price)}&sortBy=creation_time_descend"
        
        try:
            self.driver.get(search_url + params)
            
            # Wait for listings to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='marketplace_feed']"))
            )
            
            # Scroll to load more items
            self._scroll_page(3)
            
            # Parse listings
            products = []
            listing_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/marketplace/item/']")
            
            for elem in listing_elements[:20]:  # Limit to first 20 results
                try:
                    product = self._parse_listing(elem)
                    if product and product.price <= max_price:
                        products.append(product)
                except Exception as e:
                    self.logger.warning(f"Failed to parse Facebook listing: {e}")
                    continue
            
            return products
            
        except TimeoutException:
            self.logger.error("Facebook Marketplace search timed out")
            return []
        except Exception as e:
            self.logger.error(f"Facebook Marketplace search failed: {e}")
            return []
    
    def _scroll_page(self, times: int = 3):
        """Scroll page to load more content."""
        for _ in range(times):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            asyncio.sleep(1)
    
    def _parse_listing(self, element) -> Optional[Product]:
        """Parse a single Facebook Marketplace listing."""
        try:
            # Extract URL
            url = element.get_attribute("href")
            
            # Extract title
            title_elem = element.find_element(By.CSS_SELECTOR, "span[dir='auto']")
            title = title_elem.text if title_elem else None
            
            # Extract price
            price_elem = element.find_element(By.CSS_SELECTOR, "span[dir='auto']")
            price_text = price_elem.text.replace("$", "").replace(",", "")
            try:
                price = float(price_text)
            except ValueError:
                return None
            
            # Extract image
            img_elem = element.find_element(By.TAG_NAME, "img")
            image_url = img_elem.get_attribute("src") if img_elem else None
            
            # Extract location (if available)
            try:
                location_elem = element.find_element(By.CSS_SELECTOR, "span[class*='location']")
                location = location_elem.text
            except NoSuchElementException:
                location = None
            
            return Product(
                title=title,
                price=price,
                url=url,
                image_url=image_url,
                platform="facebook_marketplace",
                location=location,
                posted_date=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to parse Facebook listing element: {e}")
            return None
    
    async def get_product_details(self, url: str) -> Optional[dict]:
        """Fetch detailed information for a specific listing."""
        await self.rate_limiter.wait()
        
        try:
            self.driver.get(url)
            
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='marketplace_pdp']")))
            
            # Extract description
            try:
                desc_elem = self.driver.find_element(By.CSS_SELECTOR, "div[data-testid='product_description']")
                description = desc_elem.text
            except NoSuchElementException:
                description = None
            
            return {"description": description}
            
        except Exception as e:
            self.logger.error(f"Failed to fetch Facebook product details: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if Facebook Marketplace is accessible."""
        try:
            self._init_driver()
            self.driver.get(self.BASE_URL)
            return "marketplace" in self.driver.current_url.lower()
        except:
            return False
    
    async def close(self):
        """Close Selenium driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
```

### 3. eBay Scraper

**Implementation Strategy:**
- Use BeautifulSoup4 for HTML parsing
- Support Buy It Now and auction listings
- Advanced search filters
- No API key required

**Code Structure:**

```python
# backend/app/scrapers/ebay.py

import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime
from urllib.parse import urlencode
from .base import BaseScraper
from ..models.product import Product
from ..utils.rate_limiter import RateLimiter

class EbayScraper(BaseScraper):
    """
    eBay scraper implementation.
    
    URL Structure:
    https://www.ebay.com/sch/i.html?_nkw={query}&_udhi={max_price}&LH_BIN=1
    
    Parameters:
    - _nkw: Search keywords
    - _udhi: Maximum price
    - LH_BIN: Buy It Now only (1=yes)
    - _sop: Sort order (12=newest)
    """
    
    BASE_URL = "https://www.ebay.com"
    SEARCH_PATH = "/sch/i.html"
    
    def __init__(self):
        self.rate_limiter = RateLimiter(requests_per_minute=10)
        self.client = httpx.AsyncClient(
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            },
            timeout=30.0,
            follow_redirects=True
        )
    
    async def search(
        self,
        query: str,
        max_price: float,
        location: Optional[str] = None,
        category: str = "general"
    ) -> List[Product]:
        """
        Search eBay for products matching criteria.
        
        Args:
            query: Search query
            max_price: Maximum price
            location: Not used for eBay (searches globally)
            category: Product category
            
        Returns:
            List of Product objects
        """
        await self.rate_limiter.wait()
        
        # Build search parameters
        params = {
            "_nkw": query,
            "_udhi": int(max_price),
            "LH_BIN": 1,  # Buy It Now only
            "_sop": 12,   # Sort by newest
            "rt": "nc",   # New condition
            "_ipg": 50    # Items per page
        }
        
        search_url = f"{self.BASE_URL}{self.SEARCH_PATH}?{urlencode(params)}"
        
        try:
            response = await self.client.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            products = []
            
            # Parse search results
            for item in soup.select("li.s-item"):
                try:
                    product = self._parse_listing(item)
                    if product and product.price <= max_price:
                        products.append(product)
                except Exception as e:
                    self.logger.warning(f"Failed to parse eBay listing: {e}")
                    continue
            
            return products
            
        except httpx.HTTPError as e:
            self.logger.error(f"eBay search failed: {e}")
            return []
    
    def _parse_listing(self, item: BeautifulSoup) -> Optional[Product]:
        """Parse a single eBay listing."""
        
        # Extract title and URL
        title_elem = item.select_one("h3.s-item__title")
        link_elem = item.select_one("a.s-item__link")
        
        if not title_elem or not link_elem:
            return None
        
        title = title_elem.get_text(strip=True)
        url = link_elem["href"]
        
        # Skip ads
        if "Shop on eBay" in title:
            return None
        
        # Extract price
        price_elem = item.select_one("span.s-item__price")
        if not price_elem:
            return None
        
        price_text = price_elem.get_text(strip=True)
        # Handle price ranges (take the lower price)
        if "to" in price_text:
            price_text = price_text.split("to")[0]
        
        price_text = price_text.replace("$", "").replace(",", "").strip()
        try:
            price = float(price_text)
        except ValueError:
            return None
        
        # Extract image
        img_elem = item.select_one("img.s-item__image-img")
        image_url = img_elem["src"] if img_elem and "src" in img_elem.attrs else None
        
        # Extract location
        location_elem = item.select_one("span.s-item__location")
        location = location_elem.get_text(strip=True) if location_elem else None
        
        # Extract condition
        condition_elem = item.select_one("span.SECONDARY_INFO")
        condition = condition_elem.get_text(strip=True) if condition_elem else "Used"
        
        return Product(
            title=title,
            price=price,
            url=url,
            image_url=image_url,
            platform="ebay",
            location=location,
            posted_date=datetime.utcnow(),
            description=f"Condition: {condition}"
        )
    
    async def get_product_details(self, url: str) -> Optional[dict]:
        """Fetch detailed information for a specific listing."""
        await self.rate_limiter.wait()
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract description
            desc_elem = soup.select_one("div.d-item-description")
            description = desc_elem.get_text(strip=True) if desc_elem else None
            
            # Extract additional images
            image_elems = soup.select("img.img-fluid")
            images = [img["src"] for img in image_elems if "src" in img.attrs]
            
            # Extract seller info
            seller_elem = soup.select_one("span.ux-textspans--BOLD")
            seller = seller_elem.get_text(strip=True) if seller_elem else None
            
            return {
                "description": description,
                "images": images,
                "seller": seller
            }
            
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to fetch eBay product details: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if eBay is accessible."""
        try:
            response = httpx.get(self.BASE_URL, timeout=5.0)
            return response.status_code == 200
        except:
            return False
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
```

---

## Configuration Templates

### Environment Variables (.env.example)

```bash
# Application Settings
APP_NAME=Product Search Agent
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=1

# Database
DATABASE_URL=sqlite:///./product_search.db
DATABASE_ECHO=false

# Redis (Optional - for caching)
REDIS_URL=redis://localhost:6379/0
REDIS_ENABLED=false

# Search Configuration
SEARCH_INTERVAL_HOURS=2
MAX_CONCURRENT_SEARCHES=5
MATCH_THRESHOLD_DEFAULT=70.0
MAX_RESULTS_PER_PLATFORM=20

# Scraper Settings
CRAIGSLIST_DEFAULT_CITY=boston
CRAIGSLIST_RATE_LIMIT=10
FACEBOOK_RATE_LIMIT=5
EBAY_RATE_LIMIT=10

# Selenium Configuration (for Facebook)
SELENIUM_HEADLESS=true
SELENIUM_TIMEOUT=30

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_ALLOW_CREDENTIALS=true

# WebSocket
WEBSOCKET_HEARTBEAT_INTERVAL=30

# Notification Settings
ENABLE_EMAIL_NOTIFICATIONS=false
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Deployment
ENVIRONMENT=production
SENTRY_DSN=
```

### Requirements Files

**requirements.txt:**
```txt
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
alembic==1.12.1
aiosqlite==0.19.0

# HTTP Clients
httpx==0.25.1
requests==2.31.0

# Web Scraping
beautifulsoup4==4.12.2
lxml==4.9.3
selenium==4.15.2
webdriver-manager==4.0.1

# Task Scheduling
apscheduler==3.10.4

# Text Processing
rapidfuzz==3.5.2
spacy==3.7.2

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Redis (Optional)
redis==5.0.1
hiredis==2.2.3

# Logging
structlog==23.2.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx-mock==0.10.0
```

**requirements-dev.txt:**
```txt
-r requirements.txt

# Development Tools
black==23.11.0
flake8==6.1.0
mypy==1.7.1
isort==5.12.0
pre-commit==3.5.0

# Testing
pytest-watch==4.2.0
faker==20.1.0

# Documentation
mkdocs==1.5.3
mkdocs-material==9.4.14
```

---

## Docker Configuration

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome and ChromeDriver for Selenium
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY ./app ./app

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:////app/data/product_search.db
      - REDIS_URL=redis://redis:6379/0
      - REDIS_ENABLED=true
    volumes:
      - ./backend/app:/app/app
      - ./data:/app/data
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
      - VITE_WS_URL=ws://localhost:8000
    volumes:
      - ./frontend/src:/app/src
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  redis_data:
```

---

## Setup Instructions

### Local Development Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd product-search-agent

# 2. Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Download spaCy model
python -m spacy download en_core_web_sm

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 5. Initialize database
alembic upgrade head

# 6. Run backend
uvicorn app.main:app --reload

# 7. Set up frontend (in new terminal)
cd ../frontend
npm install
npm run dev

# 8. Access application
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Frontend: http://localhost:3000
```

### Docker Setup

```bash
# 1. Build and run with Docker Compose
docker-compose up --build

# 2. Access application
# Backend API: http://localhost:8000
# Frontend: http://localhost:3000

# 3. View logs
docker-compose logs -f

# 4. Stop services
docker-compose down
```

### Cloud Deployment (Render.com)

```bash
# 1. Create render.yaml in project root
# 2. Connect GitHub repository to Render
# 3. Render will auto-deploy on push to main branch
# 4. Set environment variables in Render dashboard
```

---

## Testing Strategy

### Unit Tests

```python
# backend/app/tests/test_scrapers.py

import pytest
from app.scrapers.craigslist import CraigslistScraper

@pytest.mark.asyncio
async def test_craigslist_search():
    scraper = CraigslistScraper(city="boston")
    products = await scraper.search(
        query="toyota camry",
        max_price=6000
    )
    
    assert isinstance(products, list)
    assert all(p.price <= 6000 for p in products)
    assert all(p.platform == "craigslist" for p in products)
    
    await scraper.close()

@pytest.mark.asyncio
async def test_craigslist_availability():
    scraper = CraigslistScraper()
    assert scraper.is_available() == True
```

### Integration Tests

```python
# backend/app/tests/test_api.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_search_request():
    response = client.post(
        "/api/search-requests",
        json={
            "product_name": "Toyota Camry",
            "product_description": "2015 model",
            "budget": 6000,
            "location": "boston"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["product_name"] == "Toyota Camry"
    assert data["budget"] == 6000
```

---

This implementation guide provides all the necessary details to build the agentic product search system. Each scraper is designed to be modular, maintainable, and follows best practices for web scraping.