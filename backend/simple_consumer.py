import subprocess
import json
import time
from datetime import datetime

def consume_from_kafka(topic):
    """Consume messages from Kafka using docker exec"""
    cmd = [
        "docker", "exec", "-i", "kafka-kafka-1",
        "kafka-console-consumer",
        "--bootstrap-server", "localhost:9092",
        "--topic", topic,
        "--from-beginning"
    ]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print(f"📥 Listening to topic: {topic}")
        
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                try:
                    # Parse JSON message
                    transaction = json.loads(line.strip())
                    print(f"📥 [{topic}] Received: {transaction}")
                    
                    # Here you would normally save to database
                    # For now, just print
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON: {line.strip()}")
                    
    except KeyboardInterrupt:
        print(f"\n🛑 Consumer for {topic} stopped")
        process.terminate()
    except Exception as e:
        print(f"❌ Consumer error: {e}")

if __name__ == "__main__":
    # For now, just consume from core_txns
    # In a real system, you'd consume from all topics simultaneously
    consume_from_kafka("core_txns")