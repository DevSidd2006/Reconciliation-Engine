# 🏦 Real-Time Transaction Reconciliation Engine

[![Node.js](https://img.shields.io/badge/Node.js-20+-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A production-ready banking reconciliation system that detects and highlights transaction mismatches across multiple data sources in real-time, with visual dashboards and automated alerting.

**#techfiesta** | Built for enterprise-grade financial operations

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Usage Examples](#-usage-examples)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

Banks and financial institutions face critical reconciliation challenges where transactions between systems (Core Banking, Payment Gateways, Mobile Apps) don't match due to failures, delays, or inconsistencies. This engine provides:

- **Real-time mismatch detection** across multiple transaction sources
- **Automated reconciliation** with intelligent matching algorithms
- **Visual dashboards** with heatmaps for pattern recognition
- **Instant alerts** for discrepancies requiring immediate attention
- **Comprehensive reporting** for audit and compliance

### Problem Statement

Traditional reconciliation processes are:
- ⏰ **Time-consuming**: Manual matching takes hours or days
- ❌ **Error-prone**: Human oversight misses critical discrepancies
- 📊 **Lack visibility**: No real-time insights into reconciliation status
- 🔍 **Reactive**: Issues discovered after they've caused problems

### Our Solution

This engine provides:
- ⚡ **Real-time processing**: Instant detection of mismatches
- 🤖 **Automated matching**: AI-powered transaction correlation
- 📈 **Live dashboards**: Visual heatmaps and trend analysis
- 🚨 **Proactive alerts**: Immediate notification of discrepancies

---

## ✨ Key Features

### Core Capabilities

#### 🔄 Multi-Source Reconciliation
- Ingest transactions from 3+ data sources simultaneously
- Support for Core Banking, Payment Gateway, and Mobile App systems
- Extensible architecture for additional sources

#### 🎯 Intelligent Mismatch Detection
- **Amount Discrepancies**: Detect differences in transaction amounts
- **Timestamp Delays**: Identify timing inconsistencies across systems
- **Missing Entries**: Flag transactions present in one source but absent in others
- **Duplicate Detection**: Identify duplicate transaction entries

#### 📊 Real-Time Streaming
- WebSocket-based live updates using Socket.io
- Sub-second latency for mismatch notifications
- Scalable pub/sub architecture with Redis
- Optional Kafka integration for high-volume scenarios

#### 📈 Visual Analytics Dashboard
- **Mismatch Heatmap**: Color-coded visualization of reconciliation status
- **Live Statistics**: Real-time metrics on reconciliation rates
- **Alert Feed**: Chronological stream of detected discrepancies
- **Detailed Tables**: Drill-down views with transaction details

#### 🚨 Automated Alerting
- Configurable alert thresholds
- Multi-channel notifications (WebSocket, Email, Slack)
- Priority-based alert routing
- Alert acknowledgment and resolution tracking

#### 📑 Comprehensive Reporting
- Exportable reconciliation reports (PDF, Excel, JSON)
- Historical trend analysis
- Audit trail for compliance
- Customizable report templates

---

## 🏗️ Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Data Sources"
        CBS[Core Banking System]
        PG[Payment Gateway]
        MA[Mobile App]
    end
    
    subgraph "Backend Services"
        API[Express REST API]
        WS[Socket.io WebSocket Server]
        RE[Reconciliation Engine]
        MDG[Mock Data Generator]
        SS[Streaming Service]
    end
    
    subgraph "Data Layer"
        PG_DB[(PostgreSQL)]
        REDIS[(Redis Cache)]
    end
    
    subgraph "Frontend"
        DASH[React Dashboard]
        CHART[Chart.js Visualizations]
        WS_CLIENT[Socket.io Client]
    end
    
    CBS --> MDG
    PG --> MDG
    MA --> MDG
    
    MDG --> RE
    RE --> API
    RE --> SS
    SS --> WS
    
    API --> PG_DB
    API --> REDIS
    WS --> REDIS
    
    DASH --> API
    DASH --> WS_CLIENT
    WS_CLIENT --> WS
    CHART --> DASH
    
    style RE fill:#ff6b6b
    style DASH fill:#4ecdc4
    style PG_DB fill:#95e1d3
    style REDIS fill:#f38181
```

### Data Flow

1. **Ingestion**: Mock data generators simulate transactions from multiple sources
2. **Processing**: Reconciliation engine matches and compares transactions
3. **Detection**: Mismatches identified based on configurable rules
4. **Storage**: Results stored in PostgreSQL, cached in Redis
5. **Streaming**: Real-time updates pushed via Socket.io
6. **Visualization**: React dashboard renders live data and alerts

---

## 🛠️ Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Node.js** | 20+ | Runtime environment |
| **TypeScript** | 5+ | Type-safe development |
| **Express.js** | 4.18+ | REST API framework |
| **Socket.io** | 4.6+ | Real-time WebSocket communication |
| **Prisma** | 5+ | ORM for database operations |
| **Bull** | 4+ | Job queue for background processing |
| **Jest** | 29+ | Testing framework |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18+ | UI framework |
| **TypeScript** | 5+ | Type-safe development |
| **Vite** | 5+ | Build tool and dev server |
| **TailwindCSS** | 3+ | Utility-first CSS framework |
| **Chart.js** | 4+ | Data visualization |
| **React Query** | 5+ | Server state management |
| **Socket.io Client** | 4.6+ | Real-time client |

### Database & Infrastructure

| Technology | Version | Purpose |
|------------|---------|---------|
| **PostgreSQL** | 15+ | Primary relational database |
| **Redis** | 7+ | Caching and pub/sub |
| **Docker** | 24+ | Containerization |
| **Docker Compose** | 2+ | Multi-container orchestration |

### Optional (Production Scale)

- **Apache Kafka**: High-volume message streaming
- **Kubernetes**: Container orchestration
- **Prometheus**: Metrics and monitoring
- **Grafana**: Metrics visualization

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:

- **Node.js** 20+ ([Download](https://nodejs.org/))
- **npm** or **yarn** or **pnpm**
- **PostgreSQL** 15+ ([Download](https://www.postgresql.org/download/))
- **Redis** 7+ ([Download](https://redis.io/download/))
- **Docker** (optional, for containerized setup)

### Quick Start (Development)

#### 1. Clone the Repository

```bash
git clone https://github.com/DevSidd2006/Reconciliation-Engine.git
cd Reconciliation-Engine
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Edit .env with your database credentials
# DATABASE_URL="postgresql://user:password@localhost:5432/reconciliation"
# REDIS_URL="redis://localhost:6379"

# Run database migrations
npx prisma migrate dev

# Seed database with initial data (optional)
npm run seed

# Start development server
npm run dev
```

Backend will run on `http://localhost:3000`

#### 3. Frontend Setup

```bash
# Open new terminal, navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Edit .env with backend URL
# VITE_API_URL=http://localhost:3000
# VITE_WS_URL=http://localhost:3000

# Start development server
npm run dev
```

Frontend will run on `http://localhost:5173`

#### 4. Access the Application

Open your browser and navigate to:
- **Dashboard**: http://localhost:5173
- **API Docs**: http://localhost:3000/api-docs

### Quick Start (Docker)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

Services will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

## 📁 Project Structure

```
Reconciliation-Engine/
├── backend/
│   ├── src/
│   │   ├── config/           # Configuration files
│   │   ├── controllers/      # Request handlers
│   │   ├── models/           # Data models (Prisma schema)
│   │   ├── services/         # Business logic
│   │   │   ├── reconciliationEngine.ts
│   │   │   ├── mockDataGenerator.ts
│   │   │   └── streamingService.ts
│   │   ├── routes/           # API routes
│   │   ├── middleware/       # Express middleware
│   │   ├── utils/            # Helper functions
│   │   └── server.ts         # Entry point
│   ├── prisma/
│   │   └── schema.prisma     # Database schema
│   ├── tests/                # Test files
│   ├── package.json
│   └── tsconfig.json
│
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── Dashboard/
│   │   │   ├── Heatmap/
│   │   │   ├── AlertFeed/
│   │   │   └── MismatchTable/
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API clients
│   │   ├── utils/            # Helper functions
│   │   ├── types/            # TypeScript types
│   │   ├── App.tsx           # Root component
│   │   └── main.tsx          # Entry point
│   ├── public/               # Static assets
│   ├── package.json
│   └── vite.config.ts
│
├── docker-compose.yml        # Docker orchestration
├── .gitignore
├── LICENSE
└── README.md
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:3000/api
```

### Authentication
Currently uses API key authentication. Include in headers:
```
X-API-Key: your-api-key-here
```

### Endpoints

#### 1. Get Reconciliation Report

```http
GET /api/reconciliation/report
```

**Response:**
```json
{
  "timestamp": "2025-12-11T18:30:00Z",
  "totalTransactions": 15000,
  "matchedTransactions": 14250,
  "mismatches": 750,
  "reconciliationRate": 95.0,
  "sources": ["core_banking", "payment_gateway", "mobile_app"],
  "mismatchBreakdown": {
    "amountDifference": 450,
    "timestampDelay": 200,
    "missingEntries": 100
  }
}
```

#### 2. Get All Mismatches

```http
GET /api/reconciliation/mismatches?page=1&limit=50&type=amount
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 50)
- `type` (optional): Filter by mismatch type (`amount`, `timestamp`, `missing`)

**Response:**
```json
{
  "data": [
    {
      "id": "mismatch-001",
      "transactionId": "TXN-12345",
      "type": "amount_difference",
      "severity": "high",
      "sources": {
        "core_banking": {
          "amount": 1000.00,
          "timestamp": "2025-12-11T10:30:00Z"
        },
        "payment_gateway": {
          "amount": 999.50,
          "timestamp": "2025-12-11T10:30:05Z"
        }
      },
      "difference": 0.50,
      "detectedAt": "2025-12-11T10:30:10Z",
      "status": "unresolved"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 750,
    "pages": 15
  }
}
```

#### 3. Get Statistics

```http
GET /api/reconciliation/stats
```

**Response:**
```json
{
  "current": {
    "reconciliationRate": 95.0,
    "totalMismatches": 750,
    "criticalAlerts": 12
  },
  "trends": {
    "last24Hours": {
      "reconciliationRate": 94.5,
      "change": "+0.5%"
    }
  }
}
```

#### 4. Trigger Manual Reconciliation

```http
POST /api/reconciliation/run
```

**Request Body:**
```json
{
  "sources": ["core_banking", "payment_gateway"],
  "dateRange": {
    "start": "2025-12-11T00:00:00Z",
    "end": "2025-12-11T23:59:59Z"
  }
}
```

#### 5. Get Transactions by Source

```http
GET /api/transactions/:source?page=1&limit=100
```

**Path Parameters:**
- `source`: Data source name (`core_banking`, `payment_gateway`, `mobile_app`)

### WebSocket Events

#### Connect to WebSocket

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:3000');
```

#### Subscribe to Events

```javascript
// New mismatch detected
socket.on('mismatch:detected', (data) => {
  console.log('New mismatch:', data);
});

// Statistics update
socket.on('stats:update', (stats) => {
  console.log('Updated stats:', stats);
});

// Reconciliation complete
socket.on('reconciliation:complete', (report) => {
  console.log('Reconciliation report:', report);
});
```

---

## 💡 Usage Examples

### Example 1: Monitor Real-Time Mismatches

```typescript
import { useEffect, useState } from 'react';
import io from 'socket.io-client';

function MismatchMonitor() {
  const [mismatches, setMismatches] = useState([]);

  useEffect(() => {
    const socket = io('http://localhost:3000');
    
    socket.on('mismatch:detected', (mismatch) => {
      setMismatches(prev => [mismatch, ...prev]);
    });

    return () => socket.disconnect();
  }, []);

  return (
    <div>
      {mismatches.map(m => (
        <Alert key={m.id} severity={m.severity}>
          {m.type}: ${m.difference}
        </Alert>
      ))}
    </div>
  );
}
```

### Example 2: Fetch Reconciliation Report

```typescript
async function getReconciliationReport() {
  const response = await fetch('http://localhost:3000/api/reconciliation/report', {
    headers: {
      'X-API-Key': 'your-api-key'
    }
  });
  
  const report = await response.json();
  console.log(`Reconciliation Rate: ${report.reconciliationRate}%`);
  console.log(`Total Mismatches: ${report.mismatches}`);
}
```

### Example 3: Trigger Manual Reconciliation

```typescript
async function runReconciliation() {
  const response = await fetch('http://localhost:3000/api/reconciliation/run', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your-api-key'
    },
    body: JSON.stringify({
      sources: ['core_banking', 'payment_gateway'],
      dateRange: {
        start: new Date().toISOString(),
        end: new Date().toISOString()
      }
    })
  });
  
  const result = await response.json();
  console.log('Reconciliation complete:', result);
}
```

---

## ⚙️ Configuration

### Environment Variables

#### Backend (.env)

```bash
# Server Configuration
NODE_ENV=development
PORT=3000
API_KEY=your-secret-api-key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/reconciliation

# Redis
REDIS_URL=redis://localhost:6379

# Reconciliation Settings
MISMATCH_THRESHOLD=0.01          # Amount difference threshold ($0.01)
TIMESTAMP_TOLERANCE=300          # Timestamp tolerance (5 minutes)
RECONCILIATION_INTERVAL=60000    # Auto-reconciliation interval (1 minute)

# Alert Settings
ENABLE_EMAIL_ALERTS=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Optional: Kafka
KAFKA_ENABLED=false
KAFKA_BROKERS=localhost:9092
```

#### Frontend (.env)

```bash
# API Configuration
VITE_API_URL=http://localhost:3000
VITE_WS_URL=http://localhost:3000

# Feature Flags
VITE_ENABLE_MOCK_DATA=true
VITE_ENABLE_REAL_TIME=true
```

---

## 🧪 Testing

### Run Backend Tests

```bash
cd backend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test suite
npm test -- reconciliationEngine.test.ts

# Run in watch mode
npm test -- --watch
```

### Run Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

### Test Coverage Goals

- Unit Tests: > 80%
- Integration Tests: > 70%
- E2E Tests: Critical user flows

---

## 🚢 Deployment

### Production Build

#### Backend

```bash
cd backend
npm run build
npm run start:prod
```

#### Frontend

```bash
cd frontend
npm run build
# Build output in dist/
```

### Docker Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Cloud Deployment Options

- **AWS**: ECS + RDS + ElastiCache
- **Google Cloud**: Cloud Run + Cloud SQL + Memorystore
- **Azure**: App Service + Azure Database + Redis Cache
- **Heroku**: Heroku Postgres + Heroku Redis