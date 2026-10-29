
import time
import uuid
import requests

API = "http://13.220.92.44:8000"
COUNT = 20

submitted = []

for i in range(COUNT):
    transaction = {
        "step": 1,
        "type": "CASH_OUT" if i % 2 == 0 else "TRANSFER",
        "amount": 100 + (i * 137),
        "nameOrig": f"C{uuid.uuid4().int % 10**10:010d}",
        "oldbalanceOrg": 10000 + (i * 137),
        "newbalanceOrig": 10000,
        "nameDest": f"C{uuid.uuid4().int % 10**10:010d}",
        "oldbalanceDest": 500 + (i * 20),
        "newbalanceDest": 600 + (i * 20),
    }

    try:
        response = requests.post(
            f"{API}/transactions",
            json=transaction,
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
        submitted.append(result["transaction_id"])
        print(f"{i + 1:02}/{COUNT}: {result}")
    except Exception as exc:
        print(f"{i + 1:02}/{COUNT}: FAILED - {exc}")

print(f"\nAccepted: {len(submitted)}/{COUNT}")
print("Waiting 10 seconds for worker processing...")
time.sleep(10)

completed = 0
for transaction_id in submitted:
    try:
        response = requests.get(
            f"{API}/predictions/{transaction_id}",
            timeout=10,
        )
        if response.ok and response.json().get("status") == "completed":
            completed += 1
    except requests.RequestException:
        pass

print(f"Predictions completed after 10 seconds: {completed}/{len(submitted)}")
