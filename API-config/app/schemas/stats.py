
from typing import List, Dict, Any
from pydantic import BaseModel
from app.schemas.mismatch import MismatchResponse

class StatsSummary(BaseModel):
    total_transactions: int
    by_source: Dict[str, int]
    by_status: Dict[str, int]
    total_mismatches: int
    by_mismatch_type: Dict[str, int]

class DashboardStats(BaseModel):
    incoming_txn_per_minute: float
    mismatch_rate: float
    top_mismatch_type: str
    last_10_mismatches: List[MismatchResponse]
