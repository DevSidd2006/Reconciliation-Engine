from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.transactions_router import router as txn_router
from .routers.mismatches_router import router as mismatch_router
from .routers.dashboard_router_temp import router as dashboard_router
from .routers.auth_router_simple import router as auth_router
from .routers.analytics_router import router as analytics_router

app = FastAPI(
    title="Banking Reconciliation API",
    description="Enterprise-grade transaction reconciliation system with security",
    version="2.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server (default)
        "http://localhost:3001",  # React dev server (alternative port)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "https://localhost",      # HTTPS frontend
        "https://localhost:443"   # HTTPS frontend with port
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(txn_router, prefix="/transactions")
app.include_router(mismatch_router, prefix="/mismatches")
app.include_router(dashboard_router, prefix="/api", tags=["Dashboard"])