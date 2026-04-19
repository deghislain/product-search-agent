from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi import WebSocket
from app.main import app
from app.core.websocket_manager import ConnectionManager, manager


class TestWebSocketConnection:
    """Test WebSocket connection functionality"""
    
    def test_websocket_connection_ping_pong(self):
        """Test WebSocket connection with ping/pong"""
        client = TestClient(app)
        
        with client.websocket_connect("/ws/notifications") as websocket:
            # Send ping message
            websocket.send_text("ping")
            
            # Receive pong response
            data = websocket.receive_text()
            assert data == "pong"
    
    def test_websocket_connection_echo(self):
        """Test WebSocket connection with echo message"""
        client = TestClient(app)
        
        with client.websocket_connect("/ws/notifications") as websocket:
            # Send non-ping message
            websocket.send_text("hello")
            
            # Receive echo response
            data = websocket.receive_text()
            assert "Connected: hello" in data
    
    def test_websocket_multiple_connections(self):
        """Test multiple WebSocket connections"""
        client = TestClient(app)
        
        with client.websocket_connect("/ws/notifications") as ws1:
            with client.websocket_connect("/ws/notifications") as ws2:
                # Send messages to both
                ws1.send_text("ping")
                ws2.send_text("ping")
                
                # Both should respond
                assert ws1.receive_text() == "pong"
                assert ws2.receive_text() == "pong"
    
    def test_websocket_disconnect(self):
        """Test WebSocket disconnection"""
        client = TestClient(app)
        
        # Connect and disconnect
        with client.websocket_connect("/ws/notifications") as websocket:
            websocket.send_text("ping")
            assert websocket.receive_text() == "pong"
        
        # Connection should be closed after context manager exits


class TestConnectionManager:
    """Test ConnectionManager class"""
    
    @pytest.fixture
    def connection_manager(self):
        """Create a fresh ConnectionManager instance for each test"""
        return ConnectionManager()
    
    @pytest.mark.asyncio
    async def test_connect(self, connection_manager):
        """Test connecting a WebSocket"""
        mock_websocket = AsyncMock(spec=WebSocket)
        
        await connection_manager.connect(mock_websocket)
        
        # Verify websocket.accept() was called
        mock_websocket.accept.assert_called_once()
        
        # Verify connection was added to active connections
        assert mock_websocket in connection_manager.active_connections
        assert len(connection_manager.active_connections) == 1
    
    def test_disconnect(self, connection_manager):
        """Test disconnecting a WebSocket"""
        mock_websocket = Mock(spec=WebSocket)
        connection_manager.active_connections.append(mock_websocket)
        
        connection_manager.disconnect(mock_websocket)
        
        # Verify connection was removed
        assert mock_websocket not in connection_manager.active_connections
        assert len(connection_manager.active_connections) == 0
    
    @pytest.mark.asyncio
    async def test_send_personal_message(self, connection_manager):
        """Test sending personal message to specific client"""
        mock_websocket = AsyncMock(spec=WebSocket)
        
        await connection_manager.send_personal_message("test message", mock_websocket)
        
        # Verify send_text was called with correct message
        mock_websocket.send_text.assert_called_once_with("test message")
    
    @pytest.mark.asyncio
    async def test_broadcast_single_client(self, connection_manager):
        """Test broadcasting to single client"""
        mock_websocket = AsyncMock(spec=WebSocket)
        connection_manager.active_connections.append(mock_websocket)
        
        test_message = {"type": "test", "data": "hello"}
        await connection_manager.broadcast(test_message)
        
        # Verify message was sent
        mock_websocket.send_text.assert_called_once()
        sent_message = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_message == test_message
    
    @pytest.mark.asyncio
    async def test_broadcast_multiple_clients(self, connection_manager):
        """Test broadcasting to multiple clients"""
        mock_ws1 = AsyncMock(spec=WebSocket)
        mock_ws2 = AsyncMock(spec=WebSocket)
        mock_ws3 = AsyncMock(spec=WebSocket)
        
        connection_manager.active_connections.extend([mock_ws1, mock_ws2, mock_ws3])
        
        test_message = {"type": "notification", "message": "broadcast test"}
        await connection_manager.broadcast(test_message)
        
        # Verify all clients received the message
        for ws in [mock_ws1, mock_ws2, mock_ws3]:
            ws.send_text.assert_called_once()
            sent_message = json.loads(ws.send_text.call_args[0][0])
            assert sent_message == test_message
    
    @pytest.mark.asyncio
    async def test_broadcast_with_failed_connection(self, connection_manager):
        """Test broadcasting with one failed connection"""
        mock_ws1 = AsyncMock(spec=WebSocket)
        mock_ws2 = AsyncMock(spec=WebSocket)
        mock_ws3 = AsyncMock(spec=WebSocket)
        
        # Make ws2 fail
        mock_ws2.send_text.side_effect = Exception("Connection failed")
        
        connection_manager.active_connections.extend([mock_ws1, mock_ws2, mock_ws3])
        
        test_message = {"type": "test", "data": "error handling"}
        await connection_manager.broadcast(test_message)
        
        # Verify ws1 and ws3 received message
        mock_ws1.send_text.assert_called_once()
        mock_ws3.send_text.assert_called_once()
        
        # Verify failed connection was removed
        assert mock_ws2 not in connection_manager.active_connections
        assert len(connection_manager.active_connections) == 2
    
    @pytest.mark.asyncio
    async def test_broadcast_all_connections_fail(self, connection_manager):
        """Test broadcasting when all connections fail"""
        mock_ws1 = AsyncMock(spec=WebSocket)
        mock_ws2 = AsyncMock(spec=WebSocket)
        
        # Make both fail
        mock_ws1.send_text.side_effect = Exception("Connection 1 failed")
        mock_ws2.send_text.side_effect = Exception("Connection 2 failed")
        
        connection_manager.active_connections.extend([mock_ws1, mock_ws2])
        
        test_message = {"type": "test", "data": "all fail"}
        await connection_manager.broadcast(test_message)
        
        # Verify all connections were removed
        assert len(connection_manager.active_connections) == 0
    
    @pytest.mark.asyncio
    async def test_broadcast_empty_connections(self, connection_manager):
        """Test broadcasting with no active connections"""
        test_message = {"type": "test", "data": "no clients"}
        
        # Should not raise an error
        await connection_manager.broadcast(test_message)
        
        assert len(connection_manager.active_connections) == 0
    
    @pytest.mark.asyncio
    async def test_broadcast_complex_message(self, connection_manager):
        """Test broadcasting complex nested message"""
        mock_websocket = AsyncMock(spec=WebSocket)
        connection_manager.active_connections.append(mock_websocket)
        
        complex_message = {
            "type": "match_found",
            "data": {
                "product": {
                    "id": "123",
                    "title": "Test Product",
                    "price": 99.99,
                    "nested": {
                        "field": "value"
                    }
                },
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
        
        await connection_manager.broadcast(complex_message)
        
        # Verify complex message was serialized correctly
        mock_websocket.send_text.assert_called_once()
        sent_message = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_message == complex_message


class TestWebSocketManager:
    """Test the singleton manager instance"""
    
    def test_manager_exists(self):
        """Test that manager singleton exists"""
        from app.core.websocket_manager import manager
        
        assert manager is not None
        assert isinstance(manager, ConnectionManager)
    
    def test_manager_has_methods(self):
        """Test that manager has all required methods"""
        from app.core.websocket_manager import manager
        
        assert hasattr(manager, 'connect')
        assert hasattr(manager, 'disconnect')
        assert hasattr(manager, 'broadcast')
        assert hasattr(manager, 'send_personal_message')
        assert hasattr(manager, 'active_connections')
    
    def test_manager_is_singleton(self):
        """Test that manager is a singleton"""
        from app.core.websocket_manager import manager as manager1
        from app.core.websocket_manager import manager as manager2
        
        # Both imports should reference the same instance
        assert manager1 is manager2


class TestWebSocketEndpoint:
    """Test WebSocket endpoint behavior"""
    
    def test_websocket_endpoint_exists(self):
        """Test that WebSocket endpoint is registered"""
        client = TestClient(app)
        
        # Should be able to connect
        with client.websocket_connect("/ws/notifications") as websocket:
            assert websocket is not None
            # Send a message to verify connection works
            websocket.send_text("ping")
            response = websocket.receive_text()
            assert response == "pong"
    
    @pytest.mark.asyncio
    async def test_websocket_heartbeat_on_idle(self):
        """Test that heartbeat is sent when connection is idle"""
        from fastapi import WebSocket
        from unittest.mock import AsyncMock, patch
        import asyncio
        
        # Create a mock websocket
        mock_ws = AsyncMock(spec=WebSocket)
        
        # Simulate timeout on first receive, then disconnect
        async def receive_side_effect():
            await asyncio.sleep(0.1)  # Small delay
            raise asyncio.TimeoutError()
        
        mock_ws.receive_text.side_effect = receive_side_effect
        
        # Track what was sent
        sent_messages = []
        async def send_side_effect(msg):
            sent_messages.append(msg)
            # After first heartbeat, raise disconnect
            if len(sent_messages) >= 1:
                from fastapi import WebSocketDisconnect
                raise WebSocketDisconnect()
        
        mock_ws.send_text.side_effect = send_side_effect
        
        # Import and test the endpoint logic
        from app.api.routes.websocket import websocket_endpoint
        from app.core.websocket_manager import manager
        
        # Mock the manager.connect to not actually accept
        original_connect = manager.connect
        async def mock_connect(ws):
            manager.active_connections.append(ws)
        
        manager.connect = mock_connect
        
        try:
            # Run the endpoint (it should timeout and send heartbeat)
            await websocket_endpoint(mock_ws)
        except Exception:
            pass  # Expected to fail when disconnecting
        finally:
            # Restore original
            manager.connect = original_connect
            # Clean up
            if mock_ws in manager.active_connections:
                manager.active_connections.remove(mock_ws)
        
        # Verify heartbeat was sent
        assert len(sent_messages) > 0
        heartbeat = json.loads(sent_messages[0])
        assert heartbeat["type"] == "heartbeat"
        assert "timestamp" in heartbeat


class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality"""
    
    def test_full_connection_lifecycle(self):
        """Test complete connection lifecycle"""
        client = TestClient(app)
        
        # Connect
        with client.websocket_connect("/ws/notifications") as websocket:
            # Send ping
            websocket.send_text("ping")
            assert websocket.receive_text() == "pong"
            
            # Send custom message
            websocket.send_text("test message")
            response = websocket.receive_text()
            assert "Connected: test message" in response
        
        # After context manager, connection should be closed
    
    def test_concurrent_connections(self):
        """Test multiple concurrent connections"""
        client = TestClient(app)
        
        connections = []
        
        # Create multiple connections
        for i in range(3):
            ws = client.websocket_connect("/ws/notifications")
            ws.__enter__()
            connections.append(ws)
        
        try:
            # Send messages to all
            for i, ws in enumerate(connections):
                ws.send_text(f"message_{i}")
                response = ws.receive_text()
                assert f"Connected: message_{i}" in response
        finally:
            # Clean up
            for ws in connections:
                ws.__exit__(None, None, None)


class TestWebSocketErrorHandling:
    """Test error handling in WebSocket connections"""
    
    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_connection(self):
        """Test disconnecting a connection that doesn't exist"""
        connection_manager = ConnectionManager()
        mock_websocket = Mock(spec=WebSocket)
        
        # Should raise ValueError when trying to remove non-existent connection
        with pytest.raises(ValueError):
            connection_manager.disconnect(mock_websocket)
    
    @pytest.mark.asyncio
    async def test_send_to_closed_connection(self):
        """Test sending to a closed connection"""
        connection_manager = ConnectionManager()
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.send_text.side_effect = Exception("Connection closed")
        
        connection_manager.active_connections.append(mock_websocket)
        
        # Broadcast should handle the error and remove the connection
        await connection_manager.broadcast({"type": "test"})
        
        assert mock_websocket not in connection_manager.active_connections


# Run coverage check
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app.core.websocket_manager", "--cov=app.api.routes.websocket", "--cov-report=term-missing"])

# Made with Bob
