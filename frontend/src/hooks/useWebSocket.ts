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
  const reconnectTimeout = useRef<number | null>(null);

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

  const sendMessage = useCallback((message: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(message);
      console.log('📤 Sent message:', message);
    } else {
      console.warn('⚠️ WebSocket not connected, cannot send message');
    }
  }, []);

  const reconnect = useCallback(() => {
    reconnectAttempts.current = 0; // Reset attempts
    connect();
  }, [connect]);

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

  useEffect(() => {
    if (!isConnected) return;

    // Send ping every 45 seconds (less than backend's 60 second timeout)
    const pingInterval = setInterval(() => {
      sendMessage('ping');
    }, 45000);

    return () => clearInterval(pingInterval);
  }, [isConnected, sendMessage]);

  return {
    isConnected,
    sendMessage,
    reconnect
  };
}

// Made with Bob
