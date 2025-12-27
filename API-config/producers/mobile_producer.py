from confluent_kafka import Producer
import time
import json
from fastavro import schemaless_writer
from io import BytesIO
from utils import generate_txn, apply_mismatch, choose_mismatch

TOPIC = "mobile_txns"
SOURCE = "mobile"
schema_id = 2  # updated schema with nullable fields

producer = Producer({"bootstrap.servers": "localhost:9092"})

def serialize(record):
    out = BytesIO()
    from fastavro import parse_schema
    with open("../kafka/schemas/transaction.avsc") as f:
        schema = parse_schema(json.load(f))
    schemaless_writer(out, schema, record)
    return bytes([0, 0, 0, 0, schema_id]) + out.getvalue()

while True:
    mismatch = choose_mismatch()
    txn = generate_txn(SOURCE)
    
    if mismatch != "CORRECT":
        txn = apply_mismatch(txn, mismatch)
    
    try:
        serialized_data = serialize(txn)
        producer.produce(TOPIC, serialized_data)
        print(f"[MOBILE] Sent → {txn} | Mismatch = {mismatch}")
    except Exception as e:
        print(f"[MOBILE] Schema validation failed → {txn} | Mismatch = {mismatch} | Error: {e}")
    
    producer.flush()
    time.sleep(1.4)