import { useEffect, useRef } from 'react';
import { useNotifications } from './NotificationManager';
import type { Product } from '../services/searchRequestService';

interface WebSocketMessage {
  type: string;
  search_request_id?: string;
  status?: string;
  product_name?: string;
  message?: string;
  timestamp?: string;
  stage?: string;
  progress?: number;
  products_found?: number;
  matches_found?: number;
  product?: {
    title: string;
    price: number;
    score: number;
    url: string;
    platform: string;
    location?: string;
  };
  error?: string;
}

export default function WebSocketHandler() {
  const { addNotification, showToast, updateSearchProgress, clearSearchProgress } = useNotifications();
  const hasShownErrorRef = useRef(false);
  const reconnectTimeoutRef = useRef<number>();

  useEffect(() => {
    let ws: WebSocket | null = null;
    let isIntentionallyClosed = false;

    const connect = () => {
      // Don't reconnect if intentionally closed
      if (isIntentionallyClosed) return;

      // Connect to WebSocket
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/notifications`;
      
      console.log('Connecting to WebSocket:', wsUrl);
      
      try {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log('✅ WebSocket connected');
          hasShownErrorRef.current = false; // Reset error flag on successful connection
        };

        ws.onmessage = (event) => {
          try {
            const data: WebSocketMessage = JSON.parse(event.data);
            console.log('📨 WebSocket message:', data);

            switch (data.type) {
              case 'connection':
                // Connection confirmation
                console.log('Connection confirmed:', data.status);
                break;

              case 'heartbeat':
                // Heartbeat to keep connection alive
                console.log('💓 Heartbeat received');
                break;

              case 'search_started':
                showToast(
                  `🔍 Searching for ${data.product_name || 'products'}...`,
                  'info'
                );
                if (data.search_request_id) {
                  updateSearchProgress({
                    searchRequestId: data.search_request_id,
                    stage: 'starting',
                    progress: 0,
                    message: data.message || 'Starting search...',
                  });
                }
                break;

              case 'search_progress':
                if (data.search_request_id) {
                  updateSearchProgress({
                    searchRequestId: data.search_request_id,
                    stage: data.stage || 'processing',
                    progress: data.progress || 0,
                    message: data.message || 'Processing...',
                  });
                }
                break;

              case 'search_complete':
                showToast(
                  `✅ Search complete! Found ${data.matches_found || 0} matches out of ${data.products_found || 0} products.`,
                  'success'
                );
                if (data.search_request_id) {
                  // Keep progress visible for 2 seconds before clearing
                  setTimeout(() => {
                    clearSearchProgress(data.search_request_id!);
                  }, 2000);
                }
                break;

              case 'new_match':
                if (data.product) {
                  // Convert WebSocket product to Product type
                  const product: Product = {
                    id: `temp-${Date.now()}`, // Temporary ID
                    title: data.product.title,
                    price: data.product.price,
                    url: data.product.url,
                    platform: data.product.platform,
                    location: data.product.location,
                    match_score: data.product.score,
                    created_at: data.timestamp || new Date().toISOString(),
                  };
                  
                  addNotification(product);
                  showToast(
                    `🎉 New match: ${data.product.title} - $${data.product.price.toLocaleString()}`,
                    'success'
                  );
                }
                break;

              case 'search_error':
                showToast(
                  `❌ Search failed: ${data.error || data.message || 'Unknown error'}`,
                  'error'
                );
                if (data.search_request_id) {
                  clearSearchProgress(data.search_request_id);
                }
                break;

              default:
                console.log('Unknown message type:', data.type);
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          // Only show error toast once
          if (!hasShownErrorRef.current) {
            showToast('WebSocket connection error. Retrying...', 'warning');
            hasShownErrorRef.current = true;
          }
        };

        ws.onclose = () => {
          console.log('🔌 WebSocket disconnected');
          
          // Only attempt reconnect if not intentionally closed
          if (!isIntentionallyClosed) {
            console.log('Attempting to reconnect in 5 seconds...');
            reconnectTimeoutRef.current = window.setTimeout(() => {
              connect();
            }, 5000);
          }
        };
      } catch (error) {
        console.error('Failed to create WebSocket:', error);
        // Only show error toast once
        if (!hasShownErrorRef.current) {
          showToast('Failed to connect to notification server', 'error');
          hasShownErrorRef.current = true;
        }
      }
    };

    // Initial connection
    connect();

    // Cleanup on unmount
    return () => {
      isIntentionallyClosed = true;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [addNotification, showToast, updateSearchProgress, clearSearchProgress]);

  // This component doesn't render anything
  return null;
}

// Made with Bob
