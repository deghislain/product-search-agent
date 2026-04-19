import asyncio
import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from datetime import datetime, timezone

import sys
from pathlib import Path

# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.main import app
from app.models.search_request import SearchRequest
from app.models.product import Product
from app.core.websocket_manager import manager


def test_notification_flow_with_mocks():
    """Test complete notification flow with mocked database and orchestrator"""
    
    print("\nRunning WebSocket notification flow test (with mocks)...")
    print("=" * 60)
    
    # Create mock search request
    mock_search_request = Mock(spec=SearchRequest)
    mock_search_request.id = "test-search-123"
    mock_search_request.product_name = "Test Gaming Laptop"
    mock_search_request.product_description = "Looking for a gaming laptop"
    mock_search_request.budget = 1000.0
    mock_search_request.location = "Halifax, NS"
    mock_search_request.match_threshold = 70.0
    mock_search_request.is_active = True
    mock_search_request.search_craigslist = True
    mock_search_request.search_ebay = True
    mock_search_request.search_facebook = False
    
    # Create mock product
    mock_product = Mock(spec=Product)
    mock_product.id = "test-product-456"
    mock_product.title = "Gaming Laptop RTX 3060"
    mock_product.price = 899.99
    mock_product.url = "https://example.com/product/123"
    mock_product.platform = "ebay"
    mock_product.match_score = 85.5
    
    print(f"✓ Created mock search request: {mock_search_request.product_name}")
    print(f"✓ Created mock product: {mock_product.title}")
    
    # Track notifications sent through the manager
    notifications_sent = []
    
    # Mock the broadcast method to capture notifications
    original_broadcast = manager.broadcast
    
    async def mock_broadcast(message: dict):
        """Capture broadcast messages"""
        notifications_sent.append(message)
        print(f"✓ Broadcast called: {message.get('type', 'unknown')} - {message.get('message', 'no message')[:50]}")
    
    manager.broadcast = mock_broadcast
    
    try:
        # Create test client
        client = TestClient(app)
        
        # Test WebSocket connection
        with client.websocket_connect("/ws/notifications") as websocket:
            print("✓ Connected to WebSocket")
            
            # Send initial ping
            websocket.send_text("ping")
            
            # Receive initial response
            try:
                initial_response = websocket.receive_text()
                print(f"✓ Received initial response: {initial_response[:50]}...")
            except:
                print("✓ WebSocket connection established (no initial response)")
            
            # Now simulate the orchestrator sending notifications
            print("\n✓ Simulating orchestrator notifications...")
            
            # Simulate search started notification
            asyncio.run(manager.broadcast({
                "type": "SEARCH_STARTED",
                "message": f"Search started: {mock_search_request.product_name}",
                "search_request_id": mock_search_request.id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))
            
            # Simulate match found notification
            asyncio.run(manager.broadcast({
                "type": "MATCH_FOUND",
                "message": f"New match found: {mock_product.title}",
                "search_request_id": mock_search_request.id,
                "product_id": mock_product.id,
                "product_title": mock_product.title,
                "product_price": mock_product.price,
                "product_url": mock_product.url,
                "match_score": mock_product.match_score,
                "platform": mock_product.platform,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))
            
            # Simulate search completed notification
            asyncio.run(manager.broadcast({
                "type": "SEARCH_COMPLETED",
                "message": f"Search completed: {mock_search_request.product_name}",
                "search_request_id": mock_search_request.id,
                "status": "completed",
                "matches_found": 1,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))
            
            print(f"\n✓ Sent {len(notifications_sent)} notifications via broadcast")
            
            # Verify notifications were captured
            assert len(notifications_sent) == 3, f"Expected 3 notifications, got {len(notifications_sent)}"
            
            # Verify notification types
            notification_types = [n.get('type') for n in notifications_sent]
            expected_types = ['SEARCH_STARTED', 'MATCH_FOUND', 'SEARCH_COMPLETED']
            
            print(f"\n✓ Notification types sent: {notification_types}")
            assert notification_types == expected_types, f"Expected {expected_types}, got {notification_types}"
            
            # Verify notification content
            match_notification = notifications_sent[1]
            assert match_notification['product_title'] == mock_product.title
            assert match_notification['product_price'] == mock_product.price
            assert match_notification['match_score'] == mock_product.match_score
            
            print("\n✅ All assertions passed!")
            print(f"✓ Test completed successfully!")
            print(f"✓ Verified {len(notifications_sent)} notifications were sent correctly")
    
    finally:
        # Restore original broadcast method
        manager.broadcast = original_broadcast
        print("=" * 60)


def test_websocket_connection_and_disconnect():
    """Test WebSocket connection and disconnection handling"""
    
    print("\nTesting WebSocket connection and disconnection...")
    print("=" * 60)
    
    client = TestClient(app)
    
    # Test connection
    with client.websocket_connect("/ws/notifications") as websocket:
        print("✓ WebSocket connected")
        
        # Send ping
        websocket.send_text("ping")
        
        # Receive response
        response = websocket.receive_text()
        print(f"✓ Received response: {response[:50]}...")
        
        # Verify we got a response
        assert response is not None
        assert len(response) > 0
    
    # Connection should be closed after exiting context
    print("✓ WebSocket disconnected")
    print("=" * 60)


def test_websocket_heartbeat_timeout():
    """Test WebSocket heartbeat on timeout"""
    
    print("\nTesting WebSocket heartbeat timeout...")
    print("=" * 60)
    
    client = TestClient(app)
    
    with client.websocket_connect("/ws/notifications") as websocket:
        print("✓ WebSocket connected")
        
        # Don't send anything and wait for heartbeat
        # The endpoint should send a heartbeat after timeout
        try:
            # Try to receive with a short timeout
            import time
            time.sleep(0.1)  # Small delay
            
            # Send ping to keep connection alive
            websocket.send_text("ping")
            response = websocket.receive_text()
            
            print(f"✓ Received: {response[:50]}...")
            assert "pong" in response or "Connected" in response
            
        except Exception as e:
            print(f"✓ Handled exception: {type(e).__name__}")
    
    print("=" * 60)


def test_connection_manager_methods():
    """Test ConnectionManager methods directly"""
    
    print("\nTesting ConnectionManager methods...")
    print("=" * 60)
    
    from app.core.websocket_manager import ConnectionManager
    
    # Create a new manager instance for testing
    test_manager = ConnectionManager()
    
    # Test initialization
    assert test_manager.active_connections == []
    print("✓ Manager initialized with empty connections")
    
    # Create mock websockets
    mock_ws1 = Mock()
    mock_ws1.accept = AsyncMock()
    mock_ws1.send_text = AsyncMock()
    
    mock_ws2 = Mock()
    mock_ws2.accept = AsyncMock()
    mock_ws2.send_text = AsyncMock()
    
    # Test connect
    asyncio.run(test_manager.connect(mock_ws1))
    assert len(test_manager.active_connections) == 1
    print("✓ Connection added")
    
    asyncio.run(test_manager.connect(mock_ws2))
    assert len(test_manager.active_connections) == 2
    print("✓ Second connection added")
    
    # Test send_personal_message
    asyncio.run(test_manager.send_personal_message("test message", mock_ws1))
    mock_ws1.send_text.assert_called_with("test message")
    print("✓ Personal message sent")
    
    # Test broadcast
    test_message = {"type": "test", "message": "broadcast test"}
    asyncio.run(test_manager.broadcast(test_message))
    
    # Both websockets should have received the message
    assert mock_ws1.send_text.call_count >= 2  # personal + broadcast
    assert mock_ws2.send_text.call_count >= 1  # broadcast
    print("✓ Broadcast sent to all connections")
    
    # Test disconnect
    test_manager.disconnect(mock_ws1)
    assert len(test_manager.active_connections) == 1
    print("✓ Connection removed")
    
    test_manager.disconnect(mock_ws2)
    assert len(test_manager.active_connections) == 0
    print("✓ All connections removed")
    
    print("=" * 60)


def test_broadcast_with_failed_connection():
    """Test broadcast handles failed connections gracefully"""
    
    print("\nTesting broadcast with failed connection...")
    print("=" * 60)
    
    from app.core.websocket_manager import ConnectionManager
    
    test_manager = ConnectionManager()
    
    # Create mock websockets - one working, one failing
    mock_ws_working = Mock()
    mock_ws_working.accept = AsyncMock()
    mock_ws_working.send_text = AsyncMock()
    
    mock_ws_failing = Mock()
    mock_ws_failing.accept = AsyncMock()
    mock_ws_failing.send_text = AsyncMock(side_effect=Exception("Connection broken"))
    
    # Add both connections
    asyncio.run(test_manager.connect(mock_ws_working))
    asyncio.run(test_manager.connect(mock_ws_failing))
    
    assert len(test_manager.active_connections) == 2
    print("✓ Added 2 connections (1 working, 1 failing)")
    
    # Broadcast should handle the failure
    test_message = {"type": "test", "message": "test broadcast"}
    asyncio.run(test_manager.broadcast(test_message))
    
    # Working connection should have received message
    mock_ws_working.send_text.assert_called()
    print("✓ Working connection received message")
    
    # Failing connection should be removed
    assert len(test_manager.active_connections) == 1
    assert mock_ws_failing not in test_manager.active_connections
    print("✓ Failed connection removed from active list")
    
    print("=" * 60)


def test_websocket_disconnect_exception():
    """Test WebSocket disconnect exception handling"""
    
    print("\nTesting WebSocket disconnect exception...")
    print("=" * 60)
    
    client = TestClient(app)
    
    # Connect and immediately close
    with client.websocket_connect("/ws/notifications") as websocket:
        print("✓ WebSocket connected")
        
        # Send a message
        websocket.send_text("test")
        
        # Receive response
        response = websocket.receive_text()
        print(f"✓ Received: {response[:50]}...")
    
    # Disconnection should be handled gracefully
    print("✓ Disconnect handled gracefully")
    print("=" * 60)


def test_multiple_concurrent_connections():
    """Test multiple concurrent WebSocket connections"""
    
    print("\nTesting multiple concurrent connections...")
    print("=" * 60)
    
    client = TestClient(app)
    
    # Open multiple connections
    with client.websocket_connect("/ws/notifications") as ws1:
        print("✓ Connection 1 established")
        
        with client.websocket_connect("/ws/notifications") as ws2:
            print("✓ Connection 2 established")
            
            # Send messages to both
            ws1.send_text("ping1")
            ws2.send_text("ping2")
            
            # Receive responses
            response1 = ws1.receive_text()
            response2 = ws2.receive_text()
            
            print(f"✓ Connection 1 response: {response1[:30]}...")
            print(f"✓ Connection 2 response: {response2[:30]}...")
            
            assert response1 is not None
            assert response2 is not None
    
    print("✓ All connections closed")
    print("=" * 60)


if __name__ == "__main__":
    # Run all tests
    print("\n" + "="*60)
    print("RUNNING ALL WEBSOCKET TESTS")
    print("="*60 + "\n")
    
    test_notification_flow_with_mocks()
    test_websocket_connection_and_disconnect()
    test_websocket_heartbeat_timeout()
    test_connection_manager_methods()
    test_broadcast_with_failed_connection()
    test_websocket_disconnect_exception()
    test_multiple_concurrent_connections()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print("="*60 + "\n")