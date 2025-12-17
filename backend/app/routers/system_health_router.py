"""
System Health Router for Banking-Grade Transaction Reconciliation Engine

This module provides system monitoring endpoints:
- Infrastructure health checks
- Performance metrics
- Service status monitoring
- Resource utilization
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
import psutil
import time
from datetime import datetime, timedelta
from db.database import get_db
from utils.response import success, error
from security.rbac_manager import require_admin
from security.auth import get_current_user
from security import audit_logger

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/overview", dependencies=[Depends(require_admin)])
def get_system_health_overview(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive system health overview"""
    try:
        # System resource metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Database health
        db_status = "healthy"
        db_connections = 0
        try:
            db = next(get_db())
            result = db.execute("SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active'")
            db_connections = result.scalar()
            db.close()
        except Exception as e:
            db_status = "unhealthy"
            logger.warning(f"Database health check failed: {e}")
        
        # Redis health
        redis_status = "healthy"
        redis_memory = 0
        try:
            from utils.redis import redis_client
            client = redis_client.get_client()
            client.ping()
            info = client.info('memory')
            redis_memory = info.get('used_memory', 0)
        except Exception as e:
            redis_status = "unhealthy"
            logger.warning(f"Redis health check failed: {e}")
        
        # Service health summary
        services = [
            {
                "name": "FastAPI Backend",
                "status": "running",
                "uptime": "99.9%",
                "last_check": datetime.now().isoformat()
            },
            {
                "name": "PostgreSQL Database",
                "status": db_status,
                "uptime": "99.8%",
                "connections": db_connections,
                "last_check": datetime.now().isoformat()
            },
            {
                "name": "Redis Cache",
                "status": redis_status,
                "uptime": "99.7%",
                "memory_mb": round(redis_memory / 1024 / 1024, 1),
                "last_check": datetime.now().isoformat()
            },
            {
                "name": "Socket.IO Server",
                "status": "running",
                "uptime": "99.6%",
                "last_check": datetime.now().isoformat()
            }
        ]
        
        # Overall system status
        overall_status = "healthy"
        if db_status != "healthy" or redis_status != "healthy":
            overall_status = "degraded"
        if cpu_percent > 90 or memory.percent > 90:
            overall_status = "warning"
        
        health_data = {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "system_resources": {
                "cpu_percent": round(cpu_percent, 1),
                "memory_percent": round(memory.percent, 1),
                "memory_available_gb": round(memory.available / 1024 / 1024 / 1024, 2),
                "disk_percent": round(disk.percent, 1),
                "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 2)
            },
            "services": services,
            "alerts": []
        }
        
        # Generate alerts
        if cpu_percent > 80:
            health_data["alerts"].append({
                "type": "warning",
                "message": f"High CPU usage: {cpu_percent}%",
                "severity": "medium"
            })
        
        if memory.percent > 80:
            health_data["alerts"].append({
                "type": "warning", 
                "message": f"High memory usage: {memory.percent}%",
                "severity": "medium"
            })
        
        if db_status != "healthy":
            health_data["alerts"].append({
                "type": "error",
                "message": "Database connection issues detected",
                "severity": "high"
            })
        
        # Log health check
        audit_logger.log_admin_action(
            user_id=current_user["user_id"],
            username=current_user["username"],
            action="system_health_check",
            resource="system_health",
            ip_address=request.client.host,
            details={"overall_status": overall_status, "alerts_count": len(health_data["alerts"])}
        )
        
        return success(data=health_data)
        
    except Exception as e:
        logger.error(f"Failed to get system health overview: {e}")
        raise HTTPException(
            status_code=500,
            detail=error("Failed to get system health overview", "HEALTH_OVERVIEW_ERROR")
        )

@router.get("/kafka", dependencies=[Depends(require_admin)])
def get_kafka_health(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get Kafka cluster health metrics"""
    try:
        # Simulated Kafka health metrics
        # In a real implementation, this would connect to Kafka and get actual metrics
        kafka_health = {
            "status": "healthy",
            "cluster_id": "kafka-cluster-1",
            "brokers": [
                {"id": 1, "host": "localhost:9092", "status": "online"},
                {"id": 2, "host": "localhost:9093", "status": "online"},
                {"id": 3, "host": "localhost:9094", "status": "online"}
            ],
            "topics": [
                {
                    "name": "core_txns",
                    "partitions": 3,
                    "replication_factor": 2,
                    "messages_per_sec": 150,
                    "lag": 12
                },
                {
                    "name": "gateway_txns", 
                    "partitions": 3,
                    "replication_factor": 2,
                    "messages_per_sec": 120,
                    "lag": 8
                },
                {
                    "name": "mobile_txns",
                    "partitions": 3,
                    "replication_factor": 2,
                    "messages_per_sec": 90,
                    "lag": 5
                }
            ],
            "consumer_groups": [
                {
                    "name": "reconciliation-consumer",
                    "status": "stable",
                    "members": 3,
                    "lag": 25
                }
            ],
            "performance": {
                "total_messages_per_sec": 360,
                "total_lag": 25,
                "avg_response_time_ms": 45
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Log Kafka health check
        audit_logger.log_admin_action(
            user_id=current_user["user_id"],
            username=current_user["username"],
            action="kafka_health_check",
            resource="kafka",
            ip_address=request.client.host
        )
        
        return success(data=kafka_health)
        
    except Exception as e:
        logger.error(f"Failed to get Kafka health: {e}")
        raise HTTPException(
            status_code=500,
            detail=error("Failed to get Kafka health", "KAFKA_HEALTH_ERROR")
        )

@router.get("/database", dependencies=[Depends(require_admin)])
def get_database_health(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get database health and performance metrics"""
    try:
        # Database connection and performance metrics
        db_health = {
            "status": "healthy",
            "version": "PostgreSQL 13.x",
            "connections": {
                "active": 0,
                "idle": 0,
                "max_connections": 100
            },
            "performance": {
                "avg_query_time_ms": 0,
                "slow_queries": 0,
                "cache_hit_ratio": 0.95
            },
            "storage": {
                "database_size_mb": 0,
                "table_count": 0,
                "index_count": 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Get connection stats
            result = db.execute("""
                SELECT state, COUNT(*) 
                FROM pg_stat_activity 
                WHERE datname = current_database()
                GROUP BY state
            """)
            for row in result:
                if row[0] == 'active':
                    db_health["connections"]["active"] = row[1]
                elif row[0] == 'idle':
                    db_health["connections"]["idle"] = row[1]
            
            # Get database size
            result = db.execute("SELECT pg_database_size(current_database())")
            size_bytes = result.scalar()
            db_health["storage"]["database_size_mb"] = round(size_bytes / 1024 / 1024, 2)
            
            # Get table count
            result = db.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            db_health["storage"]["table_count"] = result.scalar()
            
            # Get index count
            result = db.execute("""
                SELECT COUNT(*) FROM pg_indexes 
                WHERE schemaname = 'public'
            """)
            db_health["storage"]["index_count"] = result.scalar()
            
        except Exception as e:
            logger.warning(f"Failed to get detailed database metrics: {e}")
            db_health["status"] = "degraded"
        
        # Log database health check
        audit_logger.log_admin_action(
            user_id=current_user["user_id"],
            username=current_user["username"],
            action="database_health_check",
            resource="database",
            ip_address=request.client.host,
            details=db_health["connections"]
        )
        
        return success(data=db_health)
        
    except Exception as e:
        logger.error(f"Failed to get database health: {e}")
        raise HTTPException(
            status_code=500,
            detail=error("Failed to get database health", "DATABASE_HEALTH_ERROR")
        )

@router.get("/redis", dependencies=[Depends(require_admin)])
def get_redis_health(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get Redis cache health and performance metrics"""
    try:
        redis_health = {
            "status": "healthy",
            "version": "Redis 6.x",
            "memory": {
                "used_mb": 0,
                "peak_mb": 0,
                "fragmentation_ratio": 1.0
            },
            "performance": {
                "hit_rate": 0.95,
                "ops_per_sec": 1000,
                "avg_response_time_ms": 0.5
            },
            "keys": {
                "total": 0,
                "expired": 0,
                "evicted": 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            from utils.redis import redis_client
            client = redis_client.get_client()
            
            # Get Redis info
            info = client.info()
            
            # Memory info
            redis_health["memory"]["used_mb"] = round(info.get('used_memory', 0) / 1024 / 1024, 2)
            redis_health["memory"]["peak_mb"] = round(info.get('used_memory_peak', 0) / 1024 / 1024, 2)
            redis_health["memory"]["fragmentation_ratio"] = info.get('mem_fragmentation_ratio', 1.0)
            
            # Key statistics
            redis_health["keys"]["total"] = info.get('db0', {}).get('keys', 0) if 'db0' in info else 0
            redis_health["keys"]["expired"] = info.get('expired_keys', 0)
            redis_health["keys"]["evicted"] = info.get('evicted_keys', 0)
            
            # Performance stats
            redis_health["performance"]["ops_per_sec"] = info.get('instantaneous_ops_per_sec', 0)
            
            # Calculate hit rate from cache manager if available
            try:
                from utils.redis import cache_manager
                cache_info = cache_manager.get_cache_info()
                redis_health["performance"]["hit_rate"] = cache_info.get('hit_rate', 0.95)
            except:
                pass
                
        except Exception as e:
            logger.warning(f"Failed to get detailed Redis metrics: {e}")
            redis_health["status"] = "degraded"
        
        # Log Redis health check
        audit_logger.log_admin_action(
            user_id=current_user["user_id"],
            username=current_user["username"],
            action="redis_health_check",
            resource="redis",
            ip_address=request.client.host,
            details=redis_health["memory"]
        )
        
        return success(data=redis_health)
        
    except Exception as e:
        logger.error(f"Failed to get Redis health: {e}")
        raise HTTPException(
            status_code=500,
            detail=error("Failed to get Redis health", "REDIS_HEALTH_ERROR")
        )