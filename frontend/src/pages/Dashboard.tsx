import { useState, useEffect } from 'react';
import SearchRequestList from '../components/SearchRequestList';
import SearchRequestForm from '../components/SearchRequestForm';
import { createSearchRequest, getSearchRequests } from '../services/searchRequestService';
import { getProducts } from '../services/productService';

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
      const products = await getProducts();
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
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Dashboard
        </h1>
        <p className="text-gray-600">
          Manage your product search requests
        </p>
      </div>

          {/* Content will go here */}
          {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6 animate-fade-in">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">Active Searches</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">{stats.activeSearches}</p>
            </div>
            <div className="bg-blue-100 rounded-full p-3">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 animate-fade-in" style={{ animationDelay: '0.1s' }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">Total Matches</p>
              <p className="text-3xl font-bold text-green-600 mt-2">{stats.totalMatches}</p>
            </div>
            <div className="bg-green-100 rounded-full p-3">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 animate-fade-in" style={{ animationDelay: '0.2s' }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">New Today</p>
              <p className="text-3xl font-bold text-purple-600 mt-2">{stats.newToday}</p>
            </div>
            <div className="bg-purple-100 rounded-full p-3">
              <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>
      {/* Create Search Button */}
      <div className="mb-6">
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
                setRefreshKey(prev => prev + 1); // Trigger list refresh
              } catch (error) {
                console.error('Failed to create search:', error);
              }
            }}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}
      {/* Search Requests List */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Your Search Requests
        </h2>
        <SearchRequestList key={refreshKey} />
      </div>
    </div>
  );
}