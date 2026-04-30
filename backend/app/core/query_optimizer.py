"""
Query Optimizer - Makes search queries smarter using AI.

Before: User searches for "car"
After: AI suggests "Toyota Camry 2015-2018 sedan reliable under 100k miles"
"""
import logging
from typing import List, Dict
from app.core.llm_client import get_groq_client
from app.models.product import Product


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



class QueryOptimizer:
    """
    Uses AI to improve search queries based on past results.
    
    How it works:
    1. User creates search: "car"
    2. System finds some results
    3. User clicks on some, ignores others
    4. AI analyzes what user liked
    5. AI suggests better query: "Toyota Camry 2015-2018"
    """
    
    def __init__(self):
        """Initialize with Ollama client."""
        self.llm = get_groq_client()
    
    async def optimize_query(
        self,
        original_query: str,
        budget: float,
        previous_results: List[Product],
        clicked_products: List[Product],
        ignored_products: List[Product]
    ) -> str:
        """
        Generate an improved search query.
        
        Args:
            original_query: User's original search (e.g., "car")
            budget: User's budget
            previous_results: All products found before
            clicked_products: Products user clicked on
            ignored_products: Products user ignored
        
        Returns:
            str: Improved query (e.g., "Toyota Camry 2015-2018 sedan")
        
        Example:
            >>> optimizer = QueryOptimizer()
            >>> improved = await optimizer.optimize_query(
            ...     original_query="car",
            ...     budget=10000,
            ...     previous_results=[...],
            ...     clicked_products=[toyota1, toyota2],
            ...     ignored_products=[honda1, ford1]
            ... )
            >>> print(improved)
            "Toyota Camry 2015-2018 sedan under $10k"
        """
        logger.info(f"Optimizing query: {original_query}")
        
        # Build context for AI
        clicked_titles = [p.title for p in clicked_products[:5]]
        ignored_titles = [p.title for p in ignored_products[:5]]
        
        prompt = f"""
You are a product search expert. Analyze the user's search behavior and suggest a better search query.

Original Query: "{original_query}"
Budget: ${budget:,.0f}

Products User CLICKED (they liked these):
{chr(10).join(f"- {title}" for title in clicked_titles) if clicked_titles else "- None yet"}

Products User IGNORED (they didn't like these):
{chr(10).join(f"- {title}" for title in ignored_titles) if ignored_titles else "- None yet"}

Total Results Found: {len(previous_results)}

Based on what the user clicked vs ignored, suggest a MORE SPECIFIC search query that will find products they actually want.

Rules:
1. Include specific brands/models if user showed preference
2. Include year range if relevant
3. Include condition keywords if user prefers certain conditions
4. Keep it concise (under 10 words)
5. Return ONLY the improved query, nothing else

Improved Query:"""

        try:
            improved_query = await self.llm.generate(
                prompt,
                temperature=0.3,  # Low temperature = more focused
                max_tokens=50
            )
            
            # Clean up response
            improved_query = improved_query.strip().strip('"').strip("'")
            
            logger.info(f"Optimized query: {original_query} → {improved_query}")
            return improved_query
            
        except Exception as e:
            logger.error(f"Query optimization failed: {e}")
            # Fallback to original query
            return original_query
    
    async def suggest_search_improvements(
        self,
        search_request_id: int,
        results_count: int,
        match_count: int
    ) -> Dict[str, any]:
        """
        Suggest improvements to search strategy.
        
        Args:
            search_request_id: ID of search request
            results_count: Total products found
            match_count: Products that matched threshold
        
        Returns:
            dict: Suggestions like:
                {
                    "should_adjust_threshold": True,
                    "suggested_threshold": 65.0,
                    "should_expand_query": False,
                    "reasoning": "You're getting too few matches..."
                }
        """
        prompt = f"""
Analyze this product search performance:

Total Products Found: {results_count}
Products Matching Threshold: {match_count}
Match Rate: {(match_count/results_count*100) if results_count > 0 else 0:.1f}%

Suggest improvements:
1. Should we adjust the match threshold? (currently 70%)
2. Should we expand or narrow the search query?
3. Should we search more or less frequently?

Respond in JSON format:
{{
    "should_adjust_threshold": true/false,
    "suggested_threshold": 65.0,
    "should_expand_query": true/false,
    "reasoning": "explanation here"
}}
"""
        
        try:
            response = await self.llm.generate(prompt, temperature=0.3)
            # Parse JSON response
            import json
            suggestions = json.loads(response)
            return suggestions
        except Exception as e:
            logger.error(f"Failed to get suggestions: {e}")
            return {
                "should_adjust_threshold": False,
                "reasoning": "Unable to analyze at this time"
            }