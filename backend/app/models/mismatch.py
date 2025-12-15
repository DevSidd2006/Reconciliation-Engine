from sqlalchemy import Column, String, DateTime, Integer, Text, Float
from sqlalchemy.sql import func
from ..db.database import Base

class Mismatch(Base):
    __tablename__ = "mismatches"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    txn_id = Column(String, nullable=False, index=True)
    mismatch_type = Column(String, nullable=False, index=True)  # AMOUNT_MISMATCH, STATUS_MISMATCH, etc.
    severity = Column(String, nullable=False)  # HIGH, MEDIUM, LOW
    details = Column(Text, nullable=False)
    sources_involved = Column(Text, nullable=False)  # JSON array of sources
    
    # Mismatch values for analysis
    expected_value = Column(String, nullable=True)
    actual_value = Column(String, nullable=True)
    difference_amount = Column(Float, nullable=True)  # For amount mismatches
    
    # Status tracking
    status = Column(String, default="OPEN")  # OPEN, INVESTIGATING, RESOLVED, IGNORED
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Audit fields - use application time instead of server time
    detected_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)