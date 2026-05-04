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
    client_id = id(websocket)
    logger.info(f"Client {client_id} attempting to connect")
    
    try:
        await manager.connect(websocket)
        logger.info(f"Client {client_id} connected successfully")
        
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection",
            "status": "connected",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }))
        
        while True:
            try:
                # Wait for messages with a longer timeout
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0  # 60 second timeout (increased from 30)
                )
                
                # Handle ping/pong
                if data == "ping":
                    await websocket.send_text("pong")
                    logger.debug(f"Client {client_id} ping/pong")
                else:
                    # Log other messages
                    logger.debug(f"Client {client_id} sent: {data}")
                    
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                try:
                    await websocket.send_text(json.dumps({
                        "type": "heartbeat",
                        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                    }))
                    logger.debug(f"Sent heartbeat to client {client_id}")
                except RuntimeError as e:
                    logger.warning(f"WebSocket closed during heartbeat for client {client_id}: {e}")
                    break
                except Exception as e:
                    logger.error(f"Failed to send heartbeat to client {client_id}: {type(e).__name__}: {e}")
                    break
    
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {type(e).__name__}: {e}")
    finally:
        # Always clean up the connection
        try:
            manager.disconnect(websocket)
            logger.info(f"Client {client_id} cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up client {client_id}: {e}")