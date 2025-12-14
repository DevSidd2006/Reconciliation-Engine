from kafka import KafkaProducer
import time
import json
from utils import generate_txn, apply_mismatch, choose_mismatch

TOPIC = "core_txns"
SOURCE = "core"

# Create Kafka producer with JSON serialization
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
            # Send to Kafka
            future = producer.send(TOPIC, value=txn, key=txn['txn_id'])
            producer.flush()  # Ensure message is sent
            print(f"[{SOURCE.upper()}] Sent → {txn} | Mismatch = {mismatch}")
        except Exception as e:
            print(f"[{SOURCE.upper()}] Failed to send → {txn} | Error: {e}")
        
        time.sleep(1)

except KeyboardInterrupt:
    print(f"\n🛑 {SOURCE} producer stopped")
finally:
    producer.close()