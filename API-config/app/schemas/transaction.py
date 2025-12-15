
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.models.transaction import TransactionSource

class TransactionBase(BaseModel):
    amount: float
    currency: str
    status: str
    source: TransactionSource
    description: Optional[str] = None
    reference_id: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class TransactionList(BaseModel):
    total: int
    items: List[TransactionResponse]
