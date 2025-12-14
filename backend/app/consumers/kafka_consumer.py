import json
import sys
import os
from kafka import KafkaConsumer
from datetime import datetime

# Add the parent directory to the path so we can import from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from models.transaction import Transaction

# Kafka configuration
KAFKA_BROKER = "localhost:9092"
TOPIC = "transactions"

def save_transaction_to_db(txn_data):
    """Save transaction to PostgreSQL database"""
    db = SessionLocal()
    try:
        # Parse timestamp
        timestamp = None
        if txn_data.get('timestamp'):
            timestamp = datetime.fromisoformat(txn_data['timestamp'].replace('Z', '+00:00'))
        
        # Create transaction record
        transaction = Transaction(
            txn_id=txn_data['txn_id'],
            amount=txn_data['amount'],
            source=txn_data['source'],
            timestamp=timestamp,
            status="SUCCESS",  # Default status
            currency="USD",    # Default currency
            account_id=None    # Will be null for now
        )
        
        db.add(transaction)
        db.commit()
        print(f"💾 Saved transaction {txn_data['txn_id']} to database")
        
    except Exception as e:
        print(f"❌ Error saving transaction: {e}")
        db.rollback()
    finally:
        db.close()

def start_consumer():
    """Start Kafka consumer to receive transactions"""
    print("📥 Connected to Kafka...")
    
    # Create Kafka consumer
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',  # Start from beginning of topic
        group_id='reconciliation-consumer'
    )
    
    print(f"📥 Listening for messages on topic '{TOPIC}'...")
    
    try:
        for message in consumer:
            txn_data = message.value
            print(f"📥 Received message from Kafka: {txn_data}")
            
            # Save to database
            save_transaction_to_db(txn_data)
            
    except KeyboardInterrupt:
        print("\n🛑 Consumer stopped by user")
    except Exception as e:
        print(f"❌ Consumer error: {e}")
    finally:
        consumer.close()

if __name__ == "__main__":
    start_consumer()