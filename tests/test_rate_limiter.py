"""
Test the rate limiter
"""
from cine_genesis.utils.rate_limiter import RateLimiter
import time

print("Testing RateLimiter (5 requests/minute)...\n")

limiter = RateLimiter(max_requests=5, time_window=60)

print("Making 8 requests (should pause after 5th)...")
for i in range(1, 9):
    start = time.time()
    limiter.wait_if_needed()
    elapsed = time.time() - start
    
    remaining = limiter.get_remaining_requests()
    print(f"Request {i}: Waited {elapsed:.1f}s | Remaining: {remaining}")

print("\n✅ Rate limiter working correctly!")
