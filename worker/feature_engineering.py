
import pandas as pd


FEATURE_ORDER = [
    "amount",
    "dest_is_merchant",
    "errorBalanceOrig",
    "errorBalanceDest",
    "drained_to_customer",
    "type_CASH_OUT",
    "type_TRANSFER",
]


def build_model_features(transaction: dict) -> pd.DataFrame:
    amount = float(transaction["amount"])
    old_balance_orig = float(transaction["oldbalanceOrg"])
    new_balance_orig = float(transaction["newbalanceOrig"])
    old_balance_dest = float(transaction["oldbalanceDest"])
    new_balance_dest = float(transaction["newbalanceDest"])

    transaction_type = transaction["type"]
    destination = str(transaction["nameDest"])

    features = {
        "amount": amount,
        "dest_is_merchant": int(destination.startswith("M")),
        "errorBalanceOrig": (
            old_balance_orig - amount - new_balance_orig
        ),
        "errorBalanceDest": (
            old_balance_dest + amount - new_balance_dest
        ),
        "drained_to_customer": int(
            new_balance_orig == 0 and destination.startswith("C")
        ),
        "type_CASH_OUT": transaction_type == "CASH_OUT",
        "type_TRANSFER": transaction_type == "TRANSFER",
    }

    return pd.DataFrame(
        [[features[name] for name in FEATURE_ORDER]],
        columns=FEATURE_ORDER,
    )
