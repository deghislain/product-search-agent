"""
Test script for Pydantic schemas.

This script validates that all schemas work correctly with proper
validation, serialization, and error handling.

Usage:
    python -m app.schemas.test_schemas
"""
import sys
from pathlib import Path

# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import datetime
from app.schemas import (
    SearchRequestCreate,
    SearchRequestUpdate,
    SearchRequestResponse,
    ProductResponse,
    SearchExecutionResponse,
    NotificationResponse,
    SearchStatus,
    NotificationType,
)
import sys


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_test(test_name: str):
    """Print a test name."""
    print(f"\n📝 {test_name}")


def print_success(message: str):
    """Print a success message."""
    print(f"   ✅ {message}")


def print_error(message: str):
    """Print an error message."""
    print(f"   ❌ {message}")


def test_search_request_schemas():
    """Test SearchRequest schemas."""
    print_section("TEST 1: SearchRequest Schemas")
    
    try:
        # Test SearchRequestCreate
        print_test("Testing SearchRequestCreate schema")
        create_data = {
            "product_name": "iPhone 13",
            "product_description": "Looking for iPhone 13 in good condition",
            "budget": 600.0,
            "location": "Boston, MA",
            "match_threshold": 75.0
        }
        search_create = SearchRequestCreate(**create_data)
        print_success(f"Created: {search_create.product_name}")
        print_success(f"Budget: ${search_create.budget}")
        print_success(f"Threshold: {search_create.match_threshold}%")
        
        # Test validation - budget must be positive
        print_test("Testing budget validation (must be > 0)")
        try:
            invalid_search = SearchRequestCreate(
                product_name="Test",
                product_description="Test",
                budget=-100.0
            )
            print_error("Should have raised validation error for negative budget")
            return False
        except Exception as e:
            print_success(f"Correctly raised validation error: {type(e).__name__}")
        
        # Test validation - threshold must be 0-100
        print_test("Testing threshold validation (must be 0-100)")
        try:
            invalid_search = SearchRequestCreate(
                product_name="Test",
                product_description="Test",
                budget=100.0,
                match_threshold=150.0
            )
            print_error("Should have raised validation error for threshold > 100")
            return False
        except Exception as e:
            print_success(f"Correctly raised validation error: {type(e).__name__}")
        
        # Test SearchRequestUpdate
        print_test("Testing SearchRequestUpdate schema")
        update_data = {
            "budget": 650.0,
            "status": SearchStatus.PAUSED
        }
        search_update = SearchRequestUpdate(**update_data)
        print_success(f"Update budget: ${search_update.budget}")
        print_success(f"Update status: {search_update.status.value}")
        
        # Test SearchRequestResponse
        print_test("Testing SearchRequestResponse schema")
        response_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "product_name": "iPhone 13",
            "product_description": "Looking for iPhone 13",
            "budget": 600.0,
            "location": "Boston, MA",
            "match_threshold": 75.0,
            "status": SearchStatus.ACTIVE,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        search_response = SearchRequestResponse(**response_data)
        print_success(f"Response ID: {search_response.id}")
        print_success(f"Response status: {search_response.status.value}")
        
        # Test JSON serialization
        print_test("Testing JSON serialization")
        json_data = search_response.model_dump_json()
        print_success(f"Serialized to JSON ({len(json_data)} chars)")
        
        print_success("All SearchRequest schema tests passed!")
        return True
        
    except Exception as e:
        print_error(f"SearchRequest schema test failed: {e}")
        return False


def test_product_schemas():
    """Test Product schemas."""
    print_section("TEST 2: Product Schemas")
    
    try:
        # Test ProductResponse
        print_test("Testing ProductResponse schema")
        product_data = {
            "id": "123e4567-e89b-12d3-a456-426614174001",
            "search_execution_id": "123e4567-e89b-12d3-a456-426614174002",
            "title": "iPhone 13 128GB Blue",
            "description": "Excellent condition",
            "price": 450.0,
            "url": "https://example.com/product/123",
            "image_url": "https://example.com/image.jpg",
            "platform": "craigslist",
            "location": "Boston, MA",
            "posted_date": datetime.utcnow(),
            "match_score": 85.5,
            "is_match": True,
            "created_at": datetime.utcnow()
        }
        product = ProductResponse(**product_data)
        print_success(f"Product: {product.title}")
        print_success(f"Price: ${product.price}")
        print_success(f"Match score: {product.match_score}%")
        print_success(f"Platform: {product.platform}")
        
        # Test validation - price must be positive
        print_test("Testing price validation (must be > 0)")
        try:
            invalid_product = ProductResponse(
                **{**product_data, "price": -50.0}
            )
            print_error("Should have raised validation error for negative price")
            return False
        except Exception as e:
            print_success(f"Correctly raised validation error: {type(e).__name__}")
        
        # Test JSON serialization
        print_test("Testing JSON serialization")
        json_data = product.model_dump_json()
        print_success(f"Serialized to JSON ({len(json_data)} chars)")
        
        print_success("All Product schema tests passed!")
        return True
        
    except Exception as e:
        print_error(f"Product schema test failed: {e}")
        return False


def test_search_execution_schemas():
    """Test SearchExecution schemas."""
    print_section("TEST 3: SearchExecution Schemas")
    
    try:
        # Test SearchExecutionResponse
        print_test("Testing SearchExecutionResponse schema")
        execution_data = {
            "id": "123e4567-e89b-12d3-a456-426614174003",
            "search_request_id": "123e4567-e89b-12d3-a456-426614174000",
            "started_at": datetime.utcnow(),
            "completed_at": datetime.utcnow(),
            "status": "completed",
            "products_found": 25,
            "matches_found": 3,
            "error_message": None,
            "duration_seconds": 45.5,
            "match_rate": 12.0
        }
        execution = SearchExecutionResponse(**execution_data)
        print_success(f"Execution ID: {execution.id}")
        print_success(f"Status: {execution.status}")
        print_success(f"Products found: {execution.products_found}")
        print_success(f"Matches found: {execution.matches_found}")
        print_success(f"Match rate: {execution.match_rate}%")
        print_success(f"Duration: {execution.duration_seconds}s")
        
        # Test validation - counts must be non-negative
        print_test("Testing count validation (must be >= 0)")
        try:
            invalid_execution = SearchExecutionResponse(
                **{**execution_data, "products_found": -5}
            )
            print_error("Should have raised validation error for negative count")
            return False
        except Exception as e:
            print_success(f"Correctly raised validation error: {type(e).__name__}")
        
        # Test JSON serialization
        print_test("Testing JSON serialization")
        json_data = execution.model_dump_json()
        print_success(f"Serialized to JSON ({len(json_data)} chars)")
        
        print_success("All SearchExecution schema tests passed!")
        return True
        
    except Exception as e:
        print_error(f"SearchExecution schema test failed: {e}")
        return False


def test_notification_schemas():
    """Test Notification schemas."""
    print_section("TEST 4: Notification Schemas")
    
    try:
        # Test NotificationResponse
        print_test("Testing NotificationResponse schema")
        notification_data = {
            "id": "123e4567-e89b-12d3-a456-426614174004",
            "search_request_id": "123e4567-e89b-12d3-a456-426614174000",
            "product_id": "123e4567-e89b-12d3-a456-426614174001",
            "type": NotificationType.MATCH_FOUND,
            "message": "Found match: iPhone 13 for $450",
            "read": False,
            "created_at": datetime.utcnow(),
            "age_minutes": 5.5,
            "is_recent": True
        }
        notification = NotificationResponse(**notification_data)
        print_success(f"Notification ID: {notification.id}")
        print_success(f"Type: {notification.type.value}")
        print_success(f"Message: {notification.message}")
        print_success(f"Read: {notification.read}")
        print_success(f"Age: {notification.age_minutes} minutes")
        
        # Test different notification types
        print_test("Testing different notification types")
        for notif_type in NotificationType:
            test_notif = NotificationResponse(
                **{**notification_data, "type": notif_type}
            )
            print_success(f"Type {notif_type.value}: OK")
        
        # Test JSON serialization
        print_test("Testing JSON serialization")
        json_data = notification.model_dump_json()
        print_success(f"Serialized to JSON ({len(json_data)} chars)")
        
        print_success("All Notification schema tests passed!")
        return True
        
    except Exception as e:
        print_error(f"Notification schema test failed: {e}")
        return False


def test_schema_imports():
    """Test that all schemas can be imported from package."""
    print_section("TEST 5: Schema Package Imports")
    
    try:
        print_test("Testing package-level imports")
        
        from app.schemas import (
            SearchRequestCreate,
            SearchRequestUpdate,
            SearchRequestResponse,
            ProductResponse,
            SearchExecutionResponse,
            NotificationResponse,
        )
        
        print_success("SearchRequestCreate imported")
        print_success("SearchRequestUpdate imported")
        print_success("SearchRequestResponse imported")
        print_success("ProductResponse imported")
        print_success("SearchExecutionResponse imported")
        print_success("NotificationResponse imported")
        
        print_success("All schema imports successful!")
        return True
        
    except Exception as e:
        print_error(f"Schema import test failed: {e}")
        return False


def run_all_tests():
    """Run all schema tests."""
    print("\n" + "=" * 70)
    print("  PYDANTIC SCHEMA VALIDATION TESTS")
    print("=" * 70)
    print("\nTesting all Pydantic schemas for validation and serialization...")
    
    results = []
    
    # Run individual tests
    results.append(("SearchRequest Schemas", test_search_request_schemas()))
    results.append(("Product Schemas", test_product_schemas()))
    results.append(("SearchExecution Schemas", test_search_execution_schemas()))
    results.append(("Notification Schemas", test_notification_schemas()))
    results.append(("Schema Imports", test_schema_imports()))
    
    # Final summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status}: {test_name}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "=" * 70)
        print("  🎉 ALL SCHEMA TESTS PASSED! 🎉")
        print("=" * 70 + "\n")
        return True
    else:
        print("\n" + "=" * 70)
        print("  ❌ SOME TESTS FAILED ❌")
        print("=" * 70 + "\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

# Made with Bob
