"""
API Documentation Router for Banking-Grade Transaction Reconciliation Engine

This module provides comprehensive API documentation and endpoint information
"""

from fastapi import APIRouter, Depends, Request
from utils.response import success
from security.rbac_manager import require_viewer
from security.auth import get_current_user

router = APIRouter()

@router.get("/endpoints", dependencies=[Depends(require_viewer)])
def get_api_endpoints(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive list of all API endpoints"""
    
    endpoints = {
        "authentication": {
            "base_path": "/auth",
            "description": "Authentication and authorization endpoints",
            "endpoints": [
                {
                    "path": "/auth/login",
                    "method": "POST",
                    "description": "User login with credentials",
                    "auth_required": False
                },
                {
                    "path": "/auth/refresh",
                    "method": "POST", 
                    "description": "Refresh JWT token",
                    "auth_required": True
                }
            ]
        },
        "transactions": {
            "base_path": "/transactions",
            "description": "Transaction management and querying",
            "endpoints": [
                {
                    "path": "/transactions/",
                    "method": "GET",
                    "description": "Get all transactions with filtering and pagination",
                    "auth_required": True,
                    "min_role": "operator"
                },
                {
                    "path": "/transactions/stats",
                    "method": "GET",
                    "description": "Get transaction statistics",
                    "auth_required": True,
                    "min_role": "operator"
                },
                {
                    "path": "/transactions/{txn_id}",
                    "method": "GET",
                    "description": "Get specific transaction by ID",
                    "auth_required": True,
                    "min_role": "operator"
                },
                {
                    "path": "/transactions/{txn_id}/details",
                    "method": "GET",
                    "description": "Get comprehensive transaction details",
                    "auth_required": True,
                    "min_role": "operator"
                }
            ]
        },
        "mismatches": {
            "base_path": "/mismatches",
            "description": "Mismatch detection and resolution",
            "endpoints": [
                {
                    "path": "/mismatches/",
                    "method": "GET",
                    "description": "Get all mismatches with filtering",
                    "auth_required": True,
                    "min_role": "operator"
                },
                {
                    "path": "/mismatches/stats",
                    "method": "GET",
                    "description": "Get mismatch statistics",
                    "auth_required": True,
                    "min_role": "operator"
                },
                {
                    "path": "/mismatches/{mismatch_id}",
                    "method": "GET",
                    "description": "Get specific mismatch by ID",
                    "auth_required": True,
                    "min_role": "operator"
                }
            ]
        },
        "reports": {
            "base_path": "/reports",
            "description": "Comprehensive reporting system",
            "endpoints": [
                {
                    "path": "/reports/daily-summary",
                    "method": "GET",
                    "description": "Generate daily reconciliation summary",
                    "auth_required": True,
                    "min_role": "auditor"
                },
                {
                    "path": "/reports/failure-patterns",
                    "method": "GET",
                    "description": "Generate failure patterns report",
                    "auth_required": True,
                    "min_role": "auditor"
                }
            ]
        },
        "ai_insights": {
            "base_path": "/ai-insights",
            "description": "AI-powered analytics and insights",
            "endpoints": [
                {
                    "path": "/ai-insights/anomalies",
                    "method": "GET",
                    "description": "Detect transaction anomalies",
                    "auth_required": True,
                    "min_role": "operator"
                },
                {
                    "path": "/ai-insights/fraud-scores",
                    "method": "GET",
                    "description": "Calculate fraud risk scores",
                    "auth_required": True,
                    "min_role": "operator"
                },
                {
                    "path": "/ai-insights/recommendations",
                    "method": "GET",
                    "description": "Get AI-powered recommendations",
                    "auth_required": True,
                    "min_role": "operator"
                },
                {
                    "path": "/ai-insights/model-performance",
                    "method": "GET",
                    "description": "Get AI model performance metrics",
                    "auth_required": True,
                    "min_role": "operator"
                }
            ]
        },
        "live_stream": {
            "base_path": "/live-stream",
            "description": "Real-time streaming and monitoring",
            "endpoints": [
                {
                    "path": "/live-stream/stats",
                    "method": "GET",
                    "description": "Get real-time streaming statistics",
                    "auth_required": True,
                    "min_role": "operator"
                },
                {
                    "path": "/live-stream/recent",
                    "method": "GET",
                    "description": "Get recent transactions for live display",
                    "auth_required": True,
                    "min_role": "operator"
                },
                {
                    "path": "/live-stream/control",
                    "method": "POST",
                    "description": "Control live stream (start/stop/pause)",
                    "auth_required": True,
                    "min_role": "operator"
                },
                {
                    "path": "/live-stream/performance",
                    "method": "GET",
                    "description": "Get streaming performance metrics",
                    "auth_required": True,
                    "min_role": "operator"
                }
            ]
        },
        "system_health": {
            "base_path": "/system-health",
            "description": "System monitoring and health checks",
            "endpoints": [
                {
                    "path": "/system-health/overview",
                    "method": "GET",
                    "description": "Get comprehensive system health overview",
                    "auth_required": True,
                    "min_role": "admin"
                },
                {
                    "path": "/system-health/kafka",
                    "method": "GET",
                    "description": "Get Kafka cluster health metrics",
                    "auth_required": True,
                    "min_role": "admin"
                },
                {
                    "path": "/system-health/database",
                    "method": "GET",
                    "description": "Get database health and performance",
                    "auth_required": True,
                    "min_role": "admin"
                },
                {
                    "path": "/system-health/redis",
                    "method": "GET",
                    "description": "Get Redis cache health metrics",
                    "auth_required": True,
                    "min_role": "admin"
                }
            ]
        },
        "admin": {
            "base_path": "/admin",
            "description": "Administrative functions and system management",
            "endpoints": [
                {
                    "path": "/admin/",
                    "method": "GET",
                    "description": "Admin dashboard access",
                    "auth_required": True,
                    "min_role": "admin"
                },
                {
                    "path": "/admin/audit-logs",
                    "method": "GET",
                    "description": "Get audit logs with filtering",
                    "auth_required": True,
                    "min_role": "admin"
                },
                {
                    "path": "/admin/system-health",
                    "method": "GET",
                    "description": "Get system health status",
                    "auth_required": True,
                    "min_role": "admin"
                },
                {
                    "path": "/admin/security/reset-rate-limits",
                    "method": "POST",
                    "description": "Reset all rate limits",
                    "auth_required": True,
                    "min_role": "admin"
                }
            ]
        }
    }
    
    return success(data={
        "api_version": "1.0.0",
        "total_endpoints": sum(len(category["endpoints"]) for category in endpoints.values()),
        "categories": len(endpoints),
        "endpoints": endpoints,
        "authentication": {
            "type": "JWT Bearer Token",
            "roles": ["admin", "auditor", "operator", "viewer"],
            "role_hierarchy": "admin > auditor > operator > viewer"
        },
        "real_time": {
            "socket_io": True,
            "events": [
                "new_transaction",
                "new_mismatch", 
                "stats_update",
                "ai_insight",
                "system_alert",
                "transaction_flow_update"
            ]
        }
    })

@router.get("/socket-events", dependencies=[Depends(require_viewer)])
def get_socket_events(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get Socket.IO event documentation"""
    
    socket_events = {
        "client_events": {
            "description": "Events that clients can emit to the server",
            "events": [
                {
                    "event": "connect",
                    "description": "Client connects to server",
                    "data": None
                },
                {
                    "event": "disconnect", 
                    "description": "Client disconnects from server",
                    "data": None
                },
                {
                    "event": "join_room",
                    "description": "Join a specific room for targeted updates",
                    "data": {"room": "string"}
                },
                {
                    "event": "leave_room",
                    "description": "Leave a specific room",
                    "data": {"room": "string"}
                },
                {
                    "event": "ping",
                    "description": "Ping server for connection testing",
                    "data": {}
                }
            ]
        },
        "server_events": {
            "description": "Events that server emits to clients",
            "events": [
                {
                    "event": "connection_status",
                    "description": "Connection status update",
                    "data": {
                        "status": "connected|disconnected",
                        "client_id": "string",
                        "timestamp": "ISO string"
                    }
                },
                {
                    "event": "new_transaction",
                    "description": "New transaction received",
                    "data": {
                        "id": "string",
                        "source": "core|gateway|mobile",
                        "amount": "number",
                        "status": "string",
                        "timestamp": "ISO string"
                    }
                },
                {
                    "event": "new_mismatch",
                    "description": "New mismatch detected",
                    "data": {
                        "id": "string",
                        "type": "amount|status|timestamp|missing",
                        "severity": "high|medium|low",
                        "timestamp": "ISO string"
                    }
                },
                {
                    "event": "stats_update",
                    "description": "Dashboard statistics update",
                    "data": {
                        "totalTransactions": "number",
                        "matchedTransactions": "number",
                        "mismatches": "number",
                        "timestamp": "ISO string"
                    }
                },
                {
                    "event": "ai_insight",
                    "description": "AI-generated insight or alert",
                    "data": {
                        "type": "anomaly|performance|security|trend",
                        "message": "string",
                        "severity": "high|medium|low|info",
                        "confidence": "number",
                        "timestamp": "ISO string"
                    }
                },
                {
                    "event": "system_alert",
                    "description": "System health alert",
                    "data": {
                        "type": "warning|error|info",
                        "message": "string",
                        "severity": "high|medium|low",
                        "component": "system|database|redis|kafka",
                        "timestamp": "ISO string"
                    }
                },
                {
                    "event": "transaction_flow_update",
                    "description": "Real-time transaction flow data for charts",
                    "data": {
                        "coreBanking": "number",
                        "mobileApp": "number", 
                        "paymentGateway": "number",
                        "totalEvents": "number",
                        "timestamp": "ISO string"
                    }
                },
                {
                    "event": "pong",
                    "description": "Response to ping",
                    "data": {
                        "timestamp": "ISO string",
                        "client_id": "string"
                    }
                }
            ]
        }
    }
    
    return success(data=socket_events)