import re
import html
from typing import Optional

def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
        
    Example:
        >>> clean_text("  Hello   World  ")
        "Hello World"
    """
    if not text:
        return ""
    
    # Decode HTML entities (& -> &)
    text = html.unescape(text)
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def extract_price(text: str) -> Optional[float]:
    """
    Extract price from text.
    
    Args:
        text: Text containing price
        
    Returns:
        Price as float, or None if not found
        
    Example:
        >>> extract_price("$1,234.56")
        1234.56
    """
    if not text:
        return None
    
    # Remove currency symbols and commas
    text = re.sub(r'[$,]', '', text)
    
    # Find first number (with optional decimal)
    match = re.search(r'\d+\.?\d*', text)
    
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    
    return None

def normalize_text(text: str) -> str:
    """
    Normalize text for comparison (lowercase, remove punctuation).
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
        
    Example:
        >>> normalize_text("iPhone 13 Pro!!!")
        "iphone 13 pro"
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation except spaces
    text = re.sub(r'[^\w\s]', '', text)
    
    # Clean whitespace
    text = " ".join(text.split())
    
    return text

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].strip() + suffix

def extract_numbers(text: str) -> list:
    """
    Extract all numbers from text.
    
    Args:
        text: Text to search
        
    Returns:
        List of numbers found
        
    Example:
        >>> extract_numbers("iPhone 13 Pro 256GB for $999")
        [13, 256, 999]
    """
    if not text:
        return []
    
    return [int(n) for n in re.findall(r'\d+', text)]





if __name__ == "__main__":
    # Test clean_text
    assert clean_text("  Hello   World  ") == "Hello World"
    print("✓ clean_text works")
    
    # Test extract_price
    assert extract_price("$1,234.56") == 1234.56
    assert extract_price("Price: $50") == 50.0
    print("✓ extract_price works")
    
    # Test normalize_text
    assert normalize_text("iPhone 13 Pro!!!") == "iphone 13 pro"
    print("✓ normalize_text works")
    
    print("\n✅ All text processing functions working!")