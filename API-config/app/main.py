
import time
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.rate_limit import limiter
from app.api.routes import auth, transactions, mismatches, stats, health

# Setup Logging
log_dir = Path("app/logs")
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=log_dir / "api.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("api")


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Rate Limit State
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Middleware
    @application.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        formatted_process_time = "{0:.2f}".format(process_time)
        logger.info(f"path={request.url.path} method={request.method} status={response.status_code} duration={formatted_process_time}ms")
        return response

    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    application.add_middleware(SlowAPIMiddleware)

    # Routes
    application.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
    application.include_router(transactions.router, prefix=f"{settings.API_V1_STR}/transactions", tags=["transactions"])
    application.include_router(mismatches.router, prefix=f"{settings.API_V1_STR}/mismatches", tags=["mismatches"])
    application.include_router(stats.router, prefix=f"{settings.API_V1_STR}/stats", tags=["stats"])
    application.include_router(health.router, prefix="/health", tags=["health"])
    
    # Root redirect or message
    @application.get("/")
    async def root():
        return {"message": "Welcome to Reconciliation Engine API", "docs": "/docs"}

    return application

app = create_application()
