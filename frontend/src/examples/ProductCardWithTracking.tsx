/**
 * Example: Product Card with User Interaction Tracking
 * 
 * This file demonstrates how to integrate user tracking into your ProductCard component.
 * Copy the relevant parts into your actual ProductCard.tsx component.
 */

import { useProductViewTracking, useProductInteractions, useProductLinkClick } from '../hooks/useProductTracking';

interface Product {
  id: string;
  title: string;
  price: number;
  url: string;
  image_url?: string;
  platform: string;
  match_score?: number;
}

interface ProductCardProps {
  product: Product;
}

/**
 * Example 1: Basic Product Card with View Tracking
 * 
 * This tracks how long users view each product card
 */
export function ProductCardWithViewTracking({ product }: ProductCardProps) {
  // Automatically track view duration
  useProductViewTracking(product.id);
  
  return (
    <div className="product-card">
      <img src={product.image_url} alt={product.title} />
      <h3>{product.title}</h3>
      <p>${product.price}</p>
      <a href={product.url} target="_blank" rel="noopener noreferrer">
        View Product
      </a>
    </div>
  );
}

/**
 * Example 2: Product Card with Click Tracking
 * 
 * This tracks when users click to view the product
 */
export function ProductCardWithClickTracking({ product }: ProductCardProps) {
  const handleClick = useProductLinkClick(product.id, product.url);
  
  return (
    <div className="product-card">
      <img src={product.image_url} alt={product.title} />
      <h3>{product.title}</h3>
      <p>${product.price}</p>
      <a 
        href={product.url} 
        target="_blank" 
        rel="noopener noreferrer"
        onClick={handleClick}  // Track the click
      >
        View Product
      </a>
    </div>
  );
}

/**
 * Example 3: Full Product Card with All Tracking
 * 
 * This tracks views, clicks, and provides ignore/purchase buttons
 */
export function ProductCardWithFullTracking({ product }: ProductCardProps) {
  // Track view duration
  useProductViewTracking(product.id);
  
  // Get tracking functions
  const { trackClick, trackPurchase, trackIgnore } = useProductInteractions();
  
  const handleViewProduct = async () => {
    await trackClick(product.id);
    window.open(product.url, '_blank');
  };
  
  const handlePurchase = async () => {
    await trackPurchase(product.id, { price: product.price });
    // Redirect to product or show purchase confirmation
    window.open(product.url, '_blank');
  };
  
  const handleIgnore = async () => {
    await trackIgnore(product.id);
    // Maybe hide the card or show feedback
  };
  
  return (
    <div className="product-card">
      {product.image_url && (
        <img src={product.image_url} alt={product.title} />
      )}
      
      <div className="product-info">
        <h3>{product.title}</h3>
        <p className="price">${product.price}</p>
        <p className="platform">{product.platform}</p>
        
        {product.match_score && (
          <p className="match-score">
            Match: {product.match_score.toFixed(1)}%
          </p>
        )}
      </div>
      
      <div className="product-actions">
        <button onClick={handleViewProduct} className="btn-primary">
          View Details
        </button>
        <button onClick={handlePurchase} className="btn-success">
          Buy Now
        </button>
        <button onClick={handleIgnore} className="btn-secondary">
          Not Interested
        </button>
      </div>
    </div>
  );
}

/**
 * Example 4: Product Grid with Tracking
 * 
 * Shows how to use tracking in a list of products
 */
export function ProductGridWithTracking({ products }: { products: Product[] }) {
  return (
    <div className="product-grid">
      {products.map(product => (
        <ProductCardWithFullTracking 
          key={product.id} 
          product={product} 
        />
      ))}
    </div>
  );
}

/**
 * Example 5: Integration with Existing ProductCard
 * 
 * If you already have a ProductCard component, add these lines:
 */
export function IntegrateIntoExistingCard({ product }: ProductCardProps) {
  // ADD THIS LINE to track view duration
  useProductViewTracking(product.id);
  
  // ADD THIS LINE to get tracking functions
  const { trackClick, trackPurchase, trackIgnore } = useProductInteractions();
  
  // Your existing component code...
  // Just add onClick handlers to your buttons:
  
  return (
    <div className="product-card">
      {/* Your existing JSX */}
      <button onClick={() => trackClick(product.id)}>
        View
      </button>
      <button onClick={() => trackPurchase(product.id)}>
        Buy
      </button>
      <button onClick={() => trackIgnore(product.id)}>
        Ignore
      </button>
    </div>
  );
}

/**
 * Example 6: Initialize User ID in App Component
 * 
 * Add this to your main App.tsx file:
 */
/*
import { useEffect } from 'react';
import { initializeUserIdentification } from './utils/userIdentification';

function App() {
  useEffect(() => {
    // Initialize user identification on app load
    initializeUserIdentification();
  }, []);
  
  return (
    // Your app content
  );
}
*/

/**
 * Example 7: Display User Stats (Optional)
 * 
 * Show user their interaction statistics
 */
/*
import { useState, useEffect } from 'react';
import { getUserStats } from './services/userInteractionService';

function UserStatsPanel() {
  const [stats, setStats] = useState(null);
  
  useEffect(() => {
    getUserStats().then(setStats);
  }, []);
  
  if (!stats) return null;
  
  return (
    <div className="user-stats">
      <h3>Your Activity</h3>
      <p>Products Viewed: {stats.total_views}</p>
      <p>Products Clicked: {stats.total_clicks}</p>
      <p>Click Rate: {(stats.click_through_rate * 100).toFixed(1)}%</p>
    </div>
  );
}
*/

// Made with Bob
