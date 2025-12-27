import random
import uuid
from datetime import datetime, timedelta

# Weighted mismatch probabilities (realistic banking distribution)
# Banking systems typically maintain 95%+ accuracy
MISMATCH_WEIGHTS = {
    "CORRECT": 85,
    "AMOUNT_MISMATCH": 7,
    "STATUS_MISMATCH": 4,
    "TIME_MISMATCH": 2,
    "CURRENCY_MISMATCH": 1,
    "MISSING_FIELD": 1,
    "WRONG_ACCOUNT": 0,
    "WRONG_SCHEMA": 0,
    "DUPLICATE": 0
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
        # More sophisticated variance to simulate real banking scenarios:
        # rounding errors, fee discrepancies, percentage-based differences
        variation_type = random.choice(["rounding", "fee", "percentage"])
        if variation_type == "rounding":
            txn["amount"] = round(txn["amount"] + random.uniform(-0.50, 0.50), 2)
        elif variation_type == "fee":
            txn["amount"] += random.choice([2.50, 5.00, 10.00, 25.00])
        else:  # percentage
            txn["amount"] *= random.uniform(0.98, 1.02)  # ±2% variation
        txn["amount"] = round(txn["amount"], 2)
    
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
        # Maintain base structure but add invalid field to trigger validation errors
        # This preserves downstream processing compatibility
        txn["_invalid_field"] = "schema_error"
        txn["malformed_data"] = True
    
    elif mismatch_type == "DUPLICATE":
        # Keep same txn_id but change source to create duplicate scenario
        pass  # No changes needed, duplicate will be detected by reconciliation engine
    
    return txn