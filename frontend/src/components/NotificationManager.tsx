import { useState, createContext, useContext, useEffect } from 'react';
import type { ReactNode } from 'react';
import MatchNotification from './MatchNotification';
import type { Product } from '../services/searchRequestService';

interface Notification {
  id: string;
  product: Product;
}

interface SearchProgress {
  searchRequestId: string;
  stage: string;
  progress: number;
  message: string;
}

interface Toast {
  id: string;
  type: 'info' | 'success' | 'error' | 'warning';
  message: string;
}

interface NotificationContextType {
  addNotification: (product: Product) => void;
  showToast: (message: string, type: 'info' | 'success' | 'error' | 'warning') => void;
  updateSearchProgress: (progress: SearchProgress) => void;
  clearSearchProgress: (searchRequestId: string) => void;
}

const NotificationContext = createContext<NotificationContextType | null>(null);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [searchProgress, setSearchProgress] = useState<Map<string, SearchProgress>>(new Map());

  const addNotification = (product: Product) => {
    const notification: Notification = {
      id: `${product.id}-${Date.now()}`,
      product,
    };
    setNotifications(prev => [...prev, notification]);
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const showToast = (message: string, type: 'info' | 'success' | 'error' | 'warning' = 'info') => {
    const toast: Toast = {
      id: `toast-${Date.now()}`,
      type,
      message,
    };
    setToasts(prev => [...prev, toast]);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== toast.id));
    }, 5000);
  };

  const updateSearchProgress = (progress: SearchProgress) => {
    setSearchProgress(prev => {
      const newMap = new Map(prev);
      newMap.set(progress.searchRequestId, progress);
      return newMap;
    });
  };

  const clearSearchProgress = (searchRequestId: string) => {
    setSearchProgress(prev => {
      const newMap = new Map(prev);
      newMap.delete(searchRequestId);
      return newMap;
    });
  };

  // Get toast background color
  const getToastColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      case 'warning':
        return 'bg-yellow-500';
      default:
        return 'bg-blue-500';
    }
  };

  // Get toast icon
  const getToastIcon = (type: string) => {
    switch (type) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      default:
        return 'ℹ️';
    }
  };

  return (
    <NotificationContext.Provider value={{ addNotification, showToast, updateSearchProgress, clearSearchProgress }}>
      {children}
      
      {/* Match Notifications */}
      <div className="fixed top-0 right-0 z-50 p-4 space-y-4">
        {notifications.map((notification) => (
          <MatchNotification
            key={notification.id}
            product={notification.product}
            onClose={() => removeNotification(notification.id)}
          />
        ))}
      </div>

      {/* Toast Notifications */}
      <div className="fixed bottom-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`${getToastColor(toast.type)} text-white px-4 py-3 rounded-lg shadow-lg flex items-center space-x-2 animate-fade-in max-w-md`}
          >
            <span className="text-xl">{getToastIcon(toast.type)}</span>
            <span className="flex-1">{toast.message}</span>
            <button
              onClick={() => setToasts(prev => prev.filter(t => t.id !== toast.id))}
              className="text-white hover:text-gray-200"
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      {/* Search Progress Indicators */}
      <div className="fixed bottom-4 left-4 z-50 space-y-2">
        {Array.from(searchProgress.values()).map((progress) => (
          <div
            key={progress.searchRequestId}
            className="bg-white rounded-lg shadow-lg p-4 max-w-sm animate-fade-in"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-gray-800">🤖 AI Search</span>
              <span className="text-sm text-gray-500">{progress.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${progress.progress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600">{progress.message}</p>
          </div>
        ))}
      </div>
    </NotificationContext.Provider>
  );
}

// Made with Bob
