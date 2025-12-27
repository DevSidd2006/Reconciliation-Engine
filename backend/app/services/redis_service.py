"""
Redis service for banking-grade transaction reconciliation
Handles caching, throttling, and temporary transaction storage
"""
import json
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import hashlib

class RedisService:
    def __init__(self, host='localhost', port=6379, db=0):
        """Initialize Redis connection for banking operations"""
        self.redis_client = redis.Redis(
            host=host, 
            port=port, 
            db=db, 
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        
        # Banking-specific cache TTLs (Time To Live)
        self.CACHE_TTL = {
            'api_response': 30,          # API responses - 30 seconds
            'transaction_temp': 300,     # In-flight transactions - 5 minutes
            'mismatch_throttle': 5,      # Mismatch check throttling - 5 seconds
            'stats_cache': 120,          # Statistics cache - 2 minutes
            'reconciliation_lock': 30,   # Reconciliation locks - 30 seconds
            'rate_limit': 3600          # Rate limiting - 1 hour
        }
        
        # Redis key prefixes for organization
        self.PREFIXES = {
            'transaction': 'txn:',
            'mismatch': 'mismatch:',
            'cache': 'cache:',
            'lock': 'lock:',
            'throttle': 'throttle:',
            'stats': 'stats:',
            'temp': 'temp:',
            'rate_limit': 'rate:'
        }
    
    def is_connected(self) -> bool:
        """Check Redis connection health"""
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    # ==================== IN-FLIGHT TRANSACTION STORAGE ====================
    
    def store_inflight_transaction(self, txn_id: str, transaction_data: Dict) -> bool:
        """Store in-flight transaction temporarily for reconciliation"""
        try:
            key = f"{self.PREFIXES['temp']}{txn_id}"
            
            # Add metadata
            transaction_data['stored_at'] = datetime.now().isoformat()
            transaction_data['status'] = 'IN_FLIGHT'
            
            # Store with TTL
            self.redis_client.setex(
                key, 
                self.CACHE_TTL['transaction_temp'],
                json.dumps(transaction_data)
            )
            
            # Add to source-specific set for quick lookups
            source_key = f"{self.PREFIXES['temp']}source:{transaction_data['source']}"
            self.redis_client.sadd(source_key, txn_id)
            self.redis_client.expire(source_key, self.CACHE_TTL['transaction_temp'])
            
            return True
            
        except Exception as e:
            print(f"Error storing in-flight transaction: {e}")
            return False
    
    def get_inflight_transaction(self, txn_id: str) -> Optional[Dict]:
        """Retrieve in-flight transaction"""
        try:
            key = f"{self.PREFIXES['temp']}{txn_id}"
            data = self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            print(f"Error retrieving in-flight transaction: {e}")
            return None
    
    def get_inflight_by_source(self, source: str) -> List[Dict]:
        """Get all in-flight transactions for a specific source"""
        try:
            source_key = f"{self.PREFIXES['temp']}source:{source}"
            txn_ids = self.redis_client.smembers(source_key)
            
            transactions = []
            for txn_id in txn_ids:
                txn_data = self.get_inflight_transaction(txn_id)
                if txn_data:
                    transactions.append(txn_data)
            
            return transactions
            
        except Exception as e:
            print(f"Error retrieving in-flight transactions by source: {e}")
            return []
    
    def remove_inflight_transaction(self, txn_id: str, source: str) -> bool:
        """Remove in-flight transaction after reconciliation"""
        try:
            # Remove main transaction
            key = f"{self.PREFIXES['temp']}{txn_id}"
            self.redis_client.delete(key)
            
            # Remove from source set
            source_key = f"{self.PREFIXES['temp']}source:{source}"
            self.redis_client.srem(source_key, txn_id)
            
            return True
            
        except Exception as e:
            print(f"Error removing in-flight transaction: {e}")
            return False
    
    # ==================== MISMATCH THROTTLING ====================
    
    def should_check_mismatch(self, txn_id: str) -> bool:
        """Throttle mismatch checks to prevent excessive processing"""
        try:
            throttle_key = f"{self.PREFIXES['throttle']}mismatch:{txn_id}"
            
            # Check if already throttled
            if self.redis_client.exists(throttle_key):
                return False
            
            # Set throttle
            self.redis_client.setex(
                throttle_key,
                self.CACHE_TTL['mismatch_throttle'],
                "throttled"
            )
            
            return True
            
        except Exception as e:
            print(f"Error checking mismatch throttle: {e}")
            return True  # Default to allowing check
    
    def get_mismatch_check_count(self, txn_id: str) -> int:
        """Get number of mismatch checks performed for a transaction"""
        try:
            count_key = f"{self.PREFIXES['throttle']}count:{txn_id}"
            count = self.redis_client.get(count_key)
            return int(count) if count else 0
            
        except Exception as e:
            print(f"Error getting mismatch check count: {e}")
            return 0
    
    def increment_mismatch_check(self, txn_id: str) -> int:
        """Increment mismatch check counter"""
        try:
            count_key = f"{self.PREFIXES['throttle']}count:{txn_id}"
            count = self.redis_client.incr(count_key)
            self.redis_client.expire(count_key, 3600)  # 1 hour TTL
            return count
            
        except Exception as e:
            print(f"Error incrementing mismatch check: {e}")
            return 0
    
    # ==================== API RESPONSE CACHING ====================
    
    def cache_api_response(self, endpoint: str, params: Dict, response_data: Any) -> bool:
        """Cache API response for faster subsequent requests"""
        try:
            # Create cache key from endpoint and parameters
            cache_key = self._generate_cache_key(endpoint, params)
            
            cache_data = {
                'data': response_data,
                'cached_at': datetime.now().isoformat(),
                'endpoint': endpoint,
                'params': params
            }
            
            self.redis_client.setex(
                cache_key,
                self.CACHE_TTL['api_response'],
                json.dumps(cache_data, default=str)
            )
            
            return True
            
        except Exception as e:
            print(f"Error caching API response: {e}")
            return False
    
    def get_cached_response(self, endpoint: str, params: Dict) -> Optional[Any]:
        """Retrieve cached API response"""
        try:
            cache_key = self._generate_cache_key(endpoint, params)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                cache_obj = json.loads(cached_data)
                return cache_obj['data']
            
            return None
            
        except Exception as e:
            print(f"Error retrieving cached response: {e}")
            return None
    
    def _generate_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate consistent cache key from endpoint and parameters"""
        # Sort parameters for consistent key generation
        sorted_params = json.dumps(params, sort_keys=True)
        key_string = f"{endpoint}:{sorted_params}"
        
        # Hash for consistent length
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{self.PREFIXES['cache']}{key_hash}"
    
    # ==================== STATISTICS CACHING ====================
    
    def cache_stats(self, stats_type: str, stats_data: Dict) -> bool:
        """Cache statistics for faster dashboard loading"""
        try:
            stats_key = f"{self.PREFIXES['stats']}{stats_type}"
            
            cache_data = {
                'stats': stats_data,
                'generated_at': datetime.now().isoformat()
            }
            
            self.redis_client.setex(
                stats_key,
                self.CACHE_TTL['stats_cache'],
                json.dumps(cache_data, default=str)
            )
            
            return True
            
        except Exception as e:
            print(f"Error caching stats: {e}")
            return False
    
    def get_cached_stats(self, stats_type: str) -> Optional[Dict]:
        """Retrieve cached statistics"""
        try:
            stats_key = f"{self.PREFIXES['stats']}{stats_type}"
            cached_data = self.redis_client.get(stats_key)
            
            if cached_data:
                cache_obj = json.loads(cached_data)
                return cache_obj['stats']
            
            return None
            
        except Exception as e:
            print(f"Error retrieving cached stats: {e}")
            return None
    
    # ==================== RECONCILIATION LOCKING ====================
    
    def acquire_reconciliation_lock(self, txn_id: str) -> bool:
        """Acquire lock for transaction reconciliation to prevent race conditions"""
        try:
            lock_key = f"{self.PREFIXES['lock']}reconcile:{txn_id}"
            
            # Try to acquire lock
            acquired = self.redis_client.set(
                lock_key,
                datetime.now().isoformat(),
                nx=True,  # Only set if key doesn't exist
                ex=self.CACHE_TTL['reconciliation_lock']
            )
            
            return bool(acquired)
            
        except Exception as e:
            print(f"Error acquiring reconciliation lock: {e}")
            return False
    
    def release_reconciliation_lock(self, txn_id: str) -> bool:
        """Release reconciliation lock"""
        try:
            lock_key = f"{self.PREFIXES['lock']}reconcile:{txn_id}"
            self.redis_client.delete(lock_key)
            return True
            
        except Exception as e:
            print(f"Error releasing reconciliation lock: {e}")
            return False
    
    # ==================== RATE LIMITING ====================
    
    def check_rate_limit(self, identifier: str, limit: int, window_seconds: int = 3600) -> bool:
        """Check if request is within rate limit"""
        try:
            rate_key = f"{self.PREFIXES['rate_limit']}{identifier}"
            current_count = self.redis_client.get(rate_key)
            
            if current_count is None:
                # First request in window
                self.redis_client.setex(rate_key, window_seconds, 1)
                return True
            
            if int(current_count) >= limit:
                return False
            
            # Increment counter
            self.redis_client.incr(rate_key)
            return True
            
        except Exception as e:
            print(f"Error checking rate limit: {e}")
            return True  # Default to allowing request
    
    # ==================== SYSTEM MONITORING ====================
    
    def get_redis_stats(self) -> Dict:
        """Get Redis performance statistics"""
        try:
            info = self.redis_client.info()
            
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0)
            }
            
        except Exception as e:
            print(f"Error getting Redis stats: {e}")
            return {}
    
    def cleanup_expired_keys(self) -> int:
        """Clean up expired keys (maintenance operation)"""
        try:
            # Get all keys with our prefixes
            all_keys = []
            for prefix in self.PREFIXES.values():
                keys = self.redis_client.keys(f"{prefix}*")
                all_keys.extend(keys)
            
            # Check TTL and remove expired keys
            cleaned = 0
            for key in all_keys:
                ttl = self.redis_client.ttl(key)
                if ttl == -1:  # No expiration set
                    # Set default expiration based on key type
                    if 'temp:' in key:
                        self.redis_client.expire(key, self.CACHE_TTL['transaction_temp'])
                    elif 'cache:' in key:
                        self.redis_client.expire(key, self.CACHE_TTL['api_response'])
                    cleaned += 1
            
            return cleaned
            
        except Exception as e:
            print(f"Error cleaning up expired keys: {e}")
            return 0

# Global Redis service instance
redis_service = RedisService()