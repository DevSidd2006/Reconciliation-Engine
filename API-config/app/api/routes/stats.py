
from typing import Any, Dict, List
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api import deps
from app.core.database import get_db
from app.models.transaction import Transaction
from app.models.mismatch import Mismatch
from app.schemas.stats import StatsSummary, DashboardStats
from app.schemas.mismatch import MismatchResponse

router = APIRouter()

@router.get("/summary", response_model=StatsSummary)
async def get_stats_summary(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    # Total Transactions
    total_txns = await db.scalar(select(func.count(Transaction.id)))
    
    # By Source
    source_result = await db.execute(select(Transaction.source, func.count(Transaction.id)).group_by(Transaction.source))
    by_source = {row[0]: row[1] for row in source_result.all()}
    
    # By Status
    status_result = await db.execute(select(Transaction.status, func.count(Transaction.id)).group_by(Transaction.status))
    by_status = {row[0]: row[1] for row in status_result.all()}
    
    # Total Mismatches
    total_mismatches = await db.scalar(select(func.count(Mismatch.id)))
    
    # By Mismatch Type
    type_result = await db.execute(select(Mismatch.type, func.count(Mismatch.id)).group_by(Mismatch.type))
    by_mismatch_type = {row[0]: row[1] for row in type_result.all()}
    
    return StatsSummary(
        total_transactions=total_txns or 0,
        by_source=by_source,
        by_status=by_status,
        total_mismatches=total_mismatches or 0,
        by_mismatch_type=by_mismatch_type
    )

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    # 1. Incoming Txn Per Minute (Est. based on last hour)
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    txns_last_hour = await db.scalar(select(func.count(Transaction.id)).where(Transaction.timestamp >= one_hour_ago))
    incoming_txn_per_minute = (txns_last_hour or 0) / 60.0
    
    # 2. Mismatch Rate
    total_txns = await db.scalar(select(func.count(Transaction.id)))
    total_mismatches = await db.scalar(select(func.count(Mismatch.id)))
    mismatch_rate = (total_mismatches / total_txns * 100) if total_txns and total_txns > 0 else 0.0
    
    # 3. Top Mismatch Type
    top_type_result = await db.execute(
        select(Mismatch.type, func.count(Mismatch.id))
        .group_by(Mismatch.type)
        .order_by(func.count(Mismatch.id).desc())
        .limit(1)
    )
    first_row = top_type_result.first()
    top_mismatch_type = first_row[0] if first_row else "None"
    
    # 4. Last 10 Mismatches
    last_10_result = await db.execute(
        select(Mismatch).order_by(Mismatch.created_at.desc()).limit(10)
    )
    last_10 = last_10_result.scalars().all()
    
    return DashboardStats(
        incoming_txn_per_minute=round(incoming_txn_per_minute, 2),
        mismatch_rate=round(mismatch_rate, 2),
        top_mismatch_type=top_mismatch_type,
        last_10_mismatches=last_10
    )
