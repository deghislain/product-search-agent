/**
 * User Interaction Service
 * 
 * Handles tracking user interactions with products for preference learning.
 */

import api from './api';
import { getUserId } from '../utils/userIdentification';

export interface TrackInteractionParams {
  productId: string;
  interactionType: 'view' | 'click' | 'ignore' | 'purchase';
  durationSeconds?: number;
  metadata?: Record<string, any>;
}

export interface UserInteractionStats {
  total_interactions: number;
  total_views: number;
  total_clicks: number;
  total_purchases: number;
  click_through_rate: number;
  purchase_rate: number;
  avg_view_duration: number;
}

export interface UserPreferenceWeights {
  price_sensitivity: number;
  condition_importance: number;
  location_preference: number;
  platform_scores: Record<string, number>;
  preferred_features: string[];
  location_scores: Record<string, number>;
}

/**
 * Track a user interaction with a product
 * 
 * @param params - Interaction parameters
 * @returns Promise that resolves when interaction is tracked
 * 
 * @example
 * ```typescript
 * // Track a product view
 * await trackInteraction({
 *   productId: 123,
 *   interactionType: 'view',
 *   durationSeconds: 30
 * });
 * 
 * // Track a product click
 * await trackInteraction({
 *   productId: 123,
 *   interactionType: 'click'
 * });
 * ```
 */
export async function trackInteraction(params: TrackInteractionParams): Promise<void> {
  try {
    const userId = getUserId();
    
    await api.post('/api/user-interactions/', {
      user_id: userId,
      product_id: params.productId,
      interaction_type: params.interactionType,
      duration_seconds: params.durationSeconds || 0,
      interaction_metadata: params.metadata ? JSON.stringify(params.metadata) : null
    });
    
    console.log(`Tracked ${params.interactionType} interaction for product ${params.productId}`);
  } catch (error) {
    console.error('Failed to track interaction:', error);
    // Don't throw - tracking failures shouldn't break the app
  }
}

/**
 * Track a product view
 * 
 * @param productId - ID of the product
 * @param durationSeconds - How long the user viewed the product
 * 
 * @example
 * ```typescript
 * await trackProductView(123, 45);
 * ```
 */
export async function trackProductView(
  productId: string,
  durationSeconds: number = 0
): Promise<void> {
  return trackInteraction({
    productId,
    interactionType: 'view',
    durationSeconds
  });
}

/**
 * Track a product click
 * 
 * @param productId - ID of the product
 * 
 * @example
 * ```typescript
 * await trackProductClick(123);
 * ```
 */
export async function trackProductClick(productId: string): Promise<void> {
  return trackInteraction({
    productId,
    interactionType: 'click'
  });
}

/**
 * Track a product purchase
 * 
 * @param productId - ID of the product
 * @param metadata - Optional purchase metadata (price, etc.)
 * 
 * @example
 * ```typescript
 * await trackProductPurchase(123, { price: 299.99 });
 * ```
 */
export async function trackProductPurchase(
  productId: string,
  metadata?: Record<string, any>
): Promise<void> {
  return trackInteraction({
    productId,
    interactionType: 'purchase',
    metadata
  });
}

/**
 * Track a product ignore
 * 
 * @param productId - ID of the product
 * 
 * @example
 * ```typescript
 * await trackProductIgnore(123);
 * ```
 */
export async function trackProductIgnore(productId: string): Promise<void> {
  return trackInteraction({
    productId,
    interactionType: 'ignore'
  });
}

/**
 * Get user interaction statistics
 * 
 * @returns Promise that resolves to user statistics
 * 
 * @example
 * ```typescript
 * const stats = await getUserStats();
 * console.log(`Click-through rate: ${stats.click_through_rate}`);
 * ```
 */
export async function getUserStats(): Promise<UserInteractionStats> {
  try {
    const userId = getUserId();
    const response = await api.get(`/user-interactions/stats/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to get user stats:', error);
    throw error;
  }
}

/**
 * Get user preference weights
 * 
 * @returns Promise that resolves to preference weights
 * 
 * @example
 * ```typescript
 * const weights = await getPreferenceWeights();
 * console.log(`Price sensitivity: ${weights.price_sensitivity}`);
 * console.log(`Preferred features: ${weights.preferred_features.join(', ')}`);
 * ```
 */
export async function getPreferenceWeights(): Promise<UserPreferenceWeights> {
  try {
    const userId = getUserId();
    const response = await api.get(`/user-interactions/preferences/${userId}/weights`);
    return response.data;
  } catch (error) {
    console.error('Failed to get preference weights:', error);
    throw error;
  }
}

/**
 * Hook for tracking product view duration
 * Returns start time and a function to track the view
 * 
 * @example
 * ```typescript
 * const { startTracking, stopTracking } = useProductViewTracking();
 * 
 * useEffect(() => {
 *   startTracking();
 *   return () => stopTracking(productId);
 * }, [productId]);
 * ```
 */
export function createViewTracker() {
  let startTime: number | null = null;
  
  return {
    start: () => {
      startTime = Date.now();
    },
    stop: async (productId: string) => {
      if (startTime) {
        const duration = Math.floor((Date.now() - startTime) / 1000);
        if (duration > 0) {
          await trackProductView(productId, duration);
        }
        startTime = null;
      }
    }
  };
}

/**
 * Batch track multiple interactions
 * Useful for tracking multiple actions at once
 * 
 * @param interactions - Array of interactions to track
 * 
 * @example
 * ```typescript
 * await batchTrackInteractions([
 *   { productId: 1, interactionType: 'view', durationSeconds: 30 },
 *   { productId: 2, interactionType: 'view', durationSeconds: 15 },
 *   { productId: 1, interactionType: 'click' }
 * ]);
 * ```
 */
export async function batchTrackInteractions(
  interactions: TrackInteractionParams[]
): Promise<void> {
  try {
    await Promise.all(interactions.map(interaction => trackInteraction(interaction)));
    console.log(`Batch tracked ${interactions.length} interactions`);
  } catch (error) {
    console.error('Failed to batch track interactions:', error);
    // Don't throw - tracking failures shouldn't break the app
  }
}

// Made with Bob
