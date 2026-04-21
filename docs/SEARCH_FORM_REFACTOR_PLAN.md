# Search Form Refactor Plan

## Overview
Update the search request form to use more intuitive field names that match the backend schema:
- Replace "Search Query" → "Product Name"
- Add "Product Description" field
- Replace "Min Price" and "Max Price" → Single "Budget" field

## Current State Analysis

### Backend (Already Correct ✅)
The backend already uses the correct schema:
- [`SearchRequest`](backend/app/models/search_request.py:17) model has `product_name`, `product_description`, `budget`
- [`SearchRequestBase`](backend/app/schemas/search_request.py:21) schema matches the model
- No backend changes needed

### Frontend (Needs Updates ❌)
The frontend currently uses outdated field names:
- [`SearchRequestForm.tsx`](frontend/src/components/SearchRequestForm.tsx:1) uses `query`, `minPrice`, `maxPrice`
- [`searchRequestService.ts`](frontend/src/services/searchRequestService.ts:1) has transformation layer mapping old → new fields
- TypeScript interfaces use old field names

## Implementation Plan

### Phase 1: Update TypeScript Interfaces

**File:** [`frontend/src/services/searchRequestService.ts`](frontend/src/services/searchRequestService.ts:2)

**Current Interface:**
```typescript
export interface SearchRequest {
  id?: number;
  query: string;
  platforms: string[];
  max_price?: number;
  min_price?: number;
  location?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}
```

**New Interface:**
```typescript
export interface SearchRequest {
  id?: string;  // Backend uses UUID strings
  product_name: string;
  product_description: string;
  budget: number;
  platforms: string[];
  location?: string;
  match_threshold?: number;
  status: 'active' | 'paused' | 'completed' | 'cancelled';
  created_at?: string;
  updated_at?: string;
}
```

**Changes:**
1. Rename `query` → `product_name`
2. Add `product_description` field
3. Replace `min_price` and `max_price` → single `budget` field
4. Change `id` type from `number` to `string` (backend uses UUIDs)
5. Replace `is_active` → `status` enum
6. Add `match_threshold` field

---

### Phase 2: Update Form Component

**File:** [`frontend/src/components/SearchRequestForm.tsx`](frontend/src/components/SearchRequestForm.tsx:1)

#### 2.1 Update Interface (Lines 10-16)

**Current:**
```typescript
interface SearchRequestData {
  query: string;
  platforms: string[];
  max_price?: number;
  min_price?: number;
  location?: string;
}
```

**New:**
```typescript
interface SearchRequestData {
  product_name: string;
  product_description: string;
  budget: number;
  platforms: string[];
  location?: string;
  match_threshold?: number;
}
```

#### 2.2 Update Form State (Lines 31-38)

**Current:**
```typescript
{
  query: initialData?.query || '',
  platforms: initialData?.platforms || ([] as string[]),
  minPrice: initialData?.min_price?.toString() || '',
  maxPrice: initialData?.max_price?.toString() || '',
  location: initialData?.location || '',
}
```

**New:**
```typescript
{
  productName: initialData?.product_name || '',
  productDescription: initialData?.product_description || '',
  budget: initialData?.budget?.toString() || '',
  platforms: initialData?.platforms || ([] as string[]),
  location: initialData?.location || '',
  matchThreshold: initialData?.match_threshold?.toString() || '70',
}
```

#### 2.3 Update Validation Rules (Lines 39-63)

**Current:**
```typescript
{
  query: (value) => {
    if (!value.trim()) return 'Query is required';
    if (value.trim().length < 3) return 'Query must be at least 3 characters';
    return null;
  },
  platforms: (value) => {
    if (value.length === 0) return 'Select at least one platform';
    return null;
  },
  minPrice: (value) => {
    if (value && isNaN(parseFloat(value))) return 'Invalid price';
    return null;
  },
  maxPrice: (value, formData) => {
    if (value && isNaN(parseFloat(value))) return 'Invalid price';
    const min = parseFloat(formData.minPrice);
    const max = parseFloat(value);
    if (value && formData.minPrice && min > max) {
      return 'Max price must be greater than min price';
    }
    return null;
  },
}
```

**New:**
```typescript
{
  productName: (value) => {
    if (!value.trim()) return 'Product name is required';
    if (value.trim().length < 3) return 'Product name must be at least 3 characters';
    return null;
  },
  productDescription: (value) => {
    if (!value.trim()) return 'Product description is required';
    if (value.trim().length < 10) return 'Description must be at least 10 characters';
    return null;
  },
  budget: (value) => {
    if (!value) return 'Budget is required';
    if (isNaN(parseFloat(value))) return 'Invalid budget amount';
    if (parseFloat(value) <= 0) return 'Budget must be greater than 0';
    return null;
  },
  platforms: (value) => {
    if (value.length === 0) return 'Select at least one platform';
    return null;
  },
  matchThreshold: (value) => {
    if (value && isNaN(parseFloat(value))) return 'Invalid threshold';
    const threshold = parseFloat(value);
    if (value && (threshold < 0 || threshold > 100)) {
      return 'Threshold must be between 0 and 100';
    }
    return null;
  },
}
```

#### 2.4 Update Form Submission (Lines 65-84)

**Current:**
```typescript
const formData: SearchRequestData = {
  query: values.query.trim(),
  platforms: values.platforms,
  min_price: values.minPrice ? parseFloat(values.minPrice) : undefined,
  max_price: values.maxPrice ? parseFloat(values.maxPrice) : undefined,
  location: values.location.trim() || undefined,
};
```

**New:**
```typescript
const formData: SearchRequestData = {
  product_name: values.productName.trim(),
  product_description: values.productDescription.trim(),
  budget: parseFloat(values.budget),
  platforms: values.platforms,
  location: values.location.trim() || undefined,
  match_threshold: values.matchThreshold ? parseFloat(values.matchThreshold) : 70,
};
```

#### 2.5 Update Form Fields (Lines 90-198)

**Replace Query Input (Lines 90-109) with Product Name:**
```tsx
<div className="mb-4">
  <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="productName">
    Product Name *
  </label>
  <input
    id="productName"
    type="text"
    value={values.productName}
    onChange={(e) => handleChange('productName', e.target.value)}
    onBlur={() => handleBlur('productName')}
    className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
      touched.productName && errors.productName ? 'border-red-500' : ''
    }`}
    placeholder="e.g., iPhone 13 Pro"
  />
  {touched.productName && errors.productName && (
    <p className="text-red-500 text-xs italic mt-1">{errors.productName}</p>
  )}
</div>
```

**Add Product Description Field (New):**
```tsx
<div className="mb-4">
  <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="productDescription">
    Product Description *
  </label>
  <textarea
    id="productDescription"
    value={values.productDescription}
    onChange={(e) => handleChange('productDescription', e.target.value)}
    onBlur={() => handleBlur('productDescription')}
    rows={4}
    className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
      touched.productDescription && errors.productDescription ? 'border-red-500' : ''
    }`}
    placeholder="Describe the product you're looking for in detail..."
  />
  {touched.productDescription && errors.productDescription && (
    <p className="text-red-500 text-xs italic mt-1">{errors.productDescription}</p>
  )}
</div>
```

**Replace Price Range (Lines 140-182) with Single Budget Field:**
```tsx
<div className="mb-4">
  <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="budget">
    Budget ($) *
  </label>
  <input
    id="budget"
    type="number"
    value={values.budget}
    onChange={(e) => handleChange('budget', e.target.value)}
    onBlur={() => handleBlur('budget')}
    className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
      touched.budget && errors.budget ? 'border-red-500' : ''
    }`}
    placeholder="1000"
    min="0"
    step="0.01"
  />
  {touched.budget && errors.budget && (
    <p className="text-red-500 text-xs italic mt-1">{errors.budget}</p>
  )}
  <p className="text-gray-600 text-xs mt-1">Maximum amount you're willing to pay</p>
</div>
```

**Keep Platform Checkboxes (Lines 111-138) - No Changes**

**Keep Location Input (Lines 184-198) - No Changes**

**Add Match Threshold Field (Optional, Advanced):**
```tsx
<div className="mb-6">
  <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="matchThreshold">
    Match Threshold (%)
  </label>
  <input
    id="matchThreshold"
    type="number"
    value={values.matchThreshold}
    onChange={(e) => handleChange('matchThreshold', e.target.value)}
    onBlur={() => handleBlur('matchThreshold')}
    className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
      touched.matchThreshold && errors.matchThreshold ? 'border-red-500' : ''
    }`}
    placeholder="70"
    min="0"
    max="100"
  />
  {touched.matchThreshold && errors.matchThreshold && (
    <p className="text-red-500 text-xs italic mt-1">{errors.matchThreshold}</p>
  )}
  <p className="text-gray-600 text-xs mt-1">Minimum similarity score (0-100) for matches. Default: 70</p>
</div>
```

---

### Phase 3: Update Service Layer

**File:** [`frontend/src/services/searchRequestService.ts`](frontend/src/services/searchRequestService.ts:1)

#### 3.1 Remove Transformation Layer in `getSearchRequests()` (Lines 30-57)

**Current (with transformation):**
```typescript
export const getSearchRequests = async (): Promise<SearchRequest[]> => {
  const response = await apiClient.get('/api/search-requests');
  
  if (response.data.items) {
    return response.data.items.map((item: any) => {
      const platforms: string[] = [];
      if (item.search_craigslist) platforms.push('craigslist');
      if (item.search_ebay) platforms.push('ebay');
      if (item.search_facebook) platforms.push('facebook');
      
      return {
        id: item.id,
        query: item.product_name,  // Transform
        platforms: platforms,
        max_price: item.budget,    // Transform
        min_price: undefined,
        location: item.location,
        is_active: item.status === 'active',  // Transform
        created_at: item.created_at,
        updated_at: item.updated_at,
      };
    });
  }
  
  return [];
};
```

**New (direct mapping):**
```typescript
export const getSearchRequests = async (): Promise<SearchRequest[]> => {
  const response = await apiClient.get('/api/search-requests');
  
  if (response.data.items) {
    return response.data.items.map((item: any) => {
      const platforms: string[] = [];
      if (item.search_craigslist) platforms.push('craigslist');
      if (item.search_ebay) platforms.push('ebay');
      if (item.search_facebook) platforms.push('facebook');
      
      return {
        id: item.id,
        product_name: item.product_name,
        product_description: item.product_description,
        budget: item.budget,
        platforms: platforms,
        location: item.location,
        match_threshold: item.match_threshold,
        status: item.status,
        created_at: item.created_at,
        updated_at: item.updated_at,
      };
    });
  }
  
  return [];
};
```

#### 3.2 Simplify `createSearchRequest()` (Lines 66-107)

**Current (with transformation):**
```typescript
export const createSearchRequest = async (data: Omit<SearchRequest, 'id'>): Promise<SearchRequest> => {
  console.log('Frontend data received:', data);
  
  // Transform frontend data to match backend schema
  const backendData = {
    product_name: data.query,
    product_description: data.query,  // Using query as description
    budget: data.max_price || 10000,
    location: data.location || null,
    match_threshold: 70.0,
    search_craigslist: data.platforms.includes('craigslist'),
    search_ebay: data.platforms.includes('ebay'),
    search_facebook: data.platforms.includes('facebook'),
  };
  
  console.log('Sending to backend:', backendData);
  
  const response = await apiClient.post('/api/search-requests', backendData);
  
  // Transform response back...
};
```

**New (direct pass-through):**
```typescript
export const createSearchRequest = async (data: Omit<SearchRequest, 'id' | 'status' | 'created_at' | 'updated_at'>): Promise<SearchRequest> => {
  const backendData = {
    product_name: data.product_name,
    product_description: data.product_description,
    budget: data.budget,
    location: data.location || null,
    match_threshold: data.match_threshold || 70.0,
    search_craigslist: data.platforms.includes('craigslist'),
    search_ebay: data.platforms.includes('ebay'),
    search_facebook: data.platforms.includes('facebook'),
  };
  
  const response = await apiClient.post('/api/search-requests', backendData);
  
  // Build platforms array from response
  const platforms: string[] = [];
  if (response.data.search_craigslist) platforms.push('craigslist');
  if (response.data.search_ebay) platforms.push('ebay');
  if (response.data.search_facebook) platforms.push('facebook');
  
  return {
    ...response.data,
    platforms,
  };
};
```

---

### Phase 4: Update Components Using SearchRequest

**Files to Check:**
1. [`frontend/src/pages/Dashboard.tsx`](frontend/src/pages/Dashboard.tsx:1) - Update to use new field names
2. [`frontend/src/components/SearchRequestList.tsx`](frontend/src/components/SearchRequestList.tsx:1) - Update display logic
3. Any other components that reference `query`, `min_price`, `max_price`, or `is_active`

**Changes Needed:**
- Replace `request.query` → `request.product_name`
- Replace `request.max_price` → `request.budget`
- Replace `request.is_active` → `request.status === 'active'`
- Remove references to `request.min_price`

---

## Testing Checklist

### Unit Tests
- [ ] Form validation for `product_name` (required, min 3 chars)
- [ ] Form validation for `product_description` (required, min 10 chars)
- [ ] Form validation for `budget` (required, > 0)
- [ ] Form validation for `match_threshold` (0-100 range)
- [ ] Platform selection (at least one required)

### Integration Tests
- [ ] Create new search request with all fields
- [ ] Verify data sent to backend matches schema
- [ ] Verify response data is correctly mapped
- [ ] Display search requests in list view
- [ ] Edit existing search request
- [ ] Delete search request

### Manual Testing
1. **Create Search:**
   - Fill in product name: "iPhone 13 Pro"
   - Fill in description: "Looking for iPhone 13 Pro in good condition, 128GB or more, unlocked"
   - Set budget: 600
   - Select platforms: Craigslist, eBay
   - Set location: "Boston, MA"
   - Submit form
   - Verify search is created and appears in list

2. **View Search:**
   - Check that product name displays correctly
   - Check that budget displays correctly
   - Check that platforms display correctly

3. **Edit Search:**
   - Update budget to 650
   - Update description
   - Save changes
   - Verify updates are reflected

4. **Search Execution:**
   - Verify search executes with new fields
   - Check that matching uses product_name and product_description
   - Verify budget constraint is applied

---

## Migration Notes

### Breaking Changes
⚠️ **This is a breaking change for the frontend interface**

**Before:**
```typescript
{
  query: "iPhone 13",
  min_price: 500,
  max_price: 700,
  is_active: true
}
```

**After:**
```typescript
{
  product_name: "iPhone 13 Pro",
  product_description: "Looking for iPhone 13 Pro...",
  budget: 700,
  status: "active"
}
```

### Data Migration
No database migration needed - backend schema is already correct. Only frontend needs updates.

### Backward Compatibility
None - this is a complete refactor of the frontend interface to match backend schema.

---

## Benefits

1. **Consistency:** Frontend and backend use same field names
2. **Clarity:** "Product Name" and "Budget" are more intuitive than "Query" and "Max Price"
3. **Better UX:** Separate description field allows more detailed search criteria
4. **Simplified Code:** No transformation layer needed between frontend and backend
5. **Type Safety:** TypeScript interfaces match backend Pydantic schemas exactly

---

## Implementation Order

1. ✅ **Phase 1:** Update TypeScript interfaces in `searchRequestService.ts`
2. ✅ **Phase 2:** Update form component `SearchRequestForm.tsx`
3. ✅ **Phase 3:** Update service layer to remove transformations
4. ✅ **Phase 4:** Update other components using SearchRequest
5. ✅ **Phase 5:** Test all functionality
6. ✅ **Phase 6:** Document changes

---

## Estimated Time

- Phase 1: 15 minutes
- Phase 2: 30 minutes
- Phase 3: 20 minutes
- Phase 4: 20 minutes
- Testing: 30 minutes
- Documentation: 15 minutes

**Total: ~2 hours**

---

## Success Criteria

- [ ] Form uses product_name, product_description, budget fields
- [ ] All validation rules work correctly
- [ ] Search requests can be created successfully
- [ ] Search requests display correctly in list
- [ ] Search execution works with new fields
- [ ] No console errors
- [ ] TypeScript compiles without errors
- [ ] All tests pass