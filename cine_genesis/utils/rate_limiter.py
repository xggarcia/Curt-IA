"""
Rate limiter for API requests
"""
import time
from collections import deque
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter to prevent API quota exceeded errors
    Tracks requests and enforces waiting periods
    """
    
    def __init__(self, max_requests: int = 5, time_window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests allowed in the time window
            time_window: Time window in seconds (default: 60 = 1 minute)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_times = deque()
        
    def wait_if_needed(self):
        """
        Check if we need to wait before making a request
        Automatically sleeps if rate limit would be exceeded
        """
        current_time = time.time()
        
        # Remove requests older than the time window
        while self.request_times and current_time - self.request_times[0] > self.time_window:
            self.request_times.popleft()
        
        # Check if we've hit the limit
        if len(self.request_times) >= self.max_requests:
            # Calculate how long to wait
            oldest_request = self.request_times[0]
            wait_time = self.time_window - (current_time - oldest_request)
            
            if wait_time > 0:
                logger.info(
                    f"⏱️  Rate limit reached ({self.max_requests} requests/{self.time_window}s). "
                    f"Waiting {wait_time:.1f} seconds..."
                )
                time.sleep(wait_time + 0.5)  # Add 0.5s buffer
                
                # Clean up again after waiting
                current_time = time.time()
                while self.request_times and current_time - self.request_times[0] > self.time_window:
                    self.request_times.popleft()
        
        # Record this request
        self.request_times.append(time.time())
        
    def get_remaining_requests(self) -> int:
        """
        Get number of requests remaining in current window
        
        Returns:
            Number of requests available
        """
        current_time = time.time()
        
        # Remove old requests
        while self.request_times and current_time - self.request_times[0] > self.time_window:
            self.request_times.popleft()
        
        return max(0, self.max_requests - len(self.request_times))
    
    def reset(self):
        """Reset the rate limiter"""
        self.request_times.clear()
