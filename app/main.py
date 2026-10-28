from typing import Literal
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models import Prediction, TransactionRecord

import json
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError

app = FastAPI()

kinesis = boto3.client(
    "kinesis",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
)

KINESIS_STREAM_NAME = os.getenv(
    "KINESIS_STREAM_NAME",
    "paysim-transactions",
)


# feature schema
class PaySimTransaction(BaseModel):
    step: int = Field(ge=1)

    type: Literal[
        "CASH_IN",
        "CASH_OUT",
        "DEBIT",
        "PAYMENT",
        "TRANSFER",
    ]

    amount: float = Field(gt=0)

    nameOrig: str
    oldbalanceOrg: float = Field(ge=0)
    newbalanceOrig: float = Field(ge=0)

    nameDest: str
    oldbalanceDest: float = Field(ge=0)
    newbalanceDest: float = Field(ge=0)

    model_config = {"extra": "forbid"}

# response schema
class PredictionResponse(BaseModel):
    transaction_id: str
    status: Literal["pending", "completed"]
    fraud_probability: float | None = None
    decision: Literal["ALLOW", "BLOCK"] | None = None


@app.get("/")
def root():
    return {
        "project": "Transaction Anomaly Detector",
        "version": "1.0",
    }

@app.post("/transactions", status_code=201)
def receive_paysim_transaction(
    transaction: PaySimTransaction,
    db: Session = Depends(get_db),
):
    transaction_id = str(uuid4())

    db_transaction = TransactionRecord(
        transaction_id=transaction_id,
        step=transaction.step,
        transaction_type=transaction.type,
        amount=transaction.amount,
        name_orig=transaction.nameOrig,
        oldbalance_orig=transaction.oldbalanceOrg,
        newbalance_orig=transaction.newbalanceOrig,
        name_dest=transaction.nameDest,
        oldbalance_dest=transaction.oldbalanceDest,
        newbalance_dest=transaction.newbalanceDest,
        status="pending",
    )

    try:
        db.add(db_transaction)
        db.commit()
    except Exception:
        db.rollback()
        raise

    event = {
        "transaction_id": transaction_id,
        "transaction": transaction.model_dump(),
    }

    try:
        kinesis.put_record(
            StreamName=KINESIS_STREAM_NAME,
            Data=json.dumps(event),
            PartitionKey=transaction_id,
        )
    except (BotoCoreError, ClientError):
        db_transaction.status = "pending"
        db.commit()
        raise HTTPException(
            status_code=503,
            detail="Transaction stored but publishing to Kinesis failed",
        )

    return {
        "message": "Transaction stored",
        "transaction_id": transaction_id,
        "status": "pending",
    }

@app.get(
    "/predictions/{transaction_id}",
    response_model=PredictionResponse,
)
def get_prediction(
    transaction_id: str,
    db: Session = Depends(get_db),
):
    transaction = db.get(TransactionRecord, transaction_id)

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    prediction = db.get(Prediction, transaction_id)

    if prediction is None:
        return PredictionResponse(
            transaction_id=transaction_id,
            status="pending",
        )

    return PredictionResponse(
        transaction_id=transaction_id,
        status="completed",
        fraud_probability=prediction.fraud_probability,
        decision=prediction.decision,
    )
