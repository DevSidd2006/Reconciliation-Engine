
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.models.mismatch import MismatchSeverity, MismatchStatus

class MismatchBase(BaseModel):
    transaction_id: str
    type: str
    severity: MismatchSeverity
    status: MismatchStatus
    details: Optional[str] = None

class MismatchResponse(MismatchBase):
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
