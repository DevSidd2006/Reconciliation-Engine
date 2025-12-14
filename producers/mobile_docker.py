import subprocess
import time
import json
from utils import generate_txn, apply_mismatch, choose_mismatch

SOURCE = "mobile"
TOPIC = "mobile_txns"

print(f"🚀 Starting {SOURCE} producer (Docker mode)...")
print("Press Ctrl+C to stop")

def send_to_kafka_via_docker(topic, message):
    """Send message to Kafka using docker exec"""
    try:
        # Convert message to JSON string
        json_message = json.dumps(message)
        
        # Use docker exec to send message via kafka-console-producer
        cmd = [
            "docker", "exec", "-i", "kafka-kafka-1",
            "kafka-console-producer",
            "--bootstrap-server", "localhost:9092",
            "--topic", topic
        ]
        
        # Run the command and send the message via stdin
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input=json_message)
        
        if process.returncode == 0:
            return True
        else:
            print(f"Error sending message: {stderr}")
            return False
            
    except Exception as e:
        print(f"Exception sending message: {e}")
        return False

try:
    while True:
        mismatch = choose_mismatch()
        txn = generate_txn(SOURCE)
        
        if mismatch != "CORRECT":
            txn = apply_mismatch(txn, mismatch)
        
        # Send to Kafka via Docker
        success = send_to_kafka_via_docker(TOPIC, txn)
        
        if success:
            print(f"[{SOURCE.upper()}] Sent → {txn} | Mismatch = {mismatch}")
        else:
            print(f"[{SOURCE.upper()}] Failed → {txn} | Mismatch = {mismatch}")
        
        time.sleep(1.4)  # Different timing than core and gateway

except KeyboardInterrupt:
    print(f"\n🛑 {SOURCE} producer stopped")