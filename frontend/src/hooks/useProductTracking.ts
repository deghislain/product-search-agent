/**
 * React Hook for Product Interaction Tracking
 * 
 * Provides easy-to-use hooks for tracking user interactions with products.
 */

import { useEffect, useRef, useCallback } from 'react';
import {
  trackProductView,
  trackProductClick,
  trackProductPurchase,
  trackProductIgnore,
  createViewTracker
} from '../services/userInteractionService';

/**
 * Hook to automatically track product views with duration
 * 
 * @param productId - ID of the product being viewed
 * @param enabled - Whether tracking is enabled (default: true)
 * 
 * @example
 * ```typescript
 * function ProductDetail({ product }) {
 *   useProductViewTracking(product.id);
 *   
 *   return <div>...</div>;
 * }
 * ```
 */
export function useProductViewTracking(
  productId: string | null | undefined,
  enabled: boolean = true
) {
  const viewTracker = useRef(createViewTracker());
  
  useEffect(() => {
    if (!enabled || !productId) return;
    
    // Start tracking when component mounts
    viewTracker.current.start();
    
    // Stop tracking and send duration when component unmounts
    return () => {
      viewTracker.current.stop(productId);
    };
  }, [productId, enabled]);
}

/**
 * Hook that provides tracking functions for product interactions
 * 
 * @returns Object with tracking functions
 * 
 * @example
 * ```typescript
 * function ProductCard({ product }) {
 *   const { trackClick, trackPurchase, trackIgnore } = useProductInteractions();
 *   
 *   return (
 *     <div>
 *       <button onClick={() => trackClick(product.id)}>
 *         View Details
 *       </button>
 *       <button onClick={() => trackPurchase(product.id)}>
 *         Buy Now
 *       </button>
 *       <button onClick={() => trackIgnore(product.id)}>
 *         Not Interested
 *       </button>
 *     </div>
 *   );
 * }
 * ```
 */
export function useProductInteractions() {
  const trackClick = useCallback(async (productId: string) => {
    await trackProductClick(productId);
  }, []);
  
  const trackPurchase = useCallback(async (
    productId: string,
    metadata?: Record<string, any>
  ) => {
    await trackProductPurchase(productId, metadata);
  }, []);
  
  const trackIgnore = useCallback(async (productId: string) => {
    await trackProductIgnore(productId);
  }, []);
  
  const trackView = useCallback(async (
    productId: string,
    durationSeconds?: number
  ) => {
    await trackProductView(productId, durationSeconds);
  }, []);
  
  return {
    trackClick,
    trackPurchase,
    trackIgnore,
    trackView
  };
}

/**
 * Hook for tracking product link clicks
 * Automatically tracks when user clicks to view product on external site
 * 
 * @param productId - ID of the product
 * @param productUrl - URL of the product
 * 
 * @returns Click handler function
 * 
 * @example
 * ```typescript
 * function ProductCard({ product }) {
 *   const handleClick = useProductLinkClick(product.id, product.url);
 *   
 *   return (
 *     <a href={product.url} onClick={handleClick} target="_blank">
 *       View Product
 *     </a>
 *   );
 * }
 * ```
 */
export function useProductLinkClick(
  productId: string | null | undefined,
  _productUrl: string
) {
  return useCallback(async (_event: React.MouseEvent) => {
    if (!productId) return;
    
    // Track the click
    await trackProductClick(productId);
    
    // Let the default link behavior continue
    // (opening in new tab/window)
  }, [productId]);
}

/**
 * Hook for tracking product card visibility
 * Tracks when a product card enters/exits the viewport
 * 
 * @param productId - ID of the product
 * @param threshold - Visibility threshold (0-1, default: 0.5)
 * 
 * @returns Ref to attach to the product card element
 * 
 * @example
 * ```typescript
 * function ProductCard({ product }) {
 *   const cardRef = useProductVisibility(product.id);
 *   
 *   return (
 *     <div ref={cardRef}>
 *       {product.title}
 *     </div>
 *   );
 * }
 * ```
 */
export function useProductVisibility(
  productId: string | null | undefined,
  threshold: number = 0.5
) {
  const elementRef = useRef<HTMLDivElement>(null);
  const hasTrackedView = useRef(false);
  
  useEffect(() => {
    if (!productId || !elementRef.current) return;
    
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasTrackedView.current) {
            // Product is visible, track view
            trackProductView(productId, 0);
            hasTrackedView.current = true;
          }
        });
      },
      { threshold }
    );
    
    observer.observe(elementRef.current);
    
    return () => {
      observer.disconnect();
      hasTrackedView.current = false;
    };
  }, [productId, threshold]);
  
  return elementRef;
}

/**
 * Hook for tracking time spent on a product detail page
 * More accurate than useProductViewTracking for detail pages
 * 
 * @param productId - ID of the product
 * 
 * @example
 * ```typescript
 * function ProductDetailPage({ product }) {
 *   useProductDetailTracking(product.id);
 *   
 *   return <div>...</div>;
 * }
 * ```
 */
export function useProductDetailTracking(productId: string | null | undefined) {
  const startTimeRef = useRef<number>(Date.now());
  const intervalRef = useRef<number | null>(null);
  
  useEffect(() => {
    if (!productId) return;
    
    startTimeRef.current = Date.now();
    
    // Track view every 30 seconds while user is on page
    intervalRef.current = setInterval(() => {
      const duration = Math.floor((Date.now() - startTimeRef.current) / 1000);
      trackProductView(productId, duration);
      startTimeRef.current = Date.now(); // Reset for next interval
    }, 30000); // 30 seconds
    
    // Track final duration on unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      
      const finalDuration = Math.floor((Date.now() - startTimeRef.current) / 1000);
      if (finalDuration > 0) {
        trackProductView(productId, finalDuration);
      }
    };
  }, [productId]);
}

// Made with Bob
