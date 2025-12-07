"""Rate limiting middleware for FastAPI."""
from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from typing import Dict, Optional
import asyncio

# In-memory rate limit store (use Redis in production)
rate_limit_store: Dict[str, Dict] = {}


class RateLimiter:
    """
    Rate limiter with sliding window algorithm.
    
    Example:
        rate_limiter = RateLimiter(requests=100, window=60)  # 100 requests per minute
        
        @app.get("/api/products")
        async def list_products(request: Request):
            await rate_limiter.check_rate_limit(request)
            ...
    """
    
    def __init__(self, requests: int, window: int):
        """
        Initialize rate limiter.
        
        Args:
            requests: Maximum number of requests
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window
    
    def _get_client_id(self, request: Request) -> str:
        """
        Get unique client identifier.
        
        Uses IP address or authenticated user ID.
        """
        # Prefer user ID if authenticated
        if hasattr(request.state, 'user') and request.state.user:
            return f"user:{request.state.user.id}"
        
        # Fall back to IP address
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            client_ip = forwarded.split(',')[0].strip()
        else:
            client_ip = request.client.host if request.client else 'unknown'
        
        return f"ip:{client_ip}"
    
    async def check_rate_limit(self, request: Request) -> None:
        """
        Check if request exceeds rate limit.
        
        Args:
            request: FastAPI request
            
        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        client_id = self._get_client_id(request)
        now = datetime.utcnow()
        
        # Get or create client record
        if client_id not in rate_limit_store:
            rate_limit_store[client_id] = {
                'requests': [],
                'blocked_until': None
            }
        
        client_data = rate_limit_store[client_id]
        
        # Check if client is blocked
        if client_data['blocked_until'] and now < client_data['blocked_until']:
            retry_after = int((client_data['blocked_until'] - now).total_seconds())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Retry after {retry_after} seconds",
                headers={"Retry-After": str(retry_after)}
            )
        
        # Remove requests outside the window
        window_start = now - timedelta(seconds=self.window)
        client_data['requests'] = [
            req_time for req_time in client_data['requests']
            if req_time > window_start
        ]
        
        # Check rate limit
        if len(client_data['requests']) >= self.requests:
            # Block for remaining window time
            oldest_request = min(client_data['requests'])
            client_data['blocked_until'] = oldest_request + timedelta(seconds=self.window)
            retry_after = int((client_data['blocked_until'] - now).total_seconds())
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Retry after {retry_after} seconds",
                headers={"Retry-After": str(retry_after)}
            )
        
        # Add current request
        client_data['requests'].append(now)
    
    def __call__(self, requests: int, window: int):
        """Allow rate limiter to be used as decorator factory."""
        return RateLimiter(requests, window)


# Pre-configured rate limiters
rate_limiter_strict = RateLimiter(requests=10, window=60)  # 10 requests/minute
rate_limiter_moderate = RateLimiter(requests=100, window=60)  # 100 requests/minute
rate_limiter_permissive = RateLimiter(requests=1000, window=60)  # 1000 requests/minute

# Auth-specific rate limiters
rate_limiter_auth = RateLimiter(requests=5, window=300)  # 5 login attempts per 5 minutes
rate_limiter_register = RateLimiter(requests=3, window=3600)  # 3 registrations per hour


async def cleanup_rate_limit_store():
    """
    Clean up expired rate limit data.
    
    Call periodically as background task:
        @app.on_event("startup")
        @repeat_every(seconds=300)  # Every 5 minutes
        async def cleanup():
            await cleanup_rate_limit_store()
    """
    now = datetime.utcnow()
    expired_clients = []
    
    for client_id, data in rate_limit_store.items():
        # Remove if no recent requests and not blocked
        if (not data['requests'] or 
            (data['requests'] and max(data['requests']) < now - timedelta(hours=1)) and
            (not data['blocked_until'] or data['blocked_until'] < now)):
            expired_clients.append(client_id)
    
    for client_id in expired_clients:
        del rate_limit_store[client_id]


def get_rate_limit_info(request: Request, limiter: RateLimiter) -> Dict:
    """
    Get rate limit information for client.
    
    Returns:
        Dict with remaining requests and reset time
    """
    client_id = limiter._get_client_id(request)
    
    if client_id not in rate_limit_store:
        return {
            'limit': limiter.requests,
            'remaining': limiter.requests,
            'reset': int((datetime.utcnow() + timedelta(seconds=limiter.window)).timestamp())
        }
    
    client_data = rate_limit_store[client_id]
    now = datetime.utcnow()
    window_start = now - timedelta(seconds=limiter.window)
    
    # Count valid requests
    valid_requests = [
        req_time for req_time in client_data['requests']
        if req_time > window_start
    ]
    
    remaining = max(0, limiter.requests - len(valid_requests))
    reset_time = int((now + timedelta(seconds=limiter.window)).timestamp())
    
    return {
        'limit': limiter.requests,
        'remaining': remaining,
        'reset': reset_time
    }
