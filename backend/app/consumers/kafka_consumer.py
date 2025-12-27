import json
import sys
import os
import logging
from kafka import KafkaConsumer
from datetime import datetime

# Add the parent directory to the path so we can import from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from models.transaction import Transaction
from services.mismatch_service import ReconciliationEngine
from utils.redis import banking_deduplicator, cache_manager
from utils.db_retry import retry_db_operation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Kafka configuration
KAFKA_BROKER = "localhost:9092"
TOPIC = "transactions"

def save_transaction_to_db(txn_data):
    """Save transaction to PostgreSQL database with banking-grade Redis deduplication"""
    txn_id = txn_data['txn_id']
    source = txn_data['source']
    
    logger.info(f"Processing transaction: {txn_id} from {source}")
    
    # Use banking deduplicator for safe transaction processing
    should_process, reason = banking_deduplicator.process_transaction_safely(txn_id, source)
    
    if not should_process:
        logger.info(f"🔄 Transaction skipped: {txn_id} from {source} - {reason}")
        return
    
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
        
        # Use retry logic for database operations
        retry_db_operation(lambda: db.commit())
        
        # Mark as processed using banking deduplicator
        banking_deduplicator.mark_processed(txn_id, source)
        
        logger.info(f"💾 Successfully saved transaction {txn_id} to database")
        
        # Invalidate cache to ensure fresh stats
        cache_manager.invalidate_cache("transactions", "stats")
        
        # Run reconciliation engine to detect mismatches
        engine = ReconciliationEngine(db)
        mismatches = engine.detect_mismatches(transaction.txn_id)
        
        if mismatches:
            logger.warning(f"⚠️ MISMATCHES FOUND for {transaction.txn_id}: {mismatches}")
            # Invalidate mismatch cache when new mismatches are found
            cache_manager.invalidate_cache("mismatches", "stats")
        else:
            logger.debug(f"✔ Transaction clean: {transaction.txn_id}")
        
    except Exception as e:
        logger.error(f"❌ Error saving transaction {txn_id}: {e}")
        db.rollback()
        raise
    finally:
        # Always release in-flight lock
        banking_deduplicator.release_inflight(txn_id, source)
        db.close()

def start_consumer():
    """Start banking-grade Kafka consumer with Redis deduplication"""
    logger.info("📥 Starting banking-grade Kafka consumer...")
    
    # Create Kafka consumer
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',  # Start from beginning of topic
        group_id='reconciliation-consumer',
        enable_auto_commit=True,
        auto_commit_interval_ms=1000
    )
    
    logger.info(f"📥 Listening for messages on topic '{TOPIC}' with deduplication...")
    
    try:
        for message in consumer:
            txn_data = message.value
            logger.debug(f"📥 Received message from Kafka: {txn_data}")
            
            # Save to database with deduplication
            try:
                save_transaction_to_db(txn_data)
            except Exception as e:
                logger.error(f"Failed to process transaction {txn_data.get('txn_id', 'unknown')}: {e}")
                # Continue processing other messages
                continue
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Consumer stopped by user")
    except Exception as e:
        logger.error(f"❌ Consumer error: {e}")
        raise
    finally:
        logger.info("Closing Kafka consumer...")
        consumer.close()
        
        # Log final in-flight status
        inflight_count = banking_deduplicator.get_inflight_count()
        if inflight_count > 0:
            logger.warning(f"Consumer stopped with {inflight_count} transactions still in-flight")
        else:
            logger.info("Consumer stopped cleanly with no in-flight transactions")

if __name__ == "__main__":
    start_consumer()