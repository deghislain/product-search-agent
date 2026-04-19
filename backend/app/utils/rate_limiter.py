"""
Rate Limiter Module

This module provides a rate limiting utility to control the frequency of requests
to external services, preventing overwhelming servers and avoiding being blocked.

The RateLimiter uses a sliding window algorithm to track requests over time.
"""

import time
import asyncio
from typing import List


class RateLimiter:
    """
    Controls the rate of requests to prevent overwhelming servers.
    
    Uses a sliding window algorithm where requests are tracked by timestamp.
    When the maximum number of requests is reached within the time window,
    new requests must wait until older requests expire.
    
    Example:
        >>> limiter = RateLimiter(max_requests=10, time_window=60)
        >>> await limiter.acquire()  # Wait if needed, then proceed
        >>> # Make your request here
        
    Attributes:
        max_requests: Maximum number of requests allowed in the time window
        time_window: Time window in seconds
        requests: List of timestamps for recent requests
    """
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the time window.
                         Default is 10 requests.
            time_window: Time window in seconds. Default is 60 seconds.
                        
        Example:
            >>> # Allow 5 requests per 10 seconds
            >>> limiter = RateLimiter(max_requests=5, time_window=10)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[float] = []  # Store timestamps of requests
        
    async def acquire(self) -> None:
        """
        Wait if necessary, then allow request to proceed.
        
        This is the main method you'll call before making requests.
        It will:
        1. Clean up old requests outside the time window
        2. Check if we're at capacity
        3. If at capacity, wait until the oldest request expires
        4. Record the new request timestamp
        
        This method is async and should be awaited.
        
        Example:
            >>> limiter = RateLimiter(max_requests=5, time_window=10)
            >>> await limiter.acquire()
            >>> # Now safe to make request
        """
        # Remove requests that are outside our time window
        self._clean_old_requests()
        
        # If we're at max capacity, we need to wait
        if len(self.requests) >= self.max_requests:
            wait_time = self._calculate_wait_time()
            if wait_time > 0:
                # Wait until the oldest request expires
                await asyncio.sleep(wait_time)
                # Clean again after waiting
                self._clean_old_requests()
        
        # Record this request
        self.requests.append(time.time())
    
    def _clean_old_requests(self) -> None:
        """
        Remove requests older than the time window.
        
        This method filters out timestamps that are older than
        (current_time - time_window), keeping only recent requests.
        
        Example:
            If time_window is 60 seconds and current time is 1000,
            this will remove all requests with timestamp < 940.
        """
        current_time = time.time()
        cutoff_time = current_time - self.time_window
        
        # Keep only requests within the time window
        self.requests = [
            req_time for req_time in self.requests 
            if req_time > cutoff_time
        ]
    
    def _calculate_wait_time(self) -> float:
        """
        Calculate how long to wait before the next request can be made.
        
        Returns the time in seconds until the oldest request expires
        from the time window, allowing a new request to be made.
        
        Returns:
            float: Number of seconds to wait. Returns 0 if no wait needed.
            
        Example:
            If the oldest request was made 50 seconds ago and time_window
            is 60 seconds, this returns 10 (need to wait 10 more seconds).
        """
        if not self.requests:
            return 0.0
        
        # Get the oldest request timestamp
        oldest_request = min(self.requests)
        current_time = time.time()
        
        # Calculate when the oldest request will expire
        expiry_time = oldest_request + self.time_window
        
        # Calculate wait time (how long until oldest request expires)
        wait_time = expiry_time - current_time
        
        # Return wait time, but never negative
        return max(0.0, wait_time)
    
    def get_current_rate(self) -> int:
        """
        Get the number of requests in the current time window.
        
        This is useful for monitoring and debugging to see how many
        requests have been made recently.
        
        Returns:
            int: Number of requests in the current time window
            
        Example:
            >>> limiter = RateLimiter(max_requests=10, time_window=60)
            >>> await limiter.acquire()
            >>> print(f"Current rate: {limiter.get_current_rate()}/10")
            Current rate: 1/10
        """
        self._clean_old_requests()
        return len(self.requests)
    
    def is_available(self) -> bool:
        """
        Check if a request can be made immediately without waiting.
        
        Returns:
            bool: True if a request can be made now, False if at capacity
            
        Example:
            >>> limiter = RateLimiter(max_requests=5, time_window=10)
            >>> if limiter.is_available():
            ...     await limiter.acquire()
            ...     # Make request
        """
        self._clean_old_requests()
        return len(self.requests) < self.max_requests
    
    def reset(self) -> None:
        """
        Reset the rate limiter by clearing all request history.
        
        This is useful for testing or when you want to start fresh.
        
        Example:
            >>> limiter.reset()
            >>> print(limiter.get_current_rate())
            0
        """
        self.requests.clear()
    
    def __repr__(self) -> str:
        """
        String representation of the RateLimiter.
        
        Returns:
            str: Human-readable representation
        """
        return (
            f"RateLimiter(max_requests={self.max_requests}, "
            f"time_window={self.time_window}s, "
            f"current_rate={self.get_current_rate()})"
        )


# Test code - runs when file is executed directly
if __name__ == "__main__":
    async def test_rate_limiter():
        """Test the rate limiter with a simple example."""
        print("=" * 60)
        print("Testing Rate Limiter")
        print("=" * 60)
        print()
        
        # Create a rate limiter: 5 requests per 10 seconds
        limiter = RateLimiter(max_requests=5, time_window=10)
        print(f"Created: {limiter}")
        print(f"Configuration: {limiter.max_requests} requests per {limiter.time_window} seconds")
        print()
        
        print("Making 10 requests...")
        print("(First 5 should be instant, next 5 should wait)")
        print("-" * 60)
        
        start_time = time.time()
        
        for i in range(10):
            request_start = time.time()
            print(f"\nRequest {i+1}...")
            print(f"  Time elapsed: {request_start - start_time:.2f}s")
            print(f"  Current rate before: {limiter.get_current_rate()}/{limiter.max_requests}")
            print(f"  Available: {limiter.is_available()}")
            
            # Acquire permission to make request
            await limiter.acquire()
            
            request_end = time.time()
            wait_time = request_end - request_start
            
            print(f"  ✓ Request {i+1} completed")
            print(f"  Wait time: {wait_time:.2f}s")
            print(f"  Current rate after: {limiter.get_current_rate()}/{limiter.max_requests}")
        
        total_time = time.time() - start_time
        print()
        print("-" * 60)
        print(f"✅ All 10 requests completed in {total_time:.2f} seconds")
        print()
        print("Expected behavior:")
        print("  - First 5 requests: instant (0s wait)")
        print("  - Next 5 requests: ~10s wait each")
        print("  - Total time: ~50 seconds")
        print()
        
        # Test reset
        print("Testing reset...")
        limiter.reset()
        print(f"  After reset: {limiter}")
        print(f"  ✓ Reset successful")
        print()
        print("=" * 60)
    
    # Run the test
    asyncio.run(test_rate_limiter())

# Made with Bob
