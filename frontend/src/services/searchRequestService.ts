import apiClient from './api';

export interface SearchRequest {
  id?: string;  // Backend uses UUID strings
  product_name: string;
  product_description: string;
  budget: number;
  platforms: string[];
  location?: string;
  match_threshold?: number;
  email_address?: string;
  status: 'active' | 'paused' | 'completed' | 'cancelled';
  created_at?: string;
  updated_at?: string;
}

export interface Product {
     id: string;  // UUID string
     title: string;
     price: number;
     url: string;
     platform: string;
     location?: string;
     description?: string;
     image_url?: string;
     match_score?: number;
     created_at: string;
   }



// GET all search requests
export const getSearchRequests = async (): Promise<SearchRequest[]> => {
  const response = await apiClient.get('/api/search-requests/');
  
  if (response.data.items) {
    return response.data.items.map((item: any) => {
      // Build platforms array based on backend flags
      const platforms: string[] = [];
      if (item.search_craigslist) platforms.push('craigslist');
      if (item.search_ebay) platforms.push('ebay');
      if (item.search_facebook) platforms.push('facebook');
      
      return {
        id: item.id,
        product_name: item.product_name,
        product_description: item.product_description,
        budget: item.budget,
        platforms: platforms,
        location: item.location,
        match_threshold: item.match_threshold,
        status: item.status,
        created_at: item.created_at,
        updated_at: item.updated_at,
      };
    });
  }
  
  return [];
};

// GET single search request
export const getSearchRequest = async (id: string): Promise<SearchRequest> => {
  const response = await apiClient.get(`/api/search-requests/${id}`);
  
  const item = response.data;
  const platforms: string[] = [];
  if (item.search_craigslist) platforms.push('craigslist');
  if (item.search_ebay) platforms.push('ebay');
  if (item.search_facebook) platforms.push('facebook');
  
  return {
    ...item,
    platforms,
  };
};

// POST create new search request
export const createSearchRequest = async (data: Omit<SearchRequest, 'id' | 'status' | 'created_at' | 'updated_at'>): Promise<SearchRequest> => {
  const backendData = {
    product_name: data.product_name,
    product_description: data.product_description,
    budget: data.budget,
    location: data.location || null,
    match_threshold: data.match_threshold || 70.0,
    search_craigslist: data.platforms.includes('craigslist'),
    search_ebay: data.platforms.includes('ebay'),
    search_facebook: data.platforms.includes('facebook'),
    email_address: data.email_address || null,
  };
  
  const response = await apiClient.post('/api/search-requests/', backendData);
  
  // Build platforms array from response
  const platforms: string[] = [];
  if (response.data.search_craigslist) platforms.push('craigslist');
  if (response.data.search_ebay) platforms.push('ebay');
  if (response.data.search_facebook) platforms.push('facebook');
  
  return {
    ...response.data,
    platforms,
  };
};

// PUT update search request
export const updateSearchRequest = async (id: string, data: Partial<SearchRequest>): Promise<SearchRequest> => {
  const response = await apiClient.put(`/api/search-requests/${id}`, data);
  return response.data;
};

// DELETE search request
export const deleteSearchRequest = async (id: string): Promise<void> => {
  await apiClient.delete(`/api/search-requests/${id}`);
};