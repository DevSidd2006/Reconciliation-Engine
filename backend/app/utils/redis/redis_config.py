"""
Redis Configuration Module for Banking-Grade Transaction Reconciliation Engine

This module centralizes all Redis configuration settings including:
- Connection parameters
- Rate limiting configuration
- Cache TTL settings
- Deduplication settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)


class RedisConfig:
    """Centralized Redis configuration for the banking reconciliation system"""
    
    # Connection Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Rate Limiting Configuration
    RATE_LIMIT_GLOBAL: int = int(os.getenv("RATE_LIMIT_GLOBAL", 20))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", 10))
    
    # Per-Endpoint Rate Limits (requests per window)
    PER_ENDPOINT_LIMITS: Dict[str, int] = {
        "/transactions": 20,
        "/transactions/stats": 5,
        "/mismatches/stats": 3,
        "/mismatches": 20,
        "/health": 100,  # Health checks should have higher limits
        "/": 100,
    }
    
    # Cache TTL Settings (in seconds)
    CACHE_TTL_SHORT: int = 5      # For frequently changing stats
    CACHE_TTL_MEDIUM: int = 30    # For moderately changing data
    CACHE_TTL_LONG: int = 300     # For rarely changing data
    
    # Deduplication TTL Settings (in seconds)
    DEDUPE_TTL_INFLIGHT: int = 60    # How long to track in-flight transactions
    DEDUPE_TTL_PROCESSED: int = 3600  # How long to remember processed transactions
    
    # Redis Key Namespaces
    NAMESPACE_CACHE: str = "cache"
    NAMESPACE_RATE: str = "rate"
    NAMESPACE_DEDUPE: str = "dedupe"
    NAMESPACE_INFLIGHT: str = "inflight"
    
    @classmethod
    def get_cache_key(cls, category: str, identifier: str) -> str:
        """Generate standardized cache key"""
        return f"{cls.NAMESPACE_CACHE}:{category}:{identifier}"
    
    @classmethod
    def get_rate_key(cls, ip: str, endpoint: str) -> str:
        """Generate standardized rate limiting key"""
        return f"{cls.NAMESPACE_RATE}:{ip}:{endpoint}"
    
    @classmethod
    def get_dedupe_key(cls, txn_id: str, source: str) -> str:
        """Generate standardized deduplication key"""
        return f"{cls.NAMESPACE_DEDUPE}:{txn_id}:{source}"
    
    @classmethod
    def get_inflight_key(cls, txn_id: str, source: str) -> str:
        """Generate standardized in-flight tracking key"""
        return f"{cls.NAMESPACE_INFLIGHT}:{txn_id}:{source}"


# Global configuration instance
redis_config = RedisConfig()