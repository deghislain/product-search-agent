# Immediate Search Execution - Implementation Plan

## 📋 Overview

**Goal:** Execute search immediately when user clicks "Create Search", then repeat every 2 hours until deleted.

**Current Behavior:** Search requests are created but only execute when the scheduler runs (every 2 hours).

**New Behavior:** 
1. User clicks "Create Search" → Search executes immediately
2. Search continues to run every 2 hours automatically
3. Search stops when user deletes it from dashboard

---

## 🎯 High-Level Architecture

### Pattern: **Event-Driven + Background Task Pattern**

```
User Action (Create Search)
    ↓
API Endpoint (POST /api/search-requests)
    ↓
1. Save to Database
    ↓
2. Trigger Immediate Execution (Background Task)
    ↓
3. Return Response to User
    ↓
Scheduler continues running every 2 hours
```

---

## 📦 Components to Modify

### Backend Files:
1. `backend/app/api/routes/search_requests.py` - Add immediate execution
2. `backend/app/core/orchestrator.py` - Make execution async-friendly
3. `backend/app/core/scheduler.py` - Ensure no conflicts
4. `backend/app/main.py` - Add background task support

### Frontend Files:
5. `frontend/src/pages/Dashboard.tsx` - Show execution feedback
6. `frontend/src/components/SearchRequestForm.tsx` - Add loading state

---

## 🔧 Implementation Tasks

### Task 1: Add Background Task Support to FastAPI
**File:** `backend/app/main.py`  
**Difficulty:** ⭐ Easy  
**Time:** 15 minutes

**What to do:**
1. Import BackgroundTasks from FastAPI
2. No code changes needed - FastAPI already supports this!

**Why:** FastAPI's BackgroundTasks allows us to run tasks after returning a response to the user.

**Code Pattern:**
```python
from fastapi import BackgroundTasks

@app.post("/endpoint")
async def create_item(background_tasks: BackgroundTasks):
    # Save to database
    # Add background task
    background_tasks.add_task(function_to_run, arg1, arg2)
    # Return response immediately
    return {"status": "created"}
```

---

### Task 2: Create Immediate Execution Function
**File:** `backend/app/core/orchestrator.py`  
**Difficulty:** ⭐⭐ Medium  
**Time:** 30 minutes

**What to do:**
1. Add a new method `execute_search_immediately()`
2. This method runs a single search execution
3. Handles errors gracefully
4. Logs execution results

**Why:** We need a function that can be called as a background task.

**Code to Add:**
```python
async def execute_search_immediately(
    self,
    search_request_id: str,
    db: Session
) -> None:
    """
    Execute a search immediately (called as background task).
    
    Args:
        search_request_id: ID of the search request to execute
        db: Database session
    """
    try:
        logger.info(f"Starting immediate execution for search request {search_request_id}")
        
        # Get search request from database
        search_request = db.query(SearchRequest).filter(
            SearchRequest.id == search_request_id
        ).first()
        
        if not search_request:
            logger.error(f"Search request {search_request_id} not found")
            return
        
        # Execute the search
        await self.execute_search(search_request, db)
        
        logger.info(f"Immediate execution completed for search request {search_request_id}")
        
    except Exception as e:
        logger.error(f"Error in immediate execution: {str(e)}", exc_info=True)
    finally:
        db.close()
```

**Key Points:**
- Uses `async` because it may take time
- Handles errors so it doesn't crash the app
- Closes database session when done
- Logs everything for debugging

---

### Task 3: Update Create Search Endpoint
**File:** `backend/app/api/routes/search_requests.py`  
**Difficulty:** ⭐⭐ Medium  
**Time:** 45 minutes

**What to do:**
1. Add `BackgroundTasks` parameter to the create endpoint
2. After saving search request, trigger immediate execution
3. Return response immediately (don't wait for execution)

**Current Code:**
```python
@router.post("/", response_model=SearchRequestResponse)
def create_search_request(
    request: SearchRequestCreate,
    db: Session = Depends(get_db)
):
    # Create search request
    db_request = SearchRequest(**request.model_dump())
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    return db_request
```

**New Code:**
```python
from fastapi import BackgroundTasks
from app.core.orchestrator import SearchOrchestrator

@router.post("/", response_model=SearchRequestResponse)
async def create_search_request(
    request: SearchRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new search request and execute it immediately.
    
    The search will:
    1. Execute immediately (in background)
    2. Continue executing every 2 hours via scheduler
    3. Stop when deleted
    """
    # Create search request
    db_request = SearchRequest(**request.model_dump())
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    # Trigger immediate execution in background
    orchestrator = SearchOrchestrator()
    background_tasks.add_task(
        orchestrator.execute_search_immediately,
        search_request_id=db_request.id,
        db=db
    )
    
    logger.info(f"Search request {db_request.id} created and queued for immediate execution")
    
    return db_request
```

**Key Changes:**
1. Added `async` to function definition
2. Added `BackgroundTasks` parameter
3. Added `background_tasks.add_task()` call
4. Added logging

**Important Notes:**
- The API returns immediately (user doesn't wait)
- Search runs in background
- Scheduler continues to run it every 2 hours

---

### Task 4: Ensure Scheduler Doesn't Conflict
**File:** `backend/app/core/scheduler.py`  
**Difficulty:** ⭐ Easy  
**Time:** 15 minutes

**What to do:**
1. Verify scheduler checks if search is already running
2. Add lock mechanism if needed

**Current Behavior:**
- Scheduler runs every 2 hours
- Executes all active search requests

**What to Check:**
```python
def execute_all_searches(self):
    """Execute all active search requests"""
    # Get all active searches
    searches = db.query(SearchRequest).filter(
        SearchRequest.status == "active"
    ).all()
    
    for search in searches:
        # Check if already running (add this check)
        if self._is_search_running(search.id):
            logger.info(f"Search {search.id} already running, skipping")
            continue
            
        # Execute search
        self.orchestrator.execute_search(search, db)
```

**Add Helper Method:**
```python
def _is_search_running(self, search_id: str) -> bool:
    """
    Check if a search is currently executing.
    
    Args:
        search_id: ID of search request
        
    Returns:
        True if search is running, False otherwise
    """
    # Check SearchExecution table for running executions
    running = db.query(SearchExecution).filter(
        SearchExecution.search_request_id == search_id,
        SearchExecution.status == "running"
    ).first()
    
    return running is not None
```

**Why:** Prevents duplicate executions if immediate execution is still running when scheduler fires.

---

### Task 5: Add Execution Status Tracking
**File:** `backend/app/core/orchestrator.py`  
**Difficulty:** ⭐⭐ Medium  
**Time:** 30 minutes

**What to do:**
1. Update `execute_search()` to create SearchExecution record at start
2. Update status to "completed" or "failed" at end
3. This helps track if search is running

**Code Pattern:**
```python
async def execute_search(
    self,
    search_request: SearchRequest,
    db: Session
) -> SearchExecution:
    """Execute a search and track its status"""
    
    # Create execution record (status = "running")
    execution = SearchExecution(
        search_request_id=search_request.id,
        status="running",
        started_at=datetime.utcnow()
    )
    db.add(execution)
    db.commit()
    
    try:
        # Run the actual search
        results = await self._run_search(search_request)
        
        # Update status to completed
        execution.status = "completed"
        execution.completed_at = datetime.utcnow()
        execution.products_found = len(results)
        
    except Exception as e:
        # Update status to failed
        execution.status = "failed"
        execution.error_message = str(e)
        
    finally:
        db.commit()
        
    return execution
```

**Why:** This allows us to check if a search is currently running.

---

### Task 6: Add Frontend Loading State
**File:** `frontend/src/pages/Dashboard.tsx`  
**Difficulty:** ⭐ Easy  
**Time:** 20 minutes

**What to do:**
1. Show "Executing..." message after creating search
2. Update stats after execution completes

**Code to Add:**
```typescript
const [executingSearches, setExecutingSearches] = useState<Set<string>>(new Set());

const handleCreateSearch = async (data: SearchRequestData) => {
  try {
    const newSearch = await createSearchRequest({
      ...data,
      is_active: true,
    });
    
    // Add to executing set
    setExecutingSearches(prev => new Set(prev).add(newSearch.id));
    
    // Show message
    setMessage({
      type: 'info',
      text: 'Search created! Executing now...'
    });
    
    // Poll for completion (optional)
    pollSearchExecution(newSearch.id);
    
    setShowForm(false);
    setRefreshKey(prev => prev + 1);
  } catch (error) {
    console.error('Failed to create search:', error);
  }
};

const pollSearchExecution = async (searchId: string) => {
  // Poll every 5 seconds for up to 2 minutes
  const maxAttempts = 24; // 2 minutes / 5 seconds
  let attempts = 0;
  
  const interval = setInterval(async () => {
    attempts++;
    
    // Check if execution completed
    const isComplete = await checkExecutionStatus(searchId);
    
    if (isComplete || attempts >= maxAttempts) {
      clearInterval(interval);
      setExecutingSearches(prev => {
        const newSet = new Set(prev);
        newSet.delete(searchId);
        return newSet;
      });
      
      // Refresh stats
      fetchStats();
      
      setMessage({
        type: 'success',
        text: 'Search execution completed!'
      });
    }
  }, 5000);
};
```

**Why:** Gives user feedback that search is running.

---

### Task 7: Add Execution Status Badge
**File:** `frontend/src/components/SearchRequestList.tsx`  
**Difficulty:** ⭐ Easy  
**Time:** 15 minutes

**What to do:**
1. Show "Executing..." badge for running searches
2. Show "Active" badge for idle searches

**Code to Add:**
```typescript
<span className={`px-3 py-1 rounded text-sm font-medium ${
  isExecuting(search.id)
    ? 'bg-yellow-100 text-yellow-800 animate-pulse'
    : search.is_active 
      ? 'bg-green-100 text-green-800' 
      : 'bg-gray-100 text-gray-800'
}`}>
  {isExecuting(search.id) ? 'Executing...' : search.is_active ? 'Active' : 'Paused'}
</span>
```

**Why:** Visual feedback for user.

---

## 🔄 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ USER CLICKS "CREATE SEARCH"                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Frontend: POST /api/search-requests                         │
│ - Sends search data                                         │
│ - Shows loading state                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Backend API Endpoint                                        │
│ 1. Save search request to database                          │
│ 2. Add background task: execute_search_immediately()        │
│ 3. Return response immediately (don't wait)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├──────────────────────────────────────┐
                     │                                      │
                     ▼                                      ▼
┌─────────────────────────────────┐    ┌──────────────────────────────┐
│ Frontend Receives Response      │    │ Background Task Starts       │
│ - Shows "Executing..." message  │    │ - Runs orchestrator          │
│ - Polls for completion          │    │ - Scrapes platforms          │
│ - Updates UI when done          │    │ - Saves products             │
└─────────────────────────────────┘    │ - Sends notifications        │
                                       └──────────┬───────────────────┘
                                                  │
                                                  ▼
                                       ┌──────────────────────────────┐
                                       │ Execution Completes          │
                                       │ - Updates SearchExecution    │
                                       │ - Status = "completed"       │
                                       └──────────┬───────────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────┐
│ Scheduler (Runs Every 2 Hours)                              │
│ - Checks all active searches                                │
│ - Skips if already running                                  │
│ - Executes search again                                     │
│ - Repeats every 2 hours                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing Plan

### Test 1: Immediate Execution
1. Create a new search request
2. Check logs - should see "Starting immediate execution"
3. Wait 30 seconds
4. Check database - should have products
5. Check dashboard - should show matches

### Test 2: Recurring Execution
1. Wait 2 hours (or change scheduler interval for testing)
2. Check logs - should see scheduled execution
3. Verify new products are found
4. Verify no duplicate executions

### Test 3: Delete Search
1. Delete a search request
2. Wait 2 hours
3. Verify search doesn't execute anymore
4. Verify no errors in logs

### Test 4: Multiple Searches
1. Create 3 search requests quickly
2. All should execute immediately
3. All should continue running every 2 hours
4. No conflicts or race conditions

---

## 📝 Implementation Checklist

### Backend Changes:
- [ ] Task 1: Verify BackgroundTasks support (already done)
- [ ] Task 2: Add `execute_search_immediately()` to orchestrator
- [ ] Task 3: Update create search endpoint
- [ ] Task 4: Add conflict prevention to scheduler
- [ ] Task 5: Add execution status tracking

### Frontend Changes:
- [ ] Task 6: Add loading state to Dashboard
- [ ] Task 7: Add execution status badge

### Testing:
- [ ] Test immediate execution
- [ ] Test recurring execution
- [ ] Test delete stops execution
- [ ] Test multiple concurrent searches

### Documentation:
- [ ] Update API documentation
- [ ] Update user guide
- [ ] Add comments to code

---

## 🚨 Common Pitfalls & Solutions

### Pitfall 1: Database Session Issues
**Problem:** Background task uses closed database session  
**Solution:** Pass a new session or use session factory

```python
# Wrong
background_tasks.add_task(func, db=db)  # Session might close

# Right
from app.database import SessionLocal
background_tasks.add_task(func, db=SessionLocal())
```

### Pitfall 2: Duplicate Executions
**Problem:** Scheduler runs while immediate execution is still running  
**Solution:** Check SearchExecution status before running

### Pitfall 3: Long-Running Tasks Block API
**Problem:** If background task is synchronous, it blocks  
**Solution:** Use `async def` for background tasks

### Pitfall 4: No User Feedback
**Problem:** User doesn't know search is running  
**Solution:** Add loading states and status badges

---

## 📊 Success Criteria

Implementation is complete when:
1. ✅ Search executes immediately after creation
2. ✅ Search continues every 2 hours automatically
3. ✅ No duplicate executions occur
4. ✅ User sees execution status in UI
5. ✅ Deleting search stops future executions
6. ✅ All tests pass
7. ✅ No errors in logs

---

## 🎓 Key Concepts for Junior Developers

### Background Tasks
- Run after API returns response
- Don't block the user
- Good for long-running operations

### Async/Await
- `async def` = function can wait for things
- `await` = wait for this to finish
- Allows multiple things to run at once

### Database Sessions
- Each request gets its own session
- Must close session when done
- Background tasks need their own session

### Scheduler vs Background Tasks
- **Scheduler:** Runs on a schedule (every 2 hours)
- **Background Tasks:** Run once, triggered by event
- Both can coexist!

---

## 📞 Need Help?

If you get stuck:
1. Check the logs for error messages
2. Review the code patterns above
3. Test each task individually
4. Ask for help with specific error messages

**Good luck with the implementation! 🚀**