from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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