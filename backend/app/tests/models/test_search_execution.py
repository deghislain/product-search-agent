"""
Test script for SearchExecution model.

This script tests the SearchExecution model functionality including:
- Creating executions
- Updating status
- Helper methods
- Relationships
"""
import sys
from pathlib import Path

# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pytest
from datetime import datetime
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import SearchRequest, SearchExecution, SearchStatus, ExecutionStatus


# Pytest fixtures
@pytest.fixture(scope="function")
def db():
    """Create a test database session."""
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
        product_description="Looking for iPhone 13 in good condition",
        budget=500.0,
        location="Boston, MA",
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


def test_search_execution_creation(execution, search):
    """Test creating a SearchExecution instance."""
    print("\n" + "="*70)
    print("TEST 1: SearchExecution Creation")
    print("="*70)
    
    print(f"✅ Created SearchRequest: {search.id}")
    print(f"✅ Created SearchExecution: {execution.id}")
    print(f"   - Status: {execution.status}")
    print(f"   - Started at: {execution.started_at}")
    
    assert execution.id is not None
    assert execution.search_request_id == search.id
    assert execution.status == ExecutionStatus.RUNNING.value
    assert execution.started_at is not None


def test_is_running_method(execution):
    """Test is_running() method."""
    print("\n" + "="*70)
    print("TEST 2: is_running() Method")
    print("="*70)
    
    assert execution.is_running() == True
    print("✅ is_running() returns True for running execution")


def test_complete_method(db, execution):
    """Test complete() method."""
    print("\n" + "="*70)
    print("TEST 3: complete() Method")
    print("="*70)
    
    time.sleep(0.1)  # Simulate some processing time
    execution.complete(products_found=25, matches_found=3)
    db.commit()
    
    print(f"✅ Execution completed")
    print(f"   - Status: {execution.status}")
    print(f"   - Products found: {execution.products_found}")
    print(f"   - Matches found: {execution.matches_found}")
    print(f"   - Completed at: {execution.completed_at}")
    
    assert execution.status == ExecutionStatus.COMPLETED.value
    assert execution.products_found == 25
    assert execution.matches_found == 3
    assert execution.completed_at is not None
    assert execution.is_completed() == True
    assert execution.is_successful() == True
    assert execution.is_running() == False
    assert execution.is_failed() == False


def test_duration_calculation(db, execution):
    """Test duration_seconds() method."""
    print("\n" + "="*70)
    print("TEST 4: duration_seconds() Method")
    print("="*70)
    
    time.sleep(0.1)
    execution.complete(products_found=10, matches_found=2)
    db.commit()
    
    duration = execution.duration_seconds()
    print(f"✅ Duration: {duration:.2f} seconds")
    
    assert duration > 0
    assert isinstance(duration, float)


def test_match_rate_calculation(db, execution):
    """Test match_rate() method."""
    print("\n" + "="*70)
    print("TEST 5: match_rate() Method")
    print("="*70)
    
    execution.complete(products_found=25, matches_found=3)
    db.commit()
    
    match_rate = execution.match_rate()
    expected_rate = (3 / 25) * 100
    
    print(f"✅ Match rate: {match_rate:.1f}%")
    print(f"   Expected: {expected_rate:.1f}%")
    
    assert abs(match_rate - expected_rate) < 0.01


def test_has_matches_method(db, execution):
    """Test has_matches() method."""
    print("\n" + "="*70)
    print("TEST 6: has_matches() Method")
    print("="*70)
    
    execution.complete(products_found=25, matches_found=3)
    db.commit()
    
    assert execution.has_matches() == True
    print("✅ has_matches() returns True when matches > 0")


def test_to_dict_method(db, execution):
    """Test to_dict() method."""
    print("\n" + "="*70)
    print("TEST 7: to_dict() Method")
    print("="*70)
    
    execution.complete(products_found=10, matches_found=2)
    db.commit()
    
    execution_dict = execution.to_dict()
    
    print("✅ Converted to dictionary:")
    for key in ['id', 'search_request_id', 'status', 'started_at', 'products_found', 'matches_found']:
        print(f"   - {key}: {execution_dict.get(key)}")
    
    assert 'id' in execution_dict
    assert 'status' in execution_dict
    assert 'started_at' in execution_dict
    assert execution_dict['products_found'] == 10
    assert execution_dict['matches_found'] == 2


def test_failed_execution(db, search):
    """Test fail() method."""
    print("\n" + "="*70)
    print("TEST 8: Failed Execution")
    print("="*70)
    
    failed_execution = SearchExecution(
        search_request_id=search.id,
        started_at=datetime.utcnow(),
        status=ExecutionStatus.RUNNING.value
    )
    db.add(failed_execution)
    db.commit()
    
    failed_execution.fail("Scraper timeout error")
    db.commit()
    
    print(f"✅ Failed execution created")
    print(f"   - Status: {failed_execution.status}")
    print(f"   - Error: {failed_execution.error_message}")
    
    assert failed_execution.status == ExecutionStatus.FAILED.value
    assert failed_execution.error_message == "Scraper timeout error"
    assert failed_execution.is_failed() == True
    assert failed_execution.is_completed() == False
    assert failed_execution.is_successful() == False


def test_cancelled_execution(db, search):
    """Test cancel() method."""
    print("\n" + "="*70)
    print("TEST 9: Cancelled Execution")
    print("="*70)
    
    cancelled_execution = SearchExecution(
        search_request_id=search.id,
        started_at=datetime.utcnow(),
        status=ExecutionStatus.RUNNING.value
    )
    db.add(cancelled_execution)
    db.commit()
    
    cancelled_execution.cancel()
    db.commit()
    
    print(f"✅ Cancelled execution created")
    print(f"   - Status: {cancelled_execution.status}")
    
    assert cancelled_execution.status == ExecutionStatus.CANCELLED.value
    assert cancelled_execution.completed_at is not None


def test_execution_with_no_matches(db, search):
    """Test execution with no matches."""
    print("\n" + "="*70)
    print("TEST 10: Execution With No Matches")
    print("="*70)
    
    no_match_execution = SearchExecution(
        search_request_id=search.id,
        started_at=datetime.utcnow(),
        status=ExecutionStatus.RUNNING.value
    )
    db.add(no_match_execution)
    db.commit()
    
    no_match_execution.complete(products_found=10, matches_found=0)
    db.commit()
    
    print(f"✅ No-match execution created")
    print(f"   - Products found: {no_match_execution.products_found}")
    print(f"   - Matches found: {no_match_execution.matches_found}")
    print(f"   - Has matches: {no_match_execution.has_matches()}")
    print(f"   - Match rate: {no_match_execution.match_rate():.1f}%")
    
    assert no_match_execution.has_matches() == False
    assert no_match_execution.match_rate() == 0.0


def test_query_executions(db, search, execution):
    """Test querying executions."""
    print("\n" + "="*70)
    print("TEST 11: Query Executions")
    print("="*70)
    
    # Create additional executions
    exec2 = SearchExecution(
        search_request_id=search.id,
        started_at=datetime.utcnow(),
        status=ExecutionStatus.RUNNING.value
    )
    db.add(exec2)
    exec2.complete(products_found=5, matches_found=1)
    db.commit()
    
    all_executions = db.query(SearchExecution).filter_by(
        search_request_id=search.id
    ).all()
    
    print(f"✅ Found {len(all_executions)} executions")
    assert len(all_executions) >= 2


def test_foreign_key_relationship(db, search, execution):
    """Test foreign key relationship."""
    print("\n" + "="*70)
    print("TEST 12: Foreign Key Relationship")
    print("="*70)
    
    queried_execution = db.query(SearchExecution).filter_by(
        id=execution.id
    ).first()
    
    assert queried_execution is not None
    assert queried_execution.search_request_id == search.id
    print("✅ Foreign key relationship working correctly")


def test_duration_with_no_completion(db, search):
    """Test duration_seconds() when execution is not completed."""
    print("\n" + "="*70)
    print("TEST 13: Duration With No Completion")
    print("="*70)
    
    running_execution = SearchExecution(
        search_request_id=search.id,
        started_at=datetime.utcnow(),
        status=ExecutionStatus.RUNNING.value
    )
    db.add(running_execution)
    db.commit()
    
    # Test duration when completed_at is None
    duration = running_execution.duration_seconds()
    print(f"✅ Duration for running execution: {duration}")
    
    assert duration == 0.0
    print("✅ duration_seconds() returns 0.0 when not completed")


def test_match_rate_with_no_products(db, search):
    """Test match_rate() when no products found."""
    print("\n" + "="*70)
    print("TEST 14: Match Rate With No Products")
    print("="*70)
    
    empty_execution = SearchExecution(
        search_request_id=search.id,
        started_at=datetime.utcnow(),
        status=ExecutionStatus.RUNNING.value
    )
    db.add(empty_execution)
    db.commit()
    
    empty_execution.complete(products_found=0, matches_found=0)
    db.commit()
    
    match_rate = empty_execution.match_rate()
    print(f"✅ Match rate with 0 products: {match_rate}")
    
    assert match_rate == 0.0
    print("✅ match_rate() returns 0.0 when products_found is 0")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

# Made with Bob
