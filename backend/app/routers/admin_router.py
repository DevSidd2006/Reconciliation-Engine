"""
Admin Router for Banking-Grade Transaction Reconciliation Engine

This module provides administrative endpoints with strict access control:
- System configuration management
- User management operations
- Audit log access
- System health monitoring
"""

from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging
from db.database import get_db
from utils.response import success, error
from security.rbac_manager import require_admin
from security.auth import get_current_user
from security import audit_logger

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", dependencies=[Depends(require_admin)])
def admin_dashboard(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Admin dashboard with system overview (admin access required)"""
    try:
        # Log admin access
        audit_logger.log_admin_action(
            user_id=current_user["user_id"],
            username=current_user["username"],
            action="dashboard_access",
            resource="admin_dashboard",
            ip_address=request.client.host
        )
        
        return success(data={
            "message": "Admin dashboard access granted",
            "user": current_user["username"],
            "role": "admin",
            "features": [
                "System Configuration",
                "User Management", 
                "Audit Logs",
                "System Health",
                "Security Settings"
            ]
        })
    except Exception as e:
        logger.error(f"Failed to access admin dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail=error("Failed to access admin dashboard", "ADMIN_DASHBOARD_ERROR")
        )

@router.get("/audit-logs", dependencies=[Depends(require_admin)])
def get_audit_logs(
    request: Request,
    current_user: dict = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=1000, description="Number of audit logs to return"),
    offset: int = Query(0, ge=0, description="Number of audit logs to skip"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db)
):
    """Get audit logs (admin access required)"""
    try:
        from security.audit_logger import AuditLog
        
        query = db.query(AuditLog)
        
        # Apply filters
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        audit_logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
        
        # Log admin access to audit logs
        audit_logger.log_admin_action(
            user_id=current_user["user_id"],
            username=current_user["username"],
            action="audit_logs_access",
            resource="audit_logs",
            ip_address=request.client.host,
            details={
                "filters": {"event_type": event_type, "user_id": user_id},
                "records_accessed": len(audit_logs)
            }
        )
        
        return success(
            data=audit_logs,
            meta={
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        )
    except Exception as e:
        logger.error(f"Failed to retrieve audit logs: {e}")
        raise HTTPException(
            status_code=500,
            detail=error("Failed to retrieve audit logs", "AUDIT_LOGS_ERROR")
        )

@router.get("/system-health", dependencies=[Depends(require_admin)])
def get_system_health(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get system health status (admin access required)"""
    try:
        from utils.redis import redis_client, cache_manager
        
        # Check database connection
        db_status = "healthy"
        try:
            db = next(get_db())
            db.execute("SELECT 1")
            db.close()
        except Exception:
            db_status = "unhealthy"
        
        # Check Redis connection
        redis_status = "healthy"
        try:
            redis_client.get_client().ping()
        except Exception:
            redis_status = "unhealthy"
        
        # Get cache info
        cache_info = cache_manager.get_cache_info()
        
        health_data = {
            "database": {"status": db_status},
            "redis": {"status": redis_status},
            "cache": cache_info,
            "security": {
                "authentication": "enabled",
                "authorization": "enabled", 
                "audit_logging": "enabled",
                "rate_limiting": "enabled"
            }
        }
        
        # Log admin access
        audit_logger.log_admin_action(
            user_id=current_user["user_id"],
            username=current_user["username"],
            action="system_health_check",
            resource="system_health",
            ip_address=request.client.host,
            details=health_data
        )
        
        return success(data=health_data)
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(
            status_code=500,
            detail=error("Failed to get system health", "SYSTEM_HEALTH_ERROR")
        )

@router.post("/security/reset-rate-limits", dependencies=[Depends(require_admin)])
def reset_rate_limits(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Reset all rate limits (admin access required)"""
    try:
        from utils.redis import redis_client
        
        # Get all rate limit keys
        rate_limit_keys = redis_client.get_client().keys("rate:*")
        
        # Delete all rate limit keys
        if rate_limit_keys:
            deleted_count = redis_client.get_client().delete(*rate_limit_keys)
        else:
            deleted_count = 0
        
        # Log admin action
        audit_logger.log_admin_action(
            user_id=current_user["user_id"],
            username=current_user["username"],
            action="reset_rate_limits",
            resource="rate_limits",
            ip_address=request.client.host,
            details={"keys_deleted": deleted_count}
        )
        
        return success(data={
            "message": "Rate limits reset successfully",
            "keys_deleted": deleted_count
        })
    except Exception as e:
        logger.error(f"Failed to reset rate limits: {e}")
        raise HTTPException(
            status_code=500,
            detail=error("Failed to reset rate limits", "RATE_LIMIT_RESET_ERROR")
        )