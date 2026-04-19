import pytest
from unittest.mock import Mock, patch

import sys
from pathlib import Path

# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.matching import ProductMatcher
from app.models.product import Product
from app.models.search_request import SearchRequest
from app.core.scoring import ScoreCalculator
from app.core.similarity import SimilarityCalculator


class TestProductMatcher:
    """Test main matching engine."""
    
    def setup_method(self):
        """Setup for each test."""
        self.matcher = ProductMatcher(min_score_threshold=60.0)
    
    def test_find_matches_basic(self):
        """Test basic matching workflow."""
        products = [
            Product(title="iPhone 13 Pro", price=500, platform="craigslist"),
            Product(title="Samsung Galaxy S21", price=400, platform="ebay"),
            Product(title="iPhone 12", price=300, platform="facebook")
        ]
        

        search = SearchRequest(
            product_name="iPhone",
            budget=600
        )
        
        matches = self.matcher.find_matches(products, search)
        
        # Should find iPhone products
        assert len(matches) >= 1
        
        # Should be sorted by score (highest first)
        if len(matches) > 1:
            assert matches[0].match_score >= matches[1].match_score
        
        # All matches should be above threshold
        for match in matches:
            assert match.match_score >= 60.0
    
    def test_find_matches_no_matches(self):
        """Test when no products match."""
        products = [
            Product(title="Samsung Galaxy", price=400, platform="ebay")
        ]
        
        search = SearchRequest(product_name="iPhone", budget=600)
        
        matches = self.matcher.find_matches(products, search)
        assert len(matches) == 0
   
    def test_find_matches_with_duplicates(self):
        """Test duplicate removal in matching."""
        products = [
            Product(title="iPhone 13", price=500, platform="craigslist"),
            Product(title="iPhone 13", price=510, platform="ebay"),  # Duplicate
            Product(title="Samsung Galaxy", price=400, platform="facebook")
        ]
        
        search = SearchRequest(product_name="iPhone", budget=600)
        
        matches = self.matcher.find_matches(products, search, remove_duplicates=True)
        
        # Should only have one iPhone (duplicate removed)
        iphone_matches = [m for m in matches if "iPhone" in m.title]
        assert len(iphone_matches) <= 1
    
    def test_find_matches_max_results(self):
        """Test result limiting."""
        products = [
            Product(title="iPhone 13", price=500, platform="craigslist"),
            Product(title="iPhone 12", price=400, platform="ebay"),
            Product(title="iPhone 11", price=300, platform="facebook")
        ]
        
        search = SearchRequest(product_name="iPhone", budget=600)
        
        matches = self.matcher.find_matches(products, search, max_results=2)
        assert len(matches) <= 2
    
    def test_get_match_statistics(self):
        """Test statistics calculation."""
        products = [
            Product(title="iPhone 13", price=500, platform="craigslist"),
            Product(title="Samsung Galaxy", price=400, platform="ebay")
        ]
        
        search = SearchRequest(product_name="iPhone", budget=600)
        matches =self.matcher.find_matches(products, search)
        
        stats = self.matcher.get_match_statistics(matches, search)
        
        assert "total_products" in stats
        assert "matches_found" in stats
        assert "average_score" in stats
        assert stats["total_products"] == 1


        # ==================== Test Edge Cases and Error Handling ====================


    def test_empty_product_list(self):
        """Test with no products."""
        matcher = ProductMatcher()
        search = SearchRequest(product_name="iPhone", budget=600)
        
        matches = matcher.find_matches([], search)
        assert matches == []
    
    def test_none_values(self):
        """Test handling of None values."""
        calc = ScoreCalculator()
        
        # None description
        score = calc.calculate_description_score(None, "iPhone")
        assert score == 50.0  # Neutral score
        
        # None max_price
        score = calc.calculate_price_score(500, None)
        assert score == 100.0  # All prices acceptable
    
    def test_invalid_scores(self):
        """Test score bounds."""
        calc = ScoreCalculator()
        
        # Scores should be 0-100
        product = Product(title="Test", description="Test", price=100)
        search = SearchRequest(product_name="Different", budget=50)
        
        score = calc.calculate_match_score(product, search)
        assert 0 <= score <= 100

    # ==================== Test performance with larger datasets ====================
    def test_large_product_list_performance(self):
        """Test matching with many products."""
        import time
        
        # Create 1000 products
        products = []
        for i in range(1000):
            products.append(Product(
                title=f"Product {i}",
                price=100 + i,
                platform="craigslist"
            ))
        
        matcher = ProductMatcher(min_score_threshold = 80.0)
        search = SearchRequest(product_name="Product", budget=600)
        
        start_time = time.time()
        matches = matcher.find_matches(products, search)
        end_time = time.time()
        
        # Should complete within reasonable time (adjust as needed)
        assert end_time - start_time < 5.0  # 5 seconds max
        assert len(matches) > 0
    
    def test_get_match_statistics_empty_list(self):
        """Test statistics with empty product list."""
        matcher = ProductMatcher()
        search = SearchRequest(product_name="iPhone", budget=600)
        
        stats = matcher.get_match_statistics([], search)
        
        assert stats["total_products"] == 0
        assert stats["matches_found"] == 0
        assert stats["average_score"] == 0.0
        print("\n✅ Empty list statistics tested (line 99)")
    
    def test_get_match_statistics_score_ranges(self):
        """Test statistics with products in different score ranges."""
        # Create products with specific scores to hit all ranges
        products = []
        
        # Score 0-20 range
        p1 = Product(title="Completely Different Product", price=100, platform="craigslist")
        p1.match_score = 15.0
        p1.is_match = False
        products.append(p1)
        
        # Score 21-40 range
        p2 = Product(title="Somewhat Different", price=200, platform="ebay")
        p2.match_score = 35.0
        p2.is_match = False
        products.append(p2)
        
        # Score 41-60 range
        p3 = Product(title="Moderate Match", price=300, platform="facebook")
        p3.match_score = 55.0
        p3.is_match = False
        products.append(p3)
        
        # Score 61-80 range
        p4 = Product(title="Good Match", price=400, platform="craigslist")
        p4.match_score = 75.0
        p4.is_match = False
        products.append(p4)
        
        # Score 81-100 range
        p5 = Product(title="Excellent Match", price=500, platform="ebay")
        p5.match_score = 95.0
        p5.is_match = True
        products.append(p5)
        
        matcher = ProductMatcher()
        search = SearchRequest(product_name="Test", budget=600)
        
        stats = matcher.get_match_statistics(products, search)
        
        # Verify all score ranges are counted
        assert stats["score_distribution"]["0-20"] == 1, "Line 118 not covered"
        assert stats["score_distribution"]["21-40"] == 1, "Line 120 not covered"
        assert stats["score_distribution"]["41-60"] == 1, "Line 122 not covered"
        assert stats["score_distribution"]["61-80"] == 1, "Line 124 not covered"
        assert stats["score_distribution"]["81-100"] == 1, "Line 126 not covered"
        
        # Verify platform breakdown only counts matches
        assert stats["platform_breakdown"]["ebay"] == 1, "Line 130 not covered"
        assert "craigslist" not in stats["platform_breakdown"]  # Not a match
        
        print("\n✅ All score ranges tested (lines 118, 120, 122, 126, 130)")
    