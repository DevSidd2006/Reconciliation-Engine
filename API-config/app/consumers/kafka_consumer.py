import json
import logging
from datetime import datetime

from kafka import KafkaConsumer

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.transaction import Transaction

# Kafka configuration
KAFKA_BROKER = "localhost:9092"
TOPIC = "transactions"

logger = logging.getLogger("kafka.consumer")


def save_transaction_to_db(txn_data):
    """Save transaction to PostgreSQL database"""
    db = SessionLocal()
    try:
        timestamp = None
        if txn_data.get("timestamp"):
            timestamp = datetime.fromisoformat(txn_data["timestamp"].replace("Z", "+00:00"))

        transaction = Transaction(
            txn_id=txn_data["txn_id"],
            amount=txn_data["amount"],
            source=txn_data["source"],
            timestamp=timestamp,
            status="SUCCESS",
            currency="USD",
            account_id=None,
        )

        db.add(transaction)
        db.commit()
        logger.info("Saved transaction %s to database", txn_data["txn_id"])

    except Exception as e:
        logger.exception("Error saving transaction %s", txn_data.get("txn_id"))
        db.rollback()
    finally:
        db.close()


def start_consumer():
    """Start Kafka consumer to receive transactions"""
    logger.info("Connecting to Kafka at %s", KAFKA_BROKER)

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id="reconciliation-consumer",
    )

    logger.info("Listening for messages on topic '%s'...", TOPIC)

    try:
        for message in consumer:
            txn_data = message.value
            logger.debug("Received message from Kafka: %s", txn_data)
            save_transaction_to_db(txn_data)

    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
    except Exception as e:
        logger.exception("Consumer error")
    finally:
        consumer.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    start_consumer()