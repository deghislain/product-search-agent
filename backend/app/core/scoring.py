from typing import Optional
from app.models.product import Product
from app.models.search_request import SearchRequest
from app.core.similarity import SimilarityCalculator

class ScoreCalculator:
    """
    Calculates match scores for products against search criteria.
    
    Uses weighted scoring: Title (40%) + Description (40%) + Price (20%)
    """
    
    def __init__(self):
        # Weights for scoring components
        self.TITLE_WEIGHT = 0.40
        self.DESCRIPTION_WEIGHT = 0.40
        self.PRICE_WEIGHT = 0.20
    
    def calculate_title_score(
        self, 
        product_title: str, 
        search_product_name: str
    ) -> float:
        """Calculate title similarity score (0-100)."""
        return SimilarityCalculator.calculate_similarity(
            product_title, 
            search_product_name
        )
    
    def calculate_description_score(
        self,
        product_description: Optional[str],
        search_product_description: str
    ) -> float:
        """Calculate description similarity score (0-100)."""
        if not product_description:
            return 50.0
        return SimilarityCalculator.calculate_similarity(
            product_description, 
            search_product_description
        )
    
    def calculate_price_score(
        self,
        product_price: float,
        search_product_max_price: Optional[float]
    ) -> float:
        """Calculate price attractiveness score (0-100)."""
        if not search_product_max_price:
            return 100.0
        
        # Binary scoring: within budget or not
        if product_price <= search_product_max_price:
            return 100.0
        else:
            return 0.0
    
    def calculate_match_score(
        self,
        product: Product,
        search_request: SearchRequest
    ) -> float:
        """Calculate overall match score (0-100)."""
        # Get individual scores (all 0-100)
        title_score = self.calculate_title_score(
            product.title, 
            search_request.product_name
        )
        description_score = self.calculate_description_score(
            product.description, 
            search_request.product_description
        )
        price_score = self.calculate_price_score(
            product.price, 
            search_request.budget
        )
        # Apply weights and calculate final score
        final_score = (
            (title_score * self.TITLE_WEIGHT) +
            (description_score * self.DESCRIPTION_WEIGHT) +
            (price_score * self.PRICE_WEIGHT)
        )
        
        return round(final_score, 2)