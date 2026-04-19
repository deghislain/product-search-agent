from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import manager
import logging
import datetime
import asyncio
import json

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
                else:
                    # Echo back to confirm connection
                    await manager.send_personal_message(
                        f"Connected: {data}",
                        websocket
                    )
                    
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_text(json.dumps({
                    "type": "heartbeat",
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }))
    
    except WebSocketDisconnect:
        # Client disconnected
        manager.disconnect(websocket)
        logger.error("Client disconnected")