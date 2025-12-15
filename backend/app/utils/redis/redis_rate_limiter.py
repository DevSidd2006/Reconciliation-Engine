"""
Banking-Grade Redis Rate Limiter for Transaction Reconciliation Engine

This module implements a sophisticated sliding-window rate limiter using Redis:
- Per-endpoint rate limiting
- Sliding window algorithm with Redis sorted sets
- Fail-open design for high availability
- Comprehensive logging and monitoring
"""

import time
import logging
from datetime import datetime
from typing import Tuple
from fastapi import Request
from fastapi.responses import JSONResponse
from .redis_client import redis_client
from .redis_config import redis_config

# Configure logging
logger = logging.getLogger(__name__)


class BankingRateLimiter:
    """
    Production-grade rate limiter using Redis sliding window algorithm
    
    Features:
    - Sliding window rate limiting using Redis sorted sets
    - Per-endpoint configuration
    - Automatic cleanup of expired entries
    - Fail-open behavior for Redis unavailability
    - Detailed logging for security monitoring
    """
    
    def __init__(self):
        """Initialize rate limiter with configuration from redis_config"""
        self.client = redis_client
        self.config = redis_config
        self.global_limit = self.config.RATE_LIMIT_GLOBAL
        self.window_seconds = self.config.RATE_LIMIT_WINDOW
        self.endpoint_limits = self.config.PER_ENDPOINT_LIMITS
        
        logger.info(f"Rate limiter initialized: {self.global_limit} req/{self.window_seconds}s global")
    
    def get_endpoint_key(self, path: str) -> str:
        """
        Extract standardized endpoint key from request path
        
        Handles path parameters and query strings intelligently:
        - /transactions/123 -> /transactions
        - /transactions?limit=5 -> /transactions
        - /transactions/stats -> /transactions/stats
        
        Args:
            path: Request path from FastAPI
            
        Returns:
            Standardized endpoint key for rate limiting
        """
        # Remove query parameters
        clean_path = path.split('?')[0]
        
        # Check for exact matches first (most specific)
        if clean_path in self.endpoint_limits:
            return clean_path
        
        # Handle path parameters by checking prefixes
        for endpoint in sorted(self.endpoint_limits.keys(), key=len, reverse=True):
            if clean_path.startswith(endpoint):
                # Ensure we don't match partial paths incorrectly
                remaining = clean_path[len(endpoint):]
                if not remaining or remaining.startswith('/'):
                    return endpoint
        
        # Default to global limit
        return "global"
    
    def is_allowed(self, client_ip: str, endpoint: str) -> Tuple[bool, dict]:
        """
        Check if request is allowed using sliding window algorithm
        
        Algorithm:
        1. Remove expired timestamps from sorted set
        2. Count current requests in window
        3. If under limit, add current timestamp and allow
        4. If over limit, block and log
        
        Args:
            client_ip: Client IP address
            endpoint: Standardized endpoint key
            
        Returns:
            Tuple of (is_allowed: bool, info: dict)
        """
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        
        # Get limit for this endpoint
        limit = self.endpoint_limits.get(endpoint, self.global_limit)
        
        # Generate Redis key
        rate_key = self.config.get_rate_key(client_ip, endpoint)
        
        try:
            # Use Redis pipeline for atomic operations
            pipe = self.client.get_client().pipeline()
            
            # Remove expired timestamps
            pipe.zremrangebyscore(rate_key, 0, window_start)
            
            # Count current requests in window
            pipe.zcard(rate_key)
            
            # Execute pipeline
            results = pipe.execute()
            current_requests = results[1] if len(results) > 1 else 0
            
            # Check if request should be allowed
            if current_requests >= limit:
                # Log blocked request for security monitoring
                timestamp = datetime.now().isoformat()
                logger.warning(
                    f"RATE LIMIT BLOCKED {client_ip} {endpoint} {timestamp} "
                    f"({current_requests}/{limit} in {self.window_seconds}s)"
                )
                
                return False, {
                    "current_requests": current_requests,
                    "limit": limit,
                    "window_seconds": self.window_seconds,
                    "reset_time": current_time + self.window_seconds
                }
            
            # Add current timestamp and set expiry
            pipe = self.client.get_client().pipeline()
            pipe.zadd(rate_key, {str(current_time): current_time})
            pipe.expire(rate_key, self.window_seconds + 1)  # +1 for safety margin
            pipe.execute()
            
            logger.debug(
                f"Rate limit OK: {client_ip} {endpoint} "
                f"({current_requests + 1}/{limit} in {self.window_seconds}s)"
            )
            
            return True, {
                "current_requests": current_requests + 1,
                "limit": limit,
                "window_seconds": self.window_seconds,
                "remaining": limit - current_requests - 1
            }
            
        except Exception as e:
            # Fail-open: Allow request if Redis is unavailable
            logger.error(f"Rate limiter Redis error for {client_ip} {endpoint}: {e}")
            logger.warning(f"Rate limiter failing open due to Redis error")
            
            return True, {
                "error": "rate_limiter_unavailable",
                "fail_open": True
            }
    
    def get_rate_limit_status(self, client_ip: str, endpoint: str) -> dict:
        """
        Get current rate limit status for debugging/monitoring
        
        Args:
            client_ip: Client IP address
            endpoint: Endpoint to check
            
        Returns:
            Dictionary with current rate limit status
        """
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        limit = self.endpoint_limits.get(endpoint, self.global_limit)
        rate_key = self.config.get_rate_key(client_ip, endpoint)
        
        try:
            # Count requests in current window
            current_requests = self.client.get_client().zcount(rate_key, window_start, current_time)
            
            return {
                "endpoint": endpoint,
                "limit": limit,
                "current_requests": current_requests,
                "remaining": max(0, limit - current_requests),
                "window_seconds": self.window_seconds,
                "reset_time": current_time + self.window_seconds
            }
        except Exception as e:
            logger.error(f"Failed to get rate limit status: {e}")
            return {"error": str(e)}


# Global rate limiter instance
banking_rate_limiter = BankingRateLimiter()


async def banking_rate_limit_middleware(request: Request, call_next):
    """
    FastAPI middleware for banking-grade rate limiting
    
    Applies per-endpoint rate limits and returns structured error responses
    when limits are exceeded.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/handler in chain
        
    Returns:
        Response object (either rate limit error or normal response)
    """
    client_ip = request.client.host
    endpoint = banking_rate_limiter.get_endpoint_key(request.url.path)
    
    # Check rate limit
    is_allowed, info = banking_rate_limiter.is_allowed(client_ip, endpoint)
    
    if not is_allowed:
        # Return structured rate limit error
        return JSONResponse(
            status_code=429,
            content={
                "status": "error",
                "message": f"Rate limit exceeded for {endpoint}. Try again later.",
                "code": "RATE_LIMIT_EXCEEDED",
                "details": {
                    "endpoint": endpoint,
                    "limit": info.get("limit"),
                    "window_seconds": info.get("window_seconds"),
                    "reset_time": info.get("reset_time"),
                    "current_requests": info.get("current_requests")
                }
            },
            headers={
                "X-RateLimit-Limit": str(info.get("limit", 0)),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(info.get("reset_time", 0)),
                "Retry-After": str(info.get("window_seconds", 60))
            }
        )
    
    # Add rate limit headers to successful responses
    response = await call_next(request)
    
    if not info.get("fail_open"):
        response.headers["X-RateLimit-Limit"] = str(info.get("limit", 0))
        response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", 0))
        response.headers["X-RateLimit-Reset"] = str(info.get("reset_time", 0))
    
    return response