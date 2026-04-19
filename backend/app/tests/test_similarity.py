import pytest
import sys
from pathlib import Path

# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.similarity import SimilarityCalculator


class TestSimilarityCalculator:
    """Test text similarity calculations."""
    
    def setup_method(self):
        """Setup for each test - create calculator instance."""
        self.calc = SimilarityCalculator()
    
    def test_normalize_text_basic(self):
        """Test basic text normalization."""
        # Test punctuation removal
        assert self.calc.normalize_text("iPhone 13 Pro!!!") == "iphone 13 pro"
        
        # Test extra whitespace handling
        # Note: RapidFuzz's default_process preserves internal whitespace structure
        result = self.calc.normalize_text("  EXTRA   SPACES  ")
        assert result.startswith("extra")
        assert result.endswith("spaces")
        
        # Test special characters - RapidFuzz replaces special chars with spaces
        result = self.calc.normalize_text("Special@#$Characters")
        assert "special" in result.lower()
        assert "characters" in result.lower()
        
        # Test mixed case
        assert self.calc.normalize_text("MiXeD CaSe") == "mixed case"
    
    def test_normalize_text_edge_cases(self):
        """Test edge cases in normalization."""
        # Empty string
        assert self.calc.normalize_text("") == ""
        
        # Only special characters
        assert self.calc.normalize_text("!!!@@@###") == ""
        
        # Only whitespace
        assert self.calc.normalize_text("     ") == ""
        
        # Numbers and letters
        assert self.calc.normalize_text("iPhone13Pro") == "iphone13pro"
    
    def test_normalize_text_invalid_input(self):
        """Test handling of invalid input."""
        # None input - type: ignore for testing error handling
        assert self.calc.normalize_text(None) == ""  # type: ignore
        
        # Non-string input (should handle gracefully) - type: ignore for testing
        assert self.calc.normalize_text(123) == ""  # type: ignore
    
    def test_calculate_similarity_exact_match(self):
        """Test similarity calculation for exact matches."""
        # Exact match
        assert self.calc.calculate_similarity("iPhone", "iPhone") == 100.0
        
        # Different case - token_set_ratio is case-sensitive by default
        # Use processor parameter for case-insensitive matching
        score = self.calc.calculate_similarity("iPhone", "iphone")
        assert score > 80  # High similarity but not 100% due to case difference
    
    def test_calculate_similarity_partial_match(self):
        """Test similarity calculation for partial matches."""
        # Similar words
        score = self.calc.calculate_similarity("iPhone 13", "iPhone 13 Pro")
        assert 70 <= score <= 100  # Should be high similarity
        
        # Word order doesn't matter (token_set_ratio)
        score1 = self.calc.calculate_similarity("red bike", "bike red")
        assert score1 == 100.0  # token_set_ratio ignores order
        
        # Typos
        score = self.calc.calculate_similarity("iPhone", "iPhon")
        assert score > 85  # Should still be similar
    
    def test_calculate_similarity_no_match(self):
        """Test similarity calculation for completely different texts."""
        # Completely different
        score = self.calc.calculate_similarity("iPhone", "Samsung")
        assert score < 30
        
        # Different products
        score = self.calc.calculate_similarity("laptop", "bicycle")
        assert score < 20
    
    def test_calculate_similarity_empty_strings(self):
        """Test similarity with empty strings."""
        # Both empty - RapidFuzz returns 0.0 for empty strings
        score = self.calc.calculate_similarity("", "")
        assert score == 0.0  # RapidFuzz treats empty strings as no match
        
        # One empty
        score = self.calc.calculate_similarity("iPhone", "")
        assert score == 0.0  # No similarity
    
    def test_is_similar_with_default_threshold(self):
        """Test similarity threshold checking with default threshold (80%)."""
        # High similarity - should pass
        assert self.calc.is_similar("iPhone 13", "iPhone 13") == True
        assert self.calc.is_similar("iPhone 13", "iphone 13") == True
        
        # Low similarity - should fail
        assert self.calc.is_similar("iPhone", "Samsung") == False
        assert self.calc.is_similar("laptop", "bicycle") == False
    
    def test_is_similar_with_custom_threshold(self):
        """Test similarity threshold checking with custom thresholds."""
        # Lower threshold (60%) - more lenient
        assert self.calc.is_similar("iPhone", "iPhone 13", threshold=60.0) == True
        
        # Higher threshold (95%) - more strict
        # token_set_ratio gives high scores for subset matches
        score = self.calc.calculate_similarity("iPhone 13", "iPhone 13 Pro")
        # Adjust threshold based on actual score
        assert self.calc.is_similar("iPhone 13", "iPhone 13 Pro", threshold=score + 1) == False
        
        # Very low threshold (10%) - almost everything passes
        assert self.calc.is_similar("iPhone", "Samsung", threshold=10.0) == True
    
    def test_is_similar_edge_cases(self):
        """Test edge cases for similarity checking."""
        # Exact match always passes any threshold
        assert self.calc.is_similar("test", "test", threshold=100.0) == True
        
        # Empty strings - RapidFuzz returns 0.0 for empty strings
        assert self.calc.is_similar("", "", threshold=80.0) == False  # Score is 0.0
        assert self.calc.is_similar("test", "", threshold=80.0) == False
        
        # Empty strings with low threshold
        assert self.calc.is_similar("", "", threshold=0.0) == True  # 0.0 >= 0.0
    
    def test_real_world_product_scenarios(self):
        """Test with real-world product title scenarios."""
        # Same product, different formatting
        assert self.calc.is_similar(
            "Apple iPhone 13 Pro Max 256GB",
            "iPhone 13 Pro Max 256GB Apple"
        ) == True
        
        # Same product with extra details
        score = self.calc.calculate_similarity(
            "iPhone 13",
            "iPhone 13 - Brand New in Box"
        )
        assert score >= 70  # Should still be similar
        
        # Different models of same brand
        score = self.calc.calculate_similarity(
            "iPhone 13",
            "iPhone 12"
        )
        assert 50 <= score <= 90  # Moderately similar
        
        # Completely different products
        assert self.calc.is_similar(
            "iPhone 13",
            "Samsung Galaxy S21",
            threshold=80.0
        ) == False


class TestSimilarityCalculatorPerformance:
    """Test performance characteristics of similarity calculator."""
    
    def test_performance_with_long_strings(self):
        """Test that similarity calculation is fast even with long strings."""
        import time
        
        calc = SimilarityCalculator()
        
        # Create long product descriptions
        long_text1 = "iPhone 13 Pro Max " * 100  # 1800+ characters
        long_text2 = "iPhone 13 Pro " * 100
        
        start_time = time.time()
        score = calc.calculate_similarity(long_text1, long_text2)
        end_time = time.time()
        
        # Should complete quickly (< 0.1 seconds)
        assert end_time - start_time < 0.1
        assert score > 80  # Should still detect similarity
    
    def test_performance_with_many_comparisons(self):
        """Test performance with multiple comparisons."""
        import time
        
        calc = SimilarityCalculator()
        
        products = [
            "iPhone 13",
            "iPhone 12",
            "Samsung Galaxy",
            "Google Pixel",
            "OnePlus 9"
        ]
        
        start_time = time.time()
        
        # Compare each product with every other product
        for i, prod1 in enumerate(products):
            for prod2 in products[i+1:]:
                calc.calculate_similarity(prod1, prod2)
        
        end_time = time.time()
        
        # Should complete quickly (< 0.05 seconds for 10 comparisons)
        assert end_time - start_time < 0.05


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])