"""
API endpoint integration tests using FastAPI TestClient.

These tests don't require a running server - they use FastAPI's TestClient
which simulates HTTP requests.

Usage:
    pytest app/tests/test_api.py -v
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Import all models to ensure they're registered with Base.metadata
from app.models import SearchRequest, SearchExecution, Product, Notification

@pytest.fixture(scope="function")
def test_db():
    """Create test database and tables."""
    # Use in-memory database for each test
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield engine, TestingSessionLocal
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with test database."""
    engine, TestingSessionLocal = test_db
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Use TestClient without context manager to avoid issues
    test_client = TestClient(app)
    yield test_client
    
    app.dependency_overrides.clear()


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_search_request(client):
    """Test creating a search request."""
    data = {
        "product_name": "Test iPhone",
        "product_description": "Testing API",
        "budget": 500.0,
        "location": "Test City",
        "match_threshold": 75.0
    }
    
    response = client.post("/api/search-requests/", json=data)
    assert response.status_code == 201
    result = response.json()
    assert result["product_name"] == "Test iPhone"
    assert "id" in result


def test_list_search_requests(client):
    """Test listing search requests."""
    # First create a search request
    data = {
        "product_name": "Test Product",
        "budget": 100.0,
        "location": "Test City"
    }
    client.post("/api/search-requests/", json=data)
    
    # Then list them
    response = client.get("/api/search-requests/")
    assert response.status_code == 200
    result = response.json()
    assert "items" in result
    assert "total" in result
    assert result["total"] >= 1


def test_get_search_request(client):
    """Test getting a single search request."""
    # Create a search request first (use same format as test_create_search_request)
    data = {
        "product_name": "Test iPhone Get",
        "product_description": "Testing API",
        "budget": 500.0,
        "location": "Test City",
        "match_threshold": 75.0
    }
    create_response = client.post("/api/search-requests/", json=data)
    assert create_response.status_code == 201
    response_data = create_response.json()
    
    # List all search requests to find the one we just created
    list_response = client.get("/api/search-requests/")
    items = list_response.json()["items"]
    # Find the one we just created by product name
    search_id = None
    for item in items:
        if item["product_name"] == "Test iPhone Get":
            search_id = item["id"]
            break
    
    assert search_id is not None, "Could not find the created search request"
    
    # Get the search request
    response = client.get(f"/api/search-requests/{search_id}")
    assert response.status_code == 200
    result = response.json()
    assert result["product_name"] == "Test iPhone Get"


def test_update_search_request(client):
    """Test updating a search request."""
    # Create a search request first
    data = {
        "product_name": "Test Product",
        "product_description": "Testing API",
        "budget": 500.0,
        "location": "Test City",
        "match_threshold": 75.0
    }
    create_response = client.post("/api/search-requests/", json=data)
    assert create_response.status_code == 201
    
    # List to get the ID
    list_response = client.get("/api/search-requests/")
    items = list_response.json()["items"]
    search_id = items[0]["id"]
    
    # Update it
    update_data = {"budget": 600.0}
    response = client.put(f"/api/search-requests/{search_id}", json=update_data)
    assert response.status_code == 200
    result = response.json()
    assert result["budget"] == 600.0


def test_pause_search_request(client):
    """Test pausing a search request."""
    # Create a search request first
    data = {
        "product_name": "Test Product",
        "product_description": "Testing API",
        "budget": 500.0,
        "location": "Test City",
        "match_threshold": 75.0
    }
    create_response = client.post("/api/search-requests/", json=data)
    assert create_response.status_code == 201
    
    # List to get the ID
    list_response = client.get("/api/search-requests/")
    items = list_response.json()["items"]
    search_id = items[0]["id"]
    
    # Pause it
    response = client.post(f"/api/search-requests/{search_id}/pause")
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "paused"


def test_resume_search_request(client):
    """Test resuming a search request."""
    # Create and pause a search request first
    data = {
        "product_name": "Test Product",
        "product_description": "Testing API",
        "budget": 500.0,
        "location": "Test City",
        "match_threshold": 75.0
    }
    create_response = client.post("/api/search-requests/", json=data)
    assert create_response.status_code == 201
    
    # List to get the ID
    list_response = client.get("/api/search-requests/")
    items = list_response.json()["items"]
    search_id = items[0]["id"]
    
    client.post(f"/api/search-requests/{search_id}/pause")
    
    # Resume it
    response = client.post(f"/api/search-requests/{search_id}/resume")
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "active"


def test_delete_search_request(client):
    """Test deleting a search request."""
    # Create a search request first
    data = {
        "product_name": "Test Product",
        "product_description": "Testing API",
        "budget": 500.0,
        "location": "Test City",
        "match_threshold": 75.0
    }
    create_response = client.post("/api/search-requests/", json=data)
    assert create_response.status_code == 201
    
    # List to get the ID
    list_response = client.get("/api/search-requests/")
    items = list_response.json()["items"]
    search_id = items[0]["id"]
    
    # Delete it
    response = client.delete(f"/api/search-requests/{search_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/search-requests/{search_id}")
    assert get_response.status_code == 404


def test_list_products(client):
    """Test listing products."""
    response = client.get("/api/products/")
    assert response.status_code == 200
    result = response.json()
    assert "items" in result
    assert "total" in result


def test_list_matches(client):
    """Test listing matching products."""
    response = client.get("/api/products/matches")
    assert response.status_code == 200
    result = response.json()
    assert "items" in result
    assert "total" in result