from sqlalchemy import Column, String, Float, DateTime, Index, UniqueConstraint
from db.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    txn_id = Column(String, primary_key=True, index=True)
    amount = Column(Float)
    status = Column(String, index=True)
    timestamp = Column(DateTime, nullable=True, index=True)
    currency = Column(String, nullable=True)
    account_id = Column(String, nullable=True)
    source = Column(String, index=True)
    
    __table_args__ = (
        UniqueConstraint('txn_id', 'source', name='unique_txn_per_source'),
        Index('ix_txn_source_time', 'source', 'timestamp'),
    )