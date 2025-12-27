"""
Banking-Grade Redis Caching System for Transaction Reconciliation Engine

This module provides high-performance caching capabilities with:
- Structured cache key management
- TTL-based expiration strategies
- Cache invalidation patterns
- Performance monitoring
"""

import logging
from typing import Optional, Any, List
from .redis_client import redis_client
from .redis_config import redis_config

# Configure logging
logger = logging.getLogger(__name__)


class BankingCacheManager:
    """
    Production-grade caching manager for banking transaction data
    
    Features:
    - Standardized cache key patterns
    - Multiple TTL strategies
    - Bulk cache operations
    - Cache statistics and monitoring
    """
    
    def __init__(self):
        self.client = redis_client
        self.config = redis_config
    
    def cache_json(self, category: str, identifier: str, data: Any, ttl: Optional[int] = None) -> bool:
        """
        Cache JSON data with standardized key pattern
        
        Args:
            category: Cache category (e.g., 'transactions', 'mismatches')
            identifier: Unique identifier (e.g., 'stats', 'summary')
            data: Data to cache
            ttl: Time-to-live in seconds (uses CACHE_TTL_SHORT if not specified)
            
        Returns:
            True if caching successful, False otherwise
        """
        if ttl is None:
            ttl = self.config.CACHE_TTL_SHORT
        
        cache_key = self.config.get_cache_key(category, identifier)
        success = self.client.safe_set_json(cache_key, data, ttl)
        
        if success:
            logger.debug(f"Cached data for key: {cache_key} (TTL: {ttl}s)")
        else:
            logger.warning(f"Failed to cache data for key: {cache_key}")
        
        return success
    
    def get_cached_json(self, category: str, identifier: str) -> Optional[Any]:
        """
        Retrieve cached JSON data
        
        Args:
            category: Cache category
            identifier: Unique identifier
            
        Returns:
            Cached data if exists and valid, None otherwise
        """
        cache_key = self.config.get_cache_key(category, identifier)
        data = self.client.safe_get_json(cache_key)
        
        if data is not None:
            logger.debug(f"Cache HIT for key: {cache_key}")
        else:
            logger.debug(f"Cache MISS for key: {cache_key}")
        
        return data
    
    def cache_stats(self, stats_type: str, data: Any) -> bool:
        """
        Cache statistical data with short TTL for real-time updates
        
        Args:
            stats_type: Type of statistics ('transactions' or 'mismatches')
            data: Statistics data to cache
            
        Returns:
            True if caching successful, False otherwise
        """
        return self.cache_json(stats_type, "stats", data, self.config.CACHE_TTL_SHORT)
    
    def get_cached_stats(self, stats_type: str) -> Optional[Any]:
        """
        Retrieve cached statistical data
        
        Args:
            stats_type: Type of statistics to retrieve
            
        Returns:
            Cached statistics if available, None otherwise
        """
        return self.get_cached_json(stats_type, "stats")
    
    def invalidate_cache(self, category: str, identifier: Optional[str] = None) -> int:
        """
        Invalidate cache entries
        
        Args:
            category: Cache category to invalidate
            identifier: Specific identifier to invalidate (if None, invalidates all in category)
            
        Returns:
            Number of keys invalidated
        """
        if identifier:
            # Invalidate specific cache entry
            cache_key = self.config.get_cache_key(category, identifier)
            success = self.client.safe_delete(cache_key)
            count = 1 if success else 0
            logger.info(f"Invalidated cache key: {cache_key}")
        else:
            # Invalidate all entries in category (requires pattern matching)
            pattern = f"{self.config.NAMESPACE_CACHE}:{category}:*"
            try:
                keys = self.client.get_client().keys(pattern)
                if keys:
                    count = self.client.get_client().delete(*keys)
                    logger.info(f"Invalidated {count} cache keys for category: {category}")
                else:
                    count = 0
            except Exception as e:
                logger.error(f"Failed to invalidate cache for category {category}: {e}")
                count = 0
        
        return count
    
    def cache_transaction_summary(self, summary_data: Any) -> bool:
        """
        Cache transaction summary with medium TTL
        
        Args:
            summary_data: Transaction summary data
            
        Returns:
            True if caching successful, False otherwise
        """
        return self.cache_json("transactions", "summary", summary_data, self.config.CACHE_TTL_MEDIUM)
    
    def cache_mismatch_analysis(self, analysis_data: Any) -> bool:
        """
        Cache mismatch analysis with medium TTL
        
        Args:
            analysis_data: Mismatch analysis data
            
        Returns:
            True if caching successful, False otherwise
        """
        return self.cache_json("mismatches", "analysis", analysis_data, self.config.CACHE_TTL_MEDIUM)
    
    def get_cache_info(self) -> dict:
        """
        Get cache performance information
        
        Returns:
            Dictionary containing cache statistics
        """
        try:
            info = self.client.get_client().info('memory')
            return {
                "used_memory": info.get('used_memory_human', 'N/A'),
                "used_memory_peak": info.get('used_memory_peak_human', 'N/A'),
                "connected_clients": info.get('connected_clients', 0),
                "total_commands_processed": info.get('total_commands_processed', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get cache info: {e}")
            return {"error": str(e)}


# Global cache manager instance
cache_manager = BankingCacheManager()