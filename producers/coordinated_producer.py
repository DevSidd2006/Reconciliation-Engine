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
        
    def send_to_kafka_via_docker(self, topic, message):
        """Send message to Kafka using docker exec"""
        try:
            json_message = json.dumps(message)
            
            cmd = [
                "docker", "exec", "-i", "kafka-kafka-1",
                "kafka-console-producer",
                "--bootstrap-server", "localhost:9092",
                "--topic", topic
            ]
            
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(input=json_message)
            
            return process.returncode == 0
        except Exception as e:
            print(f"Exception sending message: {e}")
            return False
    
    def generate_base_transaction(self):
        """Generate a base transaction that will be sent to multiple sources"""
        return {
            "txn_id": str(uuid.uuid4()),
            "amount": round(random.uniform(100, 2000), 2),
            "status": random.choice(["SUCCESS", "FAILED", "PENDING"]),
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "currency": "INR",
            "account_id": str(random.randint(100000, 999999)),
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
        
        print(f"\n🔄 Creating coordinated transaction: {base_txn['txn_id']}")
        print(f"   Base amount: ₹{base_txn['amount']}, Status: {base_txn['status']}")
        
        # Decide which sources will receive this transaction (2-3 sources)
        available_sources = list(self.topics.keys())
        num_sources = random.choice([2, 3])  # Send to 2 or 3 sources
        selected_sources = random.sample(available_sources, num_sources)
        
        print(f"   Sending to sources: {selected_sources}")
        
        # Send to each selected source
        for source in selected_sources:
            source_txn, mismatch = self.create_source_transaction(base_txn, source)
            topic = self.topics[source]
            
            success = self.send_to_kafka_via_docker(topic, source_txn)
            
            if success:
                print(f"   ✅ [{source.upper()}] Sent → Amount: ₹{source_txn['amount']}, Status: {source_txn['status']}, Mismatch: {mismatch}")
            else:
                print(f"   ❌ [{source.upper()}] Failed to send")
            
            # Small delay between sources to simulate real-world timing
            time.sleep(random.uniform(0.5, 2.0))
    
    def run(self):
        """Run the coordinated producer"""
        print("🚀 Starting Coordinated Transaction Producer...")
        print("This will create transactions with the same txn_id across multiple sources")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.send_coordinated_transaction()
                
                # Wait before next transaction (30-60 seconds for very slow observation)
                wait_time = random.uniform(30, 60)
                print(f"   ⏳ Waiting {wait_time:.1f}s before next transaction...\n")
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            print("\n🛑 Coordinated producer stopped")

if __name__ == "__main__":
    producer = CoordinatedProducer()
    producer.run()