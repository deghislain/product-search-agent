# Day 21-22: Core Components - Detailed Implementation Plan

## 📋 Overview
**Duration:** 12 hours (2 days)  
**Difficulty:** Intermediate  
**Goal:** Build the main UI components for creating searches, displaying results, and showing notifications

---

## 🎯 What You'll Build

By the end of Day 21-22, you'll have:
1. **SearchRequestForm** - Form to create/edit product searches
2. **SearchRequestList** - Display list of active searches
3. **ProductCard** - Show individual product results
4. **MatchNotification** - Display real-time match alerts

---

## 📚 Design Patterns & Concepts

### 1. **Controlled Components Pattern**
- **What:** Form inputs whose values are controlled by React state
- **Why:** Provides single source of truth for form data
- **Where:** SearchRequestForm
- **Example:**
  ```typescript
  const [query, setQuery] = useState('');
  <input value={query} onChange={(e) => setQuery(e.target.value)} />
  ```

### 2. **Presentational vs Container Components**
- **What:** Separate data logic from UI rendering
- **Presentational:** Pure UI components (ProductCard)
- **Container:** Components with logic (SearchRequestList)
- **Why:** Easier to test and reuse

### 3. **Composition Pattern**
- **What:** Build complex UIs from smaller, reusable pieces
- **Why:** DRY (Don't Repeat Yourself) principle
- **Where:** ProductCard used inside SearchRequestList

### 4. **Custom Hooks Pattern**
- **What:** Extract reusable stateful logic
- **Why:** Share logic between components
- **Where:** Form validation, data fetching

### 5. **Optimistic UI Updates**
- **What:** Update UI immediately, then sync with server
- **Why:** Better user experience
- **Where:** Creating/deleting search requests

---

## 🔧 Sub-Tasks Breakdown

### Sub-Task 1: SearchRequestForm Component (3 hours)

**What you're building:** A form to create new product search requests

**File:** `frontend/src/components/SearchRequestForm.tsx`

**Concepts:**
- Form state management
- Input validation
- Error handling
- Controlled components

---

#### Step 1.1: Create Basic Form Structure (30 min)

**Create the component file:**

```typescript
import { useState, type FormEvent } from 'react';

interface SearchRequestFormProps {
  onSubmit: (data: SearchRequestData) => void;
  onCancel?: () => void;
  initialData?: SearchRequestData;
}

interface SearchRequestData {
  query: string;
  platforms: string[];
  max_price?: number;
  min_price?: number;
  location?: string;
}

export default function SearchRequestForm({ 
  onSubmit, 
  onCancel,
  initialData 
}: SearchRequestFormProps) {
  // State will go here
  
  return (
    <form className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
      <h2 className="text-2xl font-bold mb-6">Create Search Request</h2>
      {/* Form fields will go here */}
    </form>
  );
}
```

**Key Concepts:**
- `interface` defines the shape of props
- `onSubmit` is a callback function passed from parent
- `initialData` allows editing existing searches

---

#### Step 1.2: Add Form State (30 min)

**Add state for each form field:**

```typescript
export default function SearchRequestForm({ onSubmit, onCancel, initialData }: SearchRequestFormProps) {
  // Form state
  const [query, setQuery] = useState(initialData?.query || '');
  const [platforms, setPlatforms] = useState<string[]>(initialData?.platforms || []);
  const [minPrice, setMinPrice] = useState(initialData?.min_price?.toString() || '');
  const [maxPrice, setMaxPrice] = useState(initialData?.max_price?.toString() || '');
  const [location, setLocation] = useState(initialData?.location || '');
  
  // UI state
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Component JSX...
}
```

**Understanding State:**
- `useState('')` - Initialize with empty string
- `useState<string[]>([])` - Initialize with empty array (TypeScript generic)
- `initialData?.query || ''` - Use initial data if provided, otherwise empty
- `errors` - Object to store validation errors
- `isSubmitting` - Track form submission state

---

#### Step 1.3: Create Input Fields (45 min)

**Add query input field:**

```typescript
<div className="mb-4">
  <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="query">
    Search Query *
  </label>
  <input
    id="query"
    type="text"
    value={query}
    onChange={(e) => setQuery(e.target.value)}
    className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
      errors.query ? 'border-red-500' : ''
    }`}
    placeholder="e.g., iPhone 13 Pro"
  />
  {errors.query && (
    <p className="text-red-500 text-xs italic mt-1">{errors.query}</p>
  )}
</div>
```

**Add platform checkboxes:**

```typescript
<div className="mb-4">
  <label className="block text-gray-700 text-sm font-bold mb-2">
    Platforms *
  </label>
  <div className="flex flex-col space-y-2">
    {['craigslist', 'facebook', 'ebay'].map((platform) => (
      <label key={platform} className="inline-flex items-center">
        <input
          type="checkbox"
          checked={platforms.includes(platform)}
          onChange={(e) => {
            if (e.target.checked) {
              setPlatforms([...platforms, platform]);
            } else {
              setPlatforms(platforms.filter(p => p !== platform));
            }
          }}
          className="form-checkbox h-5 w-5 text-blue-600"
        />
        <span className="ml-2 text-gray-700 capitalize">{platform}</span>
      </label>
    ))}
  </div>
  {errors.platforms && (
    <p className="text-red-500 text-xs italic mt-1">{errors.platforms}</p>
  )}
</div>
```

**Add price range inputs:**

```typescript
<div className="mb-4 grid grid-cols-2 gap-4">
  <div>
    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="minPrice">
      Min Price ($)
    </label>
    <input
      id="minPrice"
      type="number"
      value={minPrice}
      onChange={(e) => setMinPrice(e.target.value)}
      className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
      placeholder="0"
      min="0"
    />
  </div>
  <div>
    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="maxPrice">
      Max Price ($)
    </label>
    <input
      id="maxPrice"
      type="number"
      value={maxPrice}
      onChange={(e) => setMaxPrice(e.target.value)}
      className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
      placeholder="1000"
      min="0"
    />
  </div>
</div>
```

**Add location input:**

```typescript
<div className="mb-6">
  <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="location">
    Location
  </label>
  <input
    id="location"
    type="text"
    value={location}
    onChange={(e) => setLocation(e.target.value)}
    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
    placeholder="e.g., San Francisco, CA"
  />
</div>
```

**Tailwind Classes Explained:**
- `mb-4` - Margin bottom (spacing)
- `grid grid-cols-2 gap-4` - Two-column grid with gap
- `focus:outline-none focus:shadow-outline` - Remove default outline, add custom shadow on focus
- `border-red-500` - Red border for errors

---

#### Step 1.4: Add Validation Logic (45 min)

**Create validation function:**

```typescript
const validateForm = (): boolean => {
  const newErrors: Record<string, string> = {};

  // Validate query
  if (!query.trim()) {
    newErrors.query = 'Search query is required';
  } else if (query.trim().length < 3) {
    newErrors.query = 'Query must be at least 3 characters';
  }

  // Validate platforms
  if (platforms.length === 0) {
    newErrors.platforms = 'Select at least one platform';
  }

  // Validate price range
  const min = parseFloat(minPrice);
  const max = parseFloat(maxPrice);
  
  if (minPrice && isNaN(min)) {
    newErrors.minPrice = 'Invalid price';
  }
  
  if (maxPrice && isNaN(max)) {
    newErrors.maxPrice = 'Invalid price';
  }
  
  if (minPrice && maxPrice && min > max) {
    newErrors.maxPrice = 'Max price must be greater than min price';
  }

  setErrors(newErrors);
  return Object.keys(newErrors).length === 0;
};
```

**Understanding Validation:**
- `!query.trim()` - Check if empty after removing whitespace
- `platforms.length === 0` - Check if array is empty
- `parseFloat()` - Convert string to number
- `isNaN()` - Check if "Not a Number"
- Return `true` if no errors

---

#### Step 1.5: Add Submit Handler (30 min)

**Create submit function:**

```typescript
const handleSubmit = async (e: FormEvent) => {
  e.preventDefault(); // Prevent page reload
  
  if (!validateForm()) {
    return; // Stop if validation fails
  }

  setIsSubmitting(true);

  try {
    const formData: SearchRequestData = {
      query: query.trim(),
      platforms,
      min_price: minPrice ? parseFloat(minPrice) : undefined,
      max_price: maxPrice ? parseFloat(maxPrice) : undefined,
      location: location.trim() || undefined,
    };

    await onSubmit(formData);
    
    // Reset form on success
    setQuery('');
    setPlatforms([]);
    setMinPrice('');
    setMaxPrice('');
    setLocation('');
    setErrors({});
  } catch (error) {
    console.error('Form submission error:', error);
    setErrors({ submit: 'Failed to create search request' });
  } finally {
    setIsSubmitting(false);
  }
};
```

**Key Concepts:**
- `e.preventDefault()` - Stop default form submission
- `async/await` - Handle asynchronous operations
- `try/catch/finally` - Error handling
- Reset form after successful submission

---

#### Step 1.6: Add Form Buttons (30 min)

**Add submit and cancel buttons:**

```typescript
<div className="flex items-center justify-between">
  <button
    type="submit"
    disabled={isSubmitting}
    className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline ${
      isSubmitting ? 'opacity-50 cursor-not-allowed' : ''
    }`}
  >
    {isSubmitting ? 'Creating...' : 'Create Search'}
  </button>
  
  {onCancel && (
    <button
      type="button"
      onClick={onCancel}
      className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
    >
      Cancel
    </button>
  )}
</div>

{errors.submit && (
  <p className="text-red-500 text-xs italic mt-4">{errors.submit}</p>
)}
```

**Understanding Buttons:**
- `type="submit"` - Triggers form submission
- `type="button"` - Regular button (doesn't submit)
- `disabled={isSubmitting}` - Disable during submission
- `{isSubmitting ? 'Creating...' : 'Create Search'}` - Dynamic text
- `onCancel &&` - Only show if onCancel prop provided

---

### Sub-Task 2: SearchRequestList Component (2.5 hours)

**What you're building:** Display list of active search requests with actions

**File:** `frontend/src/components/SearchRequestList.tsx`

---

#### Step 2.1: Create Component Structure (30 min)

```typescript
import { useState, useEffect } from 'react';
import { getSearchRequests, deleteSearchRequest } from '../services/searchRequestService';
import type { SearchRequest } from '../services/searchRequestService';

export default function SearchRequestList() {
  const [searches, setSearches] = useState<SearchRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch searches on component mount
  useEffect(() => {
    fetchSearches();
  }, []);

  const fetchSearches = async () => {
    try {
      setLoading(true);
      const data = await getSearchRequests();
      setSearches(data);
      setError(null);
    } catch (err) {
      setError('Failed to load search requests');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Component JSX...
}
```

**Understanding useEffect:**
- `useEffect(() => {}, [])` - Runs once when component mounts
- Empty dependency array `[]` means "run once"
- Used for data fetching on component load

---

#### Step 2.2: Add Loading and Error States (20 min)

```typescript
if (loading) {
  return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>
  );
}

if (error) {
  return (
    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
      <p>{error}</p>
      <button 
        onClick={fetchSearches}
        className="mt-2 bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-3 rounded text-sm"
      >
        Retry
      </button>
    </div>
  );
}

if (searches.length === 0) {
  return (
    <div className="text-center py-12">
      <p className="text-gray-500 text-lg">No search requests yet</p>
      <p className="text-gray-400 mt-2">Create your first search to get started!</p>
    </div>
  );
}
```

**UI States:**
- **Loading:** Show spinner while fetching
- **Error:** Show error message with retry button
- **Empty:** Show helpful message when no data

---

#### Step 2.3: Create Search Item Card (45 min)

```typescript
const handleDelete = async (id: number) => {
  if (!confirm('Are you sure you want to delete this search?')) {
    return;
  }

  try {
    await deleteSearchRequest(id);
    setSearches(searches.filter(s => s.id !== id));
  } catch (err) {
    alert('Failed to delete search request');
    console.error(err);
  }
};

return (
  <div className="space-y-4">
    {searches.map((search) => (
      <div 
        key={search.id} 
        className="bg-white shadow-md rounded-lg p-6 hover:shadow-lg transition-shadow"
      >
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-gray-800 mb-2">
              {search.query}
            </h3>
            
            <div className="flex flex-wrap gap-2 mb-3">
              {search.platforms.map((platform) => (
                <span 
                  key={platform}
                  className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                >
                  {platform}
                </span>
              ))}
            </div>

            <div className="text-sm text-gray-600 space-y-1">
              {search.min_price && search.max_price && (
                <p>Price Range: ${search.min_price} - ${search.max_price}</p>
              )}
              {search.location && (
                <p>Location: {search.location}</p>
              )}
              <p className="text-xs text-gray-400">
                Created: {new Date(search.created_at!).toLocaleDateString()}
              </p>
            </div>
          </div>

          <div className="flex flex-col space-y-2 ml-4">
            <span className={`px-3 py-1 rounded text-sm font-medium ${
              search.is_active 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              {search.is_active ? 'Active' : 'Paused'}
            </span>
            
            <button
              onClick={() => handleDelete(search.id!)}
              className="px-3 py-1 bg-red-500 hover:bg-red-700 text-white text-sm rounded"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    ))}
  </div>
);
```

**Key Features:**
- `map()` - Loop through array and render each item
- `key={search.id}` - Unique identifier for React
- Conditional rendering with `&&` and ternary `? :`
- `filter()` - Remove deleted item from state
- `confirm()` - Browser confirmation dialog

---

### Sub-Task 3: ProductCard Component (2 hours)

**What you're building:** Display individual product with image, price, and details

**File:** `frontend/src/components/ProductCard.tsx`

---

#### Step 3.1: Create Component Structure (30 min)

```typescript
import type { Product } from '../services/searchRequestService';

interface ProductCardProps {
  product: Product;
  onViewDetails?: (product: Product) => void;
}

export default function ProductCard({ product, onViewDetails }: ProductCardProps) {
  const handleClick = () => {
    if (onViewDetails) {
      onViewDetails(product);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300">
      {/* Card content */}
    </div>
  );
}
```

---

#### Step 3.2: Add Product Image (30 min)

```typescript
{/* Product Image */}
<div className="relative h-48 bg-gray-200">
  {product.image_url ? (
    <img
      src={product.image_url}
      alt={product.title}
      className="w-full h-full object-cover"
      onError={(e) => {
        // Fallback if image fails to load
        e.currentTarget.src = 'https://via.placeholder.com/400x300?text=No+Image';
      }}
    />
  ) : (
    <div className="w-full h-full flex items-center justify-center text-gray-400">
      <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    </div>
  )}
  
  {/* Match Score Badge */}
  {product.match_score && (
    <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-bold">
      {Math.round(product.match_score * 100)}% Match
    </div>
  )}
  
  {/* Platform Badge */}
  <div className="absolute bottom-2 left-2 bg-blue-500 text-white px-2 py-1 rounded text-xs font-semibold capitalize">
    {product.platform}
  </div>
</div>
```

**Image Handling:**
- `onError` - Fallback if image fails to load
- `object-cover` - Crop image to fit container
- `absolute` positioning for badges
- SVG icon for missing images

---

#### Step 3.3: Add Product Details (45 min)

```typescript
{/* Product Details */}
<div className="p-4">
  {/* Title */}
  <h3 className="text-lg font-semibold text-gray-800 mb-2 line-clamp-2">
    {product.title}
  </h3>

  {/* Price */}
  <div className="flex items-center justify-between mb-3">
    <span className="text-2xl font-bold text-green-600">
      ${product.price.toLocaleString()}
    </span>
    {product.location && (
      <span className="text-sm text-gray-500">
        📍 {product.location}
      </span>
    )}
  </div>

  {/* Description */}
  {product.description && (
    <p className="text-sm text-gray-600 mb-4 line-clamp-3">
      {product.description}
    </p>
  )}

  {/* Action Buttons */}
  <div className="flex space-x-2">
    <a
      href={product.url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex-1 bg-blue-500 hover:bg-blue-700 text-white text-center py-2 px-4 rounded font-medium transition-colors"
    >
      View Listing
    </a>
    {onViewDetails && (
      <button
        onClick={handleClick}
        className="bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 px-4 rounded font-medium transition-colors"
      >
        Details
      </button>
    )}
  </div>

  {/* Timestamp */}
  <p className="text-xs text-gray-400 mt-3">
    Found: {new Date(product.created_at).toLocaleString()}
  </p>
</div>
```

**Tailwind Utilities:**
- `line-clamp-2` - Limit text to 2 lines with ellipsis
- `toLocaleString()` - Format number with commas
- `target="_blank"` - Open link in new tab
- `rel="noopener noreferrer"` - Security for external links

---

### Sub-Task 4: MatchNotification Component (2 hours)

**What you're building:** Toast-style notifications for new matches

**File:** `frontend/src/components/MatchNotification.tsx`

---

#### Step 4.1: Create Notification Component (45 min)

```typescript
import { useState, useEffect } from 'react';
import type { Product } from '../services/searchRequestService';

interface MatchNotificationProps {
  product: Product;
  onClose: () => void;
  autoClose?: boolean;
  duration?: number;
}

export default function MatchNotification({ 
  product, 
  onClose, 
  autoClose = true,
  duration = 5000 
}: MatchNotificationProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Slide in animation
    setIsVisible(true);

    // Auto close after duration
    if (autoClose) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [autoClose, duration]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(onClose, 300); // Wait for animation
  };

  return (
    <div className={`fixed top-4 right-4 z-50 transition-all duration-300 ${
      isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
    }`}>
      {/* Notification content */}
    </div>
  );
}
```

**Animation Concepts:**
- `translate-x-full` - Move off-screen to the right
- `translate-x-0` - Move to original position
- `transition-all duration-300` - Smooth animation
- `setTimeout` - Delay before removing from DOM

---

#### Step 4.2: Add Notification Content (45 min)

```typescript
<div className="bg-white rounded-lg shadow-2xl max-w-sm w-full overflow-hidden border-l-4 border-green-500">
  {/* Header */}
  <div className="bg-green-50 px-4 py-3 flex items-center justify-between">
    <div className="flex items-center">
      <span className="text-2xl mr-2">🎉</span>
      <h4 className="font-bold text-green-800">New Match Found!</h4>
    </div>
    <button
      onClick={handleClose}
      className="text-gray-400 hover:text-gray-600"
    >
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
      </svg>
    </button>
  </div>

  {/* Content */}
  <div className="p-4">
    <div className="flex">
      {/* Thumbnail */}
      {product.image_url && (
        <img
          src={product.image_url}
          alt={product.title}
          className="w-20 h-20 object-cover rounded mr-3"
        />
      )}

      {/* Details */}
      <div className="flex-1">
        <h5 className="font-semibold text-gray-800 line-clamp-2 mb-1">
          {product.title}
        </h5>
        <p className="text-lg font-bold text-green-600 mb-1">
          ${product.price.toLocaleString()}
        </p>
        <p className="text-xs text-gray-500 capitalize">
          {product.platform}
        </p>
      </div>
    </div>

    {/* Match Score */}
    {product.match_score && (
      <div className="mt-3 bg-green-100 rounded p-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-green-800 font-medium">Match Score</span>
          <span className="text-green-600 font-bold">
            {Math.round(product.match_score * 100)}%
          </span>
        </div>
      </div>
    )}

    {/* Action Button */}
    <a
      href={product.url}
      target="_blank"
      rel="noopener noreferrer"
      className="mt-3 block w-full bg-green-500 hover:bg-green-600 text-white text-center py-2 rounded font-medium transition-colors"
    >
      View Now
    </a>
  </div>
</div>
```

---

#### Step 4.3: Create Notification Manager (30 min)

**File:** `frontend/src/components/NotificationManager.tsx`

```typescript
import { useState } from 'react';
import MatchNotification from './MatchNotification';
import type { Product } from '../services/searchRequestService';

interface Notification {
  id: string;
  product: Product;
}

export default function NotificationManager() {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  // This will be called from WebSocket or polling
  const addNotification = (product: Product) => {
    const notification: Notification = {
      id: `${product.id}-${Date.now()}`,
      product,
    };
    setNotifications(prev => [...prev, notification]);
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  return (
    <div className="fixed top-0 right-0 z-50 p-4 space-y-4">
      {notifications.map((notification) => (
        <MatchNotification
          key={notification.id}
          product={notification.product}
          onClose={() => removeNotification(notification.id)}
        />
      ))}
    </div>
  );
}

// Export function to add notifications from outside
export { addNotification };
```

---

### Sub-Task 5: Form Validation Hook (1.5 hours)

**What you're building:** Reusable form validation logic

**File:** `frontend/src/hooks/useFormValidation.ts`

---

#### Step 5.1: Create Custom Hook (45 min)

```typescript
import { useState } from 'react';

interface ValidationRules<T> {
  [key: string]: (value: any, formData: T) => string | null;
}

export function useFormValidation<T extends Record<string, any>>(
  initialValues: T,
  validationRules: ValidationRules<T>
) {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const handleChange = (name: string, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleBlur = (name: string) => {
    setTouched(prev => ({ ...prev, [name]: true }));
    
    // Validate on blur
    if (validationRules[name]) {
      const error = validationRules[name](values[name], values);
      if (error) {
        setErrors(prev => ({ ...prev, [name]: error }));
      }
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    Object.keys(validationRules).forEach(key => {
      const error = validationRules[key](values[key], values);
      if (error) {
        newErrors[key] = error;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const reset = () => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  };

  return {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    validate,
    reset,
    setValues,
  };
}
```

**Hook Benefits:**
- Reusable across multiple forms
- Centralized validation logic
- Tracks touched fields
- Provides reset functionality

---

#### Step 5.2: Use Hook in Form (45 min)

**Update SearchRequestForm to use the hook:**

```typescript
import { useFormValidation } from '../hooks/useFormValidation';

export default function SearchRequestForm({ onSubmit }: SearchRequestFormProps) {
  const {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    validate,
    reset,
  } = useFormValidation(
    {
      query: '',
      platforms: [] as string[],
      minPrice: '',
      maxPrice: '',
      location: '',
    },
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
      maxPrice: (value, formData) => {
        const min = parseFloat(formData.minPrice);
        const max = parseFloat(value);
        if (value && formData.minPrice && min > max) {
          return 'Max price must be greater than min price';
        }
        return null;
      },
    }
  );

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!validate()) return;

    // Submit logic...
    await onSubmit(values);
    reset();
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={values.query}
        onChange={(e) => handleChange('query', e.target.value)}
        onBlur={() => handleBlur('query')}
      />
      {touched.query && errors.query && (
        <p className="text-red-500">{errors.query}</p>
      )}
      {/* Other fields... */}
    </form>
  );
}
```

---

### Sub-Task 6: Styling and Polish (2 hours)

#### Step 6.1: Add Responsive Design (45 min)

**Make components mobile-friendly:**

```typescript
// ProductCard - Responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {products.map(product => (
    <ProductCard key={product.id} product={product} />
  ))}
</div>

// SearchRequestForm - Stack on mobile
<div className="mb-4 grid grid-cols-1 md:grid-cols-2 gap-4">
  {/* Price inputs */}
</div>
```

**Responsive Breakpoints:**
- `md:` - Medium screens (768px+)
- `lg:` - Large screens (1024px+)
- `xl:` - Extra large (1280px+)

---

#### Step 6.2: Add Loading States (45 min)

**Create loading skeleton:**

```typescript
// ProductCardSkeleton.tsx
export function ProductCardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden animate-pulse">
      <div className="h-48 bg-gray-300"></div>
      <div className="p-4">
        <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
        <div className="h-4 bg-gray-300 rounded w-1/2 mb-4"></div>
        <div className="h-8 bg-gray-300 rounded"></div>
      </div>
    </div>
  );
}
```

---

#### Step 6.3: Add Transitions and Animations (30 min)

```typescript
// Fade in animation
<div className="animate-fade-in">
  {/* Content */}
</div>

// Add to tailwind.config.js
module.exports = {
  theme: {
    extend: {
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
};
```

---

## 🧪 Testing Your Components

### Test 1: SearchRequestForm
```typescript
// Test in Dashboard.tsx
import SearchRequestForm from '../components/SearchRequestForm';
import { createSearchRequest } from '../services/searchRequestService';

function Dashboard() {
  const handleSubmit = async (data) => {
    try {
      await createSearchRequest(data);
      alert('Search created!');
    } catch (error) {
      alert('Error creating search');
    }
  };

  return <SearchRequestForm onSubmit={handleSubmit} />;
}
```

### Test 2: SearchRequestList
```typescript
// Test in Dashboard.tsx
import SearchRequestList from '../components/SearchRequestList';

function Dashboard() {
  return (
    <div>
      <h1>My Searches</h1>
      <SearchRequestList />
    </div>
  );
}
```

### Test 3: ProductCard
```typescript
// Test in Matches.tsx
import ProductCard from '../components/ProductCard';

const mockProduct = {
  id: 1,
  title: 'iPhone 13 Pro',
  price: 899,
  url: 'https://example.com',
  platform: 'craigslist',
  image_url: 'https://via.placeholder.com/400',
  match_score: 0.95,
  created_at: new Date().toISOString(),
};

function Matches() {
  return <ProductCard product={mockProduct} />;
}
```

---

## 📁 Final File Structure

```
frontend/src/
├── components/
│   ├── SearchRequestForm.tsx      ✅ Form component
│   ├── SearchRequestList.tsx      ✅ List component
│   ├── ProductCard.tsx            ✅ Card component
│   ├── ProductCardSkeleton.tsx    ✅ Loading state
│   ├── MatchNotification.tsx      ✅ Notification
│   └── NotificationManager.tsx    ✅ Manager
├── hooks/
│   └── useFormValidation.ts       ✅ Custom hook
├── services/
│   ├── api.ts
│   ├── searchRequestService.ts
│   └── productService.ts
└── pages/
    ├── Dashboard.tsx
    ├── Matches.tsx
    └── Settings.tsx
```

---

## 🎓 Key Learnings

After Day 21-22, you'll understand:

1. **Form Management:**
   - Controlled components
   - Validation logic
   - Error handling
   - Submit handling

2. **Data Fetching:**
   - useEffect for API calls
   - Loading states
   - Error handling
   - Data transformation

3. **Component Composition:**
   - Props and callbacks
   - Reusable components
   - Conditional rendering
   - List rendering

4. **Custom Hooks:**
   - Extracting logic
   - Reusability
   - State management
   - Side effects

5. **Styling:**
   - Tailwind utilities
   - Responsive design
   - Animations
   - Accessibility

---

## 🚨 Common Mistakes to Avoid

1. **Not validating forms:**
   ```typescript
   // ❌ Wrong
   const handleSubmit = () => {
     onSubmit(values);
   };
   
   // ✅ Correct
   const handleSubmit = () => {
     if (!validate()) return;
     onSubmit(values);
   };
   ```

2. **Forgetting keys in lists:**
   ```typescript
   // ❌ Wrong
   {items.map(item => <div>{item.name}</div>)}
   
   // ✅ Correct
   {items.map(item => <div key={item.id}>{item.name}</div>)}
   ```

3. **Not handling loading states:**
   ```typescript
   // ❌ Wrong
   const [data, setData] = useState([]);
   
   // ✅ Correct
   const [data, setData] = useState([]);
   const [loading, setLoading] = useState(true);
   const [error, setError] = useState(null);
   ```

4. **Mutating state directly:**
   ```typescript
   // ❌ Wrong
   platforms.push(newPlatform);
   
   // ✅ Correct
   setPlatforms([...platforms, newPlatform]);
   ```

---

## ✅ Completion Checklist

- [ ] SearchRequestForm component created
- [ ] Form validation working
- [ ] SearchRequestList displays data
- [ ] ProductCard shows product details
- [ ] MatchNotification appears correctly
- [ ] Custom validation hook implemented
- [ ] All components styled with Tailwind
- [ ] Responsive design implemented
- [ ] Loading states added
- [ ] Error handling in place
- [ ] Components tested manually

---

## 🎯 Next Steps (Day 23)

After completing Day 21-22, you'll integrate these components into full pages:
- Dashboard with form and list
- Matches page with product grid
- Settings page with preferences

**Estimated Time:** 12 hours  
**Difficulty:** ⭐⭐⭐☆☆ (Intermediate)

Good luck building your components! 🚀