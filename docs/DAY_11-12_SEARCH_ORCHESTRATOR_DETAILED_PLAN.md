# Day 11-12: Search Orchestrator - Detailed Implementation Plan

**Total Time:** 10 hours  
**Difficulty:** Intermediate  
**Prerequisites:** Completed Day 9-10 (Matching Engine), All scrapers working

---

## 📋 Overview

The **Search Orchestrator** is the "conductor" of your product search system. It coordinates all the scrapers, manages the search workflow, integrates the matching engine, and saves results to the database. Think of it as the brain that brings everything together!

### What You'll Build
- A central orchestrator that runs searches across multiple platforms
- Error handling and retry logic for robust operation
- Database integration to persist search results
- Integration tests to ensure everything works together

---

## 🎯 Learning Objectives

By the end of Day 11-12, you will understand:
1. **Orchestration Pattern** - How to coordinate multiple services
2. **Error Handling** - Graceful failure and retry mechanisms
3. **Async Programming** - Running multiple scrapers concurrently
4. **Integration Testing** - Testing components working together

---

## 🏗️ Design Patterns Used

### 1. **Orchestrator Pattern (Coordinator Pattern)**
**What it is:** A central component that coordinates the workflow of multiple services.

**Why we use it:** 
- Keeps business logic in one place
- Makes it easy to add/remove scrapers
- Simplifies error handling and monitoring

**Example:**
```python
# Instead of calling scrapers directly everywhere:
# ❌ Bad approach
craigslist_results = craigslist_scraper.search()
ebay_results = ebay_scraper.search()
facebook_results = facebook_scraper.search()

# ✅ Good approach - Orchestrator handles it
orchestrator = SearchOrchestrator()
all_results = orchestrator.execute_search(search_request)
```

### 2. **Strategy Pattern**
**What it is:** Selecting different algorithms (scrapers) at runtime.

**Why we use it:**
- Each platform has its own scraper implementation
- Easy to add new platforms without changing orchestrator code

### 3. **Repository Pattern**
**What it is:** Abstracting database operations.

**Why we use it:**
- Separates business logic from data access
- Makes testing easier (can mock database)

---

## 📅 Day-by-Day Breakdown

### **Day 11: Core Orchestrator (6 hours)**

#### **Morning Session (3 hours): Basic Structure**

##### **Sub-task 1.1: Create Orchestrator File Structure (30 min)**

**What to do:**
1. Create `backend/app/core/orchestrator.py`
2. Set up basic class structure
3. Import necessary dependencies

**Code Template:**
```python
"""
Search Orchestrator - Coordinates multi-platform product searches
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio
import logging

from app.models.search_request import SearchRequest
from app.models.product import Product
from app.models.search_execution import SearchExecution
from app.scrapers.craigslist import CraigslistScraper
from app.scrapers.ebay import EbayScraper
from app.scrapers.facebook_marketplace import FacebookMarketplaceScraper
from app.core.matching import MatchingEngine

logger = logging.getLogger(__name__)


class SearchOrchestrator:
    """
    Orchestrates product searches across multiple platforms.
    
    Responsibilities:
    - Coordinate scraper execution
    - Integrate matching engine
    - Save results to database
    - Handle errors and retries
    """
    
    def __init__(self, db: Session):
        """Initialize orchestrator with database session."""
        self.db = db
        self.matching_engine = MatchingEngine()
        
        # Initialize scrapers
        self.scrapers = {
            'craigslist': CraigslistScraper(),
            'ebay': EbayScraper(),
            'facebook': FacebookMarketplaceScraper()
        }
        
    # Methods will be added in next sub-tasks
```

**Deliverable:** Basic orchestrator file with imports and class structure

---

##### **Sub-task 1.2: Implement execute_search() Method (1 hour)**

**What to do:**
Create the main method that runs a complete search workflow.

**Step-by-step:**
1. Create search execution record
2. Get active platforms from search request
3. Search each platform
4. Collect all results
5. Update execution status

**Code to Add:**
```python
async def execute_search(self, search_request: SearchRequest) -> SearchExecution:
    """
    Execute a complete search across all enabled platforms.
    
    Args:
        search_request: The search request to execute
        
    Returns:
        SearchExecution: Record of the search execution
        
    Workflow:
    1. Create execution record
    2. Search each platform
    3. Match products against criteria
    4. Save results to database
    5. Update execution status
    """
    logger.info(f"Starting search execution for request {search_request.id}")
    
    # Step 1: Create execution record
    execution = SearchExecution(
        search_request_id=search_request.id,
        status='running',
        started_at=datetime.utcnow()
    )
    self.db.add(execution)
    self.db.commit()
    
    try:
        # Step 2: Get platforms to search
        platforms = self._get_active_platforms(search_request)
        
        # Step 3: Search all platforms concurrently
        all_products = await self._search_all_platforms(
            search_request, 
            platforms
        )
        
        # Step 4: Match products against criteria
        matched_products = self._match_products(
            search_request, 
            all_products
        )
        
        # Step 5: Save results to database
        self._save_products(matched_products, execution.id)
        
        # Step 6: Update execution status
        execution.status = 'completed'
        execution.completed_at = datetime.utcnow()
        execution.products_found = len(matched_products)
        
        logger.info(
            f"Search execution {execution.id} completed. "
            f"Found {len(matched_products)} matching products"
        )
        
    except Exception as e:
        logger.error(f"Search execution {execution.id} failed: {str(e)}")
        execution.status = 'failed'
        execution.error_message = str(e)
        execution.completed_at = datetime.utcnow()
        
    finally:
        self.db.commit()
        
    return execution
```

**Key Concepts Explained:**
- **async/await**: Allows running scrapers concurrently (faster!)
- **try/except/finally**: Ensures database is updated even if errors occur
- **Logging**: Helps debug issues in production

**Deliverable:** Working execute_search() method

---

##### **Sub-task 1.3: Implement Helper Methods (1.5 hours)**

**What to do:**
Create supporting methods that execute_search() uses.

**Method 1: _get_active_platforms()**
```python
def _get_active_platforms(self, search_request: SearchRequest) -> List[str]:
    """
    Get list of platforms to search based on search request settings.
    
    Args:
        search_request: The search request
        
    Returns:
        List of platform names to search
    """
    platforms = []
    
    # Check which platforms are enabled
    if search_request.search_craigslist:
        platforms.append('craigslist')
    if search_request.search_ebay:
        platforms.append('ebay')
    if search_request.search_facebook:
        platforms.append('facebook')
        
    logger.info(f"Active platforms for search {search_request.id}: {platforms}")
    return platforms
```

**Method 2: _search_all_platforms()**
```python
async def _search_all_platforms(
    self, 
    search_request: SearchRequest, 
    platforms: List[str]
) -> List[Dict]:
    """
    Search all platforms concurrently.
    
    Args:
        search_request: The search request
        platforms: List of platform names to search
        
    Returns:
        List of all products found across platforms
    """
    # Create search tasks for each platform
    tasks = [
        self._search_platform(search_request, platform)
        for platform in platforms
    ]
    
    # Run all searches concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Flatten results and filter out errors
    all_products = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(
                f"Platform {platforms[i]} search failed: {str(result)}"
            )
        else:
            all_products.extend(result)
            
    logger.info(f"Total products found across all platforms: {len(all_products)}")
    return all_products
```

**Method 3: _search_platform()**
```python
async def _search_platform(
    self, 
    search_request: SearchRequest, 
    platform: str
) -> List[Dict]:
    """
    Search a single platform with retry logic.
    
    Args:
        search_request: The search request
        platform: Platform name ('craigslist', 'ebay', 'facebook')
        
    Returns:
        List of products found on this platform
    """
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(
                f"Searching {platform} (attempt {attempt + 1}/{max_retries})"
            )
            
            # Get the appropriate scraper
            scraper = self.scrapers[platform]
            
            # Execute search
            products = await scraper.search(
                query=search_request.product_name,
                location=search_request.location,
                max_price=search_request.max_price,
                min_price=search_request.min_price
            )
            
            logger.info(f"Found {len(products)} products on {platform}")
            return products
            
        except Exception as e:
            logger.warning(
                f"Attempt {attempt + 1} failed for {platform}: {str(e)}"
            )
            
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"All retries exhausted for {platform}")
                raise
                
    return []
```

**Key Concepts:**
- **asyncio.gather()**: Runs multiple async functions concurrently
- **Retry logic**: Automatically retries failed searches
- **Error isolation**: One platform failing doesn't stop others

**Deliverable:** All helper methods implemented

---

#### **Afternoon Session (3 hours): Matching & Database Integration**

##### **Sub-task 1.4: Integrate Matching Engine (1 hour)**

**What to do:**
Use the matching engine from Day 9-10 to filter products.

**Code to Add:**
```python
def _match_products(
    self, 
    search_request: SearchRequest, 
    products: List[Dict]
) -> List[Dict]:
    """
    Match products against search criteria using matching engine.
    
    Args:
        search_request: The search request with criteria
        products: List of products to match
        
    Returns:
        List of products that match criteria (with match scores)
    """
    logger.info(f"Matching {len(products)} products against criteria")
    
    # Use matching engine to score products
    matched_products = self.matching_engine.match_products(
        products=products,
        search_criteria={
            'product_name': search_request.product_name,
            'description': search_request.description,
            'max_price': search_request.max_price,
            'min_price': search_request.min_price,
            'keywords': search_request.keywords
        },
        min_score=search_request.min_match_score or 0.7
    )
    
    logger.info(
        f"Found {len(matched_products)} products above match threshold"
    )
    
    return matched_products
```

**Deliverable:** Matching engine integrated

---

##### **Sub-task 1.5: Implement Database Persistence (1.5 hours)**

**What to do:**
Save matched products to the database.

**Code to Add:**
```python
def _save_products(
    self, 
    products: List[Dict], 
    execution_id: int
) -> None:
    """
    Save matched products to database.
    
    Args:
        products: List of matched products
        execution_id: ID of the search execution
    """
    logger.info(f"Saving {len(products)} products to database")
    
    for product_data in products:
        # Check if product already exists (duplicate detection)
        existing_product = self.db.query(Product).filter(
            Product.external_id == product_data['external_id'],
            Product.platform == product_data['platform']
        ).first()
        
        if existing_product:
            # Update existing product
            existing_product.price = product_data['price']
            existing_product.is_available = product_data['is_available']
            existing_product.last_seen = datetime.utcnow()
            existing_product.match_score = product_data.get('match_score')
            logger.debug(f"Updated existing product {existing_product.id}")
        else:
            # Create new product
            new_product = Product(
                search_execution_id=execution_id,
                platform=product_data['platform'],
                external_id=product_data['external_id'],
                title=product_data['title'],
                description=product_data.get('description'),
                price=product_data['price'],
                url=product_data['url'],
                image_url=product_data.get('image_url'),
                location=product_data.get('location'),
                posted_date=product_data.get('posted_date'),
                is_available=product_data.get('is_available', True),
                match_score=product_data.get('match_score'),
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow()
            )
            self.db.add(new_product)
            logger.debug(f"Created new product: {new_product.title}")
    
    self.db.commit()
    logger.info("All products saved successfully")
```

**Key Concepts:**
- **Duplicate detection**: Prevents saving the same product twice
- **Update vs Insert**: Updates existing products, inserts new ones
- **Timestamps**: Tracks when products were first/last seen

**Deliverable:** Database persistence working

---

##### **Sub-task 1.6: Add Error Handling & Logging (30 min)**

**What to do:**
Improve error messages and logging throughout the orchestrator.

**Best Practices:**
```python
# At the top of each method, log what's happening
logger.info(f"Starting operation X with parameters Y")

# Log important milestones
logger.info(f"Completed step 1, found {count} items")

# Log warnings for recoverable errors
logger.warning(f"Retry attempt {attempt} failed, retrying...")

# Log errors for serious issues
logger.error(f"Critical failure: {str(e)}", exc_info=True)

# Log debug info for troubleshooting
logger.debug(f"Detailed state: {some_variable}")
```

**Deliverable:** Comprehensive logging added

---

### **Day 12: Testing & Integration (4 hours)**

#### **Morning Session (2 hours): Unit Tests**

##### **Sub-task 2.1: Create Test File (15 min)**

**What to do:**
Create `backend/app/tests/test_orchestrator.py`

**Template:**
```python
"""
Tests for Search Orchestrator
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.core.orchestrator import SearchOrchestrator
from app.models.search_request import SearchRequest
from app.models.search_execution import SearchExecution


@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock()


@pytest.fixture
def sample_search_request():
    """Sample search request for testing."""
    return SearchRequest(
        id=1,
        product_name="iPhone 13",
        description="Good condition",
        max_price=500.0,
        location="Boston, MA",
        search_craigslist=True,
        search_ebay=True,
        search_facebook=False
    )


@pytest.fixture
def orchestrator(mock_db):
    """Create orchestrator instance."""
    return SearchOrchestrator(mock_db)
```

---

##### **Sub-task 2.2: Test Platform Selection (30 min)**

**What to do:**
Test that the orchestrator correctly identifies which platforms to search.

**Test Code:**
```python
def test_get_active_platforms_all_enabled(orchestrator, sample_search_request):
    """Test getting platforms when all are enabled."""
    sample_search_request.search_craigslist = True
    sample_search_request.search_ebay = True
    sample_search_request.search_facebook = True
    
    platforms = orchestrator._get_active_platforms(sample_search_request)
    
    assert len(platforms) == 3
    assert 'craigslist' in platforms
    assert 'ebay' in platforms
    assert 'facebook' in platforms


def test_get_active_platforms_partial(orchestrator, sample_search_request):
    """Test getting platforms when only some are enabled."""
    sample_search_request.search_craigslist = True
    sample_search_request.search_ebay = False
    sample_search_request.search_facebook = True
    
    platforms = orchestrator._get_active_platforms(sample_search_request)
    
    assert len(platforms) == 2
    assert 'craigslist' in platforms
    assert 'facebook' in platforms
    assert 'ebay' not in platforms
```

---

##### **Sub-task 2.3: Test Search Execution (1 hour)**

**What to do:**
Test the main execute_search() method with mocked scrapers.

**Test Code:**
```python
@pytest.mark.asyncio
async def test_execute_search_success(orchestrator, sample_search_request, mock_db):
    """Test successful search execution."""
    # Mock scraper responses
    mock_products = [
        {
            'platform': 'craigslist',
            'external_id': 'cl123',
            'title': 'iPhone 13 Pro',
            'price': 450.0,
            'url': 'https://example.com/1'
        },
        {
            'platform': 'ebay',
            'external_id': 'eb456',
            'title': 'iPhone 13',
            'price': 480.0,
            'url': 'https://example.com/2'
        }
    ]
    
    # Mock the scraper methods
    with patch.object(
        orchestrator, 
        '_search_all_platforms', 
        new=AsyncMock(return_value=mock_products)
    ):
        with patch.object(
            orchestrator, 
            '_match_products', 
            return_value=mock_products
        ):
            with patch.object(orchestrator, '_save_products'):
                execution = await orchestrator.execute_search(sample_search_request)
    
    # Verify execution was created and completed
    assert execution.status == 'completed'
    assert execution.products_found == 2


@pytest.mark.asyncio
async def test_execute_search_with_error(orchestrator, sample_search_request, mock_db):
    """Test search execution handles errors gracefully."""
    # Mock a scraper failure
    with patch.object(
        orchestrator, 
        '_search_all_platforms', 
        new=AsyncMock(side_effect=Exception("Scraper failed"))
    ):
        execution = await orchestrator.execute_search(sample_search_request)
    
    # Verify execution failed gracefully
    assert execution.status == 'failed'
    assert 'Scraper failed' in execution.error_message
```

---

##### **Sub-task 2.4: Test Retry Logic (15 min)**

**What to do:**
Test that platform searches retry on failure.

**Test Code:**
```python
@pytest.mark.asyncio
async def test_search_platform_retries_on_failure(orchestrator, sample_search_request):
    """Test that platform search retries on failure."""
    # Mock scraper that fails twice then succeeds
    mock_scraper = Mock()
    mock_scraper.search = AsyncMock(
        side_effect=[
            Exception("Network error"),
            Exception("Timeout"),
            [{'title': 'Product 1'}]  # Success on third try
        ]
    )
    
    orchestrator.scrapers['craigslist'] = mock_scraper
    
    # Execute search
    results = await orchestrator._search_platform(
        sample_search_request, 
        'craigslist'
    )
    
    # Verify it retried and eventually succeeded
    assert len(results) == 1
    assert mock_scraper.search.call_count == 3
```

---

#### **Afternoon Session (2 hours): Integration Tests**

##### **Sub-task 2.5: End-to-End Integration Test (1.5 hours)**

**What to do:**
Test the complete workflow with real database and scrapers.

**Test Code:**
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_search_workflow(db_session):
    """
    Integration test: Complete search workflow.
    
    This test:
    1. Creates a search request
    2. Runs orchestrator
    3. Verifies products are saved to database
    4. Checks execution record
    """
    # Step 1: Create search request
    search_request = SearchRequest(
        product_name="Test Product",
        max_price=100.0,
        location="Test City",
        search_craigslist=True,
        search_ebay=False,
        search_facebook=False
    )
    db_session.add(search_request)
    db_session.commit()
    
    # Step 2: Run orchestrator
    orchestrator = SearchOrchestrator(db_session)
    execution = await orchestrator.execute_search(search_request)
    
    # Step 3: Verify execution completed
    assert execution.status == 'completed'
    assert execution.products_found > 0
    
    # Step 4: Verify products were saved
    products = db_session.query(Product).filter(
        Product.search_execution_id == execution.id
    ).all()
    
    assert len(products) == execution.products_found
    
    # Step 5: Verify product data
    for product in products:
        assert product.title is not None
        assert product.price > 0
        assert product.url is not None
        assert product.platform in ['craigslist', 'ebay', 'facebook']
```

**Note:** This test requires scrapers to be working. You may want to use test data or mock external calls.

---

##### **Sub-task 2.6: Test Database Persistence (30 min)**

**What to do:**
Test that products are correctly saved and updated.

**Test Code:**
```python
def test_save_products_creates_new(orchestrator, mock_db):
    """Test saving new products to database."""
    products = [
        {
            'platform': 'craigslist',
            'external_id': 'test123',
            'title': 'Test Product',
            'price': 50.0,
            'url': 'https://example.com',
            'is_available': True
        }
    ]
    
    # Mock database query to return no existing products
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    orchestrator._save_products(products, execution_id=1)
    
    # Verify product was added
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_save_products_updates_existing(orchestrator, mock_db):
    """Test updating existing products."""
    # Mock existing product
    existing_product = Mock()
    existing_product.price = 100.0
    mock_db.query.return_value.filter.return_value.first.return_value = existing_product
    
    products = [
        {
            'platform': 'craigslist',
            'external_id': 'test123',
            'title': 'Test Product',
            'price': 75.0,  # Price changed
            'url': 'https://example.com',
            'is_available': True
        }
    ]
    
    orchestrator._save_products(products, execution_id=1)
    
    # Verify product was updated, not added
    assert existing_product.price == 75.0
    mock_db.add.assert_not_called()
    mock_db.commit.assert_called_once()
```

---

## 🧪 Testing Checklist

Run these tests to verify everything works:

```bash
# Unit tests
pytest backend/app/tests/test_orchestrator.py -v

# Integration tests
pytest backend/app/tests/test_orchestrator.py -v -m integration

# Test coverage
pytest backend/app/tests/test_orchestrator.py --cov=app.core.orchestrator

# Run all tests
pytest backend/app/tests/ -v
```

---

## 📝 Code Quality Checklist

Before considering Day 11-12 complete:

- [ ] All methods have docstrings
- [ ] Error handling in place for all external calls
- [ ] Logging added at appropriate levels
- [ ] Type hints used for all parameters and returns
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] Code follows PEP 8 style guidelines
- [ ] No hardcoded values (use config)
- [ ] Database transactions properly handled
- [ ] Async/await used correctly

---

## 🐛 Common Issues & Solutions

### Issue 1: "RuntimeError: Event loop is closed"
**Solution:** Make sure you're using `@pytest.mark.asyncio` for async tests.

### Issue 2: Database locked errors
**Solution:** Use separate database sessions for tests, or use in-memory SQLite.

### Issue 3: Scrapers timing out
**Solution:** Increase timeout values or mock scraper responses in tests.

### Issue 4: Products not saving
**Solution:** Check that `db.commit()` is called and no exceptions are raised.

---

## 📚 Key Concepts Summary

### Orchestration Pattern
- **Purpose:** Coordinate multiple services
- **Benefits:** Centralized logic, easier maintenance
- **When to use:** Complex workflows with multiple steps

### Async Programming
- **async/await:** Non-blocking operations
- **asyncio.gather():** Run multiple tasks concurrently
- **Benefits:** Faster execution, better resource usage

### Error Handling
- **try/except/finally:** Ensure cleanup happens
- **Retry logic:** Automatically recover from transient failures
- **Logging:** Track what went wrong

### Database Patterns
- **Upsert:** Update if exists, insert if not
- **Transactions:** Group operations that should succeed/fail together
- **Timestamps:** Track when data was created/modified

---

## 🎯 Success Criteria

Day 11-12 is complete when:

1. ✅ Orchestrator can search multiple platforms concurrently
2. ✅ Matching engine is integrated and working
3. ✅ Products are saved to database correctly
4. ✅ Duplicate products are detected and updated
5. ✅ Error handling works (one platform failing doesn't stop others)
6. ✅ Retry logic functions properly
7. ✅ All unit tests pass
8. ✅ Integration tests pass
9. ✅ Code is well-documented
10. ✅ Logging provides useful information

---

## 🚀 Next Steps

After completing Day 11-12:
- **Day 13:** Implement scheduler to run searches automatically
- **Day 14-15:** Add WebSocket notifications for real-time updates
- **Day 16-17:** Implement email notification system

---

## 💡 Tips for Junior Developers

1. **Start Simple:** Get basic orchestration working before adding complexity
2. **Test Early:** Write tests as you go, not at the end
3. **Use Logging:** It's your best friend for debugging
4. **Read Error Messages:** They usually tell you exactly what's wrong
5. **Ask Questions:** If stuck for >30 minutes, seek help
6. **Commit Often:** Small, frequent commits are better than large ones
7. **Take Breaks:** Step away if frustrated; fresh eyes help

---

## 📖 Additional Resources

- [Async Python Tutorial](https://realpython.com/async-io-python/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)
- [Pytest Async Testing](https://pytest-asyncio.readthedocs.io/)
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging.html)

---

**Good luck with your implementation! 🎉**

Remember: The orchestrator is the heart of your system. Take your time to get it right!