from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routers.transactions_router import router as txn_router
from routers.mismatches_router import router as mismatch_router
from routers.admin_router import router as admin_router
from utils.redis import banking_rate_limit_middleware
from security import (
    SecurityHeadersMiddleware, RequestValidationMiddleware, 
    SecurityMonitoringMiddleware, get_cors_config, audit_logger
)
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/banking_api.log') if os.path.exists('logs') else logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize FastAPI with banking-grade security
app = FastAPI(
    title="Banking-Grade Transaction Reconciliation API",
    description="Secure, compliant transaction reconciliation system with comprehensive audit logging",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENABLE_DOCS", "false").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("ENABLE_DOCS", "false").lower() == "true" else None,
    openapi_url="/openapi.json" if os.getenv("ENABLE_DOCS", "false").lower() == "true" else None
)

# Security Middleware Stack (order matters!)
# 1. Security monitoring (outermost)
app.add_middleware(SecurityMonitoringMiddleware)

# 2. Request validation
app.add_middleware(RequestValidationMiddleware)

# 3. Security headers
app.add_middleware(SecurityHeadersMiddleware)

# 4. Rate limiting
app.middleware("http")(banking_rate_limit_middleware)

# 5. CORS (innermost, closest to application)
cors_config = get_cors_config()
app.add_middleware(CORSMiddleware, **cors_config)

# Global exception handler for security
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with security logging"""
    logger.error(f"Unhandled exception: {str(exc)} for {request.method} {request.url.path}")
    
    # Log security incident for unexpected errors
    audit_logger.log_security_incident(
        incident_type="unhandled_exception",
        description=f"Unhandled exception: {str(exc)}",
        ip_address=request.client.host,
        severity="medium",
        details={
            "method": request.method,
            "path": request.url.path,
            "exception_type": type(exc).__name__
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "code": "INTERNAL_ERROR"
        }
    )

# Include routers with security
app.include_router(txn_router, prefix="/transactions", tags=["Transactions"])
app.include_router(mismatch_router, prefix="/mismatches", tags=["Mismatches"])
app.include_router(admin_router, prefix="/admin", tags=["Administration"])

@app.get("/", tags=["Health"])
async def root(request: Request):
    """Root endpoint with basic API info"""
    return {
        "service": "Banking-Grade Transaction Reconciliation API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs" if os.getenv("ENABLE_DOCS", "false").lower() == "true" else "disabled"
    }

@app.get("/health", tags=["Health"])
async def health_check(request: Request):
    """Detailed health check endpoint with system status"""
    from datetime import datetime
    
    # Basic health status
    health_status = {
        "status": "healthy",
        "service": "Banking-Grade Transaction Reconciliation API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "security": {
            "authentication": "enabled",
            "authorization": "enabled",
            "audit_logging": "enabled",
            "rate_limiting": "enabled"
        }
    }
    
    # Check database connectivity
    try:
        from db.database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = "disconnected"
        health_status["status"] = "degraded"
        logger.warning(f"Database health check failed: {e}")
    
    # Check Redis connectivity
    try:
        from utils.redis import redis_client
        redis_client.ping()
        health_status["cache"] = "connected"
    except Exception as e:
        health_status["cache"] = "disconnected"
        health_status["status"] = "degraded"
        logger.warning(f"Redis health check failed: {e}")
    
    return health_status

@app.get("/security/status", tags=["Security"])
async def security_status():
    """Security configuration status endpoint"""
    return {
        "authentication": "Keycloak OAuth2/OIDC",
        "authorization": "Role-Based Access Control (RBAC)",
        "audit_logging": "enabled",
        "rate_limiting": "enabled",
        "security_headers": "enabled",
        "cors": "hardened",
        "https": os.getenv("ENABLE_HTTPS", "false").lower() == "true"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup with security initialization"""
    logger.info("Starting Banking-Grade Transaction Reconciliation API")
    logger.info("Security features: Authentication, Authorization, Audit Logging, Rate Limiting")
    
    # Log application startup
    audit_logger.log_admin_action(
        user_id="system",
        username="system",
        action="application_startup",
        resource="api_server",
        ip_address="127.0.0.1",
        details={"version": "1.0.0", "security_enabled": True}
    )

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown with security logging"""
    logger.info("Shutting down Banking-Grade Transaction Reconciliation API")
    
    # Log application shutdown
    audit_logger.log_admin_action(
        user_id="system",
        username="system",
        action="application_shutdown",
        resource="api_server",
        ip_address="127.0.0.1",
        details={"graceful_shutdown": True}
    )