# Multi-Platform Search Fix 🔧

## Problem

When users check all three platform checkboxes (Craigslist, eBay, Facebook), only Craigslist searches are executed.

## Root Cause

The Pydantic schemas were missing `search_ebay` and `search_facebook` fields, so the API was ignoring these parameters even when sent by the frontend.

## Solution

### Backend Changes

**File 1: `backend/app/schemas/search_request.py`**

Added missing fields to `SearchRequestBase`:
```python
search_ebay: bool = Field(
    default=False,
    description="Enable the search on eBay"
)
search_facebook: bool = Field(
    default=False,
    description="Enable the search on Facebook Marketplace"
)
```

Added missing fields to `SearchRequestUpdate`:
```python
search_ebay: Optional[bool] = Field(
    None,
    description="Enable the search on eBay"
)
search_facebook: Optional[bool] = Field(
    None,
    description="Enable the search on Facebook Marketplace"
)
```

### Frontend Changes

**File 2: `frontend/src/services/searchRequestService.ts`**

**Fixed `createSearchRequest()`** to send all three platform flags:
```typescript
const backendData = {
  product_name: data.query,
  product_description: data.query,
  budget: data.max_price || 10000,
  location: data.location || null,
  match_threshold: 70.0,
  search_craigslist: data.platforms.includes('craigslist'),
  search_ebay: data.platforms.includes('ebay'),           // ADDED
  search_facebook: data.platforms.includes('facebook'),   // ADDED
};
```

**Fixed `getSearchRequests()`** to read all three platform flags:
```typescript
// Build platforms array based on backend flags
const platforms: string[] = [];
if (item.search_craigslist) platforms.push('craigslist');
if (item.search_ebay) platforms.push('ebay');           // ADDED
if (item.search_facebook) platforms.push('facebook');   // ADDED
```

**Fixed response transformation** in `createSearchRequest()`:
```typescript
// Build platforms array based on backend flags
const platforms: string[] = [];
if (item.search_craigslist) platforms.push('craigslist');
if (item.search_ebay) platforms.push('ebay');           // ADDED
if (item.search_facebook) platforms.push('facebook');   // ADDED

return {
  id: item.id,
  query: item.product_name,
  platforms: platforms,  // Now includes all checked platforms
  // ... other fields
};
```

## Testing

### Step 1: Restart Backend Server

**IMPORTANT:** The backend server must be restarted to pick up the schema changes.

```bash
# Stop the current server (Ctrl+C in the terminal)
# Then restart:
cd backend
uv run uvicorn app.main:app --reload
```

### Step 2: Test via API

```bash
curl -X POST http://localhost:8000/api/search-requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "iPhone 13",
    "product_description": "test all platforms",
    "budget": 500,
    "location": "USA",
    "match_threshold": 70.0,
    "search_craigslist": true,
    "search_ebay": true,
    "search_facebook": true
  }'
```

**Expected Response:**
```json
{
  "product_name": "iPhone 13",
  "search_craigslist": true,
  "search_ebay": true,        ← Should be true
  "search_facebook": true,    ← Should be true
  "id": "...",
  "status": "active"
}
```

### Step 3: Test via Frontend

1. Open http://localhost:5174
2. Click "Create Search"
3. Enter search details
4. **Check all three platform checkboxes:**
   - ☑ Craigslist
   - ☑ eBay
   - ☑ Facebook Marketplace
5. Click "Create Search"
6. Check backend logs - should see:
   ```
   INFO - Active platforms for search {id}: ['craigslist', 'ebay', 'facebook']
   INFO - Searching craigslist (attempt 1/3)
   INFO - Searching ebay (attempt 1/3)
   INFO - Searching facebook (attempt 1/3)
   ```

### Step 4: Verify in Database

```bash
cd backend
sqlite3 product_search.db "SELECT id, product_name, search_craigslist, search_ebay, search_facebook FROM search_requests ORDER BY created_at DESC LIMIT 1;"
```

**Expected:**
```
{id}|iPhone 13|1|1|1
```
(All three should be 1/true)

## Verification Checklist

- [ ] Backend server restarted
- [ ] API test shows all three flags as `true`
- [ ] Frontend checkboxes all work
- [ ] Backend logs show all three platforms being searched
- [ ] Database shows all three flags as `1`
- [ ] Products from all three platforms appear in results

## Files Modified

### Backend (1 file)
- `backend/app/schemas/search_request.py` - Added `search_ebay` and `search_facebook` fields

### Frontend (1 file)
- `frontend/src/services/searchRequestService.ts` - Send and receive all three platform flags

## Impact

**Before Fix:**
- Only Craigslist searches executed
- eBay and Facebook checkboxes had no effect
- Users couldn't search multiple platforms

**After Fix:**
- All checked platforms are searched
- Concurrent searches across platforms
- More comprehensive product results

## Related Issues

This fix also works with:
- Location normalization (see `docs/CRAIGSLIST_LOCATION_FIX.md`)
- Immediate search execution (see `docs/IMMEDIATE_SEARCH_IMPLEMENTATION_COMPLETE.md`)

## Notes

- The database model already had all three fields (lines 162-179 in `search_request.py`)
- The orchestrator already supports all three platforms
- Only the Pydantic schemas were missing the fields
- Frontend was already designed to handle multiple platforms

## Future Enhancements

1. **Platform-Specific Settings**
   - Different budgets per platform
   - Different locations per platform
   - Platform-specific filters

2. **Platform Priority**
   - Search preferred platforms first
   - Fallback to other platforms if no results

3. **Platform Analytics**
   - Track which platforms find the most matches
   - Show platform-specific statistics

---

**Status:** ✅ FIXED  
**Date:** April 18, 2026  
**Requires:** Backend server restart  
**Testing:** Required after restart