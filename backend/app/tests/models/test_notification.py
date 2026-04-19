"""
Test script for Notification model.

This script tests the Notification model functionality including:
- Creating notification instances
- Helper methods
- Enum types
- Read/unread tracking
"""

import sys
from pathlib import Path

# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import (
    Notification,
    NotificationType,
    SearchRequest,
    SearchExecution,
    Product,
    SearchStatus,
    ExecutionStatus
)


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
        product_description="Looking for iPhone 13",
        budget=600.0,
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
        title="iPhone 13 128GB",
        price=450.0,
        url="https://example.com/product/123",
        platform="craigslist",
        match_score=85.5,
        is_match=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@pytest.fixture
def notifications(db, search, product):
    """Create test notifications of different types."""
    notifs = []
    
    # Match found notification
    notif1 = Notification(
        search_request_id=search.id,
        product_id=product.id,
        type=NotificationType.MATCH_FOUND,
        message=f"Found match: {product.title} for ${product.price}"
    )
    db.add(notif1)
    notifs.append(notif1)
    
    # Search started notification
    notif2 = Notification(
        search_request_id=search.id,
        type=NotificationType.SEARCH_STARTED,
        message="Search for iPhone 13 has started"
    )
    db.add(notif2)
    notifs.append(notif2)
    
    # Search completed notification
    notif3 = Notification(
        search_request_id=search.id,
        type=NotificationType.SEARCH_COMPLETED,
        message="Search completed. Found 5 products, 2 matches."
    )
    db.add(notif3)
    notifs.append(notif3)
    
    # Error notification
    notif4 = Notification(
        search_request_id=search.id,
        type=NotificationType.ERROR_OCCURRED,
        message="Failed to scrape Craigslist: Connection timeout"
    )
    db.add(notif4)
    notifs.append(notif4)
    
    db.commit()
    for notif in notifs:
        db.refresh(notif)
    
    return notifs


def test_notification_creation(notifications, search, product):
    """Test creating Notification instances."""
    print("\n" + "="*70)
    print("TEST 1: Notification Creation")
    print("="*70)
    
    print(f"✅ Created SearchRequest: {search.id}")
    print(f"✅ Created Product: {product.id}")
    
    print(f"\n✅ Created {len(notifications)} notifications:")
    for notif in notifications:
        print(f"   - {notif.type.value}: {notif.get_short_message(40)}")
        print(f"     ID: {notif.id}, Read: {notif.read}")
    
    assert len(notifications) == 4
    assert notifications[0].type == NotificationType.MATCH_FOUND
    assert notifications[1].type == NotificationType.SEARCH_STARTED
    assert notifications[2].type == NotificationType.SEARCH_COMPLETED
    assert notifications[3].type == NotificationType.ERROR_OCCURRED


def test_notification_methods(db, notifications):
    """Test Notification helper methods."""
    print("\n" + "="*70)
    print("TEST 2: Notification Helper Methods")
    print("="*70)
    
    # Get the match notification
    notification = notifications[0]  # First one is MATCH_FOUND
    
    print(f"\nTesting with notification: {notification.id}")
    print(f"Type: {notification.type.value}")
    print(f"Message: {notification.message}")
    
    # Test is_read/is_unread
    print(f"\n1. Testing read status:")
    print(f"   is_read(): {notification.is_read()}")
    print(f"   is_unread(): {notification.is_unread()}")
    assert notification.is_unread() == True
    assert notification.is_read() == False
    
    # Test mark_as_read
    print(f"\n2. Testing mark_as_read():")
    notification.mark_as_read()
    db.commit()
    print(f"   After marking as read:")
    print(f"   is_read(): {notification.is_read()}")
    print(f"   is_unread(): {notification.is_unread()}")
    assert notification.is_read() == True
    assert notification.is_unread() == False
    
    # Test mark_as_unread
    print(f"\n3. Testing mark_as_unread():")
    notification.mark_as_unread()
    db.commit()
    print(f"   After marking as unread:")
    print(f"   is_read(): {notification.is_read()}")
    print(f"   is_unread(): {notification.is_unread()}")
    assert notification.is_unread() == True
    
    # Test type checking methods
    print(f"\n4. Testing type checking methods:")
    print(f"   is_match_notification(): {notification.is_match_notification()}")
    print(f"   is_error_notification(): {notification.is_error_notification()}")
    assert notification.is_match_notification() == True
    assert notification.is_error_notification() == False
    
    # Test has_product
    print(f"\n5. Testing has_product():")
    print(f"   has_product(): {notification.has_product()}")
    print(f"   product_id: {notification.product_id}")
    assert notification.has_product() == True
    
    # Test age methods
    print(f"\n6. Testing age methods:")
    print(f"   age_seconds(): {notification.age_seconds():.2f}")
    print(f"   age_minutes(): {notification.age_minutes():.2f}")
    print(f"   age_hours(): {notification.age_hours():.4f}")
    print(f"   is_recent(60): {notification.is_recent(60)}")
    assert notification.age_seconds() >= 0
    assert notification.is_recent(60) == True
    
    # Test get_short_message
    print(f"\n7. Testing get_short_message():")
    print(f"   Full message: {notification.message}")
    print(f"   Short (30 chars): {notification.get_short_message(30)}")
    print(f"   Short (50 chars): {notification.get_short_message(50)}")
    assert len(notification.get_short_message(30)) <= 30
    
    # Test to_dict
    print(f"\n8. Testing to_dict():")
    notif_dict = notification.to_dict()
    print(f"   Dictionary keys: {list(notif_dict.keys())}")
    print(f"   Type from dict: {notif_dict['type']}")
    print(f"   Read from dict: {notif_dict['read']}")
    assert 'id' in notif_dict
    assert 'type' in notif_dict
    
    print("\n✅ All helper methods work correctly!")


def test_notification_types(db, notifications):
    """Test different notification types."""
    print("\n" + "="*70)
    print("TEST 3: Notification Types")
    print("="*70)
    
    # Get notifications of each type
    for notif_type in NotificationType:
        type_notifs = [n for n in notifications if n.type == notif_type]
        print(f"\n{notif_type.value}:")
        print(f"   Count: {len(type_notifs)}")
        
        if type_notifs:
            notif = type_notifs[0]
            print(f"   Example: {notif.get_short_message(50)}")
            print(f"   is_match_notification(): {notif.is_match_notification()}")
            print(f"   is_error_notification(): {notif.is_error_notification()}")
    
    print("\n✅ All notification types work correctly!")
    assert len(notifications) == 4


def test_notification_queries(db, notifications):
    """Test querying notifications."""
    print("\n" + "="*70)
    print("TEST 4: Notification Queries")
    print("="*70)
    
    # Query all notifications
    all_notifs = db.query(Notification).all()
    print(f"✅ Total notifications: {len(all_notifs)}")
    assert len(all_notifs) >= 4
    
    # Query unread notifications
    unread_notifs = db.query(Notification).filter_by(read=False).all()
    print(f"✅ Unread notifications: {len(unread_notifs)}")
    
    # Query read notifications
    read_notifs = db.query(Notification).filter_by(read=True).all()
    print(f"✅ Read notifications: {len(read_notifs)}")
    
    # Query match notifications
    match_notifs = db.query(Notification).filter_by(
        type=NotificationType.MATCH_FOUND
    ).all()
    print(f"✅ Match notifications: {len(match_notifs)}")
    assert len(match_notifs) >= 1
    
    # Query error notifications
    error_notifs = db.query(Notification).filter_by(
        type=NotificationType.ERROR_OCCURRED
    ).all()
    print(f"✅ Error notifications: {len(error_notifs)}")
    assert len(error_notifs) >= 1
    
    # Query notifications with products
    product_notifs = db.query(Notification).filter(
        Notification.product_id.isnot(None)
    ).all()
    print(f"✅ Notifications with products: {len(product_notifs)}")
    assert len(product_notifs) >= 1
    
    # Query recent notifications (last hour)
    recent_time = datetime.utcnow() - timedelta(hours=1)
    recent_notifs = db.query(Notification).filter(
        Notification.created_at >= recent_time
    ).all()
    print(f"✅ Recent notifications (last hour): {len(recent_notifs)}")
    
    print("\n✅ All queries executed successfully!")


def test_notification_read_tracking(db, notifications):
    """Test read/unread tracking."""
    print("\n" + "="*70)
    print("TEST 5: Read/Unread Tracking")
    print("="*70)
    
    # Get all unread notifications
    unread = db.query(Notification).filter_by(read=False).all()
    print(f"Initial unread count: {len(unread)}")
    initial_unread = len(unread)
    
    # Mark half as read
    half = len(unread) // 2
    if half > 0:
        for notif in unread[:half]:
            notif.mark_as_read()
        db.commit()
        
        # Check counts
        unread_after = db.query(Notification).filter_by(read=False).count()
        read_after = db.query(Notification).filter_by(read=True).count()
        
        print(f"\nAfter marking {half} as read:")
        print(f"   Unread: {unread_after}")
        print(f"   Read: {read_after}")
        assert unread_after == initial_unread - half
    
    # Mark all as unread
    all_notifs = db.query(Notification).all()
    for notif in all_notifs:
        notif.mark_as_unread()
    db.commit()
    
    unread_final = db.query(Notification).filter_by(read=False).count()
    print(f"\nAfter marking all as unread:")
    print(f"   Unread: {unread_final}")
    assert unread_final == len(all_notifs)
    
    print("\n✅ Read/unread tracking works correctly!")


if __name__ == "__main__":
    # Run tests with pytest
    import pytest
    sys.exit(pytest.main([__file__, "-vv", "-s"]))

# Made with Bob
