from typing import Dict, List, Optional

from pydantic import BaseModel

from app.schemas.mismatch_schema import MismatchSchema


class SummaryStats(BaseModel):
    per_source: Dict[str, int]
    per_status: Dict[str, int]
    per_mismatch_type: Dict[str, int]


class DashboardStats(BaseModel):
    incoming_txn_per_minute: int
    mismatch_rate: float
    top_mismatch_type: Optional[str]
    last_10_mismatches: List[MismatchSchema]


