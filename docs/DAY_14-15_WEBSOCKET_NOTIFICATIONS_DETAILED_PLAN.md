# Day 14-15: WebSocket Notifications - Detailed Implementation Plan

**Total Time:** 8 hours  
**Difficulty:** Intermediate  
**Prerequisites:** Completed Day 13 (Scheduler Service)

---

## 📚 What You'll Learn

- Real-time communication using WebSockets
- Connection management patterns
- Event-driven architecture
- Integration with existing backend services

---

## 🎯 Overview

WebSockets enable **real-time, bidirectional communication** between the server and client. Unlike traditional HTTP requests (request → response), WebSockets maintain an open connection that allows the server to push updates to clients instantly.

**Use Case:** When the orchestrator finds new product matches, it will immediately notify all connected clients without them having to refresh the page.

---

## 🏗️ Architecture & Design Patterns

### Design Patterns Used:

1. **Observer Pattern** (Pub/Sub)
   - Orchestrator publishes events
   - WebSocket manager subscribes and broadcasts to clients
   
2. **Singleton Pattern**
   - Single ConnectionManager instance manages all connections
   
3. **Manager Pattern**
   - ConnectionManager handles connection lifecycle (connect, disconnect, broadcast)

### Architecture Flow:
```
Orchestrator finds match → Notification Event → ConnectionManager → All Connected Clients
```

---

## 📋 Sub-Tasks Breakdown

### **Sub-Task 1: Understand WebSocket Basics** (30 minutes)

**Goal:** Learn how WebSockets work in FastAPI

**What to Learn:**
- WebSocket vs HTTP differences
- Connection lifecycle (connect → send/receive → disconnect)
- FastAPI's WebSocket support

**Reading:**
- FastAPI WebSocket docs: https://fastapi.tiangolo.com/advanced/websockets/

**Key Concepts:**
```python
# WebSocket endpoint structure
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept connection
    try:
        while True:
            data = await websocket.receive_text()  # Receive from client
            await websocket.send_text(f"Echo: {data}")  # Send to client
    except WebSocketDisconnect:
        # Handle disconnection
        pass
```

**Deliverable:** Understanding of WebSocket basics

---

### **Sub-Task 2: Create Connection Manager** (2 hours)

**Goal:** Build a class to manage multiple WebSocket connections

**File to Create:** `backend/app/core/websocket_manager.py`

**What It Does:**
- Keeps track of all active WebSocket connections
- Broadcasts messages to all connected clients
- Handles connection/disconnection

**Implementation Steps:**

#### Step 2.1: Create Basic Manager Class (30 min)
```python
from typing import List
from fastapi import WebSocket

class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""
    
    def __init__(self):
        # List to store active connections
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and store new connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove connection from active list"""
        self.active_connections.remove(websocket)
```

#### Step 2.2: Add Broadcast Functionality (30 min)
```python
    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        # Convert dict to JSON string
        import json
        message_str = json.dumps(message)
        
        # Send to all connections
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                # Handle broken connections
                print(f"Error sending to client: {e}")
```

#### Step 2.3: Add Personal Message Method (30 min)
```python
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific client"""
        await websocket.send_text(message)
```

#### Step 2.4: Create Singleton Instance (30 min)
```python
# At bottom of file
# Create single instance to be used throughout app
manager = ConnectionManager()
```

**Design Pattern Explanation:**
- **Singleton Pattern:** Only one `manager` instance exists, ensuring all parts of the app use the same connection list
- **Manager Pattern:** Encapsulates connection management logic in one place

**Deliverable:** `websocket_manager.py` with ConnectionManager class

---

### **Sub-Task 3: Create WebSocket Endpoint** (1.5 hours)

**Goal:** Create API endpoint that clients connect to

**File to Create:** `backend/app/api/routes/websocket.py`

**Implementation Steps:**

#### Step 3.1: Create Basic Endpoint (30 min)
```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import manager

router = APIRouter()

@router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time notifications
    
    Clients connect here to receive:
    - New product matches
    - Search status updates
    - System notifications
    """
    await manager.connect(websocket)
    
    try:
        # Keep connection alive
        while True:
            # Wait for messages from client (heartbeat/ping)
            data = await websocket.receive_text()
            
            # Echo back to confirm connection
            await manager.send_personal_message(
                f"Connected: {data}", 
                websocket
            )
    
    except WebSocketDisconnect:
        # Client disconnected
        manager.disconnect(websocket)
        print("Client disconnected")
```

#### Step 3.2: Add to Main App (30 min)

**File to Modify:** `backend/app/main.py`

```python
# Add import
from app.api.routes import websocket

# Include router
app.include_router(
    websocket.router,
    tags=["websocket"]
)
```

#### Step 3.3: Test with Simple Client (30 min)

Create test file: `app/test/test_websocket_client.py`

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/notifications"
    
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")
        
        # Send test message
        await websocket.send("Hello Server")
        
        # Receive response
        response = await websocket.recv()
        print(f"Received: {response}")
        
        # Keep connection open
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(test_websocket())
```

**Test Command:**
```bash
# Terminal 1: Start server
cd backend
uvicorn app.main:app --reload

# Terminal 2: Run test client
python test_websocket_client.py
```

**Deliverable:** Working WebSocket endpoint that accepts connections

---

### **Sub-Task 4: Review & Enhance Notification Schema** (30 minutes)

**Goal:** Review existing notification schemas and add WebSocket-specific message formats

**File to Review:** `backend/app/schemas/notification.py` ✅ (Already exists!)

**What's Already Implemented:**
Your existing schema includes:
- ✅ `NotificationType` enum (MATCH_FOUND, SEARCH_STARTED, SEARCH_COMPLETED, ERROR_OCCURRED)
- ✅ `NotificationBase` - Base schema with all required fields
- ✅ `NotificationResponse` - For API responses with computed fields
- ✅ `NotificationListResponse` - For paginated lists
- ✅ Additional helper schemas for filtering and stats

**What You Need to Add:**

#### Step 4.1: Add WebSocket Message Schemas (30 min)

**File to Modify:** `backend/app/schemas/notification.py`

Add these new schemas at the end of the file (before the "# Made with Bob" comment):

```python
# ========================================================================
# WebSocket-Specific Schemas
# ========================================================================

class WebSocketNotificationBase(BaseModel):
    """Base schema for WebSocket notifications."""
    type: NotificationType = Field(..., description="Type of notification")
    message: str = Field(..., description="Notification message text")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When notification was sent")


class WebSocketMatchFoundNotification(WebSocketNotificationBase):
    """WebSocket notification when new product match is found."""
    type: NotificationType = NotificationType.MATCH_FOUND
    search_request_id: str = Field(..., description="ID of the search request")
    product_id: str = Field(..., description="ID of the matched product")
    product_title: str = Field(..., description="Title of the matched product")
    product_price: float = Field(..., description="Price of the matched product")
    product_url: str = Field(..., description="URL to the product listing")
    match_score: float = Field(..., ge=0, le=100, description="Match score (0-100)")
    platform: str = Field(..., description="Platform where product was found")


class WebSocketSearchStatusNotification(WebSocketNotificationBase):
    """WebSocket notification for search status updates."""
    search_request_id: str = Field(..., description="ID of the search request")
    search_execution_id: Optional[str] = Field(None, description="ID of the search execution")
    status: str = Field(..., description="Current status of the search")
    matches_found: Optional[int] = Field(None, description="Number of matches found (for completed searches)")


class WebSocketErrorNotification(WebSocketNotificationBase):
    """WebSocket notification for errors."""
    type: NotificationType = NotificationType.ERROR_OCCURRED
    search_request_id: Optional[str] = Field(None, description="ID of the search request (if applicable)")
    error_details: Optional[str] = Field(None, description="Detailed error information")
    error_code: Optional[str] = Field(None, description="Error code for categorization")


class WebSocketHeartbeat(BaseModel):
    """WebSocket heartbeat/ping message."""
    type: str = Field(default="heartbeat", description="Message type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Current server time")
    server_status: str = Field(default="ok", description="Server status")
```

**Why These Schemas?**
- **WebSocket-specific:** Optimized for real-time messaging (lighter than full API responses)
- **Type safety:** Ensures consistent message structure across WebSocket connections
- **Easy serialization:** Can be converted to JSON with `.dict()` or `.model_dump()`
- **Self-documenting:** Field descriptions help frontend developers understand the data

**Usage Example:**
```python
# In orchestrator or websocket manager
from app.schemas.notification import WebSocketMatchFoundNotification

# Create notification
notification = WebSocketMatchFoundNotification(
    message=f"New match found: {product.title}",
    search_request_id=search_request.id,
    product_id=product.id,
    product_title=product.title,
    product_price=product.price,
    product_url=product.url,
    match_score=match_score,
    platform=product.platform
)

# Send via WebSocket (converts to dict/JSON automatically)
await manager.broadcast(notification.model_dump())
```

**Deliverable:** Enhanced notification schemas with WebSocket support

---

### **Sub-Task 5: Integrate with Orchestrator** (2 hours)

**Goal:** Make orchestrator send notifications when it finds matches

**File to Modify:** `backend/app/core/orchestrator.py`

#### Step 5.1: Import Manager (10 min)
```python
from app.core.websocket_manager import manager
from app.schemas.notification import (
    WebSocketMatchFoundNotification,
    WebSocketSearchStatusNotification,
    WebSocketErrorNotification
)
from datetime import datetime
```

#### Step 5.2: Add Notification Method (30 min)
```python
async def _notify_match_found(
    self,
    search_request_id: str,
    product: Product,
    match_score: float
):
    """Send real-time notification for new match"""
    notification = WebSocketMatchFoundNotification(
        message=f"New match found: {product.title}",
        search_request_id=search_request_id,
        product_id=product.id,
        product_title=product.title,
        product_price=product.price,
        product_url=product.url,
        match_score=match_score,
        platform=product.platform
    )
    
    # Broadcast to all connected clients
    await manager.broadcast(notification.model_dump())
```

#### Step 5.3: Call Notification in Execute Search (1 hour)

Find the section where matches are saved and add notification:

```python
# In execute_search method, after saving match to database
for match in matches:
    # Save to database
    db.add(match)
    db.commit()
    
    # Send real-time notification
    await self._notify_match_found(
        search_request_id=search_request.id,
        product=match,
        match_score=match.match_score
    )
```

#### Step 5.4: Add Search Status Notifications (20 min)
```python
# At start of search
start_notification = WebSocketSearchStatusNotification(
    message=f"Search started: {search_request.product_name}",
    type=NotificationType.SEARCH_STARTED,
    search_request_id=search_request.id,
    search_execution_id=execution.id if execution else None,
    status="started"
)
await manager.broadcast(start_notification.model_dump())

# At end of search
complete_notification = WebSocketSearchStatusNotification(
    message=f"Search completed: {search_request.product_name}",
    type=NotificationType.SEARCH_COMPLETED,
    search_request_id=search_request.id,
    search_execution_id=execution.id if execution else None,
    status="completed",
    matches_found=len(matches)
)
await manager.broadcast(complete_notification.model_dump())
```

**Deliverable:** Orchestrator sends notifications when finding matches

---

### **Sub-Task 6: Add Error Handling** (1 hour)

**Goal:** Handle connection errors gracefully

#### Step 6.1: Improve ConnectionManager (30 min)

**File to Modify:** `backend/app/core/websocket_manager.py`

```python
async def broadcast(self, message: dict):
    """Send message to all connected clients with error handling"""
    import json
    message_str = json.dumps(message)
    
    # Track failed connections
    disconnected = []
    
    for connection in self.active_connections:
        try:
            await connection.send_text(message_str)
        except Exception as e:
            print(f"Error sending to client: {e}")
            disconnected.append(connection)
    
    # Remove failed connections
    for connection in disconnected:
        self.disconnect(connection)
```

#### Step 6.2: Add Connection Heartbeat (30 min)

**File to Modify:** `backend/app/api/routes/websocket.py`

```python
import asyncio

@router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        while True:
            # Set timeout for receiving messages
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0  # 30 second timeout
                )
                
                # Handle ping/pong
                if data == "ping":
                    await websocket.send_text("pong")
                    
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_text(json.dumps({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                }))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

**Deliverable:** Robust error handling and connection management

---

### **Sub-Task 7: Testing** (1.5 hours)

**Goal:** Verify everything works end-to-end

#### Step 7.1: Unit Tests (45 min)

**File to Create:** `backend/app/tests/test_websocket.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_websocket_connection():
    """Test WebSocket connection"""
    client = TestClient(app)
    
    with client.websocket_connect("/ws/notifications") as websocket:
        # Send message
        websocket.send_text("ping")
        
        # Receive response
        data = websocket.receive_text()
        assert "pong" in data or "Connected" in data

def test_websocket_broadcast():
    """Test broadcasting to multiple clients"""
    from app.core.websocket_manager import manager
    import asyncio
    
    # Test broadcast method exists
    assert hasattr(manager, 'broadcast')
    assert hasattr(manager, 'connect')
    assert hasattr(manager, 'disconnect')
```

#### Step 7.2: Integration Test (45 min)

Create: `backend/test_full_notification_flow.py`

```python
import asyncio
import websockets
import json
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.search_request import SearchRequest
from app.core.orchestrator import SearchOrchestrator

async def test_notification_flow():
    """Test complete notification flow"""
    
    # Connect WebSocket client
    uri = "ws://localhost:8000/ws/notifications"
    async with websockets.connect(uri) as websocket:
        print("✓ Connected to WebSocket")
        
        # Trigger a search (this should send notifications)
        db = SessionLocal()
        orchestrator = SearchOrchestrator(db)
        
        # Get first active search request
        search_request = db.query(SearchRequest).filter(
            SearchRequest.is_active == True
        ).first()
        
        if search_request:
            print(f"✓ Triggering search for: {search_request.product_name}")
            
            # Execute search (should trigger notifications)
            await orchestrator.execute_search(search_request.id)
            
            # Listen for notifications
            try:
                for _ in range(5):  # Listen for up to 5 messages
                    message = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=10.0
                    )
                    notification = json.loads(message)
                    print(f"✓ Received: {notification['type']} - {notification['message']}")
            except asyncio.TimeoutError:
                print("✓ No more messages")
        
        db.close()

if __name__ == "__main__":
    asyncio.run(test_notification_flow())
```

**Test Commands:**
```bash
# Run unit tests
pytest backend/app/tests/test_websocket.py -v

# Run integration test (server must be running)
python backend/test_full_notification_flow.py
```

**Deliverable:** All tests passing

---

## 🎯 Final Deliverables Checklist

- [ ] `websocket_manager.py` - Connection manager created
- [ ] `api/routes/websocket.py` - WebSocket endpoint implemented
- [ ] `schemas/notification.py` - Notification schemas defined
- [ ] Orchestrator integration complete
- [ ] Error handling implemented
- [ ] Unit tests written and passing
- [ ] Integration tests successful
- [ ] Real-time notifications working

---

## 🧪 How to Test Everything Works

### Manual Test:

1. **Start the server:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Open browser console** (F12) and run:
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws/notifications');
   
   ws.onopen = () => {
       console.log('Connected!');
       ws.send('ping');
   };
   
   ws.onmessage = (event) => {
       console.log('Received:', JSON.parse(event.data));
   };
   ```

3. **Trigger a search** (in another terminal):
   ```bash
   curl -X POST http://localhost:8000/api/search-requests/1/execute
   ```

4. **Watch browser console** - you should see notifications appear in real-time!

---

## 📚 Key Concepts Summary

### WebSocket Lifecycle:
1. **Connect:** Client initiates connection
2. **Accept:** Server accepts connection
3. **Communicate:** Bidirectional message exchange
4. **Disconnect:** Either side closes connection

### Why Use WebSockets?
- **Real-time updates** without polling
- **Efficient** - single persistent connection
- **Bidirectional** - server can push to client

### Design Patterns:
- **Observer Pattern:** Orchestrator notifies manager, manager notifies clients
- **Singleton:** One manager instance for all connections
- **Manager Pattern:** Centralized connection management

---

## 🚨 Common Issues & Solutions

### Issue: "WebSocket connection failed"
**Solution:** Check server is running and URL is correct (`ws://` not `http://`)

### Issue: "Connection closes immediately"
**Solution:** Add `while True` loop to keep connection alive

### Issue: "Messages not received"
**Solution:** Ensure `await manager.broadcast()` is called with `await`

### Issue: "Multiple connections not working"
**Solution:** Verify using singleton `manager` instance, not creating new instances

---

## 📖 Additional Resources

- **FastAPI WebSockets:** https://fastapi.tiangolo.com/advanced/websockets/
- **WebSocket Protocol:** https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- **Python websockets library:** https://websockets.readthedocs.io/

---

## ✅ Success Criteria

You've successfully completed Day 14-15 when:

1. ✅ WebSocket endpoint accepts connections
2. ✅ Multiple clients can connect simultaneously
3. ✅ Orchestrator sends notifications when finding matches
4. ✅ All connected clients receive notifications instantly
5. ✅ Connections handle errors gracefully
6. ✅ Tests pass
7. ✅ You can see real-time notifications in browser console

---

## 🎓 What You Learned

- Real-time communication with WebSockets
- Connection management patterns
- Event-driven architecture
- Integration between backend services
- Error handling for network connections

**Next:** Day 16-17 - Email Service (sending beautiful HTML emails!)

---

**Good luck! 🚀 Remember: Take breaks, test frequently, and don't hesitate to review the code examples!**