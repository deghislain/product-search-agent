import { useState, createContext, useContext, useRef, useEffect } from 'react';
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
}

const NotificationContext = createContext<NotificationContextType | null>(null);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};

// Stage → icon
const stageIcon: Record<string, string> = {
  starting:    '🚀',
  initializing:'⚙️',
  searching:   '🔍',
  analyzing:   '🤖',
  pricing:     '💰',
  quality:     '✅',
  saving:      '💾',
  completed:   '🎉',
  failed:      '❌',
  processing:  '⏳',
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

function formatTime(d: Date) {
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [toasts, setToasts]               = useState<Toast[]>([]);
  // Accumulated log entries — never replaced, only appended
  const [logEntries, setLogEntries]        = useState<LogEntry[]>([]);
  const [logMinimised, setLogMinimised]    = useState(false);
  const logEndRef                          = useRef<HTMLDivElement>(null);

  // Auto-scroll to the latest log line
  useEffect(() => {
    if (!logMinimised) {
      logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logEntries, logMinimised]);

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

  const hasActivity = logEntries.length > 0;
  // Is any search still running (last entry for that ID is not completed/failed)?
  const activeIds = new Set(
    logEntries
      .filter(e => e.stage !== 'completed' && e.stage !== 'failed')
      .map(e => e.searchRequestId)
  );
  const isRunning = activeIds.size > 0;

  return (
    <NotificationContext.Provider value={{ addNotification, showToast, updateSearchProgress, clearSearchProgress }}>
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

      {/* ── Agent Activity Log — fixed top-left, below the nav bar ── */}
      <div
        className="fixed left-4 top-28 z-50 bg-white border border-gray-200 rounded-xl shadow-xl flex flex-col"
        style={{ width: '26rem' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-gray-100 bg-gray-50 rounded-t-xl shrink-0">
          <div className="flex items-center gap-2">
            <span className="text-base">🤖</span>
            <span className="text-sm font-semibold text-gray-700">AI Agent Activity</span>
            {isRunning && (
              <span className="inline-flex h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
            )}
          </div>
          <div className="flex items-center gap-1">
            {hasActivity && (
              <button
                onClick={clearLog}
                className="text-gray-400 hover:text-red-500 text-xs px-2 py-0.5 rounded hover:bg-gray-100 transition-colors"
                title="Clear log"
              >
                Clear
              </button>
            )}
            <button
              onClick={() => setLogMinimised(v => !v)}
              className="text-gray-400 hover:text-gray-600 text-xs font-medium px-2 py-0.5 rounded hover:bg-gray-100 transition-colors"
              title={logMinimised ? 'Expand' : 'Minimise'}
            >
              {logMinimised ? '▲' : '▼'}
            </button>
          </div>
        </div>

        {/* Log lines — scrollable, never auto-cleared */}
        {!logMinimised && (
          <div className="overflow-y-auto px-3 py-2 space-y-1" style={{ maxHeight: '22rem' }}>
            {hasActivity ? (
              <>
                {logEntries.map(entry => {
                  const icon = stageIcon[entry.stage] ?? '⏳';
                  const pct  = Math.min(100, Math.max(0, entry.progress));

                  return (
                    <div key={entry.id} className="text-xs border-b border-gray-50 pb-1.5 last:border-0">
                      {/* Row: icon · stage · pct · time */}
                      <div className="flex items-center gap-1.5">
                        <span className="shrink-0">{icon}</span>
                        <span className="font-medium text-gray-700 truncate flex-1">{entry.message}</span>
                        <span className="shrink-0 text-gray-400">{pct}%</span>
                        <span className="shrink-0 text-gray-300">{formatTime(entry.timestamp)}</span>
                      </div>
                      {/* Progress bar */}
                      <div className="mt-1 w-full bg-gray-100 rounded-full h-1">
                        <div
                          className={`h-1 rounded-full transition-all duration-500 ${
                            entry.stage === 'completed' ? 'bg-green-500' :
                            entry.stage === 'failed'    ? 'bg-red-500'   : 'bg-blue-500'
                          }`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
                <div ref={logEndRef} />
              </>
            ) : (
              <p className="text-xs text-gray-400 text-center py-4">
                No active searches. Logs will appear here.
              </p>
            )}
          </div>
        )}
      </div>
    </NotificationContext.Provider>
  );
}

// Made with Bob
