"""
User Preference Learning Module

This module implements the PreferenceLearner class that tracks user interactions
with products and learns their preferences over time to improve product matching.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from collections import defaultdict
import json

from app.models.product import Product
from app.models.search_request import SearchRequest
from app.models.user_interaction import UserInteraction
from app.models.user_preference import UserPreference
from app.database import SessionLocal


class PreferenceLearner:
    """
    Tracks user interactions to learn preferences:
    - Which products they click
    - Which they ignore
    - Which they purchase
    - Time spent viewing
    
    The learner analyzes patterns in user behavior to:
    1. Adjust match thresholds dynamically
    2. Learn price sensitivity
    3. Identify preferred brands/features
    4. Understand location preferences
    """
    
    def __init__(self, db: Optional[Session] = None):
        """
        Initialize the PreferenceLearner.
        
        Args:
            db: Optional database session. If not provided, creates a new one.
        """
        self.db = db
        self._should_close_db = db is None
        if self.db is None:
            self.db = SessionLocal()
    
    def __del__(self):
        """Clean up database session if we created it."""
        if self._should_close_db and self.db:
            self.db.close()
    
    async def track_interaction(
        self,
        user_id: str,
        product: Product,
        action: str,  # 'view', 'click', 'ignore', 'purchase'
        duration_seconds: int = 0,
        metadata: Optional[Dict] = None
    ) -> UserInteraction:
        """
        Record user interaction with product.
        
        Args:
            user_id: Unique identifier for the user
            product: Product that was interacted with
            action: Type of interaction ('view', 'click', 'ignore', 'purchase')
            duration_seconds: How long the user viewed the product
            metadata: Additional interaction data (optional)
        
        Returns:
            UserInteraction: The created interaction record
        
        Example:
            ```python
            learner = PreferenceLearner()
            interaction = await learner.track_interaction(
                user_id="user123",
                product=product,
                action="click",
                duration_seconds=45
            )
            ```
        """
        # Create interaction record
        interaction = UserInteraction(
            user_id=user_id,
            product_id=product.id,  # product.id is already a string (UUID)
            interaction_type=action,
            timestamp=datetime.utcnow(),
            duration_seconds=duration_seconds,
            interaction_metadata=json.dumps(metadata) if metadata else None
        )
        
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        
        # Update user preferences based on this interaction
        await self._update_preferences_from_interaction(user_id, product, action, duration_seconds)
        
        return interaction
    
    async def _update_preferences_from_interaction(
        self,
        user_id: str,
        product: Product,
        action: str,
        duration_seconds: int
    ):
        """
        Update user preferences based on a single interaction.
        
        This method analyzes the interaction and updates various preference metrics.
        """
        # Weight different actions differently
        action_weights = {
            'purchase': 1.0,
            'click': 0.7,
            'view': 0.3,
            'ignore': -0.2
        }
        
        weight = action_weights.get(action, 0.0)
        
        # Update price sensitivity
        if action in ['purchase', 'click']:
            await self._update_price_preference(user_id, product.price, weight)
        
        # Update platform preference
        await self._update_platform_preference(user_id, product.platform, weight)
        
        # Update location preference
        if product.location:
            await self._update_location_preference(user_id, product.location, weight)
        
        # Extract and update feature preferences from title/description
        await self._update_feature_preferences(user_id, product, weight)
    
    async def _update_price_preference(self, user_id: str, price: float, weight: float):
        """Update user's price sensitivity based on interaction."""
        pref = self.db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.preference_type == 'price_sensitivity'
            )
        ).first()
        
        if pref:
            # Update existing preference
            current_data = json.loads(pref.preference_value)
            current_data['total_interactions'] = current_data.get('total_interactions', 0) + 1
            current_data['avg_price'] = (
                (current_data.get('avg_price', price) * current_data.get('total_interactions', 1) + price) /
                (current_data.get('total_interactions', 1) + 1)
            )
            current_data['max_price'] = max(current_data.get('max_price', price), price)
            current_data['min_price'] = min(current_data.get('min_price', price), price)
            
            pref.preference_value = json.dumps(current_data)
            pref.confidence_score = min(1.0, pref.confidence_score + 0.05)
            pref.last_updated = datetime.utcnow()
        else:
            # Create new preference
            pref = UserPreference(
                user_id=user_id,
                preference_type='price_sensitivity',
                preference_value=json.dumps({
                    'avg_price': price,
                    'max_price': price,
                    'min_price': price,
                    'total_interactions': 1
                }),
                confidence_score=0.1,
                last_updated=datetime.utcnow()
            )
            self.db.add(pref)
        
        self.db.commit()
    
    async def _update_platform_preference(self, user_id: str, platform: str, weight: float):
        """Update user's platform preferences."""
        pref = self.db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.preference_type == 'platform_preference'
            )
        ).first()
        
        if pref:
            current_data = json.loads(pref.preference_value)
            current_data[platform] = current_data.get(platform, 0) + weight
            pref.preference_value = json.dumps(current_data)
            pref.confidence_score = min(1.0, pref.confidence_score + 0.05)
            pref.last_updated = datetime.utcnow()
        else:
            pref = UserPreference(
                user_id=user_id,
                preference_type='platform_preference',
                preference_value=json.dumps({platform: weight}),
                confidence_score=0.1,
                last_updated=datetime.utcnow()
            )
            self.db.add(pref)
        
        self.db.commit()
    
    async def _update_location_preference(self, user_id: str, location: str, weight: float):
        """Update user's location preferences."""
        pref = self.db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.preference_type == 'location_preference'
            )
        ).first()
        
        if pref:
            current_data = json.loads(pref.preference_value)
            current_data[location] = current_data.get(location, 0) + weight
            pref.preference_value = json.dumps(current_data)
            pref.confidence_score = min(1.0, pref.confidence_score + 0.05)
            pref.last_updated = datetime.utcnow()
        else:
            pref = UserPreference(
                user_id=user_id,
                preference_type='location_preference',
                preference_value=json.dumps({location: weight}),
                confidence_score=0.1,
                last_updated=datetime.utcnow()
            )
            self.db.add(pref)
        
        self.db.commit()
    
    async def _update_feature_preferences(self, user_id: str, product: Product, weight: float):
        """Extract and update feature preferences from product title/description."""
        # Simple keyword extraction (in production, use NLP)
        text = f"{product.title} {product.description or ''}".lower()
        
        # Common feature keywords to track
        feature_keywords = [
            'new', 'used', 'excellent', 'good', 'fair',
            'warranty', 'box', 'original', 'unlocked',
            'leather', 'fabric', 'metal', 'wood',
            'automatic', 'manual', 'electric'
        ]
        
        found_features = [kw for kw in feature_keywords if kw in text]
        
        if not found_features:
            return
        
        pref = self.db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.preference_type == 'feature_preference'
            )
        ).first()
        
        if pref:
            current_data = json.loads(pref.preference_value)
            for feature in found_features:
                current_data[feature] = current_data.get(feature, 0) + weight
            pref.preference_value = json.dumps(current_data)
            pref.confidence_score = min(1.0, pref.confidence_score + 0.02)
            pref.last_updated = datetime.utcnow()
        else:
            pref = UserPreference(
                user_id=user_id,
                preference_type='feature_preference',
                preference_value=json.dumps({f: weight for f in found_features}),
                confidence_score=0.05,
                last_updated=datetime.utcnow()
            )
            self.db.add(pref)
        
        self.db.commit()
    
    async def get_preference_weights(self, user_id: str) -> Dict:
        """
        Return learned weights for scoring.
        
        Args:
            user_id: User identifier
        
        Returns:
            Dictionary with preference weights:
            {
                'price_sensitivity': 0.8,
                'condition_importance': 0.6,
                'location_preference': 0.3,
                'platform_scores': {'craigslist': 0.8, 'ebay': 0.5},
                'preferred_features': ['leather', 'warranty']
            }
        
        Example:
            ```python
            learner = PreferenceLearner()
            weights = await learner.get_preference_weights("user123")
            print(f"Price sensitivity: {weights['price_sensitivity']}")
            ```
        """
        preferences = self.db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).all()
        
        weights = {
            'price_sensitivity': 0.5,  # Default
            'condition_importance': 0.5,
            'location_preference': 0.3,
            'platform_scores': {},
            'preferred_features': [],
            'location_scores': {}
        }
        
        for pref in preferences:
            data = json.loads(pref.preference_value)
            
            if pref.preference_type == 'price_sensitivity':
                # Calculate price sensitivity based on interaction patterns
                avg_price = data.get('avg_price', 0)
                max_price = data.get('max_price', 0)
                if max_price > 0:
                    weights['price_sensitivity'] = min(1.0, avg_price / max_price)
            
            elif pref.preference_type == 'platform_preference':
                weights['platform_scores'] = data
            
            elif pref.preference_type == 'location_preference':
                weights['location_scores'] = data
            
            elif pref.preference_type == 'feature_preference':
                # Get top features by score
                sorted_features = sorted(data.items(), key=lambda x: x[1], reverse=True)
                weights['preferred_features'] = [f[0] for f in sorted_features[:10]]
        
        return weights
    
    async def adjust_match_threshold(
        self,
        user_id: str,
        search_request: SearchRequest
    ) -> float:
        """
        Dynamically adjust threshold based on:
        - How many matches user typically clicks
        - If user complains about too many/few results
        - Historical interaction patterns
        
        Args:
            user_id: User identifier
            search_request: The search request to adjust threshold for
        
        Returns:
            float: Adjusted match threshold (0-100)
        
        Example:
            ```python
            learner = PreferenceLearner()
            new_threshold = await learner.adjust_match_threshold("user123", search)
            search.update_threshold(new_threshold)
            ```
        """
        # Get user's interaction history
        recent_interactions = self.db.query(UserInteraction).filter(
            and_(
                UserInteraction.user_id == user_id,
                UserInteraction.timestamp >= datetime.utcnow() - timedelta(days=30)
            )
        ).all()
        
        if not recent_interactions:
            # No history, use default threshold
            return search_request.match_threshold
        
        # Calculate click-through rate
        total_views = len([i for i in recent_interactions if i.interaction_type == 'view'])
        total_clicks = len([i for i in recent_interactions if i.interaction_type == 'click'])
        total_purchases = len([i for i in recent_interactions if i.interaction_type == 'purchase'])
        
        if total_views == 0:
            return search_request.match_threshold
        
        click_rate = total_clicks / total_views
        purchase_rate = total_purchases / total_views if total_views > 0 else 0
        
        # Adjust threshold based on engagement
        current_threshold = search_request.match_threshold
        
        if click_rate < 0.1:
            # User clicks very few items - lower threshold to show more options
            adjusted_threshold = max(50.0, current_threshold - 5.0)
        elif click_rate > 0.5:
            # User clicks many items - raise threshold to show only best matches
            adjusted_threshold = min(90.0, current_threshold + 5.0)
        else:
            # Good engagement, keep threshold similar
            adjusted_threshold = current_threshold
        
        # Boost threshold if user makes purchases (they know what they want)
        if purchase_rate > 0.05:
            adjusted_threshold = min(95.0, adjusted_threshold + 3.0)
        
        return adjusted_threshold
    
    async def get_user_stats(self, user_id: str) -> Dict:
        """
        Get statistics about user's interaction patterns.
        
        Args:
            user_id: User identifier
        
        Returns:
            Dictionary with user statistics
        """
        interactions = self.db.query(UserInteraction).filter(
            UserInteraction.user_id == user_id
        ).all()
        
        if not interactions:
            return {
                'total_interactions': 0,
                'total_views': 0,
                'total_clicks': 0,
                'total_purchases': 0,
                'click_through_rate': 0.0,
                'purchase_rate': 0.0
            }
        
        total_views = len([i for i in interactions if i.interaction_type == 'view'])
        total_clicks = len([i for i in interactions if i.interaction_type == 'click'])
        total_purchases = len([i for i in interactions if i.interaction_type == 'purchase'])
        
        return {
            'total_interactions': len(interactions),
            'total_views': total_views,
            'total_clicks': total_clicks,
            'total_purchases': total_purchases,
            'click_through_rate': total_clicks / total_views if total_views > 0 else 0.0,
            'purchase_rate': total_purchases / total_views if total_views > 0 else 0.0,
            'avg_view_duration': sum(i.duration_seconds for i in interactions) / len(interactions)
        }


# Made with Bob