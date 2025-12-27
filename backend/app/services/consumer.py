import asyncio
import json
import logging
import os
from aiokafka import AIOKafkaConsumer
from services.reconciliation import reconciliation_service

logger = logging.getLogger(__name__)

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_TXNS = ["core_txns", "gateway_txns", "mobile_txns"]

async def consume_transactions():
    """
    Background task to consume transactions from Kafka
    """
    logger.info(f"Starting Kafka Consumer for topics: {KAFKA_TOPIC_TXNS}")
    
    consumer = AIOKafkaConsumer(
        *KAFKA_TOPIC_TXNS,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="reconciliation_engine_v1",
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset="latest" # Start from new messages
    )

    try:
        await consumer.start()
        logger.info("Kafka Consumer connected successfully")
        
        async for msg in consumer:
            try:
                data = msg.value
                logger.info(f"Received transaction from {msg.topic}: {data.get('txn_id')}")
                
                # Normalize source based on topic if not in data
                if 'source' not in data:
                    if 'core' in msg.topic: data['source'] = 'core'
                    elif 'mobile' in msg.topic: data['source'] = 'mobile'
                    elif 'gateway' in msg.topic: data['source'] = 'gateway'
                
                # Process
                await reconciliation_service.process_transaction(data)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                
    except Exception as e:
        logger.error(f"Failed to start Kafka Consumer: {e}")
        logger.warning("System running in 'API Only' mode without real-time Kafka ingestion.")
    finally:
        logger.info("Stopping Kafka Consumer...")
        try:
            await consumer.stop()
        except:
            pass
