"""Rate limiting utilities for API calls."""

import asyncio
import time
from typing import Dict, Optional, Callable, Any
from collections import defaultdict
from utils.advanced_logging import get_logger

logger = get_logger(__name__)

class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.calls: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def acquire(self, key: str = "default") -> bool:
        """Acquire permission to make an API call."""
        async with self.lock:
            now = time.time()
            minute_ago = now - 60
            
            # Clean old calls
            self.calls[key] = [call_time for call_time in self.calls[key] 
                             if call_time > minute_ago]
            
            # Check if we can make a call
            if len(self.calls[key]) < self.calls_per_minute:
                self.calls[key].append(now)
                return True
            
            return False
    
    async def wait_and_acquire(self, key: str = "default", timeout: float = 60.0) -> bool:
        """Wait for rate limit and acquire permission."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await self.acquire(key):
                return True
            
            # Wait a bit before trying again
            await asyncio.sleep(1)
        
        logger.warning(f"Rate limit timeout for key: {key}")
        return False

class APIRateLimiter:
    """Rate limiter for different API endpoints."""
    
    def __init__(self):
        self.limiters = {
            "openai": RateLimiter(60),  # 60 calls per minute
            "twitter": RateLimiter(300),  # 300 calls per 15 minutes
            "reddit": RateLimiter(60),  # 60 calls per minute
            "telegram": RateLimiter(30),  # 30 calls per minute
            "newsapi": RateLimiter(100),  # 100 calls per day
            "coingecko": RateLimiter(50),  # 50 calls per minute
        }
    
    async def acquire(self, api_name: str) -> bool:
        """Acquire permission for a specific API."""
        limiter = self.limiters.get(api_name)
        if not limiter:
            logger.warning(f"No rate limiter configured for API: {api_name}")
            return True
        
        return await limiter.acquire()
    
    async def wait_and_acquire(self, api_name: str, timeout: float = 60.0) -> bool:
        """Wait for rate limit and acquire permission for a specific API."""
        limiter = self.limiters.get(api_name)
        if not limiter:
            logger.warning(f"No rate limiter configured for API: {api_name}")
            return True
        
        return await limiter.wait_and_acquire(timeout=timeout)

def rate_limited(api_name: str, timeout: float = 60.0):
    """Decorator for rate limiting API calls."""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs) -> Any:
            limiter = APIRateLimiter()
            
            if not await limiter.wait_and_acquire(api_name, timeout):
                raise Exception(f"Rate limit exceeded for {api_name}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Global rate limiter instance
api_limiter = APIRateLimiter() 