from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.transactions_router import router as txn_router
from app.routers.mismatches_router import router as mismatch_router
from app.utils.socket_manager import socket_manager
import socketio

app = FastAPI(title="Reconciliation Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO app
app.mount("/socket.io", socket_manager.app)

app.include_router(txn_router, prefix="/transactions", tags=["Transactions"])
app.include_router(mismatch_router, prefix="/mismatches", tags=["Mismatches"])

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "Reconciliation Engine API"}