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
            
            success = self.send_to_kafka_via_docker(topic, source_txn)
            
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
        print("🏦 Starting Realistic Banking Transaction Producer...")
        print("🔄 Simulating real-time Indian banking transactions with reconciliation")
        print("📊 Features: INR currency, Various channels, Realistic amounts, Banking workflows")
        print("Press Ctrl+C to stop\n")
        
        try:
            transaction_count = 0
            while True:
                transaction_count += 1
                print(f"📈 Transaction #{transaction_count}")
                self.send_coordinated_transaction()
                
                # Realistic banking transaction frequency (15-45 seconds between transactions)
                wait_time = random.uniform(15, 45)
                print(f"   ⏳ Next transaction in {wait_time:.1f}s...\n")
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Banking producer stopped after {transaction_count} transactions")
            print("📊 System ready for reconciliation analysis")

if __name__ == "__main__":
    producer = CoordinatedProducer()
    producer.run()