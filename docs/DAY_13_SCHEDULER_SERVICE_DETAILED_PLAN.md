# Day 13: Scheduler Service - Detailed Implementation Plan

**Total Time:** 6 hours  
**Difficulty:** Intermediate  
**Prerequisites:** Completed Day 11-12 (Search Orchestrator working)

---

## 📋 Overview

The **Scheduler Service** automatically runs your product searches at regular intervals (every 2 hours). Think of it as a "robot assistant" that wakes up periodically, checks which searches need to run, and executes them automatically without you having to click any buttons!

### What You'll Build
- A background scheduler that runs searches every 2 hours
- Integration with FastAPI so the scheduler starts when your app starts
- Proper error handling and logging
- Tests to ensure the scheduler works correctly

---

## 🎯 Learning Objectives

By the end of Day 13, you will understand:
1. **Background Tasks** - How to run code automatically in the background
2. **APScheduler** - A Python library for scheduling tasks
3. **FastAPI Lifecycle** - How to start/stop services with your app
4. **Cron Expressions** - How to schedule tasks at specific intervals

---

## 🏗️ Design Patterns Used

### 1. **Singleton Pattern**
**What it is:** Ensuring only one instance of the scheduler exists.

**Why we use it:** 
- Prevents multiple schedulers from running the same searches
- Saves system resources
- Makes the scheduler easy to control

**Example:**
```python
# ❌ Bad - Multiple schedulers
scheduler1 = Scheduler()
scheduler2 = Scheduler()  # Oops! Now we have two!

# ✅ Good - Single scheduler instance
scheduler = Scheduler.get_instance()  # Always returns the same one
```

### 2. **Observer Pattern (Event-Driven)**
**What it is:** The scheduler "observes" the clock and triggers actions at specific times.

**Why we use it:**
- Decouples the timing logic from the search logic
- Makes it easy to add/remove scheduled tasks
- Allows multiple tasks to run on different schedules

---

## 📅 Hour-by-Hour Breakdown

### **Hour 1-2: Setup & Basic Scheduler (2 hours)**

#### **Sub-task 1.1: Install APScheduler (15 min)**

**What to do:**
1. Install the APScheduler library
2. Verify installation

**Commands:**
```bash
cd backend
source venv/bin/activate  # or: venv\Scripts\activate on Windows
pip install apscheduler
pip freeze | grep apscheduler  # Verify it's installed
```

**Expected Output:**
```
APScheduler==3.10.4
```

**Deliverable:** APScheduler installed and verified

---

#### **Sub-task 1.2: Create Scheduler File (30 min)**

**What to do:**
Create the basic scheduler file structure.

**File:** `backend/app/core/scheduler.py`

**Code Template:**
```python
"""
Background Scheduler Service

This module provides automatic scheduling of product searches.
Searches run every 2 hours for all active search requests.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging
from typing import Optional

from app.database import SessionLocal
from app.models import SearchRequest, SearchStatus
from app.core.orchestrator import SearchOrchestrator

# Setup logging
logger = logging.getLogger(__name__)


class SearchScheduler:
    """
    Manages automatic execution of product searches.
    
    The scheduler runs as a background service and executes
    searches for all active search requests every 2 hours.
    
    Example:
        ```python
        scheduler = SearchScheduler()
        scheduler.start()  # Starts the scheduler
        # ... app runs ...
        scheduler.shutdown()  # Stops the scheduler
        ```
    """
    
    def __init__(self):
        """Initialize the scheduler."""
        # Create an async scheduler (works with FastAPI)
        self.scheduler = AsyncIOScheduler()
        self._is_running = False
        logger.info("SearchScheduler initialized")
    
    # Methods will be added in next sub-tasks
```

**Key Concepts Explained:**
- **AsyncIOScheduler**: A scheduler that works with async Python (FastAPI uses async)
- **logger**: Helps us see what the scheduler is doing
- **_is_running**: Tracks whether the scheduler is active

**Deliverable:** Basic scheduler file created

---

#### **Sub-task 1.3: Add Start Method (45 min)**

**What to do:**
Add the method to start the scheduler and configure the 2-hour interval.

**Code to Add:**
```python
def start(self):
    """
    Start the scheduler.
    
    This method:
    1. Configures the scheduler to run every 2 hours
    2. Starts the background scheduler
    3. Optionally runs an immediate search on startup
    """
    if self._is_running:
        logger.warning("Scheduler is already running")
        return
    
    try:
        # Add the job to run every 2 hours
        self.scheduler.add_job(
            func=self._run_all_searches,  # The function to call
            trigger=IntervalTrigger(hours=2),  # Run every 2 hours
            id='search_job',  # Unique identifier
            name='Run All Product Searches',  # Human-readable name
            replace_existing=True  # Replace if job already exists
        )
        
        # Start the scheduler
        self.scheduler.start()
        self._is_running = True
        
        logger.info("✅ Scheduler started successfully")
        logger.info("📅 Searches will run every 2 hours")
        
        # Optional: Run searches immediately on startup
        # Uncomment the next line if you want this behavior
        # asyncio.create_task(self._run_all_searches())
        
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {str(e)}")
        raise
```

**Understanding the Code:**
- **add_job()**: Tells the scheduler what to do and when
- **IntervalTrigger(hours=2)**: Creates a trigger that fires every 2 hours
- **id='search_job'**: Gives the job a unique name so we can reference it later
- **replace_existing=True**: If we restart the app, replace the old job

**Alternative Schedules:**
```python
# Every 30 minutes
IntervalTrigger(minutes=30)

# Every day at 9 AM
CronTrigger(hour=9, minute=0)

# Every Monday at 10 AM
CronTrigger(day_of_week='mon', hour=10, minute=0)
```

**Deliverable:** Start method implemented

---

#### **Sub-task 1.4: Add Shutdown Method (30 min)**

**What to do:**
Add the method to gracefully stop the scheduler.

**Code to Add:**
```python
def shutdown(self):
    """
    Shutdown the scheduler gracefully.
    
    This method:
    1. Stops accepting new jobs
    2. Waits for running jobs to complete
    3. Shuts down the scheduler
    """
    if not self._is_running:
        logger.warning("Scheduler is not running")
        return
    
    try:
        logger.info("🛑 Shutting down scheduler...")
        
        # Shutdown the scheduler
        # wait=True means wait for running jobs to finish
        self.scheduler.shutdown(wait=True)
        
        self._is_running = False
        logger.info("✅ Scheduler shut down successfully")
        
    except Exception as e:
        logger.error(f"❌ Error shutting down scheduler: {str(e)}")
        raise
```

**Why Graceful Shutdown Matters:**
- Prevents data corruption (searches complete before stopping)
- Ensures database connections are closed properly
- Avoids leaving "zombie" processes running

**Deliverable:** Shutdown method implemented

---

### **Hour 3-4: Core Search Logic (2 hours)**

#### **Sub-task 2.1: Implement _run_all_searches Method (1 hour)**

**What to do:**
Create the method that actually runs the searches.

**Code to Add:**
```python
async def _run_all_searches(self):
    """
    Run searches for all active search requests.
    
    This method:
    1. Gets all active search requests from database
    2. Runs each search using the orchestrator
    3. Logs results and errors
    
    This is the method that gets called every 2 hours.
    """
    logger.info("=" * 70)
    logger.info("🔍 Starting scheduled search execution")
    logger.info(f"⏰ Time: {datetime.utcnow().isoformat()}")
    logger.info("=" * 70)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Step 1: Get all active search requests
        active_searches = db.query(SearchRequest).filter(
            SearchRequest.status == SearchStatus.ACTIVE.value
        ).all()
        
        logger.info(f"📊 Found {len(active_searches)} active search requests")
        
        if not active_searches:
            logger.info("ℹ️  No active searches to run")
            return
        
        # Step 2: Run each search
        for search_request in active_searches:
            try:
                logger.info(f"\n🔎 Running search: {search_request.product_name}")
                logger.info(f"   ID: {search_request.id}")
                logger.info(f"   Location: {search_request.location}")
                
                # Create orchestrator and run search
                orchestrator = SearchOrchestrator(db)
                execution = await orchestrator.execute_search(search_request)
                
                # Log results
                if execution.status == 'completed':
                    logger.info(f"✅ Search completed successfully")
                    logger.info(f"   Products found: {execution.products_found}")
                    logger.info(f"   Matches: {execution.matches_found}")
                else:
                    logger.warning(f"⚠️  Search failed: {execution.error_message}")
                
            except Exception as e:
                logger.error(
                    f"❌ Error running search {search_request.id}: {str(e)}"
                )
                # Continue with next search even if this one fails
                continue
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ Scheduled search execution completed")
        logger.info("=" * 70 + "\n")
        
    except Exception as e:
        logger.error(f"❌ Critical error in scheduled execution: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Always close the database session
        db.close()
```

**Key Concepts:**
- **async def**: This is an async function (works with FastAPI)
- **try/except/finally**: Ensures database is closed even if errors occur
- **continue**: If one search fails, keep going with the others

**Deliverable:** Search execution method implemented

---

#### **Sub-task 2.2: Add Helper Methods (1 hour)**

**What to do:**
Add utility methods for checking status and getting job info.

**Code to Add:**
```python
def is_running(self) -> bool:
    """
    Check if the scheduler is currently running.
    
    Returns:
        bool: True if scheduler is running, False otherwise
    """
    return self._is_running


def get_next_run_time(self) -> Optional[datetime]:
    """
    Get the next scheduled run time.
    
    Returns:
        datetime: Next run time, or None if scheduler not running
        
    Example:
        ```python
        next_run = scheduler.get_next_run_time()
        print(f"Next search at: {next_run}")
        ```
    """
    if not self._is_running:
        return None
    
    try:
        job = self.scheduler.get_job('search_job')
        if job:
            return job.next_run_time
        return None
    except Exception as e:
        logger.error(f"Error getting next run time: {str(e)}")
        return None


def get_job_info(self) -> dict:
    """
    Get information about the scheduled job.
    
    Returns:
        dict: Job information including next run time, interval, etc.
        
    Example:
        ```python
        info = scheduler.get_job_info()
        print(f"Job: {info['name']}")
        print(f"Next run: {info['next_run']}")
        ```
    """
    if not self._is_running:
        return {
            'status': 'stopped',
            'message': 'Scheduler is not running'
        }
    
    try:
        job = self.scheduler.get_job('search_job')
        if job:
            return {
                'status': 'running',
                'job_id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            }
        return {
            'status': 'running',
            'message': 'No job found'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
```

**Deliverable:** Helper methods added

---

### **Hour 5: FastAPI Integration (1.5 hours)**

#### **Sub-task 3.1: Create Scheduler Instance (30 min)**

**What to do:**
Create a global scheduler instance and integrate with FastAPI.

**File:** `backend/app/main.py`

**Code to Add (at the top of the file):**
```python
from app.core.scheduler import SearchScheduler

# Create global scheduler instance
scheduler = SearchScheduler()
```

**Code to Add (in startup event):**
```python
@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    """
    logger.info("\n" + "=" * 70)
    logger.info("🚀 Product Search Agent API Starting Up")
    logger.info("=" * 70)
    
    # Start the scheduler
    try:
        scheduler.start()
        logger.info("✅ Scheduler started successfully")
        
        # Log next run time
        next_run = scheduler.get_next_run_time()
        if next_run:
            logger.info(f"📅 Next search scheduled for: {next_run}")
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {str(e)}")
    
    logger.info("=" * 70 + "\n")
```

**Code to Add (in shutdown event):**
```python
@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown.
    """
    logger.info("\n" + "=" * 70)
    logger.info("🛑 Product Search Agent API Shutting Down")
    logger.info("=" * 70)
    
    # Shutdown the scheduler
    try:
        scheduler.shutdown()
        logger.info("✅ Scheduler shut down successfully")
    except Exception as e:
        logger.error(f"❌ Error shutting down scheduler: {str(e)}")
    
    logger.info("=" * 70 + "\n")
```

**Deliverable:** Scheduler integrated with FastAPI lifecycle

---

#### **Sub-task 3.2: Add Scheduler Status Endpoint (1 hour)**

**What to do:**
Create an API endpoint to check scheduler status.

**File:** `backend/app/api/routes/scheduler.py` (create new file)

**Code:**
```python
"""
Scheduler API Routes

Endpoints for checking and managing the scheduler.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.main import scheduler

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


@router.get("/status")
async def get_scheduler_status() -> Dict[str, Any]:
    """
    Get the current status of the scheduler.
    
    Returns:
        dict: Scheduler status including next run time
        
    Example Response:
        ```json
        {
            "status": "running",
            "is_running": true,
            "next_run": "2024-01-15T14:30:00",
            "job_info": {
                "job_id": "search_job",
                "name": "Run All Product Searches",
                "trigger": "interval[0:02:00:00]"
            }
        }
        ```
    """
    try:
        is_running = scheduler.is_running()
        next_run = scheduler.get_next_run_time()
        job_info = scheduler.get_job_info()
        
        return {
            "status": "running" if is_running else "stopped",
            "is_running": is_running,
            "next_run": next_run.isoformat() if next_run else None,
            "job_info": job_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting scheduler status: {str(e)}"
        )


@router.post("/trigger")
async def trigger_search_now() -> Dict[str, str]:
    """
    Manually trigger a search execution now.
    
    This runs all active searches immediately without waiting
    for the scheduled time.
    
    Returns:
        dict: Success message
        
    Example Response:
        ```json
        {
            "message": "Search execution triggered successfully"
        }
        ```
    """
    try:
        if not scheduler.is_running():
            raise HTTPException(
                status_code=400,
                detail="Scheduler is not running"
            )
        
        # Trigger the search job immediately
        await scheduler._run_all_searches()
        
        return {
            "message": "Search execution triggered successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error triggering search: {str(e)}"
        )
```

**Add to main.py:**
```python
from app.api.routes import scheduler as scheduler_routes

# Include scheduler routes
app.include_router(scheduler_routes.router)
```

**Deliverable:** Scheduler status endpoint created

---

### **Hour 6: Testing (1.5 hours)**

#### **Sub-task 4.1: Manual Testing (45 min)**

**What to do:**
Test the scheduler manually to ensure it works.

**Steps:**
1. Start the FastAPI server:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Check the logs - you should see:
```
✅ Scheduler started successfully
📅 Next search scheduled for: 2024-01-15T14:30:00
```

3. Test the status endpoint:
```bash
curl http://localhost:8000/api/scheduler/status
```

Expected response:
```json
{
  "status": "running",
  "is_running": true,
  "next_run": "2024-01-15T14:30:00",
  "job_info": {
    "status": "running",
    "job_id": "search_job",
    "name": "Run All Product Searches"
  }
}
```

4. Trigger a manual search:
```bash
curl -X POST http://localhost:8000/api/scheduler/trigger
```

5. Watch the logs for search execution

**Deliverable:** Manual testing complete

---

#### **Sub-task 4.2: Write Unit Tests (45 min)**

**What to do:**
Create automated tests for the scheduler.

**File:** `backend/app/tests/test_scheduler.py`

**Code:**
```python
"""
Tests for Scheduler Service
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from app.core.scheduler import SearchScheduler


@pytest.fixture
def scheduler():
    """Create a scheduler instance for testing."""
    return SearchScheduler()


def test_scheduler_initialization(scheduler):
    """Test that scheduler initializes correctly."""
    assert scheduler is not None
    assert scheduler.is_running() == False


def test_scheduler_start(scheduler):
    """Test starting the scheduler."""
    scheduler.start()
    assert scheduler.is_running() == True
    scheduler.shutdown()


def test_scheduler_shutdown(scheduler):
    """Test shutting down the scheduler."""
    scheduler.start()
    assert scheduler.is_running() == True
    
    scheduler.shutdown()
    assert scheduler.is_running() == False


def test_get_next_run_time(scheduler):
    """Test getting next run time."""
    # Before starting
    assert scheduler.get_next_run_time() is None
    
    # After starting
    scheduler.start()
    next_run = scheduler.get_next_run_time()
    assert next_run is not None
    
    scheduler.shutdown()


def test_get_job_info(scheduler):
    """Test getting job information."""
    # Before starting
    info = scheduler.get_job_info()
    assert info['status'] == 'stopped'
    
    # After starting
    scheduler.start()
    info = scheduler.get_job_info()
    assert info['status'] == 'running'
    assert info['job_id'] == 'search_job'
    
    scheduler.shutdown()


@pytest.mark.asyncio
async def test_run_all_searches(scheduler):
    """Test the search execution method."""
    with patch('app.core.scheduler.SessionLocal') as mock_session:
        with patch('app.core.scheduler.SearchOrchestrator') as mock_orchestrator:
            # Mock database session
            mock_db = Mock()
            mock_session.return_value = mock_db
            
            # Mock search requests
            mock_search = Mock()
            mock_search.id = 1
            mock_search.product_name = "Test Product"
            mock_search.location = "Test City"
            mock_db.query.return_value.filter.return_value.all.return_value = [mock_search]
            
            # Mock orchestrator
            mock_exec = Mock()
            mock_exec.status = 'completed'
            mock_exec.products_found = 5
            mock_exec.matches_found = 2
            mock_orchestrator.return_value.execute_search = AsyncMock(return_value=mock_exec)
            
            # Run the search
            await scheduler._run_all_searches()
            
            # Verify database was queried
            mock_db.query.assert_called_once()
            
            # Verify orchestrator was called
            mock_orchestrator.return_value.execute_search.assert_called_once()
```

**Run the tests:**
```bash
pytest app/tests/test_scheduler.py -v
```

**Deliverable:** Unit tests written and passing

---

## 🧪 Testing Checklist

Run these tests to verify everything works:

```bash
# 1. Start the server
uvicorn app.main:app --reload

# 2. Check scheduler status
curl http://localhost:8000/api/scheduler/status

# 3. Trigger manual search
curl -X POST http://localhost:8000/api/scheduler/trigger

# 4. Run unit tests
pytest app/tests/test_scheduler.py -v

# 5. Check logs for scheduled executions
# Wait 2 hours or change interval to 1 minute for testing
```

---

## 📝 Code Quality Checklist

Before considering Day 13 complete:

- [ ] Scheduler starts automatically with FastAPI
- [ ] Scheduler shuts down gracefully
- [ ] Searches run every 2 hours
- [ ] Logs show clear information about executions
- [ ] Status endpoint returns correct information
- [ ] Manual trigger works
- [ ] Unit tests pass
- [ ] Code has docstrings
- [ ] Error handling in place
- [ ] Database sessions properly closed

---

## 🐛 Common Issues & Solutions

### Issue 1: "Scheduler already running" error
**Solution:** The scheduler is already started. Check if you're calling `start()` multiple times.

### Issue 2: Searches not running
**Solution:** 
1. Check if scheduler is running: `curl http://localhost:8000/api/scheduler/status`
2. Check logs for errors
3. Verify active search requests exist in database

### Issue 3: "Event loop is closed" error
**Solution:** Use `AsyncIOScheduler` instead of `BackgroundScheduler`.

### Issue 4: Database locked errors
**Solution:** Ensure database sessions are properly closed in `finally` blocks.

---

## 📚 Key Concepts Summary

### APScheduler
- **Purpose:** Schedule Python functions to run automatically
- **Types:** BackgroundScheduler (sync), AsyncIOScheduler (async)
- **Triggers:** IntervalTrigger (every X hours), CronTrigger (specific times)

### FastAPI Lifecycle Events
- **startup:** Code that runs when app starts
- **shutdown:** Code that runs when app stops
- **Use case:** Perfect for starting/stopping background services

### Background Tasks
- **What:** Code that runs independently of HTTP requests
- **Why:** Allows long-running operations without blocking the API
- **How:** APScheduler manages the timing and execution

---

## 🎯 Success Criteria

Day 13 is complete when:

1. ✅ Scheduler starts automatically with FastAPI
2. ✅ Searches run every 2 hours automatically
3. ✅ Status endpoint shows scheduler information
4. ✅ Manual trigger works
5. ✅ Graceful shutdown on app stop
6. ✅ Proper error handling and logging
7. ✅ Unit tests pass
8. ✅ Code is documented

---

## 🚀 Next Steps

After completing Day 13:
- **Day 14-15:** Implement WebSocket notifications for real-time updates
- **Day 16-17:** Add email notification system
- **Day 18:** Create daily digest scheduler

---

## 💡 Tips for Junior Developers

1. **Start Simple:** Get basic scheduling working before adding features
2. **Use Logs:** They're your best friend for debugging background tasks
3. **Test Frequently:** Don't wait 2 hours - use 1-minute intervals for testing
4. **Read Errors:** APScheduler error messages are usually very helpful
5. **Ask Questions:** If stuck for >30 minutes, seek help
6. **Commit Often:** Small, frequent commits are better than large ones

---

## 📖 Additional Resources

- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Cron Expression Guide](https://crontab.guru/)
- [Python Async/Await Tutorial](https://realpython.com/async-io-python/)

---

**Good luck with your implementation! 🎉**

Remember: The scheduler is like a reliable robot assistant - once set up correctly, it works tirelessly in the background!