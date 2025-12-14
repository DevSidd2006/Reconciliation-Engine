from fastapi import FastAPI
from routers.transactions_router import router as txn_router
from routers.mismatches_router import router as mismatch_router

app = FastAPI(title="Reconciliation Backend")

app.include_router(txn_router, prefix="/transactions")
app.include_router(mismatch_router, prefix="/mismatches")