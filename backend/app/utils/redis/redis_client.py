"""
Banking-Grade Redis Client for Transaction Reconciliation Engine

This module provides a robust, production-ready Redis client with:
- Connection retry logic
- Comprehensive error handling
- Type hints and logging
- Safe operations with fallback behavior
"""

import redis
import json
import logging
import time
from typing import Optional, Any, Union
from .redis_config import redis_config

# Configure logging
logger = logging.getLogger(__name__)


class BankingRedisClient:
    """
    Production-grade Redis client with banking-level reliability and error handling
    
    Features:
    - Automatic connection retry
    - Graceful error handling with logging
    - Type-safe operations
    - Connection pooling
    - Fail-safe operations for high availability
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize Redis client with connection pooling and retry logic
        
        Args:
            max_retries: Maximum number of connection retry attempts
            retry_delay: Delay between retry attempts in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client = None
        self._connect()
    
    def _connect(self) -> None:
        """Establish Redis connection with retry logic"""
        for attempt in range(self.max_retries):
            try:
                self._client = redis.from_url(
                    redis_config.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                # Test connection
                self._client.ping()
                logger.info("Redis connection established successfully")
                return
            except Exception as e:
                logger.warning(f"Redis connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Failed to establish Redis connection after all retries")
                    raise
    
    def get_client(self) -> redis.Redis:
        """Get the underlying Redis client instance"""
        if self._client is None:
            self._connect()
        return self._client
    
    def safe_get_json(self, key: str) -> Optional[Any]:
        """
        Safely retrieve and deserialize JSON data from Redis
        
        Args:
            key: Redis key to retrieve
            
        Returns:
            Deserialized JSON data or None if key doesn't exist or error occurs
        """
        try:
            json_str = self._client.get(key)
            if json_str:
                return json.loads(json_str)
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for key {key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Redis GET_JSON error for key {key}: {e}")
            return None
    
    def safe_set_json(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """
        Safely serialize and store JSON data in Redis
        
        Args:
            key: Redis key to store data under
            data: Data to serialize and store
            ttl: Time-to-live in seconds (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            json_str = json.dumps(data, default=str, ensure_ascii=False)
            if ttl:
                return bool(self._client.setex(key, ttl, json_str))
            else:
                return bool(self._client.set(key, json_str))
        except (TypeError, ValueError) as e:
            logger.error(f"JSON serialization error for key {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Redis SET_JSON error for key {key}: {e}")
            return False
    
    def safe_delete(self, key: str) -> bool:
        """
        Safely delete a key from Redis
        
        Args:
            key: Redis key to delete
            
        Returns:
            True if key was deleted, False otherwise
        """
        try:
            return bool(self._client.delete(key))
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    def safe_sadd(self, key: str, value: str) -> bool:
        """
        Safely add value to a Redis set
        
        Args:
            key: Redis set key
            value: Value to add to set
            
        Returns:
            True if value was added, False otherwise
        """
        try:
            return bool(self._client.sadd(key, value))
        except Exception as e:
            logger.error(f"Redis SADD error for key {key}: {e}")
            return False
    
    def safe_sismember(self, key: str, value: str) -> bool:
        """
        Safely check if value exists in Redis set
        
        Args:
            key: Redis set key
            value: Value to check for membership
            
        Returns:
            True if value exists in set, False otherwise
        """
        try:
            return bool(self._client.sismember(key, value))
        except Exception as e:
            logger.error(f"Redis SISMEMBER error for key {key}: {e}")
            return False
    
    def safe_srem(self, key: str, value: str) -> bool:
        """
        Safely remove value from Redis set
        
        Args:
            key: Redis set key
            value: Value to remove from set
            
        Returns:
            True if value was removed, False otherwise
        """
        try:
            return bool(self._client.srem(key, value))
        except Exception as e:
            logger.error(f"Redis SREM error for key {key}: {e}")
            return False
    
    def atomic_increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """
        Atomically increment a counter with optional TTL
        
        Args:
            key: Redis key for counter
            amount: Amount to increment by (default: 1)
            ttl: Time-to-live in seconds (optional)
            
        Returns:
            New counter value, or 0 if error occurred
        """
        try:
            pipe = self._client.pipeline()
            pipe.incrby(key, amount)
            if ttl:
                pipe.expire(key, ttl)
            results = pipe.execute()
            return results[0] if results else 0
        except Exception as e:
            logger.error(f"Redis INCR error for key {key}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis
        
        Args:
            key: Redis key to check
            
        Returns:
            True if key exists, False otherwise
        """
        try:
            return bool(self._client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False


# Global Redis client instance
redis_client = BankingRedisClient()