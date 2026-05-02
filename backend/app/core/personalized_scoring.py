"""
Personalized Scoring Module

This module extends the base scoring system with user preference learning.
It adjusts product scores based on learned user behavior and preferences.
"""

from typing import Optional, Dict
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.search_request import SearchRequest
from app.core.scoring import ScoreCalculator
from app.core.preference_learner import PreferenceLearner


class PersonalizedScoreCalculator(ScoreCalculator):
    """
    Enhanced score calculator that incorporates user preferences.
    
    Extends the base ScoreCalculator with personalization based on:
    - User's price sensitivity
    - Platform preferences
    - Location preferences
    - Feature preferences
    
    Example:
        ```python
        from app.core.personalized_scoring import PersonalizedScoreCalculator
        from app.database import SessionLocal
        
        db = SessionLocal()
        calculator = PersonalizedScoreCalculator(db=db)
        
        # Calculate personalized score
        score = await calculator.calculate_personalized_score(
            product=product,
            search_request=search_request,
            user_id="user123"
        )
        ```
    """
    
    def __init__(self, db: Optional[Session] = None):
        """
        Initialize the personalized score calculator.
        
        Args:
            db: Optional database session. If not provided, creates a new one.
        """
        super().__init__()
        self.db = db
        self.learner = PreferenceLearner(db=db)
    
    async def calculate_personalized_score(
        self,
        product: Product,
        search_request: SearchRequest,
        user_id: Optional[str] = None
    ) -> float:
        """
        Calculate a personalized match score for a product.
        
        This method:
        1. Calculates the base score using standard scoring
        2. Retrieves user preferences if user_id is provided
        3. Applies preference-based adjustments to the score
        
        Args:
            product: The product to score
            search_request: The search criteria
            user_id: Optional user identifier for personalization
        
        Returns:
            float: Personalized match score (0-100)
        
        Example:
            ```python
            score = await calculator.calculate_personalized_score(
                product=product,
                search_request=search,
                user_id="user123"
            )
            print(f"Personalized score: {score}")
            ```
        """
        # Calculate base score
        base_score = self.calculate_match_score(product, search_request)
        
        # If no user_id, return base score
        if not user_id:
            return base_score
        
        # Get user preference weights
        try:
            weights = await self.learner.get_preference_weights(user_id)
        except Exception as e:
            # If preferences can't be loaded, return base score
            print(f"Warning: Could not load preferences for user {user_id}: {e}")
            return base_score
        
        # Apply preference-based adjustments
        adjusted_score = self._apply_preference_adjustments(
            base_score=base_score,
            product=product,
            search_request=search_request,
            weights=weights
        )
        
        # Ensure score stays within 0-100 range
        return max(0.0, min(100.0, adjusted_score))
    
    def _apply_preference_adjustments(
        self,
        base_score: float,
        product: Product,
        search_request: SearchRequest,
        weights: Dict
    ) -> float:
        """
        Apply preference-based adjustments to the base score.
        
        Args:
            base_score: The base match score
            product: The product being scored
            search_request: The search criteria
            weights: User preference weights
        
        Returns:
            float: Adjusted score
        """
        adjusted_score = base_score
        
        # 1. Platform preference adjustment
        platform_scores = weights.get('platform_scores', {})
        if product.platform in platform_scores:
            platform_boost = platform_scores[product.platform] * 5  # Max 5 point boost
            adjusted_score += platform_boost
        
        # 2. Price sensitivity adjustment
        price_sensitivity = weights.get('price_sensitivity', 0.5)
        if search_request.budget and product.price:
            price_ratio = product.price / search_request.budget
            
            # If user is price sensitive and product is cheap, boost score
            if price_sensitivity > 0.7 and price_ratio < 0.7:
                adjusted_score += 5.0
            # If user is not price sensitive and product is expensive, don't penalize
            elif price_sensitivity < 0.3 and price_ratio > 0.9:
                adjusted_score += 2.0
        
        # 3. Location preference adjustment
        location_scores = weights.get('location_scores', {})
        if product.location:
            for preferred_location, location_score in location_scores.items():
                if preferred_location.lower() in product.location.lower():
                    location_boost = location_score * 3  # Max 3 point boost
                    adjusted_score += location_boost
                    break
        
        # 4. Feature preference adjustment
        preferred_features = weights.get('preferred_features', [])
        if preferred_features and product.title:
            title_lower = product.title.lower()
            desc_lower = (product.description or '').lower()
            
            feature_matches = 0
            for feature in preferred_features[:5]:  # Check top 5 features
                if feature in title_lower or feature in desc_lower:
                    feature_matches += 1
            
            # Boost score based on feature matches
            if feature_matches > 0:
                feature_boost = min(feature_matches * 2, 8)  # Max 8 point boost
                adjusted_score += feature_boost
        
        return adjusted_score
    
    async def get_dynamic_threshold(
        self,
        search_request: SearchRequest,
        user_id: Optional[str] = None
    ) -> float:
        """
        Get a dynamically adjusted match threshold for a user.
        
        This method uses the PreferenceLearner to adjust the threshold
        based on user behavior patterns.
        
        Args:
            search_request: The search request
            user_id: Optional user identifier
        
        Returns:
            float: Adjusted match threshold (0-100)
        
        Example:
            ```python
            threshold = await calculator.get_dynamic_threshold(
                search_request=search,
                user_id="user123"
            )
            print(f"Dynamic threshold: {threshold}")
            ```
        """
        if not user_id:
            return search_request.match_threshold
        
        try:
            return await self.learner.adjust_match_threshold(user_id, search_request)
        except Exception as e:
            print(f"Warning: Could not adjust threshold for user {user_id}: {e}")
            return search_request.match_threshold
    
    async def score_and_filter_products(
        self,
        products: list[Product],
        search_request: SearchRequest,
        user_id: Optional[str] = None
    ) -> list[tuple[Product, float]]:
        """
        Score multiple products and filter by threshold.
        
        Args:
            products: List of products to score
            search_request: The search criteria
            user_id: Optional user identifier for personalization
        
        Returns:
            list: List of (product, score) tuples for products above threshold
        
        Example:
            ```python
            scored_products = await calculator.score_and_filter_products(
                products=all_products,
                search_request=search,
                user_id="user123"
            )
            
            for product, score in scored_products:
                print(f"{product.title}: {score}")
            ```
        """
        # Get dynamic threshold
        threshold = await self.get_dynamic_threshold(search_request, user_id)
        
        # Score all products
        scored_products = []
        for product in products:
            score = await self.calculate_personalized_score(
                product=product,
                search_request=search_request,
                user_id=user_id
            )
            
            # Only include products above threshold
            if score >= threshold:
                scored_products.append((product, score))
        
        # Sort by score (highest first)
        scored_products.sort(key=lambda x: x[1], reverse=True)
        
        return scored_products


# Made with Bob