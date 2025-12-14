import subprocess
import json
import threading
import time
import logging
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.real_reconciliation_service import reconciliation_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealKafkaConsumer:
    def __init__(self):
        self.topics = ['core_txns', 'gateway_txns', 'mobile_txns']
        self.consumers = {}
        self.running = False
        
    def start_consumer_for_topic(self, topic: str):
        """Start a consumer for a specific topic"""
        def consume():
            cmd = [
                "docker", "exec", "-i", "kafka-kafka-1",
                "kafka-console-consumer",
                "--bootstrap-server", "localhost:9092",
                "--topic", topic,
                "--from-beginning"
            ]
            
            try:
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                logger.info(f"Started consumer for topic: {topic}")
                
                while self.running:
                    line = process.stdout.readline()
                    if line:
                        try:
                            # Parse JSON transaction
                            transaction = json.loads(line.strip())
                            logger.info(f"Received from {topic}: {transaction.get('txn_id', 'unknown')}")
                            
                            # Add to reconciliation engine
                            reconciliation_engine.add_transaction(transaction)
                            
                        except json.JSONDecodeError as e:
                            logger.warning(f"Invalid JSON from {topic}: {line.strip()}")
                        except Exception as e:
                            logger.error(f"Error processing message from {topic}: {e}")
                    
                    if process.poll() is not None:
                        break
                        
            except Exception as e:
                logger.error(f"Consumer error for {topic}: {e}")
            finally:
                if 'process' in locals():
                    process.terminate()
        
        # Start consumer in separate thread
        thread = threading.Thread(target=consume, daemon=True)
        thread.start()
        self.consumers[topic] = thread
        
    def start_all_consumers(self):
        """Start consumers for all topics"""
        self.running = True
        logger.info("Starting Kafka consumers for all topics...")
        
        for topic in self.topics:
            self.start_consumer_for_topic(topic)
            time.sleep(1)  # Small delay between starting consumers
        
        logger.info(f"Started consumers for topics: {self.topics}")
        
    def stop_all_consumers(self):
        """Stop all consumers"""
        self.running = False
        logger.info("Stopping all Kafka consumers...")
        
        # Wait for threads to finish
        for topic, thread in self.consumers.items():
            if thread.is_alive():
                thread.join(timeout=5)
        
        logger.info("All consumers stopped")
        
    def get_status(self):
        """Get consumer status"""
        return {
            'running': self.running,
            'topics': self.topics,
            'active_consumers': len([t for t in self.consumers.values() if t.is_alive()])
        }

# Global consumer instance
kafka_consumer = RealKafkaConsumer()

def start_reconciliation_consumer():
    """Start the reconciliation consumer service"""
    logger.info("🚀 Starting Real-Time Reconciliation Consumer...")
    
    try:
        kafka_consumer.start_all_consumers()
        
        # Keep the main thread alive
        while True:
            time.sleep(10)
            
            # Print status every 10 seconds
            stats = reconciliation_engine.get_statistics()
            logger.info(f"📊 Stats: Reconciled={stats['total_reconciled']}, "
                       f"Mismatches={stats['total_mismatches']}, "
                       f"Pending={stats['pending_reconciliation']}, "
                       f"Success Rate={stats['success_rate']}%")
            
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down reconciliation consumer...")
        kafka_consumer.stop_all_consumers()
    except Exception as e:
        logger.error(f"❌ Consumer error: {e}")
        kafka_consumer.stop_all_consumers()

if __name__ == "__main__":
    start_reconciliation_consumer()