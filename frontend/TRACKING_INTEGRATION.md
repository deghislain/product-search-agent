# Frontend User Tracking Integration Guide

This guide explains how to integrate user interaction tracking into your Product Search Agent frontend.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Files Created](#files-created)
3. [Step-by-Step Integration](#step-by-step-integration)
4. [Usage Examples](#usage-examples)
5. [API Reference](#api-reference)
6. [Testing](#testing)

---

## 🚀 Quick Start

### 1. Initialize User Identification

Add this to your `src/App.tsx`:

```typescript
import { useEffect } from 'react';
import { initializeUserIdentification } from './utils/userIdentification';

function App() {
  useEffect(() => {
    // Initialize user ID on app load
    initializeUserIdentification();
  }, []);
  
  return (
    // Your app content
  );
}
```

### 2. Add Tracking to Product Cards

Update your `ProductCard` component:

```typescript
import { useProductViewTracking, useProductInteractions } from './hooks/useProductTracking';

function ProductCard({ product }) {
  // Track view duration automatically
  useProductViewTracking(product.id);
  
  // Get tracking functions
  const { trackClick } = useProductInteractions();
  
  const handleClick = async () => {
    await trackClick(product.id);
    window.open(product.url, '_blank');
  };
  
  return (
    <div className="product-card">
      <h3>{product.title}</h3>
      <p>${product.price}</p>
      <button onClick={handleClick}>View Product</button>
    </div>
  );
}
```

### 3. Done! 🎉

Your app is now tracking user interactions and learning preferences!

---

## 📁 Files Created

### Core Files

1. **`src/utils/userIdentification.ts`**
   - Manages user ID generation and storage
   - Uses localStorage with cookie fallback
   - Provides functions: `getUserId()`, `setUserId()`, `clearUserId()`

2. **`src/services/userInteractionService.ts`**
   - API service for tracking interactions
   - Functions for tracking views, clicks, purchases, ignores
   - Functions for getting user stats and preferences

3. **`src/hooks/useProductTracking.ts`**
   - React hooks for easy integration
   - `useProductViewTracking` - Auto-track view duration
   - `useProductInteractions` - Get tracking functions
   - `useProductLinkClick` - Track link clicks
   - `useProductVisibility` - Track when product enters viewport

4. **`src/examples/ProductCardWithTracking.tsx`**
   - Complete examples showing different integration patterns
   - Copy-paste ready code snippets

---

## 🔧 Step-by-Step Integration

### Step 1: Initialize User ID (Required)

In `src/App.tsx` or `src/main.tsx`:

```typescript
import { useEffect } from 'react';
import { initializeUserIdentification } from './utils/userIdentification';

function App() {
  useEffect(() => {
    initializeUserIdentification();
    console.log('User tracking initialized');
  }, []);
  
  // Rest of your app...
}
```

### Step 2: Track Product Views

**Option A: Automatic tracking with duration**

```typescript
import { useProductViewTracking } from './hooks/useProductTracking';

function ProductCard({ product }) {
  // Automatically tracks view when component mounts/unmounts
  useProductViewTracking(product.id);
  
  return <div>...</div>;
}
```

**Option B: Manual tracking**

```typescript
import { trackProductView } from './services/userInteractionService';

async function handleView(productId: number) {
  await trackProductView(productId, 30); // 30 seconds
}
```

### Step 3: Track Product Clicks

**Option A: Using hook**

```typescript
import { useProductLinkClick } from './hooks/useProductTracking';

function ProductCard({ product }) {
  const handleClick = useProductLinkClick(product.id, product.url);
  
  return (
    <a href={product.url} onClick={handleClick} target="_blank">
      View Product
    </a>
  );
}
```

**Option B: Using service directly**

```typescript
import { trackProductClick } from './services/userInteractionService';

async function handleClick(productId: number) {
  await trackProductClick(productId);
  window.open(productUrl, '_blank');
}
```

### Step 4: Track Purchases (Optional)

```typescript
import { useProductInteractions } from './hooks/useProductTracking';

function ProductCard({ product }) {
  const { trackPurchase } = useProductInteractions();
  
  const handleBuyNow = async () => {
    await trackPurchase(product.id, { 
      price: product.price,
      platform: product.platform 
    });
    window.open(product.url, '_blank');
  };
  
  return (
    <button onClick={handleBuyNow}>Buy Now</button>
  );
}
```

### Step 5: Track Ignores (Optional)

```typescript
import { useProductInteractions } from './hooks/useProductTracking';

function ProductCard({ product }) {
  const { trackIgnore } = useProductInteractions();
  
  const handleNotInterested = async () => {
    await trackIgnore(product.id);
    // Maybe hide the card or show feedback
  };
  
  return (
    <button onClick={handleNotInterested}>Not Interested</button>
  );
}
```

---

## 💡 Usage Examples

### Example 1: Minimal Integration

```typescript
import { useProductViewTracking } from './hooks/useProductTracking';

function ProductCard({ product }) {
  useProductViewTracking(product.id);
  return <div>{product.title}</div>;
}
```

### Example 2: Full Integration

```typescript
import { 
  useProductViewTracking, 
  useProductInteractions 
} from './hooks/useProductTracking';

function ProductCard({ product }) {
  useProductViewTracking(product.id);
  const { trackClick, trackPurchase, trackIgnore } = useProductInteractions();
  
  return (
    <div className="product-card">
      <h3>{product.title}</h3>
      <p>${product.price}</p>
      
      <button onClick={() => trackClick(product.id)}>
        View Details
      </button>
      <button onClick={() => trackPurchase(product.id)}>
        Buy Now
      </button>
      <button onClick={() => trackIgnore(product.id)}>
        Not Interested
      </button>
    </div>
  );
}
```

### Example 3: Product Detail Page

```typescript
import { useProductDetailTracking } from './hooks/useProductTracking';

function ProductDetailPage({ product }) {
  // Tracks time spent on detail page with periodic updates
  useProductDetailTracking(product.id);
  
  return (
    <div>
      <h1>{product.title}</h1>
      {/* Product details */}
    </div>
  );
}
```

### Example 4: Display User Stats

```typescript
import { useState, useEffect } from 'react';
import { getUserStats } from './services/userInteractionService';

function UserStatsPanel() {
  const [stats, setStats] = useState(null);
  
  useEffect(() => {
    getUserStats().then(setStats).catch(console.error);
  }, []);
  
  if (!stats) return <div>Loading stats...</div>;
  
  return (
    <div className="stats-panel">
      <h3>Your Activity</h3>
      <p>Products Viewed: {stats.total_views}</p>
      <p>Products Clicked: {stats.total_clicks}</p>
      <p>Purchases: {stats.total_purchases}</p>
      <p>Click Rate: {(stats.click_through_rate * 100).toFixed(1)}%</p>
    </div>
  );
}
```

---

## 📚 API Reference

### User Identification

```typescript
// Get current user ID (creates one if doesn't exist)
const userId = getUserId();

// Set custom user ID (for authenticated users)
setUserId('authenticated_user_123');

// Clear user ID (for logout)
clearUserId();

// Check if user ID exists
const exists = hasUserId();
```

### Tracking Functions

```typescript
// Track product view
await trackProductView(productId, durationSeconds);

// Track product click
await trackProductClick(productId);

// Track product purchase
await trackProductPurchase(productId, { price: 299.99 });

// Track product ignore
await trackProductIgnore(productId);

// Get user statistics
const stats = await getUserStats();

// Get preference weights
const weights = await getPreferenceWeights();
```

### React Hooks

```typescript
// Auto-track view duration
useProductViewTracking(productId);

// Get tracking functions
const { trackClick, trackPurchase, trackIgnore, trackView } = useProductInteractions();

// Track link clicks
const handleClick = useProductLinkClick(productId, productUrl);

// Track visibility in viewport
const cardRef = useProductVisibility(productId);

// Track detail page views
useProductDetailTracking(productId);
```

---

## 🧪 Testing

### Test User Identification

```typescript
import { getUserId, clearUserId } from './utils/userIdentification';

// Test 1: Get user ID
console.log('User ID:', getUserId());

// Test 2: Clear and regenerate
clearUserId();
console.log('New User ID:', getUserId());
```

### Test Tracking

```typescript
import { trackProductView, getUserStats } from './services/userInteractionService';

// Test tracking
await trackProductView(1, 30);
await trackProductView(2, 45);

// Check stats
const stats = await getUserStats();
console.log('Stats:', stats);
```

### Test in Browser Console

```javascript
// Get user ID
localStorage.getItem('product_search_user_id')

// Clear user ID
localStorage.removeItem('product_search_user_id')

// Check API
fetch('http://localhost:8000/api/user-interactions/stats/YOUR_USER_ID')
  .then(r => r.json())
  .then(console.log)
```

---

## 🎯 Best Practices

1. **Initialize Early**: Call `initializeUserIdentification()` in your App component
2. **Track Views**: Use `useProductViewTracking` in all product card components
3. **Track Clicks**: Always track when users click to view products
4. **Don't Block UI**: All tracking is async and won't block the UI
5. **Handle Errors**: Tracking failures are logged but don't break the app
6. **Test Locally**: Use browser console to verify tracking is working

---

## 🔍 Troubleshooting

### User ID not persisting

**Problem**: User ID changes on every page load

**Solution**: Check if localStorage is enabled in browser

```typescript
try {
  localStorage.setItem('test', 'test');
  localStorage.removeItem('test');
  console.log('localStorage is working');
} catch (e) {
  console.error('localStorage is not available');
}
```

### Tracking not working

**Problem**: Interactions not being tracked

**Solution**: Check API connection

```typescript
import api from './services/api';

// Test API connection
api.get('/health')
  .then(() => console.log('API connected'))
  .catch(err => console.error('API error:', err));
```

### CORS errors

**Problem**: CORS errors when calling API

**Solution**: Ensure backend CORS is configured for your frontend URL

---

## 📖 Additional Resources

- **Backend Integration**: See `docs/USER_PREFERENCE_INTEGRATION_GUIDE.md`
- **API Documentation**: http://localhost:8000/docs
- **Examples**: See `frontend/src/examples/ProductCardWithTracking.tsx`

---

## ✅ Integration Checklist

- [ ] Added `initializeUserIdentification()` to App component
- [ ] Added `useProductViewTracking` to ProductCard component
- [ ] Added click tracking to product links
- [ ] Tested user ID generation in browser console
- [ ] Tested tracking API calls in Network tab
- [ ] Verified interactions appear in backend database

---

**Happy Tracking! 🚀**

The system will now learn from user behavior and provide personalized product recommendations!