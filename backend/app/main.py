from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.transactions_router import router as txn_router
from routers.mismatches_router import router as mismatch_router
from utils.redis import banking_rate_limit_middleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="Reconciliation Backend - Banking Grade")

# Add banking-grade rate limiting middleware
app.middleware("http")(banking_rate_limit_middleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO will be added later

app.include_router(txn_router, prefix="/transactions", tags=["Transactions"])
app.include_router(mismatch_router, prefix="/mismatches", tags=["Mismatches"])

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "Reconciliation Engine API"}