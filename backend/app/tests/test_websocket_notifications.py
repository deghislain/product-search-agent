#!/usr/bin/env python3
"""
Standalone test for WebSocket notifications.
Run this while the FastAPI server is running.

Usage:
    Terminal 1: uvicorn app.main:app --reload
    Terminal 2: python test_websocket_notifications.py
"""

import asyncio
import websockets
import json
import sys
from pathlib import Path

# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


from app.database import SessionLocal
from app.models.search_request import SearchRequest
from app.core.orchestrator import SearchOrchestrator


async def test_websocket_notifications():
    """Test WebSocket notification flow"""
    
    print("=" * 70)
    print("WebSocket Notification Flow Test")
    print("=" * 70)
    print()
    
    # Step 1: Connect to WebSocket
    uri = "ws://localhost:8000/ws/notifications"
    print(f"📡 Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket server")
            print()
            
            # Step 2: Get a search request from database
            print("🔍 Looking for active search requests...")
            db = SessionLocal()
            
            try:
                # Find an active search request
                search_request = db.query(SearchRequest).filter(
                    SearchRequest.is_active.is_(True)
                ).first()
                
                if not search_request:
                    print("⚠️  No active search requests found")
                    print("   Create one using the API first:")
                    print("   POST http://localhost:8000/api/search-requests")
                    return
                
                print(f"✅ Found search request: {search_request.product_name}")
                print(f"   ID: {search_request.id}")
                print(f"   Budget: ${search_request.budget}")
                print(f"   Location: {search_request.location}")
                print()
                
                # Step 3: Execute search (this will trigger notifications)
                print("🚀 Executing search...")
                orchestrator = SearchOrchestrator(db)
                
                # Start search in background
                search_task = asyncio.create_task(
                    orchestrator.execute_search(search_request)
                )
                
                # Step 4: Listen for notifications
                print("👂 Listening for notifications...")
                print("-" * 70)
                
                notifications_received = []
                
                try:
                    while True:
                        # Wait for message with timeout
                        message = await asyncio.wait_for(
                            websocket.recv(),
                            timeout=30.0
                        )
                        
                        # Parse notification
                        notification = json.loads(message)
                        notifications_received.append(notification)
                        
                        # Display notification
                        notif_type = notification.get('type', 'unknown')
                        notif_message = notification.get('message', 'no message')
                        timestamp = notification.get('timestamp', '')
                        
                        print(f"📬 [{notif_type}] {notif_message}")
                        
                        # Show additional details for match notifications
                        if notif_type == 'match_found':
                            print(f"   Product: {notification.get('product_title', 'N/A')}")
                            print(f"   Price: ${notification.get('product_price', 0):.2f}")
                            print(f"   Score: {notification.get('match_score', 0):.1f}%")
                            print(f"   Platform: {notification.get('platform', 'N/A')}")
                            print(f"   URL: {notification.get('product_url', 'N/A')}")
                        
                        print()
                        
                        # Check if search is completed
                        if notif_type in ['search_completed', 'error_occurred']:
                            print("✅ Search execution finished")
                            break
                            
                except asyncio.TimeoutError:
                    print("⏱️  Timeout - no more notifications")
                
                # Wait for search task to complete
                await search_task
                
                print("-" * 70)
                print(f"\n📊 Summary:")
                print(f"   Total notifications received: {len(notifications_received)}")
                
                # Count notification types
                type_counts = {}
                for notif in notifications_received:
                    notif_type = notif.get('type', 'unknown')
                    type_counts[notif_type] = type_counts.get(notif_type, 0) + 1
                
                for notif_type, count in type_counts.items():
                    print(f"   - {notif_type}: {count}")
                
                print()
                print("✅ Test completed successfully!")
                
            finally:
                db.close()
                
    except ConnectionRefusedError:
        print("❌ Could not connect to WebSocket server")
        print("   Make sure the FastAPI server is running:")
        print("   uvicorn app.main:app --reload")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print()
    asyncio.run(test_websocket_notifications())
    print()

# Made with Bob
