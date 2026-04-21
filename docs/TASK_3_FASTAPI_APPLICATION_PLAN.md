# Task 3: FastAPI Application - Sub-Implementation Plan

## Overview
This document breaks down Day 3 (FastAPI Application) into manageable subtasks designed for junior developers. Each subtask builds on the previous one and includes clear objectives, code examples, and testing steps.

---

## Prerequisites
✅ Day 2 completed: Configuration, Database Models, and Pydantic Schemas ready
✅ Virtual environment activated
✅ Dependencies installed (FastAPI, Uvicorn)

---

## Day 3 Goal
Create a working FastAPI application with REST API endpoints for managing search requests and products.

**Estimated Time:** 6 hours
**Difficulty:** Medium

---

## Subtask Breakdown

### Subtask 3.1: Create Basic FastAPI App (30 minutes)
**File:** `backend/app/main.py`

**Objective:** Set up the basic FastAPI application structure with a health check endpoint.

**What You'll Learn:**
- FastAPI application initialization
- Basic routing
- Running the development server
- Testing endpoints with curl/browser

**Steps:**
1. Create `backend/app/main.py`
2. Import FastAPI
3. Create app instance
4. Add health check endpoint
5. Configure CORS (for frontend)
6. Add startup/shutdown events

**Code Template:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="Product Search Agent API",
    description="API for automated product search across multiple platforms",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify API is running."""
    return {
        "status": "healthy",
        "message": "Product Search Agent API is running"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Product Search Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }
```

**Testing:**
```bash
# Start the server
cd backend
uvicorn app.main:app --reload

# Test in browser or with curl
curl http://localhost:8000/api/health
curl http://localhost:8000/

# View auto-generated docs
# Open browser: http://localhost:8000/docs
```

**Success Criteria:**
- ✅ Server starts without errors
- ✅ Health check returns 200 OK
- ✅ Swagger docs accessible at /docs
- ✅ Root endpoint returns API info

---

### Subtask 3.2: Create Database Dependency (20 minutes)
**File:** `backend/app/api/dependencies.py`

**Objective:** Create a dependency function to provide database sessions to route handlers.

**What You'll Learn:**
- FastAPI dependency injection
- Database session management
- Context managers with yield

**Steps:**
1. Create `backend/app/api/` directory
2. Create `dependencies.py` file
3. Import database session
4. Create get_db dependency function

**Code Template:**
```python
"""
FastAPI dependencies for database sessions and other shared resources.
"""

from typing import Generator
from sqlalchemy.orm import Session
from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that provides a database session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Testing:**
```python
# Test in Python REPL
from app.api.dependencies import get_db

# Get a database session
db_gen = get_db()
db = next(db_gen)
print(f"Database session: {db}")

# Clean up
try:
    next(db_gen)
except StopIteration:
    print("Session closed properly")
```

**Success Criteria:**
- ✅ Dependency function created
- ✅ Returns database session
- ✅ Properly closes session after use
- ✅ No import errors

---

### Subtask 3.3: Create Search Request Routes - Part 1 (GET endpoints) (45 minutes)
**File:** `backend/app/api/routes/search_requests.py`

**Objective:** Create GET endpoints to retrieve search requests.

**What You'll Learn:**
- FastAPI routing with APIRouter
- Database queries with SQLAlchemy
- Path parameters
- Query parameters
- Response models

**Endpoints to Create:**
- `GET /api/search-requests` - List all search requests
- `GET /api/search-requests/{id}` - Get single search request

**Steps:**
1. Create `backend/app/api/routes/` directory
2. Create `search_requests.py` file
3. Import necessary modules
4. Create APIRouter
5. Implement GET endpoints

**Code Template:**
```python
"""
API routes for search request management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db
from app.models import SearchRequest
from app.schemas import SearchRequestResponse, SearchRequestListResponse

# Create router
router = APIRouter(
    prefix="/api/search-requests",
    tags=["search-requests"]
)


@router.get("/", response_model=SearchRequestListResponse)
def list_search_requests(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List all search requests with pagination.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        SearchRequestListResponse: Paginated list of search requests
    """
    # Query database
    search_requests = db.query(SearchRequest).offset(skip).limit(limit).all()
    total = db.query(SearchRequest).count()
    
    return SearchRequestListResponse(
        items=search_requests,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/{search_request_id}", response_model=SearchRequestResponse)
def get_search_request(
    search_request_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a single search request by ID.
    
    Args:
        search_request_id: Unique identifier of the search request
        db: Database session
        
    Returns:
        SearchRequestResponse: Search request details
        
    Raises:
        HTTPException: 404 if search request not found
    """
    # Query database
    search_request = db.query(SearchRequest).filter(
        SearchRequest.id == search_request_id
    ).first()
    
    # Check if found
    if not search_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search request with id {search_request_id} not found"
        )
    
    return search_request
```

**Testing:**
```bash
# Start server
uvicorn app.main:app --reload

# Test endpoints (after creating some data)
curl http://localhost:8000/api/search-requests/
curl http://localhost:8000/api/search-requests/{id}

# Or use Swagger UI at http://localhost:8000/docs
```

**Success Criteria:**
- ✅ GET /api/search-requests returns list
- ✅ GET /api/search-requests/{id} returns single item
- ✅ 404 error for non-existent ID
- ✅ Pagination works correctly

---

### Subtask 3.4: Create Search Request Routes - Part 2 (POST endpoint) (45 minutes)
**File:** Update `backend/app/api/routes/search_requests.py`

**Objective:** Add POST endpoint to create new search requests.

**What You'll Learn:**
- Request body validation
- Creating database records
- Handling validation errors
- Returning created resources

**Endpoint to Create:**
- `POST /api/search-requests` - Create new search request

**Code to Add:**
```python
from app.schemas import SearchRequestCreate

@router.post("/", response_model=SearchRequestResponse, status_code=status.HTTP_201_CREATED)
def create_search_request(
    search_request: SearchRequestCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new search request.
    
    Args:
        search_request: Search request data from request body
        db: Database session
        
    Returns:
        SearchRequestResponse: Created search request
    """
    # Create database model from schema
    db_search_request = SearchRequest(
        product_name=search_request.product_name,
        product_description=search_request.product_description,
        budget=search_request.budget,
        location=search_request.location,
        match_threshold=search_request.match_threshold
    )
    
    # Add to database
    db.add(db_search_request)
    db.commit()
    db.refresh(db_search_request)
    
    return db_search_request
```

**Testing:**
```bash
# Test with curl
curl -X POST http://localhost:8000/api/search-requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "iPhone 13",
    "product_description": "Looking for iPhone 13 in good condition",
    "budget": 600.0,
    "location": "Boston, MA",
    "match_threshold": 75.0
  }'

# Or use Swagger UI for easier testing
```

**Success Criteria:**
- ✅ POST creates new search request
- ✅ Returns 201 Created status
- ✅ Validation errors return 422
- ✅ Created record has valid ID

---

### Subtask 3.5: Create Search Request Routes - Part 3 (PUT/DELETE endpoints) (45 minutes)
**File:** Update `backend/app/api/routes/search_requests.py`

**Objective:** Add PUT and DELETE endpoints for updating and deleting search requests.

**What You'll Learn:**
- Updating database records
- Deleting database records
- Partial updates
- Cascade deletes

**Endpoints to Create:**
- `PUT /api/search-requests/{id}` - Update search request
- `DELETE /api/search-requests/{id}` - Delete search request

**Code to Add:**
```python
from app.schemas import SearchRequestUpdate

@router.put("/{search_request_id}", response_model=SearchRequestResponse)
def update_search_request(
    search_request_id: str,
    search_request_update: SearchRequestUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing search request.
    
    Args:
        search_request_id: ID of search request to update
        search_request_update: Updated data (only provided fields will be updated)
        db: Database session
        
    Returns:
        SearchRequestResponse: Updated search request
        
    Raises:
        HTTPException: 404 if search request not found
    """
    # Find existing record
    db_search_request = db.query(SearchRequest).filter(
        SearchRequest.id == search_request_id
    ).first()
    
    if not db_search_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search request with id {search_request_id} not found"
        )
    
    # Update fields (only if provided)
    update_data = search_request_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_search_request, field, value)
    
    # Save changes
    db.commit()
    db.refresh(db_search_request)
    
    return db_search_request


@router.delete("/{search_request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_search_request(
    search_request_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a search request.
    
    Args:
        search_request_id: ID of search request to delete
        db: Database session
        
    Returns:
        None (204 No Content)
        
    Raises:
        HTTPException: 404 if search request not found
    """
    # Find existing record
    db_search_request = db.query(SearchRequest).filter(
        SearchRequest.id == search_request_id
    ).first()
    
    if not db_search_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search request with id {search_request_id} not found"
        )
    
    # Delete record
    db.delete(db_search_request)
    db.commit()
    
    return None
```

**Testing:**
```bash
# Update search request
curl -X PUT http://localhost:8000/api/search-requests/{id} \
  -H "Content-Type: application/json" \
  -d '{"budget": 700.0}'

# Delete search request
curl -X DELETE http://localhost:8000/api/search-requests/{id}
```

**Success Criteria:**
- ✅ PUT updates search request
- ✅ Partial updates work (only provided fields)
- ✅ DELETE removes search request
- ✅ Returns 404 for non-existent IDs

---

### Subtask 3.6: Create Search Request Routes - Part 4 (Action endpoints) (30 minutes)
**File:** Update `backend/app/api/routes/search_requests.py`

**Objective:** Add action endpoints for pausing and resuming searches.

**What You'll Learn:**
- Custom action endpoints
- Using model methods
- RESTful API design patterns

**Endpoints to Create:**
- `POST /api/search-requests/{id}/pause` - Pause search
- `POST /api/search-requests/{id}/resume` - Resume search

**Code to Add:**
```python
@router.post("/{search_request_id}/pause", response_model=SearchRequestResponse)
def pause_search_request(
    search_request_id: str,
    db: Session = Depends(get_db)
):
    """
    Pause an active search request.
    
    Args:
        search_request_id: ID of search request to pause
        db: Database session
        
    Returns:
        SearchRequestResponse: Updated search request
        
    Raises:
        HTTPException: 404 if search request not found
    """
    # Find existing record
    db_search_request = db.query(SearchRequest).filter(
        SearchRequest.id == search_request_id
    ).first()
    
    if not db_search_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search request with id {search_request_id} not found"
        )
    
    # Pause the search
    db_search_request.pause()
    db.commit()
    db.refresh(db_search_request)
    
    return db_search_request


@router.post("/{search_request_id}/resume", response_model=SearchRequestResponse)
def resume_search_request(
    search_request_id: str,
    db: Session = Depends(get_db)
):
    """
    Resume a paused search request.
    
    Args:
        search_request_id: ID of search request to resume
        db: Database session
        
    Returns:
        SearchRequestResponse: Updated search request
        
    Raises:
        HTTPException: 404 if search request not found
    """
    # Find existing record
    db_search_request = db.query(SearchRequest).filter(
        SearchRequest.id == search_request_id
    ).first()
    
    if not db_search_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search request with id {search_request_id} not found"
        )
    
    # Resume the search
    db_search_request.resume()
    db.commit()
    db.refresh(db_search_request)
    
    return db_search_request
```

**Testing:**
```bash
# Pause search
curl -X POST http://localhost:8000/api/search-requests/{id}/pause

# Resume search
curl -X POST http://localhost:8000/api/search-requests/{id}/resume
```

**Success Criteria:**
- ✅ POST /pause changes status to PAUSED
- ✅ POST /resume changes status to ACTIVE
- ✅ Returns updated search request
- ✅ 404 for non-existent IDs

---

### Subtask 3.7: Create Product Routes (45 minutes)
**File:** `backend/app/api/routes/products.py`

**Objective:** Create endpoints for retrieving products and matches.

**What You'll Learn:**
- Filtering with query parameters
- Complex database queries
- Ordering results

**Endpoints to Create:**
- `GET /api/products` - List all products
- `GET /api/products/matches` - List only matching products

**Code Template:**
```python
"""
API routes for product management.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api.dependencies import get_db
from app.models import Product
from app.schemas import ProductResponse, ProductListResponse

# Create router
router = APIRouter(
    prefix="/api/products",
    tags=["products"]
)


@router.get("/", response_model=ProductListResponse)
def list_products(
    skip: int = 0,
    limit: int = 50,
    platform: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    List all products with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        platform: Filter by platform (craigslist, facebook, ebay)
        min_price: Minimum price filter
        max_price: Maximum price filter
        db: Database session
        
    Returns:
        ProductListResponse: Paginated list of products
    """
    # Build query
    query = db.query(Product)
    
    # Apply filters
    if platform:
        query = query.filter(Product.platform == platform)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Get results
    products = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return ProductListResponse(
        items=products,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/matches", response_model=ProductListResponse)
def list_matching_products(
    skip: int = 0,
    limit: int = 50,
    min_score: float = Query(default=70.0, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """
    List only products that are matches.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        min_score: Minimum match score filter
        db: Database session
        
    Returns:
        ProductListResponse: Paginated list of matching products
    """
    # Query for matches only
    query = db.query(Product).filter(
        Product.is_match == True,
        Product.match_score >= min_score
    ).order_by(Product.match_score.desc())
    
    # Get results
    products = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return ProductListResponse(
        items=products,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )
```

**Testing:**
```bash
# List all products
curl http://localhost:8000/api/products/

# Filter by platform
curl "http://localhost:8000/api/products/?platform=craigslist"

# Filter by price range
curl "http://localhost:8000/api/products/?min_price=100&max_price=500"

# List matches only
curl http://localhost:8000/api/products/matches

# Filter matches by score
curl "http://localhost:8000/api/products/matches?min_score=80"
```

**Success Criteria:**
- ✅ GET /api/products returns all products
- ✅ Filtering by platform works
- ✅ Price range filtering works
- ✅ GET /api/products/matches returns only matches
- ✅ Results ordered by match score

---

### Subtask 3.8: Register Routes in Main App (15 minutes)
**File:** Update `backend/app/main.py`

**Objective:** Register all route modules with the main FastAPI app.

**What You'll Learn:**
- Including routers in FastAPI
- API organization
- Route prefixes and tags

**Code to Add:**
```python
from app.api.routes import search_requests, products

# Include routers
app.include_router(search_requests.router)
app.include_router(products.router)

# Update startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("🚀 Product Search Agent API starting up...")
    print("📚 API Documentation: http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("👋 Product Search Agent API shutting down...")
```

**Testing:**
```bash
# Restart server
uvicorn app.main:app --reload

# Check all endpoints in Swagger UI
# http://localhost:8000/docs

# Verify all routes are registered
curl http://localhost:8000/openapi.json | jq '.paths | keys'
```

**Success Criteria:**
- ✅ All routes accessible
- ✅ Swagger UI shows all endpoints
- ✅ Routes organized by tags
- ✅ No import errors

---

### Subtask 3.9: Create API Test Script (45 minutes)
**File:** `backend/app/api/test_api.py`

**Objective:** Create a comprehensive test script to verify all API endpoints.

**What You'll Learn:**
- API testing with requests library
- Test organization
- HTTP status codes
- JSON response validation

**Code Template:**
```python
"""
API endpoint testing script.

Tests all API endpoints to ensure they work correctly.

Usage:
    # Start the server first
    uvicorn app.main:app --reload
    
    # Then run tests in another terminal
    python -m app.api.test_api
"""

import requests
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def print_test(test_name: str):
    """Print test name."""
    print(f"\n📝 {test_name}")


def print_success(message: str):
    """Print success message."""
    print(f"   ✅ {message}")


def print_error(message: str):
    """Print error message."""
    print(f"   ❌ {message}")


def test_health_check():
    """Test health check endpoint."""
    print_test("Testing GET /api/health")
    
    response = requests.get(f"{BASE_URL}/api/health")
    
    if response.status_code == 200:
        print_success(f"Status: {response.status_code}")
        print_success(f"Response: {response.json()}")
        return True
    else:
        print_error(f"Expected 200, got {response.status_code}")
        return False


def test_create_search_request() -> str:
    """Test creating a search request."""
    print_test("Testing POST /api/search-requests")
    
    data = {
        "product_name": "Test iPhone",
        "product_description": "Testing API",
        "budget": 500.0,
        "location": "Test City",
        "match_threshold": 75.0
    }
    
    response = requests.post(f"{BASE_URL}/api/search-requests/", json=data)
    
    if response.status_code == 201:
        result = response.json()
        print_success(f"Status: {response.status_code}")
        print_success(f"Created ID: {result['id']}")
        return result['id']
    else:
        print_error(f"Expected 201, got {response.status_code}")
        return None


def test_list_search_requests():
    """Test listing search requests."""
    print_test("Testing GET /api/search-requests")
    
    response = requests.get(f"{BASE_URL}/api/search-requests/")
    
    if response.status_code == 200:
        result = response.json()
        print_success(f"Status: {response.status_code}")
        print_success(f"Total items: {result['total']}")
        return True
    else:
        print_error(f"Expected 200, got {response.status_code}")
        return False


def test_get_search_request(search_id: str):
    """Test getting a single search request."""
    print_test(f"Testing GET /api/search-requests/{search_id}")
    
    response = requests.get(f"{BASE_URL}/api/search-requests/{search_id}")
    
    if response.status_code == 200:
        result = response.json()
        print_success(f"Status: {response.status_code}")
        print_success(f"Product: {result['product_name']}")
        return True
    else:
        print_error(f"Expected 200, got {response.status_code}")
        return False


def test_update_search_request(search_id: str):
    """Test updating a search request."""
    print_test(f"Testing PUT /api/search-requests/{search_id}")
    
    data = {"budget": 600.0}
    response = requests.put(f"{BASE_URL}/api/search-requests/{search_id}", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print_success(f"Status: {response.status_code}")
        print_success(f"Updated budget: ${result['budget']}")
        return True
    else:
        print_error(f"Expected 200, got {response.status_code}")
        return False


def test_pause_search_request(search_id: str):
    """Test pausing a search request."""
    print_test(f"Testing POST /api/search-requests/{search_id}/pause")
    
    response = requests.post(f"{BASE_URL}/api/search-requests/{search_id}/pause")
    
    if response.status_code == 200:
        result = response.json()
        print_success(f"Status: {response.status_code}")
        print_success(f"New status: {result['status']}")
        return True
    else:
        print_error(f"Expected 200, got {response.status_code}")
        return False


def test_resume_search_request(search_id: str):
    """Test resuming a search request."""
    print_test(f"Testing POST /api/search-requests/{search_id}/resume")
    
    response = requests.post(f"{BASE_URL}/api/search-requests/{search_id}/resume")
    
    if response.status_code == 200:
        result = response.json()
        print_success(f"Status: {response.status_code}")
        print_success(f"New status: {result['status']}")
        return True
    else:
        print_error(f"Expected 200, got {response.status_code}")
        return False


def test_delete_search_request(search_id: str):
    """Test deleting a search request."""
    print_test(f"Testing DELETE /api/search-requests/{search_id}")
    
    response = requests.delete(f"{BASE_URL}/api/search-requests/{search_id}")
    
    if response.status_code == 204:
        print_success(f"Status: {response.status_code}")
        print_success("Search request deleted")
        return True
    else:
        print_error(f"Expected 204, got {response.status_code}")
        return False


def test_list_products():
    """Test listing products."""
    print_test("Testing GET /api/products")
    
    response = requests.get(f"{BASE_URL}/api/products/")
    
    if response.status_code == 200:
        result = response.json()
        print_success(f"Status: {response.status_code}")
        print_success(f"Total products: {result['total']}")
        return True
    else:
        print_error(f"Expected 200, got {response.status_code}")
        return False


def test_list_matches():
    """Test listing matching products."""
    print_test("Testing GET /api/products/matches")
    
    response = requests.get(f"{BASE_URL}/api/products/matches")
    
    if response.status_code == 200:
        result = response.json()
        print_success(f"Status: {response.status_code}")
        print_success(f"Total matches: {result['total']}")
        return True
    else:
        print_error(f"Expected 200, got {response.status_code}")
        return False


def run_all_tests():
    """Run all API tests."""
    print("=" * 70)
    print("  API ENDPOINT TESTS")
    print("=" * 70)
    print("\nMake sure the server is running: uvicorn app.main:app --reload\n")
    
    results = []
    
    # Test health check
    results.append(("Health Check", test_health_check()))
    
    # Test search request CRUD
    search_id = test_create_search_request()
    if search_id:
        results.append(("Create Search Request", True))
        results.append(("List Search Requests", test_list_search_requests()))
        results.append(("Get Search Request", test_get_search_request(search_id)))
        results.append(("Update Search Request", test_update_search_request(search_id)))
        results.append(("Pause Search Request", test_pause_search_request(search_id)))
        results.append(("Resume Search Request", test_resume_search_request(search_id)))
        results.append(("Delete Search Request", test_delete_search_request(search_id)))
    else:
        results.append(("Create Search Request", False))
    
    # Test product endpoints
    results.append(("List Products", test_list_products()))
    results.append(("List Matches", test_list_matches()))
    
    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status}: {test_name}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL API TESTS PASSED! 🎉\n")
        return True
    else:
        print("\n❌ SOME TESTS FAILED ❌\n")
        return False


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server")
        print("Make sure the server is running: uvicorn app.main:app --reload\n")
        sys.exit(1)
```

**Testing:**
```bash
# Terminal 1: Start server
uvicorn app.main:app --reload

# Terminal 2: Run tests
python -m app.api.test_api
```

**Success Criteria:**
- ✅ All API tests pass
- ✅ CRUD operations work correctly
- ✅ Action endpoints work
- ✅ Product endpoints work

---

### Subtask 3.10: Create API Documentation (30 minutes)
**File:** `docs/API_DOCUMENTATION.md`

**Objective:** Document all API endpoints with examples.

**What You'll Learn:**
- API documentation best practices
- Request/response examples
- Error handling documentation

**Content to Include:**
- Endpoint descriptions
- Request examples
- Response examples
- Error codes
- Authentication (for future)

**Success Criteria:**
- ✅ All endpoints documented
- ✅ Examples provided
- ✅ Error codes listed
- ✅ Clear and beginner-friendly

---

## Final Checklist

Before moving to Day 4, ensure:

- [ ] **Subtask 3.1**: Basic FastAPI app running
- [ ] **Subtask 3.2**: Database dependency created
- [ ] **Subtask 3.3**: GET endpoints for search requests
- [ ] **Subtask 3.4**: POST endpoint for creating searches
- [ ] **Subtask 3.5**: PUT/DELETE endpoints for searches
- [ ] **Subtask 3.6**: Pause/Resume action endpoints
- [ ] **Subtask 3.7**: Product endpoints (list and matches)
- [ ] **Subtask 3.8**: Routes registered in main app
- [ ] **Subtask 3.9**: API test script passing
- [ ] **Subtask 3.10**: API documentation complete

---

## Estimated Time Breakdown

| Subtask | Time | Difficulty |
|---------|------|------------|
| 3.1 Basic App | 30 min | Easy |
| 3.2 Dependencies | 20 min | Easy |
| 3.3 GET Routes | 45 min | Medium |
| 3.4 POST Route | 45 min | Medium |
| 3.5 PUT/DELETE Routes | 45 min | Medium |
| 3.6 Action Routes | 30 min | Easy |
| 3.7 Product Routes | 45 min | Medium |
| 3.8 Register Routes | 15 min | Easy |
| 3.9 Test Script | 45 min | Medium |
| 3.10 Documentation | 30 min | Easy |
| **Total** | **~6 hours** | **Medium** |

---

## Common Issues & Solutions

### Issue 1: Import Errors
**Problem:** Cannot import modules
**Solution:**
- Check you're in the backend directory
- Verify virtual environment is activated
- Run from project root: `python -m app.main`

### Issue 2: Database Not Found
**Problem:** Database file doesn't exist
**Solution:**
- Run database initialization: `python -m app.models.init_db`
- Check database path in config

### Issue 3: Port Already in Use
**Problem:** Port 8000 is already in use
**Solution:**
- Kill existing process: `lsof -ti:8000 | xargs kill`
- Or use different port: `uvicorn app.main:app --port 8001`

### Issue 4: CORS Errors
**Problem:** Frontend can't access API
**Solution:**
- Check CORS middleware is configured
- Verify allowed origins include frontend URL

---

## Next Steps

After completing Day 3, you'll be ready for:
- **Day 4**: Base Scraper & Utilities
- **Day 5-6**: Platform-specific scrapers
- **Day 7-8**: Matching engine and orchestrator

---

## Tips for Success

1. **Test Frequently**: Test each endpoint as you create it
2. **Use Swagger UI**: The auto-generated docs at /docs are very helpful
3. **Read Error Messages**: FastAPI provides detailed error messages
4. **Commit Often**: Commit after each working subtask
5. **Take Breaks**: Don't try to do everything at once
6. **Ask Questions**: If stuck, review the code examples

---

**Good luck with Day 3! You've got this! 🚀**