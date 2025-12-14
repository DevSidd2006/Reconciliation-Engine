import time
import json
import requests
from utils import generate_txn, apply_mismatch, choose_mismatch

SOURCE = "core"
BACKEND_URL = "http://localhost:8000"  # We'll create a simple endpoint

print(f"🚀 Starting {SOURCE} producer (HTTP mode)...")
print("Press Ctrl+C to stop")

try:
    while True:
        mismatch = choose_mismatch()
        txn = generate_txn(SOURCE)
        
        if mismatch != "CORRECT":
            txn = apply_mismatch(txn, mismatch)
        
        # For now, just print the transaction (we'll add HTTP later)
        print(f"[{SOURCE.upper()}] Generated → {txn} | Mismatch = {mismatch}")
        
        time.sleep(1)

except KeyboardInterrupt:
    print(f"\n🛑 {SOURCE} producer stopped")