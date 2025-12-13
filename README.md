# 🚀 Real-Time Transaction Reconciliation Engine

![Status](https://img.shields.io/badge/Status-Prototype-blue)
![Python](https://img.shields.io/badge/Backend-FastAPI-green)
![React](https://img.shields.io/badge/Frontend-React-61DAFB)
![Kafka](https://img.shields.io/badge/Streaming-Kafka-black)
![License](https://img.shields.io/badge/License-MIT-yellow)

**A production-grade, bank-level mismatch detection system using Kafka, FastAPI, Redis, PostgreSQL, Keycloak & React.**

---

## 📌 Overview

Banks face reconciliation issues when transactions flowing through multiple systems (Core Banking, Payment Gateway, Mobile App) do not match due to delays, failures, or inconsistencies.

**This project simulates a real-time reconciliation system that:**
* **Ingests** live transaction events from three sources.
* **Detects mismatches** (amount, status, timestamp, missing entries).
* **Stores results** securely in a database.
* **Logs every action** for compliance.
* **Updates a dashboard** in real-time.

> **⚠️ Note:** Even though no real payments occur, the architecture is built exactly like a real bank system using modern enterprise-grade components.

---

## 🏗 System Architecture

The system uses an Event-Driven Architecture (EDA) to ingest and process transactions securely.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#fff', 'edgeLabelBackground':'#ffffff', 'tertiaryColor': '#f4f4f4'}}}%%
graph TD
    %% --- Define Subgraphs ---
    subgraph "Simulation Layer"
        style SIM_NOTE fill:#ffcccc,stroke:#ff0000,color:#000
        SIM_NOTE[/"⚠️ NOTE: EVENTS ARE SIMULATED.<br/>NO REAL USERS OR PAYMENTS."/]
        P_CORE["core_producer.py"]
        P_GW["gateway_producer.py"]
        P_MOB["mobile_producer.py"]
    end

    subgraph "Governance & Security"
        SR["Schema Registry<br/>(Avro)"]
        KC["Keycloak<br/>(OAuth2 / JWT / RBAC)"]
    end

    subgraph "Data Ingestion Bus"
        KAFKA["Apache Kafka<br/>(TLS Secured)"]
    end

    subgraph "Processing Layer"
        API["Reconciliation Engine<br/>FastAPI Backend"]
    end

    subgraph "Storage Layer"
        REDIS[("Redis<br/>Temporary In-flight State")]
        PG[("PostgreSQL<br/>Events, Results, audit_logs")]
    end

    subgraph "Frontend"
        DASH["React Dashboard<br/>(HTTPS)"]
    end

    %% --- Define Connections ---
    SIM_NOTE --- P_CORE & P_GW & P_MOB
    P_CORE -->|"core_txns (TLS)"| KAFKA
    P_GW -->|"gateway_txns (TLS)"| KAFKA
    P_MOB -->|"mobile_txns (TLS)"| KAFKA

    SR -.-|Enforces Strict Schema| KAFKA

    KAFKA -->|Consumer (TLS)| API
    API <-->|"Read/Write State"| REDIS
    API -->|"Store Final Results"| PG

    DASH -.->|"1. Login (Creds)"| KC
    KC -.->|"2. Returns JWT"| DASH
    DASH -->|"3. HTTPS API Call (+JWT)"| API
    API -.-|Validate JWT on every request| KC
    API -->|"4. Real-time Update (Socket.IO)"| DASH

    %% --- Apply Styling ---
    classDef py fill:#f9f2f4,stroke:#d15b93,stroke-width:2px;
    classDef kafka fill:#333,stroke:#000,stroke-width:2px,color:#fff;
    classDef gov fill:#fff3cd,stroke:#856404,stroke-width:2px,stroke-dasharray: 5 5;
    classDef api fill:#d1e7dd,stroke:#0f5132,stroke-width:2px;
    classDef db fill:#e2e3e5,stroke:#383d41,stroke-width:2px;
    classDef ui fill:#cff4fc,stroke:#055160,stroke-width:2px;

    class P_CORE,P_GW,P_MOB py;
    class KAFKA kafka;
    class SR,KC gov;
    class API api;
    class REDIS,PG db;
    class DASH ui;
