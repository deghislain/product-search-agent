# Match Threshold Bug Fix

## Issue Description

**Bug:** Products with match scores above the user-specified threshold were being filtered out.

**Symptoms:**
- User sets `match_threshold` to 70 in the form
- Scrapers find 11 products
- Products score 80.0 (above threshold)
- But 0 products are returned after filtering

**Root Cause:**
The `ProductMatcher` class was using a hardcoded `min_score_threshold` of 85.0 instead of the `search_request.match_threshold` value provided by the user.

## Log Evidence

```
2026-04-18 20:02:41,981 - INFO - Matching 11 products against criteria
**********score lenght= 11
**********score = 80.0
***********Filtered lenght= 0  <-- BUG: Should be 11!
2026-04-18 20:02:41,981 - INFO - Found 0 products above match threshold
```

**Analysis:**
- 11 products found
- All scored 80.0
- User's threshold: 70.0
- Hardcoded threshold: 85.0 ❌
- Result: 80.0 < 85.0 → All products filtered out

## Code Analysis

### Problem Location

**File:** `backend/app/core/matching.py`

**Line 61 (Before Fix):**
```python
products = [p for p in products if p.match_score >= self.min_score_threshold]
```

**Issue:** Uses `self.min_score_threshold` (85.0) instead of `search_request.match_threshold` (70.0)

### Initialization Issue

**File:** `backend/app/core/orchestrator.py`

**Line 50:**
```python
self.matching_engine = ProductMatcher(min_score_threshold = 85.0)
```

**Issue:** Hardcoded threshold at initialization, but each search request can have a different threshold.

## Solution

### Fix Applied

**File:** `backend/app/core/matching.py`

**Changed Line 61:**
```python
# Before
products = [p for p in products if p.match_score >= self.min_score_threshold]

# After
threshold = search_request.match_threshold
products = [p for p in products if p.match_score >= threshold]
```

**Added Debug Logging:**
```python
print(f"**********threshold = {threshold}")
```

### Why This Works

1. **Per-Request Threshold:** Each search request now uses its own `match_threshold` value
2. **User Control:** Users can set threshold from 0-100 in the form
3. **Default Value:** Backend defaults to 70.0 if not specified
4. **Flexible Matching:** Different searches can have different sensitivity levels

## Testing

### Before Fix
```
User threshold: 70
Product score: 80
Hardcoded threshold: 85
Result: 80 < 85 → FILTERED OUT ❌
```

### After Fix
```
User threshold: 70
Product score: 80
Used threshold: 70
Result: 80 >= 70 → INCLUDED ✅
```

## Expected Behavior After Fix

With the fix applied, the logs should show:
```
2026-04-18 XX:XX:XX - INFO - Matching 11 products against criteria
**********score lenght= 11
**********score = 80.0
**********threshold = 70.0  <-- NEW: Shows user's threshold
***********Filtered lenght= 11  <-- FIXED: All products pass!
2026-04-18 XX:XX:XX - INFO - Found 11 products above match threshold
```

## Impact

### Before Fix
- ❌ User sets threshold to 70, but system uses 85
- ❌ Products scoring 70-84 are incorrectly filtered out
- ❌ Users get fewer matches than expected
- ❌ Match threshold field in form is effectively ignored

### After Fix
- ✅ System respects user's threshold setting
- ✅ Products scoring above user's threshold are included
- ✅ Users get expected number of matches
- ✅ Match threshold field works as intended

## Related Files

1. ✅ `backend/app/core/matching.py` - Fixed threshold usage
2. `backend/app/core/orchestrator.py` - Calls matching engine (no changes needed)
3. `frontend/src/components/SearchRequestForm.tsx` - User sets threshold (already working)
4. `backend/app/models/search_request.py` - Stores threshold (already working)

## Verification Steps

1. **Restart Backend:**
   ```bash
   cd backend
   uv run uvicorn app.main:app --reload
   ```

2. **Create Search with Threshold 70:**
   - Product Name: "Test Product"
   - Description: "Testing threshold"
   - Budget: 1000
   - Match Threshold: 70
   - Platforms: Craigslist

3. **Check Logs:**
   - Should see: `**********threshold = 70.0`
   - Should see: `***********Filtered lenght= X` (where X > 0 if products score >= 70)

4. **Verify Database:**
   ```bash
   sqlite3 product_search.db "SELECT COUNT(*) FROM products;"
   ```
   Should show products were saved.

## Type Checker Warnings

**Note:** The type checker shows warnings about SQLAlchemy Column types:
```
Invalid conditional operand of type "ColumnElement[bool] | bool"
```

**These are false positives:**
- At runtime, `match_score` is a `float`, not a SQLAlchemy Column
- The warnings occur because the Product model uses SQLAlchemy columns
- The code works correctly at runtime
- These warnings can be safely ignored or suppressed

## Summary

**Bug:** Hardcoded threshold (85.0) ignored user's setting  
**Fix:** Use `search_request.match_threshold` instead  
**Result:** Users now get matches based on their chosen threshold  
**Status:** ✅ Fixed and ready for testing

---

**Next Step:** Restart backend and test with a search request to verify products are now saved correctly.