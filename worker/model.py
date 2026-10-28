import joblib
from pathlib import Path

from worker.feature_engineering import build_model_features

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "artifacts"
    / "paysim_fraud_lgbm.pkl"
)


def load_model():
    return joblib.load(MODEL_PATH)


def predict_fraud(model, transaction: dict) -> float:
    features = build_model_features(transaction)
    probability = model.predict_proba(features)[0][1]
    return float(probability)
