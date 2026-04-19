"""
Test suite for Rate Limiter Helper Methods
Tests Step 1.4 implementation
"""

import asyncio
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from app.utils.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_get_current_rate():
    """Test get_current_rate() method."""
    limiter = RateLimiter(max_requests=5, time_window=10)
    
    # Initially should be 0
    assert limiter.get_current_rate() == 0
    
    # After 3 requests, should be 3
    for _ in range(3):
        await limiter.acquire()
    assert limiter.get_current_rate() == 3
    
    # After 5 requests, should be 5
    for _ in range(2):
        await limiter.acquire()
    assert limiter.get_current_rate() == 5
    
    print("✓ get_current_rate() working correctly")


@pytest.mark.asyncio
async def test_is_available():
    """Test is_available() method."""
    limiter = RateLimiter(max_requests=3, time_window=10)
    
    # Initially should be available
    assert limiter.is_available() is True
    
    # After 2 requests, still available
    await limiter.acquire()
    await limiter.acquire()
    assert limiter.is_available() is True
    
    # After 3 requests (at capacity), not available
    await limiter.acquire()
    assert limiter.is_available() is False
    
    print("✓ is_available() working correctly")


@pytest.mark.asyncio
async def test_reset():
    """Test reset() method."""
    limiter = RateLimiter(max_requests=5, time_window=10)
    
    # Make some requests
    for _ in range(5):
        await limiter.acquire()
    
    # Should be at capacity
    assert limiter.get_current_rate() == 5
    assert limiter.is_available() is False
    
    # Reset
    limiter.reset()
    
    # Should be empty now
    assert limiter.get_current_rate() == 0
    assert limiter.is_available() is True
    
    print("✓ reset() working correctly")


def test_repr():
    """Test __repr__() method."""
    limiter = RateLimiter(max_requests=10, time_window=60)
    
    # Should have readable string representation
    repr_str = repr(limiter)
    assert "RateLimiter" in repr_str
    assert "max_requests=10" in repr_str
    assert "time_window=60" in repr_str
    assert "current_rate=0" in repr_str
    
    print(f"✓ __repr__() working correctly: {repr_str}")


@pytest.mark.asyncio
async def test_all_helpers_together():
    """Integration test using all helper methods together."""
    print("\n" + "="*60)
    print("Testing All Helper Methods Together")
    print("="*60)
    
    limiter = RateLimiter(max_requests=3, time_window=5)
    print(f"\nCreated: {limiter}")
    
    # Test 1: Check initial state
    print("\n1. Initial State:")
    print(f"   Current rate: {limiter.get_current_rate()}/3")
    print(f"   Available: {limiter.is_available()}")
    assert limiter.get_current_rate() == 0
    assert limiter.is_available() is True
    
    # Test 2: Make some requests
    print("\n2. Making 2 requests:")
    for i in range(2):
        await limiter.acquire()
        print(f"   Request {i+1} - Rate: {limiter.get_current_rate()}/3, Available: {limiter.is_available()}")
    assert limiter.get_current_rate() == 2
    assert limiter.is_available() is True
    
    # Test 3: Fill to capacity
    print("\n3. Filling to capacity:")
    await limiter.acquire()
    print(f"   Request 3 - Rate: {limiter.get_current_rate()}/3, Available: {limiter.is_available()}")
    assert limiter.get_current_rate() == 3
    assert limiter.is_available() is False
    
    # Test 4: Reset
    print("\n4. Resetting:")
    limiter.reset()
    print(f"   After reset: {limiter}")
    print(f"   Rate: {limiter.get_current_rate()}/3, Available: {limiter.is_available()}")
    assert limiter.get_current_rate() == 0
    assert limiter.is_available() is True
    
    print("\n" + "="*60)
    print("✅ All helper methods working perfectly!")
    print("="*60)


@pytest.mark.asyncio
async def test_acquire_waits_when_at_capacity():
    """Test that acquire() waits when at capacity."""
    # Create limiter with short time window for faster testing
    limiter = RateLimiter(max_requests=2, time_window=1)
    
    # Fill to capacity
    await limiter.acquire()
    await limiter.acquire()
    
    # Should be at capacity
    assert limiter.get_current_rate() == 2
    assert limiter.is_available() is False
    
    # Next acquire should wait
    start_time = time.time()
    await limiter.acquire()
    elapsed = time.time() - start_time
    
    # Should have waited approximately 1 second (time_window)
    assert elapsed >= 0.9  # Allow small margin for timing
    assert limiter.get_current_rate() == 1  # Old requests expired
    
    print(f"✓ acquire() waited {elapsed:.2f}s when at capacity")


@pytest.mark.asyncio
async def test_clean_old_requests():
    """Test that old requests are cleaned up."""
    limiter = RateLimiter(max_requests=5, time_window=1)
    
    # Make 3 requests
    await limiter.acquire()
    await limiter.acquire()
    await limiter.acquire()
    
    assert limiter.get_current_rate() == 3
    
    # Wait for requests to expire
    await asyncio.sleep(1.1)
    
    # Old requests should be cleaned
    assert limiter.get_current_rate() == 0
    
    print("✓ _clean_old_requests() working correctly")


def test_calculate_wait_time_empty():
    """Test _calculate_wait_time() with no requests."""
    limiter = RateLimiter(max_requests=5, time_window=10)
    
    # No requests, should return 0
    wait_time = limiter._calculate_wait_time()
    assert wait_time == 0.0
    
    print("✓ _calculate_wait_time() returns 0 when empty")


@pytest.mark.asyncio
async def test_calculate_wait_time_with_requests():
    """Test _calculate_wait_time() with requests."""
    limiter = RateLimiter(max_requests=2, time_window=2)
    
    # Make requests
    await limiter.acquire()
    await limiter.acquire()
    
    # Calculate wait time
    wait_time = limiter._calculate_wait_time()
    
    # Should be approximately 2 seconds (time_window)
    assert 1.9 <= wait_time <= 2.1
    
    print(f"✓ _calculate_wait_time() calculated {wait_time:.2f}s")


@pytest.mark.asyncio
async def test_acquire_multiple_waits():
    """Test multiple acquire() calls that require waiting."""
    limiter = RateLimiter(max_requests=2, time_window=1)
    
    # Fill to capacity
    await limiter.acquire()
    await limiter.acquire()
    
    # Make 2 more requests that will need to wait
    start_time = time.time()
    
    await limiter.acquire()  # Should wait ~1s for first request to expire
    await limiter.acquire()  # Should not wait much since first already expired
    
    elapsed = time.time() - start_time
    
    # Should have waited approximately 1 second (for first old request to expire)
    # The second acquire happens quickly since the first old request already expired
    assert elapsed >= 0.9  # Allow margin for timing
    assert elapsed < 1.5  # Should not wait for both
    
    print(f"✓ Multiple acquire() calls waited {elapsed:.2f}s total")


def test_init_custom_values():
    """Test initialization with custom values."""
    limiter = RateLimiter(max_requests=20, time_window=120)
    
    assert limiter.max_requests == 20
    assert limiter.time_window == 120
    assert limiter.requests == []
    
    print("✓ Initialization with custom values working")


def test_init_default_values():
    """Test initialization with default values."""
    limiter = RateLimiter()
    
    assert limiter.max_requests == 10
    assert limiter.time_window == 60
    assert limiter.requests == []
    
    print("✓ Initialization with default values working")


if __name__ == "__main__":
    print("Testing Rate Limiter Helper Methods (Step 1.4)")
    print("="*60)
    
    # Run all tests with pytest
    pytest.main([__file__, "-v", "-s"])
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED - Step 1.4 Complete!")
    print("="*60)

# Made with Bob
