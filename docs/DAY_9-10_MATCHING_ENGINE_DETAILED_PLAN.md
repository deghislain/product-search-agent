# Day 9-10: Matching Engine - Detailed Implementation Plan

A comprehensive, junior-developer-friendly breakdown of the Matching Engine implementation.

---

## 📋 Overview

**Duration:** 8 hours (2 days × 4 hours)  
**Difficulty:** Intermediate  
**Prerequisites:** 
- Understanding of text similarity algorithms
- Basic knowledge of Python classes and functions
- Familiarity with the Product and SearchRequest models

**What You'll Build:**
A smart matching engine that compares scraped products against user search criteria and assigns match scores to help users find the best deals.

---

## 🎯 Learning Objectives

By the end of Day 9-10, you will understand:
1. Text similarity algorithms (fuzzy matching)
2. Scoring systems and weighted calculations
3. Duplicate detection techniques
4. The Strategy Pattern for flexible matching algorithms
5. Unit testing for complex logic

---

## 🏗️ Architecture & Design Patterns

### Design Patterns Used

#### 1. **Strategy Pattern**
- **Why:** Allows different matching strategies (exact, fuzzy, semantic) without changing core code
- **Where:** `MatchingStrategy` base class with concrete implementations
- **Benefit:** Easy to add new matching algorithms later

#### 2. **Single Responsibility Principle**
- Each class/function has one clear purpose:
  - `ProductMatcher` - Orchestrates matching
  - `SimilarityCalculator` - Calculates text similarity
  - `DuplicateDetector` - Identifies duplicate products
  - `ScoreCalculator` - Computes final match scores

#### 3. **Dependency Injection**
- Pass dependencies (like similarity calculator) to classes
- Makes testing easier and code more flexible

---

## 📦 File Structure

```
backend/app/core/
├── __init__.py
├── matching.py              # Main matching engine
├── similarity.py            # Text similarity calculations
├── duplicate_detection.py   # Duplicate detection logic
└── scoring.py              # Score calculation logic

backend/app/tests/
└── test_matching.py        # Comprehensive tests
```

---

## 🔨 Day 9: Core Matching Logic (4 hours)

### Sub-Task 9.1: Setup & Dependencies (30 minutes)

**Goal:** Install required libraries and create file structure

**Steps:**

1. **Install RapidFuzz library** (for fuzzy text matching):
```bash
cd backend
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install rapidfuzz
```

2. **Create core directory** (if not exists):
```bash
mkdir -p app/core
touch app/core/__init__.py
```

3. **Create matching module files**:
```bash
touch app/core/matching.py
touch app/core/similarity.py
touch app/core/duplicate_detection.py
touch app/core/scoring.py
```

**Deliverable:** ✅ Files created, dependencies installed

---

### Sub-Task 9.2: Text Similarity Calculator (1 hour)

**Goal:** Build a utility to compare text strings and calculate similarity scores

**Concepts:**
- **Fuzzy Matching:** Finds similar strings even with typos (e.g., "iPhone 13" vs "iphone13")
- **Token Set Ratio:** Compares words regardless of order (e.g., "red bike" vs "bike red")

**File:** `app/core/similarity.py`

**What to Implement:**

```python
from rapidfuzz import fuzz
from typing import Optional
import re

class SimilarityCalculator:
    """
    Calculates similarity between text strings using fuzzy matching.
    
    Uses RapidFuzz library for efficient string comparison.
    """
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Clean and normalize text for comparison.
        
        Steps:
        1. Convert to lowercase
        2. Remove extra whitespace
        3. Remove special characters (keep alphanumeric and spaces)
        
        Example:
            "iPhone 13 Pro!!!" -> "iphone 13 pro"
        """
        # TODO: Implement normalization
        pass
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """
        Calculate similarity score between two texts (0-100).
        
        Uses token_set_ratio which:
        - Ignores word order
        - Handles partial matches
        - Returns score 0-100 (100 = identical)
        
        Example:
            calculate_similarity("iPhone 13", "iphone13") -> 95.0
        """
        # TODO: Implement similarity calculation
        pass
    
    @staticmethod
    def is_similar(text1: str, text2: str, threshold: float = 80.0) -> bool:
        """
        Check if two texts are similar above a threshold.
        
        Args:
            text1: First text
            text2: Second text
            threshold: Minimum similarity score (default 80%)
        
        Returns:
            True if similarity >= threshold
        """
        # TODO: Implement similarity check
        pass
```

**Implementation Tips:**
- Use `re.sub()` for removing special characters
- Use `fuzz.token_set_ratio()` from rapidfuzz
- Test with various product titles

**Test Cases to Consider:**
```python
# Exact match
assert calculate_similarity("iPhone 13", "iPhone 13") == 100

# Case insensitive
assert calculate_similarity("iPhone 13", "iphone 13") > 95

# Word order
assert calculate_similarity("red bike", "bike red") > 90

# Typos
assert calculate_similarity("iPhone", "iPhon") > 85
```

**Deliverable:** ✅ SimilarityCalculator class working with tests

---

### Sub-Task 9.3: Score Calculator (1 hour)

**Goal:** Implement the weighted scoring formula

**Scoring Formula Breakdown:**
```
Final Score = (Title Similarity × 0.40) + 
              (Description Similarity × 0.40) + 
              (Price Attractiveness × 0.20)
```

**File:** `app/core/scoring.py`

**What to Implement:**

```python
from typing import Optional
from app.models.product import Product
from app.models.search_request import SearchRequest
from app.core.similarity import SimilarityCalculator

class ScoreCalculator:
    """
    Calculates match scores for products against search criteria.
    
    Uses weighted scoring: Title (40%) + Description (40%) + Price (20%)
    """
    
    def __init__(self, similarity_calculator: SimilarityCalculator):
        self.similarity_calculator = similarity_calculator
        
        # Weights for scoring components
        self.TITLE_WEIGHT = 0.40
        self.DESCRIPTION_WEIGHT = 0.40
        self.PRICE_WEIGHT = 0.20
    
    def calculate_title_score(
        self, 
        product_title: str, 
        search_query: str
    ) -> float:
        """
        Calculate title similarity score (0-100).
        
        Compares product title against search query.
        
        Example:
            Product: "iPhone 13 Pro 128GB"
            Query: "iPhone 13"
            Score: ~85
        """
        # TODO: Use similarity_calculator
        pass
    
    def calculate_description_score(
        self,
        product_description: Optional[str],
        search_query: str
    ) -> float:
        """
        Calculate description similarity score (0-100).
        
        If no description, return 50 (neutral score).
        
        Example:
            Description: "Brand new iPhone in excellent condition"
            Query: "iPhone"
            Score: ~70
        """
        # TODO: Handle None description, use similarity_calculator
        pass
    
    def calculate_price_score(
        self,
        product_price: float,
        max_price: Optional[float]
    ) -> float:
        """
        Calculate price attractiveness score (0-100).
        
        Logic:
        - If no max_price set: return 100 (all prices acceptable)
        - If price <= max_price: return 100 (within budget)
        - If price > max_price: return 0 (over budget)
        
        Future enhancement: Could use sliding scale for prices near max
        
        Example:
            Product: $500, Max: $600 -> 100
            Product: $700, Max: $600 -> 0
        """
        # TODO: Implement price scoring logic
        pass
    
    def calculate_match_score(
        self,
        product: Product,
        search_request: SearchRequest
    ) -> float:
        """
        Calculate overall match score (0-100).
        
        Combines all scoring components with weights.
        
        Steps:
        1. Calculate title score
        2. Calculate description score
        3. Calculate price score
        4. Apply weights and sum
        5. Round to 2 decimal places
        
        Returns:
            Final weighted score (0-100)
        """
        # TODO: Calculate each component
        # TODO: Apply weights
        # TODO: Return final score
        pass
```

**Implementation Tips:**
- Handle `None` values gracefully (description, max_price)
- Use `round(score, 2)` for clean scores
- Ensure scores stay in 0-100 range

**Test Cases:**
```python
# Perfect match
product = Product(title="iPhone 13", description="New iPhone", price=500)
search = SearchRequest(query="iPhone 13", max_price=600)
# Expected: ~95-100

# Partial match
product = Product(title="Samsung Galaxy", description="Phone", price=400)
search = SearchRequest(query="iPhone", max_price=600)
# Expected: ~20-40

# Over budget
product = Product(title="iPhone 13", description="New", price=800)
search = SearchRequest(query="iPhone 13", max_price=600)
# Expected: ~60-70 (good match but expensive)
```

**Deliverable:** ✅ ScoreCalculator class with weighted scoring

---

### Sub-Task 9.4: Duplicate Detection (1.5 hours)

**Goal:** Identify duplicate products across different platforms

**Why Needed:**
- Same product may appear on Craigslist, eBay, and Facebook
- Avoid showing user the same item multiple times
- Keep the best version (highest score or most recent)

**File:** `app/core/duplicate_detection.py`

**What to Implement:**

```python
from typing import List, Set, Tuple
from app.models.product import Product
from app.core.similarity import SimilarityCalculator

class DuplicateDetector:
    """
    Detects duplicate products across different platforms.
    
    Uses title similarity and price proximity to identify duplicates.
    """
    
    def __init__(
        self,
        similarity_calculator: SimilarityCalculator,
        title_threshold: float = 85.0,
        price_tolerance: float = 0.10  # 10% price difference
    ):
        """
        Initialize duplicate detector.
        
        Args:
            similarity_calculator: For comparing titles
            title_threshold: Minimum title similarity to consider duplicate
            price_tolerance: Max price difference ratio (0.10 = 10%)
        """
        self.similarity_calculator = similarity_calculator
        self.title_threshold = title_threshold
        self.price_tolerance = price_tolerance
    
    def are_duplicates(self, product1: Product, product2: Product) -> bool:
        """
        Check if two products are duplicates.
        
        Criteria for duplicates:
        1. Titles are highly similar (>= threshold)
        2. Prices are close (within tolerance)
        3. Different platforms (same platform = different listings)
        
        Example:
            Product 1: "iPhone 13 Pro" $500 (Craigslist)
            Product 2: "iPhone 13 Pro" $510 (eBay)
            -> True (same item, 2% price diff)
        
        Returns:
            True if products are likely duplicates
        """
        # TODO: Check if same platform (not duplicates if same)
        # TODO: Calculate title similarity
        # TODO: Calculate price difference ratio
        # TODO: Return True if both criteria met
        pass
    
    def _calculate_price_difference_ratio(
        self,
        price1: float,
        price2: float
    ) -> float:
        """
        Calculate relative price difference.
        
        Formula: |price1 - price2| / max(price1, price2)
        
        Example:
            $500 vs $550 -> 0.09 (9% difference)
            $100 vs $200 -> 0.50 (50% difference)
        
        Returns:
            Ratio between 0 and 1
        """
        # TODO: Implement price difference calculation
        pass
    
    def find_duplicates(
        self,
        products: List[Product]
    ) -> List[Tuple[Product, Product]]:
        """
        Find all duplicate pairs in a list of products.
        
        Returns list of tuples, each containing two duplicate products.
        
        Example:
            Input: [prod1, prod2, prod3, prod4]
            Output: [(prod1, prod3), (prod2, prod4)]
            (prod1 and prod3 are duplicates, prod2 and prod4 are duplicates)
        """
        # TODO: Compare each product with every other product
        # TODO: Use are_duplicates() to check
        # TODO: Avoid duplicate pairs (if A-B found, don't add B-A)
        pass
    
    def remove_duplicates(
        self,
        products: List[Product],
        keep_strategy: str = "highest_score"
    ) -> List[Product]:
        """
        Remove duplicate products, keeping the best one.
        
        Args:
            products: List of products to deduplicate
            keep_strategy: Which duplicate to keep
                - "highest_score": Keep product with highest match_score
                - "most_recent": Keep most recently scraped
                - "lowest_price": Keep cheapest option
        
        Returns:
            List with duplicates removed
        """
        # TODO: Find all duplicate pairs
        # TODO: Group duplicates together
        # TODO: Apply keep_strategy to choose which to keep
        # TODO: Return deduplicated list
        pass
```

**Implementation Tips:**
- Use nested loops for comparing all pairs: `for i in range(len(products)): for j in range(i+1, len(products)):`
- Handle edge cases: empty lists, single product
- Consider using sets to track already processed products

**Test Cases:**
```python
# Clear duplicates
prod1 = Product(title="iPhone 13", price=500, platform="craigslist")
prod2 = Product(title="iPhone 13", price=505, platform="ebay")
assert are_duplicates(prod1, prod2) == True

# Different products
prod1 = Product(title="iPhone 13", price=500, platform="craigslist")
prod2 = Product(title="Samsung Galaxy", price=500, platform="ebay")
assert are_duplicates(prod1, prod2) == False

# Same platform (different listings)
prod1 = Product(title="iPhone 13", price=500, platform="craigslist")
prod2 = Product(title="iPhone 13", price=500, platform="craigslist")
assert are_duplicates(prod1, prod2) == False
```

**Deliverable:** ✅ DuplicateDetector class with comprehensive logic

---

## 🔨 Day 10: Main Matching Engine & Tests (4 hours)

### Sub-Task 10.1: Main Matching Engine (2 hours)

**Goal:** Create the main ProductMatcher class that orchestrates everything

**File:** `app/core/matching.py`

**What to Implement:**

```python
from typing import List, Optional, Dict, Any
from app.models.product import Product
from app.models.search_request import SearchRequest
from app.core.similarity import SimilarityCalculator
from app.core.scoring import ScoreCalculator
from app.core.duplicate_detection import DuplicateDetector

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
        min_score_threshold: float = 60.0,
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
        self.score_calculator = score_calculator or ScoreCalculator(self.similarity_calculator)
        self.duplicate_detector = duplicate_detector or DuplicateDetector(self.similarity_calculator)
    
    def find_matches(
        self,
        products: List[Product],
        search_request: SearchRequest,
        remove_duplicates: bool = True,
        max_results: Optional[int] = None
    ) -> List[Product]:
        """
        Find and rank product matches for a search request.
        
        Workflow:
        1. Calculate match scores for all products
        2. Filter by minimum score threshold
        3. Remove duplicates (if enabled)
        4. Sort by score (highest first)
        5. Limit results (if max_results specified)
        
        Args:
            products: List of scraped products
            search_request: User's search criteria
            remove_duplicates: Whether to deduplicate results
            max_results: Maximum number of results to return
        
        Returns:
            List of matching products, sorted by score (best first)
        """
        # TODO: Step 1 - Calculate scores
        # TODO: Step 2 - Filter by threshold
        # TODO: Step 3 - Remove duplicates
        # TODO: Step 4 - Sort by score
        # TODO: Step 5 - Limit results
        pass
    
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
        # TODO: Loop through products
        # TODO: Calculate score for each
        # TODO: Set product.match_score
        pass
    
    def get_match_statistics(
        self,
        products: List[Product],
        search_request: SearchRequest
    ) -> Dict[str, Any]:
        """
        Get statistics about matching results.
        
        Returns:
            Dictionary with statistics:
            - total_products: Total products evaluated
            - matches_found: Products above threshold
            - average_score: Average match score
            - score_distribution: Count by score ranges
            - platform_breakdown: Matches per platform
        """
        # TODO: Calculate various statistics
        # TODO: Return as dictionary
        pass
```

**Implementation Tips:**
- Use list comprehensions for filtering: `[p for p in products if p.match_score >= threshold]`
- Sort with: `products.sort(key=lambda p: p.match_score, reverse=True)`
- Handle empty lists gracefully

**Deliverable:** ✅ ProductMatcher class orchestrating the full workflow

---

### Sub-Task 10.2: Comprehensive Testing (2 hours)

**Goal:** Write thorough tests to ensure matching engine works correctly

**File:** `app/tests/test_matching.py`

**Test Categories:**

1. **Unit Tests** - Test individual components
2. **Integration Tests** - Test components working together
3. **Edge Case Tests** - Handle unusual inputs
4. **Performance Tests** - Ensure reasonable speed

**What to Implement:**

```python
import pytest
from unittest.mock import Mock, patch
from app.core.matching import ProductMatcher
from app.core.similarity import SimilarityCalculator
from app.core.scoring import ScoreCalculator
from app.core.duplicate_detection import DuplicateDetector
from app.models.product import Product
from app.models.search_request import SearchRequest

class TestSimilarityCalculator:
    """Test text similarity calculations."""
    
    def test_normalize_text(self):
        """Test text normalization."""
        calc = SimilarityCalculator()
        
        # Test cases
        assert calc.normalize_text("iPhone 13 Pro!!!") == "iphone 13 pro"
        assert calc.normalize_text("  EXTRA   SPACES  ") == "extra spaces"
        assert calc.normalize_text("Special@#$Characters") == "specialcharacters"
    
    def test_calculate_similarity(self):
        """Test similarity calculation."""
        calc = SimilarityCalculator()
        
        # Exact match
        assert calc.calculate_similarity("iPhone", "iPhone") == 100.0
        
        # Case insensitive
        score = calc.calculate_similarity("iPhone", "iphone")
        assert score > 95
        
        # Completely different
        score = calc.calculate_similarity("iPhone", "Samsung")
        assert score < 30
    
    def test_is_similar(self):
        """Test similarity threshold checking."""
        calc = SimilarityCalculator()
        
        assert calc.is_similar("iPhone 13", "iPhone 13") == True
        assert calc.is_similar("iPhone", "Samsung", threshold=80) == False

class TestScoreCalculator:
    """Test scoring calculations."""
    
    def setup_method(self):
        """Setup for each test."""
        self.similarity_calc = SimilarityCalculator()
        self.score_calc = ScoreCalculator(self.similarity_calc)
    
    def test_calculate_title_score(self):
        """Test title scoring."""
        score = self.score_calc.calculate_title_score("iPhone 13", "iPhone")
        assert 70 <= score <= 100  # Should be high similarity
    
    def test_calculate_price_score(self):
        """Test price scoring."""
        # Within budget
        assert self.score_calc.calculate_price_score(500, 600) == 100
        
        # Over budget
        assert self.score_calc.calculate_price_score(700, 600) == 0
        
        # No max price
        assert self.score_calc.calculate_price_score(1000, None) == 100
    
    def test_calculate_match_score_integration(self):
        """Test full score calculation."""
        product = Product(
            title="iPhone 13 Pro",
            description="Brand new iPhone",
            price=500,
            platform="craigslist"
        )
        
        search = SearchRequest(
            query="iPhone 13",
            max_price=600
        )
        
        score = self.score_calc.calculate_match_score(product, search)
        assert 80 <= score <= 100  # Should be high match

class TestDuplicateDetector:
    """Test duplicate detection."""
    
    def setup_method(self):
        """Setup for each test."""
        self.similarity_calc = SimilarityCalculator()
        self.detector = DuplicateDetector(self.similarity_calc)
    
    def test_are_duplicates_true(self):
        """Test duplicate detection - positive case."""
        prod1 = Product(title="iPhone 13", price=500, platform="craigslist")
        prod2 = Product(title="iPhone 13", price=510, platform="ebay")
        
        assert self.detector.are_duplicates(prod1, prod2) == True
    
    def test_are_duplicates_false_different_titles(self):
        """Test duplicate detection - different products."""
        prod1 = Product(title="iPhone 13", price=500, platform="craigslist")
        prod2 = Product(title="Samsung Galaxy", price=500, platform="ebay")
        
        assert self.detector.are_duplicates(prod1, prod2) == False
    
    def test_are_duplicates_false_same_platform(self):
        """Test duplicate detection - same platform."""
        prod1 = Product(title="iPhone 13", price=500, platform="craigslist")
        prod2 = Product(title="iPhone 13", price=500, platform="craigslist")
        
        assert self.detector.are_duplicates(prod1, prod2) == False
    
    def test_remove_duplicates(self):
        """Test duplicate removal."""
        products = [
            Product(title="iPhone 13", price=500, platform="craigslist", match_score=85),
            Product(title="iPhone 13", price=510, platform="ebay", match_score=90),
            Product(title="Samsung Galaxy", price=400, platform="facebook", match_score=75)
        ]
        
        result = self.detector.remove_duplicates(products, keep_strategy="highest_score")
        
        # Should keep 2 products (Samsung + best iPhone)
        assert len(result) == 2
        
        # Should keep the eBay iPhone (higher score)
        iphone_products = [p for p in result if "iPhone" in p.title]
        assert len(iphone_products) == 1
        assert iphone_products[0].platform == "ebay"

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
        
        search = SearchRequest(query="iPhone", max_price=600)
        
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
        
        search = SearchRequest(query="iPhone", max_price=600)
        
        matches = self.matcher.find_matches(products, search)
        assert len(matches) == 0
    
    def test_find_matches_with_duplicates(self):
        """Test duplicate removal in matching."""
        products = [
            Product(title="iPhone 13", price=500, platform="craigslist"),
            Product(title="iPhone 13", price=510, platform="ebay"),  # Duplicate
            Product(title="Samsung Galaxy", price=400, platform="facebook")
        ]
        
        search = SearchRequest(query="iPhone", max_price=600)
        
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
        
        search = SearchRequest(query="iPhone", max_price=600)
        
        matches = self.matcher.find_matches(products, search, max_results=2)
        assert len(matches) <= 2
    
    def test_get_match_statistics(self):
        """Test statistics calculation."""
        products = [
            Product(title="iPhone 13", price=500, platform="craigslist"),
            Product(title="Samsung Galaxy", price=400, platform="ebay")
        ]
        
        search = SearchRequest(query="iPhone", max_price=600)
        
        stats = self.matcher.get_match_statistics(products, search)
        
        assert "total_products" in stats
        assert "matches_found" in stats
        assert "average_score" in stats
        assert stats["total_products"] == 2

# Edge Cases and Error Handling
class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_product_list(self):
        """Test with no products."""
        matcher = ProductMatcher()
        search = SearchRequest(query="iPhone", max_price=600)
        
        matches = matcher.find_matches([], search)
        assert matches == []
    
    def test_none_values(self):
        """Test handling of None values."""
        calc = ScoreCalculator(SimilarityCalculator())
        
        # None description
        score = calc.calculate_description_score(None, "iPhone")
        assert score == 50.0  # Neutral score
        
        # None max_price
        score = calc.calculate_price_score(500, None)
        assert score == 100.0  # All prices acceptable
    
    def test_invalid_scores(self):
        """Test score bounds."""
        calc = ScoreCalculator(SimilarityCalculator())
        
        # Scores should be 0-100
        product = Product(title="Test", description="Test", price=100)
        search = SearchRequest(query="Different", max_price=50)
        
        score = calc.calculate_match_score(product, search)
        assert 0 <= score <= 100

# Performance Tests
class TestPerformance:
    """Test performance with larger datasets."""
    
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
        
        matcher = ProductMatcher()
        search = SearchRequest(query="Product", max_price=600)
        
        start_time = time.time()
        matches = matcher.find_matches(products, search)
        end_time = time.time()
        
        # Should complete within reasonable time (adjust as needed)
        assert end_time - start_time < 5.0  # 5 seconds max
        assert len(matches) > 0

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
```

**Running Tests:**
```bash
cd backend
pytest app/tests/test_matching.py -v --cov=app.core
```

**Deliverable:** ✅ Comprehensive test suite with 90%+ coverage

---

## 🎯 Integration Points

### How Matching Engine Connects to Other Components

1. **Called by Orchestrator** (`core/orchestrator.py`):
```python
# In orchestrator.py
from app.core.matching import ProductMatcher

matcher = ProductMatcher()
matches = matcher.find_matches(scraped_products, search_request)
```

2. **Uses Product Models** (`models/product.py`):
```python
# Products have match_score added
product.match_score = 85.5
```

3. **Integrates with Database** (saves match results):
```python
# Save matches to database
for match in matches:
    db.add(match)
db.commit()
```

---

## 🧪 Testing Strategy

### Test Pyramid

1. **Unit Tests (70%)**
   - Individual functions
   - Edge cases
   - Error handling

2. **Integration Tests (20%)**
   - Components working together
   - Database interactions
   - API endpoints

3. **End-to-End Tests (10%)**
   - Full workflow
   - User scenarios

### Test Data

Create realistic test data:
```python
# Good matches
IPHONE_PRODUCTS = [
    Product(title="iPhone 13 Pro Max 256GB", price=800, platform="craigslist"),
    Product(title="Apple iPhone 13 Pro", price=750, platform="ebay"),
]

# Poor matches
ANDROID_PRODUCTS = [
    Product(title="Samsung Galaxy S21", price=600, platform="facebook"),
    Product(title="Google Pixel 6", price=500, platform="craigslist"),
]

# Edge cases
EDGE_CASE_PRODUCTS = [
    Product(title="", price=0, platform="unknown"),  # Empty title
    Product(title="Very long title " * 20, price=999999, platform="test"),  # Long title
]
```

---

## 🚀 Performance Considerations

### Optimization Tips

1. **Batch Processing**
   - Process products in chunks for large datasets
   - Use generators for memory efficiency

2. **Caching**
   - Cache similarity calculations for repeated comparisons
   - Store normalized text to avoid re-processing

3. **Early Termination**
   - Skip products that obviously won't match
   - Use quick filters before expensive calculations

4. **Parallel Processing** (Future Enhancement)
   - Use multiprocessing for large product lists
   - Parallelize similarity calculations

---

## 📋 Checklist

### Day 9 Checklist
- [ ] **Sub-Task 9.1:** Dependencies installed, files created
- [ ] **Sub-Task 9.2:** SimilarityCalculator implemented and tested
- [ ] **Sub-Task 9.3:** ScoreCalculator with weighted scoring working
- [ ] **Sub-Task 9.4:** DuplicateDetector finding and removing duplicates

### Day 10 Checklist
- [ ] **Sub-Task 10.1:** ProductMatcher orchestrating full workflow
- [ ] **Sub-Task 10.2:** Comprehensive test suite passing
- [ ] **Integration:** Matching engine ready for orchestrator integration
- [ ] **Documentation:** Code commented and documented

---

## 🎓 Key Learning Outcomes

After completing Day 9-10, you will have learned:

1. **Algorithm Design**
   - Text similarity algorithms
   - Weighted scoring systems
   - Duplicate detection strategies

2. **Software Architecture**
   - Strategy pattern implementation
   - Dependency injection
   - Single responsibility principle

3. **Testing Best Practices**
   - Unit vs integration testing
   - Edge case handling
   - Performance testing

4. **Python Skills**
   - Advanced list comprehensions
   - Class design and composition
   - Error handling patterns

---

## 🔧 Troubleshooting

### Common Issues

1. **Low Similarity Scores**
   - Check text normalization
   - Adjust fuzzy matching parameters
   - Verify test data quality

2. **Performance Problems**
   - Profile with `cProfile`
   - Optimize nested loops
   - Consider caching strategies

3. **Test Failures**
   - Check floating-point comparisons (use ranges)
   - Verify mock setups
   - Ensure test data consistency

### Debug Commands
```bash
# Run specific test
pytest app/tests/test_matching.py::TestProductMatcher::test_find_matches_basic -v

# Run with coverage
pytest app/tests/test_matching.py --cov=app.core.matching --cov-report=html

# Profile performance
python -m cProfile -o profile.stats your_test_script.py
```

---

## 🎉 Success Criteria

Day 9-10 is complete when:

1. ✅ **All components implemented**
   - SimilarityCalculator working
   - ScoreCalculator with proper weights
   - DuplicateDetector removing duplicates
   - ProductMatcher orchestrating workflow

2. ✅ **Tests passing**
   - 90%+ code coverage
   - All unit tests pass
   - Integration tests working
   - Edge cases handled

3. ✅ **Performance acceptable**
   - Handles 1000+ products in <5 seconds
   - Memory usage reasonable
   - No obvious bottlenecks

4. ✅ **Ready for integration**
   - Clear API for orchestrator
   - Proper error handling
   - Well-documented code

---

## 📚 Additional Resources

### Libraries Used
- **RapidFuzz:** Fast fuzzy string matching
- **pytest:** Testing framework
- **unittest.mock:** Mocking for tests

### Further Reading
- [Fuzzy String Matching Algorithms](https://en.wikipedia.org/wiki/Approximate_string_matching)
- [Strategy Pattern in Python](https://refactoring.guru/design-patterns/strategy/python/example)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

### Next Steps
After Day 9-10, you'll move to Day 11-12: Search Orchestrator, which will use your matching engine to coordinate the entire search workflow.

---

**Good luck with your matching engine implementation! 🚀**