
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api import deps
from app.core.database import get_db
from app.models.transaction import Transaction, TransactionSource
from app.models.mismatch import Mismatch
from app.schemas.transaction import TransactionResponse, TransactionList

router = APIRouter()

@router.get("/", response_model=TransactionList)
async def read_transactions(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve transactions (paginated).
    """
    # Count total
    count_query = select(func.count(Transaction.id))
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Get items
    query = select(Transaction).offset(skip).limit(limit).order_by(Transaction.timestamp.desc())
    result = await db.execute(query)
    items = result.scalars().all()

    return {"total": total, "items": items}

@router.get("/mismatched", response_model=List[TransactionResponse])
async def read_mismatched_transactions(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve transactions that have associated mismatches.
    """
    # Join Transaction with Mismatch
    query = (
        select(Transaction)
        .join(Mismatch, Transaction.id == Mismatch.transaction_id)
        .distinct()
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/source/{source}", response_model=List[TransactionResponse])
async def read_transactions_by_source(
    source: TransactionSource,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Filter transactions by source (core, gateway, mobile).
    """
    query = (
        select(Transaction)
        .where(Transaction.source == source)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{txn_id}", response_model=TransactionResponse)
async def read_transaction(
    txn_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get transaction by ID.
    """
    result = await db.execute(select(Transaction).where(Transaction.id == txn_id))
    transaction = result.scalars().first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction
