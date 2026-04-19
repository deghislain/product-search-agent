import { useState, useEffect } from 'react';
import type { Product } from '../services/searchRequestService';

interface MatchNotificationProps {
  product: Product;
  onClose: () => void;
  autoClose?: boolean;
  duration?: number;
}

export default function MatchNotification({ 
  product, 
  onClose, 
  autoClose = true,
  duration = 5000 
}: MatchNotificationProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Slide in animation
    setIsVisible(true);

    // Auto close after duration
    if (autoClose) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [autoClose, duration]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(onClose, 300); // Wait for animation
  };

  return (
    <div className={`transition-all duration-300 ${
      isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
    }`}>
      <div className="bg-white rounded-lg shadow-2xl max-w-sm w-full overflow-hidden border-l-4 border-green-500">
        {/* Header */}
        <div className="bg-green-50 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center">
            <span className="text-2xl mr-2">🎉</span>
            <h4 className="font-bold text-green-800">New Match Found!</h4>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-4">
          <div className="flex">
            {/* Thumbnail */}
            {product.image_url && (
              <img
                src={product.image_url}
                alt={product.title}
                className="w-20 h-20 object-cover rounded mr-3"
              />
            )}

            {/* Details */}
            <div className="flex-1">
              <h5 className="font-semibold text-gray-800 line-clamp-2 mb-1">
                {product.title}
              </h5>
              <p className="text-lg font-bold text-green-600 mb-1">
                ${product.price.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 capitalize">
                {product.platform}
              </p>
            </div>
          </div>

          {/* Match Score */}
          {product.match_score && (
            <div className="mt-3 bg-green-100 rounded p-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-green-800 font-medium">Match Score</span>
                <span className="text-green-600 font-bold">
                  {Math.round(product.match_score * 100)}%
                </span>
              </div>
            </div>
          )}

          {/* Action Button */}
          <a
            href={product.url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-3 block w-full bg-green-500 hover:bg-green-600 text-white text-center py-2 rounded font-medium transition-colors"
          >
            View Now
          </a>
        </div>
      </div>
    </div>
  );
}