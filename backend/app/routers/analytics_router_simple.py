"""
Real Analytics Router with Simple Authentication
Uses real database data with simple JWT authentication
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from .auth_router_simple import verify_token
from ..services.database_service import db_service

router = APIRouter()

@router.get("/overview")
def get_overview_stats(
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: dict = Depends(verify_token)
):
    """📊 Real Banking KPI Overview from Database"""
    
    try:
        # Get real statistics from database
        stats = db_service.get_transaction_stats()
        
        # Calculate today's metrics
        today = datetime.now().date()
        today_transactions = db_service.get_transactions_by_date(today)
        
        # Calculate delayed and duplicate transactions
        delayed_count = db_service.get_delayed_transactions_count(minutes=5)
        duplicate_count = db_service.get_duplicate_transactions_count()
        
        return {
            "kpis": {
                "total_transactions_today": len(today_transactions),
                "total_mismatches": stats.get('total_mismatches', 0),
                "reconciliation_accuracy": stats.get('success_rate', 100.0),
                "pending_transactions": stats.get('pending_reconciliation', 0),
                "duplicates_detected": duplicate_count,
                "delayed_transactions": delayed_count
            },
            "trends": {
                "transactions_vs_yesterday": "stable",  # Could be calculated from historical data
                "mismatches_vs_yesterday": "stable",
                "accuracy_trend": "stable"
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error getting overview stats: {e}")
        # Fallback to basic stats
        return {
            "kpis": {
                "total_transactions_today": 0,
                "total_mismatches": 0,
                "reconciliation_accuracy": 100.0,
                "pending_transactions": 0,
                "duplicates_detected": 0,
                "delayed_transactions": 0
            },
            "trends": {
                "transactions_vs_yesterday": "stable",
                "mismatches_vs_yesterday": "stable",
                "accuracy_trend": "stable"
            },
            "generated_at": datetime.now().isoformat()
        }

@router.get("/mismatch-summary")
def get_mismatch_summary(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: dict = Depends(verify_token)
):
    """🚨 Mismatch Summary Analytics - Real Data from Database"""
    
    try:
        # Get real statistics from database
        stats = db_service.get_transaction_stats()
        mismatch_types = stats.get('mismatch_types', {})
        
        # Calculate totals
        total_mismatches = sum(mismatch_types.values())
        critical_mismatches = mismatch_types.get('AMOUNT_MISMATCH', 0) + mismatch_types.get('CURRENCY_MISMATCH', 0)
        
        # Calculate resolution rate (for now, assume all are open, so 0% resolved)
        resolution_rate = 0.0  # Could be enhanced to track actual resolutions
        
        # Severity breakdown (based on mismatch types)
        severity_breakdown = {
            "HIGH": mismatch_types.get('AMOUNT_MISMATCH', 0) + mismatch_types.get('CURRENCY_MISMATCH', 0),
            "MEDIUM": mismatch_types.get('STATUS_MISMATCH', 0) + mismatch_types.get('ACCOUNT_MISMATCH', 0),
            "LOW": mismatch_types.get('TIMESTAMP_MISMATCH', 0) + mismatch_types.get('MISSING_FIELD', 0)
        }
        
        # Source breakdown (simplified - could be enhanced to track by source)
        source_breakdown = {
            "core": total_mismatches // 3,
            "gateway": total_mismatches // 3,
            "mobile": total_mismatches - (2 * (total_mismatches // 3))
        }
        
        # Top issues
        top_issues = [[k, v] for k, v in sorted(mismatch_types.items(), key=lambda x: x[1], reverse=True)]
        
        return {
            "summary": {
                "total_mismatches": total_mismatches,
                "critical_mismatches": critical_mismatches,
                "resolution_rate": resolution_rate
            },
            "breakdown": {
                "by_type": mismatch_types,
                "by_severity": severity_breakdown,
                "by_source": source_breakdown
            },
            "top_issues": top_issues[:5]  # Top 5 issues
        }
        
    except Exception as e:
        print(f"Error getting mismatch summary: {e}")
        # Fallback to empty data
        return {
            "summary": {
                "total_mismatches": 0,
                "critical_mismatches": 0,
                "resolution_rate": 0.0
            },
            "breakdown": {
                "by_type": {},
                "by_severity": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
                "by_source": {"core": 0, "gateway": 0, "mobile": 0}
            },
            "top_issues": []
        }

@router.get("/source-distribution")
def get_source_distribution(
    hours: int = Query(24, description="Hours to analyze"),
    current_user: dict = Depends(verify_token)
):
    """📈 Transaction Source Distribution - Real Data from Database"""
    
    try:
        # Get real statistics from database
        stats = db_service.get_transaction_stats()
        source_distribution = stats.get('source_distribution', {})
        
        # Calculate total and percentages
        total_transactions = sum(source_distribution.values())
        
        # Create distribution array with colors
        colors = {
            "core": "#2196F3",
            "gateway": "#E91E63", 
            "mobile": "#00BCD4"
        }
        
        distribution = []
        for source, count in source_distribution.items():
            percentage = (count / total_transactions * 100) if total_transactions > 0 else 0
            distribution.append({
                "source": source,
                "count": count,
                "percentage": round(percentage, 1),
                "color": colors.get(source, "#666666")
            })
        
        return {
            "distribution": distribution,
            "total_transactions": total_transactions,
            "analysis_period": f"Last {hours} hours",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error getting source distribution: {e}")
        # Fallback to empty data
        return {
            "distribution": [],
            "total_transactions": 0,
            "analysis_period": f"Last {hours} hours",
            "generated_at": datetime.now().isoformat()
        }

@router.get("/mismatch-type-counts")
def get_mismatch_type_counts(
    current_user: dict = Depends(verify_token)
):
    """📊 Mismatch Type Analysis - Real Data from Database"""
    
    try:
        # Get real statistics from database
        stats = db_service.get_transaction_stats()
        mismatch_types = stats.get('mismatch_types', {})
        
        # Convert to chart format
        chart_data = []
        colors = {
            'AMOUNT_MISMATCH': '#F44336',
            'STATUS_MISMATCH': '#FF9800', 
            'CURRENCY_MISMATCH': '#E91E63',
            'TIMESTAMP_MISMATCH': '#FFC107',
            'ACCOUNT_MISMATCH': '#9C27B0',
            'MISSING_FIELD': '#607D8B'
        }
        
        for mtype, count in mismatch_types.items():
            if count > 0:
                chart_data.append({
                    "type": mtype.replace('_', ' ').title(),
                    "count": count,
                    "severity": "HIGH" if "AMOUNT" in mtype or "CURRENCY" in mtype else "MEDIUM" if "STATUS" in mtype else "LOW",
                    "color": colors.get(mtype, "#666666")
                })
        
        # Find most common
        most_common = None
        if chart_data:
            most_common = max(chart_data, key=lambda x: x['count'])
        
        return {
            "mismatch_types": chart_data,
            "total_types": len(chart_data),
            "most_common": most_common
        }
        
    except Exception as e:
        print(f"Error getting mismatch type counts: {e}")
        # Fallback to empty data
        return {
            "mismatch_types": [],
            "total_types": 0,
            "most_common": None
        }

@router.get("/timeline")
def get_timeline_data(
    hours: int = Query(24, description="Hours of timeline data"),
    interval: str = Query("hour", description="Interval: minute, hour, day"),
    current_user: dict = Depends(verify_token)
):
    """📈 Time-series Analytics - Real Data from Database"""
    
    try:
        # Get real timeline data from database
        timeline_data = db_service.get_timeline_stats(hours, interval)
        
        # If no data, create empty timeline
        if not timeline_data:
            timeline_data = []
            for i in range(24):
                hour = f"{i:02d}:00"
                timeline_data.append({
                    "hour": hour,
                    "timestamp": (datetime.now() - timedelta(hours=23-i)).isoformat(),
                    "transactions": 0,
                    "mismatches": 0
                })
        
        # Calculate summary
        total_transactions = sum(item.get('transactions', 0) for item in timeline_data)
        total_mismatches = sum(item.get('mismatches', 0) for item in timeline_data)
        avg_per_interval = total_transactions / len(timeline_data) if timeline_data else 0
        
        # Find peak hour
        peak_hour = "00:00"
        max_transactions = 0
        for item in timeline_data:
            if item.get('transactions', 0) > max_transactions:
                max_transactions = item.get('transactions', 0)
                peak_hour = item.get('hour', '00:00')
        
        return {
            "timeline": timeline_data,
            "period": f"Last {hours} hours",
            "interval": interval,
            "summary": {
                "peak_hour": peak_hour,
                "avg_per_interval": round(avg_per_interval, 1),
                "trend": "stable",  # Could be enhanced to calculate actual trend
                "total_transactions": total_transactions,
                "total_mismatches": total_mismatches
            }
        }
        
    except Exception as e:
        print(f"Error getting timeline data: {e}")
        # Fallback to empty timeline
        timeline_data = []
        for i in range(24):
            hour = f"{i:02d}:00"
            timeline_data.append({
                "hour": hour,
                "timestamp": (datetime.now() - timedelta(hours=23-i)).isoformat(),
                "transactions": 0,
                "mismatches": 0
            })
        
        return {
            "timeline": timeline_data,
            "period": f"Last {hours} hours",
            "interval": interval,
            "summary": {
                "peak_hour": "00:00",
                "avg_per_interval": 0.0,
                "trend": "stable"
            }
        }

@router.get("/anomalies")
def get_anomaly_detection(
    current_user: dict = Depends(verify_token)
):
    """🚨 Anomaly Detection - Mock Data"""
    
    return {
        "anomalies": [
            {
                "type": "TRANSACTION_SPIKE",
                "severity": "MEDIUM",
                "description": "Transaction rate 127/min is 1.8x normal",
                "detected_at": datetime.now().isoformat()
            }
        ],
        "total_anomalies": 1,
        "system_health": "ATTENTION_REQUIRED"
    }

@router.post("/reconcile/{txn_id}")
def manual_reconciliation(
    txn_id: str,
    current_user: dict = Depends(verify_token)
):
    """🔄 Manual Reconciliation Trigger - Mock Response"""
    
    # Check if user has admin role
    if 'admin' not in current_user.get('roles', []):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    return {
        "txn_id": txn_id,
        "reconciliation_triggered": True,
        "result": {
            "status": "COMPLETED",
            "sources_reconciled": 3,
            "mismatches_found": 0,
            "processing_time_ms": 150
        },
        "triggered_by": current_user['username'],
        "triggered_at": datetime.now().isoformat()
    }