from sqlalchemy import Column, String, Float, DateTime, Integer, Text, Boolean
from sqlalchemy.sql import func
from ..db.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    txn_id = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)  # SUCCESS, FAILED, PENDING
    timestamp = Column(DateTime, nullable=True)
    currency = Column(String, default="INR")
    account_id = Column(String, nullable=True)
    source = Column(String, nullable=False, index=True)  # core, gateway, mobile
    
    # Reconciliation fields
    reconciliation_status = Column(String, nullable=True)  # MATCHED, MISMATCH, PENDING
    reconciled_at = Column(DateTime, nullable=True)
    reconciled_with_sources = Column(Text, nullable=True)  # JSON array of sources
    
    # Audit fields - use application time instead of server time
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)