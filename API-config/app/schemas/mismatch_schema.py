from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class MismatchSchema(BaseModel):
    id: str
    txn_id: str
    mismatch_type: str
    detected_at: datetime
    details: str
    severity: Optional[str] = None

    class Config:
        orm_mode = True


class PaginatedMismatches(BaseModel):
    items: List[MismatchSchema]
    total: int
    page: int
    page_size: int


class MismatchWithTxn(BaseModel):
    mismatch: MismatchSchema
    source: Optional[str] = None