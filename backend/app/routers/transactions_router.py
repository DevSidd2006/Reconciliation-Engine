from fastapi import APIRouter
from datetime import datetime
import random

router = APIRouter()

# Mock data for development
def generate_mock_transactions(count=20):
    sources = ["core", "gateway", "mobile"]
    statuses = ["success", "pending", "failed"]
    transactions = []
    
    for i in range(count):
        transactions.append({
            "txn_id": f"TXN{str(i+1).zfill(6)}",
            "amount": round(random.uniform(100, 10000), 2),
            "status": random.choice(statuses),
            "timestamp": datetime.now().isoformat(),
            "currency": "USD",
            "account_id": f"ACC{random.randint(100, 999)}",
            "source": random.choice(sources)
        })
    
    return transactions

@router.get("/")
async def get_all_transactions():
    """Get all transactions with mock data"""
    # Socket.IO integration will be added later
    return generate_mock_transactions()

@router.get("/stats")
def get_transaction_stats():
    """Get transaction statistics"""
    return {
        "total": random.randint(5000, 10000),
        "successful": random.randint(4500, 9000),
        "pending": random.randint(100, 500),
        "failed": random.randint(50, 200)
    }

@router.get("/{txn_id}")
def get_transaction_by_id(txn_id: str):
    """Get a specific transaction by ID"""
    return {
        "txn_id": txn_id,
        "amount": round(random.uniform(100, 10000), 2),
        "status": random.choice(["success", "pending", "failed"]),
        "timestamp": datetime.now().isoformat(),
        "currency": "USD",
        "account_id": f"ACC{random.randint(100, 999)}",
        "source": random.choice(["core", "gateway", "mobile"])
    }