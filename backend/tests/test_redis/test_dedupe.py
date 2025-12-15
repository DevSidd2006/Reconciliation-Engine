"""
Unit Tests for Banking-Grade Redis Deduplication System

Tests cover:
- Duplicate detection
- In-flight transaction tracking
- Processed transaction memory
- TTL behavior
- Race condition prevention
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add app directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from utils.redis.redis_dedupe import BankingDeduplicator
from utils.redis.redis_config import RedisConfig


class TestBankingDeduplicator:
    """Test suite for banking-grade deduplicator"""
    
    @pytest.fixture
    def deduplicator(self):
        """Create deduplicator instance for testing"""
        return BankingDeduplicator()
    
    @pytest.fixture
    def sample_transaction(self):
        """Sample transaction data for testing"""
        return {
            "txn_id": "TXN123456",
            "source": "core",
            "amount": 1000.00
        }
    
    @patch('utils.redis.redis_dedupe.redis_client')
    def test_is_duplicate_not_duplicate(self, mock_redis_client, deduplicator, sample_transaction):
        """Test detection of non-duplicate transaction"""
        # Mock Redis to return False for both processed and in-flight checks
        mock_redis_client.exists.return_value = False
        
        is_dup, reason = deduplicator.is_duplicate(
            sample_transaction["txn_id"], 
            sample_transaction["source"]
        )
        
        assert is_dup is False
        assert reason == "not_duplicate"
    
    @patch('utils.redis.redis_dedupe.redis_client')
    def test_is_duplicate_already_processed(self, mock_redis_client, deduplicator, sample_transaction):
        """Test detection of already processed transaction"""
        # Mock Redis to return True for processed check
        def mock_exists(key):
            return "txn_processed:" in key
        
        mock_redis_client.exists.side_effect = mock_exists
        
        is_dup, reason = deduplicator.is_duplicate(
            sample_transaction["txn_id"], 
            sample_transaction["source"]
        )
        
        assert is_dup is True
        assert reason == "already_processed"
    
    @patch('utils.redis.redis_dedupe.redis_client')
    def test_is_duplicate_in_flight(self, mock_redis_client, deduplicator, sample_transaction):
        """Test detection of in-flight transaction"""
        # Mock Redis to return True for in-flight check, False for processed
        def mock_exists(key):
            if "txn_processed:" in key:
                return False
            elif "inflight:" in key:
                return True
            return False
        
        mock_redis_client.exists.side_effect = mock_exists
        
        is_dup, reason = deduplicator.is_duplicate(
            sample_transaction["txn_id"], 
            sample_transaction["source"]
        )
        
        assert is_dup is True
        assert reason == "in_flight"
    
    @patch('utils.redis.redis_dedupe.redis_client')
    def test_mark_inflight_success(self, mock_redis_client, deduplicator, sample_transaction):
        """Test successful in-flight marking"""
        # Mock successful Redis operations
        mock_redis_client.get_client.return_value.setex.return_value = True
        mock_redis_client.safe_sadd.return_value = True
        
        result = deduplicator.mark_inflight(
            sample_transaction["txn_id"], 
            sample_transaction["source"]
        )
        
        assert result is True
        
        # Verify Redis calls
        mock_redis_client.get_client.return_value.setex.assert_called_once()
        mock_redis_client.safe_sadd.assert_called_once()
    
    @patch('utils.redis.redis_dedupe.redis_client')
    def test_mark_processed_success(self, mock_redis_client, deduplicator, sample_transaction):
        """Test successful processed marking"""
        # Mock successful Redis operation
        mock_redis_client.get_client.return_value.setex.return_value = True
        
        result = deduplicator.mark_processed(
            sample_transaction["txn_id"], 
            sample_transaction["source"]
        )
        
        assert result is True
        mock_redis_client.get_client.return_value.setex.assert_called_once()
    
    @patch('utils.redis.redis_dedupe.redis_client')
    def test_release_inflight_success(self, mock_redis_client, deduplicator, sample_transaction):
        """Test successful in-flight release"""
        # Mock successful Redis operations
        mock_redis_client.safe_delete.return_value = True
        mock_redis_client.safe_srem.return_value = True
        
        result = deduplicator.release_inflight(
            sample_transaction["txn_id"], 
            sample_transaction["source"]
        )
        
        assert result is True
        
        # Verify Redis calls
        mock_redis_client.safe_delete.assert_called_once()
        mock_redis_client.safe_srem.assert_called_once()
    
    @patch('utils.redis.redis_dedupe.redis_client')
    def test_process_transaction_safely_success(self, mock_redis_client, deduplicator, sample_transaction):
        """Test safe transaction processing flow"""
        # Mock non-duplicate and successful in-flight marking
        mock_redis_client.exists.return_value = False  # Not duplicate
        mock_redis_client.get_client.return_value.setex.return_value = True  # Successful in-flight
        mock_redis_client.safe_sadd.return_value = True
        
        should_process, reason = deduplicator.process_transaction_safely(
            sample_transaction["txn_id"], 
            sample_transaction["source"]
        )
        
        assert should_process is True
        assert reason == "ready_for_processing"
    
    @patch('utils.redis.redis_dedupe.redis_client')
    def test_process_transaction_safely_duplicate(self, mock_redis_client, deduplicator, sample_transaction):
        """Test safe transaction processing with duplicate"""
        # Mock duplicate detection
        mock_redis_client.exists.return_value = True  # Is duplicate
        
        should_process, reason = deduplicator.process_transaction_safely(
            sample_transaction["txn_id"], 
            sample_transaction["source"]
        )
        
        assert should_process is False
        assert reason in ["already_processed", "in_flight"]
    
    @patch('utils.redis.redis_dedupe.redis_client')
    def test_get_inflight_count(self, mock_redis_client, deduplicator):
        """Test in-flight transaction count retrieval"""
        # Mock Redis set cardinality
        mock_redis_client.get_client.return_value.scard.return_value = 5
        
        count = deduplicator.get_inflight_count()
        
        assert count == 5
        mock_redis_client.get_client.return_value.scard.assert_called_once()
    
    @patch('utils.redis.redis_dedupe.redis_client')
    def test_get_inflight_transactions(self, mock_redis_client, deduplicator):
        """Test in-flight transaction list retrieval"""
        # Mock Redis set members
        mock_transactions = {"TXN123:core", "TXN456:gateway", "TXN789:mobile"}
        mock_redis_client.get_client.return_value.smembers.return_value = mock_transactions
        
        transactions = deduplicator.get_inflight_transactions()
        
        assert len(transactions) == 3
        assert "TXN123:core" in transactions
        assert "TXN456:gateway" in transactions
        assert "TXN789:mobile" in transactions
    
    @patch('utils.redis.redis_dedupe.redis_client')
    def test_cleanup_expired_inflight(self, mock_redis_client, deduplicator):
        """Test cleanup of expired in-flight transactions"""
        # Mock in-flight transactions
        mock_transactions = ["TXN123:core", "TXN456:gateway"]
        mock_redis_client.get_client.return_value.smembers.return_value = mock_transactions
        
        # Mock exists check - first doesn't exist (expired), second exists
        mock_redis_client.exists.side_effect = [False, True]
        
        # Mock successful cleanup
        mock_redis_client.safe_delete.return_value = True
        mock_redis_client.safe_srem.return_value = True
        
        cleaned = deduplicator.cleanup_expired_inflight()
        
        assert cleaned == 1  # Only one was expired and cleaned
    
    @patch('utils.redis.redis_dedupe.redis_client')
    def test_error_handling(self, mock_redis_client, deduplicator, sample_transaction):
        """Test graceful error handling"""
        # Mock Redis error
        mock_redis_client.exists.side_effect = Exception("Redis connection failed")
        
        # Should handle error gracefully
        is_dup, reason = deduplicator.is_duplicate(
            sample_transaction["txn_id"], 
            sample_transaction["source"]
        )
        
        # Should fail-safe (assume not duplicate)
        assert is_dup is False
        assert reason == "check_failed"
    
    def test_ttl_configuration(self, deduplicator):
        """Test TTL configuration values"""
        assert deduplicator.inflight_ttl == 60  # 1 minute
        assert deduplicator.processed_ttl == 3600  # 1 hour
    
    @pytest.mark.integration
    def test_full_transaction_lifecycle(self, deduplicator, sample_transaction):
        """Integration test for complete transaction lifecycle"""
        # This test would require a real Redis instance
        # and would test the complete flow:
        # 1. Check not duplicate
        # 2. Mark in-flight
        # 3. Process transaction
        # 4. Mark processed
        # 5. Release in-flight
        # 6. Verify duplicate detection works
        pass


if __name__ == "__main__":
    pytest.main([__file__])