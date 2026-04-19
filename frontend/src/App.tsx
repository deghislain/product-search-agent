import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState } from 'react';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Matches from './pages/Matches';
import Settings from './pages/Settings';
import { NotificationProvider, useNotifications } from './components/NotificationManager';
import { useWebSocket } from './hooks/useWebSocket';
import { ConnectionStatus } from './components/ConnectionStatus';

// WebSocket Provider Component
function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const { addNotification } = useNotifications();
  const [error, setError] = useState<string | null>(null);
  
  const { isConnected } = useWebSocket({
    url: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/notifications',
    onMessage: (data) => {
      // Handle different message types
      if (data.type === 'new_match') {
        console.log('🎉 New match received:', data.data.product);
        addNotification(data.data.product);
      } else if (data.type === 'search_started') {
        console.log('🔍 Search started:', data.data);
      } else if (data.type === 'search_completed') {
        console.log('✅ Search completed:', data.data);
      } else if (data.type === 'heartbeat') {
        // Heartbeat received, connection is alive
        console.log('💓 Heartbeat received');
      } else {
        console.log('📨 Unknown message type:', data);
      }
    },
    onOpen: () => {
      console.log('✅ Connected to notification server');
      setError(null);
    },
    onClose: () => {
      console.warn('⚠️ Disconnected from notification server');
    },
    onError: (error) => {
      console.error('❌ WebSocket error:', error);
      setError('Connection error. Retrying...');
      setTimeout(() => setError(null), 5000);
    }
  });

  return (
    <>
      {children}
      
      {/* Connection Status Indicator */}
      <ConnectionStatus isConnected={isConnected} />

      {/* Error Toast */}
      {error && (
        <div className="fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 animate-slide-in">
          {error}
        </div>
      )}
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <NotificationProvider>
        <WebSocketProvider>
          <Layout>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/matches" element={<Matches />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
        </WebSocketProvider>
      </NotificationProvider>
    </BrowserRouter>
  );
}

export default App;

// Made with Bob
