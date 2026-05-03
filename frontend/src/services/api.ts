import axios from 'axios';

// ============================================================================
// API Configuration
// ============================================================================

// Get API base URL from environment variables
// Development: http://localhost:8000 (from .env.development)
// Production: https://your-backend.onrender.com (from .env.production)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';

// WebSocket URL for real-time notifications
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

// Log the API URL being used (helpful for debugging)
console.log('API Base URL:', API_BASE_URL);
console.log('WebSocket URL:', WS_URL);
console.log('Environment:', import.meta.env.MODE);

// ============================================================================
// Axios Client Configuration
// ============================================================================

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 60000, // 30 second timeout
});

// ============================================================================
// Request Interceptor
// ============================================================================

apiClient.interceptors.request.use(
    (config) => {
        // Log requests in development mode
        if (import.meta.env.DEV) {
            console.log('API Request:', {
                method: config.method?.toUpperCase(),
                url: config.url,
                baseURL: config.baseURL,
                fullURL: `${config.baseURL}${config.url}`,
            });
        }
        
        // You can add auth tokens here later
        // const token = localStorage.getItem('auth_token');
        // if (token) {
        //     config.headers.Authorization = `Bearer ${token}`;
        // }
        
        return config;
    },
    (error) => {
        console.error('Request Error:', error);
        return Promise.reject(error);
    }
);

// ============================================================================
// Response Interceptor
// ============================================================================

apiClient.interceptors.response.use(
    (response) => {
        // Log successful responses in development mode
        if (import.meta.env.DEV) {
            console.log('API Response:', {
                status: response.status,
                url: response.config.url,
                data: response.data,
            });
        }
        return response;
    },
    (error) => {
        // Enhanced error logging
        if (error.response) {
            // Server responded with error status
            console.error('API Error Response:', {
                status: error.response.status,
                statusText: error.response.statusText,
                url: error.config?.url,
                data: error.response.data,
            });
        } else if (error.request) {
            // Request made but no response received
            console.error('API No Response:', {
                url: error.config?.url,
                message: 'No response received from server',
                baseURL: API_BASE_URL,
            });
        } else {
            // Error in request setup
            console.error('API Request Setup Error:', error.message);
        }
        
        return Promise.reject(error);
    }
);

// Email Preferences API
export interface EmailPreferences {
  email: string;
  notify_on_match: boolean;
  daily_digest: boolean;
  digest_time: string;
}

export const getEmailPreferences = async (): Promise<EmailPreferences | null> => {
  try {
    const response = await apiClient.get('/api/email-preferences/');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch email preferences:', error);
    return null;
  }
};

export const updateEmailPreferences = async (preferences: EmailPreferences): Promise<void> => {
  await apiClient.post('/api/email-preferences/', preferences);
};


export interface GlobalEmailPreferences {
  id: number;
  email_address: string;
  notify_on_match: boolean;
  notify_on_start: boolean;
  include_in_digest: boolean;
  digest_time: string;
  digest_timezone: string;
  created_at: string;
  updated_at: string;
}

export interface GlobalEmailPreferencesCreate {
  email_address: string;
  notify_on_match?: boolean;
  notify_on_start?: boolean;
  include_in_digest?: boolean;
  digest_time?: string;
  digest_timezone?: string;
}

export interface GlobalEmailPreferencesUpdate {
  notify_on_match?: boolean;
  notify_on_start?: boolean;
  include_in_digest?: boolean;
  digest_time?: string;
  digest_timezone?: string;
}

export async function createOrUpdateGlobalEmailPreferences(
  data: GlobalEmailPreferencesCreate
): Promise<GlobalEmailPreferences> {
  const response = await fetch(`${API_BASE_URL}/api/global-email-preferences/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to save preferences');
  return response.json();
}

export async function getGlobalEmailPreferences(
  email: string
): Promise<GlobalEmailPreferences | null> {
  const response = await fetch(
    `${API_BASE_URL}/api/global-email-preferences/${encodeURIComponent(email)}`
  );
  if (!response.ok) {
    if (response.status === 404) return null;
    throw new Error('Failed to fetch preferences');
  }
  return response.json();
}

export async function updateGlobalEmailPreferences(
  email: string,
  data: GlobalEmailPreferencesUpdate
): Promise<GlobalEmailPreferences> {
  const response = await fetch(
    `${API_BASE_URL}/api/global-email-preferences/${encodeURIComponent(email)}`,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }
  );
  if (!response.ok) throw new Error('Failed to update preferences');
  return response.json();
}

export default apiClient;


