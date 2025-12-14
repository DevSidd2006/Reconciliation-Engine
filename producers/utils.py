import random
import uuid
from datetime import datetime, timedelta

# Weighted mismatch probabilities (realistic banking distribution)
MISMATCH_WEIGHTS = {
    "CORRECT": 50,
    "AMOUNT_MISMATCH": 20,
    "STATUS_MISMATCH": 10,
    "TIME_MISMATCH": 5,
    "CURRENCY_MISMATCH": 5,
    "MISSING_FIELD": 3,
    "WRONG_ACCOUNT": 2,
    "WRONG_SCHEMA": 2,
    "DUPLICATE": 3
}

STATUSES = ["SUCCESS", "FAILED", "PENDING"]
CURRENCIES = ["INR", "USD", "EUR"]

def choose_mismatch():
    return random.choices(
        population=list(MISMATCH_WEIGHTS.keys()),
        weights=list(MISMATCH_WEIGHTS.values()),
        k=1
    )[0]

def generate_txn(source):
    return {
        "txn_id": str(uuid.uuid4()),
        "amount": round(random.uniform(100, 2000), 2),
        "status": random.choice(STATUSES),
        "timestamp": datetime.utcnow().isoformat(),
        "currency": "INR",
        "account_id": str(random.randint(100000, 999999)),
        "source": source,
    }

def apply_mismatch(txn, mismatch_type):
    if mismatch_type == "AMOUNT_MISMATCH":
        txn["amount"] += random.randint(10, 200)
    
    elif mismatch_type == "STATUS_MISMATCH":
        txn["status"] = random.choice(["FAILED", "SUCCESS"])
    
    elif mismatch_type == "TIME_MISMATCH":
        txn["timestamp"] = (datetime.utcnow() + timedelta(seconds=random.randint(6, 20))).isoformat()
    
    elif mismatch_type == "CURRENCY_MISMATCH":
        txn["currency"] = random.choice(["USD", "EUR"])
    
    elif mismatch_type == "MISSING_FIELD":
        # Set timestamp to null (proper way with nullable schema)
        txn["timestamp"] = None
    
    elif mismatch_type == "WRONG_ACCOUNT":
        txn["account_id"] = str(random.randint(1000000, 9999999))
    
    elif mismatch_type == "WRONG_SCHEMA":
        # Send invalid structure but keep required fields for display
        txn["invalid_field"] = "malformed_data"
        txn["extra_field"] = random.randint(1000, 9999)
        # Remove a required field to make it invalid
        if "currency" in txn:
            del txn["currency"]
    
    elif mismatch_type == "DUPLICATE":
        # Keep same txn_id but change source to create duplicate scenario
        pass  # No changes needed, duplicate will be detected by reconciliation engine
    
    return txn