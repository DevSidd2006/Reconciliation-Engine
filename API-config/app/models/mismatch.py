
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class MismatchSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MismatchStatus(str, enum.Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    IGNORED = "ignored"

class Mismatch(Base):
    __tablename__ = "mismatches"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=True)
    type = Column(String, index=True, nullable=False) 
    severity = Column(Enum(MismatchSeverity), default=MismatchSeverity.MEDIUM)
    status = Column(Enum(MismatchStatus), default=MismatchStatus.OPEN)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    transaction = relationship("Transaction", backref="mismatches")
    
    details = Column(String, nullable=True)
