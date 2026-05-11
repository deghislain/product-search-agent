
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from ..models.search_request import SearchRequest
from ..models.product import Product
from ..models.user_interaction import UserInteraction
from ..database import SessionLocal
from sqlalchemy.orm import Session
import logging
import json

# Remove duplicate logging config - should be in main app
logger = logging.getLogger(__name__)

class SearchAgent(BaseAgent):
    """
    SearchAgent specializes in finding products across multiple platforms.
    
    Responsibilities:
    - Analyze past search results and user behavior
    - Decide which platforms to search
    - Optimize search queries based on patterns
    - Execute searches concurrently across platforms
    - Learn from user interactions to improve future searches
    
    Attributes:
        SUPPORTED_PLATFORMS: List of valid platform names
        DEFAULT_MAX_RESULTS: Default number of results per platform
        MAX_CLICKED_PRODUCTS: Maximum clicked products to analyze
    """
    
    # Class constants
    SUPPORTED_PLATFORMS = ['craigslist', 'ebay', 'facebook']
    DEFAULT_MAX_RESULTS = 20
    MAX_CLICKED_PRODUCTS = 20
    
    async def decide_search_strategy(
        self,
        search_request: SearchRequest,
        past_results: List[Product]
    ) -> Dict:
        """
        Analyze past results and decide:
        - Which platforms are most productive
        - Whether to expand or narrow search
        - If query needs refinement
        """
        from datetime import datetime
        
        # Get platform statistics with scores
        platform_stats = self._analyze_platform_performance(past_results)
        
        craigslist_count = platform_stats['craigslist']['count']
        craigslist_avg = platform_stats['craigslist']['avg_score']
        ebay_count = platform_stats['ebay']['count']
        ebay_avg = platform_stats['ebay']['avg_score']
        facebook_count = platform_stats['facebook']['count']
        facebook_avg = platform_stats['facebook']['avg_score']
        
        # Get clicked products (pass user_id if available from search_request)
        user_id = getattr(search_request, 'user_id', None)
        clicked_products = self._get_clicked_products(user_id=user_id)
        
        # Analyze user behavior patterns
        total_clicks = len(clicked_products)
        platform_clicks = {}
        total_clicked_price = 0
        
        for click in clicked_products:
            platform = click.get('platform', 'unknown')
            platform_clicks[platform] = platform_clicks.get(platform, 0) + 1
            total_clicked_price += click.get('price', 0)
        
        most_clicked_platform = max(platform_clicks.items(), key=lambda x: x[1])[0] if platform_clicks else 'none'
        avg_clicked_price = total_clicked_price / total_clicks if total_clicks > 0 else 0
        
        # Get current time context
        now = datetime.now()
        day_of_week = now.strftime('%A')
        time_of_day = now.strftime('%H:%M')
        
        # Build enhanced prompt with rich context
        prompt = f"""
You are a search specialist agent analyzing product search patterns to optimize future searches.

## Search Request
- Product: {search_request.product_name}
- Budget: ${search_request.budget}
- Location: {getattr(search_request, 'location', 'Not specified')}

## Temporal Context
- Current Time: {day_of_week} at {time_of_day}
- Note: Consider that certain platforms have more activity on specific days/times

## Past Results (Last 7 Days)
- Craigslist: {craigslist_count} products found (avg match score: {craigslist_avg:.1f}%)
- eBay: {ebay_count} products found (avg match score: {ebay_avg:.1f}%)
- Facebook: {facebook_count} products found (avg match score: {facebook_avg:.1f}%)

## User Behavior Analysis
- Total clicks: {total_clicks}
- Platform preference: {most_clicked_platform} ({platform_clicks.get(most_clicked_platform, 0)} clicks)
- Average price of clicked items: ${avg_clicked_price:.2f}
- Click distribution: {json.dumps(platform_clicks)}

## Recent Clicked Products (Top 5)
{json.dumps(clicked_products[:5], indent=2) if clicked_products else "No recent clicks"}

## Your Task
Based on the above data, provide strategic recommendations:

1. **Platform Priority**: Which platforms should we search? Consider:
   - Historical match quality (avg scores)
   - User click patterns
   - Platform-specific timing (e.g., Craigslist is better on weekends)
   - Product type suitability

2. **Query Optimization**: Should we adjust the search query? Consider:
   - If current query is too broad/narrow
   - Alternative keywords that might work better
   - Common terms in clicked products

3. **Search Frequency**: How often should we search? Consider:
   - How quickly new listings appear on each platform
   - User engagement level
   - Time of day/week patterns

4. **Reasoning**: Briefly explain your recommendations

## Response Format
Respond in JSON format:
{{
    "platforms": ["platform1", "platform2"],
    "query_adjustment": "adjusted query" or null,
    "search_frequency": "hourly" | "twice_daily" | "daily" | "weekly",
    "reasoning": "Brief explanation of your strategy"
}}
"""
        
        try:
            response = await self.llm.chat.completions.create(
                model= self.llm.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.choices[0].message.content
            strategy = json.loads(content)
    
            # Add validation
            if not self._validate_strategy(strategy):
                logger.warning("Invalid strategy from LLM, using default")
                return self._get_default_strategy()
            
            return strategy
    
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._get_default_strategy()
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return self._get_default_strategy()


    def _get_clicked_products(self, user_id: Optional[str] = None, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        """
        Get list of products user has clicked on.
        
        Args:
            user_id: Optional user identifier. If None, returns all clicks.
            db: Optional database session. If None, creates a new one.
            
        Returns:
            List of dictionaries containing product information from clicked items
        """
        # Create database session if not provided
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True
        
        try:
            # Query user interactions for 'click' type
            query = db.query(UserInteraction, Product).join(
                Product,
                UserInteraction.product_id == Product.id
            ).filter(
                UserInteraction.interaction_type == 'click'
            )
            
            # Filter by user_id if provided
            if user_id:
                query = query.filter(UserInteraction.user_id == user_id)
            
            # Order by most recent clicks first
            query = query.order_by(UserInteraction.timestamp.desc())
            
            # Limit to last 20 clicks to avoid overwhelming the LLM
            results = query.limit(20).all()
            
            # Format results for LLM prompt
            clicked_products = []
            for interaction, product in results:
                clicked_products.append({
                    'title': product.title,
                    'price': product.price,
                    'platform': product.platform,
                    'match_score': product.match_score,
                    'clicked_at': interaction.timestamp.isoformat(),
                    'duration_seconds': interaction.duration_seconds
                })
            
            return clicked_products
            
        except Exception as e:
            logger.error(f"Error fetching clicked products: {e}")
            return []
        finally:
            if should_close_db:
                db.close()

    async def perceive(self, environment: Dict) -> Dict:
        """Extract search-relevant information from environment."""
        return {
            'search_request': environment.get('search_request'),
            'past_results': environment.get('past_results', []),
            'user_interactions': environment.get('user_interactions', []),
            'platform_performance': self._analyze_platform_performance(
                environment.get('past_results', [])
            )
        }

    async def decide(self, observations: Dict) -> Dict:
        """Decide search strategy based on observations."""
        return await self.decide_search_strategy(
            observations['search_request'],
            observations['past_results']
        )

    async def act(self, decision: Dict) -> Dict[str, Any]:
        """
        Execute the search strategy decided by the agent.
        
        Args:
            decision: Dictionary containing:
                - platforms: List of platforms to search
                - query_adjustment: Optional query modification
                - search_frequency: Recommended search frequency
                - search_request: The original search request
                - user_id: Optional user identifier
                
        Returns:
            Dictionary with execution results:
                - products: List of found products
                - platforms_searched: List of platforms that were searched
                - query_used: The actual query used
                - execution_time: Time taken to execute
                - errors: Any errors encountered
        """
        from ..scrapers.craigslist import CraigslistScraper
        from ..scrapers.ebay_factory import get_ebay_scraper, EbayScraperType
        from ..scrapers.facebook_marketplace import FacebookMarketplaceScraper
        from datetime import datetime
        import time
        import asyncio
        
        logger.info(f"SearchAgent executing strategy: {decision}")
        
        start_time = time.time()
        results = {
            'products': [],
            'platforms_searched': [],
            'query_used': None,
            'execution_time': 0,
            'errors': []
        }
        
        try:
            # Extract decision parameters
            platforms = decision.get('platforms', ['craigslist', 'ebay', 'facebook'])
            query_adjustment = decision.get('query_adjustment')
            search_request = decision.get('search_request')
            
            if not search_request:
                logger.error("No search_request provided in decision")
                results['errors'].append("Missing search_request")
                return results
            
            # Apply query adjustment if recommended
            query = search_request.product_name
            if query_adjustment:
                query = query_adjustment
                logger.info(f"Adjusted query from '{search_request.product_name}' to '{query}'")
            
            results['query_used'] = query
            
            # Initialize scrapers for selected platforms
            scrapers = {}
            if 'craigslist' in platforms:
                scrapers['craigslist'] = CraigslistScraper()
            if 'ebay' in platforms:
                scrapers['ebay'] = get_ebay_scraper(scraper_type=EbayScraperType.AUTO)
            if 'facebook' in platforms:
                scrapers['facebook'] = FacebookMarketplaceScraper()
            
            # Execute searches on each platform concurrently
            search_tasks = []
            platform_names = []
            
            for platform_name, scraper in scrapers.items():
                logger.info(f"Preparing search on {platform_name} for: {query}")
                
                try:
                    # Create search task (coroutine)
                    task = scraper.search(
                        query=query,
                        location=getattr(search_request, 'location', None),
                        max_price=getattr(search_request, 'budget', None),
                        max_results=20  # Limit results per platform
                    )
                    search_tasks.append(task)
                    platform_names.append(platform_name)
                    
                except Exception as e:
                    logger.error(f"Error creating search task for {platform_name}: {e}")
                    results['errors'].append(f"{platform_name}: {str(e)}")
            
            # Execute all searches concurrently using asyncio.gather
            if search_tasks:
                logger.info(f"Executing {len(search_tasks)} searches concurrently...")
                
                # gather with return_exceptions=True to handle individual failures
                search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
                
                # Process results
                for platform_name, result in zip(platform_names, search_results):
                    if isinstance(result, Exception):
                        logger.error(f"Search failed on {platform_name}: {result}")
                        results['errors'].append(f"{platform_name}: {str(result)}")
                    elif isinstance(result, list):
                        results['products'].extend(result)
                        results['platforms_searched'].append(platform_name)
                        logger.info(f"Found {len(result)} products on {platform_name}")
                    else:
                        logger.warning(f"Unexpected result type from {platform_name}: {type(result)}")
                        results['errors'].append(f"{platform_name}: Unexpected result type")
            else:
                logger.warning("No search tasks were created")
            
            # Calculate execution time
            results['execution_time'] = time.time() - start_time
            
            # Log results to memory
            self.add_to_memory({
                'action': 'search_execution',
                'timestamp': datetime.now().isoformat(),
                'platforms': results['platforms_searched'],
                'products_found': len(results['products']),
                'query': query,
                'execution_time': results['execution_time']
            })
            
            logger.info(
                f"Search completed: {len(results['products'])} products found "
                f"across {len(results['platforms_searched'])} platforms "
                f"in {results['execution_time']:.2f}s"
            )
            
        except Exception as e:
            logger.error(f"Critical error in act(): {e}")
            results['errors'].append(f"Critical error: {str(e)}")
        
        return results

    def _get_default_strategy(self) -> Dict:
        """
        Fallback strategy if LLM fails.
        
        Returns a safe default strategy that searches all platforms
        with no query adjustment and daily frequency.
        """
        return {
            'platforms': ['craigslist', 'ebay', 'facebook'],
            'query_adjustment': None,
            'search_frequency': 'daily'
        }

    def _analyze_platform_performance(self, past_results: List[Product]) -> Dict:
        """Analyze which platforms are performing best."""
        performance = {}
        for platform in ['craigslist', 'ebay', 'facebook']:
            # Use getattr to safely access platform attribute
            platform_products = [p for p in past_results if getattr(p, 'platform', None) == platform]
            
            # Calculate average score, handling None values
            scores = [getattr(p, 'match_score', 0) for p in platform_products if getattr(p, 'match_score', None) is not None]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            performance[platform] = {
                'count': len(platform_products),
                'avg_score': avg_score
            }
        return performance

    def _validate_strategy(self, strategy: Dict) -> bool:
        """
        Validate that strategy has all required fields and correct types.
        
        Args:
            strategy: Strategy dictionary from LLM
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['platforms', 'query_adjustment', 'search_frequency']
        
        # Check all required fields exist
        if not all(field in strategy for field in required_fields):
            logger.error(f"Strategy missing required fields. Got: {strategy.keys()}")
            return False
        
        # Validate platforms is a list
        if not isinstance(strategy['platforms'], list):
            logger.error(f"'platforms' must be a list, got: {type(strategy['platforms'])}")
            return False
        
        # Validate platforms contains valid platform names
        valid_platforms = ['craigslist', 'ebay', 'facebook']
        for platform in strategy['platforms']:
            if platform not in valid_platforms:
                logger.error(f"Invalid platform: {platform}. Valid: {valid_platforms}")
                return False
        
        # Validate query_adjustment is string or None
        if strategy['query_adjustment'] is not None and not isinstance(strategy['query_adjustment'], str):
            logger.error(f"'query_adjustment' must be string or null, got: {type(strategy['query_adjustment'])}")
            return False
        
        # Validate search_frequency is a string
        if not isinstance(strategy['search_frequency'], str):
            logger.error(f"'search_frequency' must be a string, got: {type(strategy['search_frequency'])}")
            return False
        
        # Validate search_frequency has valid value
        valid_frequencies = ['hourly', 'daily', 'weekly', 'twice_daily']
        if strategy['search_frequency'] not in valid_frequencies:
            logger.warning(f"Unusual search_frequency: {strategy['search_frequency']}. Expected: {valid_frequencies}")
            # Don't fail validation, just warn
        
        return True
