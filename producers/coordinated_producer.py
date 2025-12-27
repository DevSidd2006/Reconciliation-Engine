from confluent_kafka import Producer
import time
import json
import os
import random
import uuid
from datetime import datetime
import pytz

TOPICS = ["core_txns", "gateway_txns", "mobile_txns"]
SOURCES = ["core", "gateway", "mobile"]

bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

# Simple mismatch types (reduced set)
MISMATCH_TYPES = ["CORRECT", "AMOUNT_MISMATCH", "STATUS_MISMATCH", "MISSING_FIELD"]
MISMATCH_WEIGHTS = [85, 7, 4, 4]  # 85% correct, 15% mismatches

def choose_mismatch():
    """Choose mismatch type with weights"""
    return random.choices(MISMATCH_TYPES, weights=MISMATCH_WEIGHTS, k=1)[0]

def generate_simple_txn(source):
    """Generate simple transaction (original format before complex banking)"""
    # Use local time without timezone info to avoid UTC conversion
    current_time = datetime.now()
    
    return {
        "txn_id": str(uuid.uuid4()),
        "amount": round(random.uniform(100, 10000), 2),
        "status": random.choice(["SUCCESS", "PENDING", "FAILED"]),
        "timestamp": current_time.isoformat(),
        "currency": "INR",
        "account_id": str(random.randint(100000000, 999999999)),
        "source": source
    }

def apply_simple_mismatch(txn, mismatch_type):
    """Apply simple mismatches to transaction"""
    if mismatch_type == "AMOUNT_MISMATCH":
        # Small amount difference
        variance = random.uniform(1, 50)
        txn["amount"] = round(txn["amount"] + variance, 2)
    elif mismatch_type == "STATUS_MISMATCH":
        # Different status
        current_status = txn["status"]
        if current_status == "SUCCESS":
            txn["status"] = "PENDING"
        elif current_status == "PENDING":
            txn["status"] = "SUCCESS"
        else:
            txn["status"] = "PENDING"
    elif mismatch_type == "MISSING_FIELD":
        # Remove account_id
        txn["account_id"] = None
    
    return txn

def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}", flush=True)
    else:
        print(
            f"✅ Delivered to {msg.topic()} [{msg.partition()}]",
            flush=True
        )

producer = Producer({
    "bootstrap.servers": bootstrap_servers,
    "acks": "all"
})

def serialize_json(record):
    return json.dumps(record).encode("utf-8")

print("🚀 Starting Simple Coordinated Producer...", flush=True)
print(f"🔗 Kafka: {bootstrap_servers}", flush=True)

while True:
    # Generate base transaction using simple format
    base_txn = generate_simple_txn("coordinated")
    
    # Send to multiple sources (2-3 sources per transaction)
    selected_sources = random.sample(
        list(zip(SOURCES, TOPICS)),
        random.choice([2, 3])
    )
    
    print(f"\n[COORDINATED] TXN {base_txn['txn_id']}", flush=True)
    
    for source, topic in selected_sources:
        # Create source-specific transaction
        mismatch = choose_mismatch()
        txn = base_txn.copy()
        txn["source"] = source
        
        if mismatch != "CORRECT":
            txn = apply_simple_mismatch(txn, mismatch)
        
        producer.produce(
            topic,
            serialize_json(txn),
            on_delivery=delivery_report
        )
        
        # Critical for message delivery
        producer.poll(0)
        
        print(
            f"[{source.upper()}] → {topic} | mismatch={mismatch}",
            flush=True
        )
    
    time.sleep(2)