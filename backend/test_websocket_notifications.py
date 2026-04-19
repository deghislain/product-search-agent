"""
Test script to manually trigger WebSocket notifications

This script sends a test notification to all connected WebSocket clients.
Use this to verify that the frontend receives and displays notifications correctly.

Usage:
    1. Start the backend server: uvicorn app.main:app --reload
    2. Open the frontend in a browser
    3. Run this script: python test_websocket_notifications.py
    4. Check the browser for the notification popup

Requirements:
    - Backend server must be running
    - At least one browser tab must be connected to the WebSocket
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.websocket_manager import manager


async def send_test_notification():
    """Send a test notification to all connected clients"""
    
    print("=" * 70)
    print("WebSocket Test Notification Sender")
    print("=" * 70)
    print()
    
    # Check if any clients are connected
    if not manager.active_connections:
        print("⚠️  No WebSocket clients connected")
        print()
        print("To test:")
        print("1. Make sure backend is running: uvicorn app.main:app --reload")
        print("2. Open frontend in browser: http://localhost:5173")
        print("3. Run this script again")
        print()
        return
    
    print(f"✅ Found {len(manager.active_connections)} connected client(s)")
    print()
    
    # Create test product notification
    test_product = {
        "type": "new_match",
        "data": {
            "product": {
                "id": "test-123",
                "title": "Test iPhone 13 Pro Max 256GB",
                "price": 599.99,
                "url": "https://example.com/test-product",
                "image_url": "https://via.placeholder.com/300x300?text=iPhone+13",
                "platform": "craigslist",
                "location": "San Francisco, CA",
                "posted_date": "2024-01-15",
                "description": "Like new condition, includes original box and accessories",
                "match_score": 85.5
            }
        }
    }
    
    print("📤 Sending test notification...")
    print(f"   Type: {test_product['type']}")
    print(f"   Product: {test_product['data']['product']['title']}")
    print(f"   Price: ${test_product['data']['product']['price']}")
    print(f"   Platform: {test_product['data']['product']['platform']}")
    print()
    
    try:
        # Broadcast to all connected clients
        await manager.broadcast(test_product)
        
        print("✅ Test notification sent successfully!")
        print()
        print("Check your browser for the notification popup.")
        print("It should appear in the top-right corner.")
        print()
        
    except Exception as e:
        print(f"❌ Error sending notification: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def send_multiple_notifications():
    """Send multiple test notifications with different types"""
    
    print("=" * 70)
    print("Sending Multiple Test Notifications")
    print("=" * 70)
    print()
    
    if not manager.active_connections:
        print("⚠️  No WebSocket clients connected")
        return
    
    notifications = [
        {
            "type": "search_started",
            "data": {
                "search_id": "test-search-1",
                "product_name": "iPhone 13",
                "platforms": ["craigslist", "ebay", "facebook"]
            }
        },
        {
            "type": "new_match",
            "data": {
                "product": {
                    "id": "test-456",
                    "title": "iPhone 13 128GB Blue",
                    "price": 499.99,
                    "url": "https://example.com/test-2",
                    "image_url": "https://via.placeholder.com/300x300?text=iPhone",
                    "platform": "ebay",
                    "location": "New York, NY",
                    "posted_date": "2024-01-16",
                    "match_score": 78.0
                }
            }
        },
        {
            "type": "new_match",
            "data": {
                "product": {
                    "id": "test-789",
                    "title": "iPhone 13 Pro 512GB",
                    "price": 699.99,
                    "url": "https://example.com/test-3",
                    "image_url": "https://via.placeholder.com/300x300?text=iPhone+Pro",
                    "platform": "facebook",
                    "location": "Los Angeles, CA",
                    "posted_date": "2024-01-17",
                    "match_score": 92.5
                }
            }
        },
        {
            "type": "search_completed",
            "data": {
                "search_id": "test-search-1",
                "products_found": 3,
                "matches_found": 2,
                "duration_seconds": 45
            }
        }
    ]
    
    for i, notification in enumerate(notifications, 1):
        print(f"📤 Sending notification {i}/{len(notifications)}: {notification['type']}")
        await manager.broadcast(notification)
        await asyncio.sleep(2)  # Wait 2 seconds between notifications
    
    print()
    print("✅ All test notifications sent!")
    print()


def print_usage():
    """Print usage instructions"""
    print()
    print("Usage:")
    print("  python test_websocket_notifications.py [option]")
    print()
    print("Options:")
    print("  (no option)  - Send a single test notification")
    print("  multiple     - Send multiple notifications with delays")
    print("  help         - Show this help message")
    print()
    print("Examples:")
    print("  python test_websocket_notifications.py")
    print("  python test_websocket_notifications.py multiple")
    print()


if __name__ == "__main__":
    print()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "help":
            print_usage()
            sys.exit(0)
        elif sys.argv[1] == "multiple":
            asyncio.run(send_multiple_notifications())
        else:
            print(f"❌ Unknown option: {sys.argv[1]}")
            print_usage()
            sys.exit(1)
    else:
        asyncio.run(send_test_notification())
    
    print()

# Made with Bob
