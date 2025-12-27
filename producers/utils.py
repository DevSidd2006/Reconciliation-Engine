import random
import uuid
from datetime import datetime, timedelta

# Weighted mismatch probabilities (reduced to 10-15% mismatch rate, INR-only system)
MISMATCH_WEIGHTS = {
    "CORRECT": 85,           # 85% correct transactions
    "AMOUNT_MISMATCH": 7,    # 7% amount mismatches (increased from 6%)
    "STATUS_MISMATCH": 4,    # 4% status mismatches (increased from 3%)
    "TIME_MISMATCH": 2,      # 2% time mismatches
    "CURRENCY_MISMATCH": 1,  # 1% currency format mismatches (INR formatting issues)
    "MISSING_FIELD": 1,      # 1% missing field
    "WRONG_ACCOUNT": 0,      # 0% wrong account (removed to maintain 15% total)
    "WRONG_SCHEMA": 0,       # 0% wrong schema (removed to maintain 15% total)
    "DUPLICATE": 0           # 0% duplicates (removed for cleaner data)
}

# Realistic banking transaction statuses with weights
STATUS_WEIGHTS = {
    "SUCCESS": 70,    # 70% successful transactions
    "PENDING": 25,    # 25% pending (realistic for real-time processing)
    "FAILED": 5       # 5% failed transactions
}

# Banking transaction types
TRANSACTION_TYPES = [
    "TRANSFER", "DEPOSIT", "WITHDRAWAL", "PAYMENT", 
    "REFUND", "FEE", "INTEREST", "LOAN_PAYMENT"
]

# Realistic currency distribution for Indian banking (INR only)
CURRENCY_WEIGHTS = {
    "INR": 100    # 100% INR transactions for Indian banking system
}

# Banking channels
CHANNELS = ["ATM", "ONLINE", "MOBILE", "BRANCH", "POS", "UPI"]

# Bank codes (realistic Indian bank codes)
BANK_CODES = ["HDFC", "ICICI", "SBI", "AXIS", "KOTAK", "PNB", "BOI", "CANARA"]

def choose_mismatch():
    return random.choices(
        population=list(MISMATCH_WEIGHTS.keys()),
        weights=list(MISMATCH_WEIGHTS.values()),
        k=1
    )[0]

def choose_realistic_status():
    """Choose transaction status with realistic banking distribution"""
    return random.choices(
        population=list(STATUS_WEIGHTS.keys()),
        weights=list(STATUS_WEIGHTS.values()),
        k=1
    )[0]

def choose_realistic_currency():
    """Choose currency with realistic distribution for Indian banking"""
    return random.choices(
        population=list(CURRENCY_WEIGHTS.keys()),
        weights=list(CURRENCY_WEIGHTS.values()),
        k=1
    )[0]

def generate_realistic_amount():
    """Generate realistic transaction amounts based on banking patterns"""
    # 60% small transactions (100-5000), 30% medium (5000-50000), 10% large (50000-500000)
    amount_type = random.choices(
        population=["small", "medium", "large"],
        weights=[60, 30, 10],
        k=1
    )[0]
    
    if amount_type == "small":
        return round(random.uniform(100, 5000), 2)
    elif amount_type == "medium":
        return round(random.uniform(5000, 50000), 2)
    else:
        return round(random.uniform(50000, 500000), 2)

def generate_txn(source):
    """Generate a realistic banking transaction"""
    return {
        "txn_id": str(uuid.uuid4()),
        "amount": generate_realistic_amount(),
        "status": choose_realistic_status(),
        "timestamp": datetime.utcnow().isoformat(),
        "currency": choose_realistic_currency(),
        "account_id": str(random.randint(100000000, 999999999)),  # 9-digit account numbers
        "source": source,
        "transaction_type": random.choice(TRANSACTION_TYPES),
        "channel": random.choice(CHANNELS),
        "bank_code": random.choice(BANK_CODES),
        "reference_number": f"REF{random.randint(100000000, 999999999)}",
        "merchant_id": f"MER{random.randint(10000, 99999)}" if random.random() < 0.3 else None,
        "description": f"Transaction via {random.choice(CHANNELS)}",
    }

def apply_mismatch(txn, mismatch_type):
    """Apply realistic banking mismatches"""
    if mismatch_type == "AMOUNT_MISMATCH":
        # Realistic amount discrepancies (fees, rounding, exchange rate differences)
        variance = random.choice([
            random.uniform(0.01, 5.00),      # Small rounding differences
            random.uniform(10, 100),         # Fee discrepancies
            txn["amount"] * 0.02             # 2% processing difference
        ])
        txn["amount"] = round(txn["amount"] + variance, 2)
    
    elif mismatch_type == "STATUS_MISMATCH":
        # Realistic status transitions
        current_status = txn["status"]
        if current_status == "PENDING":
            txn["status"] = random.choice(["SUCCESS", "FAILED"])
        elif current_status == "SUCCESS":
            txn["status"] = "PENDING"  # System lag
        else:
            txn["status"] = "PENDING"
    
    elif mismatch_type == "TIME_MISMATCH":
        # Realistic timing differences (system delays, timezone issues)
        delay_seconds = random.choice([
            random.randint(1, 30),      # Network delay
            random.randint(60, 300),    # Processing delay
            random.randint(3600, 7200)  # System batch processing delay
        ])
        txn["timestamp"] = (datetime.utcnow() + timedelta(seconds=delay_seconds)).isoformat()
    
    elif mismatch_type == "CURRENCY_MISMATCH":
        # For INR-only system, currency mismatch would be rare formatting issues
        # Keep INR but maybe change format or add extra characters
        txn["currency"] = random.choice(["INR ", "INR", "Rs", "₹"])
    
    elif mismatch_type == "MISSING_FIELD":
        # Missing critical fields (system integration issues)
        missing_fields = ["reference_number", "bank_code", "merchant_id"]
        field_to_remove = random.choice(missing_fields)
        if field_to_remove in txn:
            txn[field_to_remove] = None
    
    elif mismatch_type == "WRONG_ACCOUNT":
        # Account number discrepancies
        txn["account_id"] = str(random.randint(100000000, 999999999))
    
    elif mismatch_type == "WRONG_SCHEMA":
        # Schema validation errors
        txn["invalid_field"] = "malformed_data"
        txn["extra_amount"] = random.uniform(1, 100)
        # Remove required field
        if "transaction_type" in txn:
            del txn["transaction_type"]
    
    elif mismatch_type == "DUPLICATE":
        # Keep same txn_id but different source timestamp
        txn["duplicate_flag"] = True
    
    return txn