from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import logging
from db.database import get_db
from models.transaction import Transaction
from schemas.transaction_schema import TransactionSchema
from utils.response import success, error
from utils.redis import cache_manager

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
def get_all_transactions(
    limit: int = Query(50, ge=1, le=1000, description="Number of transactions to return"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip"),
    source: Optional[str] = Query(None, description="Filter by source (core, gateway, mobile)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """Get transactions from database with pagination and filtering"""
    try:
        query = db.query(Transaction)
        
        # Apply filters
        if source:
            query = query.filter(Transaction.source == source)
        if status:
            query = query.filter(Transaction.status == status)
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination and ordering
        transactions = query.order_by(Transaction.timestamp.desc()).offset(offset).limit(limit).all()
        
        return success(
            data=transactions,
            meta={
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error("Failed to retrieve transactions", "TXN_QUERY_ERROR")
        )

@router.get("/stats")
def get_transaction_stats(db: Session = Depends(get_db)):
    """Get real transaction statistics from database with banking-grade Redis caching"""
    try:
        # Check Redis cache first using banking cache manager
        cached = cache_manager.get_cached_stats("transactions")
        if cached:
            logger.debug("Transaction stats served from cache")
            return success(data=cached)
        
        logger.debug("Computing transaction stats from database")
        
        # If not cached, compute from database
        total = db.query(Transaction).count()
        
        # Count by status
        success_count = db.query(Transaction).filter(Transaction.status == "SUCCESS").count()
        pending_count = db.query(Transaction).filter(Transaction.status == "PENDING").count()
        failed_count = db.query(Transaction).filter(Transaction.status == "FAILED").count()
        
        # Count by source
        core_count = db.query(Transaction).filter(Transaction.source == "core").count()
        gateway_count = db.query(Transaction).filter(Transaction.source == "gateway").count()
        mobile_count = db.query(Transaction).filter(Transaction.source == "mobile").count()
        
        result = {
            "total": total,
            "by_status": {
                "success": success_count,
                "pending": pending_count,
                "failed": failed_count
            },
            "by_source": {
                "core": core_count,
                "gateway": gateway_count,
                "mobile": mobile_count
            }
        }
        
        # Cache result using banking cache manager
        cache_manager.cache_stats("transactions", result)
        logger.info(f"Transaction stats computed and cached: {total} total transactions")
        
        return success(data=result)
    except Exception as e:
        logger.error(f"Failed to retrieve transaction statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=error("Failed to retrieve transaction statistics", "TXN_STATS_ERROR")
        )

@router.get("/{txn_id}")
def get_transaction_by_id(txn_id: str, db: Session = Depends(get_db)):
    """Get a specific transaction by ID from database"""
    try:
        transaction = db.query(Transaction).filter(Transaction.txn_id == txn_id).first()
        
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail=error("Transaction not found", "TXN_NOT_FOUND")
            )
        
        return success(data=transaction)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error("Failed to retrieve transaction", "TXN_RETRIEVE_ERROR")
        )