# Day 18: Daily Digest Scheduler - Detailed Implementation Plan

A comprehensive, beginner-friendly guide to implementing the daily digest email scheduler for the Product Search Agent.

---

## 📋 Overview

**Duration:** 4 hours  
**Difficulty:** Intermediate  
**Prerequisites:** 
- Days 1-17 completed
- Email service working (Day 16-17)
- Scheduler service running (Day 13)
- Understanding of async programming

---

## 🎯 What You'll Build

A scheduled job that:
1. Runs automatically every day at 9 AM
2. Collects all product matches from the last 24 hours
3. Groups matches by user email preferences
4. Sends a beautiful daily digest email to each user
5. Logs all activities for monitoring

---

## 🏗️ Architecture & Design Patterns

### Design Patterns Used

#### 1. **Cron Job Pattern** (Main Pattern)
**What it is:** A scheduled task that runs at specific times automatically.

**Why we use it:**
- Automates repetitive tasks
- Runs without user intervention
- Reliable and predictable execution
- Doesn't block other operations

**Example:**
```python
# Instead of manually sending digests:
def send_digest():
    # Send digest... (BAD - requires manual trigger)

# We schedule it:
scheduler.add_job(
    send_daily_digest,
    trigger='cron',
    hour=9,
    minute=0
)  # Runs automatically at 9 AM (GOOD)
```

#### 2. **Aggregation Pattern**
**What it is:** Collecting and combining data from multiple sources into a summary.

**Why we use it:**
- Reduces email noise (one email vs many)
- Provides overview of all activity
- Better user experience
- More efficient than individual emails

**Example:**
```python
# Instead of sending 10 separate emails:
for match in matches:
    send_email(match)  # BAD - email spam

# We aggregate and send one:
digest = aggregate_matches(matches)
send_digest_email(digest)  # GOOD - one comprehensive email
```

#### 3. **Query Builder Pattern**
**What it is:** Building database queries step by step to fetch specific data.

**Why we use it:**
- Flexible data retrieval
- Efficient database queries
- Easy to modify and extend
- Readable code

**Example:**
```python
# Build query step by step
query = db.query(Product)
query = query.filter(Product.created_at >= yesterday)
query = query.filter(Product.is_match == True)
matches = query.all()
```

---

## 📝 Sub-Tasks Breakdown

### **Sub-Task 1: Create Daily Digest Service Method** (1 hour)

#### What You'll Do:
Add a method to collect and aggregate matches for the daily digest.

#### Steps:

1. **Update `backend/app/services/email_service.py`:**
   - Add method to prepare digest data
   - Query database for recent matches
   - Group matches by email preferences

#### Code Structure:
```python
class EmailService:
    # ... existing methods ...
    
    async def prepare_daily_digest_data(
        self, 
        db: Session
    ) -> Dict[str, List[Dict]]:
        """
        Prepare data for daily digest emails.
        
        Returns:
            Dict mapping email addresses to their matches
        """
        from datetime import datetime, timedelta
        
        # 1. Calculate time range (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        
        # 2. Get all matches from last 24 hours
        recent_matches = db.query(Product).filter(
            Product.created_at >= yesterday,
            Product.is_match == True
        ).all()
        
        # 3. Get all email preferences with digest enabled
        email_prefs = db.query(EmailPreference).filter(
            EmailPreference.include_in_digest == True
        ).all()
        
        # 4. Group matches by email address
        digest_data = {}
        for pref in email_prefs:
            # Get matches for this search request
            matches = [
                m for m in recent_matches 
                if m.search_execution.search_request_id == pref.search_request_id
            ]
            
            if matches:
                if pref.email_address not in digest_data:
                    digest_data[pref.email_address] = []
                
                # Add matches with search request info
                for match in matches:
                    digest_data[pref.email_address].append({
                        'product': match,
                        'search_request': pref.search_request
                    })
        
        return digest_data
```

#### Key Concepts:

**Timedelta:**
- Represents a duration of time
- Used to calculate "24 hours ago"
- Example: `datetime.now() - timedelta(days=1)`

**Dictionary Grouping:**
- Organize data by key (email address)
- Allows sending one email per user
- Efficient data structure for aggregation

#### Deliverable:
- ✅ `prepare_daily_digest_data()` method implemented
- ✅ Queries database for recent matches
- ✅ Groups matches by email address

---

### **Sub-Task 2: Add Digest Scheduler Job** (1 hour)

#### What You'll Do:
Add a scheduled job to the scheduler that runs daily at 9 AM.

#### Steps:

1. **Update `backend/app/core/scheduler.py`:**
   - Import email service
   - Add daily digest job
   - Configure cron trigger

#### Code Example:
```python
from app.services.email_service import EmailService
from app.config import settings

class SearchScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.email_service = EmailService(settings)
    
    def start(self):
        """Start the scheduler with all jobs"""
        # Existing search job
        self.scheduler.add_job(
            self._run_all_searches,
            trigger='interval',
            hours=2,
            id='search_job'
        )
        
        # NEW: Daily digest job
        self.scheduler.add_job(
            self._send_daily_digest,
            trigger='cron',
            hour=9,  # 9 AM
            minute=0,
            id='daily_digest_job'
        )
        
        self.scheduler.start()
    
    async def _send_daily_digest(self):
        """Send daily digest emails to all users"""
        logger.info("Starting daily digest job...")
        
        try:
            # Get database session
            db = next(get_db())
            
            # Prepare digest data
            digest_data = await self.email_service.prepare_daily_digest_data(db)
            
            # Send digest to each email
            for email, matches in digest_data.items():
                try:
                    await self.email_service.send_daily_digest(
                        email=email,
                        matches=matches
                    )
                    logger.info(f"Sent daily digest to {email}")
                except Exception as e:
                    logger.error(f"Failed to send digest to {email}: {str(e)}")
            
            logger.info(f"Daily digest job completed. Sent {len(digest_data)} emails")
            
        except Exception as e:
            logger.error(f"Daily digest job failed: {str(e)}")
        finally:
            db.close()
```

#### Key Concepts:

**Cron Trigger:**
- Schedule based on time of day
- Uses cron-like syntax
- `hour=9, minute=0` = 9:00 AM daily
- More precise than interval triggers

**Error Handling:**
- Try-except for each email
- One failure doesn't stop others
- Comprehensive logging
- Always close database connection

#### Deliverable:
- ✅ Daily digest job added to scheduler
- ✅ Runs at 9 AM daily
- ✅ Sends emails to all users with matches

---

### **Sub-Task 3: Add Manual Trigger Endpoint** (30 minutes)

#### What You'll Do:
Create an API endpoint to manually trigger the daily digest (useful for testing).

#### Steps:

1. **Create `backend/app/api/routes/digest.py`:**

```python
"""
Daily Digest API Routes

Endpoints for managing and triggering daily digest emails.
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.email_service import EmailService
from app.config import settings

router = APIRouter(prefix="/api/digest", tags=["digest"])


@router.post(
    "/send-now",
    summary="Manually trigger daily digest",
    description="Send daily digest emails immediately (for testing)"
)
async def send_digest_now(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger the daily digest email send.
    
    Useful for:
    - Testing the digest functionality
    - Sending digest at non-scheduled times
    - Debugging email issues
    
    Returns:
        dict: Status message
    """
    email_service = EmailService(settings)
    
    # Run in background to not block the response
    background_tasks.add_task(
        send_digest_task,
        email_service,
        db
    )
    
    return {
        "status": "success",
        "message": "Daily digest is being sent in the background"
    }


async def send_digest_task(email_service: EmailService, db: Session):
    """Background task to send digest"""
    try:
        # Prepare digest data
        digest_data = await email_service.prepare_daily_digest_data(db)
        
        # Send to each email
        for email, matches in digest_data.items():
            await email_service.send_daily_digest(
                email=email,
                matches=matches
            )
        
        logger.info(f"Manual digest sent to {len(digest_data)} recipients")
        
    except Exception as e:
        logger.error(f"Manual digest failed: {str(e)}")


@router.get(
    "/preview",
    summary="Preview digest data",
    description="See what would be included in the next digest"
)
async def preview_digest(db: Session = Depends(get_db)):
    """
    Preview the data that would be included in the daily digest.
    
    Useful for:
    - Checking if there are matches to send
    - Debugging digest logic
    - Verifying email preferences
    
    Returns:
        dict: Preview of digest data
    """
    email_service = EmailService(settings)
    digest_data = await email_service.prepare_daily_digest_data(db)
    
    # Format for preview
    preview = {
        "total_recipients": len(digest_data),
        "recipients": []
    }
    
    for email, matches in digest_data.items():
        preview["recipients"].append({
            "email": email,
            "match_count": len(matches),
            "matches": [
                {
                    "product_title": m['product'].title,
                    "product_price": m['product'].price,
                    "search_query": m['search_request'].query
                }
                for m in matches[:5]  # Show first 5 matches
            ]
        })
    
    return preview
```

2. **Register the router in `backend/app/main.py`:**

```python
from app.api.routes import digest

app.include_router(digest.router)
```

#### Key Concepts:

**Background Tasks:**
- Runs after response is sent
- Doesn't block the API
- Good for long-running operations
- FastAPI built-in feature

**Preview Endpoint:**
- Shows what will be sent
- Useful for debugging
- No actual emails sent
- Returns JSON data

#### Deliverable:
- ✅ Manual trigger endpoint created
- ✅ Preview endpoint for debugging
- ✅ Background task implementation

---

### **Sub-Task 4: Add Logging and Monitoring** (30 minutes)

#### What You'll Do:
Add comprehensive logging to track digest execution.

#### Steps:

1. **Enhance logging in scheduler:**

```python
async def _send_daily_digest(self):
    """Send daily digest emails with detailed logging"""
    start_time = datetime.now()
    logger.info("=" * 70)
    logger.info("📧 DAILY DIGEST JOB STARTED")
    logger.info("=" * 70)
    logger.info(f"Start time: {start_time.isoformat()}")
    
    try:
        db = next(get_db())
        
        # Prepare data
        logger.info("Preparing digest data...")
        digest_data = await self.email_service.prepare_daily_digest_data(db)
        logger.info(f"Found {len(digest_data)} recipients with matches")
        
        # Send emails
        success_count = 0
        failure_count = 0
        
        for email, matches in digest_data.items():
            try:
                logger.info(f"Sending digest to {email} ({len(matches)} matches)")
                await self.email_service.send_daily_digest(
                    email=email,
                    matches=matches
                )
                success_count += 1
                logger.info(f"✅ Successfully sent to {email}")
            except Exception as e:
                failure_count += 1
                logger.error(f"❌ Failed to send to {email}: {str(e)}")
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 70)
        logger.info("📊 DAILY DIGEST JOB SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total recipients: {len(digest_data)}")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Failed: {failure_count}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"End time: {end_time.isoformat()}")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ DAILY DIGEST JOB FAILED: {str(e)}")
        logger.exception(e)  # Log full stack trace
    finally:
        db.close()
```

#### Key Concepts:

**Structured Logging:**
- Clear start/end markers
- Summary statistics
- Duration tracking
- Success/failure counts

**Exception Logging:**
- `logger.exception()` includes stack trace
- Helps with debugging
- Doesn't stop execution
- Records all errors

#### Deliverable:
- ✅ Comprehensive logging added
- ✅ Summary statistics tracked
- ✅ Error details recorded

---

### **Sub-Task 5: Write Tests** (1 hour)

#### What You'll Do:
Write tests to ensure the daily digest works correctly.

#### Steps:

1. **Create `backend/app/tests/test_daily_digest.py`:**

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from app.services.email_service import EmailService
from app.models.product import Product
from app.models.email_preference import EmailPreference


@pytest.fixture
def mock_db():
    """Create mock database session"""
    return Mock()


@pytest.fixture
def email_service(mock_config):
    """Create email service for testing"""
    return EmailService(mock_config)


@pytest.mark.asyncio
async def test_prepare_digest_data_with_matches(email_service, mock_db):
    """Test digest data preparation with matches"""
    # Mock recent matches
    mock_product = Mock(spec=Product)
    mock_product.created_at = datetime.now()
    mock_product.is_match = True
    mock_product.title = "Test Product"
    
    # Mock email preferences
    mock_pref = Mock(spec=EmailPreference)
    mock_pref.email_address = "user@example.com"
    mock_pref.include_in_digest = True
    mock_pref.search_request_id = 1
    
    # Setup mock queries
    mock_db.query.return_value.filter.return_value.all.return_value = [mock_product]
    
    # Call method
    digest_data = await email_service.prepare_daily_digest_data(mock_db)
    
    # Assertions
    assert len(digest_data) > 0
    assert "user@example.com" in digest_data


@pytest.mark.asyncio
async def test_prepare_digest_data_no_matches(email_service, mock_db):
    """Test digest data preparation with no matches"""
    # Mock empty results
    mock_db.query.return_value.filter.return_value.all.return_value = []
    
    # Call method
    digest_data = await email_service.prepare_daily_digest_data(mock_db)
    
    # Should return empty dict
    assert len(digest_data) == 0


@pytest.mark.asyncio
@patch('app.services.email_service.SMTP')
async def test_send_daily_digest_integration(
    mock_smtp_class,
    email_service,
    mock_product,
    mock_search_request
):
    """Test sending daily digest end-to-end"""
    # Mock SMTP
    mock_smtp_instance = AsyncMock()
    mock_smtp_class.return_value.__aenter__.return_value = mock_smtp_instance
    
    # Prepare matches
    matches = [
        {
            'product': mock_product,
            'search_request': mock_search_request
        }
    ]
    
    # Send digest
    await email_service.send_daily_digest(
        email="user@example.com",
        matches=matches
    )
    
    # Verify email was sent
    mock_smtp_instance.send_message.assert_called_once()
```

#### Deliverable:
- ✅ Test file created
- ✅ Tests for data preparation
- ✅ Tests for email sending
- ✅ All tests passing

---

## 🧪 Testing Your Implementation

### Manual Testing Steps:

1. **Test Digest Data Preparation:**
   ```bash
   # Use the preview endpoint
   curl http://localhost:8000/api/digest/preview
   ```

2. **Test Manual Trigger:**
   ```bash
   # Trigger digest manually
   curl -X POST http://localhost:8000/api/digest/send-now
   ```

3. **Test Scheduled Execution:**
   ```bash
   # Start the application
   uvicorn app.main:app --reload
   
   # Check logs at 9 AM for automatic execution
   # Or temporarily change the schedule to test sooner
   ```

4. **Verify Email Delivery:**
   - Check your email inbox
   - Verify digest contains all recent matches
   - Check formatting and links

### Automated Testing:
```bash
# Run digest tests
pytest app/tests/test_daily_digest.py -v

# Run with coverage
pytest app/tests/test_daily_digest.py --cov=app.services.email_service
```

---

## 🔧 Troubleshooting Guide

### Common Issues:

#### Issue 1: Digest not sending at scheduled time
**Cause:** Scheduler not running or wrong timezone  
**Solution:**
1. Check scheduler is started in `main.py`
2. Verify timezone settings
3. Check logs for scheduler errors
4. Use manual trigger to test

#### Issue 2: Empty digests being sent
**Cause:** No matches in last 24 hours  
**Solution:**
1. Check if matches exist in database
2. Verify `is_match` flag is set correctly
3. Check time range calculation
4. Use preview endpoint to debug

#### Issue 3: Some users not receiving digest
**Cause:** Email preferences not configured  
**Solution:**
1. Verify `include_in_digest` is True
2. Check email address is valid
3. Verify search request exists
4. Check logs for specific errors

#### Issue 4: Digest job taking too long
**Cause:** Too many matches or slow email sending  
**Solution:**
1. Add pagination for large result sets
2. Send emails in batches
3. Optimize database queries
4. Consider async batch sending

---

## 📚 Key Concepts Explained

### 1. Cron Scheduling
- **What:** Time-based job scheduling
- **Syntax:** `hour=9, minute=0` = 9:00 AM
- **Frequency:** Daily, weekly, monthly, etc.
- **Reliability:** Runs automatically without intervention

### 2. Data Aggregation
- **What:** Combining multiple records into summary
- **Why:** Reduces noise, provides overview
- **How:** Group by key (email), collect matches
- **Benefit:** One email instead of many

### 3. Background Tasks
- **What:** Operations that run after response
- **Why:** Don't block API responses
- **How:** FastAPI `BackgroundTasks`
- **Use:** Long-running operations

### 4. Time Ranges
- **What:** Filtering data by date/time
- **How:** `datetime.now() - timedelta(days=1)`
- **Use:** "Last 24 hours" queries
- **Benefit:** Only recent data

---

## ✅ Completion Checklist

- [ ] **Sub-Task 1:** Digest data preparation method
  - [ ] Method implemented
  - [ ] Queries recent matches
  - [ ] Groups by email

- [ ] **Sub-Task 2:** Scheduler job added
  - [ ] Job configured
  - [ ] Runs at 9 AM
  - [ ] Sends emails

- [ ] **Sub-Task 3:** Manual trigger endpoint
  - [ ] POST endpoint created
  - [ ] Preview endpoint created
  - [ ] Background tasks working

- [ ] **Sub-Task 4:** Logging added
  - [ ] Start/end logging
  - [ ] Summary statistics
  - [ ] Error tracking

- [ ] **Sub-Task 5:** Tests written
  - [ ] Test file created
  - [ ] All tests passing
  - [ ] Coverage adequate

---

## 🎯 Success Criteria

Your Day 18 implementation is complete when:

1. ✅ Daily digest job runs automatically at 9 AM
2. ✅ Collects all matches from last 24 hours
3. ✅ Groups matches by user email
4. ✅ Sends one digest email per user
5. ✅ Manual trigger endpoint works
6. ✅ Preview endpoint shows correct data
7. ✅ Comprehensive logging in place
8. ✅ All tests passing
9. ✅ No errors in logs

---

## 📖 Additional Resources

**Scheduling:**
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [Cron Expression Guide](https://crontab.guru/)

**Background Tasks:**
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

**Testing:**
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

## 💡 Tips for Success

1. **Test with manual trigger first** - Don't wait for 9 AM to test
2. **Use preview endpoint** - See data before sending emails
3. **Start with small time ranges** - Test with last hour instead of 24 hours
4. **Check logs frequently** - Monitor for errors and issues
5. **Test with real data** - Create some matches to test with
6. **Verify email delivery** - Check your inbox after testing
7. **Handle edge cases** - No matches, no preferences, etc.

---

## 🚀 Next Steps (Day 19)

After completing Day 18, you'll move to:
- **Day 19:** Frontend Setup
- Initialize React + Vite project
- Setup Tailwind CSS
- Create project structure

---

**Good luck with your daily digest scheduler implementation! 📧**