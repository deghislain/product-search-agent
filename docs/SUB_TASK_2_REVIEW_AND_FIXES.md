# Sub-Task 2 Review: Email Preference Model & Schema

## ❌ Critical Issues Found

Your Sub-Task 2 implementation has **several critical issues** that prevent it from working. Here's what needs to be fixed:

---

## Issue 1: Wrong Base Class (CRITICAL)

**Location:** `backend/app/models/email_preference.py`

**Problem:** You're using Pydantic's `BaseModel` instead of SQLAlchemy's `Base` class.

**Current Code (WRONG):**
```python
from pydantic import Field, BaseModel

class EmailPreference(BaseModel):  # ❌ This is for API schemas, not database models!
    __tablename__ = "email_preferences"
```

**Why it's wrong:**
- `BaseModel` is from Pydantic - used for API request/response validation
- Database models must use SQLAlchemy's `Base` class
- This won't create a database table
- The fields won't be stored in the database

**Correct Code:**
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class EmailPreference(Base):  # ✅ SQLAlchemy model
    __tablename__ = "email_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    search_request_id = Column(
        Integer, 
        ForeignKey("search_requests.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    email_address = Column(String, nullable=False, index=True)
    notify_on_match = Column(Boolean, default=True, nullable=False)
    notify_on_start = Column(Boolean, default=True, nullable=False)
    include_in_digest = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    # Relationship to SearchRequest
    search_request = relationship("SearchRequest", back_populates="email_preferences")
    
    def __repr__(self):
        return f"<EmailPreference(id={self.id}, email={self.email_address})>"
```

---

## Issue 2: Missing Pydantic Schema

**Problem:** You created a model but no schema. You need BOTH:
- **Model** (SQLAlchemy) - for database storage
- **Schema** (Pydantic) - for API validation

**What's missing:** `backend/app/schemas/email_preference.py`

**Need to create this file:**

```python
"""
Pydantic schemas for email preference API validation.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class EmailPreferenceBase(BaseModel):
    """Base schema with common fields"""
    email_address: EmailStr = Field(
        ..., 
        description="Email address for notifications"
    )
    notify_on_match: bool = Field(
        default=True, 
        description="Send email when match found"
    )
    notify_on_start: bool = Field(
        default=True, 
        description="Send email when search starts"
    )
    include_in_digest: bool = Field(
        default=True, 
        description="Include in daily digest"
    )


class EmailPreferenceCreate(EmailPreferenceBase):
    """Schema for creating email preferences"""
    search_request_id: int = Field(
        ..., 
        description="ID of the search request",
        gt=0
    )


class EmailPreferenceUpdate(BaseModel):
    """Schema for updating email preferences (all fields optional)"""
    email_address: Optional[EmailStr] = None
    notify_on_match: Optional[bool] = None
    notify_on_start: Optional[bool] = None
    include_in_digest: Optional[bool] = None


class EmailPreferenceResponse(EmailPreferenceBase):
    """Schema for API responses"""
    id: int
    search_request_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models
```

---

## Issue 3: Schema Not Registered

**Location:** `backend/app/schemas/__init__.py`

**Problem:** Your new schema isn't imported or exported.

**Add these lines:**

```python
# Add to imports section (around line 49)
from app.schemas.email_preference import (
    EmailPreferenceBase,
    EmailPreferenceCreate,
    EmailPreferenceUpdate,
    EmailPreferenceResponse,
)

# Add to __all__ list (around line 80)
__all__ = [
    # ... existing exports ...
    # Email Preference
    "EmailPreferenceBase",
    "EmailPreferenceCreate",
    "EmailPreferenceUpdate",
    "EmailPreferenceResponse",
]
```

---

## Issue 4: Model Not Registered

**Location:** `backend/app/models/__init__.py`

**Problem:** Your new model isn't imported or exported.

**Add these lines:**

```python
# Add to imports (around line 162)
from app.models.email_preference import EmailPreference

# Add to __all__ list (around line 179)
__all__ = [
    # ... existing exports ...
    "EmailPreference",  # Add this
]

# Update get_all_models() function (around line 208)
def get_all_models() -> list:
    return [
        SearchRequest, 
        SearchExecution, 
        Product, 
        Notification,
        EmailPreference  # Add this
    ]
```

---

## Issue 5: Missing Relationship in SearchRequest

**Location:** `backend/app/models/search_request.py`

**Problem:** SearchRequest needs a relationship back to EmailPreference.

**Add this to SearchRequest class:**

```python
# In the SearchRequest class, add this relationship
email_preferences = relationship(
    "EmailPreference",
    back_populates="search_request",
    cascade="all, delete-orphan"  # Delete preferences when search is deleted
)
```

---

## Issue 6: Database Not Updated

**Problem:** The new table doesn't exist in your database yet.

**Solution:** Run database initialization:

```bash
cd backend
python -m app.models.init_db
```

This will create the `email_preferences` table.

---

## 📋 Complete Fix Checklist

### Step 1: Fix Model File ✅
- [ ] Replace `backend/app/models/email_preference.py` with correct SQLAlchemy model
- [ ] Use `Base` not `BaseModel`
- [ ] Use SQLAlchemy `Column` not Pydantic `Field`
- [ ] Add relationship to SearchRequest

### Step 2: Create Schema File ✅
- [ ] Create `backend/app/schemas/email_preference.py`
- [ ] Add EmailPreferenceBase
- [ ] Add EmailPreferenceCreate
- [ ] Add EmailPreferenceUpdate
- [ ] Add EmailPreferenceResponse

### Step 3: Register Schema ✅
- [ ] Update `backend/app/schemas/__init__.py`
- [ ] Import email preference schemas
- [ ] Add to `__all__` list

### Step 4: Register Model ✅
- [ ] Update `backend/app/models/__init__.py`
- [ ] Import EmailPreference model
- [ ] Add to `__all__` list
- [ ] Update `get_all_models()` function

### Step 5: Update SearchRequest ✅
- [ ] Add `email_preferences` relationship to SearchRequest model

### Step 6: Apply Database Changes ✅
- [ ] Run `python -m app.models.init_db`
- [ ] Verify table created

---

## 🎓 Understanding the Difference

### SQLAlchemy Model (Database Layer)
```python
from app.database import Base
from sqlalchemy import Column, Integer

class EmailPreference(Base):  # ← SQLAlchemy
    __tablename__ = "email_preferences"
    id = Column(Integer, primary_key=True)  # ← Database column
```

**Purpose:** Store data in database  
**Used by:** Database operations (queries, inserts, updates)  
**Location:** `app/models/`

### Pydantic Schema (API Layer)
```python
from pydantic import BaseModel, Field

class EmailPreferenceCreate(BaseModel):  # ← Pydantic
    email_address: str = Field(...)  # ← API field validation
```

**Purpose:** Validate API requests/responses  
**Used by:** FastAPI endpoints  
**Location:** `app/schemas/`

### Why You Need Both:
1. **Model** - Stores data in database
2. **Schema** - Validates data from API requests
3. FastAPI converts between them automatically

---

## 🔄 Correct Flow

```
API Request (JSON)
    ↓
Pydantic Schema (validates)
    ↓
SQLAlchemy Model (saves to DB)
    ↓
Database Table
    ↓
SQLAlchemy Model (reads from DB)
    ↓
Pydantic Schema (formats response)
    ↓
API Response (JSON)
```

---

## ✅ After Fixing

Once you've made all the fixes, test it:

```python
# Test in Python shell
from app.database import SessionLocal
from app.models import EmailPreference, SearchRequest

db = SessionLocal()

# Create a test preference
pref = EmailPreference(
    search_request_id=1,
    email_address="test@example.com",
    notify_on_match=True,
    notify_on_start=True,
    include_in_digest=True
)

db.add(pref)
db.commit()
print(f"Created: {pref}")

# Query it back
result = db.query(EmailPreference).first()
print(f"Retrieved: {result}")

db.close()
```

---

## 📚 Key Takeaways

1. **Models** use SQLAlchemy (`Base`, `Column`) - for database
2. **Schemas** use Pydantic (`BaseModel`, `Field`) - for API
3. Always register new models/schemas in `__init__.py`
4. Run `init_db` after creating new models
5. Add relationships in both directions

---

## Summary

Your Sub-Task 2 is **incomplete** and has critical errors. You need to:

1. ❌ Fix the model (use SQLAlchemy, not Pydantic)
2. ❌ Create the schema file
3. ❌ Register both model and schema
4. ❌ Add relationship to SearchRequest
5. ❌ Run database initialization

**Current Status:** 0% complete (model won't work at all)  
**After fixes:** 100% complete

Please fix these issues before moving to Sub-Task 3!