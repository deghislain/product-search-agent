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