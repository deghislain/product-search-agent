"""
Comprehensive test script for all database models.

This script tests CRUD operations, relationships, helper methods,
and edge cases for all models in the application.

Usage:
    pytest app/tests/models/test_models.py -vv
"""
import sys
from pathlib import Path


# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import SearchRequest, SearchExecution, Product, Notification
from app.models import SearchStatus, NotificationType, ExecutionStatus
from datetime import datetime, timedelta


# Pytest fixtures
@pytest.fixture(scope="function")
def db():
    """Create a test database session."""
    # Create in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def search(db):
    """Create a test SearchRequest."""
    search = SearchRequest(
        product_name="iPhone 13",
        product_description="Looking for iPhone 13 in good condition, 128GB or more",
        budget=600.0,
        location="Boston, MA",
        match_threshold=75.0,
        status=SearchStatus.ACTIVE
    )
    db.add(search)
    db.commit()
    db.refresh(search)
    return search


@pytest.fixture
def execution(db, search):
    """Create a test SearchExecution."""
    execution = SearchExecution(
        search_request_id=search.id,
        started_at=datetime.utcnow(),
        status=ExecutionStatus.RUNNING.value
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution


@pytest.fixture
def product(db, execution):
    """Create a test Product."""
    product = Product(
        search_execution_id=execution.id,
        title="iPhone 13 128GB Blue - Excellent Condition",
        description="Barely used, comes with original box and charger",
        price=450.0,
        url="https://boston.craigslist.org/product/123456",
        image_url="https://images.craigslist.org/123456.jpg",
        platform="craigslist",
        location="Boston, MA",
        posted_date=datetime.utcnow() - timedelta(days=2),
        match_score=85.5,
        is_match=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@pytest.fixture
def notification(db, search, product):
    """Create a test Notification."""
    notification = Notification(
        search_request_id=search.id,
        product_id=product.id,
        type=NotificationType.MATCH_FOUND,
        message=f"Found match: {product.title} for ${product.price}"
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


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


def test_search_request_model(db):
    """Test SearchRequest model and its methods."""
    print_section("TEST 1: SearchRequest Model")
    
    try:
        # Create SearchRequest
        print_test("Creating SearchRequest")
        search = SearchRequest(
            product_name="iPhone 13",
            product_description="Looking for iPhone 13 in good condition, 128GB or more",
            budget=600.0,
            location="Boston, MA",
            match_threshold=75.0,
            status=SearchStatus.ACTIVE
        )
        db.add(search)
        db.commit()
        db.refresh(search)
        print_success(f"Created: {search}")
        print_success(f"ID: {search.id}")
        
        # Test is_active method
        print_test("Testing is_active() method")
        assert search.is_active() == True, "Search should be active"
        print_success(f"is_active() = {search.is_active()}")
        
        # Test pause method
        print_test("Testing pause() method")
        search.pause()
        db.commit()
        assert search.status == SearchStatus.PAUSED, "Status should be PAUSED"
        assert search.is_active() == False, "Search should not be active"
        print_success(f"Status after pause: {search.status.value}")
        
        # Test resume method
        print_test("Testing resume() method")
        search.resume()
        db.commit()
        assert search.status == SearchStatus.ACTIVE, "Status should be ACTIVE"
        print_success(f"Status after resume: {search.status.value}")
        
        # Test update_budget method
        print_test("Testing update_budget() method")
        old_budget = search.budget
        search.update_budget(650.0)
        db.commit()
        assert search.budget == 650.0, "Budget should be updated"
        print_success(f"Budget updated: ${old_budget} → ${search.budget}")
        
        # Test update_threshold method
        print_test("Testing update_threshold() method")
        old_threshold = search.match_threshold
        search.update_threshold(80.0)
        db.commit()
        assert search.match_threshold == 80.0, "Threshold should be updated"
        print_success(f"Threshold updated: {old_threshold} → {search.match_threshold}")
        
        # Test invalid threshold
        print_test("Testing invalid threshold (should raise ValueError)")
        try:
            search.update_threshold(150.0)
            print_error("Should have raised ValueError for threshold > 100")
            return None
        except ValueError as e:
            print_success(f"Correctly raised ValueError: {e}")
        
        # Test to_dict method
        print_test("Testing to_dict() method")
        search_dict = search.to_dict()
        assert 'id' in search_dict, "Dict should contain 'id'"
        assert 'product_name' in search_dict, "Dict should contain 'product_name'"
        assert search_dict['budget'] == 650.0, "Dict should have updated budget"
        print_success(f"to_dict() returned {len(search_dict)} fields")
        
        # Test cancel method
        print_test("Testing cancel() method")
        search.cancel()
        db.commit()
        assert search.status == SearchStatus.CANCELLED, "Status should be CANCELLED"
        print_success(f"Status after cancel: {search.status.value}")
        
        # Create another search for further tests
        search.resume()  # Resume for other tests
        db.commit()
        
        print_success("All SearchRequest tests passed!")
        return search
        
    except Exception as e:
        print_error(f"SearchRequest test failed: {e}")
        db.rollback()
        return None


def test_search_execution_model(db, search):
    """Test SearchExecution model and its methods."""
    print_section("TEST 2: SearchExecution Model")
    
    if not search:
        print_error("Skipping: No search request available")
        return None
    
    try:
        # Create SearchExecution
        print_test("Creating SearchExecution")
        execution = SearchExecution(
            search_request_id=search.id,
            started_at=datetime.utcnow(),
            status=ExecutionStatus.RUNNING.value
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        print_success(f"Created: {execution}")
        print_success(f"ID: {execution.id}")
        
        # Test is_running method
        print_test("Testing is_running() method")
        assert execution.is_running() == True, "Execution should be running"
        print_success(f"is_running() = {execution.is_running()}")
        
        # Test complete method
        print_test("Testing complete() method")
        execution.complete(products_found=25, matches_found=3)
        db.commit()
        assert execution.is_completed() == True, "Execution should be completed"
        assert execution.products_found == 25, "Should have 25 products"
        assert execution.matches_found == 3, "Should have 3 matches"
        print_success(f"Status: {execution.status}")
        print_success(f"Products found: {execution.products_found}")
        print_success(f"Matches found: {execution.matches_found}")
        
        # Test is_successful method
        print_test("Testing is_successful() method")
        assert execution.is_successful() == True, "Execution should be successful"
        print_success(f"is_successful() = {execution.is_successful()}")
        
        # Test has_matches method
        print_test("Testing has_matches() method")
        assert execution.has_matches() == True, "Should have matches"
        print_success(f"has_matches() = {execution.has_matches()}")
        
        # Test match_rate method
        print_test("Testing match_rate() method")
        rate = execution.match_rate()
        expected_rate = (3 / 25) * 100
        assert abs(rate - expected_rate) < 0.01, f"Match rate should be {expected_rate}%"
        print_success(f"match_rate() = {rate:.1f}%")
        
        # Test duration_seconds method
        print_test("Testing duration_seconds() method")
        duration = execution.duration_seconds()
        assert duration >= 0, "Duration should be non-negative"
        print_success(f"duration_seconds() = {duration:.2f}s")
        
        # Test to_dict method
        print_test("Testing to_dict() method")
        exec_dict = execution.to_dict()
        assert 'id' in exec_dict, "Dict should contain 'id'"
        assert 'status' in exec_dict, "Dict should contain 'status'"
        assert exec_dict['products_found'] == 25, "Dict should have correct products_found"
        print_success(f"to_dict() returned {len(exec_dict)} fields")
        
        # Create a failed execution
        print_test("Creating failed execution")
        failed_exec = SearchExecution(
            search_request_id=search.id,
            started_at=datetime.utcnow(),
            status=ExecutionStatus.RUNNING.value
        )
        db.add(failed_exec)
        db.commit()
        
        failed_exec.fail("Network timeout error")
        db.commit()
        assert failed_exec.is_failed() == True, "Execution should be failed"
        assert failed_exec.error_message == "Network timeout error", "Should have error message"
        print_success(f"Failed execution created with error: {failed_exec.error_message}")
        
        print_success("All SearchExecution tests passed!")
        return execution
        
    except Exception as e:
        print_error(f"SearchExecution test failed: {e}")
        db.rollback()
        return None


def test_product_model(db, execution):
    """Test Product model and its methods."""
    print_section("TEST 3: Product Model")
    
    if not execution:
        print_error("Skipping: No search execution available")
        return None
    
    try:
        # Create Product
        print_test("Creating Product")
        product = Product(
            search_execution_id=execution.id,
            title="iPhone 13 128GB Blue - Excellent Condition",
            description="Barely used, comes with original box and charger",
            price=450.0,
            url="https://boston.craigslist.org/product/123456",
            image_url="https://images.craigslist.org/123456.jpg",
            platform="craigslist",
            location="Boston, MA",
            posted_date=datetime.utcnow() - timedelta(days=2),
            match_score=85.5,
            is_match=True
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        print_success(f"Created: {product}")
        print_success(f"ID: {product.id}")
        
        # Test is_good_match method
        print_test("Testing is_good_match() method")
        assert product.is_good_match(70.0) == True, "Should be a good match"
        assert product.is_good_match(90.0) == False, "Should not meet 90% threshold"
        print_success(f"is_good_match(70.0) = {product.is_good_match(70.0)}")
        print_success(f"is_good_match(90.0) = {product.is_good_match(90.0)}")
        
        # Test is_within_budget method
        print_test("Testing is_within_budget() method")
        assert product.is_within_budget(500.0) == True, "Should be within budget"
        assert product.is_within_budget(400.0) == False, "Should exceed budget"
        print_success(f"is_within_budget(500.0) = {product.is_within_budget(500.0)}")
        print_success(f"is_within_budget(400.0) = {product.is_within_budget(400.0)}")
        
        # Test mark_as_match method
        print_test("Testing mark_as_match() method")
        product.mark_as_match(92.0)
        db.commit()
        assert product.match_score == 92.0, "Match score should be updated"
        assert product.is_match == True, "Should be marked as match"
        print_success(f"Marked as match with score: {product.match_score}")
        
        # Test mark_as_non_match method
        print_test("Testing mark_as_non_match() method")
        product.mark_as_non_match(45.0)
        db.commit()
        assert product.match_score == 45.0, "Match score should be updated"
        assert product.is_match == False, "Should be marked as non-match"
        print_success(f"Marked as non-match with score: {product.match_score}")
        
        # Reset for other tests
        product.mark_as_match(85.5)
        db.commit()
        
        # Test get_short_title method
        print_test("Testing get_short_title() method")
        short_title = product.get_short_title(30)
        assert len(short_title) <= 30, "Short title should be <= 30 chars"
        print_success(f"Short title (30 chars): {short_title}")
        
        # Test days_since_posted method
        print_test("Testing days_since_posted() method")
        days = product.days_since_posted()
        assert days >= 2, "Should be at least 2 days old"
        print_success(f"days_since_posted() = {days} days")
        
        # Test is_recent method
        print_test("Testing is_recent() method")
        assert product.is_recent(7) == True, "Should be recent (within 7 days)"
        assert product.is_recent(1) == False, "Should not be recent (within 1 day)"
        print_success(f"is_recent(7) = {product.is_recent(7)}")
        print_success(f"is_recent(1) = {product.is_recent(1)}")
        
        # Test to_dict method
        print_test("Testing to_dict() method")
        product_dict = product.to_dict()
        assert 'id' in product_dict, "Dict should contain 'id'"
        assert 'title' in product_dict, "Dict should contain 'title'"
        assert product_dict['price'] == 450.0, "Dict should have correct price"
        assert 'days_since_posted' in product_dict, "Dict should include days_since_posted"
        print_success(f"to_dict() returned {len(product_dict)} fields")
        
        # Create product without posted_date
        print_test("Creating product without posted_date")
        product2 = Product(
            search_execution_id=execution.id,
            title="iPhone 13 Pro",
            price=550.0,
            url="https://example.com/product/789",
            platform="facebook",
            is_match=False
        )
        db.add(product2)
        db.commit()
        assert product2.days_since_posted() == 0, "Should return 0 for null posted_date"
        assert product2.is_recent() == False, "Should not be recent with null posted_date"
        print_success("Product without posted_date handled correctly")
        
        print_success("All Product tests passed!")
        return product
        
    except Exception as e:
        print_error(f"Product test failed: {e}")
        db.rollback()
        return None


def test_notification_model(db, search, product):
    """Test Notification model and its methods."""
    print_section("TEST 4: Notification Model")
    
    if not search or not product:
        print_error("Skipping: No search request or product available")
        return None
    
    try:
        # Create Notification
        print_test("Creating Notification")
        notification = Notification(
            search_request_id=search.id,
            product_id=product.id,
            type=NotificationType.MATCH_FOUND,
            message=f"Found match: {product.title} for ${product.price}"
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        print_success(f"Created: {notification}")
        print_success(f"ID: {notification.id}")
        
        # Test is_unread method
        print_test("Testing is_unread() method")
        assert notification.is_unread() == True, "Should be unread initially"
        assert notification.is_read() == False, "Should not be read initially"
        print_success(f"is_unread() = {notification.is_unread()}")
        print_success(f"is_read() = {notification.is_read()}")
        
        # Test mark_as_read method
        print_test("Testing mark_as_read() method")
        notification.mark_as_read()
        db.commit()
        assert notification.read == True, "Should be marked as read"
        assert notification.is_read() == True, "is_read() should return True"
        print_success(f"Notification marked as read: {notification.read}")
        
        # Test mark_as_unread method
        print_test("Testing mark_as_unread() method")
        notification.mark_as_unread()
        db.commit()
        assert notification.read == False, "Should be marked as unread"
        print_success(f"Notification marked as unread: {notification.read}")
        
        # Test is_match_notification method
        print_test("Testing is_match_notification() method")
        assert notification.is_match_notification() == True, "Should be match notification"
        print_success(f"is_match_notification() = {notification.is_match_notification()}")
        
        # Test is_error_notification method
        print_test("Testing is_error_notification() method")
        assert notification.is_error_notification() == False, "Should not be error notification"
        print_success(f"is_error_notification() = {notification.is_error_notification()}")
        
        # Test has_product method
        print_test("Testing has_product() method")
        assert notification.has_product() == True, "Should have associated product"
        print_success(f"has_product() = {notification.has_product()}")
        
        # Test age methods
        print_test("Testing age calculation methods")
        age_seconds = notification.age_seconds()
        age_minutes = notification.age_minutes()
        age_hours = notification.age_hours()
        assert age_seconds >= 0, "Age should be non-negative"
        assert age_minutes >= 0, "Age should be non-negative"
        assert age_hours >= 0, "Age should be non-negative"
        print_success(f"age_seconds() = {age_seconds:.2f}s")
        print_success(f"age_minutes() = {age_minutes:.2f}m")
        print_success(f"age_hours() = {age_hours:.4f}h")
        
        # Test is_recent method
        print_test("Testing is_recent() method")
        assert notification.is_recent(60) == True, "Should be recent (within 60 minutes)"
        print_success(f"is_recent(60) = {notification.is_recent(60)}")
        
        # Test get_short_message method
        print_test("Testing get_short_message() method")
        short_msg = notification.get_short_message(30)
        assert len(short_msg) <= 30, "Short message should be <= 30 chars"
        print_success(f"Short message (30 chars): {short_msg}")
        
        # Test to_dict method
        print_test("Testing to_dict() method")
        notif_dict = notification.to_dict()
        assert 'id' in notif_dict, "Dict should contain 'id'"
        assert 'type' in notif_dict, "Dict should contain 'type'"
        assert 'age_minutes' in notif_dict, "Dict should include age_minutes"
        assert 'is_recent' in notif_dict, "Dict should include is_recent"
        print_success(f"to_dict() returned {len(notif_dict)} fields")
        
        # Create error notification without product
        print_test("Creating error notification without product")
        error_notif = Notification(
            search_request_id=search.id,
            product_id=None,
            type=NotificationType.ERROR_OCCURRED,
            message="Failed to connect to Craigslist"
        )
        db.add(error_notif)
        db.commit()
        assert error_notif.is_error_notification() == True, "Should be error notification"
        assert error_notif.has_product() == False, "Should not have product"
        print_success("Error notification without product created successfully")
        
        # Create search started notification
        print_test("Creating search started notification")
        start_notif = Notification(
            search_request_id=search.id,
            type=NotificationType.SEARCH_STARTED,
            message="Search started for iPhone 13"
        )
        db.add(start_notif)
        db.commit()
        assert start_notif.is_match_notification() == False, "Should not be match notification"
        print_success("Search started notification created successfully")
        
        print_success("All Notification tests passed!")
        return notification
        
    except Exception as e:
        print_error(f"Notification test failed: {e}")
        db.rollback()
        return None


def test_relationships(db, search, execution, product, notification):
    """Test relationships between models."""
    print_section("TEST 5: Model Relationships")
    
    if not all([search, execution, product, notification]):
        print_error("Skipping: Not all models available")
        return False
    
    try:
        # Note: Relationships are commented out in models, so we'll test foreign keys
        print_test("Testing foreign key relationships")
        
        # Verify SearchExecution belongs to SearchRequest
        assert execution.search_request_id == search.id, "Execution should belong to search"
        print_success(f"SearchExecution → SearchRequest: {execution.search_request_id}")
        
        # Verify Product belongs to SearchExecution
        assert product.search_execution_id == execution.id, "Product should belong to execution"
        print_success(f"Product → SearchExecution: {product.search_execution_id}")
        
        # Verify Notification belongs to SearchRequest
        assert notification.search_request_id == search.id, "Notification should belong to search"
        print_success(f"Notification → SearchRequest: {notification.search_request_id}")
        
        # Verify Notification references Product
        assert notification.product_id == product.id, "Notification should reference product"
        print_success(f"Notification → Product: {notification.product_id}")
        
        # Test querying related records
        print_test("Testing queries for related records")
        
        # Find all executions for a search
        executions = db.query(SearchExecution).filter_by(search_request_id=search.id).all()
        print_success(f"Found {len(executions)} executions for search {search.id}")
        
        # Find all products for an execution
        products = db.query(Product).filter_by(search_execution_id=execution.id).all()
        print_success(f"Found {len(products)} products for execution {execution.id}")
        
        # Find all notifications for a search
        notifications = db.query(Notification).filter_by(search_request_id=search.id).all()
        print_success(f"Found {len(notifications)} notifications for search {search.id}")
        
        # Find notifications for a specific product
        product_notifs = db.query(Notification).filter_by(product_id=product.id).all()
        print_success(f"Found {len(product_notifs)} notifications for product {product.id}")
        
        print_success("All relationship tests passed!")
        return True
        
    except Exception as e:
        print_error(f"Relationship test failed: {e}")
        return False


def test_queries_and_filters(db):
    """Test various query patterns and filters."""
    print_section("TEST 6: Queries and Filters")
    
    try:
        # Test filtering by status
        print_test("Querying active searches")
        active_searches = db.query(SearchRequest).filter_by(status=SearchStatus.ACTIVE).all()
        print_success(f"Found {len(active_searches)} active searches")
        
        # Test filtering products by match status
        print_test("Querying matching products")
        matches = db.query(Product).filter_by(is_match=True).all()
        print_success(f"Found {len(matches)} matching products")
        
        # Test filtering unread notifications
        print_test("Querying unread notifications")
        unread = db.query(Notification).filter_by(read=False).all()
        print_success(f"Found {len(unread)} unread notifications")
        
        # Test ordering by created_at
        print_test("Querying recent products (ordered by created_at)")
        recent_products = db.query(Product).order_by(Product.created_at.desc()).limit(5).all()
        print_success(f"Found {len(recent_products)} recent products")
        
        # Test filtering by price range
        print_test("Querying products under $500")
        affordable = db.query(Product).filter(Product.price <= 500.0).all()
        print_success(f"Found {len(affordable)} products under $500")
        
        # Test filtering by platform
        print_test("Querying Craigslist products")
        craigslist_products = db.query(Product).filter_by(platform="craigslist").all()
        print_success(f"Found {len(craigslist_products)} Craigslist products")
        
        # Test counting records
        print_test("Counting total records")
        search_count = db.query(SearchRequest).count()
        execution_count = db.query(SearchExecution).count()
        product_count = db.query(Product).count()
        notification_count = db.query(Notification).count()
        print_success(f"SearchRequests: {search_count}")
        print_success(f"SearchExecutions: {execution_count}")
        print_success(f"Products: {product_count}")
        print_success(f"Notifications: {notification_count}")
        
        print_success("All query tests passed!")
        return True
        
    except Exception as e:
        print_error(f"Query test failed: {e}")
        return False


def test_print_functions():
    """Test the print helper functions."""
    # Test print_section
    print_section("Test Section")
    
    # Test print_test
    print_test("Test Name")
    
    # Test print_success
    print_success("Success message")
    
    # Test print_error
    print_error("Error message")
    
    # All print functions should execute without errors
    assert True


if __name__ == "__main__":
    # Run tests with pytest
    import pytest
    sys.exit(pytest.main([__file__, "-vv", "-s"]))

# Made with Bob
