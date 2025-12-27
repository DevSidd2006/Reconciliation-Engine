from confluent_kafka import Producer
import time
import json
from utils import generate_txn, apply_mismatch, choose_mismatch

TOPIC = "core_txns"
SOURCE = "core"

producer = Producer({"bootstrap.servers": "localhost:9092"})

def serialize_json(record):
    return json.dumps(record).encode('utf-8')

while True:
    mismatch = choose_mismatch()
    txn = generate_txn(SOURCE)
    
    if mismatch != "CORRECT":
        txn = apply_mismatch(txn, mismatch)
    
    try:
        serialized_data = serialize_json(txn)
        producer.produce(TOPIC, serialized_data)
        print(f"[CORE] Sent → {txn} | Mismatch = {mismatch}")
    except Exception as e:
        print(f"[CORE] Failed to send → {txn} | Mismatch = {mismatch} | Error: {e}")
    
    producer.flush()
    time.sleep(1)