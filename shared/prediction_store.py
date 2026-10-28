from shared.database import SessionLocal
from shared.models import Prediction, TransactionRecord


def save_prediction(
    transaction_id: str,
    fraud_probability: float,
    decision: str,
):
    if not 0 <= fraud_probability <= 1:
        raise ValueError("Fraud probability must be between 0 and 1")

    if decision not in {"ALLOW", "BLOCK"}:
        raise ValueError("Decision must be ALLOW or BLOCK")

    with SessionLocal() as db:
        transaction = db.get(TransactionRecord, transaction_id)

        if transaction is None:
            raise ValueError(
                f"Transaction {transaction_id} does not exist"
            )

        existing = db.get(Prediction, transaction_id)

        # To avoid creating duplicate predictions
        if existing is None:
            prediction = Prediction(
                transaction_id=transaction_id,
                fraud_probability=fraud_probability,
                decision=decision,
            )
            db.add(prediction)

        transaction.status = "completed"

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
