# Craigslist Location Fix 🗺️

## Problem

**Error:** `[Errno -5] No address associated with hostname` when searching Craigslist with location "USA"

**Root Cause:** 
- Users enter locations like "USA", "US", "Boston, US", "Halifax, Canada"
- Craigslist requires city-specific subdomains like `sfbay.craigslist.org`, `boston.craigslist.org`
- The code was using user input directly: `usa.craigslist.org` (invalid)

## Solution

Added `_normalize_location_for_platform()` method to `SearchOrchestrator` that:
1. Maps common location strings to valid Craigslist subdomains
2. Handles different formats: "USA", "Boston, US", "New York"
3. Defaults to "sfbay" (San Francisco Bay Area) for unknown locations

## Location Mappings

### Supported Locations

| User Input | Craigslist Subdomain |
|------------|---------------------|
| USA, US, United States | sfbay |
| San Francisco, SF, Bay Area | sfbay |
| New York, NYC, NY | newyork |
| Los Angeles, LA | losangeles |
| Chicago | chicago |
| Boston | boston |
| Seattle | seattle |
| Portland | portland |
| Denver | denver |
| Austin | austin |
| Miami | miami |
| Atlanta | atlanta |
| Philadelphia | philadelphia |
| Washington, DC | washingtondc |
| Dallas | dallas |
| Houston | houston |
| Phoenix | phoenix |
| San Diego | sandiego |
| Detroit | detroit |
| Minneapolis | minneapolis |
| Tampa | tampa |
| Baltimore | baltimore |
| St Louis | stlouis |
| Las Vegas | lasvegas |
| Sacramento | sacramento |

### Special Cases

- **"Boston, US"** → Extracts "boston" → `boston.craigslist.org`
- **"Halifax, Canada"** → No Halifax on Craigslist → Defaults to `sfbay.craigslist.org`
- **Unknown location** → Defaults to `sfbay.craigslist.org` with warning log

## Code Changes

**File:** `backend/app/core/orchestrator.py`

**Added Method:**
```python
def _normalize_location_for_platform(self, location: Optional[str], platform: str) -> str:
    """
    Normalize location string for specific platform requirements.
    
    Examples:
        >>> _normalize_location_for_platform("USA", "craigslist")
        'sfbay'
        >>> _normalize_location_for_platform("Boston, US", "craigslist")
        'boston'
    """
    # ... (see code for full implementation)
```

**Modified Method:**
```python
async def _search_platform(self, search_request: SearchRequest, platform: str) -> List[Dict]:
    # ... existing code ...
    
    # NEW: Normalize location for this platform
    normalized_location = self._normalize_location_for_platform(
        search_request.location, 
        platform
    )
    logger.info(f"Using location '{normalized_location}' for {platform}")
    
    # Execute search with normalized location
    products = await scraper.search(
        query=search_request.product_name,
        location=normalized_location,  # <-- Now uses normalized location
        max_price=search_request.budget,
    )
```

## Testing

### Test Case 1: USA Location
```bash
curl -X POST http://localhost:8000/api/search-requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "iPhone 13",
    "product_description": "test",
    "budget": 500,
    "location": "USA",
    "match_threshold": 70.0,
    "search_craigslist": true
  }'
```

**Expected:**
- Location "USA" → Normalized to "sfbay"
- URL: `https://sfbay.craigslist.org/search/sss?query=iPhone+13&max_price=500`
- ✅ No DNS error

### Test Case 2: City with State
```bash
curl -X POST http://localhost:8000/api/search-requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "MacBook Pro",
    "product_description": "test",
    "budget": 1000,
    "location": "Boston, US",
    "match_threshold": 70.0,
    "search_craigslist": true
  }'
```

**Expected:**
- Location "Boston, US" → Normalized to "boston"
- URL: `https://boston.craigslist.org/search/sss?query=MacBook+Pro&max_price=1000`
- ✅ No DNS error

### Test Case 3: Unknown Location
```bash
curl -X POST http://localhost:8000/api/search-requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "iPad",
    "product_description": "test",
    "budget": 300,
    "location": "Halifax, Canada",
    "match_threshold": 70.0,
    "search_craigslist": true
  }'
```

**Expected:**
- Location "Halifax, Canada" → Normalized to "sfbay" (default)
- Warning log: "Unknown Craigslist location 'Halifax, Canada', defaulting to 'sfbay'"
- URL: `https://sfbay.craigslist.org/search/sss?query=iPad&max_price=300`
- ✅ No DNS error

## Verification

### Check Logs
Look for these log messages in the backend output:
```
INFO - Using location 'sfbay' for craigslist
INFO - Searching craigslist (attempt 1/3)
INFO - Found X products on craigslist
```

### Check Database
```sql
SELECT id, status, products_found 
FROM search_executions 
ORDER BY started_at DESC 
LIMIT 1;
```

**Expected:**
- status: "completed" (not "failed")
- products_found: > 0 (if matches exist)

## Benefits

1. ✅ **User-Friendly**: Users can enter "USA" instead of "sfbay"
2. ✅ **Flexible**: Handles multiple formats ("Boston", "Boston, US", "boston")
3. ✅ **Robust**: Defaults to valid location if unknown
4. ✅ **Extensible**: Easy to add more city mappings
5. ✅ **Platform-Specific**: Can add different logic for eBay, Facebook

## Future Enhancements

### 1. Add More Cities
```python
location_map = {
    # ... existing mappings ...
    'san jose': 'sfbay',
    'oakland': 'sfbay',
    'pittsburgh': 'pittsburgh',
    'cleveland': 'cleveland',
    # etc.
}
```

### 2. Geo-Location API
Use a service to automatically map coordinates to nearest Craigslist city:
```python
def get_nearest_craigslist_city(lat: float, lon: float) -> str:
    # Use geolocation API
    # Return nearest city subdomain
    pass
```

### 3. User Location Preferences
Allow users to set preferred Craigslist location in settings:
```python
# In user preferences
preferred_craigslist_location = "boston"
```

### 4. Multi-City Search
Search multiple nearby cities:
```python
# For "Boston", also search:
# - boston.craigslist.org
# - worcester.craigslist.org
# - providence.craigslist.org
```

## Troubleshooting

### Issue: Still getting DNS error

**Check:**
1. Backend server restarted after code change?
2. Using correct API endpoint?
3. Location being passed correctly?

**Debug:**
```bash
# Check backend logs for:
grep "Using location" backend_logs.txt
grep "Searching craigslist" backend_logs.txt
```

### Issue: No products found

**Possible Causes:**
1. Search query too specific
2. Price too low
3. Location has no listings

**Solution:**
- Try broader search terms
- Increase budget
- Try different location (e.g., "New York" instead of "USA")

### Issue: Wrong location used

**Check:**
1. Location string spelling
2. Case sensitivity (should be case-insensitive)
3. Extra spaces (should be trimmed)

**Debug:**
```python
# Add logging to see what's being normalized
logger.info(f"Original location: '{search_request.location}'")
logger.info(f"Normalized location: '{normalized_location}'")
```

## Related Files

- `backend/app/core/orchestrator.py` - Location normalization logic
- `backend/app/scrapers/craigslist.py` - Craigslist scraper
- `backend/app/models/search_request.py` - SearchRequest model

## References

- Craigslist Site List: https://www.craigslist.org/about/sites
- Craigslist URL Format: `https://{city}.craigslist.org/search/{category}`

---

**Status:** ✅ FIXED  
**Date:** April 18, 2026  
**Impact:** Resolves DNS errors for all location inputs  
**Testing:** Required after deployment