from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from .base_agent import BaseAgent
from .pricing_agent import PricingAgent
from .quality_agent import QualityAgent
from .search_agent import SearchAgent
from ..models.search_request import SearchRequest
from ..models.product import Product
import logging
import json
import asyncio

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



class CoordinatorAgent(BaseAgent):
    """
    CoordinatorAgent orchestrates all specialized agents to find optimal products.
    
    Responsibilities:
    - Coordinate SearchAgent, PricingAgent, and QualityAgent
    - Make final decisions on which products to show users
    - Resolve conflicts between agent recommendations
    - Rank and filter products based on multiple criteria
    - Provide explanations for decisions
    - Handle agent failures gracefully
    
    Attributes:
        search_agent: Agent for finding products
        pricing_agent: Agent for price analysis
        quality_agent: Agent for quality assessment
        MIN_QUALITY_SCORE: Minimum quality score to show product
        MIN_OVERALL_SCORE: Minimum overall score to show product
    """
    
    # Class constants
    MIN_QUALITY_SCORE = 40.0  # Don't show products below this quality
    MIN_OVERALL_SCORE = 50.0  # Minimum combined score
    MAX_PRODUCTS_TO_RETURN = 50  # Limit results
    MAX_PRODUCTS_TO_ANALYZE = 10  # Limit AI analysis to top N products (token limit protection)
    BATCH_SIZE = 3  # Analyze products in batches (smaller batches = fewer tokens per batch)
    BATCH_DELAY = 5.0  # Seconds to wait between batches (token limit protection - Groq resets every 60s)
    
    def __init__(self, llm_client):
        """
        Initialize CoordinatorAgent with all specialized agents.
        
        Args:
            llm_client: LLM client for AI-powered decisions
        """
        super().__init__("Coordinator", llm_client)
        self.search_agent = SearchAgent("Search", llm_client)
        self.pricing_agent = PricingAgent("Pricing", llm_client)
        self.quality_agent = QualityAgent("Quality", llm_client)
        
        logger.info("CoordinatorAgent initialized with all specialized agents")
    
    async def perceive(self, environment: Dict) -> Dict:
        """
        Gather information from all specialized agents.
        
        Args:
            environment: Dictionary containing:
                - search_request: SearchRequest to process
                - past_results: Previous search results
                - user_preferences: User preference data
                
        Returns:
            Dictionary with observations from all agents
        """
        search_request = environment.get('search_request')
        past_results = environment.get('past_results', [])
        
        if not search_request:
            logger.warning("No search_request in environment")
            return {}
        
        # Get observations from SearchAgent
        search_observations = await self.search_agent.perceive({
            'search_request': search_request,
            'past_results': past_results,
            'user_interactions': environment.get('user_interactions', [])
        })
        
        observations = {
            'search_request': search_request,
            'past_results': past_results,
            'search_observations': search_observations,
            'agent_status': {
                'search_agent': 'ready',
                'pricing_agent': 'ready',
                'quality_agent': 'ready'
            }
        }
        
        return observations
    
    async def decide(self, observations: Dict) -> Dict:
        """
        Make coordination decisions based on all agent inputs.
        
        Args:
            observations: Observations from perceive()
            
        Returns:
            Dictionary with coordination strategy
        """
        search_request = observations.get('search_request')
        
        if not search_request:
            logger.error("No search_request in observations")
            return {'strategy': 'abort', 'reason': 'missing_search_request'}
        
        # Get search strategy from SearchAgent
        search_strategy = await self.search_agent.decide(
            observations.get('search_observations', {})
        )
        
        decision = {
            'strategy': 'execute_search',
            'search_strategy': search_strategy,
            'search_request': search_request,
            'filters': {
                'min_quality_score': self.MIN_QUALITY_SCORE,
                'min_overall_score': self.MIN_OVERALL_SCORE,
                'max_results': self.MAX_PRODUCTS_TO_RETURN
            },
            'ranking_criteria': {
                'quality_weight': 0.4,
                'price_weight': 0.3,
                'match_weight': 0.3
            }
        }
        
        return decision
    
    async def act(self, decision: Dict) -> Dict[str, Any]:
        """
        Execute coordination decision.
        
        Args:
            decision: Coordination decision from decide()
            
        Returns:
            Dictionary with execution results
        """
        if decision.get('strategy') == 'abort':
            logger.error(f"Aborting: {decision.get('reason')}")
            return {
                'success': False,
                'products': [],
                'reason': decision.get('reason')
            }
        
        search_request = decision.get('search_request')
        search_strategy = decision.get('search_strategy', {})
        
        if not search_request:
            logger.error("No search_request in decision")
            return {
                'success': False,
                'products': [],
                'reason': 'missing_search_request'
            }
        
        # Execute the full coordination workflow
        result = await self.coordinate_search(
            search_request=search_request,
            search_strategy=search_strategy,
            filters=decision.get('filters', {}),
            ranking_criteria=decision.get('ranking_criteria', {})
        )
        
        # Log to memory
        self.add_to_memory({
            'action': 'coordination',
            'timestamp': datetime.now().isoformat(),
            'products_found': len(result.get('products', [])),
            'products_shown': len(result.get('filtered_products', [])),
            'strategy': search_strategy
        })
        
        return result
    
    async def coordinate_search(
        self,
        search_request: SearchRequest,
        search_strategy: Optional[Dict] = None,
        filters: Optional[Dict] = None,
        ranking_criteria: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate all agents to find and evaluate products.
        
        Workflow:
        1. SearchAgent finds products
        2. PricingAgent evaluates each product's price
        3. QualityAgent assesses each product's quality
        4. Coordinator filters and ranks products
        5. Return best products with explanations
        
        Args:
            search_request: The search request to process
            search_strategy: Optional strategy from SearchAgent
            filters: Optional filtering criteria
            ranking_criteria: Optional ranking weights
            
        Returns:
            Dictionary with results:
                - products: All found products
                - filtered_products: Products passing filters
                - ranked_products: Top products ranked by score
                - analyses: Analysis data for each product
                - summary: Summary statistics
        """
        logger.info(f"Coordinating search for: {search_request.product_name}")
        
        filters = filters or {}
        ranking_criteria = ranking_criteria or {
            'quality_weight': 0.4,
            'price_weight': 0.3,
            'match_weight': 0.3
        }
        
        result = {
            'products': [],
            'filtered_products': [],
            'ranked_products': [],
            'analyses': {},
            'summary': {},
            'errors': []
        }
        
        try:
            # Step 1: Get search strategy if not provided
            if not search_strategy:
                search_strategy = await self.search_agent.decide_search_strategy(
                    search_request,
                    past_results=[]
                )
            
            # Step 2: Execute searches
            logger.info("Executing searches...")
            search_strategy['search_request'] = search_request
            products = await self._execute_searches(search_strategy)
            result['products'] = products
            
            logger.info(f"Found {len(products)} products")
            
            if not products:
                result['summary'] = {
                    'total_found': 0,
                    'passed_filters': 0,
                    'final_count': 0
                }
                return result
            
            # Step 3: Analyze products with specialized agents (with rate limiting)
            logger.info(f"Analyzing top {min(len(products), self.MAX_PRODUCTS_TO_ANALYZE)} products...")
            
            # Limit products to analyze (to avoid rate limits)
            products_to_analyze = products[:self.MAX_PRODUCTS_TO_ANALYZE]
            analyzed_products = []
            
            # Process in batches with delays
            for batch_start in range(0, len(products_to_analyze), self.BATCH_SIZE):
                batch_end = min(batch_start + self.BATCH_SIZE, len(products_to_analyze))
                batch = products_to_analyze[batch_start:batch_end]
                
                logger.info(f"Processing batch {batch_start//self.BATCH_SIZE + 1} ({len(batch)} products)...")
                
                # Analyze batch concurrently
                batch_tasks = []
                for product in batch:
                    batch_tasks.append(self._analyze_product(product, search_request))
                
                # Wait for batch to complete
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Process results
                for product, analysis_result in zip(batch, batch_results):
                    try:
                        if isinstance(analysis_result, Exception):
                            raise analysis_result
                        
                        # Type guard: analysis_result is Dict at this point
                        analysis: Dict = analysis_result  # type: ignore
                        
                        # Handle both dict and Product object
                        product_id = str(getattr(product, 'id', product.get('id', 'unknown')))
                        result['analyses'][product_id] = analysis
                        
                        # Add analysis scores to product for ranking
                        product_with_scores = {
                            'product': product,
                            'analysis': analysis,
                            'overall_score': analysis.get('overall_score', 0)
                        }
                        analyzed_products.append(product_with_scores)
                        
                    except Exception as e:
                        # Handle both dict and Product object for error logging
                        product_id = str(getattr(product, 'id', product.get('id', 'unknown') if isinstance(product, dict) else 'unknown'))
                        logger.error(f"Error analyzing product {product_id}: {e}", exc_info=True)
                        result['errors'].append(f"Product {product_id}: {str(e)}")
                
                # Wait between batches to avoid rate limits
                if batch_end < len(products_to_analyze):
                    logger.info(f"Waiting {self.BATCH_DELAY}s before next batch (rate limit protection)...")
                    await asyncio.sleep(self.BATCH_DELAY)
            
            # Add remaining products without AI analysis (for basic display)
            if len(products) > self.MAX_PRODUCTS_TO_ANALYZE:
                logger.info(f"Adding {len(products) - self.MAX_PRODUCTS_TO_ANALYZE} products without AI analysis")
                for product in products[self.MAX_PRODUCTS_TO_ANALYZE:]:
                    analyzed_products.append({
                        'product': product,
                        'analysis': {
                            'overall_score': 50,  # Neutral score
                            'quality_score': 50,
                            'price_score': 50,
                            'recommendation': 'review',
                            'reasoning': 'Not analyzed due to rate limits'
                        },
                        'overall_score': 50
                    })
            
            # Step 4: Filter products
            logger.info("Filtering products...")
            filtered_products = self._filter_products(
                analyzed_products,
                filters
            )
            result['filtered_products'] = [p['product'] for p in filtered_products]
            
            # Step 5: Rank products
            logger.info("Ranking products...")
            ranked_products = self._rank_products(
                filtered_products,
                ranking_criteria
            )
            result['ranked_products'] = [p['product'] for p in ranked_products]
            
            # Step 6: Generate summary
            result['summary'] = {
                'total_found': len(products),
                'passed_filters': len(filtered_products),
                'final_count': len(ranked_products),
                'avg_quality_score': sum(p['analysis'].get('quality_score', 0) for p in ranked_products) / len(ranked_products) if ranked_products else 0,
                'avg_price_rating': sum(1 if p['analysis'].get('is_good_deal') else 0 for p in ranked_products) / len(ranked_products) if ranked_products else 0,
                'platforms_searched': list(set(str(getattr(p['product'], 'platform', '')) for p in ranked_products))
            }
            
            logger.info(f"Coordination complete: {len(ranked_products)} products to show")
            
        except Exception as e:
            logger.error(f"Error in coordinate_search: {e}")
            result['errors'].append(f"Coordination error: {str(e)}")
        
        return result
    
    async def _execute_searches(self, strategy: Dict) -> List[Product]:
        """
        Execute searches based on strategy from SearchAgent.
        
        Args:
            strategy: Search strategy including platforms and query
            
        Returns:
            List of found products
        """
        try:
            # Use SearchAgent's act() method to execute searches
            search_result = await self.search_agent.act(strategy)
            
            products = search_result.get('products', [])
            errors = search_result.get('errors', [])
            
            if errors:
                logger.warning(f"Search errors: {errors}")
            
            return products
            
        except Exception as e:
            logger.error(f"Error executing searches: {e}")
            return []
    
    async def _analyze_product(
        self,
        product: Product,
        search_request: SearchRequest
    ) -> Dict:
        """
        Analyze a product with all specialized agents.
        
        Args:
            product: Product to analyze
            search_request: Original search request
            
        Returns:
            Dictionary with combined analysis from all agents
        """
        # Handle both dict and Product object
        product_id = str(getattr(product, 'id', product.get('id', 'unknown') if isinstance(product, dict) else 'unknown'))
        
        analysis = {
            'product_id': product_id,
            'price_analysis': {},
            'quality_analysis': {},
            'overall_score': 0,
            'recommendation': 'unknown',
            'reasoning': []
        }
        
        try:
            # Get price analysis
            price_analysis = await self.pricing_agent.analyze_price(product)
            analysis['price_analysis'] = price_analysis
            analysis['is_good_deal'] = price_analysis.get('is_good_deal', False)
            analysis['price_score'] = self._normalize_score(
                price_analysis.get('market_comparison', 0),
                is_price=True
            )
            
        except Exception as e:
            logger.error(f"Price analysis failed for product {product_id}: {e}")
            analysis['price_analysis'] = {'error': str(e)}
            analysis['price_score'] = 50.0
        
        try:
            # Get quality analysis
            quality_analysis = await self.quality_agent.assess_quality(product)
            analysis['quality_analysis'] = quality_analysis
            analysis['quality_score'] = quality_analysis.get('quality_score', 50.0)
            analysis['quality_rating'] = quality_analysis.get('quality_rating', 'unknown')
            
        except Exception as e:
            logger.error(f"Quality analysis failed for product {product.id}: {e}")
            analysis['quality_analysis'] = {'error': str(e)}
            analysis['quality_score'] = 50.0
        
        # Calculate overall score
        analysis['overall_score'] = self._calculate_overall_score(
            price_score=analysis.get('price_score', 50.0),
            quality_score=analysis.get('quality_score', 50.0),
            match_score=float(getattr(product, 'match_score', 50.0))
        )
        
        # Make final recommendation
        analysis['recommendation'] = self._make_recommendation(analysis)
        
        # Generate reasoning
        analysis['reasoning'] = self._generate_reasoning(analysis)
        
        return analysis
    
    def _normalize_score(self, value: float, is_price: bool = False) -> float:
        """
        Normalize a score to 0-100 range.
        
        Args:
            value: Value to normalize
            is_price: If True, treat as price comparison percentage
            
        Returns:
            Normalized score (0-100)
        """
        if is_price:
            # Price comparison: negative is good (below market)
            # -20% = 100, 0% = 50, +20% = 0
            if value <= -20:
                return 100.0
            elif value >= 20:
                return 0.0
            else:
                return 50.0 - (value * 2.5)
        else:
            # Already 0-100
            return max(0.0, min(100.0, value))
    
    def _calculate_overall_score(
        self,
        price_score: float,
        quality_score: float,
        match_score: float,
        weights: Optional[Dict] = None
    ) -> float:
        """
        Calculate weighted overall score.
        
        Args:
            price_score: Price score (0-100)
            quality_score: Quality score (0-100)
            match_score: Match score (0-100)
            weights: Optional custom weights
            
        Returns:
            Overall score (0-100)
        """
        weights = weights or {
            'quality_weight': 0.4,
            'price_weight': 0.3,
            'match_weight': 0.3
        }
        
        overall = (
            quality_score * weights['quality_weight'] +
            price_score * weights['price_weight'] +
            match_score * weights['match_weight']
        )
        
        return round(overall, 2)
    
    def _make_recommendation(self, analysis: Dict) -> str:
        """
        Make final recommendation based on analysis.
        
        Args:
            analysis: Combined analysis data
            
        Returns:
            Recommendation string
        """
        quality_rec = analysis.get('quality_analysis', {}).get('recommendation', 'unknown')
        is_good_deal = analysis.get('is_good_deal', False)
        overall_score = analysis.get('overall_score', 0)
        
        # Quality concerns override everything
        if quality_rec == 'avoid':
            return 'avoid'
        
        # High overall score + good deal = strong buy
        if overall_score >= 75 and is_good_deal:
            return 'highly_recommended'
        
        # Good score = recommend
        if overall_score >= 60:
            return 'recommended'
        
        # Decent score but caution needed
        if overall_score >= 40:
            return 'consider'
        
        # Low score
        return 'not_recommended'
    
    def _generate_reasoning(self, analysis: Dict) -> List[str]:
        """
        Generate human-readable reasoning for the recommendation.
        
        Args:
            analysis: Combined analysis data
            
        Returns:
            List of reasoning points
        """
        reasoning = []
        
        # Price reasoning
        price_analysis = analysis.get('price_analysis', {})
        if price_analysis.get('is_good_deal'):
            market_comp = price_analysis.get('market_comparison', 0)
            reasoning.append(f"Price is {abs(market_comp):.1f}% below market average")
        
        # Quality reasoning
        quality_analysis = analysis.get('quality_analysis', {})
        quality_rating = quality_analysis.get('quality_rating', 'unknown')
        if quality_rating in ['excellent', 'good']:
            reasoning.append(f"Quality assessment: {quality_rating}")
        elif quality_rating in ['poor', 'suspicious']:
            red_flags = quality_analysis.get('red_flags', [])
            reasoning.append(f"Quality concerns: {len(red_flags)} red flags detected")
        
        # Overall score
        overall_score = analysis.get('overall_score', 0)
        reasoning.append(f"Overall score: {overall_score:.1f}/100")
        
        return reasoning
    
    def _filter_products(
        self,
        analyzed_products: List[Dict],
        filters: Dict
    ) -> List[Dict]:
        """
        Filter products based on criteria.
        
        Args:
            analyzed_products: Products with analysis data
            filters: Filter criteria
            
        Returns:
            Filtered list of products
        """
        min_quality = filters.get('min_quality_score', self.MIN_QUALITY_SCORE)
        min_overall = filters.get('min_overall_score', self.MIN_OVERALL_SCORE)
        
        filtered = []
        for item in analyzed_products:
            analysis = item['analysis']
            
            # Filter by quality score
            if analysis.get('quality_score', 0) < min_quality:
                continue
            
            # Filter by overall score
            if analysis.get('overall_score', 0) < min_overall:
                continue
            
            # Filter out products with "avoid" recommendation
            if analysis.get('quality_analysis', {}).get('recommendation') == 'avoid':
                continue
            
            filtered.append(item)
        
        return filtered
    
    def _rank_products(
        self,
        filtered_products: List[Dict],
        ranking_criteria: Dict
    ) -> List[Dict]:
        """
        Rank products by overall score.
        
        Args:
            filtered_products: Filtered products with analysis
            ranking_criteria: Ranking weights (not used currently, for future)
            
        Returns:
            Ranked list of products
        """
        # Sort by overall score (descending)
        ranked = sorted(
            filtered_products,
            key=lambda x: x['analysis'].get('overall_score', 0),
            reverse=True
        )
        
        # Limit to max results
        max_results = self.MAX_PRODUCTS_TO_RETURN
        return ranked[:max_results]
    
    async def explain_decision(
        self,
        product: Product,
        analysis: Dict
    ) -> str:
        """
        Generate human-readable explanation for a product decision.
        
        Args:
            product: The product
            analysis: Analysis data for the product
            
        Returns:
            Explanation string
        """
        recommendation = analysis.get('recommendation', 'unknown')
        reasoning = analysis.get('reasoning', [])
        overall_score = analysis.get('overall_score', 0)
        
        explanation = f"Product: {getattr(product, 'title', 'Unknown')}\n"
        explanation += f"Recommendation: {recommendation.replace('_', ' ').title()}\n"
        explanation += f"Overall Score: {overall_score:.1f}/100\n\n"
        explanation += "Reasoning:\n"
        
        for i, reason in enumerate(reasoning, 1):
            explanation += f"{i}. {reason}\n"
        
        return explanation

# Made with Bob
