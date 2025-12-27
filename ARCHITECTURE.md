# Banking Reconciliation Engine - Architecture

## System Architecture Overview

### Current Simulated Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    SIMULATED BANKING SYSTEM                      │
└─────────────────────────────────────────────────────────────────┘

    coordinated_producer.py
    (Generates fake transactions)
            │
            ├─→ core_txns (Kafka Topic)
            ├─→ gateway_txns (Kafka Topic)
            └─→ mobile_txns (Kafka Topic)
                    │
                    ↓
        simple_reconciliation_consumer.py
                    │
                    ↓
        ┌───────────────────────────┐
        │ Reconciliation Engine      │
        │ - Match transactions      │
        │ - Detect mismatches       │
        │ - Calculate accuracy      │
        └───────────────────────────┘
                    │
                    ↓
        ┌───────────────────────────┐
        │ PostgreSQL Database       │
        │ - Transactions            │
        │ - Mismatches              │
        │ - Reconciliation Results  │
        └───────────────────────────┘
                    │
                    ↓
        ┌───────────────────────────┐
        │ React Frontend Dashboard  │
        │ - Real-time monitoring    │
        │ - Analytics & reports     │
        │ - Professional UI         │
        └───────────────────────────┘
```

---

## Real Banking Architecture (Target)

```
┌──────────────────────────────────────────────────────────────────────┐
│                      REAL BANKING SYSTEMS                             │
└──────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │ HDFC Bank   │
    │ REST API    │
    └──────┬──────┘
           │
    ┌─────────────┐
    │ ICICI Bank  │
    │ REST API    │
    └──────┬──────┘
           │
    ┌─────────────┐
    │ SBI         │
    │ OAuth 2.0   │
    └──────┬──────┘
           │
    ┌─────────────┐
    │ Razorpay    │
    │ REST API    │
    └──────┬──────┘
           │
    ┌─────────────┐
    │ Axis Bank   │
    │ SFTP Files  │
    └──────┬──────┘
           │
           ↓
    ┌──────────────────────────┐
    │   bank_adapter.py        │
    │ - Fetch from APIs        │
    │ - Transform data         │
    │ - Handle errors          │
    │ - Retry logic            │
    └──────────┬───────────────┘
               │
               ├─→ hdfc_txns (Kafka Topic)
               ├─→ icici_txns (Kafka Topic)
               ├─→ sbi_txns (Kafka Topic)
               ├─→ razorpay_txns (Kafka Topic)
               └─→ axis_txns (Kafka Topic)
                       │
                       ↓
        ┌──────────────────────────────┐
        │ bank_reconciliation_consumer │
        │ - Consume from Kafka         │
        │ - Validate data              │
        │ - Store in database          │
        └──────────┬───────────────────┘
                   │
                   ↓
        ┌──────────────────────────────┐
        │ Reconciliation Engine        │
        │ - Match transactions         │
        │ - Detect mismatches          │
        │ - Calculate accuracy         │
        │ - Generate reports           │
        └──────────┬───────────────────┘
                   │
                   ↓
        ┌──────────────────────────────┐
        │ PostgreSQL Database          │
        │ - Real transactions          │
        │ - Reconciliation results     │
        │ - Audit logs                 │
        └──────────┬───────────────────┘
                   │
                   ↓
        ┌──────────────────────────────┐
        │ React Frontend Dashboard     │
        │ - Real-time monitoring       │
        │ - Bank-wise analytics        │
        │ - Professional UI            │
        │ - Theme toggle               │
        └──────────────────────────────┘
```

---

## Component Details

### 1. Data Sources (Banks)

```
┌─────────────────────────────────────────────────────────────┐
│                    BANK DATA SOURCES                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  HDFC Bank                                                   │
│  ├─ API Type: REST                                          │
│  ├─ Auth: OAuth 2.0 Bearer Token                            │
│  ├─ Endpoint: https://api.hdfcbank.com/v1/transactions      │
│  └─ Rate Limit: 1000 req/hour                               │
│                                                               │
│  ICICI Bank                                                  │
│  ├─ API Type: REST                                          │
│  ├─ Auth: API Key + Bearer Token                            │
│  ├─ Endpoint: https://api.icicibank.com/v2/transactions     │
│  └─ Rate Limit: 500 req/hour                                │
│                                                               │
│  SBI (State Bank of India)                                   │
│  ├─ API Type: REST                                          │
│  ├─ Auth: OAuth 2.0                                         │
│  ├─ Endpoint: https://api.sbi.co.in/api/v1/transactions     │
│  └─ Rate Limit: 2000 req/hour                               │
│                                                               │
│  Razorpay (Payment Gateway)                                  │
│  ├─ API Type: REST                                          │
│  ├─ Auth: Basic Auth (Key + Secret)                         │
│  ├─ Endpoint: https://api.razorpay.com/v1/payments          │
│  └─ Rate Limit: Unlimited                                   │
│                                                               │
│  Axis Bank                                                   │
│  ├─ API Type: SFTP File Transfer                            │
│  ├─ Auth: SFTP Credentials                                  │
│  ├─ Path: /transactions/axis/                               │
│  └─ Frequency: Daily/Hourly                                 │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 2. Data Adapter Layer

```
┌─────────────────────────────────────────────────────────────┐
│              BANK DATA ADAPTER (bank_adapter.py)             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ BankDataAdapter Class                               │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                                                       │   │
│  │ Methods:                                             │   │
│  │ • fetch_from_hdfc_api()                              │   │
│  │ • fetch_from_icici_api()                             │   │
│  │ • fetch_from_sbi_api()                               │   │
│  │ • fetch_from_razorpay()                              │   │
│  │ • fetch_from_sftp()                                  │   │
│  │ • send_to_kafka()                                    │   │
│  │ • standardize_*_transaction()                        │   │
│  │                                                       │   │
│  │ Features:                                            │   │
│  │ ✓ Error handling & retry logic                       │   │
│  │ ✓ Data transformation                                │   │
│  │ ✓ Kafka producer integration                         │   │
│  │ ✓ Logging & monitoring                               │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 3. Message Queue (Kafka)

```
┌─────────────────────────────────────────────────────────────┐
│                    KAFKA MESSAGE QUEUE                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Topics:                                                     │
│  ├─ hdfc_txns          (HDFC transactions)                   │
│  ├─ icici_txns         (ICICI transactions)                  │
│  ├─ sbi_txns           (SBI transactions)                    │
│  ├─ razorpay_txns      (Razorpay transactions)               │
│  └─ axis_txns          (Axis transactions)                   │
│                                                               │
│  Features:                                                   │
│  ✓ Scalable message processing                              │
│  ✓ Fault tolerance                                          │
│  ✓ Real-time data streaming                                 │
│  ✓ Consumer group management                                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 4. Consumer & Processing

```
┌─────────────────────────────────────────────────────────────┐
│         BANK RECONCILIATION CONSUMER                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ BankReconciliationConsumer                          │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                                                       │   │
│  │ Process:                                             │   │
│  │ 1. Consume from Kafka topics                         │   │
│  │ 2. Validate transaction data                         │   │
│  │ 3. Save to database                                  │   │
│  │ 4. Add to reconciliation engine                      │   │
│  │ 5. Log events                                        │   │
│  │                                                       │   │
│  │ Features:                                            │   │
│  │ ✓ Multi-topic consumption                            │   │
│  │ ✓ Data validation                                    │   │
│  │ ✓ Error handling                                     │   │
│  │ ✓ Audit logging                                      │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 5. Reconciliation Engine

```
┌─────────────────────────────────────────────────────────────┐
│           RECONCILIATION ENGINE                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ReconciliationEngine                                │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                                                       │   │
│  │ Matching Logic:                                      │   │
│  │ • Match by transaction ID                            │   │
│  │ • Match by amount + timestamp                        │   │
│  │ • Match by account + amount                          │   │
│  │                                                       │   │
│  │ Mismatch Detection:                                  │   │
│  │ • Amount mismatch (6%)                               │   │
│  │ • Status mismatch (4%)                               │   │
│  │ • Time mismatch (2%)                                 │   │
│  │ • Currency mismatch (1%)                             │   │
│  │ • Missing fields (1%)                                │   │
│  │                                                       │   │
│  │ Output:                                              │   │
│  │ • Reconciliation status (MATCHED/MISMATCH)           │   │
│  │ • Mismatch details                                   │   │
│  │ • Success rate calculation                           │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 6. Data Storage

```
┌─────────────────────────────────────────────────────────────┐
│              POSTGRESQL DATABASE                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Tables:                                                     │
│  ├─ transactions                                             │
│  │  ├─ txn_id (PK)                                           │
│  │  ├─ amount                                                │
│  │  ├─ currency                                              │
│  │  ├─ status                                                │
│  │  ├─ source (bank)                                         │
│  │  ├─ timestamp                                             │
│  │  └─ ... (other fields)                                    │
│  │                                                            │
│  ├─ reconciliation_results                                   │
│  │  ├─ txn_id (FK)                                           │
│  │  ├─ status (MATCHED/MISMATCH)                             │
│  │  ├─ sources (array of banks)                              │
│  │  └─ timestamp                                             │
│  │                                                            │
│  ├─ mismatches                                               │
│  │  ├─ id (PK)                                               │
│  │  ├─ txn_id (FK)                                           │
│  │  ├─ type (mismatch type)                                  │
│  │  ├─ severity (HIGH/MEDIUM/LOW)                            │
│  │  └─ details                                               │
│  │                                                            │
│  └─ audit_logs                                               │
│     ├─ id (PK)                                               │
│     ├─ action                                                │
│     ├─ timestamp                                             │
│     └─ details                                               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 7. Frontend Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│            REACT FRONTEND DASHBOARD                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Pages:                                                      │
│  ├─ Overview Dashboard                                       │
│  │  ├─ KPI Cards (transactions, accuracy, etc.)              │
│  │  ├─ Real-time charts                                      │
│  │  └─ Recent transactions                                   │
│  │                                                            │
│  ├─ Transactions                                             │
│  │  ├─ Live transaction table                                │
│  │  ├─ Filter by bank/status                                 │
│  │  └─ Transaction details                                   │
│  │                                                            │
│  ├─ Mismatches                                               │
│  │  ├─ Mismatch list                                         │
│  │  ├─ Severity indicators                                   │
│  │  └─ Investigation tools                                   │
│  │                                                            │
│  ├─ Analytics                                                │
│  │  ├─ Bank-wise statistics                                  │
│  │  ├─ Reconciliation trends                                 │
│  │  └─ Performance metrics                                   │
│  │                                                            │
│  └─ System Health                                            │
│     ├─ Service status                                        │
│     ├─ Performance metrics                                   │
│     └─ Alerts                                                │
│                                                               │
│  Features:                                                   │
│  ✓ Professional UI (no emojis)                               │
│  ✓ Dark/Light theme toggle                                   │
│  ✓ Real-time updates                                         │
│  ✓ Responsive design                                         │
│  ✓ INR currency formatting                                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
Bank APIs
   │
   ├─→ HDFC API ──┐
   ├─→ ICICI API ─┤
   ├─→ SBI API ───┤
   ├─→ Razorpay ──┤
   └─→ Axis SFTP ─┤
                  │
                  ↓
          bank_adapter.py
          (Transform & Validate)
                  │
                  ├─→ Kafka: hdfc_txns
                  ├─→ Kafka: icici_txns
                  ├─→ Kafka: sbi_txns
                  ├─→ Kafka: razorpay_txns
                  └─→ Kafka: axis_txns
                          │
                          ↓
          bank_reconciliation_consumer
          (Consume & Process)
                          │
                          ├─→ PostgreSQL (Save)
                          └─→ Reconciliation Engine
                                  │
                                  ├─→ Match Transactions
                                  ├─→ Detect Mismatches
                                  ├─→ Calculate Accuracy
                                  └─→ Generate Reports
                                          │
                                          ├─→ PostgreSQL (Store Results)
                                          └─→ Frontend Dashboard
                                                  │
                                                  ├─→ Real-time Monitoring
                                                  ├─→ Analytics & Reports
                                                  └─→ Professional UI
```

---

## Deployment Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                      │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Docker Containers                                       │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │                                                           │ │
│  │ • kafka-kafka-1 (Kafka Broker)                           │ │
│  │ • kafka-zookeeper-1 (Zookeeper)                          │ │
│  │ • reconciliation_postgres (PostgreSQL)                   │ │
│  │ • backend-api (FastAPI Backend)                          │ │
│  │ • frontend (React Frontend)                              │ │
│  │ • bank-producer (Real Bank Producer)                     │ │
│  │ • bank-consumer (Bank Reconciliation Consumer)           │ │
│  │                                                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Monitoring & Logging                                    │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │                                                           │ │
│  │ • Application Logs (bank_producer.log)                   │ │
│  │ • Error Tracking                                         │ │
│  │ • Performance Metrics                                    │ │
│  │ • Alert System                                           │ │
│  │                                                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

```
Frontend:
├─ React 18
├─ Axios (HTTP Client)
├─ CSS (Professional Styling)
└─ Theme Toggle (Dark/Light)

Backend:
├─ FastAPI (Python)
├─ PostgreSQL (Database)
├─ SQLAlchemy (ORM)
└─ Pydantic (Data Validation)

Message Queue:
├─ Apache Kafka
├─ Zookeeper
└─ kafka-python (Client)

Data Processing:
├─ Python 3.9+
├─ Requests (HTTP)
├─ Paramiko (SFTP)
└─ Cryptography (Encryption)

Infrastructure:
├─ Docker
├─ Docker Compose
└─ Linux/Windows
```

---

## Scalability Considerations

### Horizontal Scaling
- Multiple Kafka brokers for high throughput
- Multiple consumer instances for parallel processing
- Load balancer for frontend/backend

### Vertical Scaling
- Increase database resources
- Increase Kafka broker memory
- Optimize reconciliation engine

### Performance Optimization
- Database indexing on frequently queried fields
- Kafka partition optimization
- Caching layer (Redis)
- Query optimization

---

**Last Updated**: December 27, 2025
**Version**: 1.0
