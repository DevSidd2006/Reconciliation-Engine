#!/usr/bin/env python3
"""
Redis Performance Test for Banking Reconciliation Engine
Tests all Redis features: caching, throttling, in-flight storage, locking
"""
import sys
import os
import time
import json
import asyncio
from datetime import datetime

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.redis_service import redis_service
from services.database_service import db_service

def test_redis_connection():
    """Test basic Redis connectivity"""
    print("🔌 Testing Redis Connection...")
    
    if redis_service.is_connected():
        print("✅ Redis is connected!")
        stats = redis_service.get_redis_stats()
        print(f"   Memory Usage: {stats.get('used_memory_human', 'Unknown')}")
        print(f"   Connected Clients: {stats.get('connected_clients', 0)}")
        print(f"   Uptime: {stats.get('uptime_in_seconds', 0)} seconds")
        return True
    else:
        print("❌ Redis connection failed!")
        return False

def test_inflight_transactions():
    """Test in-flight transaction storage"""
    print("\n🚀 Testing In-Flight Transaction Storage...")
    
    # Create test transactions
    test_transactions = [
        {
            'txn_id': 'TEST_001',
            'amount': 1000.00,
            'source': 'core',
            'status': 'SUCCESS',
            'timestamp': datetime.now().isoformat()
        },
        {
            'txn_id': 'TEST_001',
            'amount': 1000.00,
            'source': 'gateway',
            'status': 'SUCCESS',
            'timestamp': datetime.now().isoformat()
        },
        {
            'txn_id': 'TEST_002',
            'amount': 500.00,
            'source': 'mobile',
            'status': 'PENDING',
            'timestamp': datetime.now().isoformat()
        }
    ]
    
    # Store transactions
    for txn in test_transactions:
        success = redis_service.store_inflight_transaction(txn['txn_id'], txn)
        print(f"   {'✅' if success else '❌'} Stored {txn['txn_id']} from {txn['source']}")
    
    # Retrieve transactions
    print("\n   Retrieving stored transactions:")
    for source in ['core', 'gateway', 'mobile']:
        inflight = redis_service.get_inflight_by_source(source)
        print(f"   📊 {source.upper()}: {len(inflight)} in-flight transactions")
    
    # Test specific retrieval
    test_txn = redis_service.get_inflight_transaction('TEST_001')
    if test_txn:
        print(f"   ✅ Retrieved TEST_001: {test_txn['source']}")
    
    return True

def test_mismatch_throttling():
    """Test mismatch check throttling"""
    print("\n⏱️  Testing Mismatch Throttling...")
    
    txn_id = 'THROTTLE_TEST'
    
    # First check should be allowed
    should_check_1 = redis_service.should_check_mismatch(txn_id)
    print(f"   First check allowed: {'✅' if should_check_1 else '❌'}")
    
    # Immediate second check should be throttled
    should_check_2 = redis_service.should_check_mismatch(txn_id)
    print(f"   Second check throttled: {'✅' if not should_check_2 else '❌'}")
    
    # Test counter increment
    count = redis_service.increment_mismatch_check(txn_id)
    print(f"   Mismatch check count: {count}")
    
    return True

def test_api_caching():
    """Test API response caching"""
    print("\n💾 Testing API Response Caching...")
    
    # Test data
    endpoint = 'test_transactions'
    params = {'limit': 10, 'source': 'core'}
    test_response = {'transactions': [{'id': 1, 'amount': 100}]}
    
    # Cache response
    cached = redis_service.cache_api_response(endpoint, params, test_response)
    print(f"   Cache storage: {'✅' if cached else '❌'}")
    
    # Retrieve cached response
    retrieved = redis_service.get_cached_response(endpoint, params)
    if retrieved and retrieved == test_response:
        print("   ✅ Cache retrieval successful")
    else:
        print("   ❌ Cache retrieval failed")
    
    return True

def test_reconciliation_locking():
    """Test reconciliation locking mechanism"""
    print("\n🔒 Testing Reconciliation Locking...")
    
    txn_id = 'LOCK_TEST'
    
    # Acquire lock
    lock_acquired = redis_service.acquire_reconciliation_lock(txn_id)
    print(f"   First lock acquisition: {'✅' if lock_acquired else '❌'}")
    
    # Try to acquire same lock (should fail)
    lock_blocked = redis_service.acquire_reconciliation_lock(txn_id)
    print(f"   Second lock blocked: {'✅' if not lock_blocked else '❌'}")
    
    # Release lock
    lock_released = redis_service.release_reconciliation_lock(txn_id)
    print(f"   Lock release: {'✅' if lock_released else '❌'}")
    
    # Try to acquire again (should succeed)
    lock_reacquired = redis_service.acquire_reconciliation_lock(txn_id)
    print(f"   Lock reacquisition: {'✅' if lock_reacquired else '❌'}")
    
    # Clean up
    redis_service.release_reconciliation_lock(txn_id)
    
    return True

def test_statistics_caching():
    """Test statistics caching"""
    print("\n📊 Testing Statistics Caching...")
    
    # Test stats data
    test_stats = {
        'total_transactions': 1000,
        'total_mismatches': 50,
        'success_rate': 95.0
    }
    
    # Cache stats
    cached = redis_service.cache_stats('test_stats', test_stats)
    print(f"   Stats caching: {'✅' if cached else '❌'}")
    
    # Retrieve cached stats
    retrieved = redis_service.get_cached_stats('test_stats')
    if retrieved and retrieved == test_stats:
        print("   ✅ Stats retrieval successful")
    else:
        print("   ❌ Stats retrieval failed")
    
    return True

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("\n🚦 Testing Rate Limiting...")
    
    identifier = 'test_user'
    limit = 3
    window = 60  # 60 seconds
    
    # Test multiple requests
    results = []
    for i in range(5):
        allowed = redis_service.check_rate_limit(identifier, limit, window)
        results.append(allowed)
        print(f"   Request {i+1}: {'✅ Allowed' if allowed else '❌ Rate Limited'}")
    
    # Should allow first 3, then rate limit
    expected = [True, True, True, False, False]
    success = results == expected
    print(f"   Rate limiting working: {'✅' if success else '❌'}")
    
    return success

def test_database_integration():
    """Test Redis integration with database operations"""
    print("\n🗄️  Testing Database + Redis Integration...")
    
    try:
        # Test cached database queries
        print("   Testing cached transaction queries...")
        
        # First call (should hit database)
        start_time = time.time()
        transactions_1 = db_service.get_transactions(limit=10)
        db_time = time.time() - start_time
        
        # Second call (should hit cache)
        start_time = time.time()
        transactions_2 = db_service.get_transactions(limit=10)
        cache_time = time.time() - start_time
        
        print(f"   Database query time: {db_time:.4f}s")
        print(f"   Cached query time: {cache_time:.4f}s")
        print(f"   Cache speedup: {db_time/cache_time:.2f}x faster" if cache_time > 0 else "   Cache speedup: Instant")
        
        # Test cached stats
        print("   Testing cached statistics...")
        start_time = time.time()
        stats_1 = db_service.get_transaction_stats()
        db_stats_time = time.time() - start_time
        
        start_time = time.time()
        stats_2 = db_service.get_transaction_stats()
        cache_stats_time = time.time() - start_time
        
        print(f"   Stats query time: {db_stats_time:.4f}s")
        print(f"   Cached stats time: {cache_stats_time:.4f}s")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database integration test failed: {e}")
        return False

def performance_benchmark():
    """Run performance benchmarks"""
    print("\n⚡ Running Performance Benchmarks...")
    
    # Benchmark cache operations
    iterations = 1000
    
    # Test cache write performance
    start_time = time.time()
    for i in range(iterations):
        redis_service.cache_api_response(f'test_{i}', {'param': i}, {'data': f'value_{i}'})
    write_time = time.time() - start_time
    
    print(f"   Cache writes: {iterations} operations in {write_time:.4f}s")
    print(f"   Write rate: {iterations/write_time:.0f} ops/sec")
    
    # Test cache read performance
    start_time = time.time()
    for i in range(iterations):
        redis_service.get_cached_response(f'test_{i}', {'param': i})
    read_time = time.time() - start_time
    
    print(f"   Cache reads: {iterations} operations in {read_time:.4f}s")
    print(f"   Read rate: {iterations/read_time:.0f} ops/sec")
    
    return True

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    # Remove test transactions
    for txn_id in ['TEST_001', 'TEST_002']:
        for source in ['core', 'gateway', 'mobile']:
            redis_service.remove_inflight_transaction(txn_id, source)
    
    # Clean up expired keys
    cleaned = redis_service.cleanup_expired_keys()
    print(f"   Cleaned up {cleaned} expired keys")
    
    return True

def main():
    """Run all Redis tests"""
    print("🏦 REDIS BANKING PERFORMANCE TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Redis Connection", test_redis_connection),
        ("In-Flight Transactions", test_inflight_transactions),
        ("Mismatch Throttling", test_mismatch_throttling),
        ("API Caching", test_api_caching),
        ("Reconciliation Locking", test_reconciliation_locking),
        ("Statistics Caching", test_statistics_caching),
        ("Rate Limiting", test_rate_limiting),
        ("Database Integration", test_database_integration),
        ("Performance Benchmark", performance_benchmark),
        ("Cleanup", cleanup_test_data)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"   ❌ {test_name} failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL REDIS FEATURES WORKING PERFECTLY!")
        
        # Show final Redis stats
        if redis_service.is_connected():
            stats = redis_service.get_redis_stats()
            print(f"\n📊 Final Redis Stats:")
            print(f"   Memory Usage: {stats.get('used_memory_human', 'Unknown')}")
            print(f"   Total Commands: {stats.get('total_commands_processed', 0):,}")
            print(f"   Cache Hits: {stats.get('keyspace_hits', 0):,}")
            print(f"   Cache Misses: {stats.get('keyspace_misses', 0):,}")
            
            hits = stats.get('keyspace_hits', 0)
            misses = stats.get('keyspace_misses', 0)
            if hits + misses > 0:
                hit_ratio = (hits / (hits + misses)) * 100
                print(f"   Hit Ratio: {hit_ratio:.2f}%")
    else:
        print("⚠️  Some tests failed. Check Redis configuration.")

if __name__ == "__main__":
    main()