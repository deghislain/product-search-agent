# Phase 2 Frontend Integration Guide

## Overview
This guide explains how to integrate the Phase 2 AI-powered features into your frontend application.

---

## 🎯 What's New in Phase 2

### **1. AI-Enhanced Product Cards**
- Display AI analysis scores (overall, quality, price)
- Show AI recommendations (buy now, good deal, negotiate, avoid, etc.)
- Highlight red flags and positive signals
- Visual progress bars for scores

### **2. Real-Time WebSocket Notifications**
- Search progress tracking (0% → 100%)
- Toast notifications for events
- Live match notifications
- Error handling

### **3. Enhanced Notification System**
- Multiple notification types (toasts, progress bars, match cards)
- Auto-dismiss functionality
- Customizable styling

---

## 📦 New Components

### **1. ProductCardWithAI.tsx**
Enhanced product card that displays AI analysis.

**Features:**
- AI recommendation badges (🔥 Buy Now!, ✨ Good Deal, etc.)
- Score progress bars (Overall, Quality, Price)
- Red flags and positive signals
- AI reasoning display
- Price analysis

**Usage:**
```tsx
import ProductCardWithAI from './components/ProductCardWithAI';

<ProductCardWithAI 
  product={product} 
  onViewDetails={(p) => console.log('View details:', p)}
/>
```

### **2. NotificationManager.tsx (Enhanced)**
Manages all notification types with new features.

**New Features:**
- Toast notifications (info, success, error, warning)
- Search progress indicators
- Auto-dismiss after 5 seconds
- Multiple simultaneous notifications

**New Methods:**
```tsx
const { 
  addNotification,      // Add match notification
  showToast,            // Show toast message
  updateSearchProgress, // Update search progress
  clearSearchProgress   // Clear progress indicator
} = useNotifications();
```

### **3. WebSocketHandler.tsx (NEW)**
Handles WebSocket connection and message routing.

**Features:**
- Auto-connect to WebSocket server
- Parse and route messages
- Update UI based on message type
- Reconnection handling

**Usage:**
```tsx
import WebSocketHandler from './components/WebSocketHandler';

// In your App.tsx or main layout:
<NotificationProvider>
  <WebSocketHandler />
  {/* Your app content */}
</NotificationProvider>
```

---

## 🔧 Integration Steps

### **Step 1: Update Product Type**
The Product interface now includes AI analysis metadata.

**File:** `frontend/src/services/searchRequestService.ts`

```typescript
export interface AIAnalysis {
  overall_score?: number;
  quality_score?: number;
  price_score?: number;
  recommendation?: 'buy_now' | 'good_deal' | 'fair_price' | 'wait' | 'negotiate' | 'avoid';
  reasoning?: string;
  price_analysis?: {
    market_comparison?: string;
    is_good_deal?: boolean;
    recommendation?: string;
  };
  quality_analysis?: {
    quality_score?: number;
    scam_probability?: number;
    red_flags?: string[];
    positive_signals?: string[];
    recommendation?: string;
  };
}

export interface Product {
  // ... existing fields ...
  metadata?: AIAnalysis;  // NEW!
}
```

### **Step 2: Add WebSocketHandler to App**
**File:** `frontend/src/App.tsx`

```tsx
import { NotificationProvider } from './components/NotificationManager';
import WebSocketHandler from './components/WebSocketHandler';

function App() {
  return (
    <NotificationProvider>
      <WebSocketHandler />
      {/* Your existing app content */}
      <YourRoutes />
    </NotificationProvider>
  );
}
```

### **Step 3: Replace ProductCard with ProductCardWithAI**
**Option A: Replace everywhere**
```tsx
// Old:
import ProductCard from './components/ProductCard';

// New:
import ProductCardWithAI from './components/ProductCardWithAI';

// Usage stays the same:
<ProductCardWithAI product={product} />
```

**Option B: Use conditionally**
```tsx
import ProductCard from './components/ProductCard';
import ProductCardWithAI from './components/ProductCardWithAI';

// Use AI card if metadata exists, otherwise use regular card
{product.metadata ? (
  <ProductCardWithAI product={product} />
) : (
  <ProductCard product={product} />
)}
```

### **Step 4: Update ProductGrid (Optional)**
If you want to show AI cards in your product grid:

**File:** `frontend/src/components/ProductGrid.tsx`

```tsx
import ProductCardWithAI from './ProductCardWithAI';

export default function ProductGrid({ products }: ProductGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {products.map((product) => (
        <ProductCardWithAI 
          key={product.id} 
          product={product}
        />
      ))}
    </div>
  );
}
```

---

## 🎨 UI Components Breakdown

### **Toast Notifications**
Appear in bottom-right corner, auto-dismiss after 5 seconds.

**Types:**
- 🔵 **Info** (blue) - General information
- ✅ **Success** (green) - Successful operations
- ❌ **Error** (red) - Errors and failures
- ⚠️ **Warning** (yellow) - Warnings

**Example:**
```tsx
const { showToast } = useNotifications();

showToast('Search started!', 'info');
showToast('Found 5 matches!', 'success');
showToast('Connection failed', 'error');
showToast('Low quality detected', 'warning');
```

### **Search Progress Indicators**
Appear in bottom-left corner during searches.

**Shows:**
- Current stage (initializing, searching, analyzing)
- Progress percentage (0-100%)
- Status message

**Auto-clears** 2 seconds after completion.

### **Match Notifications**
Appear in top-right corner for new matches.

**Shows:**
- Product image
- Title and price
- Match score
- Quick action buttons

---

## 📊 WebSocket Message Types

### **1. search_started**
```json
{
  "type": "search_started",
  "search_request_id": "123",
  "product_name": "Toyota Camry 2015",
  "message": "AI agents are searching...",
  "timestamp": "2026-05-10T15:30:00Z"
}
```
**UI Action:** Show toast + start progress indicator

### **2. search_progress**
```json
{
  "type": "search_progress",
  "search_request_id": "123",
  "stage": "searching",
  "progress": 30,
  "message": "Scanning platforms..."
}
```
**UI Action:** Update progress bar

### **3. search_complete**
```json
{
  "type": "search_complete",
  "search_request_id": "123",
  "products_found": 45,
  "matches_found": 12,
  "message": "Search complete!"
}
```
**UI Action:** Show success toast + clear progress after 2s

### **4. new_match**
```json
{
  "type": "new_match",
  "search_request_id": "123",
  "product": {
    "title": "Toyota Camry 2015",
    "price": 12500,
    "score": 87.5,
    "url": "https://...",
    "platform": "craigslist"
  }
}
```
**UI Action:** Show match notification card + toast

### **5. search_error**
```json
{
  "type": "search_error",
  "search_request_id": "123",
  "error": "Connection timeout",
  "message": "Search failed"
}
```
**UI Action:** Show error toast + clear progress

---

## 🎯 AI Analysis Display

### **Recommendation Badges**
Color-coded badges based on AI recommendation:

| Recommendation | Badge | Color |
|---------------|-------|-------|
| buy_now | 🔥 Buy Now! | Green (600) |
| good_deal | ✨ Good Deal | Green (500) |
| fair_price | 👍 Fair Price | Blue (500) |
| negotiate | 💬 Negotiate | Yellow (500) |
| wait | ⏳ Wait | Orange (500) |
| avoid | ⚠️ Avoid | Red (600) |

### **Score Bars**
Three progress bars showing:
1. **Overall Score** (purple) - Combined AI assessment
2. **Quality Score** (green/yellow/red) - Product quality
3. **Price Score** (green) - Price value

### **Red Flags Section**
Shows up to 2 red flags in a red-bordered box:
```
⚠️ Red Flags:
• Suspicious pricing
• Poor description quality
```

### **Positive Signals Section**
Shows up to 2 positive signals in a green-bordered box:
```
✅ Positive Signs:
• Detailed description
• Recent listing
```

---

## 🚀 Testing the Integration

### **1. Test WebSocket Connection**
1. Open browser console
2. Look for: `✅ WebSocket connected`
3. Should see: `Connected to real-time notifications` toast

### **2. Test Search Flow**
1. Create a new search request
2. Watch for notifications:
   - Toast: "🔍 Searching for..."
   - Progress bar appears (bottom-left)
   - Progress updates: 10% → 30% → 70% → 100%
   - Toast: "✅ Search complete!"
   - Match notifications (top-right)

### **3. Test AI Product Cards**
1. View search results
2. Check for AI analysis section (purple/blue gradient box)
3. Verify score bars animate
4. Check recommendation badge appears
5. Verify red flags/positive signals display

---

## 🎨 Customization

### **Change Toast Duration**
**File:** `frontend/src/components/NotificationManager.tsx`

```tsx
// Change from 5000ms (5s) to 3000ms (3s)
setTimeout(() => {
  setToasts(prev => prev.filter(t => t.id !== toast.id));
}, 3000);  // ← Change this value
```

### **Change Progress Bar Colors**
**File:** `frontend/src/components/ProductCardWithAI.tsx`

```tsx
// Overall score bar
className="bg-purple-600"  // ← Change color

// Quality score bar
className={`${getQualityColor(aiAnalysis.quality_score)}`}

// Price score bar
className="bg-green-600"  // ← Change color
```

### **Change Recommendation Badge Colors**
**File:** `frontend/src/components/ProductCardWithAI.tsx`

```tsx
const getRecommendationColor = (recommendation?: string) => {
  switch (recommendation) {
    case 'buy_now':
      return 'bg-green-600';  // ← Change colors here
    // ... etc
  }
};
```

---

## 📱 Mobile Responsiveness

All components are mobile-responsive:
- **Toast notifications**: Stack vertically on mobile
- **Progress indicators**: Adjust width on small screens
- **Product cards**: Single column on mobile, grid on desktop
- **Match notifications**: Full width on mobile

---

## 🐛 Troubleshooting

### **WebSocket not connecting**
1. Check backend is running
2. Verify WebSocket endpoint: `/ws/notifications`
3. Check browser console for errors
4. Ensure CORS is configured correctly

### **AI analysis not showing**
1. Verify `product.metadata` exists
2. Check backend is saving AI analysis
3. Ensure Product type includes `metadata?: AIAnalysis`

### **Notifications not appearing**
1. Verify `NotificationProvider` wraps your app
2. Check `WebSocketHandler` is rendered
3. Look for console errors
4. Test with `showToast('Test', 'info')`

### **Progress bar not updating**
1. Check WebSocket messages in console
2. Verify `search_request_id` matches
3. Ensure `updateSearchProgress` is called
4. Check progress value is 0-100

---

## ✅ Checklist

- [ ] Updated Product type with AIAnalysis interface
- [ ] Added NotificationProvider to App.tsx
- [ ] Added WebSocketHandler component
- [ ] Replaced ProductCard with ProductCardWithAI
- [ ] Tested WebSocket connection
- [ ] Tested search flow with notifications
- [ ] Verified AI analysis displays correctly
- [ ] Tested on mobile devices
- [ ] Customized colors/styling (optional)

---

## 🎉 You're Done!

Your frontend now has:
- ✅ Real-time WebSocket notifications
- ✅ AI-powered product analysis display
- ✅ Progress tracking for searches
- ✅ Enhanced user experience
- ✅ Beautiful, responsive UI

**Next Steps:**
- Monitor user feedback
- Adjust notification timing
- Customize colors to match brand
- Add more AI insights as needed

---

**Made with Bob** 🤖