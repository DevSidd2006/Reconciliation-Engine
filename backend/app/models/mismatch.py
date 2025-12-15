from sqlalchemy import Column, String, DateTime, Index
from db.database import Base

class Mismatch(Base):
    __tablename__ = "mismatches"
    
    id = Column(String, primary_key=True, index=True)
    txn_id = Column(String, index=True)
    mismatch_type = Column(String, index=True)
    detected_at = Column(DateTime, index=True)
    details = Column(String)
    
    __table_args__ = (
        Index('ix_mismatch_txn_type', 'txn_id', 'mismatch_type'),
    )