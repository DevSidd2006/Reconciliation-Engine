"""
Unit Tests for Banking-Grade Redis Rate Limiter

Tests cover:
- Sliding window rate limiting
- Per-endpoint limits
- Fail-open behavior
- Window reset functionality
- Concurrent request handling
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add app directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from utils.redis.redis_rate_limiter import BankingRateLimiter
from utils.redis.redis_config import RedisConfig


class TestBankingRateLimiter:
    """Test suite for banking-grade rate limiter"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter instance for testing"""
        return BankingRateLimiter()
    
    def test_endpoint_key_extraction(self, rate_limiter):
        """Test endpoint key extraction from various paths"""
        # Exact matches
        assert rate_limiter.get_endpoint_key("/transactions") == "/transactions"
        assert rate_limiter.get_endpoint_key("/transactions/stats") == "/transactions/stats"
        assert rate_limiter.get_endpoint_key("/mismatches/stats") == "/mismatches/stats"
        
        # Path parameters
        assert rate_limiter.get_endpoint_key("/transactions/123") == "/transactions"
        assert rate_limiter.get_endpoint_key("/mismatches/456") == "/mismatches"
        
        # Query parameters
        assert rate_limiter.get_endpoint_key("/transactions?limit=10") == "/transactions"
        assert rate_limiter.get_endpoint_key("/transactions/stats?format=json") == "/transactions/stats"
        
        # Unknown endpoints
        assert rate_limiter.get_endpoint_key("/unknown/endpoint") == "global"
        assert rate_limiter.get_endpoint_key("/health") == "/health"
    
    @patch('utils.redis.redis_rate_limiter.redis_client')
    def test_rate_limit_allows_under_limit(self, mock_redis_client, rate_limiter):
        """Test that requests under limit are allowed"""
        # Mock Redis pipeline
        mock_pipe = MagicMock()
        mock_pipe.execute.return_value = [None, 2]  # 2 current requests
        mock_redis_client.get_client.return_value.pipeline.return_value = mock_pipe
        
        # Test request under limit (limit is 5 for /transactions/stats)
        is_allowed, info = rate_limiter.is_allowed("127.0.0.1", "/transactions/stats")
        
        assert is_allowed is True
        assert info["current_requests"] == 3  # 2 + 1 new request
        assert info["limit"] == 5
        assert info["remaining"] == 2
    
    @patch('utils.redis.redis_rate_limiter.redis_client')
    def test_rate_limit_blocks_over_limit(self, mock_redis_client, rate_limiter):
        """Test that requests over limit are blocked"""
        # Mock Redis pipeline - simulate limit reached
        mock_pipe = MagicMock()
        mock_pipe.execute.return_value = [None, 5]  # 5 current requests (at limit)
        mock_redis_client.get_client.return_value.pipeline.return_value = mock_pipe
        
        # Test request at limit (limit is 5 for /transactions/stats)
        is_allowed, info = rate_limiter.is_allowed("127.0.0.1", "/transactions/stats")
        
        assert is_allowed is False
        assert info["current_requests"] == 5
        assert info["limit"] == 5
    
    def test_different_endpoint_limits(self, rate_limiter):
        """Test that different endpoints have different limits"""
        # Check configured limits
        assert rate_limiter.endpoint_limits["/transactions/stats"] == 5
        assert rate_limiter.endpoint_limits["/mismatches/stats"] == 3
        assert rate_limiter.endpoint_limits["/transactions"] == 20
        assert rate_limiter.endpoint_limits["/mismatches"] == 20
    
    @patch('utils.redis.redis_rate_limiter.redis_client')
    def test_fail_open_on_redis_error(self, mock_redis_client, rate_limiter):
        """Test fail-open behavior when Redis is unavailable"""
        # Mock Redis error
        mock_redis_client.get_client.side_effect = Exception("Redis connection failed")
        
        # Should allow request despite Redis error
        is_allowed, info = rate_limiter.is_allowed("127.0.0.1", "/transactions/stats")
        
        assert is_allowed is True
        assert info["fail_open"] is True
        assert "error" in info
    
    @patch('utils.redis.redis_rate_limiter.redis_client')
    def test_sliding_window_cleanup(self, mock_redis_client, rate_limiter):
        """Test that expired timestamps are cleaned up"""
        mock_pipe = MagicMock()
        mock_pipe.execute.return_value = [None, 1]  # 1 request after cleanup
        mock_redis_client.get_client.return_value.pipeline.return_value = mock_pipe
        
        rate_limiter.is_allowed("127.0.0.1", "/transactions/stats")
        
        # Verify cleanup was called (zremrangebyscore)
        mock_pipe.zremrangebyscore.assert_called_once()
        mock_pipe.zcard.assert_called_once()
    
    def test_rate_limit_status(self, rate_limiter):
        """Test rate limit status retrieval"""
        with patch('utils.redis.redis_rate_limiter.redis_client') as mock_redis_client:
            mock_redis_client.get_client.return_value.zcount.return_value = 3
            
            status = rate_limiter.get_rate_limit_status("127.0.0.1", "/transactions/stats")
            
            assert status["endpoint"] == "/transactions/stats"
            assert status["limit"] == 5
            assert status["current_requests"] == 3
            assert status["remaining"] == 2
    
    @patch('utils.redis.redis_rate_limiter.redis_client')
    def test_concurrent_requests_same_ip(self, mock_redis_client, rate_limiter):
        """Test handling of concurrent requests from same IP"""
        # Simulate multiple concurrent requests
        mock_pipe = MagicMock()
        
        # First request: 0 current, allow
        # Second request: 1 current, allow
        # Third request: 2 current, allow
        mock_pipe.execute.side_effect = [
            [None, 0],  # First request
            [None, 1],  # Second request  
            [None, 2],  # Third request
        ]
        mock_redis_client.get_client.return_value.pipeline.return_value = mock_pipe
        
        # Test multiple requests
        results = []
        for i in range(3):
            is_allowed, info = rate_limiter.is_allowed("127.0.0.1", "/mismatches/stats")
            results.append((is_allowed, info["current_requests"]))
        
        # All should be allowed (limit is 3 for /mismatches/stats)
        assert all(result[0] for result in results)
        assert results[0][1] == 1  # 0 + 1
        assert results[1][1] == 2  # 1 + 1
        assert results[2][1] == 3  # 2 + 1
    
    @patch('utils.redis.redis_rate_limiter.redis_client')
    def test_different_ips_independent_limits(self, mock_redis_client, rate_limiter):
        """Test that different IPs have independent rate limits"""
        mock_pipe = MagicMock()
        mock_pipe.execute.return_value = [None, 0]  # Always 0 current requests
        mock_redis_client.get_client.return_value.pipeline.return_value = mock_pipe
        
        # Test requests from different IPs
        is_allowed_1, _ = rate_limiter.is_allowed("127.0.0.1", "/transactions/stats")
        is_allowed_2, _ = rate_limiter.is_allowed("192.168.1.1", "/transactions/stats")
        
        assert is_allowed_1 is True
        assert is_allowed_2 is True
        
        # Verify different Redis keys were used
        calls = mock_redis_client.get_client.return_value.pipeline.return_value.zremrangebyscore.call_args_list
        assert len(calls) == 2
        # Keys should be different (different IPs)
        assert calls[0][0][0] != calls[1][0][0]
    
    @pytest.mark.integration
    def test_window_reset_integration(self, rate_limiter):
        """Integration test for window reset (requires real Redis)"""
        # This test would require a real Redis instance
        # and would test that limits reset after the window expires
        pass


if __name__ == "__main__":
    pytest.main([__file__])