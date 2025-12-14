from fastapi import APIRouter
from datetime import datetime
import random

router = APIRouter()

# Mock data for development
def generate_mock_mismatches(count=15):
    mismatch_types = ["amount_mismatch", "status_mismatch", "timestamp_mismatch", "missing_transaction"]
    mismatches = []
    
    for i in range(count):
        mismatch_type = random.choice(mismatch_types)
        mismatches.append({
            "id": f"MISM{str(i+1).zfill(6)}",
            "txn_id": f"TXN{str(random.randint(1, 1000)).zfill(6)}",
            "mismatch_type": mismatch_type,
            "detected_at": datetime.now().isoformat(),
            "details": f"Mismatch detected: {mismatch_type.replace('_', ' ')} between sources"
        })
    
    return mismatches

@router.get("/")
def get_all_mismatches():
    """Get all mismatches with mock data"""
    return generate_mock_mismatches()

@router.get("/stats")
def get_mismatch_stats():
    """Get mismatch statistics"""
    return {
        "total": random.randint(50, 100),
        "resolved": random.randint(20, 50),
        "pending": random.randint(10, 30),
        "critical": random.randint(5, 15)
    }

@router.get("/{mismatch_id}")
def get_mismatch_by_id(mismatch_id: str):
    """Get a specific mismatch by ID"""
    return {
        "id": mismatch_id,
        "txn_id": f"TXN{str(random.randint(1, 1000)).zfill(6)}",
        "mismatch_type": random.choice(["amount_mismatch", "status_mismatch", "timestamp_mismatch", "missing_transaction"]),
        "detected_at": datetime.now().isoformat(),
        "details": "Mismatch details would appear here"
    }