from worker.model import predict_fraud
from shared.prediction_store import save_prediction


FRAUD_THRESHOLD = 0.5


def process_transaction(model, transaction_id: str, transaction: dict):
    probability = predict_fraud(model, transaction)

    decision = "BLOCK" if probability >= FRAUD_THRESHOLD else "ALLOW"

    save_prediction(
        transaction_id=transaction_id,
        fraud_probability=probability,
        decision=decision,
    )

    return {
        "transaction_id": transaction_id,
        "fraud_probability": probability,
        "decision": decision,
    }
