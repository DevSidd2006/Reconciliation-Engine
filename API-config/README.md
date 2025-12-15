
# Reconciliation Engine (FastAPI)

A FastAPI backend for real-time transaction reconciliation, mismatches tracking, stats reporting, authentication, and system monitoring.

## 🚀 Features
- **Authentication**: JWT-based login with role-based access control (Admin, Auditor, Analyst).
- **Transactions API**: List, filter by source, and view details.
- **Mismatches API**: Track reconciliation issues with filters (type, severity, date, source).
- **Stats Dashboard**: Real-time aggregation of transaction metrics and mismatch rates.
- **System Health**: Database connection status and service health checks.
- **Security**: Rate limiting, CORS, and password hashing.
- **Observability**: Request logging (file & console) and slow query detection.

## 📂 Project Structure
```
app/
├── main.py                  # App entry point, middleware, CORS
├── api/
│   ├── routes/
│   │   ├── auth.py          # Login & Token APIs
│   │   ├── transactions.py  # Transaction management
│   │   ├── mismatches.py    # Mismatch tracking
│   │   ├── stats.py         # Dashboard metrics
│   │   └── health.py        # Health check
│   └── deps.py              # Auth validators & dependencies
├── core/
│   ├── config.py            # Environment validation & settings
│   ├── database.py          # Async SQLAlchemy engine
│   ├── security.py          # JWT & Hash utilities
│   └── rate_limit.py        # Rate limiter instance
├── models/                  # Database Models (User, Transaction, Mismatch)
├── schemas/                 # Pydantic Schemas (Request/Response)
└── logs/                    # Runtime logs (api.log)
```

## 🛠️ Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root directory:
```ini
# Database (Auto-corrected to asyncpg if needed)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/reconciliation_db

# Security
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

## ▶️ Run the Server
Start the development server with hot-reload:
```bash
uvicorn app.main:app --reload
```
- **API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

## 🔑 Authentication
- **Login**: `POST /api/v1/auth/login`
  - Body: `username` (email), `password`
- **Roles**: `admin`, `auditor`, `analyst`
- **Protecting Routes**: Use `Depends(get_current_active_user)`

## 📊 APIs
| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/transactions` | List all transactions (paginated) |
| `GET /api/v1/transactions/mismatched` | List transactions with issues |
| `GET /api/v1/mismatches` | Filter issues by type, severity, failure |
| `GET /api/v1/stats/dashboard` | Real-time status & metrics |
| `GET /health` | System status |

## 🛡️ Security & Rate Limiting
- **GLobal Limit**: 100 requests/minute per IP.
- **Login Limit**: 20 requests/minute.
- **CORS**: Configurable via `.env`.
