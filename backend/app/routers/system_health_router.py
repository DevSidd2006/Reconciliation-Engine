"""
System Health API Router
Provides endpoints for real-time system monitoring
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
import logging
from ..services.system_health_service import system_health_service
from ..services.auth_service import get_current_user, require_admin, require_auditor

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health/overview")
async def get_system_health_overview():
    """
    Get complete system health overview
    Public endpoint for basic health check
    """
    try:
        return system_health_service.get_system_overview()
    except Exception as e:
        logger.error(f"Error getting system health overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system health data")

@router.get("/health/services")
async def get_service_status():
    """
    Get status of all services
    Public endpoint for service monitoring
    """
    try:
        return {
            "services": system_health_service.get_service_status(),
            "timestamp": system_health_service.get_system_overview()["timestamp"]
        }
    except Exception as e:
        logger.error(f"Error getting service status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service status")

@router.get("/health/metrics/kafka")
async def get_kafka_metrics():
    """
    Get Kafka cluster metrics
    """
    try:
        return system_health_service.get_kafka_metrics()
    except Exception as e:
        logger.error(f"Error getting Kafka metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Kafka metrics")

@router.get("/health/metrics/backend")
async def get_backend_metrics():
    """
    Get backend API metrics
    """
    try:
        return system_health_service.get_backend_metrics()
    except Exception as e:
        logger.error(f"Error getting backend metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get backend metrics")

@router.get("/health/metrics/redis")
async def get_redis_metrics():
    """
    Get Redis cache metrics
    """
    try:
        return system_health_service.get_redis_metrics()
    except Exception as e:
        logger.error(f"Error getting Redis metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Redis metrics")

@router.get("/health/metrics/database")
async def get_database_metrics():
    """
    Get PostgreSQL database metrics
    """
    try:
        return system_health_service.get_database_metrics()
    except Exception as e:
        logger.error(f"Error getting database metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get database metrics")

@router.get("/health/alerts")
async def get_system_alerts():
    """
    Get current system alerts
    """
    try:
        return {
            "alerts": system_health_service.get_system_alerts(),
            "timestamp": system_health_service.get_system_overview()["timestamp"]
        }
    except Exception as e:
        logger.error(f"Error getting system alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system alerts")

@router.get("/health/detailed")
async def get_detailed_health_metrics():
    """
    Get detailed health metrics for admin users
    Requires authentication
    """
    try:
        overview = system_health_service.get_system_overview()
        
        # Add additional detailed metrics for authenticated users
        overview["detailed"] = {
            "system_info": {
                "cpu_count": __import__('psutil').cpu_count(),
                "memory_total": f"{__import__('psutil').virtual_memory().total / 1024 / 1024 / 1024:.1f}GB",
                "disk_total": f"{__import__('psutil').disk_usage('/').total / 1024 / 1024 / 1024:.1f}GB",
                "boot_time": __import__('datetime').datetime.fromtimestamp(__import__('psutil').boot_time()).isoformat()
            },
            "network_connections": len(__import__('psutil').net_connections()),
            "process_count": len(__import__('psutil').pids())
        }
        
        return overview
    except Exception as e:
        logger.error(f"Error getting detailed health metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get detailed health metrics")