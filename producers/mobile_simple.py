from kafka import KafkaProducer
import time
import json
from utils import generate_txn, apply_mismatch, choose_mismatch

TOPIC = "mobile_txns"
SOURCE = "mobile"

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8') if k else None
)

print(f"🚀 Starting {SOURCE} producer...")
print("Press Ctrl+C to stop")

try:
    while True:
        mismatch = choose_mismatch()
        txn = generate_txn(SOURCE)
        
        if mismatch != "CORRECT":
            txn = apply_mismatch(txn, mismatch)
        
        try:
            future = producer.send(TOPIC, value=txn, key=txn['txn_id'])
            producer.flush()
            print(f"[{SOURCE.upper()}] Sent → {txn} | Mismatch = {mismatch}")
        except Exception as e:
            print(f"[{SOURCE.upper()}] Failed to send → {txn} | Error: {e}")
        
        time.sleep(1.4)

except KeyboardInterrupt:
    print(f"\n🛑 {SOURCE} producer stopped")
finally:
    producer.close()