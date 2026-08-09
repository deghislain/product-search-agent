import { useState, createContext, useContext } from 'react';
import type { ReactNode } from 'react';
import MatchNotification from './MatchNotification';
import type { Product } from '../services/searchRequestService';

interface Notification {
  id: string;
  product: Product;
}

// One line in the activity log
export interface LogEntry {
  id: string;
  searchRequestId: string;
  stage: string;
  progress: number;
  message: string;
  timestamp: Date;
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
  // Exposed so consumers (e.g. Dashboard) can render the log inline
  logEntries: LogEntry[];
  logMinimised: boolean;
  setLogMinimised: (v: boolean | ((prev: boolean) => boolean)) => void;
  clearLog: () => void;
  isRunning: boolean;
}

const NotificationContext = createContext<NotificationContextType | null>(null);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};

function getToastBg(type: string) {
  switch (type) {
    case 'success': return 'bg-green-600';
    case 'error':   return 'bg-red-600';
    case 'warning': return 'bg-yellow-500';
    default:        return 'bg-blue-600';
  }
}

function getToastIcon(type: string) {
  switch (type) {
    case 'success': return '✅';
    case 'error':   return '❌';
    case 'warning': return '⚠️';
    default:        return 'ℹ️';
  }
}

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [toasts, setToasts]               = useState<Toast[]>([]);
  // Accumulated log entries — never replaced, only appended
  const [logEntries, setLogEntries]        = useState<LogEntry[]>([]);
  const [logMinimised, setLogMinimised]    = useState(false);

  const addNotification = (product: Product) => {
    setNotifications(prev => [...prev, { id: `${product.id}-${Date.now()}`, product }]);
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const showToast = (message: string, type: 'info' | 'success' | 'error' | 'warning' = 'info') => {
    const toast: Toast = { id: `toast-${Date.now()}-${Math.random()}`, type, message };
    setToasts(prev => [...prev.slice(-3), toast]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== toast.id)), 5000);
  };

  // Append a new log line; never replace existing ones
  const updateSearchProgress = (progress: SearchProgress) => {
    const entry: LogEntry = {
      id: `log-${Date.now()}-${Math.random()}`,
      searchRequestId: progress.searchRequestId,
      stage:    progress.stage,
      progress: progress.progress,
      message:  progress.message,
      timestamp: new Date(),
    };
    setLogEntries(prev => [...prev, entry]);
  };

  // On complete/error, add a final entry but keep the log visible indefinitely
  // Only clear when the user clicks "Clear"
  const clearSearchProgress = (_searchRequestId: string) => {
    // No-op: we no longer auto-clear — user clears manually
  };

  const clearLog = () => setLogEntries([]);

  // Is any search still running (last entry for that ID is not completed/failed)?
  const activeIds = new Set(
    logEntries
      .filter(e => e.stage !== 'completed' && e.stage !== 'failed')
      .map(e => e.searchRequestId)
  );
  const isRunning = activeIds.size > 0;

  return (
    <NotificationContext.Provider value={{ addNotification, showToast, updateSearchProgress, clearSearchProgress, logEntries, logMinimised, setLogMinimised, clearLog, isRunning }}>
      {children}

      {/* ── Match notifications — top-right ── */}
      <div
        className="fixed top-4 right-4 z-50 flex flex-col gap-3 max-h-[80vh] overflow-y-auto pointer-events-none"
        style={{ width: '22rem' }}
      >
        {notifications.map(n => (
          <div key={n.id} className="pointer-events-auto">
            <MatchNotification product={n.product} onClose={() => removeNotification(n.id)} />
          </div>
        ))}
      </div>

      {/* ── Toast notifications — bottom-right ── */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col-reverse gap-2" style={{ width: '22rem' }}>
        {toasts.map(toast => (
          <div
            key={toast.id}
            className={`${getToastBg(toast.type)} text-white px-4 py-3 rounded-lg shadow-lg flex items-start gap-2 animate-fade-in`}
          >
            <span className="text-lg leading-tight shrink-0 mt-0.5">{getToastIcon(toast.type)}</span>
            <span className="flex-1 text-sm leading-snug">{toast.message}</span>
            <button
              onClick={() => setToasts(prev => prev.filter(t => t.id !== toast.id))}
              className="text-white/70 hover:text-white shrink-0 mt-0.5 text-lg leading-none"
              aria-label="Dismiss"
            >×</button>
          </div>
        ))}
      </div>

    </NotificationContext.Provider>
  );
}

// Made with Bob
