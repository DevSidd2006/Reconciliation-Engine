# Producer Scripts

These scripts simulate banking systems that generate transaction events with intentional mismatches for testing the reconciliation engine.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure Kafka is running (from the kafka directory):
```bash
docker-compose up -d
```

3. Register the schema (from the kafka directory):
```bash
python register_schema.py
```

## Running the Producers

Run each producer in a separate terminal:

```bash
# Terminal 1 - Core Banking System
python core_producer.py

# Terminal 2 - Payment Gateway
python gateway_producer.py

# Terminal 3 - Mobile App
python mobile_producer.py
```

## What Each Producer Does

- **core_producer.py**: Simulates core banking system transactions
- **gateway_producer.py**: Simulates payment gateway transactions  
- **mobile_producer.py**: Simulates mobile app transactions

Each producer:
- Generates random transaction events
- Intentionally injects mismatches (amount, status, timing, etc.)
- Sends events to separate Kafka topics
- Uses Avro schema for data validation
- Runs continuously with different intervals to simulate real-world timing

## Mismatch Types

The producers simulate these realistic banking mismatches:
- **AMOUNT_MISMATCH**: Different amounts between systems
- **STATUS_MISMATCH**: Different transaction statuses
- **TIME_MISMATCH**: Timestamp differences
- **CURRENCY_MISMATCH**: Currency code differences
- **MISSING_FIELD**: Missing required fields
- **WRONG_ACCOUNT**: Account ID mismatches
- **WRONG_SCHEMA**: Invalid data structure
- **DUPLICATE**: Duplicate transactions