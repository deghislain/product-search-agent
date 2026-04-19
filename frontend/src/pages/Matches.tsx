import { useState, useEffect } from 'react';
import ProductGrid from '../components/ProductGrid';
import { getMatchingProducts } from '../services/productService';
import { getSearchRequests } from '../services/searchRequestService';
import type { Product, SearchRequest } from '../services/searchRequestService';

export default function Matches() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'craigslist' | 'facebook' | 'ebay'>('all');
  const [activeSearch, setActiveSearch] = useState<SearchRequest | null>(null);
  const [allSearches, setAllSearches] = useState<SearchRequest[]>([]);

  useEffect(() => {
    fetchSearchesAndProducts();
  }, []);

  useEffect(() => {
    if (activeSearch) {
      fetchProducts();
    }
  }, [filter, activeSearch]);

  const fetchSearchesAndProducts = async () => {
    try {
      setLoading(true);
      // Fetch all active searches
      const searches = await getSearchRequests();
      const activeSearches = searches.filter(s => s.status === 'active');
      setAllSearches(activeSearches);
      
      // Set the first active search as default
      if (activeSearches.length > 0) {
        setActiveSearch(activeSearches[0]);
      } else {
        setError('No active searches found. Create a search to see matches.');
        setLoading(false);
      }
    } catch (err) {
      setError('Failed to load searches');
      console.error(err);
      setLoading(false);
    }
  };

  const fetchProducts = async () => {
    if (!activeSearch) return;
    
    try {
      setLoading(true);
      const data = await getMatchingProducts(activeSearch.id);
      
      // Filter by platform if needed
      const filtered = filter === 'all' 
        ? data 
        : data.filter(p => p.platform === filter);
      
      setProducts(filtered);
      setError(null);
    } catch (err) {
      setError('Failed to load products');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Content will go here */}
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              Product Matches
            </h1>
            <p className="text-gray-600">
              {products.length} products found across all platforms
            </p>
          </div>
    
          {/* Search Selector */}
          {allSearches.length > 0 && (
            <div className="mb-6">
              <label className="block text-gray-700 font-medium mb-2">
                Viewing matches for:
              </label>
              <select
                value={activeSearch?.id || ''}
                onChange={(e) => {
                  const selected = allSearches.find(s => s.id === e.target.value);
                  if (selected) setActiveSearch(selected);
                }}
                className="w-full md:w-auto border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {allSearches.map((search) => (
                  <option key={search.id} value={search.id}>
                    {search.product_name} (${search.budget})
                  </option>
                ))}
              </select>
            </div>
          )}

      {/* Filter Buttons */}
      <div className="mb-6 flex flex-wrap gap-2">
        {['all', 'craigslist', 'facebook', 'ebay'].map((platform) => (
          <button
            key={platform}
            onClick={() => setFilter(platform as any)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors capitalize ${
              filter === platform
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {platform}
          </button>
        ))}
      </div>

      {/* Sort Options */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <label className="text-gray-700 font-medium">Sort by:</label>
          <select className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="date">Newest First</option>
            <option value="price-low">Price: Low to High</option>
            <option value="price-high">Price: High to Low</option>
            <option value="match">Best Match</option>
          </select>
        </div>
        
        <button
          onClick={fetchProducts}
          className="flex items-center space-x-2 text-blue-500 hover:text-blue-700 font-medium"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Refresh</span>
        </button>
      </div>
              {/* Products Grid */}
        <ProductGrid 
          products={products} 
          loading={loading}
          onViewDetails={(product) => {
            // Open product details modal or navigate to details page
            window.open(product.url, '_blank');
          }}
        />

        {/* Error State */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <p>{error}</p>
            <button 
              onClick={fetchProducts}
              className="mt-2 bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-3 rounded text-sm"
            >
              Retry
            </button>
          </div>
        )}
    </div>
  );
}