import json
import time
import random
from kafka import KafkaProducer
from datetime import datetime

# Kafka configuration
KAFKA_BROKER = "localhost:9092"
TOPIC = "transactions"

# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def generate_transaction():
    return {
        "txn_id": f"TXN{random.randint(100000, 999999)}",
        "amount": round(random.uniform(10, 5000), 2),
        "source": random.choice(["mobile", "gateway", "core"]),
        "timestamp": datetime.utcnow().isoformat()
    }

def start_producing():
    print("🚀 Sending JSON transactions to Kafka... Press CTRL+C to stop.")
    
    while True:
        txn = generate_transaction()
        producer.send(TOPIC, txn)
        print(f"✔ Sent → {txn}")
        time.sleep(1)  # send 1 transaction per second

if __name__ == "__main__":
    start_producing()