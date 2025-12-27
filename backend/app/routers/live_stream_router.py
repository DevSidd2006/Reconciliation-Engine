"""
Live Stream Router for Banking-Grade Transaction Reconciliation Engine

This module provides real-time streaming endpoints:
- Live transaction feeds
- Stream statistics
- Performance metrics
- Stream control
"""

from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import logging
import random
from db.database import get_db
from models.transaction import Transaction
from models.mismatch import Mismatch
from utils.response import success, error
from security.rbac_manager import require_operator
from security.auth import get_current_user
from security import audit_logger

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory stream state
stream_state = {
    "is_active": True,
    "is_paused": False,
    "started_at": datetime.now(),
    "events_count": 0
}

@router.get("/statistics", dependencies=[Depends(require_operator)])
def get_stream_statistics(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time streaming statistics"""
    try:
        # Get recent transactions (last hour)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_txns = db.query(Transaction).filter(
            Transaction.timestamp >= one_hour_ago
        ).count()
        
        # Calculate events per minute
        events_per_minute = round(recent_txns / 60, 2) if recent_txns > 0 else 0
        
        # Get recent mismatches
        recent_mismatches = db.query(Mismatch).filter(
            Mismatch.detected_at >= one_hour_ago
        ).count()
        
        stats = {
            "status": "active" if stream_state["is_active"] else "inactive",
            "is_paused": stream_state["is_paused"],
            "uptime_seconds": int((datetime.now() - stream_state["started_at"]).total_seconds()),
            "events_per_minute": events_per_minute,
            "total_events_processed": stream_state["events_count"],
            "recent_mismatches": recent_mismatches,
            "queue_size": random.randint(10, 500),
            "avg_latency_ms": round(random.uniform(50, 200), 2),
            "throughput_txns_per_sec": round(random.uniform(100, 500), 2)
        }
        
        # Log access
        audit_logger.log_data_access(
            user_id=current_user["user_id"],
            username=current_user["username"],
            method=request.method,
            endpoint=request.url.path,
            resource="live_stream",
            action="read",
            ip_address=request.client.host,
            record_count=1
        )
        
        return success(data=stats)
    except Exception as e:
        logger.error(f"Failed to get stream statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=error("Failed to retrieve statistics", "STREAM_ERROR"))

@router.get("/recent-transactions", dependencies=[Depends(require_operator)])
def get_recent_transactions(
    request: Request,
    current_user: dict = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=500),
    source: Optional[str] = Query(None, description="Filter by source"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """Get recent live transactions with optional filtering"""
    try:
        query = db.query(Transaction).order_by(Transaction.timestamp.desc())
        
        # Apply filters
        if source:
            query = query.filter(Transaction.source == source)
        if status:
            query = query.filter(Transaction.status == status)
        
        transactions = query.limit(limit).all()
        
        # Log access
        audit_logger.log_data_access(
            user_id=current_user["user_id"],
            username=current_user["username"],
            method=request.method,
            endpoint=request.url.path,
            resource="live_stream",
            action="read",
            ip_address=request.client.host,
            record_count=len(transactions),
            filters={"source": source, "status": status, "limit": limit}
        )
        
        return success(data=transactions)
    except Exception as e:
        logger.error(f"Failed to get recent transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=error("Failed to retrieve transactions", "STREAM_ERROR"))

@router.get("/recent-mismatches", dependencies=[Depends(require_operator)])
def get_recent_mismatches(
    request: Request,
    current_user: dict = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=500),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    db: Session = Depends(get_db)
):
    """Get recent live mismatch alerts"""
    try:
        query = db.query(Mismatch).order_by(Mismatch.detected_at.desc())
        
        if severity:
            # Map severity string to numeric range
            severity_map = {"low": 0.3, "medium": 0.6, "high": 0.8}
            min_severity = severity_map.get(severity.lower(), 0)
            query = query.filter(Mismatch.severity >= min_severity)
        
        mismatches = query.limit(limit).all()
        
        # Log access
        audit_logger.log_data_access(
            user_id=current_user["user_id"],
            username=current_user["username"],
            method=request.method,
            endpoint=request.url.path,
            resource="live_stream",
            action="read",
            ip_address=request.client.host,
            record_count=len(mismatches),
            filters={"severity": severity, "limit": limit}
        )
        
        return success(data=mismatches)
    except Exception as e:
        logger.error(f"Failed to get recent mismatches: {str(e)}")
        raise HTTPException(status_code=500, detail=error("Failed to retrieve mismatches", "STREAM_ERROR"))

@router.post("/start", dependencies=[Depends(require_operator)])
def start_stream(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Start the live transaction stream"""
    try:
        stream_state["is_active"] = True
        stream_state["is_paused"] = False
        stream_state["started_at"] = datetime.now()
        
        # Log action
        audit_logger.log_security_incident(
            incident_type="stream_action",
            description="Live stream started",
            ip_address=request.client.host,
            severity="low",
            details={
                "user_id": current_user["user_id"],
                "username": current_user["username"],
                "action": "start_stream"
            }
        )
        
        return success(data={"message": "Stream started successfully", "status": "active"})
    except Exception as e:
        logger.error(f"Failed to start stream: {str(e)}")
        raise HTTPException(status_code=500, detail=error("Failed to start stream", "STREAM_ERROR"))

@router.post("/pause", dependencies=[Depends(require_operator)])
def pause_stream(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Pause the live transaction stream"""
    try:
        stream_state["is_paused"] = True
        
        # Log action
        audit_logger.log_security_incident(
            incident_type="stream_action",
            description="Live stream paused",
            ip_address=request.client.host,
            severity="low",
            details={
                "user_id": current_user["user_id"],
                "username": current_user["username"],
                "action": "pause_stream"
            }
        )
        
        return success(data={"message": "Stream paused successfully", "status": "paused"})
    except Exception as e:
        logger.error(f"Failed to pause stream: {str(e)}")
        raise HTTPException(status_code=500, detail=error("Failed to pause stream", "STREAM_ERROR"))

@router.post("/resume", dependencies=[Depends(require_operator)])
def resume_stream(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Resume the paused live transaction stream"""
    try:
        stream_state["is_paused"] = False
        
        # Log action
        audit_logger.log_security_incident(
            incident_type="stream_action",
            description="Live stream resumed",
            ip_address=request.client.host,
            severity="low",
            details={
                "user_id": current_user["user_id"],
                "username": current_user["username"],
                "action": "resume_stream"
            }
        )
        
        return success(data={"message": "Stream resumed successfully", "status": "active"})
    except Exception as e:
        logger.error(f"Failed to resume stream: {str(e)}")
        raise HTTPException(status_code=500, detail=error("Failed to resume stream", "STREAM_ERROR"))

@router.post("/stop", dependencies=[Depends(require_operator)])
def stop_stream(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Stop the live transaction stream"""
    try:
        stream_state["is_active"] = False
        stream_state["is_paused"] = False
        
        # Log action
        audit_logger.log_security_incident(
            incident_type="stream_action",
            description="Live stream stopped",
            ip_address=request.client.host,
            severity="low",
            details={
                "user_id": current_user["user_id"],
                "username": current_user["username"],
                "action": "stop_stream"
            }
        )
        
        return success(data={"message": "Stream stopped successfully", "status": "inactive"})
    except Exception as e:
        logger.error(f"Failed to stop stream: {str(e)}")
        raise HTTPException(status_code=500, detail=error("Failed to stop stream", "STREAM_ERROR"))

@router.get("/performance", dependencies=[Depends(require_operator)])
def get_stream_performance(
    request: Request,
    current_user: dict = Depends(get_current_user),
    hours: int = Query(24, description="Hours to analyze performance")
):
    """Get streaming performance metrics"""
    try:
        start_time = datetime.now() - timedelta(hours=hours)
        
        # Mock performance data
        performance = {
            "period_hours": hours,
            "total_events": random.randint(10000, 100000),
            "total_mismatches_detected": random.randint(100, 1000),
            "avg_latency_ms": round(random.uniform(50, 200), 2),
            "p95_latency_ms": round(random.uniform(150, 400), 2),
            "p99_latency_ms": round(random.uniform(200, 500), 2),
            "throughput_peak_txns_per_sec": round(random.uniform(500, 2000), 2),
            "system_uptime_percent": round(random.uniform(99, 99.99), 2)
        }
        
        # Log access
        audit_logger.log_data_access(
            user_id=current_user["user_id"],
            username=current_user["username"],
            method=request.method,
            endpoint=request.url.path,
            resource="live_stream",
            action="read",
            ip_address=request.client.host,
            record_count=1
        )
        
        return success(data=performance)
    except Exception as e:
        logger.error(f"Failed to get stream performance: {str(e)}")
        raise HTTPException(status_code=500, detail=error("Failed to retrieve performance data", "STREAM_ERROR"))
