from datetime import datetime

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class TransactionCreate(BaseModel):
    user_id: int
    amount: float = Field(gt=0)
    merchant_category: str
    timestamp: datetime

class AnomalyOut(BaseModel):
    transaction_id: int
    user_id: int
    amount: float
    merchant_category: str
    timestamp: datetime
    anomaly_score: float

DEMO_ANOMALIES = [
    {
        "transaction_id": 101,
        "user_id": 42,
        "amount": 2000.0,
        "merchant_category": "electronics",
        "timestamp": datetime(2026, 10, 27, 3, 0),
        "anomaly_score": 0.95
    },
    {
        "transaction_id": 102,
        "user_id": 42,
        "amount": 1500.0,
        "merchant_category": "shopping",
        "timestamp": datetime(2026, 10, 26, 23, 30),
        "anomaly_score": 0.83
    },
    {
        "transaction_id": 103,
        "user_id": 7,
        "amount": 5000.0,
        "merchant_category": "travel",
        "timestamp": datetime(2026, 10, 26, 12, 0),
        "anomaly_score": 0.91
    }
]

@app.get("/")
async def anomaly():
    return {"project": "Transaction Anomaly Detector", "version": "1.0"}

@app.post("/transactions")
async def transactions(transaction: TransactionCreate):
    return {
        "message": "Transaction received",
        "data": transaction
    }

@app.get(
    "/transactions/{user_id}/anomalies",
    response_model = list[AnomalyOut]
)
async def get_user_anomalies(
    user_id: int,
    limit: int = Query(default=10, ge=1, le=100)
):
    matches = []
    for transaction in DEMO_ANOMALIES:
        if transaction["user_id"] == user_id:
            matches.append(transaction)

    return matches[:limit]

@app.get("/transactions/{transaction_id}")
async def searchTransactions(transaction_id: int):
    for transaction in DEMO_ANOMALIES:
        if transaction["transaction_id"] == transaction_id:
            return transaction

    raise HTTPException(
        status_code=404,
        detail="Transaction not found"
    )
