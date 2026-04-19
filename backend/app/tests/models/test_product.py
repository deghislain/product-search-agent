"""
Test script for Product model.

This script tests the Product model functionality including:
- Creating product instances
- Helper methods
- Relationships (when enabled)
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
from app.models import Product, SearchExecution, SearchRequest, SearchStatus, ExecutionStatus


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
        budget=600.0,
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


@pytest.fixture
def product(db, execution):
    """Create a test Product."""
    product = Product(
        search_execution_id=execution.id,
        title="iPhone 13 128GB Blue - Excellent Condition",
        description="Barely used iPhone 13 with 128GB storage. Comes with original box and charger.",
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


def test_product_creation(product, search, execution):
    """Test creating a Product instance."""
    print("\n" + "="*70)
    print("TEST 1: Product Creation")
    print("="*70)
    
    print(f"✅ Created SearchRequest: {search.id}")
    print(f"✅ Created SearchExecution: {execution.id}")
    print(f"✅ Created Product: {product.id}")
    print(f"   Title: {product.title}")
    print(f"   Price: ${product.price:.2f}")
    print(f"   Platform: {product.platform}")
    print(f"   Match Score: {product.match_score}%")
    print(f"   Is Match: {product.is_match}")
    
    assert product.id is not None
    assert product.title == "iPhone 13 128GB Blue - Excellent Condition"
    assert product.price == 450.0
    assert product.platform == "craigslist"
    assert product.match_score == 85.5
    assert product.is_match == True


def test_product_methods(db, product):
    """Test Product helper methods."""
    print("\n" + "="*70)
    print("TEST 2: Product Helper Methods")
    print("="*70)
    
    # Test is_good_match
    print(f"\n1. Testing is_good_match():")
    print(f"   Match score: {product.match_score}%")
    print(f"   is_good_match(70.0): {product.is_good_match(70.0)}")
    print(f"   is_good_match(90.0): {product.is_good_match(90.0)}")
    assert product.is_good_match(70.0) == True
    assert product.is_good_match(90.0) == False
    
    # Test is_within_budget
    print(f"\n2. Testing is_within_budget():")
    print(f"   Price: ${product.price:.2f}")
    print(f"   is_within_budget(500.0): {product.is_within_budget(500.0)}")
    print(f"   is_within_budget(400.0): {product.is_within_budget(400.0)}")
    assert product.is_within_budget(500.0) == True
    assert product.is_within_budget(400.0) == False
    
    # Test get_short_title
    print(f"\n3. Testing get_short_title():")
    print(f"   Full title: {product.title}")
    print(f"   Short (30 chars): {product.get_short_title(30)}")
    print(f"   Short (50 chars): {product.get_short_title(50)}")
    assert len(product.get_short_title(30)) <= 30
    
    # Test days_since_posted
    print(f"\n4. Testing days_since_posted():")
    print(f"   Posted date: {product.posted_date}")
    print(f"   Days since posted: {product.days_since_posted()}")
    assert product.days_since_posted() >= 2
    
    # Test is_recent
    print(f"\n5. Testing is_recent():")
    print(f"   is_recent(7 days): {product.is_recent(7)}")
    print(f"   is_recent(1 day): {product.is_recent(1)}")
    assert product.is_recent(7) == True
    assert product.is_recent(1) == False
    
    # Test to_dict
    print(f"\n6. Testing to_dict():")
    product_dict = product.to_dict()
    print(f"   Dictionary keys: {list(product_dict.keys())}")
    print(f"   Title from dict: {product_dict['title']}")
    print(f"   Price from dict: ${product_dict['price']:.2f}")
    assert 'title' in product_dict
    assert 'price' in product_dict
    assert product_dict['title'] == product.title
    
    print("\n✅ All helper methods work correctly!")


def test_product_marking(db, execution):
    """Test marking products as match/non-match."""
    print("\n" + "="*70)
    print("TEST 3: Product Marking Methods")
    print("="*70)
    
    # Create a new product
    product = Product(
        search_execution_id=execution.id,
        title="iPhone 12 64GB - Fair Condition",
        description="Used iPhone 12, some scratches",
        price=350.0,
        url="https://boston.craigslist.org/product/789012",
        platform="craigslist",
        location="Boston, MA"
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    print(f"✅ Created test product: {product.id}")
    print(f"   Initial is_match: {product.is_match}")
    print(f"   Initial match_score: {product.match_score}")
    
    # Mark as match
    print(f"\n1. Marking as match with score 75.0:")
    product.mark_as_match(75.0)
    db.commit()
    print(f"   is_match: {product.is_match}")
    print(f"   match_score: {product.match_score}")
    assert product.is_match == True
    assert product.match_score == 75.0
    
    # Mark as non-match
    print(f"\n2. Marking as non-match with score 45.0:")
    product.mark_as_non_match(45.0)
    db.commit()
    print(f"   is_match: {product.is_match}")
    print(f"   match_score: {product.match_score}")
    assert product.is_match == False
    assert product.match_score == 45.0
    
    # Mark as non-match without score
    print(f"\n3. Marking as non-match without score:")
    product.mark_as_non_match()
    db.commit()
    print(f"   is_match: {product.is_match}")
    print(f"   match_score: {product.match_score}")
    assert product.is_match == False
    
    print("\n✅ Product marking methods work correctly!")


def test_product_queries(db, product):
    """Test querying products."""
    print("\n" + "="*70)
    print("TEST 4: Product Queries")
    print("="*70)
    
    # Query all products
    all_products = db.query(Product).all()
    print(f"✅ Total products in database: {len(all_products)}")
    assert len(all_products) >= 1
    
    # Query products by platform
    craigslist_products = db.query(Product).filter_by(platform="craigslist").all()
    print(f"✅ Craigslist products: {len(craigslist_products)}")
    assert len(craigslist_products) >= 1
    
    # Query matched products
    matched_products = db.query(Product).filter_by(is_match=True).all()
    print(f"✅ Matched products: {len(matched_products)}")
    
    # Query products within price range
    budget_products = db.query(Product).filter(Product.price <= 500.0).all()
    print(f"✅ Products under $500: {len(budget_products)}")
    assert len(budget_products) >= 1
    
    # Query products with high match score
    high_score_products = db.query(Product).filter(Product.match_score >= 80.0).all()
    print(f"✅ Products with score >= 80: {len(high_score_products)}")
    
    print("\n✅ All queries executed successfully!")


def test_product_without_posted_date(db, execution):
    """Test product methods when posted_date is None."""
    print("\n" + "="*70)
    print("TEST 5: Product Without Posted Date")
    print("="*70)
    
    # Create a product without posted_date
    product = Product(
        search_execution_id=execution.id,
        title="Product Without Date",
        description="Test product",
        price=100.0,
        url="https://example.com/test",
        platform="craigslist",
        location="Test City",
        posted_date=None  # Explicitly set to None
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    print(f"✅ Created product without posted_date: {product.id}")
    print(f"   posted_date: {product.posted_date}")
    
    # Test days_since_posted with None posted_date
    print(f"\n1. Testing days_since_posted() with None posted_date:")
    days = product.days_since_posted()
    print(f"   days_since_posted(): {days}")
    assert days == 0
    
    # Test is_recent with None posted_date
    print(f"\n2. Testing is_recent() with None posted_date:")
    is_recent = product.is_recent(7)
    print(f"   is_recent(7): {is_recent}")
    assert is_recent == False
    
    print("\n✅ Edge cases for None posted_date handled correctly!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

# Made with Bob
