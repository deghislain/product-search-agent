import { useState, useEffect, useRef } from 'react';
import SearchRequestList from '../components/SearchRequestList';
import SearchRequestForm from '../components/SearchRequestForm';
import { createSearchRequest, getSearchRequests } from '../services/searchRequestService';
import { getMatchingProducts } from '../services/productService';
import { useNotifications } from '../components/NotificationManager';
import type { LogEntry } from '../components/NotificationManager';


// Stage → colour and icon for the log
const STAGE_ICON: Record<string, string> = {
  starting:     '🚀',
  initializing: '⚙️',
  searching:    '🔍',
  analyzing:    '🤖',
  pricing:      '💰',
  quality:      '✅',
  saving:       '💾',
  completed:    '🎉',
  failed:       '❌',
  processing:   '⏳',
};

function formatTime(d: Date) {
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function LogPanel() {
  const { logEntries, logMinimised, setLogMinimised, clearLog, isRunning } = useNotifications();
  const logEndRef = useRef<HTMLDivElement>(null);
  const hasActivity = logEntries.length > 0;

  useEffect(() => {
    if (!logMinimised) {
      logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logEntries, logMinimised]);

  return (
    <div className="mb-8 bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
      {/* Panel header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <span className="text-base leading-none">🤖</span>
          <span className="text-sm font-semibold text-gray-700">AI Agent Activity</span>
          {isRunning && (
            <span className="inline-flex h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
          )}
          {hasActivity && (
            <span className="text-xs text-gray-400 font-normal">
              ({logEntries.length} {logEntries.length === 1 ? 'entry' : 'entries'})
            </span>
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
            title={logMinimised ? 'Expand log' : 'Collapse log'}
          >
            {logMinimised ? '▼ Show' : '▲ Hide'}
          </button>
        </div>
      </div>

      {/* Log body */}
      {!logMinimised && (
        <div className="overflow-y-auto px-4 py-3 space-y-2" style={{ maxHeight: '18rem' }}>
          {hasActivity ? (
            <>
              {logEntries.map((entry: LogEntry) => {
                const icon = STAGE_ICON[entry.stage] ?? '⏳';
                const pct  = Math.min(100, Math.max(0, entry.progress));
                const barColor =
                  entry.stage === 'completed' ? 'bg-green-500' :
                  entry.stage === 'failed'    ? 'bg-red-500'   : 'bg-blue-500';

                return (
                  <div key={entry.id} className="text-xs border-b border-gray-100 pb-2 last:border-0 last:pb-0">
                    <div className="flex items-baseline gap-1.5">
                      <span className="shrink-0 leading-none">{icon}</span>
                      <span className="font-medium text-gray-800 flex-1 min-w-0 break-words leading-snug">
                        {entry.message}
                      </span>
                      <span className="shrink-0 text-gray-400 tabular-nums">{pct}%</span>
                      <span className="shrink-0 text-gray-300 tabular-nums">{formatTime(entry.timestamp)}</span>
                    </div>
                    <div className="mt-1 w-full bg-gray-100 rounded-full h-1">
                      <div
                        className={`h-1 rounded-full transition-all duration-500 ${barColor}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
              <div ref={logEndRef} />
            </>
          ) : (
            <p className="text-xs text-gray-400 text-center py-6">
              No activity yet. Logs will appear here when a search runs.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default function Dashboard() {
  const [showForm, setShowForm] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [stats, setStats] = useState({
    activeSearches: 0,
    totalMatches: 0,
    newToday: 0
  });

  useEffect(() => {
    fetchStats();
  }, [refreshKey]);

  const fetchStats = async () => {
    try {
      // Fetch search requests
      const searches = await getSearchRequests();
      const activeSearches = searches.filter(s => s.status === 'active').length;

      // Fetch products
      const products = await getMatchingProducts();

     
      const totalMatches = products.length;

      // Calculate new today (products created today)
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const newToday = products.filter(p => {
        const createdDate = new Date(p.created_at);
        createdDate.setHours(0, 0, 0, 0);
        return createdDate.getTime() === today.getTime();
      }).length;

      setStats({ activeSearches, totalMatches, newToday });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  return (
    <div className="w-full py-6">
      {/* Centred content column — matches the header "Product Search Agent" alignment */}
      <div className="max-w-4xl mx-auto px-4">

        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Dashboard
          </h1>
          <p className="text-gray-600">
            Manage your product search requests
          </p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">

          <div className="bg-white rounded-lg shadow-md p-6 animate-fade-in flex flex-col items-center text-center">
            <div className="bg-blue-100 rounded-full p-3 mb-3">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <p className="text-gray-500 text-sm font-medium">Active Searches</p>
            <p className="text-3xl font-bold text-blue-600 mt-1">{stats.activeSearches}</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 animate-fade-in flex flex-col items-center text-center" style={{ animationDelay: '0.1s' }}>
            <div className="bg-green-100 rounded-full p-3 mb-3">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-gray-500 text-sm font-medium">Total Matches</p>
            <p className="text-3xl font-bold text-green-600 mt-1">{stats.totalMatches}</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 animate-fade-in flex flex-col items-center text-center" style={{ animationDelay: '0.2s' }}>
            <div className="bg-purple-100 rounded-full p-3 mb-3">
              <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-gray-500 text-sm font-medium">New Today</p>
            <p className="text-3xl font-bold text-purple-600 mt-1">{stats.newToday}</p>
          </div>
        </div>

        {/* Create Search Button */}
        <div className="mb-6 flex justify-center">
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg shadow-md transition-colors flex items-center"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            {showForm ? 'Cancel' : 'Create New Search'}
          </button>
        </div>

        {/* Search Form (conditionally rendered) */}
        {showForm && (
          <div className="mb-8 animate-fade-in">
            <SearchRequestForm
              onSubmit={async (data) => {
                try {
                  await createSearchRequest(data);
                  setShowForm(false);
                  setRefreshKey(prev => prev + 1);
                } catch (error) {
                  console.error('Failed to create search:', error);
                }
              }}
              onCancel={() => setShowForm(false)}
            />
          </div>
        )}

        {/* AI Agent Activity Log — inline, below stat cards */}
        <LogPanel />

        {/* Search Requests List */}
        <div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4 text-center">
            Your Search Requests
          </h2>
          <SearchRequestList key={refreshKey} />
        </div>

      </div>{/* end centred column */}
    </div>
  );
}