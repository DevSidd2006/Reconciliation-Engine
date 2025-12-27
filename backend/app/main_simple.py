from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from .routers.auth_router_simple import router as auth_router
from .routers.analytics_router_simple import router as analytics_router
from .routers.dashboard_router_simple import router as dashboard_router
from .routers.system_health_router import router as system_health_router

app = FastAPI(
    title="Banking Reconciliation API - Working",
    description="Working version with all endpoints",
    version="2.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add middleware to disable caching
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(dashboard_router, prefix="/api", tags=["Dashboard"])
app.include_router(system_health_router, prefix="/api", tags=["System Health"])

# Add Redis stats endpoint to prevent 404 errors
@app.get("/api/redis/stats")
async def get_redis_stats():
    """Redis statistics endpoint"""
    try:
        from .services.redis_service import redis_service
        if redis_service.is_connected():
            return {
                "connected": True,
                "status": "HEALTHY",
                "cache_hits": "N/A",
                "cache_misses": "N/A",
                "memory_usage": "N/A"
            }
        else:
            return {
                "connected": False,
                "status": "DISCONNECTED",
                "error": "Redis not available"
            }
    except Exception as e:
        return {
            "connected": False,
            "status": "ERROR",
            "error": str(e)
        }

@app.get("/")
def root():
    return {"message": "Banking Reconciliation API - Working Mode", "status": "healthy"}