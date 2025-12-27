import subprocess
import time
import json
import uuid
import random
from datetime import datetime, timedelta, timezone
from utils import apply_mismatch, choose_mismatch

class CoordinatedProducer:
    """Producer that creates the same transaction across multiple sources for real reconciliation"""
    
    def __init__(self):
        self.topics = {
            'core': 'core_txns',
            'gateway': 'gateway_txns', 
            'mobile': 'mobile_txns'
        }
        
    def test_kafka_connection(self):
        """Test Kafka connectivity before starting production"""
        try:
            import os
            from confluent_kafka import Consumer
            
            bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
            print(f"🔍 Testing Kafka connection to: {bootstrap_servers}", flush=True)
            
            # Create a simple consumer to test connection and list topics
            conf = {
                'bootstrap.servers': bootstrap_servers,
                'group.id': 'test-group',
                'auto.offset.reset': 'earliest',
                'session.timeout.ms': 10000,
                'request.timeout.ms': 10000
            }
            
            consumer = Consumer(conf)
            
            # Get cluster metadata to verify connection
            metadata = consumer.list_topics(timeout=10)
            available_topics = list(metadata.topics.keys())
            consumer.close()
            
            print(f"✅ Kafka connection successful!", flush=True)
            print(f"📋 Available topics: {available_topics}", flush=True)
            
            # Check if our required topics exist
            required_topics = list(self.topics.values())
            missing_topics = [t for t in required_topics if t not in available_topics]
            
            if missing_topics:
                print(f"⚠️  Missing topics: {missing_topics}", flush=True)
                print(f"🔧 These topics will be auto-created on first message", flush=True)
            else:
                print(f"✅ All required topics exist: {required_topics}", flush=True)
            
            return True
            
        except Exception as e:
            print(f"❌ Kafka connection test failed: {str(e)}", flush=True)
            print(f"❌ Exception type: {type(e).__name__}", flush=True)
            return False
        
    def send_to_kafka(self, topic, message):
        """Send message to Kafka using confluent-kafka client"""
        try:
            import os
            import json
            from confluent_kafka import Producer
            
            # Get Kafka bootstrap servers from environment or use default
            bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
            print(f"🔗 Connecting to Kafka at: {bootstrap_servers}", flush=True)
            
            # Configure Confluent Kafka producer
            conf = {
                'bootstrap.servers': bootstrap_servers,
                'client.id': 'banking-producer',
                'acks': 'all',
                'retries': 5,
                'retry.backoff.ms': 1000,
                'request.timeout.ms': 30000,
                'delivery.timeout.ms': 60000,
                'compression.type': 'gzip',
                'linger.ms': 100,  # Allow batching
                'batch.size': 16384  # Batch size
            }
            
            producer = Producer(conf)
            
            print(f"📤 Sending message to topic: {topic}", flush=True)
            
            # Serialize message to JSON
            message_json = json.dumps(message)
            
            # Callback function to handle delivery reports
            def delivery_callback(err, msg):
                if err:
                    print(f"❌ Message delivery failed: {err}", flush=True)
                else:
                    print(f"✅ Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}", flush=True)
            
            # Send message with callback
            producer.produce(topic, value=message_json, callback=delivery_callback)
            
            # Wait for message to be delivered with longer timeout
            remaining_messages = producer.flush(timeout=60)  # 60 second timeout
            
            if remaining_messages > 0:
                print(f"⚠️ {remaining_messages} messages still in queue after flush", flush=True)
                return False
            else:
                print(f"✅ Message sent to {topic} successfully", flush=True)
                return True
            
        except Exception as e:
            print(f"❌ Exception sending message to {topic}: {str(e)}", flush=True)
            print(f"❌ Exception type: {type(e).__name__}", flush=True)
            return False
    
    def generate_base_transaction(self):
        """Generate a realistic base banking transaction"""
        from utils import generate_realistic_amount, choose_realistic_status, choose_realistic_currency, TRANSACTION_TYPES, CHANNELS, BANK_CODES
        
        return {
            "txn_id": str(uuid.uuid4()),
            "amount": generate_realistic_amount(),
            "status": choose_realistic_status(),
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "currency": choose_realistic_currency(),
            "account_id": str(random.randint(100000000, 999999999)),  # 9-digit account numbers
            "transaction_type": random.choice(TRANSACTION_TYPES),
            "channel": random.choice(CHANNELS),
            "bank_code": random.choice(BANK_CODES),
            "reference_number": f"REF{random.randint(100000000, 999999999)}",
            "merchant_id": f"MER{random.randint(10000, 99999)}" if random.random() < 0.3 else None,
            "description": f"Banking transaction via {random.choice(CHANNELS)}",
            "batch_id": f"BATCH{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}",
        }
    
    def create_source_transaction(self, base_txn, source):
        """Create a source-specific transaction with potential mismatches"""
        txn = base_txn.copy()
        txn["source"] = source
        
        # Decide if this source should have a mismatch
        mismatch_type = choose_mismatch()
        
        if mismatch_type != "CORRECT":
            txn = apply_mismatch(txn, mismatch_type)
            print(f"[{source.upper()}] Applied mismatch: {mismatch_type}")
        
        return txn, mismatch_type
    
    def send_coordinated_transaction(self):
        """Send the same transaction to multiple sources with potential mismatches"""
        base_txn = self.generate_base_transaction()
        
        print(f"\n🏦 Creating banking transaction: {base_txn['txn_id']}")
        print(f"   💰 Amount: ₹{base_txn['amount']:,.2f} {base_txn['currency']}")
        print(f"   📊 Status: {base_txn['status']} | Type: {base_txn['transaction_type']}")
        print(f"   🏛️  Bank: {base_txn['bank_code']} | Channel: {base_txn['channel']}")
        print(f"   🔢 Account: {base_txn['account_id']} | Ref: {base_txn['reference_number']}")
        
        # Decide which sources will receive this transaction (2-3 sources for reconciliation)
        available_sources = list(self.topics.keys())
        num_sources = random.choice([2, 3])  # Banking systems typically have 2-3 source systems
        selected_sources = random.sample(available_sources, num_sources)
        
        print(f"   🔄 Processing through systems: {selected_sources}")
        
        # Send to each selected source with realistic timing
        for i, source in enumerate(selected_sources):
            source_txn, mismatch = self.create_source_transaction(base_txn, source)
            topic = self.topics[source]
            
            # Add source-specific fields
            source_txn["processing_time"] = datetime.now().isoformat()
            source_txn["source_system_id"] = f"{source.upper()}_SYS_{random.randint(100, 999)}"
            
            success = self.send_to_kafka(topic, source_txn)
            
            if success:
                mismatch_emoji = "✅" if mismatch == "CORRECT" else "⚠️"
                print(f"   {mismatch_emoji} [{source.upper()}] ₹{source_txn['amount']:,.2f} | {source_txn['status']} | {mismatch}")
            else:
                print(f"   ❌ [{source.upper()}] Failed to process transaction")
            
            # Realistic inter-system processing delay
            if i < len(selected_sources) - 1:  # Don't delay after last source
                delay = random.uniform(0.5, 3.0)  # 0.5-3 second realistic processing delay
                time.sleep(delay)
    
    def run(self):
        """Run the realistic banking transaction producer"""
        print("🏦 Starting Realistic Banking Transaction Producer...", flush=True)
        print("🔄 Simulating real-time Indian banking transactions with reconciliation", flush=True)
        print("📊 Features: INR currency, Various channels, Realistic amounts, Banking workflows", flush=True)
        
        # Test Kafka connection first
        print("\n🔍 Testing Kafka connectivity...", flush=True)
        if not self.test_kafka_connection():
            print("❌ Kafka connection failed. Retrying in 30 seconds...", flush=True)
            time.sleep(30)
            if not self.test_kafka_connection():
                print("❌ Kafka connection failed again. Exiting...", flush=True)
                return
        
        print("Press Ctrl+C to stop\n", flush=True)
        
        try:
            transaction_count = 0
            while True:
                transaction_count += 1
                print(f"� Tranasaction #{transaction_count}", flush=True)
                self.send_coordinated_transaction()
                
                # Realistic banking transaction frequency (15-45 seconds between transactions)
                wait_time = random.uniform(15, 45)
                print(f"   ⏳ Next transaction in {wait_time:.1f}s...\n", flush=True)
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Banking producer stopped after {transaction_count} transactions", flush=True)
            print("📊 System ready for reconciliation analysis", flush=True)
        except Exception as e:
            print(f"❌ Producer error: {e}", flush=True)
            raise

if __name__ == "__main__":
    producer = CoordinatedProducer()
    producer.run()