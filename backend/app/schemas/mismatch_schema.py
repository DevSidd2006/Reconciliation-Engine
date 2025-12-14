from pydantic import BaseModel
from datetime import datetime

class MismatchSchema(BaseModel):
    id: str
    txn_id: str
    mismatch_type: str
    detected_at: datetime
    details: str
    
    class Config:
        orm_mode = True