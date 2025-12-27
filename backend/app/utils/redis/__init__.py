"""
Banking-Grade Redis Integration Package for Transaction Reconciliation Engine

This package provides comprehensive Redis functionality including:
- Robust Redis client with connection pooling
- High-performance caching system
- Sliding-window rate limiting
- Transaction deduplication
- Centralized configuration management
"""

from .redis_client import redis_client, BankingRedisClient
from .redis_cache import cache_manager, BankingCacheManager
from .redis_rate_limiter import banking_rate_limiter, BankingRateLimiter, banking_rate_limit_middleware
from .redis_dedupe import banking_deduplicator, BankingDeduplicator
from .redis_config import redis_config, RedisConfig

__all__ = [
    # Client
    'redis_client',
    'BankingRedisClient',
    
    # Caching
    'cache_manager',
    'BankingCacheManager',
    
    # Rate Limiting
    'banking_rate_limiter',
    'BankingRateLimiter',
    'banking_rate_limit_middleware',
    
    # Deduplication
    'banking_deduplicator',
    'BankingDeduplicator',
    
    # Configuration
    'redis_config',
    'RedisConfig',
]