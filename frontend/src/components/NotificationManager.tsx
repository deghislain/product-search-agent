import { useState, createContext, useContext } from 'react';
import type { ReactNode } from 'react';
import MatchNotification from './MatchNotification';
import type { Product } from '../services/searchRequestService';

interface Notification {
  id: string;
  product: Product;
}

interface NotificationContextType {
  addNotification: (product: Product) => void;
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

  return (
    <NotificationContext.Provider value={{ addNotification }}>
      {children}
      <div className="fixed top-0 right-0 z-50 p-4 space-y-4">
        {notifications.map((notification) => (
          <MatchNotification
            key={notification.id}
            product={notification.product}
            onClose={() => removeNotification(notification.id)}
          />
        ))}
      </div>
    </NotificationContext.Provider>
  );
}

// Made with Bob
