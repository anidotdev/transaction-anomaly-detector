
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from shared.database import Base


class TransactionRecord(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String(36), primary_key=True)

    step = Column(Integer, nullable=False)
    transaction_type = Column(String(20), nullable=False)
    amount = Column(Float, nullable=False)

    name_orig = Column(String(64), nullable=False)
    oldbalance_orig = Column(Float, nullable=False)
    newbalance_orig = Column(Float, nullable=False)

    name_dest = Column(String(64), nullable=False)
    oldbalance_dest = Column(Float, nullable=False)
    newbalance_dest = Column(Float, nullable=False)

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )

    received_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class Prediction(Base):
    __tablename__ = "predictions"

    transaction_id = Column(
        String(36),
        ForeignKey("transactions.transaction_id", ondelete="CASCADE"),
        primary_key=True,
    )

    fraud_probability = Column(Float, nullable=False)
    decision = Column(String(10), nullable=False)

    scored_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
