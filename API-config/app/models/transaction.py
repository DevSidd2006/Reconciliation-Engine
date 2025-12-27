
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base

class TransactionSource(str, enum.Enum):
    CORE = "core"
    GATEWAY = "gateway"
    MOBILE = "mobile"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True) 
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, default="completed")
    source = Column(Enum(TransactionSource), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Metadata fields
    description = Column(String, nullable=True)
    reference_id = Column(String, index=True, nullable=True)
