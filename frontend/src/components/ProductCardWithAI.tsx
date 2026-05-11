import type { Product } from '../services/searchRequestService';
import { useProductViewTracking, useProductInteractions } from '../hooks/useProductTracking';

interface ProductCardWithAIProps {
  product: Product;
  onViewDetails?: (product: Product) => void;
}

export default function ProductCardWithAI({ product, onViewDetails }: ProductCardWithAIProps) {
  // Track view duration automatically
  useProductViewTracking(product.id);
  
  // Get tracking functions
  const { trackClick } = useProductInteractions();
  
  const handleClick = () => {
    if (onViewDetails) {
      onViewDetails(product);
    }
  };
  
  const handleViewListing = async (_e: React.MouseEvent<HTMLAnchorElement>) => {
    // Track the click before opening the link
    await trackClick(product.id);
    // Let the default link behavior continue
  };

  // Get AI analysis data
  const aiAnalysis = product.metadata;
  const hasAIAnalysis = aiAnalysis && (aiAnalysis.overall_score || aiAnalysis.recommendation);

  // Get recommendation badge color
  const getRecommendationColor = (recommendation?: string) => {
    switch (recommendation) {
      case 'buy_now':
        return 'bg-green-600';
      case 'good_deal':
        return 'bg-green-500';
      case 'fair_price':
        return 'bg-blue-500';
      case 'negotiate':
        return 'bg-yellow-500';
      case 'wait':
        return 'bg-orange-500';
      case 'avoid':
        return 'bg-red-600';
      default:
        return 'bg-gray-500';
    }
  };

  // Get recommendation text
  const getRecommendationText = (recommendation?: string) => {
    switch (recommendation) {
      case 'buy_now':
        return '🔥 Buy Now!';
      case 'good_deal':
        return '✨ Good Deal';
      case 'fair_price':
        return '👍 Fair Price';
      case 'negotiate':
        return '💬 Negotiate';
      case 'wait':
        return '⏳ Wait';
      case 'avoid':
        return '⚠️ Avoid';
      default:
        return '';
    }
  };

  // Get quality badge color
  const getQualityColor = (score?: number) => {
    if (!score) return 'bg-gray-500';
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-all duration-300 animate-fade-in hover:scale-105">
      {/* Product Image */}
      <div className="relative h-48 bg-gray-200">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.title}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.currentTarget.src = 'https://via.placeholder.com/400x300?text=No+Image';
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}
        
        {/* AI Recommendation Badge */}
        {hasAIAnalysis && aiAnalysis.recommendation && (
          <div className={`absolute top-2 right-2 ${getRecommendationColor(aiAnalysis.recommendation)} text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg`}>
            {getRecommendationText(aiAnalysis.recommendation)}
          </div>
        )}
        
        {/* Match Score Badge */}
        {product.match_score && (
          <div className="absolute top-2 left-2 bg-purple-500 text-white px-2 py-1 rounded-full text-xs font-bold">
            {Math.round(product.match_score)}% Match
          </div>
        )}
        
        {/* Platform Badge */}
        <div className="absolute bottom-2 left-2 bg-blue-500 text-white px-2 py-1 rounded text-xs font-semibold capitalize">
          {product.platform}
        </div>
      </div>

      {/* Product Details */}
      <div className="p-4">
        {/* Title */}
        <h3 className="text-lg font-semibold text-gray-800 mb-2 line-clamp-2">
          {product.title}
        </h3>

        {/* Price */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-2xl font-bold text-green-600">
            ${product.price.toLocaleString()}
          </span>
          {product.location && (
            <span className="text-sm text-gray-500">
              📍 {product.location}
            </span>
          )}
        </div>

        {/* AI Analysis Section */}
        {hasAIAnalysis && (
          <div className="mb-4 p-3 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
            <div className="flex items-center mb-2">
              <span className="text-purple-600 font-semibold text-sm">🤖 AI Analysis</span>
            </div>
            
            {/* Score Bars */}
            <div className="space-y-2">
              {aiAnalysis.overall_score !== undefined && (
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-600">Overall Score</span>
                    <span className="font-semibold text-purple-600">{Math.round(aiAnalysis.overall_score)}/100</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-purple-600 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${aiAnalysis.overall_score}%` }}
                    ></div>
                  </div>
                </div>
              )}
              
              {aiAnalysis.quality_score !== undefined && (
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-600">Quality</span>
                    <span className={`font-semibold ${aiAnalysis.quality_score >= 70 ? 'text-green-600' : aiAnalysis.quality_score >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {Math.round(aiAnalysis.quality_score)}/100
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-500 ${getQualityColor(aiAnalysis.quality_score)}`}
                      style={{ width: `${aiAnalysis.quality_score}%` }}
                    ></div>
                  </div>
                </div>
              )}
              
              {aiAnalysis.price_score !== undefined && (
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-600">Price Value</span>
                    <span className="font-semibold text-green-600">{Math.round(aiAnalysis.price_score)}/100</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${aiAnalysis.price_score}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>

            {/* AI Reasoning */}
            {aiAnalysis.reasoning && (
              <div className="mt-3 text-xs text-gray-700 italic border-l-2 border-purple-400 pl-2">
                "{aiAnalysis.reasoning}"
              </div>
            )}

            {/* Quality Warnings */}
            {aiAnalysis.quality_analysis?.red_flags && aiAnalysis.quality_analysis.red_flags.length > 0 && (
              <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs">
                <span className="font-semibold text-red-700">⚠️ Red Flags:</span>
                <ul className="mt-1 ml-4 list-disc text-red-600">
                  {aiAnalysis.quality_analysis.red_flags.slice(0, 2).map((flag, idx) => (
                    <li key={idx}>{flag}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Positive Signals */}
            {aiAnalysis.quality_analysis?.positive_signals && aiAnalysis.quality_analysis.positive_signals.length > 0 && (
              <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded text-xs">
                <span className="font-semibold text-green-700">✅ Positive Signs:</span>
                <ul className="mt-1 ml-4 list-disc text-green-600">
                  {aiAnalysis.quality_analysis.positive_signals.slice(0, 2).map((signal, idx) => (
                    <li key={idx}>{signal}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Price Analysis */}
            {aiAnalysis.price_analysis?.market_comparison && (
              <div className="mt-2 text-xs text-blue-700">
                💰 {aiAnalysis.price_analysis.market_comparison}
              </div>
            )}
          </div>
        )}

        {/* Description */}
        {product.description && (
          <p className="text-sm text-gray-600 mb-4 line-clamp-3">
            {product.description}
          </p>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-2">
          <a
            href={product.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={handleViewListing}
            className="flex-1 bg-blue-500 hover:bg-blue-700 text-white text-center py-2 px-4 rounded font-medium transition-colors"
          >
            View Listing
          </a>
          {onViewDetails && (
            <button
              onClick={handleClick}
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 px-4 rounded font-medium transition-colors"
            >
              Details
            </button>
          )}
        </div>

        {/* Timestamp */}
        <p className="text-xs text-gray-400 mt-3">
          Found: {new Date(product.created_at).toLocaleString()}
        </p>
      </div>
    </div>
  );
}

// Made with Bob
