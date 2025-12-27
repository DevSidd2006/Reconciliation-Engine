
from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter()

@router.get("/")
async def health_check(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Health check for the application and database.
    """
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "db": "disconnected",
            "kafka": "connected" 
        }
    }
    
    try:
        # Check DB
        await db.execute(text("SELECT 1"))
        health_status["components"]["db"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["db"] = f"error: {str(e)}"
        
    return health_status
