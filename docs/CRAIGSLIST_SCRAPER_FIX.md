# Craigslist Scraper Fix - HTML Structure Update

## Problem Summary

When testing the Craigslist scraper, it returned **"Found 0 products"** even though the page was loading successfully.

## Root Cause

**Craigslist changed their HTML structure in 2026.** The scraper was using outdated CSS selectors that no longer matched the new page structure.

### Old Structure (Before 2026)
```html
<li class="result-row">
  <a class="result-title" href="...">Product Title</a>
  <span class="result-price">$100</span>
  <span class="result-hood">(San Jose)</span>
</li>
```

### New Structure (2026)
```html
<li class="cl-static-search-result" title="Product Title">
  <a href="...">
    <div class="title">Product Title</div>
    <div class="details">
      <div class="price">$100</div>
      <div class="location">San Jose</div>
    </div>
  </a>
</li>
```

## Changes Made

### 1. Updated CSS Selector in `search()` method
**File:** `backend/app/scrapers/craigslist.py` (lines 95-99)

**Before:**
```python
result_rows = soup.find_all('li', class_='result-row')
```

**After:**
```python
# Try new structure first
result_rows = soup.find_all('li', class_='cl-static-search-result')

# Fallback to old structure if new one not found
if not result_rows:
    result_rows = soup.find_all('li', class_='result-row')
```

### 2. Updated `_parse_search_result()` method
**File:** `backend/app/scrapers/craigslist.py` (lines 151-220)

**Key Changes:**
- Find `<a>` element first (contains all info)
- Extract title from `<div class="title">`
- Extract price from `<div class="price">`
- Extract location from `<div class="location">`
- Added fallback logic for backward compatibility

## Diagnostic Tools Created

### 1. `inspect_craigslist.py`
A diagnostic tool that:
- Fetches a Craigslist search page
- Saves the full HTML to `craigslist_page.html`
- Analyzes the structure and identifies result containers
- Shows sample elements to help understand the structure

**Usage:**
```bash
cd backend
python app/scrapers/inspect_craigslist.py
```

### 2. `craigslist_test.py`
A comprehensive test suite that:
- Tests search functionality
- Tests product detail retrieval
- Tests availability checking
- Provides diagnostic output when issues occur

**Usage:**
```bash
cd backend
python app/scrapers/craigslist_test.py
```

## Test Results

After the fix, the scraper successfully:
- ✅ Found 5 iPhone listings
- ✅ Extracted titles, prices, and locations correctly
- ✅ Retrieved detailed product information
- ✅ Checked listing availability
- ✅ Handled 404 errors gracefully

### Sample Output
```
Found 5 products

1. Apple iPhone SE 3rd Gen - UNLOCKED - Like New
   Price: $165.0
   Location: San Jose
   
2. Moment Case for iPhone Xs Max - Wood
   Price: $5.0
   Location: napa county
   
3. Apple iPhone 16e 5G - UNLOCKED - Like New
   Price: $415.0
   Location: San Jose
```

## Lessons Learned

1. **Web scraping is fragile** - Websites change their HTML structure frequently
2. **Always inspect the actual HTML** - Don't assume the structure matches documentation
3. **Build diagnostic tools** - Create tools to inspect and debug scraper issues
4. **Add fallback logic** - Support both old and new structures when possible
5. **Test with real data** - Always test scrapers against live websites

## Future Maintenance

If the scraper stops working again:

1. Run the inspector tool:
   ```bash
   python app/scrapers/inspect_craigslist.py
   ```

2. Check `craigslist_page.html` for the current structure

3. Update CSS selectors in:
   - `search()` method (line ~95)
   - `_parse_search_result()` method (line ~151)

4. Test with:
   ```bash
   python app/scrapers/craigslist_test.py
   ```

## Related Files

- `backend/app/scrapers/craigslist.py` - Main scraper implementation
- `backend/app/scrapers/base.py` - Base scraper class
- `backend/app/scrapers/craigslist_test.py` - Test suite
- `backend/app/scrapers/inspect_craigslist.py` - Diagnostic tool
- `docs/DAY_5-6_CRAIGSLIST_SCRAPER_PLAN.md` - Implementation guide

## Status

✅ **FIXED** - Craigslist scraper is now fully functional with the new HTML structure (as of April 2026)