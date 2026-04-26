"""
Reasoning Engine - Explains AI decisions to users.

Instead of just showing a match score, explain WHY it matched.
"""
from ast import Dict
import logging
from typing import Dict
from app.core.llm_client import get_ollama_client
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
        self.llm = get_ollama_client()
    
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