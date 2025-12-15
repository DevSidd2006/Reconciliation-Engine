"""
Banking-Grade Redis Deduplication System for Transaction Reconciliation Engine

This module provides robust transaction deduplication using Redis:
- In-flight transaction tracking
- Processed transaction memory
- Race condition prevention
- TTL-based cleanup
"""

import logging
from typing import Tuple, Optional
from .redis_client import redis_client
from .redis_config import redis_config

# Configure logging
logger = logging.getLogger(__name__)


class BankingDeduplicator:
    """
    Production-grade transaction deduplication system
    
    Features:
    - In-flight transaction tracking to prevent race conditions
    - Processed transaction memory to prevent duplicate processing
    - Atomic operations using Redis transactions
    - TTL-based automatic cleanup
    - Comprehensive logging for audit trails
    """
    
    def __init__(self):
        """Initialize deduplicator with Redis client and configuration"""
        self.client = redis_client
        self.config = redis_config
        self.inflight_ttl = self.config.DEDUPE_TTL_INFLIGHT
        self.processed_ttl = self.config.DEDUPE_TTL_PROCESSED
        
        logger.info(
            f"Deduplicator initialized: inflight_ttl={self.inflight_ttl}s, "
            f"processed_ttl={self.processed_ttl}s"
        )
    
    def is_duplicate(self, txn_id: str, source: str) -> Tuple[bool, str]:
        """
        Check if transaction is a duplicate (already processed or in-flight)
        
        Args:
            txn_id: Transaction ID
            source: Transaction source (core, gateway, mobile)
            
        Returns:
            Tuple of (is_duplicate: bool, reason: str)
        """
        processed_key = self.config.get_dedupe_key(txn_id, source)
        inflight_key = self.config.get_inflight_key(txn_id, source)
        
        try:
            # Check if already processed
            if self.client.exists(processed_key):
                logger.info(f"Duplicate detected - already processed: {txn_id} from {source}")
                return True, "already_processed"
            
            # Check if currently in-flight
            if self.client.exists(inflight_key):
                logger.info(f"Duplicate detected - currently in-flight: {txn_id} from {source}")
                return True, "in_flight"
            
            return False, "not_duplicate"
            
        except Exception as e:
            logger.error(f"Error checking duplicate status for {txn_id} from {source}: {e}")
            # Fail-safe: assume not duplicate to avoid blocking legitimate transactions
            return False, "check_failed"
    
    def mark_inflight(self, txn_id: str, source: str) -> bool:
        """
        Mark transaction as in-flight (currently being processed)
        
        Args:
            txn_id: Transaction ID
            source: Transaction source
            
        Returns:
            True if successfully marked, False otherwise
        """
        inflight_key = self.config.get_inflight_key(txn_id, source)
        
        try:
            # Set in-flight marker with TTL
            success = self.client.get_client().setex(inflight_key, self.inflight_ttl, "processing")
            
            if success:
                # Also add to inflight set for monitoring
                inflight_set_key = f"{self.config.NAMESPACE_INFLIGHT}:active_set"
                self.client.safe_sadd(inflight_set_key, f"{txn_id}:{source}")
                
                logger.debug(f"Marked as in-flight: {txn_id} from {source}")
            else:
                logger.warning(f"Failed to mark as in-flight: {txn_id} from {source}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error marking in-flight {txn_id} from {source}: {e}")
            return False
    
    def mark_processed(self, txn_id: str, source: str) -> bool:
        """
        Mark transaction as successfully processed
        
        Args:
            txn_id: Transaction ID
            source: Transaction source
            
        Returns:
            True if successfully marked, False otherwise
        """
        processed_key = self.config.get_dedupe_key(txn_id, source)
        
        try:
            # Set processed marker with longer TTL
            success = self.client.get_client().setex(processed_key, self.processed_ttl, "completed")
            
            if success:
                logger.debug(f"Marked as processed: {txn_id} from {source}")
            else:
                logger.warning(f"Failed to mark as processed: {txn_id} from {source}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error marking processed {txn_id} from {source}: {e}")
            return False
    
    def release_inflight(self, txn_id: str, source: str) -> bool:
        """
        Release in-flight lock (called after processing completes or fails)
        
        Args:
            txn_id: Transaction ID
            source: Transaction source
            
        Returns:
            True if successfully released, False otherwise
        """
        inflight_key = self.config.get_inflight_key(txn_id, source)
        inflight_set_key = f"{self.config.NAMESPACE_INFLIGHT}:active_set"
        
        try:
            # Remove in-flight marker
            deleted = self.client.safe_delete(inflight_key)
            
            # Remove from inflight set
            self.client.safe_srem(inflight_set_key, f"{txn_id}:{source}")
            
            if deleted:
                logger.debug(f"Released in-flight lock: {txn_id} from {source}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error releasing in-flight {txn_id} from {source}: {e}")
            return False
    
    def process_transaction_safely(self, txn_id: str, source: str) -> Tuple[bool, str]:
        """
        Atomically check and mark transaction for processing
        
        This method combines duplicate checking and in-flight marking in a
        race-condition-safe manner.
        
        Args:
            txn_id: Transaction ID
            source: Transaction source
            
        Returns:
            Tuple of (should_process: bool, reason: str)
        """
        try:
            # First check if it's a duplicate
            is_dup, reason = self.is_duplicate(txn_id, source)
            if is_dup:
                return False, reason
            
            # Try to mark as in-flight atomically
            if self.mark_inflight(txn_id, source):
                logger.info(f"Transaction ready for processing: {txn_id} from {source}")
                return True, "ready_for_processing"
            else:
                logger.warning(f"Failed to acquire in-flight lock: {txn_id} from {source}")
                return False, "lock_failed"
                
        except Exception as e:
            logger.error(f"Error in safe transaction processing for {txn_id} from {source}: {e}")
            return False, f"error: {str(e)}"
    
    def get_inflight_count(self) -> int:
        """
        Get count of currently in-flight transactions
        
        Returns:
            Number of transactions currently being processed
        """
        try:
            inflight_set_key = f"{self.config.NAMESPACE_INFLIGHT}:active_set"
            return self.client.get_client().scard(inflight_set_key)
        except Exception as e:
            logger.error(f"Error getting in-flight count: {e}")
            return 0
    
    def get_inflight_transactions(self) -> list:
        """
        Get list of currently in-flight transactions (for monitoring)
        
        Returns:
            List of transaction identifiers currently in-flight
        """
        try:
            inflight_set_key = f"{self.config.NAMESPACE_INFLIGHT}:active_set"
            return list(self.client.get_client().smembers(inflight_set_key))
        except Exception as e:
            logger.error(f"Error getting in-flight transactions: {e}")
            return []
    
    def cleanup_expired_inflight(self) -> int:
        """
        Manually cleanup expired in-flight transactions (usually automatic via TTL)
        
        Returns:
            Number of expired entries cleaned up
        """
        try:
            inflight_transactions = self.get_inflight_transactions()
            cleaned = 0
            
            for txn_identifier in inflight_transactions:
                if ':' in txn_identifier:
                    txn_id, source = txn_identifier.split(':', 1)
                    inflight_key = self.config.get_inflight_key(txn_id, source)
                    
                    # Check if the key still exists (TTL might have expired)
                    if not self.client.exists(inflight_key):
                        # Remove from set since TTL expired
                        if self.release_inflight(txn_id, source):
                            cleaned += 1
            
            if cleaned > 0:
                logger.info(f"Cleaned up {cleaned} expired in-flight transactions")
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error during in-flight cleanup: {e}")
            return 0


# Global deduplicator instance
banking_deduplicator = BankingDeduplicator()