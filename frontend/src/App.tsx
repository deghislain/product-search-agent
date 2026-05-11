import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Matches from './pages/Matches';
import Settings from './pages/Settings';
import { NotificationProvider } from './components/NotificationManager';
import WebSocketHandler from './components/WebSocketHandler';

function App() {
  return (
    <BrowserRouter>
      <NotificationProvider>
        {/* Phase 2: Enhanced WebSocket Handler with AI notifications */}
        <WebSocketHandler />
        
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/matches" element={<Matches />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </NotificationProvider>
    </BrowserRouter>
  );
}

export default App;

// Made with Bob - Phase 2 Integration Complete
