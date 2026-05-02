/**
 * User Identification Utility
 * 
 * Manages user identification for preference learning.
 * Uses localStorage to persist user ID across sessions.
 */

/**
 * Generate a unique user ID using crypto.randomUUID()
 * Falls back to a timestamp-based ID if crypto is not available
 */
function generateUserId(): string {
  try {
    // Use crypto.randomUUID() if available (modern browsers)
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
      return crypto.randomUUID();
    }
    
    // Fallback: Generate a pseudo-random ID
    return `user_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
  } catch (error) {
    console.error('Error generating user ID:', error);
    // Ultimate fallback
    return `user_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
  }
}

/**
 * Get the current user ID from localStorage.
 * If no ID exists, generates a new one and stores it.
 * 
 * @returns {string} The user ID
 * 
 * @example
 * ```typescript
 * const userId = getUserId();
 * console.log(userId); // "550e8400-e29b-41d4-a716-446655440000"
 * ```
 */
export function getUserId(): string {
  const STORAGE_KEY = 'product_search_user_id';
  
  try {
    // Try to get existing user ID from localStorage
    let userId = localStorage.getItem(STORAGE_KEY);
    
    if (!userId) {
      // Generate new user ID if none exists
      userId = generateUserId();
      localStorage.setItem(STORAGE_KEY, userId);
      console.log('Generated new user ID:', userId);
    }
    
    return userId;
  } catch (error) {
    console.error('Error accessing localStorage:', error);
    // If localStorage is not available, generate a session-only ID
    return generateUserId();
  }
}

/**
 * Clear the stored user ID (useful for testing or logout)
 * 
 * @example
 * ```typescript
 * clearUserId();
 * console.log('User ID cleared');
 * ```
 */
export function clearUserId(): void {
  const STORAGE_KEY = 'product_search_user_id';
  
  try {
    localStorage.removeItem(STORAGE_KEY);
    console.log('User ID cleared from localStorage');
  } catch (error) {
    console.error('Error clearing user ID:', error);
  }
}

/**
 * Check if a user ID exists in localStorage
 * 
 * @returns {boolean} True if user ID exists, false otherwise
 * 
 * @example
 * ```typescript
 * if (hasUserId()) {
 *   console.log('User is identified');
 * }
 * ```
 */
export function hasUserId(): boolean {
  const STORAGE_KEY = 'product_search_user_id';
  
  try {
    return localStorage.getItem(STORAGE_KEY) !== null;
  } catch (error) {
    return false;
  }
}

/**
 * Set a custom user ID (useful for authenticated users)
 * 
 * @param {string} userId - The user ID to set
 * 
 * @example
 * ```typescript
 * // After user logs in
 * setUserId('authenticated_user_123');
 * ```
 */
export function setUserId(userId: string): void {
  const STORAGE_KEY = 'product_search_user_id';
  
  try {
    localStorage.setItem(STORAGE_KEY, userId);
    console.log('User ID set:', userId);
  } catch (error) {
    console.error('Error setting user ID:', error);
  }
}

/**
 * Get user ID with cookie fallback
 * Tries localStorage first, then cookies
 * 
 * @returns {string} The user ID
 */
export function getUserIdWithCookieFallback(): string {
  const STORAGE_KEY = 'product_search_user_id';
  
  try {
    // Try localStorage first
    let userId = localStorage.getItem(STORAGE_KEY);
    
    if (userId) {
      return userId;
    }
    
    // Try cookie fallback
    const cookieUserId = getCookieUserId();
    if (cookieUserId) {
      // Sync to localStorage
      localStorage.setItem(STORAGE_KEY, cookieUserId);
      return cookieUserId;
    }
    
    // Generate new ID
    userId = generateUserId();
    localStorage.setItem(STORAGE_KEY, userId);
    setCookieUserId(userId);
    
    return userId;
  } catch (error) {
    console.error('Error getting user ID:', error);
    return generateUserId();
  }
}

/**
 * Get user ID from cookie
 */
function getCookieUserId(): string | null {
  const name = 'product_search_user_id=';
  const decodedCookie = decodeURIComponent(document.cookie);
  const cookieArray = decodedCookie.split(';');
  
  for (let cookie of cookieArray) {
    cookie = cookie.trim();
    if (cookie.indexOf(name) === 0) {
      return cookie.substring(name.length);
    }
  }
  
  return null;
}

/**
 * Set user ID in cookie
 */
function setCookieUserId(userId: string): void {
  // Set cookie to expire in 1 year
  const expiryDate = new Date();
  expiryDate.setFullYear(expiryDate.getFullYear() + 1);
  
  document.cookie = `product_search_user_id=${userId}; expires=${expiryDate.toUTCString()}; path=/; SameSite=Lax`;
}

/**
 * Initialize user identification on app load
 * Call this in your main App component
 * 
 * @example
 * ```typescript
 * // In App.tsx
 * useEffect(() => {
 *   initializeUserIdentification();
 * }, []);
 * ```
 */
export function initializeUserIdentification(): void {
  const userId = getUserId();
  console.log('User identification initialized:', userId);
}

// Made with Bob
