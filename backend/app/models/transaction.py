from sqlalchemy import Column, String, Float, DateTime
from db.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    txn_id = Column(String, primary_key=True)
    amount = Column(Float)
    status = Column(String)
    timestamp = Column(DateTime, nullable=True)
    currency = Column(String, nullable=True)
    account_id = Column(String, nullable=True)
    source = Column(String)