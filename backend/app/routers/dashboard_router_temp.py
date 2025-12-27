from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_service import db_service

router = APIRouter()

# ==================== PHASE 2 BANKING APIs ====================

@router.get("/transactions")
def get_transactions(
    limit: int = Query(50, ge=1, le=1000, description="Number of transactions to return"),
    source: Optional[str] = Query(None, description="Filter by source (core, gateway, mobile)"),
    status: Optional[str] = Query(None, description="Filter by status (SUCCESS, FAILED, PENDING)"),
    reconciliation_status: Optional[str] = Query(None, description="Filter by reconciliation status")
):
    """
    📋 Get transactions with filtering options
    
    Banking-grade transaction listing with:
    - Pagination support
    - Source filtering (core banking, gateway, mobile)
    - Status filtering
    - Reconciliation status filtering
    """
    try:
        transactions = db_service.get_transactions(
            limit=limit,
            source=source,
            status=status
        )
        
        # Filter by reconciliation status if provided
        if reconciliation_status:
            transactions = [t for t in transactions if t.get('reconciliation_status') == reconciliation_status]
        
        return {
            "transactions": transactions,
            "total": len(transactions),
            "filters": {
                "source": source,
                "status": status,
                "reconciliation_status": reconciliation_status,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving transactions: {str(e)}")

@router.get("/transactions/{txn_id}")
def get_transaction_details(txn_id: str):
    """
    🔍 Get detailed view of a specific transaction across all sources
    
    Shows the same transaction as seen by:
    - Core banking system
    - Payment gateway
    - Mobile application
    """
    try:
        transactions = db_service.get_transactions_by_txn_id(txn_id)
        
        if not transactions:
            raise HTTPException(status_code=404, detail=f"Transaction {txn_id} not found")
        
        return {
            "txn_id": txn_id,
            "sources": transactions,
            "source_count": len(transactions),
            "reconciliation_status": transactions[0].get('reconciliation_status', 'UNKNOWN')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving transaction details: {str(e)}")

@router.get("/mismatches")
def get_mismatches(
    limit: int = Query(50, ge=1, le=500, description="Number of mismatches to return"),
    severity: Optional[str] = Query(None, description="Filter by severity (HIGH, MEDIUM, LOW)"),
    mismatch_type: Optional[str] = Query(None, description="Filter by mismatch type"),
    status: Optional[str] = Query(None, description="Filter by resolution status")
):
    """
    🚨 Get mismatches with filtering options
    
    Banking-grade mismatch reporting with:
    - Severity filtering (HIGH/MEDIUM/LOW)
    - Mismatch type filtering
    - Resolution status tracking
    """
    try:
        mismatches = db_service.get_mismatches(
            limit=limit,
            severity=severity,
            mismatch_type=mismatch_type,
            status=status
        )
        
        return {
            "mismatches": mismatches,
            "total": len(mismatches),
            "filters": {
                "severity": severity,
                "mismatch_type": mismatch_type,
                "status": status,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving mismatches: {str(e)}")

@router.get("/stats")
def get_comprehensive_stats():
    """
    📊 Get comprehensive reconciliation statistics
    
    Banking-grade analytics including:
    - Transaction counts per source
    - Status distribution
    - Reconciliation success rates
    - Mismatch type breakdown
    - Recent activity metrics
    """
    try:
        stats = db_service.get_transaction_stats()
        
        return {
            "overview": {
                "total_transactions": stats['total_transactions'],
                "total_mismatches": stats['total_mismatches'],
                "success_rate": stats['success_rate'],
                "pending_reconciliation": stats['pending_reconciliation']
            },
            "source_distribution": stats['source_distribution'],
            "status_distribution": stats['status_distribution'],
            "reconciliation_breakdown": stats['reconciliation_breakdown'],
            "mismatch_analysis": {
                "types": stats['mismatch_types'],
                "total": stats['total_mismatches']
            },
            "recent_activity": stats['recent_activity'],
            "generated_at": "2025-12-14T14:45:00Z"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

@router.get("/health")
def get_health_status():
    """
    ❤️ Get system health status
    
    Banking-grade health monitoring:
    - Database connectivity
    - Redis connectivity and performance
    - Recent transaction activity
    - System status indicators
    - Uptime information
    """
    try:
        health = db_service.get_health_status()
        
        # Add Redis health check
        from services.redis_service import redis_service
        redis_connected = redis_service.is_connected()
        redis_stats = redis_service.get_redis_stats() if redis_connected else {}
        
        return {
            "status": health['status'],
            "database": {
                "connected": health['database_connected'],
                "last_transaction": health.get('last_transaction')
            },
            "redis": {
                "connected": redis_connected,
                "stats": redis_stats
            },
            "activity": {
                "transactions_last_hour": health.get('transactions_last_hour', 0)
            },
            "uptime": health['uptime'],
            "timestamp": "2025-12-14T14:45:00Z"
        }
        
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "timestamp": "2025-12-14T14:45:00Z"
        }

# ==================== LEGACY COMPATIBILITY ====================

@router.get("/metrics")
def get_metrics():
    """Legacy metrics endpoint for frontend compatibility"""
    try:
        stats = db_service.get_transaction_stats()
        
        return {
            "totalTransactions": stats['total_reconciled'],
            "totalMismatches": stats['total_mismatches'],
            "successRate": stats['success_rate'],
            "pendingReconciliation": stats['pending_reconciliation'],
            "systemStatus": "ONLINE"
        }
        
    except Exception as e:
        return {
            "totalTransactions": 0,
            "totalMismatches": 0,
            "successRate": 100,
            "pendingReconciliation": 0,
            "systemStatus": "ERROR"
        }

@router.get("/reconciliation-details")
def get_reconciliation_details():
    """Legacy reconciliation details for frontend compatibility"""
    try:
        stats = db_service.get_transaction_stats()
        transactions = db_service.get_transactions(10)
        
        return {
            "statistics": {
                "total_reconciled": stats['total_reconciled'],
                "total_mismatches": stats['total_mismatches'],
                "success_rate": stats['success_rate'],
                "pending_reconciliation": stats['pending_reconciliation']
            },
            "recent_reconciled": transactions,
            "mismatch_breakdown": stats['mismatch_types'],
            "source_breakdown": stats['source_distribution']
        }
        
    except Exception as e:
        return {
            "statistics": {"total_reconciled": 0, "total_mismatches": 0, "success_rate": 100, "pending_reconciliation": 0},
            "recent_reconciled": [],
            "mismatch_breakdown": {},
            "source_breakdown": {}
        }

@router.get("/redis-stats")
def get_redis_performance():
    """
    🚀 Get Redis cache performance statistics
    
    Banking-grade cache monitoring:
    - Cache hit/miss ratios
    - Memory usage
    - Active connections
    - In-flight transaction counts
    """
    try:
        from services.redis_service import redis_service
        
        if not redis_service.is_connected():
            return {
                "status": "DISCONNECTED",
                "error": "Redis not available"
            }
        
        # Get Redis statistics
        redis_stats = redis_service.get_redis_stats()
        
        # Calculate cache hit ratio
        hits = redis_stats.get('keyspace_hits', 0)
        misses = redis_stats.get('keyspace_misses', 0)
        total_requests = hits + misses
        hit_ratio = (hits / total_requests * 100) if total_requests > 0 else 0
        
        # Get in-flight transaction counts
        inflight_core = len(redis_service.get_inflight_by_source('core'))
        inflight_gateway = len(redis_service.get_inflight_by_source('gateway'))
        inflight_mobile = len(redis_service.get_inflight_by_source('mobile'))
        
        return {
            "status": "CONNECTED",
            "performance": {
                "cache_hit_ratio": round(hit_ratio, 2),
                "total_commands": redis_stats.get('total_commands_processed', 0),
                "connected_clients": redis_stats.get('connected_clients', 0),
                "memory_usage": redis_stats.get('used_memory_human', '0B'),
                "uptime_seconds": redis_stats.get('uptime_in_seconds', 0)
            },
            "banking_metrics": {
                "inflight_transactions": {
                    "core": inflight_core,
                    "gateway": inflight_gateway,
                    "mobile": inflight_mobile,
                    "total": inflight_core + inflight_gateway + inflight_mobile
                }
            },
            "timestamp": "2025-12-14T14:45:00Z"
        }
        
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "timestamp": "2025-12-14T14:45:00Z"
        }