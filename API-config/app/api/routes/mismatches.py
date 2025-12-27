
from typing import Any, List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.core.database import get_db
from app.models.mismatch import Mismatch, MismatchSeverity
from app.models.transaction import Transaction, TransactionSource
from app.schemas.mismatch import MismatchResponse

router = APIRouter()

@router.get("/", response_model=List[MismatchResponse])
async def read_mismatches(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    severity: Optional[MismatchSeverity] = None,
    source: Optional[TransactionSource] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve mismatches with filters.
    """
    query = select(Mismatch)
    
    # Filter by Source requires Join
    if source:
        query = query.join(Transaction, Mismatch.transaction_id == Transaction.id).where(Transaction.source == source)
    
    if type:
        query = query.where(Mismatch.type == type)
    if severity:
        query = query.where(Mismatch.severity == severity)
    if start_date:
        query = query.where(Mismatch.created_at >= start_date)
    if end_date:
        query = query.where(Mismatch.created_at <= end_date)
        
    query = query.offset(skip).limit(limit).order_by(Mismatch.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{txn_id}", response_model=List[MismatchResponse])
async def read_mismatches_by_transaction(
    txn_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get mismatch details for one transaction.
    """
    query = select(Mismatch).where(Mismatch.transaction_id == txn_id)
    result = await db.execute(query)
    mismatches = result.scalars().all()
    if not mismatches:
        return []
    return mismatches
