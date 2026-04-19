from locale import normalize
from rapidfuzz import fuzz, utils
from typing import Optional

class SimilarityCalculator:
    """
    Calculates similarity between text strings using fuzzy matching.
    
    Uses RapidFuzz library for efficient string comparison.
    """
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Clean and normalize text for comparison.
        
        Uses RapidFuzz's built-in processor for consistent normalization.
        This is the RECOMMENDED approach as it:
        - Uses optimized C++ implementation (faster)
        - Matches RapidFuzz's internal processing
        - Ensures consistency with similarity calculations
        
        Steps performed by default_process:
        1. Convert to lowercase
        2. Remove non-alphanumeric characters (except spaces)
        3. Trim and normalize whitespace
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text string, or empty string if input is invalid
            
        Example:
            >>> SimilarityCalculator.normalize_text("iPhone 13 Pro!!!")
            'iphone 13 pro'
            >>> SimilarityCalculator.normalize_text("  EXTRA   SPACES  ")
            'extra spaces'
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Use RapidFuzz's built-in processor - BEST PRACTICE
        # This ensures our normalization matches what RapidFuzz uses internally
        normalized = utils.default_process(text)
        
        # default_process returns None for empty/invalid strings
        return normalized if normalized else ""

    
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
        normalized_text1 = SimilarityCalculator.normalize_text(text1)
        normalized_text2 = SimilarityCalculator.normalize_text(text2)
        return fuzz.token_set_ratio(normalized_text1, normalized_text2)

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
        return SimilarityCalculator.calculate_similarity(text1, text2) >= threshold