from typing import List
from fastapi import WebSocket
import logging
import json

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            # Connection already removed or never added
            logger.debug(f"Connection {id(websocket)} not in active connections list")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific client"""
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        """Send message to all connected clients with error handling"""
        # Skip if no active connections
        if not self.active_connections:
            logger.debug("No active WebSocket connections to broadcast to")
            return
        
        message_str = json.dumps(message)
        logger.debug(f"Broadcasting to {len(self.active_connections)} clients: {message.get('type', 'unknown')}")
        
        # Track failed connections
        disconnected = []
        
        for connection in self.active_connections[:]:  # Create a copy to iterate safely
            try:
                await connection.send_text(message_str)
                logger.debug(f"Sent message to client {id(connection)}: {message.get('type', 'unknown')}")
            except RuntimeError as e:
                # WebSocket is closed or in invalid state
                logger.warning(f"WebSocket closed for client {id(connection)}: {type(e).__name__}: {e}")
                disconnected.append(connection)
            except ConnectionResetError as e:
                # Connection was reset by peer
                logger.warning(f"Connection reset for client {id(connection)}: {e}")
                disconnected.append(connection)
            except Exception as e:
                # Catch all other exceptions with full details
                logger.error(f"Error sending to client {id(connection)}: {type(e).__name__}: {e}", exc_info=True)
                disconnected.append(connection)
        
        # Remove failed connections
        for connection in disconnected:
            try:
                self.disconnect(connection)
                logger.info(f"Removed disconnected client {id(connection)}")
            except Exception as e:
                logger.error(f"Error removing client {id(connection)}: {type(e).__name__}: {e}")


# Create single instance to be used throughout app
manager = ConnectionManager()