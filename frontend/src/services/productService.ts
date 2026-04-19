import apiClient from './api';

import type { Product } from './searchRequestService';

export const getProducts = async (): Promise<Product[]> => {
    const response = await apiClient.get('/api/products');
    // Backend returns paginated response with 'items' array
    if (response.data.items) {
        return response.data.items;
    }
    return [];
};

export const getMatchingProducts = async (searchRequestId?: string): Promise<Product[]> => {
    const params = searchRequestId ? { search_request_id: searchRequestId } : {};
    const response = await apiClient.get('/api/products/matches', { params });
    // Backend returns paginated response with 'items' array
    if (response.data.items) {
        return response.data.items;
    }
    return [];
};