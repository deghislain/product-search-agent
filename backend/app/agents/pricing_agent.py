from typing import Dict, List, Optional, Any
from .base_agent import BaseAgent
from ..models.product import Product
from ..models.search_request import SearchRequest
from ..database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import logging
import json
import statistics

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



class PricingAgent(BaseAgent):
    """
    PricingAgent specializes in price analysis and deal identification.
    
    Responsibilities:
    - Analyze product prices against market rates
    - Identify good deals and exceptional bargains
    - Predict price drop probability
    - Recommend buy now vs wait strategies
    - Track historical price trends
    
    Attributes:
        EXCELLENT_DEAL_THRESHOLD: Price % below market for excellent deals
        GOOD_DEAL_THRESHOLD: Price % below market for good deals
        PRICE_HISTORY_DAYS: Days of historical data to analyze
    """
    
    # Class constants
    EXCELLENT_DEAL_THRESHOLD = 0.20  # 20% below market
    GOOD_DEAL_THRESHOLD = 0.10  # 10% below market
    PRICE_HISTORY_DAYS = 30
    
    def _get_product_attr(self, product, attr: str, default=None):
        """Helper to safely get product attribute from both dict and Product object."""
        if isinstance(product, dict):
            return product.get(attr, default)
        return getattr(product, attr, default)
    def _extract_json_from_response(self, content: str) -> Dict:
        """
        Extract JSON from LLM response, handling markdown code blocks and extra text.
        
        Args:
            content: Raw LLM response
            
        Returns:
            Parsed JSON dictionary
        """
        import re
        
        if not content or not content.strip():
            logger.error("Empty response from LLM")
            raise ValueError("Empty response from LLM")
        
        # Strip whitespace
        content = content.strip()
        
        try:
            # First, try direct JSON parsing
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.debug(f"Direct JSON parse failed: {e}")
        
        # Try to extract JSON from markdown code blocks
        # Look for ```json ... ``` or ``` ... ```
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError as e:
                logger.debug(f"Markdown JSON parse failed: {e}")
        
        # Look for JSON object anywhere in the text (greedy match)
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.debug(f"Extracted JSON parse failed: {e}, JSON: {json_str[:200]}")
        
        # Try to find JSON between any text
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                # Found potential JSON start, try to parse from here
                remaining = '\n'.join(lines[i:])
                json_match = re.search(r'\{.*\}', remaining, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        continue
        
        # If all else fails, log the full content and raise
        logger.error(f"Could not extract JSON from LLM response. Full content ({len(content)} chars): {content}")
        raise ValueError(f"Could not parse JSON from response: {content[:200]}")

    
    async def perceive(self, environment: Dict) -> Dict:
        """
        Extract price-relevant information from environment.
        
        Args:
            environment: Dictionary containing:
                - product: Product to analyze
                - similar_products: List of comparable products
                - search_request: Original search request
                
        Returns:
            Dictionary with price observations
        """
        product = environment.get('product')
        similar_products = environment.get('similar_products', [])
        
        if not product:
            logger.warning("No product provided to PricingAgent.perceive()")
            return {}
        
        # Handle both dict and Product object
        product_price = getattr(product, 'price', product.get('price') if isinstance(product, dict) else None)
        platform = getattr(product, 'platform', product.get('platform') if isinstance(product, dict) else 'unknown')
        
        observations = {
            'product': product,
            'product_price': product_price,
            'platform': platform,
            'similar_products': similar_products,
            'historical_prices': self._get_historical_prices(product),
            'market_statistics': self._calculate_market_statistics(similar_products),
            'price_trend': None
        }
        
        # Calculate price trend if we have historical data
        if observations['historical_prices']:
            observations['price_trend'] = self._get_price_trend(
                observations['historical_prices']
            )
        
        return observations
    
    async def decide(self, observations: Dict) -> Dict:
        """
        Decide if price is good and recommend action.
        
        Args:
            observations: Price observations from perceive()
            
        Returns:
            Dictionary with pricing decision
        """
        product = observations.get('product')
        
        if not product:
            logger.error("No product in observations")
            return self._get_default_decision()
        
        # Perform comprehensive price analysis
        analysis = await self.analyze_price(
            product=product,
            similar_products=observations.get('similar_products', []),
            historical_prices=observations.get('historical_prices', []),
            market_stats=observations.get('market_statistics', {})
        )
        
        return analysis
    
    async def act(self, decision: Dict) -> Dict[str, Any]:
        """
        Execute pricing decision (log to memory, prepare alerts).
        
        Args:
            decision: Pricing decision from decide()
            
        Returns:
            Dictionary with action results
        """
        logger.info(f"PricingAgent acting on decision: {decision.get('recommendation')}")
        
        results = {
            'action_taken': None,
            'alert_sent': False,
            'logged': False
        }
        
        try:
            # Log decision to memory
            self.add_to_memory({
                'action': 'price_analysis',
                'timestamp': datetime.now().isoformat(),
                'is_good_deal': decision.get('is_good_deal'),
                'price_rating': decision.get('price_rating'),
                'recommendation': decision.get('recommendation'),
                'confidence': decision.get('confidence')
            })
            results['logged'] = True
            
            # Determine action based on recommendation
            recommendation = decision.get('recommendation', 'wait')
            
            if recommendation == 'buy_now' and decision.get('is_good_deal'):
                results['action_taken'] = 'alert_user'
                results['alert_sent'] = True
                logger.info("Excellent deal detected - alerting user")
            elif recommendation == 'negotiate':
                results['action_taken'] = 'suggest_negotiation'
                logger.info("Price negotiable - suggesting user negotiate")
            else:
                results['action_taken'] = 'monitor'
                logger.info("Monitoring price for changes")
            
        except Exception as e:
            logger.error(f"Error in PricingAgent.act(): {e}")
            results['error'] = str(e)
        
        return results
    
    async def analyze_price(
        self,
        product: Product,
        similar_products: Optional[List[Product]] = None,
        historical_prices: Optional[List[Dict]] = None,
        market_stats: Optional[Dict] = None
    ) -> Dict:
        """
        Comprehensive price analysis using LLM and statistical methods.
        
        Args:
            product: Product to analyze
            similar_products: List of comparable products
            historical_prices: Historical price data
            market_stats: Market statistics
            
        Returns:
            Dictionary with analysis results:
                - is_good_deal: bool
                - price_rating: str ('excellent', 'good', 'fair', 'poor', 'overpriced')
                - market_comparison: float (% above/below market)
                - recommendation: str ('buy_now', 'wait', 'negotiate')
                - confidence: float (0-1)
                - reasoning: str
        """
        similar_products = similar_products or []
        historical_prices = historical_prices or []
        market_stats = market_stats or {}
        
        # Handle both dict and Product object
        product_price = float(getattr(product, 'price', product.get('price', 0) if isinstance(product, dict) else 0))
        
        # Calculate basic metrics
        market_avg = market_stats.get('average', product_price)
        market_median = market_stats.get('median', product_price)
        
        # Calculate price comparison
        if market_avg > 0:
            price_vs_market = ((product_price - market_avg) / market_avg) * 100
        else:
            price_vs_market = 0
        
        # Determine initial rating based on statistics
        if price_vs_market <= -self.EXCELLENT_DEAL_THRESHOLD * 100:
            initial_rating = 'excellent'
            is_good_deal = True
        elif price_vs_market <= -self.GOOD_DEAL_THRESHOLD * 100:
            initial_rating = 'good'
            is_good_deal = True
        elif price_vs_market <= 10:
            initial_rating = 'fair'
            is_good_deal = False
        elif price_vs_market <= 25:
            initial_rating = 'poor'
            is_good_deal = False
        else:
            initial_rating = 'overpriced'
            is_good_deal = False
        
        # Build LLM prompt for deeper analysis
        prompt = self._build_price_analysis_prompt(
            product=product,
            market_avg=market_avg,
            market_median=market_median,
            price_vs_market=price_vs_market,
            similar_products=similar_products[:5],  # Top 5 for context
            historical_prices=historical_prices,
            initial_rating=initial_rating
        )
        
        try:
            # Get LLM analysis using the generate method
            content = await self.llm.generate(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for more consistent JSON
                max_tokens=500
            )
            
            # Extract JSON from response (handle markdown code blocks)
            llm_analysis = self._extract_json_from_response(content)
            
            # Validate and merge with statistical analysis
            analysis = {
                'is_good_deal': llm_analysis.get('is_good_deal', is_good_deal),
                'price_rating': llm_analysis.get('price_rating', initial_rating),
                'market_comparison': price_vs_market,
                'recommendation': llm_analysis.get('recommendation', 'wait'),
                'confidence': llm_analysis.get('confidence', 0.5),
                'reasoning': llm_analysis.get('reasoning', 'Statistical analysis only'),
                'market_average': market_avg,
                'market_median': market_median,
                'price_trend': self._get_price_trend(historical_prices) if historical_prices else 'unknown'
            }
            
            # Validate the analysis
            if not self._validate_analysis(analysis):
                logger.warning("Invalid LLM analysis, using statistical fallback")
                return self._get_statistical_analysis(
                    product, market_avg, price_vs_market, initial_rating, is_good_deal
                )
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._get_statistical_analysis(
                product, market_avg, price_vs_market, initial_rating, is_good_deal
            )
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return self._get_statistical_analysis(
                product, market_avg, price_vs_market, initial_rating, is_good_deal
            )
    
    async def predict_price_drop(self, product: Product, historical_prices: Optional[List[Dict]] = None) -> Dict:
        """
        Predict likelihood of price dropping.
        
        Args:
            product: Product to analyze
            historical_prices: Historical price data
            
        Returns:
            Dictionary with prediction:
                - drop_probability: float (0-1)
                - expected_drop_amount: float (dollars)
                - time_to_drop: str ('days', 'weeks', 'months')
                - recommendation: str ('wait' or 'buy_now')
                - reasoning: str
        """
        historical_prices = historical_prices or []
        
        # Analyze price trend
        trend = self._get_price_trend(historical_prices) if historical_prices else 'stable'
        
        # Platform-specific patterns
        platform = self._get_product_attr(product, 'platform', 'unknown')
        platform_factor = self._get_platform_drop_probability(str(platform))
        
        # Get product details safely
        title = self._get_product_attr(product, 'title', 'Unknown Product')
        price = self._get_product_attr(product, 'price', 0)
        
        # Build prediction prompt
        prompt = f"""
Predict if this product's price will drop:

Product: {title}
Current Price: ${price}
Platform: {platform}
Price Trend: {trend}

Historical Prices: {json.dumps(historical_prices[:10], indent=2) if historical_prices else "No data"}

Platform Patterns:
- Craigslist: Sellers often reduce prices after 1-2 weeks
- eBay: Auction prices fluctuate, Buy-It-Now may drop near end
- Facebook: Prices drop if item doesn't sell quickly

Predict:
1. Probability price will drop (0-1)
2. Expected drop amount in dollars
3. Timeframe (days/weeks/months)
4. Should buyer wait or buy now?

Respond in JSON format:
{{
    "drop_probability": 0.0-1.0,
    "expected_drop_amount": 0.0,
    "time_to_drop": "days" | "weeks" | "months",
    "recommendation": "wait" | "buy_now",
    "reasoning": "explanation"
}}
"""
        
        try:
            response = await self.llm.chat.completions.create(
                model=self.llm.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.choices[0].message.content
            prediction = json.loads(content)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Price drop prediction failed: {e}")
            # Return conservative default
            return {
                'drop_probability': platform_factor,
                'expected_drop_amount': 0.0,
                'time_to_drop': 'weeks',
                'recommendation': 'buy_now' if platform_factor < 0.3 else 'wait',
                'reasoning': 'Statistical estimate based on platform patterns'
            }
    
    def _get_historical_prices(self, product, db: Optional[Session] = None) -> List[Dict]:
        """
        Get historical prices for similar products.
        
        Args:
            product: Product to find similar items for (Product object or dict)
            db: Optional database session
            
        Returns:
            List of historical price records
        """
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True
        
        try:
            # Query products with similar titles from the last N days
            cutoff_date = datetime.now() - timedelta(days=self.PRICE_HISTORY_DAYS)
            
            # Simple similarity: same platform and similar title keywords
            product_title = self._get_product_attr(product, 'title', 'unknown')
            product_platform = self._get_product_attr(product, 'platform', 'unknown')
            product_id = self._get_product_attr(product, 'id', None)
            
            title_keywords = set(str(product_title).lower().split()[:3])  # First 3 words
            
            similar_products = db.query(Product).filter(
                Product.platform == product_platform,
                Product.created_at >= cutoff_date,
                Product.id != product_id
            ).limit(50).all()
            
            # Filter by title similarity and extract prices
            historical_prices = []
            for p in similar_products:
                p_keywords = set(p.title.lower().split()[:3])
                if len(title_keywords & p_keywords) >= 2:  # At least 2 matching keywords
                    historical_prices.append({
                        'price': p.price,
                        'date': p.created_at.isoformat(),
                        'title': p.title
                    })
            
            # Sort by date
            historical_prices.sort(key=lambda x: x['date'], reverse=True)
            
            return historical_prices
            
        except Exception as e:
            logger.error(f"Error fetching historical prices: {e}")
            return []
        finally:
            if should_close_db:
                db.close()
    
    def _calculate_market_statistics(self, similar_products: List[Product]) -> Dict:
        """
        Calculate market statistics from similar products.
        
        Args:
            similar_products: List of comparable products
            
        Returns:
            Dictionary with market statistics
        """
        if not similar_products:
            return {
                'average': 0,
                'median': 0,
                'min': 0,
                'max': 0,
                'std_dev': 0,
                'count': 0
            }
        
        # Extract prices safely, handling SQLAlchemy Column objects
        prices = []
        for p in similar_products:
            try:
                price_val = getattr(p, 'price', 0)
                if price_val and price_val > 0:
                    prices.append(float(price_val))
            except (TypeError, ValueError):
                continue
        
        if not prices:
            return {
                'average': 0,
                'median': 0,
                'min': 0,
                'max': 0,
                'std_dev': 0,
                'count': 0
            }
        
        return {
            'average': statistics.mean(prices),
            'median': statistics.median(prices),
            'min': min(prices),
            'max': max(prices),
            'std_dev': statistics.stdev(prices) if len(prices) > 1 else 0,
            'count': len(prices)
        }
    
    def _get_price_trend(self, historical_prices: List[Dict]) -> str:
        """
        Analyze price trend from historical data.
        
        Args:
            historical_prices: List of historical price records
            
        Returns:
            Trend description: 'rising', 'falling', 'stable', 'volatile'
        """
        if len(historical_prices) < 3:
            return 'insufficient_data'
        
        prices = [p['price'] for p in historical_prices[:10]]  # Last 10 prices
        
        # Calculate trend
        first_half_avg = statistics.mean(prices[:len(prices)//2])
        second_half_avg = statistics.mean(prices[len(prices)//2:])
        
        change_pct = ((second_half_avg - first_half_avg) / first_half_avg) * 100 if first_half_avg > 0 else 0
        
        # Calculate volatility
        std_dev = statistics.stdev(prices) if len(prices) > 1 else 0
        avg_price = statistics.mean(prices)
        volatility = (std_dev / avg_price) * 100 if avg_price > 0 else 0
        
        if volatility > 20:
            return 'volatile'
        elif change_pct > 5:
            return 'rising'
        elif change_pct < -5:
            return 'falling'
        else:
            return 'stable'
    
    def _get_platform_drop_probability(self, platform: str) -> float:
        """
        Get baseline price drop probability for platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Probability (0-1)
        """
        platform_probabilities = {
            'craigslist': 0.6,  # High - sellers often negotiate
            'facebook': 0.5,    # Medium - social pressure to sell
            'ebay': 0.3         # Low - auctions are final, BIN less flexible
        }
        
        return platform_probabilities.get(platform.lower(), 0.4)
    
    def _build_price_analysis_prompt(
        self,
        product: Product,
        market_avg: float,
        market_median: float,
        price_vs_market: float,
        similar_products: List[Product],
        historical_prices: List[Dict],
        initial_rating: str
    ) -> str:
        """Build comprehensive prompt for LLM price analysis."""
        
        # Get product details safely
        title = self._get_product_attr(product, 'title', 'Unknown Product')
        price = self._get_product_attr(product, 'price', 0)
        platform = self._get_product_attr(product, 'platform', 'unknown')
        description = self._get_product_attr(product, 'description', 'N/A')
        if isinstance(description, str) and len(description) > 200:
            description = description[:200]
        
        # Limit similar products to save tokens
        similar_sample = similar_products[:2] if similar_products else []
        similar_str = ', '.join([f"${getattr(p, 'price', 0)}" for p in similar_sample]) if similar_sample else "None"
        
        # Safely truncate title
        title_short = str(title)[:50] if title else "Unknown"
        
        return f"""
Analyze this deal:
Product: {title_short}
Price: ${price} | Market Avg: ${market_avg:.0f} | Diff: {price_vs_market:+.0f}%
Platform: {platform}

Similar prices: {similar_str}
Rating: {initial_rating}

Respond ONLY with JSON:
{{
    "is_good_deal": true/false,
    "price_rating": "excellent" | "good" | "fair" | "poor" | "overpriced",
    "recommendation": "buy_now" | "wait" | "negotiate",
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation of your analysis"
}}
"""
    
    def _validate_analysis(self, analysis: Dict) -> bool:
        """Validate price analysis structure."""
        required_fields = ['is_good_deal', 'price_rating', 'recommendation', 'confidence']
        
        if not all(field in analysis for field in required_fields):
            return False
        
        valid_ratings = ['excellent', 'good', 'fair', 'poor', 'overpriced']
        if analysis['price_rating'] not in valid_ratings:
            return False
        
        valid_recommendations = ['buy_now', 'wait', 'negotiate']
        if analysis['recommendation'] not in valid_recommendations:
            return False
        
        if not (0 <= analysis['confidence'] <= 1):
            return False
        
        return True
    
    def _get_statistical_analysis(
        self,
        product: Product,
        market_avg: float,
        price_vs_market: float,
        initial_rating: str,
        is_good_deal: bool
    ) -> Dict:
        """Fallback statistical analysis when LLM fails."""
        
        if price_vs_market < -15:
            recommendation = 'buy_now'
        elif price_vs_market < 0:
            recommendation = 'negotiate'
        else:
            recommendation = 'wait'
        
        return {
            'is_good_deal': is_good_deal,
            'price_rating': initial_rating,
            'market_comparison': price_vs_market,
            'recommendation': recommendation,
            'confidence': 0.6,
            'reasoning': f'Statistical analysis: Price is {abs(price_vs_market):.1f}% {"below" if price_vs_market < 0 else "above"} market average of ${market_avg:.2f}',
            'market_average': market_avg,
            'market_median': market_avg,
            'price_trend': 'unknown'
        }
    
    def _get_default_decision(self) -> Dict:
        """Default decision when analysis fails."""
        return {
            'is_good_deal': False,
            'price_rating': 'unknown',
            'market_comparison': 0,
            'recommendation': 'wait',
            'confidence': 0.0,
            'reasoning': 'Insufficient data for analysis',
            'market_average': 0,
            'market_median': 0,
            'price_trend': 'unknown'
        }

# Made with Bob
