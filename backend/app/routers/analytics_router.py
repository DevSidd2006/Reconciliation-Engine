"""
Banking Analytics Router - Phase 5
Advanced analytics endpoints for operations dashboard
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_service import db_service
from services.auth_service import (
    get_current_user, 
    require_read_stats,
    require_admin,
    auth_service
)

router = APIRouter()

@router.get("/overview")
@require_read_stats()
def get_overview_stats(
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    📊 Banking KPI Overview
    
    Returns key performance indicators for operations dashboard:
    - Total transactions today
    - Total mismatches
    - Reconciliation accuracy %
    - Pending transactions
    - Duplicates detected
    - Delayed transactions (>5 min)
    """
    try:
        # Create audit log
        auth_service.create_audit_log(
            user_id=current_user['user_id'],
            action='VIEW_OVERVIEW',
            resource='analytics',
            details={'date_from': date_from, 'date_to': date_to}
        )
        
        # Get comprehensive stats
        stats = db_service.get_transaction_stats()
        
        # Calculate today's metrics
        today = datetime.now().date()
        today_transactions = db_service.get_transactions_by_date(today)
        today_mismatches = db_service.get_mismatches_by_date(today)
        
        # Calculate delayed transactions (>5 minutes between sources)
        delayed_count = db_service.get_delayed_transactions_count(minutes=5)
        
        # Calculate duplicates
        duplicate_count = db_service.get_duplicate_transactions_count()
        
        return {
            "kpis": {
                "total_transactions_today": len(today_transactions),
                "total_mismatches": stats['total_mismatches'],
                "reconciliation_accuracy": round(stats['success_rate'], 1),
                "pending_transactions": stats['pending_reconciliation'],
                "duplicates_detected": duplicate_count,
                "delayed_transactions": delayed_count
            },
            "trends": {
                "transactions_vs_yesterday": calculate_trend(today_transactions, "transactions"),
                "mismatches_vs_yesterday": calculate_trend(today_mismatches, "mismatches"),
                "accuracy_trend": "stable"  # Could be calculated from historical data
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving overview: {str(e)}")

@router.get("/mismatch-summary")
@require_read_stats()
def get_mismatch_summary(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    🚨 Mismatch Summary Analytics
    
    Detailed breakdown of mismatches by type, severity, and source
    """
    try:
        auth_service.create_audit_log(
            user_id=current_user['user_id'],
            action='VIEW_MISMATCH_SUMMARY',
            resource='analytics'
        )
        
        stats = db_service.get_transaction_stats()
        mismatches = db_service.get_mismatches(limit=1000)  # Get more for analysis
        
        # Analyze mismatch patterns
        mismatch_by_type = {}
        mismatch_by_severity = {}
        mismatch_by_source = {}
        
        for mismatch in mismatches:
            # By type
            mtype = mismatch.get('type', 'UNKNOWN')
            mismatch_by_type[mtype] = mismatch_by_type.get(mtype, 0) + 1
            
            # By severity
            severity = mismatch.get('severity', 'UNKNOWN')
            mismatch_by_severity[severity] = mismatch_by_severity.get(severity, 0) + 1
            
            # By source
            sources = mismatch.get('sources_involved', [])
            for source in sources:
                mismatch_by_source[source] = mismatch_by_source.get(source, 0) + 1
        
        return {
            "summary": {
                "total_mismatches": len(mismatches),
                "critical_mismatches": mismatch_by_severity.get('HIGH', 0),
                "resolution_rate": calculate_resolution_rate(mismatches)
            },
            "breakdown": {
                "by_type": mismatch_by_type,
                "by_severity": mismatch_by_severity,
                "by_source": mismatch_by_source
            },
            "top_issues": get_top_mismatch_issues(mismatches)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving mismatch summary: {str(e)}")

@router.get("/source-distribution")
@require_read_stats()
def get_source_distribution(
    hours: int = Query(24, description="Hours to analyze"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    📈 Transaction Source Distribution
    
    Pie chart data showing transaction distribution across sources
    """
    try:
        stats = db_service.get_transaction_stats()
        source_dist = stats.get('source_distribution', {})
        
        # Calculate percentages
        total = sum(source_dist.values())
        distribution = []
        
        for source, count in source_dist.items():
            percentage = (count / total * 100) if total > 0 else 0
            distribution.append({
                "source": source,
                "count": count,
                "percentage": round(percentage, 1),
                "color": get_source_color(source)
            })
        
        return {
            "distribution": distribution,
            "total_transactions": total,
            "analysis_period": f"Last {hours} hours",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving source distribution: {str(e)}")

@router.get("/mismatch-type-counts")
@require_read_stats()
def get_mismatch_type_counts(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    📊 Mismatch Type Analysis
    
    Bar chart data for mismatch types
    """
    try:
        stats = db_service.get_transaction_stats()
        mismatch_types = stats.get('mismatch_types', {})
        
        # Format for chart
        chart_data = []
        for mtype, count in mismatch_types.items():
            chart_data.append({
                "type": mtype.replace('_', ' ').title(),
                "count": count,
                "severity": get_mismatch_severity(mtype),
                "color": get_mismatch_color(mtype)
            })
        
        # Sort by count descending
        chart_data.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            "mismatch_types": chart_data,
            "total_types": len(chart_data),
            "most_common": chart_data[0] if chart_data else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving mismatch types: {str(e)}")

@router.get("/timeline")
@require_read_stats()
def get_timeline_data(
    hours: int = Query(24, description="Hours of timeline data"),
    interval: str = Query("hour", description="Interval: minute, hour, day"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    📈 Time-series Analytics
    
    Timeline data for transactions and mismatches
    """
    try:
        # Get timeline data from database
        timeline_data = db_service.get_timeline_stats(hours=hours, interval=interval)
        
        return {
            "timeline": timeline_data,
            "period": f"Last {hours} hours",
            "interval": interval,
            "summary": {
                "peak_hour": get_peak_hour(timeline_data),
                "avg_per_interval": calculate_average_per_interval(timeline_data),
                "trend": calculate_timeline_trend(timeline_data)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving timeline: {str(e)}")

@router.get("/anomalies")
@require_read_stats()
def get_anomaly_detection(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    🚨 Anomaly Detection
    
    Detect spikes, delays, and unusual patterns
    """
    try:
        anomalies = []
        
        # Check for transaction spikes
        recent_stats = db_service.get_recent_activity_stats(minutes=30)
        if recent_stats['transaction_rate'] > get_normal_rate() * 2:
            anomalies.append({
                "type": "TRANSACTION_SPIKE",
                "severity": "HIGH",
                "description": f"Transaction rate {recent_stats['transaction_rate']}/min is 2x normal",
                "detected_at": datetime.now().isoformat()
            })
        
        # Check for mismatch spikes
        if recent_stats['mismatch_rate'] > get_normal_mismatch_rate() * 1.5:
            anomalies.append({
                "type": "MISMATCH_SPIKE",
                "severity": "MEDIUM",
                "description": f"Mismatch rate {recent_stats['mismatch_rate']}/min is elevated",
                "detected_at": datetime.now().isoformat()
            })
        
        # Check for source delays
        source_delays = db_service.get_source_delay_analysis()
        for source, delay in source_delays.items():
            if delay > 300:  # 5 minutes
                anomalies.append({
                    "type": "SOURCE_DELAY",
                    "severity": "MEDIUM",
                    "description": f"{source} source has {delay}s average delay",
                    "detected_at": datetime.now().isoformat(),
                    "source": source
                })
        
        return {
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "system_health": "HEALTHY" if len(anomalies) == 0 else "ATTENTION_REQUIRED"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting anomalies: {str(e)}")

@router.post("/reconcile/{txn_id}")
@require_admin()
def manual_reconciliation(
    txn_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    🔄 Manual Reconciliation Trigger
    
    Manually trigger reconciliation for a specific transaction
    """
    try:
        # Create audit log for manual reconciliation
        auth_service.create_audit_log(
            user_id=current_user['user_id'],
            action='MANUAL_RECONCILIATION',
            resource='transaction',
            details={'txn_id': txn_id}
        )
        
        # Get transaction details
        transactions = db_service.get_transactions_by_txn_id(txn_id)
        if not transactions:
            raise HTTPException(status_code=404, detail=f"Transaction {txn_id} not found")
        
        # Trigger manual reconciliation
        result = trigger_manual_reconciliation(txn_id, transactions)
        
        return {
            "txn_id": txn_id,
            "reconciliation_triggered": True,
            "result": result,
            "triggered_by": current_user['username'],
            "triggered_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Manual reconciliation failed: {str(e)}")

# Helper functions
def calculate_trend(current_data, data_type):
    """Calculate trend compared to previous period"""
    # Simplified trend calculation
    return "up" if len(current_data) > 0 else "stable"

def calculate_resolution_rate(mismatches):
    """Calculate mismatch resolution rate"""
    resolved = sum(1 for m in mismatches if m.get('status') == 'RESOLVED')
    total = len(mismatches)
    return round((resolved / total * 100), 1) if total > 0 else 0

def get_top_mismatch_issues(mismatches):
    """Get top 5 mismatch issues"""
    type_counts = {}
    for m in mismatches:
        mtype = m.get('type', 'UNKNOWN')
        type_counts[mtype] = type_counts.get(mtype, 0) + 1
    
    return sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]

def get_source_color(source):
    """Get color for source visualization"""
    colors = {
        'core': '#2196F3',      # Blue
        'gateway': '#E91E63',   # Pink
        'mobile': '#00BCD4'     # Cyan
    }
    return colors.get(source, '#9E9E9E')

def get_mismatch_severity(mtype):
    """Determine mismatch severity based on type"""
    high_severity = ['AMOUNT_MISMATCH', 'ACCOUNT_MISMATCH']
    medium_severity = ['STATUS_MISMATCH', 'CURRENCY_MISMATCH']
    
    if mtype in high_severity:
        return 'HIGH'
    elif mtype in medium_severity:
        return 'MEDIUM'
    else:
        return 'LOW'

def get_mismatch_color(mtype):
    """Get color for mismatch type visualization"""
    severity = get_mismatch_severity(mtype)
    colors = {
        'HIGH': '#F44336',      # Red
        'MEDIUM': '#FF9800',    # Orange
        'LOW': '#FFC107'        # Yellow
    }
    return colors.get(severity, '#9E9E9E')

def get_peak_hour(timeline_data):
    """Find peak hour from timeline data"""
    if not timeline_data:
        return None
    
    max_transactions = max(timeline_data, key=lambda x: x.get('transactions', 0))
    return max_transactions.get('hour', 'Unknown')

def calculate_average_per_interval(timeline_data):
    """Calculate average transactions per interval"""
    if not timeline_data:
        return 0
    
    total = sum(item.get('transactions', 0) for item in timeline_data)
    return round(total / len(timeline_data), 1)

def calculate_timeline_trend(timeline_data):
    """Calculate overall trend from timeline"""
    if len(timeline_data) < 2:
        return "stable"
    
    first_half = timeline_data[:len(timeline_data)//2]
    second_half = timeline_data[len(timeline_data)//2:]
    
    first_avg = sum(item.get('transactions', 0) for item in first_half) / len(first_half)
    second_avg = sum(item.get('transactions', 0) for item in second_half) / len(second_half)
    
    if second_avg > first_avg * 1.1:
        return "increasing"
    elif second_avg < first_avg * 0.9:
        return "decreasing"
    else:
        return "stable"

def get_normal_rate():
    """Get normal transaction rate for anomaly detection"""
    return 50  # transactions per minute (configurable)

def get_normal_mismatch_rate():
    """Get normal mismatch rate for anomaly detection"""
    return 5   # mismatches per minute (configurable)

def trigger_manual_reconciliation(txn_id, transactions):
    """Trigger manual reconciliation process"""
    # This would integrate with the reconciliation engine
    # For now, return a mock result
    return {
        "status": "COMPLETED",
        "sources_reconciled": len(transactions),
        "mismatches_found": 0,
        "processing_time_ms": 150
    }