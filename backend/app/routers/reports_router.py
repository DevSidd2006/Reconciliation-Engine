"""
Reports Router for Banking-Grade Transaction Reconciliation Engine

This module provides reporting endpoints:
- Daily reconciliation summaries
- Mismatch analysis reports
- Failure pattern detection
- Performance metrics reports
"""

from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import logging
from db.database import get_db
from models.transaction import Transaction
from models.mismatch import Mismatch
from utils.response import success, error
from security.rbac_manager import require_auditor
from security.auth import get_current_user
from security import audit_logger
from sqlalchemy import func

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/daily-summary", dependencies=[Depends(require_auditor)])
def get_daily_summary(
    request: Request,
    current_user: dict = Depends(get_current_user),
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """Get daily reconciliation summary report"""
    try:
        # Parse date or use today
        if date:
            report_date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            report_date = datetime.now().date()
        
        # Get transaction counts for the day
        start_of_day = datetime.combine(report_date, datetime.min.time())
        end_of_day = datetime.combine(report_date, datetime.max.time())
        
        total_txns = db.query(Transaction).filter(
            Transaction.timestamp >= start_of_day,
            Transaction.timestamp <= end_of_day
        ).count()
        
        successful_txns = db.query(Transaction).filter(
            Transaction.timestamp >= start_of_day,
            Transaction.timestamp <= end_of_day,
            Transaction.status == "SUCCESS"
        ).count()
        
        failed_txns = db.query(Transaction).filter(
            Transaction.timestamp >= start_of_day,
            Transaction.timestamp <= end_of_day,
            Transaction.status == "FAILED"
        ).count()
        
        pending_txns = db.query(Transaction).filter(
            Transaction.timestamp >= start_of_day,
            Transaction.timestamp <= end_of_day,
            Transaction.status == "PENDING"
        ).count()
        
        # Get mismatch counts
        total_mismatches = db.query(Mismatch).filter(
            Mismatch.detected_at >= start_of_day,
            Mismatch.detected_at <= end_of_day
        ).count()
        
        success_rate = (successful_txns / total_txns * 100) if total_txns > 0 else 0
        
        report_data = {
            "report_date": report_date.isoformat(),
            "total_transactions": total_txns,
            "successful": successful_txns,
            "failed": failed_txns,
            "pending": pending_txns,
            "success_rate": round(success_rate, 2),
            "total_mismatches": total_mismatches,
            "mismatch_rate": round((total_mismatches / total_txns * 100) if total_txns > 0 else 0, 2)
        }
        
        # Log report access
        audit_logger.log_data_access(
            user_id=current_user["user_id"],
            username=current_user["username"],
            method=request.method,
            endpoint=request.url.path,
            resource="reports",
            action="read",
            ip_address=request.client.host,
            record_count=1
        )
        
        return success(data=report_data)
    except Exception as e:
        logger.error(f"Failed to generate daily summary: {str(e)}")
        raise HTTPException(status_code=500, detail=error("Failed to generate report", "REPORT_ERROR"))

@router.get("/failure-patterns", dependencies=[Depends(require_auditor)])
def get_failure_patterns(
    request: Request,
    current_user: dict = Depends(get_current_user),
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get recurring failure pattern analysis"""
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        # Get mismatch patterns
        patterns = db.query(
            Mismatch.mismatch_type,
            func.count(Mismatch.id).label('count'),
            func.avg(Mismatch.severity).label('avg_severity')
        ).filter(
            Mismatch.detected_at >= start_date
        ).group_by(Mismatch.mismatch_type).all()
        
        pattern_data = [
            {
                "type": pattern[0],
                "occurrences": pattern[1],
                "avg_severity": round(float(pattern[2]) if pattern[2] else 0, 2),
                "frequency": round((pattern[1] / max(1, sum([p[1] for p in patterns])) * 100), 2)
            }
            for pattern in patterns
        ]
        
        # Sort by occurrences
        pattern_data.sort(key=lambda x: x['occurrences'], reverse=True)
        
        # Log report access
        audit_logger.log_data_access(
            user_id=current_user["user_id"],
            username=current_user["username"],
            method=request.method,
            endpoint=request.url.path,
            resource="reports",
            action="read",
            ip_address=request.client.host,
            record_count=len(pattern_data)
        )
        
        return success(data={
            "analysis_period_days": days,
            "patterns": pattern_data,
            "total_issues": sum([p['occurrences'] for p in pattern_data])
        })
    except Exception as e:
        logger.error(f"Failed to get failure patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=error("Failed to generate report", "REPORT_ERROR"))

@router.get("/amount-mismatches", dependencies=[Depends(require_auditor)])
def get_amount_mismatches_report(
    request: Request,
    current_user: dict = Depends(get_current_user),
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get amount mismatch analysis report"""
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        mismatches = db.query(Mismatch).filter(
            Mismatch.mismatch_type == "amount",
            Mismatch.detected_at >= start_date
        ).all()
        
        total_amount_variance = sum([m.description for m in mismatches if m.description])
        
        report_data = {
            "analysis_period_days": days,
            "total_amount_mismatches": len(mismatches),
            "avg_variance": round(total_amount_variance / len(mismatches), 2) if mismatches else 0,
            "high_severity_count": sum([1 for m in mismatches if m.severity >= 0.7]),
            "sources_affected": list(set([m.source1 for m in mismatches]))
        }
        
        # Log report access
        audit_logger.log_data_access(
            user_id=current_user["user_id"],
            username=current_user["username"],
            method=request.method,
            endpoint=request.url.path,
            resource="reports",
            action="read",
            ip_address=request.client.host,
            record_count=len(mismatches)
        )
        
        return success(data=report_data)
    except Exception as e:
        logger.error(f"Failed to get amount mismatches report: {str(e)}")
        raise HTTPException(status_code=500, detail=error("Failed to generate report", "REPORT_ERROR"))

@router.get("/missing-transactions", dependencies=[Depends(require_auditor)])
def get_missing_transactions_report(
    request: Request,
    current_user: dict = Depends(get_current_user),
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get missing transactions analysis report"""
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        mismatches = db.query(Mismatch).filter(
            Mismatch.mismatch_type == "missing",
            Mismatch.detected_at >= start_date
        ).all()
        
        sources = {}
        for mismatch in mismatches:
            source = mismatch.source1 or "unknown"
            sources[source] = sources.get(source, 0) + 1
        
        report_data = {
            "analysis_period_days": days,
            "total_missing_transactions": len(mismatches),
            "by_source": sources,
            "most_affected_source": max(sources, key=sources.get) if sources else None
        }
        
        # Log report access
        audit_logger.log_data_access(
            user_id=current_user["user_id"],
            username=current_user["username"],
            method=request.method,
            endpoint=request.url.path,
            resource="reports",
            action="read",
            ip_address=request.client.host,
            record_count=len(mismatches)
        )
        
        return success(data=report_data)
    except Exception as e:
        logger.error(f"Failed to get missing transactions report: {str(e)}")
        raise HTTPException(status_code=500, detail=error("Failed to generate report", "REPORT_ERROR"))

@router.get("/processing-delay", dependencies=[Depends(require_auditor)])
def get_processing_delay_report(
    request: Request,
    current_user: dict = Depends(get_current_user),
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get processing delay analysis report"""
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        mismatches = db.query(Mismatch).filter(
            Mismatch.mismatch_type == "delay",
            Mismatch.detected_at >= start_date
        ).all()
        
        report_data = {
            "analysis_period_days": days,
            "total_delayed_transactions": len(mismatches),
            "avg_delay_severity": round(sum([m.severity for m in mismatches]) / len(mismatches), 2) if mismatches else 0,
            "critical_delays": sum([1 for m in mismatches if m.severity >= 0.8])
        }
        
        # Log report access
        audit_logger.log_data_access(
            user_id=current_user["user_id"],
            username=current_user["username"],
            method=request.method,
            endpoint=request.url.path,
            resource="reports",
            action="read",
            ip_address=request.client.host,
            record_count=len(mismatches)
        )
        
        return success(data=report_data)
    except Exception as e:
        logger.error(f"Failed to get processing delay report: {str(e)}")
        raise HTTPException(status_code=500, detail=error("Failed to generate report", "REPORT_ERROR"))

@router.get("/recent-reports", dependencies=[Depends(require_auditor)])
def get_recent_reports(
    request: Request,
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100)
):
    """Get list of recently generated reports"""
    try:
        # Mock recent reports data
        recent_reports = [
            {
                "id": "rpt_001",
                "name": "Daily Summary - 2025-12-17",
                "type": "daily_summary",
                "generated_at": datetime.now().isoformat(),
                "generated_by": current_user["username"],
                "status": "completed"
            },
            {
                "id": "rpt_002",
                "name": "Failure Patterns - Last 7 Days",
                "type": "failure_patterns",
                "generated_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "generated_by": current_user["username"],
                "status": "completed"
            }
        ]
        
        # Log report access
        audit_logger.log_data_access(
            user_id=current_user["user_id"],
            username=current_user["username"],
            method=request.method,
            endpoint=request.url.path,
            resource="reports",
            action="read",
            ip_address=request.client.host,
            record_count=len(recent_reports)
        )
        
        return success(data=recent_reports[:limit])
    except Exception as e:
        logger.error(f"Failed to get recent reports: {str(e)}")
        raise HTTPException(status_code=500, detail=error("Failed to retrieve reports", "REPORT_ERROR"))
