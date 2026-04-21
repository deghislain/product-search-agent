# Task 2: Database Models - Sub-Implementation Plan

## Overview
This document breaks down Task 2 (Create database models) from Day 2 of the implementation plan into manageable subtasks. Each subtask is designed to be completed independently and includes clear objectives, code examples, and testing steps.

---

## Prerequisites
✅ Task 1 completed: Configuration module (`app/config.py`) is ready
✅ Virtual environment activated
✅ Dependencies installed (SQLAlchemy, Pydantic)

---

## Subtask Breakdown

### Subtask 2.1: Setup Database Connection (30 minutes)
**File:** `backend/app/database.py`

**Objective:** Create the database connection and session management using SQLAlchemy.

**What You'll Learn:**
- SQLAlchemy engine and session setup
- Database connection management
- Dependency injection pattern

**Steps:**
1. Create `backend/app/database.py`
2. Import SQLAlchemy components
3. Create database engine using settings from config
4. Setup session maker
5. Create dependency function for FastAPI

**Code Structure:**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

# Database engine
# Session factory
# Base class for models
# Dependency for FastAPI routes
```

**Testing:**
- Run the file to ensure no import errors
- Verify database file is created (if using SQLite)

**Success Criteria:**
- ✅ `database.py` file created
- ✅ No import errors
- ✅ Database connection can be established

---

### Subtask 2.2: Create Base Model and Enums (20 minutes)
**File:** `backend/app/models/__init__.py`

**Objective:** Create the base model class and enums that will be used across all models.

**What You'll Learn:**
- SQLAlchemy declarative base
- Python Enums for database fields
- Model inheritance

**Steps:**
1. Create `backend/app/models/` directory
2. Create `__init__.py` file
3. Define SearchStatus enum
4. Define NotificationType enum
5. Import Base from database module

**Code Structure:**
```python
from enum import Enum

class SearchStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class NotificationType(str, Enum):
    MATCH_FOUND = "match_found"
    SEARCH_STARTED = "search_started"
    SEARCH_COMPLETED = "search_completed"
    ERROR_OCCURRED = "error_occurred"
```

**Testing:**
- Import the enums in Python REPL
- Test enum values: `SearchStatus.ACTIVE.value`

**Success Criteria:**
- ✅ Enums defined correctly
- ✅ Can import enums without errors

---

### Subtask 2.3: Create SearchRequest Model (45 minutes)
**File:** `backend/app/models/search_request.py`

**Objective:** Create the SearchRequest model to store user search criteria.

**What You'll Learn:**
- SQLAlchemy Column types
- Primary keys and constraints
- Default values and timestamps
- Model relationships

**Database Fields:**
- `id` (Primary Key, String/UUID)
- `product_name` (String, required)
- `product_description` (Text, required)
- `budget` (Float, required)
- `location` (String, optional)
- `match_threshold` (Float, default 70.0)
- `status` (Enum, default 'active')
- `created_at` (DateTime, auto-generated)
- `updated_at` (DateTime, auto-updated)

**Steps:**
1. Create `backend/app/models/search_request.py`
2. Import necessary SQLAlchemy types
3. Define SearchRequest class inheriting from Base
4. Add all columns with appropriate types
5. Add `__repr__` method for debugging
6. Add relationship to search_executions (one-to-many)

**Code Template:**
```python
from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base
from app.models import SearchStatus

class SearchRequest(Base):
    __tablename__ = "search_requests"
    
    # Define columns here
    # id = Column(...)
    # product_name = Column(...)
    # etc.
    
    # Relationships
    # executions = relationship(...)
    
    def __repr__(self):
        return f"<SearchRequest(id={self.id}, product={self.product_name})>"
```

**Testing:**
- Create a test script to instantiate the model
- Verify all fields are accessible
- Check default values work correctly

**Success Criteria:**
- ✅ Model class created with all fields
- ✅ Can create instance without errors
- ✅ Default values work correctly

---

### Subtask 2.4: Create SearchExecution Model (40 minutes)
**File:** `backend/app/models/search_execution.py`

**Objective:** Create the SearchExecution model to track each search run.

**What You'll Learn:**
- Foreign key relationships
- Nullable fields
- Status tracking
- Execution metrics

**Database Fields:**
- `id` (Primary Key, String/UUID)
- `search_request_id` (Foreign Key to search_requests)
- `started_at` (DateTime, required)
- `completed_at` (DateTime, nullable)
- `status` (String, default 'running')
- `products_found` (Integer, default 0)
- `matches_found` (Integer, default 0)
- `error_message` (Text, nullable)

**Steps:**
1. Create `backend/app/models/search_execution.py`
2. Import necessary types including ForeignKey
3. Define SearchExecution class
4. Add foreign key to search_requests
5. Add relationship back to SearchRequest
6. Add relationship to products (one-to-many)
7. Add `__repr__` method

**Code Template:**
```python
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base

class SearchExecution(Base):
    __tablename__ = "search_executions"
    
    # Define columns
    # id = Column(...)
    # search_request_id = Column(String, ForeignKey('search_requests.id'))
    # etc.
    
    # Relationships
    # search_request = relationship("SearchRequest", back_populates="executions")
    # products = relationship(...)
```

**Testing:**
- Create test instances
- Verify foreign key relationship
- Test nullable fields

**Success Criteria:**
- ✅ Model created with all fields
- ✅ Foreign key relationship defined
- ✅ Can link to SearchRequest

---

### Subtask 2.5: Create Product Model (45 minutes)
**File:** `backend/app/models/product.py`

**Objective:** Create the Product model to store scraped product information.

**What You'll Learn:**
- Multiple foreign keys
- Boolean fields
- Optional fields
- Complex relationships

**Database Fields:**
- `id` (Primary Key, String/UUID)
- `search_execution_id` (Foreign Key to search_executions)
- `title` (String, required)
- `description` (Text, nullable)
- `price` (Float, required)
- `url` (String, required)
- `image_url` (String, nullable)
- `platform` (String, required - 'craigslist', 'facebook', 'ebay')
- `location` (String, nullable)
- `posted_date` (DateTime, nullable)
- `match_score` (Float, nullable)
- `is_match` (Boolean, default False)
- `created_at` (DateTime, auto-generated)

**Steps:**
1. Create `backend/app/models/product.py`
2. Import necessary types
3. Define Product class
4. Add all columns
5. Add foreign key to search_executions
6. Add relationship to SearchExecution
7. Add relationship to notifications
8. Add `__repr__` method
9. Add helper method `is_good_match()` to check if match_score > threshold

**Code Template:**
```python
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base

class Product(Base):
    __tablename__ = "products"
    
    # Define columns
    # id = Column(...)
    # search_execution_id = Column(String, ForeignKey('search_executions.id'))
    # etc.
    
    # Relationships
    # search_execution = relationship(...)
    
    def is_good_match(self, threshold: float = 70.0) -> bool:
        """Check if product meets match threshold"""
        return self.match_score is not None and self.match_score >= threshold
```

**Testing:**
- Create product instances
- Test `is_good_match()` method
- Verify relationships work

**Success Criteria:**
- ✅ Model created with all fields
- ✅ Foreign key relationship works
- ✅ Helper method functions correctly

---

### Subtask 2.6: Create Notification Model (40 minutes)
**File:** `backend/app/models/notification.py`

**Objective:** Create the Notification model to store user notifications.

**What You'll Learn:**
- Multiple foreign keys (one nullable)
- Enum fields in database
- Read/unread tracking

**Database Fields:**
- `id` (Primary Key, String/UUID)
- `search_request_id` (Foreign Key to search_requests)
- `product_id` (Foreign Key to products, nullable)
- `type` (Enum: NotificationType)
- `message` (Text, required)
- `read` (Boolean, default False)
- `created_at` (DateTime, auto-generated)

**Steps:**
1. Create `backend/app/models/notification.py`
2. Import necessary types and NotificationType enum
3. Define Notification class
4. Add all columns including enum type
5. Add foreign keys (product_id is nullable)
6. Add relationships
7. Add `__repr__` method
8. Add helper method `mark_as_read()`

**Code Template:**
```python
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base
from app.models import NotificationType

class Notification(Base):
    __tablename__ = "notifications"
    
    # Define columns
    # type = Column(Enum(NotificationType), nullable=False)
    # etc.
    
    # Relationships
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.read = True
```

**Testing:**
- Create notification instances
- Test `mark_as_read()` method
- Verify enum values work

**Success Criteria:**
- ✅ Model created with all fields
- ✅ Enum type works correctly
- ✅ Helper method functions

---

### Subtask 2.7: Create Database Initialization Script (30 minutes)
**File:** `backend/app/models/init_db.py`

**Objective:** Create a script to initialize the database and create all tables.

**What You'll Learn:**
- Database table creation
- SQLAlchemy metadata
- Database initialization patterns

**Steps:**
1. Create `backend/app/models/init_db.py`
2. Import all models
3. Import Base and engine from database
4. Create function to initialize database
5. Add function to drop all tables (for development)
6. Add main block to run initialization

**Code Template:**
```python
from app.database import Base, engine
from app.models.search_request import SearchRequest
from app.models.search_execution import SearchExecution
from app.models.product import Product
from app.models.notification import Notification

def init_db():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def drop_db():
    """Drop all database tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All database tables dropped!")

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
```

**Testing:**
- Run the script: `python -m app.models.init_db`
- Check that database file is created
- Verify tables exist (use SQLite browser or SQL query)

**Success Criteria:**
- ✅ Script runs without errors
- ✅ All tables created in database
- ✅ Can verify tables exist

---

### Subtask 2.8: Update Models __init__.py (15 minutes)
**File:** `backend/app/models/__init__.py`

**Objective:** Export all models from the models package for easy importing.

**What You'll Learn:**
- Python package structure
- Clean imports
- Module organization

**Steps:**
1. Update `backend/app/models/__init__.py`
2. Import all model classes
3. Import enums
4. Add `__all__` list for explicit exports

**Code Template:**
```python
from app.models.search_request import SearchRequest
from app.models.search_execution import SearchExecution
from app.models.product import Product
from app.models.notification import Notification

# Enums
from enum import Enum

class SearchStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class NotificationType(str, Enum):
    MATCH_FOUND = "match_found"
    SEARCH_STARTED = "search_started"
    SEARCH_COMPLETED = "search_completed"
    ERROR_OCCURRED = "error_occurred"

__all__ = [
    "SearchRequest",
    "SearchExecution",
    "Product",
    "Notification",
    "SearchStatus",
    "NotificationType",
]
```

**Testing:**
- Test imports: `from app.models import SearchRequest, Product`
- Verify all models are accessible

**Success Criteria:**
- ✅ All models exported
- ✅ Clean import syntax works
- ✅ No circular import issues

---

### Subtask 2.9: Create Database Indexes (20 minutes)
**File:** Update model files

**Objective:** Add database indexes for better query performance.

**What You'll Learn:**
- Database indexing
- Query optimization
- SQLAlchemy Index class

**Steps:**
1. Add indexes to SearchRequest model (status field)
2. Add composite index to Product model (is_match, match_score)
3. Add composite index to Notification model (read, created_at)

**Code Example:**
```python
from sqlalchemy import Index

# In SearchRequest model
__table_args__ = (
    Index('idx_search_requests_status', 'status'),
)

# In Product model
__table_args__ = (
    Index('idx_products_match', 'is_match', 'match_score'),
)

# In Notification model
__table_args__ = (
    Index('idx_notifications_unread', 'read', 'created_at'),
)
```

**Testing:**
- Re-run init_db.py
- Verify indexes are created (check database schema)

**Success Criteria:**
- ✅ Indexes added to models
- ✅ Database recreated with indexes
- ✅ No errors during creation

---

### Subtask 2.10: Create Test Script (30 minutes)
**File:** `backend/app/models/test_models.py`

**Objective:** Create a comprehensive test script to verify all models work correctly.

**What You'll Learn:**
- Database CRUD operations
- Model relationships
- Testing patterns

**Steps:**
1. Create test script
2. Test creating each model
3. Test relationships between models
4. Test querying models
5. Test updating and deleting

**Code Template:**
```python
from app.database import SessionLocal
from app.models import SearchRequest, SearchExecution, Product, Notification
from app.models import SearchStatus, NotificationType
from datetime import datetime

def test_models():
    """Test all database models"""
    db = SessionLocal()
    
    try:
        # Test 1: Create SearchRequest
        print("Test 1: Creating SearchRequest...")
        search = SearchRequest(
            product_name="iPhone 13",
            product_description="Looking for iPhone 13 in good condition",
            budget=500.0,
            location="Boston, MA",
            status=SearchStatus.ACTIVE
        )
        db.add(search)
        db.commit()
        print(f"✅ Created: {search}")
        
        # Test 2: Create SearchExecution
        print("\nTest 2: Creating SearchExecution...")
        execution = SearchExecution(
            search_request_id=search.id,
            started_at=datetime.utcnow(),
            status="running"
        )
        db.add(execution)
        db.commit()
        print(f"✅ Created: {execution}")
        
        # Test 3: Create Product
        print("\nTest 3: Creating Product...")
        product = Product(
            search_execution_id=execution.id,
            title="iPhone 13 128GB Blue",
            description="Excellent condition, barely used",
            price=450.0,
            url="https://example.com/product/123",
            platform="craigslist",
            match_score=85.5,
            is_match=True
        )
        db.add(product)
        db.commit()
        print(f"✅ Created: {product}")
        
        # Test 4: Create Notification
        print("\nTest 4: Creating Notification...")
        notification = Notification(
            search_request_id=search.id,
            product_id=product.id,
            type=NotificationType.MATCH_FOUND,
            message=f"Found match: {product.title} for ${product.price}"
        )
        db.add(notification)
        db.commit()
        print(f"✅ Created: {notification}")
        
        # Test 5: Query with relationships
        print("\nTest 5: Testing relationships...")
        search_with_executions = db.query(SearchRequest).filter_by(id=search.id).first()
        print(f"Search has {len(search_with_executions.executions)} executions")
        print(f"Execution has {len(execution.products)} products")
        
        # Test 6: Update operations
        print("\nTest 6: Testing updates...")
        notification.mark_as_read()
        db.commit()
        print(f"✅ Notification marked as read: {notification.read}")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_models()
```

**Testing:**
- Run the test script: `python -m app.models.test_models`
- Verify all operations succeed
- Check database for created records

**Success Criteria:**
- ✅ All CRUD operations work
- ✅ Relationships function correctly
- ✅ No errors during execution

---

## Final Checklist

Before moving to Task 3, ensure:

- [ ] **Subtask 2.1**: Database connection setup complete
- [ ] **Subtask 2.2**: Enums defined
- [ ] **Subtask 2.3**: SearchRequest model created
- [ ] **Subtask 2.4**: SearchExecution model created
- [ ] **Subtask 2.5**: Product model created
- [ ] **Subtask 2.6**: Notification model created
- [ ] **Subtask 2.7**: Database initialization script works
- [ ] **Subtask 2.8**: Models package properly organized
- [ ] **Subtask 2.9**: Indexes added for performance
- [ ] **Subtask 2.10**: Test script passes all tests

---

## Common Issues & Solutions

### Issue 1: Import Errors
**Problem:** Circular imports or module not found
**Solution:** 
- Check your Python path
- Ensure you're running from the correct directory
- Use relative imports within the app package

### Issue 2: Database Locked
**Problem:** SQLite database is locked
**Solution:**
- Close all database connections
- Delete the .db file and recreate
- Use `db.close()` in finally blocks

### Issue 3: Foreign Key Errors
**Problem:** Foreign key constraint fails
**Solution:**
- Ensure parent record exists before creating child
- Check that foreign key values match
- Verify relationship definitions are correct

### Issue 4: Column Type Errors
**Problem:** Wrong data type for column
**Solution:**
- Check SQLAlchemy column type matches Python type
- Use appropriate converters (e.g., str() for UUIDs)
- Verify nullable settings

---

## Estimated Time

| Subtask | Time | Difficulty |
|---------|------|------------|
| 2.1 Database Connection | 30 min | Easy |
| 2.2 Enums | 20 min | Easy |
| 2.3 SearchRequest Model | 45 min | Medium |
| 2.4 SearchExecution Model | 40 min | Medium |
| 2.5 Product Model | 45 min | Medium |
| 2.6 Notification Model | 40 min | Medium |
| 2.7 Init Script | 30 min | Easy |
| 2.8 Package Organization | 15 min | Easy |
| 2.9 Indexes | 20 min | Easy |
| 2.10 Testing | 30 min | Medium |
| **Total** | **~5 hours** | **Medium** |

---

## Next Steps

After completing Task 2, you'll be ready for:
- **Task 3**: Create Pydantic schemas for API validation
- **Task 4**: Setup FastAPI application with database integration

---

## Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)
- [Python Enums](https://docs.python.org/3/library/enum.html)
- [Database Indexing Best Practices](https://use-the-index-luke.com/)

---

**Good luck! Take your time with each subtask and don't hesitate to test frequently. 🚀**