"""
Unit Tests for Banking-Grade Redis Caching System

Tests cover:
- Cache storage and retrieval
- TTL expiration behavior
- Data shape preservation
- Cache invalidation
- Error handling
"""

import pytest
import time
import json
from unittest.mock import Mock, patch
import sys
import os

# Add app directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from utils.redis.redis_cache import BankingCacheManager
from utils.redis.redis_config import RedisConfig


class TestBankingCacheManager:
    """Test suite for banking-grade cache manager"""
    
    @pytest.fixture
    def cache_manager(self):
        """Create cache manager instance for testing"""
        return BankingCacheManager()
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for testing"""
        return {
            "total": 1000,
            "by_status": {"success": 800, "failed": 200},
            "timestamp": "2025-12-15T12:00:00Z"
        }
    
    def test_cache_json_success(self, cache_manager, sample_data):
        """Test successful JSON caching"""
        # Test caching with default TTL
        result = cache_manager.cache_json("test", "data1", sample_data)
        assert result is True
        
        # Test caching with custom TTL
        result = cache_manager.cache_json("test", "data2", sample_data, ttl=10)
        assert result is True
    
    def test_get_cached_json_success(self, cache_manager, sample_data):
        """Test successful cache retrieval"""
        # Cache data first
        cache_manager.cache_json("test", "retrieve", sample_data)
        
        # Retrieve cached data
        retrieved = cache_manager.get_cached_json("test", "retrieve")
        
        assert retrieved is not None
        assert retrieved["total"] == sample_data["total"]
        assert retrieved["by_status"] == sample_data["by_status"]
    
    def test_cache_miss(self, cache_manager):
        """Test cache miss behavior"""
        result = cache_manager.get_cached_json("nonexistent", "key")
        assert result is None
    
    def test_data_shape_preservation(self, cache_manager):
        """Test that complex data structures are preserved"""
        complex_data = {
            "nested": {
                "array": [1, 2, 3],
                "boolean": True,
                "null_value": None,
                "float": 123.45
            },
            "list_of_dicts": [
                {"id": 1, "name": "test1"},
                {"id": 2, "name": "test2"}
            ]
        }
        
        # Cache and retrieve
        cache_manager.cache_json("test", "complex", complex_data)
        retrieved = cache_manager.get_cached_json("test", "complex")
        
        assert retrieved == complex_data
        assert isinstance(retrieved["nested"]["array"], list)
        assert isinstance(retrieved["nested"]["boolean"], bool)
        assert retrieved["nested"]["null_value"] is None
        assert isinstance(retrieved["nested"]["float"], float)
    
    def test_cache_stats_functionality(self, cache_manager, sample_data):
        """Test stats-specific caching methods"""
        # Test cache_stats
        result = cache_manager.cache_stats("transactions", sample_data)
        assert result is True
        
        # Test get_cached_stats
        retrieved = cache_manager.get_cached_stats("transactions")
        assert retrieved == sample_data
    
    def test_cache_invalidation_specific(self, cache_manager, sample_data):
        """Test specific cache key invalidation"""
        # Cache some data
        cache_manager.cache_json("test", "invalidate_me", sample_data)
        cache_manager.cache_json("test", "keep_me", sample_data)
        
        # Verify data is cached
        assert cache_manager.get_cached_json("test", "invalidate_me") is not None
        assert cache_manager.get_cached_json("test", "keep_me") is not None
        
        # Invalidate specific key
        count = cache_manager.invalidate_cache("test", "invalidate_me")
        assert count >= 0  # Should return number of keys invalidated
        
        # Verify only specific key was invalidated
        assert cache_manager.get_cached_json("test", "invalidate_me") is None
        assert cache_manager.get_cached_json("test", "keep_me") is not None
    
    @patch('utils.redis.redis_cache.redis_client')
    def test_cache_failure_handling(self, mock_redis_client, cache_manager, sample_data):
        """Test graceful handling of Redis failures"""
        # Mock Redis failure
        mock_redis_client.safe_set_json.return_value = False
        mock_redis_client.safe_get_json.return_value = None
        
        # Test cache operation failure
        result = cache_manager.cache_json("test", "fail", sample_data)
        assert result is False
        
        # Test retrieval failure
        result = cache_manager.get_cached_json("test", "fail")
        assert result is None
    
    def test_cache_info(self, cache_manager):
        """Test cache information retrieval"""
        info = cache_manager.get_cache_info()
        assert isinstance(info, dict)
        # Should contain either valid info or error message
        assert "error" in info or "used_memory" in info
    
    @pytest.mark.integration
    def test_ttl_expiration(self, cache_manager, sample_data):
        """Integration test for TTL expiration (requires real Redis)"""
        # Cache with very short TTL
        cache_manager.cache_json("test", "expire", sample_data, ttl=1)
        
        # Should be available immediately
        assert cache_manager.get_cached_json("test", "expire") is not None
        
        # Wait for expiration
        time.sleep(2)
        
        # Should be expired
        assert cache_manager.get_cached_json("test", "expire") is None


if __name__ == "__main__":
    pytest.main([__file__])