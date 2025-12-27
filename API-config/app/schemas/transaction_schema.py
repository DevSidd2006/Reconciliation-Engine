from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.mismatch_schema import MismatchSchema


class TransactionSchema(BaseModel):
    txn_id: str
    amount: float
    status: str
    timestamp: Optional[datetime] = None
    currency: Optional[str] = None
    account_id: Optional[str] = None
    source: str

    class Config:
        orm_mode = True


class PaginatedTransactions(BaseModel):
    items: List[TransactionSchema]
    total: int
    page: int
    page_size: int


class MismatchedTransaction(BaseModel):
    transaction: TransactionSchema
    mismatch: MismatchSchema