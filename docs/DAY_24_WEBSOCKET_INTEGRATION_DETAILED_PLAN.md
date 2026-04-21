# Day 24: WebSocket Integration - Detailed Implementation Plan

**Estimated Time:** 4 hours  
**Difficulty:** Intermediate  
**Prerequisites:** Basic understanding of React hooks, WebSocket protocol, and async JavaScript

---

## 📋 Overview

This task involves creating a custom React hook to manage WebSocket connections and integrating it with existing components to enable real-time notifications when new product matches are found.

**What You'll Build:**
- A reusable `useWebSocket` hook for managing WebSocket connections
- Integration with the notification system to show real-time alerts
- Automatic reconnection logic for reliability
- Connection status indicators

---

## 🎯 Learning Objectives

By completing this task, you will learn:
1. How to create custom React hooks
2. How WebSocket connections work in a React application
3. How to handle connection lifecycle (connect, disconnect, reconnect)
4. How to parse and handle real-time messages
5. How to integrate WebSocket data with React state management

---

## 📚 Background Knowledge

### What is WebSocket?

WebSocket is a protocol that provides **full-duplex communication** between a client (browser) and server over a single TCP connection. Unlike HTTP requests that are one-way (client asks, server responds), WebSocket allows:
- **Server → Client**: Server can push data to client anytime
- **Client → Server**: Client can send data to server anytime
- **Persistent Connection**: Connection stays open (no need to reconnect for each message)

### Why Use WebSocket for Notifications?

Instead of the frontend constantly asking "Any new matches?" (polling), the backend can instantly notify the frontend when a match is found. This is:
- ✅ More efficient (less network traffic)
- ✅ Faster (instant notifications)
- ✅ Better user experience (real-time updates)

### WebSocket Message Format

Our backend sends messages in JSON format:
```json
{
  "type": "new_match",
  "data": {
    "product": {
      "id": "123",
      "title": "iPhone 13",
      "price": 500,
      "url": "https://...",
      "image_url": "https://...",
      "platform": "craigslist"
    }
  }
}
```

---

## 🔧 Sub-Tasks Breakdown

### **Sub-Task 1: Create the useWebSocket Hook** (90 minutes)

**File to Create:** `frontend/src/hooks/useWebSocket.ts`

**What This Hook Does:**
- Manages WebSocket connection lifecycle
- Handles automatic reconnection on disconnect
- Provides connection status to components
- Sends and receives messages
- Cleans up connection when component unmounts

**Step-by-Step Implementation:**

#### Step 1.1: Create the Hook File and Basic Structure (15 min)

Create `frontend/src/hooks/useWebSocket.ts` with:

```typescript
import { useEffect, useRef, useState, useCallback } from 'react';

interface UseWebSocketOptions {
  url: string;
  onMessage?: (data: any) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  sendMessage: (message: string) => void;
  reconnect: () => void;
}

export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
  // We'll implement this step by step
}
```

**Key Concepts:**
- `useRef`: Stores WebSocket instance without causing re-renders
- `useState`: Tracks connection status (for UI updates)
- `useCallback`: Memoizes functions to prevent unnecessary re-renders
- `useEffect`: Manages connection lifecycle

#### Step 1.2: Add State and Refs (10 min)

Inside the hook, add:

```typescript
const {
  url,
  onMessage,
  onOpen,
  onClose,
  onError,
  reconnectInterval = 3000, // 3 seconds
  maxReconnectAttempts = 5
} = options;

// Store WebSocket instance (doesn't cause re-render when changed)
const ws = useRef<WebSocket | null>(null);

// Track connection status (causes re-render when changed)
const [isConnected, setIsConnected] = useState(false);

// Track reconnection attempts
const reconnectAttempts = useRef(0);
const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);
```

**Why useRef for WebSocket?**
- WebSocket instance doesn't need to trigger re-renders
- We need the same instance across renders
- Changing it shouldn't cause component updates

**Why useState for isConnected?**
- UI needs to show connection status
- Changes should trigger re-renders to update UI

#### Step 1.3: Implement Connection Logic (20 min)

Add the `connect` function:

```typescript
const connect = useCallback(() => {
  try {
    // Close existing connection if any
    if (ws.current) {
      ws.current.close();
    }

    // Create new WebSocket connection
    ws.current = new WebSocket(url);

    // Handle connection opened
    ws.current.onopen = () => {
      console.log('✅ WebSocket connected');
      setIsConnected(true);
      reconnectAttempts.current = 0; // Reset attempts on success
      onOpen?.(); // Call optional callback
    };

    // Handle incoming messages
    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📨 WebSocket message:', data);
        onMessage?.(data); // Call optional callback with parsed data
      } catch (error) {
        console.error('❌ Error parsing WebSocket message:', error);
      }
    };

    // Handle connection closed
    ws.current.onclose = () => {
      console.log('🔌 WebSocket disconnected');
      setIsConnected(false);
      onClose?.(); // Call optional callback
      
      // Attempt reconnection if under max attempts
      if (reconnectAttempts.current < maxReconnectAttempts) {
        reconnectAttempts.current++;
        console.log(`🔄 Reconnecting... (Attempt ${reconnectAttempts.current}/${maxReconnectAttempts})`);
        
        reconnectTimeout.current = setTimeout(() => {
          connect();
        }, reconnectInterval);
      } else {
        console.error('❌ Max reconnection attempts reached');
      }
    };

    // Handle errors
    ws.current.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      onError?.(error); // Call optional callback
    };

  } catch (error) {
    console.error('❌ Error creating WebSocket:', error);
  }
}, [url, onMessage, onOpen, onClose, onError, reconnectInterval, maxReconnectAttempts]);
```

**Key Points:**
- `useCallback` prevents function recreation on every render
- Automatic reconnection with exponential backoff
- Proper error handling and logging
- Optional callbacks for flexibility

#### Step 1.4: Implement Send Message Function (10 min)

```typescript
const sendMessage = useCallback((message: string) => {
  if (ws.current && ws.current.readyState === WebSocket.OPEN) {
    ws.current.send(message);
    console.log('📤 Sent message:', message);
  } else {
    console.warn('⚠️ WebSocket not connected, cannot send message');
  }
}, []);
```

**Why Check readyState?**
- `WebSocket.OPEN` (1) = Connection is ready
- `WebSocket.CONNECTING` (0) = Still connecting
- `WebSocket.CLOSING` (2) = Closing
- `WebSocket.CLOSED` (3) = Closed

#### Step 1.5: Implement Manual Reconnect (5 min)

```typescript
const reconnect = useCallback(() => {
  reconnectAttempts.current = 0; // Reset attempts
  connect();
}, [connect]);
```

#### Step 1.6: Add Lifecycle Management with useEffect (20 min)

```typescript
useEffect(() => {
  // Connect when component mounts
  connect();

  // Cleanup when component unmounts
  return () => {
    console.log('🧹 Cleaning up WebSocket connection');
    
    // Clear reconnection timeout
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }
    
    // Close WebSocket connection
    if (ws.current) {
      ws.current.close();
    }
  };
}, [connect]);
```

**Why This Matters:**
- Prevents memory leaks
- Closes connection when component unmounts
- Clears pending reconnection attempts

#### Step 1.7: Return Hook Interface (5 min)

```typescript
return {
  isConnected,
  sendMessage,
  reconnect
};
```

#### Step 1.8: Add Heartbeat/Ping (Optional - 15 min)

To keep connection alive, add periodic ping:

```typescript
useEffect(() => {
  if (!isConnected) return;

  // Send ping every 30 seconds
  const pingInterval = setInterval(() => {
    sendMessage('ping');
  }, 30000);

  return () => clearInterval(pingInterval);
}, [isConnected, sendMessage]);
```

**Testing Sub-Task 1:**

Create a test component to verify the hook works:

```typescript
// frontend/src/components/WebSocketTest.tsx
import { useWebSocket } from '../hooks/useWebSocket';

export function WebSocketTest() {
  const { isConnected, sendMessage } = useWebSocket({
    url: 'ws://localhost:8000/ws/notifications',
    onMessage: (data) => {
      console.log('Received:', data);
    }
  });

  return (
    <div>
      <p>Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}</p>
      <button onClick={() => sendMessage('test')}>Send Test</button>
    </div>
  );
}
```

---

### **Sub-Task 2: Integrate WebSocket with Notification System** (60 minutes)

**Files to Modify:**
- `frontend/src/App.tsx` - Add WebSocket provider
- `frontend/src/components/NotificationManager.tsx` - Connect to WebSocket

#### Step 2.1: Update App.tsx to Use WebSocket (20 min)

**Current Structure:**
```typescript
<NotificationProvider>
  <RouterProvider router={router} />
</NotificationProvider>
```

**New Structure:**
```typescript
<NotificationProvider>
  <WebSocketProvider>
    <RouterProvider router={router} />
  </WebSocketProvider>
</NotificationProvider>
```

**Implementation:**

1. Import the hook:
```typescript
import { useWebSocket } from './hooks/useWebSocket';
import { useNotifications } from './components/NotificationManager';
```

2. Create WebSocketProvider component:
```typescript
function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const { addNotification } = useNotifications();
  
  const { isConnected } = useWebSocket({
    url: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/notifications',
    onMessage: (data) => {
      // Handle different message types
      if (data.type === 'new_match') {
        addNotification(data.data.product);
      } else if (data.type === 'search_started') {
        console.log('Search started:', data.data);
      } else if (data.type === 'search_completed') {
        console.log('Search completed:', data.data);
      }
    },
    onOpen: () => {
      console.log('✅ Connected to notification server');
    },
    onClose: () => {
      console.warn('⚠️ Disconnected from notification server');
    }
  });

  return (
    <>
      {children}
      {/* Optional: Show connection status indicator */}
      <div className="fixed bottom-4 right-4 z-50">
        {isConnected ? (
          <div className="bg-green-500 text-white px-3 py-1 rounded-full text-sm">
            🟢 Live
          </div>
        ) : (
          <div className="bg-red-500 text-white px-3 py-1 rounded-full text-sm">
            🔴 Offline
          </div>
        )}
      </div>
    </>
  );
}
```

#### Step 2.2: Add Environment Variable (5 min)

Create/update `frontend/.env.development`:
```
VITE_WS_URL=ws://localhost:8000/ws/notifications
```

Create/update `frontend/.env.production`:
```
VITE_WS_URL=wss://your-production-domain.com/ws/notifications
```

**Note:** Use `ws://` for local development, `wss://` for production (secure WebSocket)

#### Step 2.3: Test Integration (20 min)

**Manual Testing Steps:**

1. Start backend server:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Start frontend:
```bash
cd frontend
npm run dev
```

3. Open browser console and check for:
   - "✅ WebSocket connected" message
   - Connection status indicator shows "🟢 Live"

4. Create a new search from the dashboard

5. Watch for:
   - "📨 WebSocket message" in console
   - Notification popup appears when match is found

#### Step 2.4: Add Error Handling (15 min)

Update WebSocketProvider to handle errors gracefully:

```typescript
const [error, setError] = useState<string | null>(null);

const { isConnected } = useWebSocket({
  // ... existing options
  onError: (error) => {
    setError('Connection error. Retrying...');
    setTimeout(() => setError(null), 5000);
  }
});

// Show error toast if connection fails
{error && (
  <div className="fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded">
    {error}
  </div>
)}
```

---

### **Sub-Task 3: Add Connection Status Indicator** (30 minutes)

**File to Create:** `frontend/src/components/ConnectionStatus.tsx`

#### Step 3.1: Create Status Component (20 min)

```typescript
import { useEffect, useState } from 'react';

interface ConnectionStatusProps {
  isConnected: boolean;
}

export function ConnectionStatus({ isConnected }: ConnectionStatusProps) {
  const [showStatus, setShowStatus] = useState(true);

  // Auto-hide after 3 seconds if connected
  useEffect(() => {
    if (isConnected) {
      const timer = setTimeout(() => setShowStatus(false), 3000);
      return () => clearTimeout(timer);
    } else {
      setShowStatus(true);
    }
  }, [isConnected]);

  if (!showStatus) return null;

  return (
    <div className={`
      fixed bottom-4 right-4 z-50 
      px-4 py-2 rounded-lg shadow-lg
      transition-all duration-300
      ${isConnected 
        ? 'bg-green-500 text-white' 
        : 'bg-red-500 text-white animate-pulse'
      }
    `}>
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-white' : 'bg-white'}`} />
        <span className="text-sm font-medium">
          {isConnected ? 'Connected' : 'Reconnecting...'}
        </span>
      </div>
    </div>
  );
}
```

#### Step 3.2: Integrate Status Component (10 min)

Update `WebSocketProvider` in `App.tsx`:

```typescript
import { ConnectionStatus } from './components/ConnectionStatus';

// Inside WebSocketProvider return:
return (
  <>
    {children}
    <ConnectionStatus isConnected={isConnected} />
  </>
);
```

---

### **Sub-Task 4: Testing and Debugging** (60 minutes)

#### Step 4.1: Create Test Script (20 min)

Create `backend/test_websocket_notifications.py`:

```python
"""
Test script to manually trigger WebSocket notifications
"""
import asyncio
import json
from app.core.websocket_manager import manager

async def send_test_notification():
    """Send a test notification to all connected clients"""
    test_product = {
        "type": "new_match",
        "data": {
            "product": {
                "id": "test-123",
                "title": "Test iPhone 13",
                "price": 500.0,
                "url": "https://example.com/test",
                "image_url": "https://via.placeholder.com/300",
                "platform": "craigslist",
                "location": "San Francisco, CA",
                "posted_date": "2024-01-01"
            }
        }
    }
    
    await manager.broadcast(json.dumps(test_product))
    print("✅ Test notification sent!")

if __name__ == "__main__":
    asyncio.run(send_test_notification())
```

#### Step 4.2: Test Scenarios (30 min)

**Test 1: Basic Connection**
- Open app in browser
- Check console for "✅ WebSocket connected"
- Verify status indicator shows "🟢 Live"

**Test 2: Receive Notification**
- Run test script: `python backend/test_websocket_notifications.py`
- Verify notification popup appears
- Check notification contains correct product info

**Test 3: Reconnection**
- Stop backend server
- Verify status shows "🔴 Offline"
- Restart backend server
- Verify automatic reconnection within 3 seconds

**Test 4: Multiple Tabs**
- Open app in 2 browser tabs
- Trigger notification
- Verify both tabs receive notification

**Test 5: Network Interruption**
- Open browser DevTools → Network tab
- Set throttling to "Offline"
- Wait 5 seconds
- Set back to "Online"
- Verify reconnection

#### Step 4.3: Debug Common Issues (10 min)

**Issue: "WebSocket connection failed"**
- ✅ Check backend is running
- ✅ Verify URL is correct (ws:// not http://)
- ✅ Check CORS settings in backend

**Issue: "Messages not received"**
- ✅ Check browser console for errors
- ✅ Verify message format matches expected structure
- ✅ Check onMessage callback is called

**Issue: "Constant reconnection loop"**
- ✅ Check backend WebSocket endpoint is working
- ✅ Verify no errors in backend logs
- ✅ Check reconnection interval isn't too short

---

## ✅ Definition of Done

This task is complete when:

- [ ] `useWebSocket` hook is created and working
- [ ] Hook handles connection, disconnection, and reconnection
- [ ] WebSocket is integrated with NotificationManager
- [ ] Real-time notifications appear when matches are found
- [ ] Connection status indicator shows current state
- [ ] All test scenarios pass
- [ ] Code is documented with comments
- [ ] No console errors in browser
- [ ] Changes are committed to Git

---

## 📝 Code Review Checklist

Before marking complete, verify:

- [ ] WebSocket connection closes on component unmount (no memory leaks)
- [ ] Reconnection logic has max attempts limit
- [ ] Error handling is implemented for all scenarios
- [ ] TypeScript types are properly defined
- [ ] Console logs are helpful for debugging
- [ ] Environment variables are used for URLs
- [ ] Code follows project conventions

---

## 🎓 Learning Resources

**WebSocket Basics:**
- [MDN WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [WebSocket Protocol RFC](https://datatracker.ietf.org/doc/html/rfc6455)

**React Hooks:**
- [React useEffect](https://react.dev/reference/react/useEffect)
- [React useRef](https://react.dev/reference/react/useRef)
- [React useCallback](https://react.dev/reference/react/useCallback)

**FastAPI WebSocket:**
- [FastAPI WebSocket Documentation](https://fastapi.tiangolo.com/advanced/websockets/)

---

## 🚀 Next Steps

After completing this task:
1. Move to Day 25-26: Testing
2. Consider adding features like:
   - Message history
   - Notification sound
   - Desktop notifications (Notification API)
   - Unread notification counter

---

## 💡 Tips for Junior Developers

1. **Start Simple**: Get basic connection working first, then add features
2. **Use Console Logs**: Add lots of logs to understand flow
3. **Test Incrementally**: Test each sub-task before moving to next
4. **Read Error Messages**: They usually tell you exactly what's wrong
5. **Ask for Help**: If stuck for >30 minutes, ask a senior developer
6. **Take Breaks**: WebSocket debugging can be frustrating, step away if needed

**Good luck! 🎉**