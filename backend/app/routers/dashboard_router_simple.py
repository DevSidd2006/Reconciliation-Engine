"""
Real Dashboard Router with Simple Authentication
Uses real database data with simple JWT authentication
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import io
import csv
from .auth_router_simple import verify_token
from ..services.database_service import db_service

router = APIRouter()

@router.get("/transactions")
def get_transactions(
    limit: int = Query(50, description="Number of transactions to return"),
    page: int = Query(1, description="Page number"),
    source: Optional[str] = Query(None, description="Filter by source"),
    status: Optional[str] = Query(None, description="Filter by status"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_direction: str = Query("desc", description="Sort direction"),
    current_user: dict = Depends(verify_token)
):
    """💳 Get Real Transactions from Database"""
    
    try:
        # Get real transactions from database
        transactions = db_service.get_transactions(
            limit=limit, 
            source=source, 
            status=status
        )
        
        # Get total count for pagination
        stats = db_service.get_transaction_stats()
        total = stats.get('total_transactions', 0)
        total_pages = (total + limit - 1) // limit
        
        return {
            "transactions": transactions,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
        
    except Exception as e:
        print(f"Error getting transactions: {e}")
        # Fallback to empty data if database error
        return {
            "transactions": [],
            "total": 0,
            "page": page,
            "limit": limit,
            "total_pages": 0
        }

@router.get("/mismatches")
def get_mismatches(
    limit: int = Query(50, description="Number of mismatches to return"),
    mismatch_type: Optional[str] = Query(None, description="Filter by type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    txn_id: Optional[str] = Query(None, description="Filter by transaction ID"),
    current_user: dict = Depends(verify_token)
):
    """🚨 Get Real Mismatches from Database"""
    
    try:
        # Get real mismatches from database
        mismatches = db_service.get_mismatches(
            limit=limit,
            severity=severity,
            mismatch_type=mismatch_type,
            status=status,
            txn_id=txn_id
        )
        
        # Get stats for summary
        stats = db_service.get_transaction_stats()
        total_mismatches = stats.get('total_mismatches', 0)
        
        # Calculate summary from actual data
        high_severity = len([m for m in mismatches if m.get('severity') == 'HIGH'])
        medium_severity = len([m for m in mismatches if m.get('severity') == 'MEDIUM'])
        low_severity = len([m for m in mismatches if m.get('severity') == 'LOW'])
        
        open_count = len([m for m in mismatches if m.get('status') == 'OPEN'])
        investigating = len([m for m in mismatches if m.get('status') == 'INVESTIGATING'])
        resolved = len([m for m in mismatches if m.get('status') == 'RESOLVED'])
        
        return {
            "mismatches": mismatches,
            "total": total_mismatches,
            "summary": {
                "high_severity": high_severity,
                "medium_severity": medium_severity,
                "low_severity": low_severity,
                "open": open_count,
                "investigating": investigating,
                "resolved": resolved
            }
        }
        
    except Exception as e:
        print(f"Error getting mismatches: {e}")
        # Fallback to empty data if database error
        return {
            "mismatches": [],
            "total": 0,
            "summary": {
                "high_severity": 0,
                "medium_severity": 0,
                "low_severity": 0,
                "open": 0,
                "investigating": 0,
                "resolved": 0
            }
        }

@router.get("/transactions/{txn_id}")
def get_transaction_details(
    txn_id: str,
    current_user: dict = Depends(verify_token)
):
    """🔍 Get Transaction Details - Real Data from Database"""
    
    try:
        # Get real transactions for this txn_id from database
        transactions = db_service.get_transactions_by_txn_id(txn_id)
        
        if not transactions:
            # If no transactions found, return empty response
            return {
                "txn_id": txn_id,
                "sources": [],
                "error": "Transaction not found"
            }
        
        # Convert to sources format
        sources = []
        for txn in transactions:
            sources.append({
                "source": txn['source'],
                "amount": txn['amount'],
                "status": txn['status'],
                "timestamp": txn['timestamp'],
                "currency": txn['currency'],
                "account_id": txn['account_id'],
                "reconciliation_status": txn['reconciliation_status'],
                "reconciled_at": txn.get('reconciled_at'),
                "created_at": txn['created_at']
            })
        
        # Get mismatches for this transaction
        mismatches = db_service.get_mismatches(limit=100)
        txn_mismatches = [m for m in mismatches if m['txn_id'] == txn_id]
        
        return {
            "txn_id": txn_id,
            "sources": sources,
            "mismatches": txn_mismatches,
            "sources_count": len(sources),
            "mismatches_count": len(txn_mismatches)
        }
        
    except Exception as e:
        print(f"Error getting transaction details: {e}")
        # Fallback to error response
        return {
            "txn_id": txn_id,
            "sources": [],
            "error": f"Error retrieving transaction: {str(e)}"
        }

@router.get("/health")
def get_health_status(current_user: dict = Depends(verify_token)):
    """❤️ System Health Check - Real Data from Database"""
    
    try:
        # Get real health status from database
        health_data = db_service.get_health_status()
        return health_data
        
    except Exception as e:
        print(f"Error getting health status: {e}")
        # Fallback to basic status if database error
        return {
            "status": "ERROR",
            "database_connected": False,
            "error": str(e),
            "uptime": "ERROR"
        }

@router.get("/stats")
def get_stats(current_user: dict = Depends(verify_token)):
    """📊 Real System Statistics from Database"""
    
    try:
        # Get real statistics from database
        return db_service.get_transaction_stats()
        
    except Exception as e:
        print(f"Error getting stats: {e}")
        # Fallback to basic stats if database error
        return {
            "total_transactions": 0,
            "total_mismatches": 0,
            "success_rate": 100.0,
            "pending_reconciliation": 0,
            "reconciliation_breakdown": {},
            "source_distribution": {},
            "status_distribution": {},
            "mismatch_types": {},
            "recent_activity": {
                "transactions_24h": 0,
                "mismatches_24h": 0
            }
        }