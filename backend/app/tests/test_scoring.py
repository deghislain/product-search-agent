import pytest
import sys
from pathlib import Path

# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models.product import Product
from app.models.search_request import SearchRequest
from app.core.scoring import ScoreCalculator
from app.core.similarity import SimilarityCalculator


class TestScoreCalculator:
    """Test scoring calculations."""
    
    def setup_method(self):
        """Setup for each test - create calculator instance."""
        self.calc = ScoreCalculator()
    
    # ========== Title Score Tests ==========
    
    def test_calculate_title_score_exact_match(self):
        """Test title scoring with exact match."""
        score = self.calc.calculate_title_score("iPhone 13", "iPhone 13")
        assert score == 100.0, "Exact match should score 100"
    
    def test_calculate_title_score_partial_match(self):
        """Test title scoring with partial match."""
        score = self.calc.calculate_title_score("iPhone 13 Pro 128GB", "iPhone 13")
        assert 70 <= score <= 100, f"Partial match should score 70-100, got {score}"
    
    def test_calculate_title_score_no_match(self):
        """Test title scoring with no match."""
        score = self.calc.calculate_title_score("Samsung Galaxy", "iPhone")
        assert score < 50, f"No match should score <50, got {score}"
    
    def test_calculate_title_score_case_insensitive(self):
        """Test title scoring is case insensitive."""
        score1 = self.calc.calculate_title_score("iPhone 13", "iphone 13")
        score2 = self.calc.calculate_title_score("iPhone 13", "IPHONE 13")
        assert score1 > 95, "Case should not matter"
        assert score2 > 95, "Case should not matter"
    
    # ========== Description Score Tests ==========
    
    def test_calculate_description_score_with_description(self):
        """Test description scoring with valid description."""
        score = self.calc.calculate_description_score(
            "Brand new iPhone in excellent condition",
            "iPhone excellent condition"
        )
        assert 60 <= score <= 100, f"Good match should score 60-100, got {score}"
    
    def test_calculate_description_score_none_description(self):
        """Test description scoring with None description."""
        score = self.calc.calculate_description_score(None, "iPhone")
        assert score == 50.0, "None description should return neutral score of 50"
    
    def test_calculate_description_score_empty_description(self):
        """Test description scoring with empty description."""
        score = self.calc.calculate_description_score("", "iPhone")
        assert score == 50.0, "Empty description should return neutral score of 50"
    
    def test_calculate_description_score_no_match(self):
        """Test description scoring with no match."""
        score = self.calc.calculate_description_score(
            "Android phone Samsung",
            "iPhone Apple"
        )
        assert score < 50, f"No match should score <50, got {score}"
    
    # ========== Price Score Tests ==========
    
    def test_calculate_price_score_within_budget(self):
        """Test price scoring when within budget."""
        score = self.calc.calculate_price_score(500, 600)
        assert score == 100.0, "Price within budget should score 100"
    
    def test_calculate_price_score_at_budget(self):
        """Test price scoring when exactly at budget."""
        score = self.calc.calculate_price_score(600, 600)
        assert score == 100.0, "Price at budget should score 100"
    
    def test_calculate_price_score_over_budget(self):
        """Test price scoring when over budget."""
        score = self.calc.calculate_price_score(700, 600)
        assert score == 0.0, "Price over budget should score 0"
    
    def test_calculate_price_score_no_max_price(self):
        """Test price scoring with no max price set."""
        score = self.calc.calculate_price_score(1000, None)
        assert score == 100.0, "No max price should score 100"
    
    def test_calculate_price_score_zero_price(self):
        """Test price scoring with zero price (free item)."""
        score = self.calc.calculate_price_score(0, 600)
        assert score == 100.0, "Free item should score 100"
    
    # ========== Match Score Integration Tests ==========
    
    def test_calculate_match_score_perfect_match(self):
        """Test full score calculation with perfect match."""
        product = Product(
            title="iPhone 13",
            description="New iPhone",
            price=500
        )
        search = SearchRequest(
            product_name="iPhone 13",
            product_description="New iPhone",
            budget=600
        )
        
        score = self.calc.calculate_match_score(product, search)
        assert score >= 95, f"Perfect match should score >=95, got {score}"
    
    def test_calculate_match_score_good_match(self):
        """Test full score calculation with good match."""
        product = Product(
            title="iPhone 13 Pro 128GB",
            description="Brand new iPhone in box",
            price=550
        )
        search = SearchRequest(
            product_name="iPhone 13",
            product_description="iPhone new",
            budget=600
        )
        
        score = self.calc.calculate_match_score(product, search)
        assert 70 <= score <= 100, f"Good match should score 70-95, got {score}"
    
    def test_calculate_match_score_partial_match(self):
        """Test full score calculation with partial match."""
        product = Product(
            title="Samsung Galaxy",
            description="Phone",
            price=400
        )
        search = SearchRequest(
            product_name="iPhone",
            product_description="Phone",
            budget=600
        )
        
        score = self.calc.calculate_match_score(product, search)
        assert 20 <= score <= 65, f"Partial match should score 20-65, got {score}"
    
    def test_calculate_match_score_over_budget(self):
        """Test full score calculation when over budget."""
        product = Product(
            title="iPhone 13",
            description="New iPhone",
            price=800
        )
        search = SearchRequest(
            product_name="iPhone 13",
            product_description="New iPhone",
            budget=600
        )
        
        score = self.calc.calculate_match_score(product, search)
        # Title and description match (80%), but price fails (0%)
        # Expected: (100 * 0.4) + (100 * 0.4) + (0 * 0.2) = 80
        assert 75 <= score <= 85, f"Over budget should score 75-85, got {score}"
    
    def test_calculate_match_score_no_description(self):
        """Test full score calculation with no product description."""
        product = Product(
            title="iPhone 13",
            description=None,
            price=500
        )
        search = SearchRequest(
            product_name="iPhone 13",
            product_description="iPhone",
            budget=600
        )
        
        score = self.calc.calculate_match_score(product, search)
        # Title matches (100%), description neutral (50%), price good (100%)
        # Expected: (100 * 0.4) + (50 * 0.4) + (100 * 0.2) = 80
        assert 75 <= score <= 85, f"No description should score 75-85, got {score}"
    
    def test_calculate_match_score_no_budget(self):
        """Test full score calculation with no budget limit."""
        product = Product(
            title="iPhone 13",
            description="New iPhone",
            price=1500
        )
        search = SearchRequest(
            product_name="iPhone 13",
            product_description="New iPhone",
            budget=None
        )
        
        score = self.calc.calculate_match_score(product, search)
        assert score >= 95, f"No budget limit should score >=95, got {score}"
    
    # ========== Edge Case Tests ==========
    
    def test_calculate_match_score_empty_strings(self):
        """Test handling of empty strings."""
        product = Product(
            title="",
            description="",
            price=100
        )
        search = SearchRequest(
            product_name="iPhone",
            product_description="Phone",
            budget=200
        )
        
        score = self.calc.calculate_match_score(product, search)
        assert 0 <= score <= 100, "Score should be in valid range"
    
    def test_calculate_match_score_special_characters(self):
        """Test handling of special characters."""
        product = Product(
            title="iPhone 13 Pro!!!",
            description="Brand-new @#$ iPhone",
            price=500
        )
        search = SearchRequest(
            product_name="iPhone 13 Pro",
            product_description="Brand new iPhone",
            budget=600
        )
        
        score = self.calc.calculate_match_score(product, search)
        assert score >= 85, "Special characters should be normalized"
    
    def test_score_weights_sum_to_one(self):
        """Test that weights sum to 1.0."""
        total_weight = (
            self.calc.TITLE_WEIGHT +
            self.calc.DESCRIPTION_WEIGHT +
            self.calc.PRICE_WEIGHT
        )
        assert abs(total_weight - 1.0) < 0.001, "Weights should sum to 1.0"
    
    def test_score_always_in_range(self):
        """Test that scores are always 0-100."""
        test_cases = [
            (Product(title="A", description="B", price=100),
             SearchRequest(product_name="Z", product_description="Y", budget=50)),
            (Product(title="iPhone", description="Phone", price=500),
             SearchRequest(product_name="iPhone", product_description="Phone", budget=600)),
        ]
        
        for product, search in test_cases:
            score = self.calc.calculate_match_score(product, search)
            assert 0 <= score <= 100, f"Score {score} out of range [0, 100]"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])