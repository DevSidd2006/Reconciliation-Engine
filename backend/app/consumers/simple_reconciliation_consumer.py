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

try:
    from services.real_reconciliation_service import reconciliation_engine
except ImportError:
    from app.services.real_reconciliation_service import reconciliation_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def consume_topic(topic_name):
    """Consume messages from a specific Kafka topic"""
    logger.info(f"🚀 Starting consumer for {topic_name}")
    
    cmd = [
        "docker", "exec", "kafka-kafka-1",
        "kafka-console-consumer",
        "--bootstrap-server", "localhost:9092",
        "--topic", topic_name,
        "--from-beginning"
    ]
    
    try:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            encoding='utf-8',
            errors='ignore',
            bufsize=1
        )
        
        logger.info(f"✅ Consumer started for {topic_name}")
        
        while True:
            line = process.stdout.readline()
            if line:
                line = line.strip()
                if line:
                    try:
                        transaction = json.loads(line)
                        logger.info(f"📥 [{topic_name}] Received: {transaction.get('txn_id', 'unknown')}")
                        
                        # Save to database
                        try:
                            try:
                                from services.database_service import db_service
                            except ImportError:
                                from app.services.database_service import db_service
                            db_service.save_transaction(transaction)
                        except Exception as e:
                            logger.warning(f"Failed to save transaction to database: {e}")
                        
                        # Add to reconciliation engine
                        reconciliation_engine.add_transaction(transaction)
                        
                    except json.JSONDecodeError:
                        logger.warning(f"❌ [{topic_name}] Invalid JSON: {line}")
                    except Exception as e:
                        logger.error(f"❌ [{topic_name}] Error: {e}")
            
            # Check if process ended
            if process.poll() is not None:
                break
                
    except Exception as e:
        logger.error(f"❌ Consumer error for {topic_name}: {e}")
    finally:
        if 'process' in locals():
            process.terminate()

def main():
    """Start consumers for all topics"""
    topics = ['core_txns', 'gateway_txns', 'mobile_txns']
    
    logger.info("🚀 Starting Simple Reconciliation Consumer...")
    
    # Start a thread for each topic
    threads = []
    for topic in topics:
        thread = threading.Thread(target=consume_topic, args=(topic,), daemon=True)
        thread.start()
        threads.append(thread)
        time.sleep(1)  # Small delay between starting consumers
    
    logger.info(f"✅ Started consumers for all topics: {topics}")
    
    try:
        # Print stats every 10 seconds
        while True:
            time.sleep(10)
            stats = reconciliation_engine.get_statistics()
            logger.info(f"📊 STATS: Reconciled={stats['total_reconciled']}, "
                       f"Mismatches={stats['total_mismatches']}, "
                       f"Pending={stats['pending_reconciliation']}, "
                       f"Success Rate={stats['success_rate']}%")
            
            # Show recent reconciliation results
            recent = reconciliation_engine.get_recent_reconciled(3)
            if recent:
                logger.info("🔍 Recent reconciliations:")
                for r in recent[-3:]:
                    status_emoji = "✅" if r['status'] == 'MATCHED' else "❌"
                    logger.info(f"   {status_emoji} {r['txn_id']}: {r['status']} ({len(r['sources'])} sources)")
            
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down consumers...")
    except Exception as e:
        logger.error(f"❌ Main loop error: {e}")

if __name__ == "__main__":
    main()