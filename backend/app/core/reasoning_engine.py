"""
Reasoning Engine - Explains AI decisions to users.

Instead of just showing a match score, explain WHY it matched.
"""
import logging
from typing import Dict
from app.core.llm_client import get_groq_client
from app.models.product import Product
from app.models.search_request import SearchRequest


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



class ReasoningEngine:
    """
    Generates human-readable explanations for AI decisions.
    
    Makes the system transparent and trustworthy.
    """
    
    def __init__(self):
        """Initialize with Ollama client."""
        self.llm = get_groq_client()
    
    async def explain_match_score(
        self,
        product: Product,
        search_request: SearchRequest
    ) -> str:
        """
        Explain why a product matched (or didn't match).
        
        Args:
            product: The product to explain
            search_request: The search criteria
        
        Returns:
            str: Human-readable explanation
        
        Example output:
            "This product scored 87% because:
            ✅ Title matches 'Toyota Camry' (95% similarity)
            ✅ Price $5,500 is $500 under your budget (great deal!)
            ✅ Description mentions 'excellent condition'
            ⚠️ Located 50 miles away (you prefer local)
            ❌ Missing some features you typically prefer"
        """
        prompt = f"""
Explain why this product matched the user's search:

SEARCH CRITERIA:
- Looking for: {search_request.product_name}
- Description: {search_request.product_description}
- Budget: ${search_request.budget:,.0f}
- Location: {search_request.location or 'Any'}

PRODUCT FOUND:
- Title: {product.title}
- Price: ${product.price:,.0f}
- Description: {product.description[:200]}...
- Location: {product.location}
- Match Score: {product.match_score:.1f}%

Explain in simple terms why this product scored {product.match_score:.1f}%.
Use ✅ for good matches, ⚠️ for concerns, ❌ for mismatches.
Keep it under 100 words.

Explanation:"""

        try:
            explanation = await self.llm.generate(
                prompt,
                temperature=0.5,
                max_tokens=200
            )
            return explanation.strip()
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            return f"This product scored {product.match_score:.1f}% based on title and description similarity."
    
    async def explain_search_strategy(
        self,
        platform_results: Dict[str, int],
        user_click_history: Dict[str, int]
    ) -> str:
        """
        Explain why the system chose certain platforms.
        
        Args:
            platform_results: Results per platform (e.g., {"craigslist": 15, "ebay": 3})
            user_click_history: Clicks per platform (e.g., {"craigslist": 12, "ebay": 1})
        
        Returns:
            str: Explanation of strategy
        """
        prompt = f"""
Explain the search strategy to the user:

RESULTS BY PLATFORM:
{chr(10).join(f"- {platform}: {count} products" for platform, count in platform_results.items())}

USER ENGAGEMENT:
{chr(10).join(f"- {platform}: {count} clicks" for platform, count in user_click_history.items())}

Explain in 2-3 sentences why we're focusing on certain platforms.
Be conversational and helpful.

Explanation:"""

        try:
            explanation = await self.llm.generate(prompt, temperature=0.7)
            return explanation.strip()
        except Exception as e:
            logger.error(f"Failed to explain strategy: {e}")
            return "Searching all platforms to find the best matches for you."
    
    async def explain_optimization(
        self,
        original_query: str,
        optimized_query: str,
        clicked_products: list,
        ignored_products: list
    ) -> str:
        """
        Explain why the query was optimized in a specific way.
        
        Args:
            original_query: The original search query
            optimized_query: The AI-optimized query
            clicked_products: Products with high match scores (user liked)
            ignored_products: Products with low match scores (user ignored)
        
        Returns:
            str: Human-readable explanation of the optimization
        
        Example output:
            "Based on 15 high-scoring matches, I added year range 2015-2018
            and popular trim levels (LE, SE, XLE). I also added a mileage
            constraint based on your budget. This should give you more
            relevant results."
        """
        # Extract patterns from clicked products
        clicked_titles = [p.title for p in clicked_products[:5]]
        ignored_titles = [p.title for p in ignored_products[:5]]
        
        prompt = f"""
Explain why we optimized this search query:

ORIGINAL QUERY: "{original_query}"
OPTIMIZED QUERY: "{optimized_query}"

USER PREFERENCES (based on high-scoring products):
{chr(10).join(f"- {title}" for title in clicked_titles) if clicked_titles else "- No clear preferences yet"}

PRODUCTS USER IGNORED (low scores):
{chr(10).join(f"- {title}" for title in ignored_titles) if ignored_titles else "- None"}

Explain in 2-3 sentences what changes were made and why.
Be conversational and focus on how this helps the user.
Start with "Based on your preferences..."

Explanation:"""

        try:
            explanation = await self.llm.generate(
                prompt,
                temperature=0.7,
                max_tokens=150
            )
            return explanation.strip()
        except Exception as e:
            logger.error(f"Failed to explain optimization: {e}")
            # Fallback explanation
            changes = []
            if len(optimized_query) > len(original_query):
                changes.append("added more specific details")
            if any(year in optimized_query for year in ['2015', '2016', '2017', '2018', '2019', '2020']):
                changes.append("included year range")
            
            if changes:
                return f"Based on {len(clicked_products)} products you liked, I {' and '.join(changes)} to find better matches."
            else:
                return f"Refined the search based on {len(clicked_products)} high-scoring products to improve results."