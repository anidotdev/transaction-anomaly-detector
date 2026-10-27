from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    merchant_category = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    is_anomaly = Column(Boolean, default=False, nullable=False)
    anomaly_score = Column(Float, nullable=True)
