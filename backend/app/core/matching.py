from typing import List, Optional, Dict, Any
from app.models.product import Product
from app.models.search_request import SearchRequest
from app.core.similarity import SimilarityCalculator
from app.core.scoring import ScoreCalculator
from app.core.duplicate_detection import DuplicateDetector
from collections import defaultdict

class ProductMatcher:
    """
    Main matching engine that coordinates product matching workflow.
    
    Responsibilities:
    1. Score products against search criteria
    2. Filter by minimum score threshold
    3. Remove duplicates
    4. Sort by match score
    """
    
    def __init__(
        self,
        min_score_threshold: float = 85.0,
        similarity_calculator: Optional[SimilarityCalculator] = None,
        score_calculator: Optional[ScoreCalculator] = None,
        duplicate_detector: Optional[DuplicateDetector] = None
    ):
        """
        Initialize the matching engine.
        
        Args:
            min_score_threshold: Minimum score to consider a match
            similarity_calculator: Text similarity calculator (auto-created if None)
            score_calculator: Score calculator (auto-created if None)
            duplicate_detector: Duplicate detector (auto-created if None)
        """
        self.min_score_threshold = min_score_threshold
        
        # Use dependency injection or create defaults
        self.similarity_calculator = similarity_calculator or SimilarityCalculator()
        self.score_calculator = score_calculator or ScoreCalculator()
        self.duplicate_detector = duplicate_detector or DuplicateDetector(self.min_score_threshold)
    
    def find_matches(
            self,
            products: List[Product],
            search_request: SearchRequest,
            remove_duplicates: bool = True,
            max_results: Optional[int] = None
        ) -> List[Product]:
            """Find and rank product matches for a search request."""
            
            # Validate inputs
            if not products:
                return []
            
            # Use the search request's match threshold (not the hardcoded one)
            threshold = search_request.match_threshold
            
            # Step 1: Calculate scores
            products = self._calculate_scores_for_products(products, search_request)
            print(f"**********score lenght= {len(products)}")
            print(f"**********score = {products[0].match_score}")
            print(f"**********threshold = {threshold}")
            
            # Step 2: Filter by threshold (use search request's threshold!)
            products = [p for p in products if p.match_score >= threshold]
            print(f"***********Filtered lenght= {len(products)}")
            
            # Step 3: Remove duplicates
            if remove_duplicates:
                products = self.duplicate_detector.remove_duplicates(products)
            
            # Step 4: Sort by score (highest first)
            products.sort(key=lambda p: p.match_score, reverse=True)
            
            # Step 5: Limit results
            if max_results:
                products = products[:max_results]
            
            return products

    def _calculate_scores_for_products(
        self,
        products: List[Product],
        search_request: SearchRequest
    ) -> List[Product]:
        """
        Calculate and assign match scores to products.
        
        Modifies products in-place by setting match_score attribute.
        
        Returns:
            Same products list with match_score populated
        """
        for product in products:
            product.match_score = self.score_calculator.calculate_match_score(
                product,
                search_request
            )
        return products
    
    
    def get_match_statistics(self, products: List[Product], search_request: SearchRequest) -> Dict[str, Any]:
        if not products:
            return {
                "total_products": 0,
                "matches_found": 0,
                "average_score": 0.0,
                "score_distribution": {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0},
                "platform_breakdown": {}
            }
        
        total_products = len(products)
        matches_found = sum(1 for p in products if p.is_match)
        average_score = sum(p.match_score for p in products) / total_products
        
        score_distribution = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
        platform_breakdown = defaultdict(int)
        
        for product in products:
            # Count ALL products in distribution, not just matches
            score = product.match_score
            if score <= 20:
                score_distribution["0-20"] += 1
            elif score <= 40:
                score_distribution["21-40"] += 1
            elif score <= 60:
                score_distribution["41-60"] += 1
            elif score <= 80:
                score_distribution["61-80"] += 1
            else:
                score_distribution["81-100"] += 1
            
            # Only count matches in platform breakdown
            if product.is_match:
                platform_breakdown[product.platform] += 1
        
        return {
            "total_products": total_products,
            "matches_found": matches_found,
            "average_score": round(average_score, 2),
            "score_distribution": score_distribution,
            "platform_breakdown": dict(platform_breakdown)
        }

      