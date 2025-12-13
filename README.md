🚀 Real-Time Transaction Reconciliation Engine
A production-grade, bank-level mismatch detection system using Kafka, FastAPI, Redis, PostgreSQL, Keycloak & React.

📌 Overview
Banks face reconciliation issues when transactions flowing through multiple systems
(Core Banking, Payment Gateway, Mobile App) do not match due to delays, failures, or inconsistencies.

This project simulates a real-time reconciliation system that:

Ingests live transaction events from three sources

Detects mismatches (amount, status, timestamp, missing entries)

Stores results securely in a database

Logs every action for compliance

Updates a dashboard in real-time

Uses modern enterprise-grade components (Kafka, Keycloak, TLS, Redis)

Even though no real payments occur, the architecture is built exactly like a real bank system.

🏛 System Architecture
                NO REAL USER MAKES A REAL PAYMENT
                     (Events are simulated)
                                │
                                ▼
─────────────────────────────────────────────────────────────
              PRODUCER SCRIPTS (SIMULATION)
─────────────────────────────────────────────────────────────
core_producer.py     → Kafka topic: core_txns
gateway_producer.py  → Kafka topic: gateway_txns
mobile_producer.py   → Kafka topic: mobile_txns
• Pretend to be real banking systems
• Create random transaction events
• Inject mismatches intentionally
                                │
                                ▼
─────────────────────────────────────────────────────────────
                 SCHEMA REGISTRY (Avro)
─────────────────────────────────────────────────────────────
• Enforces strict schema for all producers  
• Prevents malformed/corrupted data  
• Guarantees consistent transaction structure
                                │
                                ▼
─────────────────────────────────────────────────────────────
                     KAFKA (Message Bus)
─────────────────────────────────────────────────────────────
• Stores events from all 3 sources  
• Guarantees durability, ordering & no data loss  
• TLS secured communication (Producers ↔ Kafka ↔ Backend)
                                │
                                ▼
─────────────────────────────────────────────────────────────
         AUTHENTICATION + AUTHORIZATION (KEYCLOAK)
─────────────────────────────────────────────────────────────
• Provides OAuth2 + JWT  
• Provides login UI for Dashboard  
• Implements RBAC (admin, viewer roles)  
• Protects backend API endpoints  
• Backend verifies JWT on every request
                                │
                                ▼
─────────────────────────────────────────────────────────────
     RECONCILIATION ENGINE (FastAPI Backend)
─────────────────────────────────────────────────────────────
1. Kafka Consumer reads events (TLS secure)  
2. Keycloak auth validates JWT  
3. Optional schema validation  
4. Temporary event state stored in Redis  
5. When ≥2 sources → perform reconciliation  
   - amount mismatch  
   - status mismatch  
   - timestamp mismatch  
   - missing event from core/gateway/mobile  
6. Store results in PostgreSQL  
7. Create audit log entry  
8. Emit real-time update to dashboard via Socket.IO  
                                │
                                ▼
─────────────────────────────────────────────────────────────
     DATABASES (PostgreSQL + Redis)
─────────────────────────────────────────────────────────────
PostgreSQL (Encrypted at-rest optional)
• raw_events table  
• reconciliation_results table  
• audit_logs table (who accessed what & when)

Redis  
• Temporary in-flight event storage
                                │
                                ▼
─────────────────────────────────────────────────────────────
                     REACT DASHBOARD
─────────────────────────────────────────────────────────────
• User logs in via Keycloak login screen  
• Receives JWT token  
• Uses HTTPS (TLS) to call backend APIs  
• Listens to Socket.IO for real-time mismatches  
• Displays results, charts, summaries & audit logs
🧩 Tech Stack
🟪 Backend
FastAPI (high-performance Python API)

Kafka Consumer (real-time ingestion)

Redis (temporary event state)

PostgreSQL (permanent storage)

Keycloak (Auth + RBAC)

Socket.IO (real-time push updates)

🟩 Frontend
React.js

Keycloak JS Adapter (for login)

Socket.IO client

TLS-secure HTTPS calls

🟧 Data Streaming
Apache Kafka

Schema Registry (Avro)

TLS-secured producers & consumers

🔍 Core Features
✔ Real-time ingestion
Three producer scripts simulate live banking systems.

✔ Strict schema validation
Ensures every transaction follows identical structure.

✔ Enterprise-grade security
Keycloak (OAuth2 + JWT)

Role-based access

TLS encryption for all communication

✔ Real-time reconciliation
Detects mismatches instantly when ≥2 sources are available.

✔ Live dashboard
Socket.IO updates → no refresh needed.

✔ Full auditing
Logs who accessed what and when (bank requirement).

🧪 Mismatch Types Detected
Type	Description
Amount Mismatch	Core vs Gateway vs Mobile amount differs
Status Mismatch	SUCCESS vs FAILED differences
Timestamp Mismatch	Delay beyond threshold
Missing Event	One system didn’t report the transaction
🗄 Database Schema Summary
PostgreSQL Tables
raw_events → Each event from producer

reconciliation_results → Final status per transaction

audit_logs → Who accessed what, when

Redis
Temporary holding of events until reconciliation is possible

🚀 How the System Works (Simple Flow)
Producers send events → Kafka

Kafka stores securely → Backend reads

Backend validates → puts partial events into Redis

When enough events arrive:
→ compare
→ detect mismatch
→ save result
→ create audit log
→ push update to dashboard

React dashboard shows live output

🛡 Security Features
TLS enabled across all services

JWT validation on every request

Role-based access (admin/viewer)

Optional at-rest encryption for PostgreSQL

Schema-enforced producers

This makes the system bank-ready for production-scale reconciliation.

📊 Dashboard Capabilities
Live mismatch stream

Summary stats

Charts & visualizations

Search and filter transactions

Audit log viewer

Admin-only insights

🙌 Why This Project Stands Out in a Hackathon
Real-world banking problem

Enterprise-grade components

Fully secure system

Real-time pipeline

Modular & scalable

Professional architecture

Easy to extend into production
