import { useState, useEffect } from 'react';
import { getSearchRequests, deleteSearchRequest } from '../services/searchRequestService';
import type { SearchRequest } from '../services/searchRequestService';

export default function SearchRequestList() {
  const [searches, setSearches] = useState<SearchRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch searches on component mount
  useEffect(() => {
    fetchSearches();
  }, []);

  const fetchSearches = async () => {
    try {
      setLoading(true);
      const data = await getSearchRequests();
      setSearches(data);
      setError(null);
    } catch (err) {
      setError('Failed to load search requests');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this search?')) {
      return;
    }

    try {
      await deleteSearchRequest(id);
      setSearches(searches.filter(s => s.id !== id));
    } catch (err) {
      alert('Failed to delete search request');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <p>{error}</p>
        <button 
          onClick={fetchSearches}
          className="mt-2 bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-3 rounded text-sm"
        >
          Retry
        </button>
      </div>
    );
  }

  if (searches.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">No search requests yet</p>
        <p className="text-gray-400 mt-2">Create your first search to get started!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {searches.map((search, index) => (
        <div
          key={search.id}
          className="bg-white shadow-md rounded-lg p-6 hover:shadow-lg transition-all duration-300 animate-fade-in"
          style={{ animationDelay: `${index * 0.1}s` }}
        >
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                {search.product_name}
              </h3>
              
              <p className="text-sm text-gray-600 mb-3">
                {search.product_description}
              </p>
              
              <div className="flex flex-wrap gap-2 mb-3">
                {search.platforms.map((platform) => (
                  <span
                    key={platform}
                    className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                  >
                    {platform}
                  </span>
                ))}
              </div>

              <div className="text-sm text-gray-600 space-y-1">
                <p>Budget: ${search.budget}</p>
                {search.location && (
                  <p>Location: {search.location}</p>
                )}
                {search.match_threshold && (
                  <p>Match Threshold: {search.match_threshold}%</p>
                )}
                <p className="text-xs text-gray-400">
                  Created: {new Date(search.created_at!).toLocaleDateString()}
                </p>
              </div>
            </div>

            <div className="flex flex-col space-y-2 ml-4">
              <span className={`px-3 py-1 rounded text-sm font-medium ${
                search.status === 'active'
                  ? 'bg-green-100 text-green-800'
                  : search.status === 'paused'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {search.status.charAt(0).toUpperCase() + search.status.slice(1)}
              </span>
              
              <button
                onClick={() => handleDelete(search.id!)}
                className="px-3 py-1 bg-red-500 hover:bg-red-700 text-white text-sm rounded"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// Made with Bob
