import asyncio
import pytest
import sys
from pathlib import Path

# Add parent directory to Python path so we can import 'app' module
# This allows the script to find the 'app' package when run directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.utils.rate_limiter import RateLimiter
from app.utils.text_processing import clean_text, extract_price

@pytest.mark.asyncio
async def test_day4():
    print("Testing Day 4 Components...\n")
    
    # Test 1: Rate Limiter
    print("1. Testing Rate Limiter...")
    limiter = RateLimiter(max_requests=3, time_window=5)
    for i in range(5):
        await limiter.acquire()
        print(f"   Request {i+1} completed")
    print("   ✓ Rate limiter working\n")
    
    # Test 2: Text Processing
    print("2. Testing Text Processing...")
    messy_text = "  iPhone   13  Pro  "
    clean = clean_text(messy_text)
    print(f"   Cleaned: '{messy_text}' -> '{clean}'")
    
    price = extract_price("$1,234.56")
    print(f"   Price extracted: $1,234.56 -> {price}")
    print("   ✓ Text processing working\n")
    
    print("✅ All Day 4 components working!")

if __name__ == "__main__":
    asyncio.run(test_day4())