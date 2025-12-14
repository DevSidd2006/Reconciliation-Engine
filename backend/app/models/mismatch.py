from sqlalchemy import Column, String, DateTime
from db.database import Base

class Mismatch(Base):
    __tablename__ = "mismatches"
    
    id = Column(String, primary_key=True)
    txn_id = Column(String)
    mismatch_type = Column(String)
    detected_at = Column(DateTime)
    details = Column(String)