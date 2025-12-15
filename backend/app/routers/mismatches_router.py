from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from db.database import get_db
from models.mismatch import Mismatch
from schemas.mismatch_schema import MismatchSchema
from utils.response import success, error

router = APIRouter()

@router.get("/")
def get_all_mismatches(
    limit: int = Query(50, ge=1, le=1000, description="Number of mismatches to return"),
    offset: int = Query(0, ge=0, description="Number of mismatches to skip"),
    mismatch_type: Optional[str] = Query(None, description="Filter by mismatch type"),
    txn_id: Optional[str] = Query(None, description="Filter by transaction ID"),
    db: Session = Depends(get_db)
):
    """Get mismatches from database with pagination and filtering"""
    try:
        query = db.query(Mismatch)
        
        # Apply filters
        if mismatch_type:
            query = query.filter(Mismatch.mismatch_type == mismatch_type)
        if txn_id:
            query = query.filter(Mismatch.txn_id == txn_id)
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination and ordering
        mismatches = query.order_by(Mismatch.detected_at.desc()).offset(offset).limit(limit).all()
        
        return success(
            data=mismatches,
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
            detail=error("Failed to retrieve mismatches", "MISMATCH_QUERY_ERROR")
        )

@router.get("/stats")
def get_mismatch_stats(db: Session = Depends(get_db)):
    """Get real mismatch statistics from database"""
    try:
        total = db.query(Mismatch).count()
        
        # Count by mismatch type
        from sqlalchemy import func
        type_counts = db.query(
            Mismatch.mismatch_type, 
            func.count(Mismatch.id).label('count')
        ).group_by(Mismatch.mismatch_type).all()
        
        type_stats = {mismatch_type: count for mismatch_type, count in type_counts}
        
        # Count recent mismatches (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_count = db.query(Mismatch).filter(Mismatch.detected_at >= yesterday).count()
        
        return success(
            data={
                "total": total,
                "by_type": type_stats,
                "recent_24h": recent_count
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error("Failed to retrieve mismatch statistics", "MISMATCH_STATS_ERROR")
        )

@router.get("/{mismatch_id}")
def get_mismatch_by_id(mismatch_id: str, db: Session = Depends(get_db)):
    """Get a specific mismatch by ID from database"""
    try:
        mismatch = db.query(Mismatch).filter(Mismatch.id == mismatch_id).first()
        
        if not mismatch:
            raise HTTPException(
                status_code=404,
                detail=error("Mismatch not found", "MISMATCH_NOT_FOUND")
            )
        
        return success(data=mismatch)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error("Failed to retrieve mismatch", "MISMATCH_RETRIEVE_ERROR")
        )

@router.get("/transaction/{txn_id}")
def get_mismatches_by_transaction(txn_id: str, db: Session = Depends(get_db)):
    """Get all mismatches for a specific transaction"""
    try:
        mismatches = db.query(Mismatch).filter(Mismatch.txn_id == txn_id).all()
        
        return success(
            data=mismatches,
            meta={"transaction_id": txn_id, "count": len(mismatches)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=error("Failed to retrieve transaction mismatches", "TXN_MISMATCH_ERROR")
        )