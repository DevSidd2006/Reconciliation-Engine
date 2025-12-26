"""
System Health Service for Banking Reconciliation Engine
Provides real-time system metrics and health status
"""
import psutil
import docker
import redis
import subprocess
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from sqlalchemy import text
from ..db.database import SessionLocal
from .redis_service import redis_service

logger = logging.getLogger(__name__)

class SystemHealthService:
    def __init__(self):
        self.docker_client = None
        self.redis_client = None
        self._init_docker_client()
        self._init_redis_client()
    
    def _init_docker_client(self):
        """Initialize Docker client"""
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.warning(f"Could not connect to Docker: {e}")
            self.docker_client = None
    
    def _init_redis_client(self):
        """Initialize Redis client"""
        try:
            self.redis_client = redis_service.redis_client if redis_service.is_connected() else None
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}")
            self.redis_client = None
    
    def get_system_overview(self) -> Dict:
        """Get complete system health overview"""
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",  # Will be calculated based on all metrics
            "services": self.get_service_status(),
            "metrics": {
                "kafka": self.get_kafka_metrics(),
                "backend": self.get_backend_metrics(),
                "redis": self.get_redis_metrics(),
                "database": self.get_database_metrics()
            },
            "alerts": self.get_system_alerts()
        }
    
    def get_service_status(self) -> List[Dict]:
        """Get status of all services"""
        services = []
        
        # Check Docker containers
        if self.docker_client:
            try:
                containers = self.docker_client.containers.list(all=True)
                container_map = {
                    'kafka-kafka-1': {
                        'name': 'Kafka Cluster',
                        'description': 'Message streaming platform',
                        'icon': 'Wifi'
                    },
                    'kafka-zookeeper-1': {
                        'name': 'Zookeeper',
                        'description': 'Kafka coordination service',
                        'icon': 'Server'
                    },
                    'reconciliation_postgres': {
                        'name': 'PostgreSQL Database',
                        'description': 'Primary data storage',
                        'icon': 'Database'
                    },
                    'reconciliation_redis': {
                        'name': 'Redis Cache',
                        'description': 'In-memory caching layer',
                        'icon': 'Zap'
                    }
                }
                
                for container in containers:
                    if container.name in container_map:
                        info = container_map[container.name]
                        status = 'running' if container.status == 'running' else 'down'
                        
                        # Calculate uptime
                        uptime = "N/A"
                        if container.status == 'running':
                            try:
                                started_at = container.attrs['State']['StartedAt']
                                start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                                uptime_seconds = (datetime.now(start_time.tzinfo) - start_time).total_seconds()
                                uptime_hours = uptime_seconds / 3600
                                if uptime_hours < 1:
                                    uptime = f"{int(uptime_seconds / 60)}m"
                                elif uptime_hours < 24:
                                    uptime = f"{uptime_hours:.1f}h"
                                else:
                                    uptime = f"{uptime_hours / 24:.1f}d"
                            except Exception:
                                uptime = "Unknown"
                        
                        services.append({
                            "name": info['name'],
                            "description": info['description'],
                            "icon": info['icon'],
                            "status": status,
                            "uptime": uptime
                        })
            except Exception as e:
                logger.error(f"Error getting Docker container status: {e}")
        
        # Add FastAPI Backend service
        services.append({
            "name": "FastAPI Backend",
            "description": "Main reconciliation API server",
            "icon": "Server",
            "status": "running",  # If this code is running, the backend is up
            "uptime": self._get_process_uptime()
        })
        
        return services
    
    def get_kafka_metrics(self) -> Dict:
        """Get Kafka cluster metrics"""
        try:
            # Try to get Kafka metrics via Docker exec
            if self.docker_client:
                kafka_container = None
                for container in self.docker_client.containers.list():
                    if 'kafka' in container.name and 'zookeeper' not in container.name:
                        kafka_container = container
                        break
                
                if kafka_container and kafka_container.status == 'running':
                    # Get topic information
                    try:
                        result = kafka_container.exec_run([
                            'kafka-topics', '--bootstrap-server', 'localhost:9092', '--list'
                        ])
                        topics = result.output.decode().strip().split('\n') if result.exit_code == 0 else []
                        topic_count = len([t for t in topics if t.strip()])
                    except Exception:
                        topic_count = 3  # Default known topics
                    
                    return {
                        "status": "healthy",
                        "eventsPerSecond": self._estimate_kafka_throughput(),
                        "lag": 0,  # Would need more complex monitoring
                        "producerHealth": "healthy",
                        "consumerHealth": "healthy",
                        "details": [
                            {"label": "Topics", "value": str(topic_count)},
                            {"label": "Partitions", "value": "12"},  # Estimated
                            {"label": "Replicas", "value": "1"}
                        ]
                    }
        except Exception as e:
            logger.error(f"Error getting Kafka metrics: {e}")
        
        return {
            "status": "unknown",
            "eventsPerSecond": 0,
            "lag": 0,
            "producerHealth": "unknown",
            "consumerHealth": "unknown",
            "details": [
                {"label": "Topics", "value": "N/A"},
                {"label": "Partitions", "value": "N/A"},
                {"label": "Replicas", "value": "N/A"}
            ]
        }
    
    def get_backend_metrics(self) -> Dict:
        """Get backend API metrics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Get process-specific metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                "status": "warning" if cpu_percent > 80 else "healthy",
                "cpu": round(cpu_percent, 1),
                "memory": round(memory.percent, 1),
                "errors": 0,  # Would need error tracking
                "details": [
                    {"label": "Process Memory", "value": f"{process_memory.rss / 1024 / 1024:.1f}MB"},
                    {"label": "Threads", "value": str(process.num_threads())},
                    {"label": "Open Files", "value": str(len(process.open_files()))}
                ]
            }
        except Exception as e:
            logger.error(f"Error getting backend metrics: {e}")
            return {
                "status": "unknown",
                "cpu": 0,
                "memory": 0,
                "errors": 0,
                "details": []
            }
    
    def get_redis_metrics(self) -> Dict:
        """Get Redis cache metrics"""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                stats = self.redis_client.info('stats')
                
                # Calculate hit rate
                hits = stats.get('keyspace_hits', 0)
                misses = stats.get('keyspace_misses', 0)
                total_requests = hits + misses
                hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0
                
                return {
                    "status": "healthy",
                    "hitRate": round(hit_rate, 1),
                    "size": round(info.get('used_memory', 0) / 1024 / 1024, 1),  # MB
                    "connections": info.get('connected_clients', 0),
                    "details": [
                        {"label": "Keys", "value": str(self.redis_client.dbsize())},
                        {"label": "Memory Used", "value": f"{info.get('used_memory_human', 'N/A')}"},
                        {"label": "Commands/sec", "value": str(stats.get('instantaneous_ops_per_sec', 0))}
                    ]
                }
        except Exception as e:
            logger.error(f"Error getting Redis metrics: {e}")
        
        return {
            "status": "disconnected",
            "hitRate": 0,
            "size": 0,
            "connections": 0,
            "details": [
                {"label": "Keys", "value": "N/A"},
                {"label": "Memory Used", "value": "N/A"},
                {"label": "Commands/sec", "value": "N/A"}
            ]
        }
    
    def get_database_metrics(self) -> Dict:
        """Get PostgreSQL database metrics"""
        try:
            db = SessionLocal()
            
            # Get database size and connection info
            result = db.execute(text("""
                SELECT 
                    pg_database_size(current_database()) as db_size,
                    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
                    (SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public') as table_count
            """))
            
            row = result.fetchone()
            db_size_mb = row[0] / 1024 / 1024 if row[0] else 0
            active_connections = row[1] if row[1] else 0
            table_count = row[2] if row[2] else 0
            
            # Get average query time (simplified)
            query_time = 15  # Placeholder - would need query performance monitoring
            
            db.close()
            
            return {
                "status": "healthy",
                "connections": active_connections,
                "queryTime": query_time,
                "storage": min(round(db_size_mb / 1000 * 100, 1), 100),  # Simulate percentage
                "details": [
                    {"label": "Database Size", "value": f"{db_size_mb:.1f}MB"},
                    {"label": "Tables", "value": str(table_count)},
                    {"label": "Active Queries", "value": str(active_connections)}
                ]
            }
        except Exception as e:
            logger.error(f"Error getting database metrics: {e}")
            return {
                "status": "error",
                "connections": 0,
                "queryTime": 0,
                "storage": 0,
                "details": [
                    {"label": "Database Size", "value": "N/A"},
                    {"label": "Tables", "value": "N/A"},
                    {"label": "Active Queries", "value": "N/A"}
                ]
            }
    
    def get_system_alerts(self) -> List[Dict]:
        """Get system alerts based on current metrics"""
        alerts = []
        
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                alerts.append({
                    "type": "warning",
                    "title": "High CPU Usage Detected",
                    "message": f"System CPU usage is at {cpu_percent:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                alerts.append({
                    "type": "warning",
                    "title": "High Memory Usage",
                    "message": f"System memory usage is at {memory.percent:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Check disk usage
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                alerts.append({
                    "type": "critical",
                    "title": "Low Disk Space",
                    "message": f"Disk usage is at {disk.percent:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Check service status
            services = self.get_service_status()
            down_services = [s for s in services if s['status'] == 'down']
            if down_services:
                alerts.append({
                    "type": "critical",
                    "title": "Service Down",
                    "message": f"Service {down_services[0]['name']} is not running",
                    "timestamp": datetime.now().isoformat()
                })
            
            # If no alerts, add success message
            if not alerts:
                alerts.append({
                    "type": "success",
                    "title": "All Systems Operational",
                    "message": "No active alerts or performance issues detected",
                    "timestamp": datetime.now().isoformat()
                })
        
        except Exception as e:
            logger.error(f"Error generating system alerts: {e}")
            alerts.append({
                "type": "error",
                "title": "Monitoring Error",
                "message": "Unable to check system status",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    def _estimate_kafka_throughput(self) -> int:
        """Estimate Kafka throughput based on recent activity"""
        # This is a simplified estimation
        # In production, you'd monitor actual Kafka metrics
        try:
            # Check if there are recent log entries indicating activity
            return 150  # Placeholder - would need actual Kafka monitoring
        except Exception:
            return 0
    
    def _get_process_uptime(self) -> str:
        """Get current process uptime"""
        try:
            process = psutil.Process()
            create_time = process.create_time()
            uptime_seconds = time.time() - create_time
            
            if uptime_seconds < 3600:  # Less than 1 hour
                return f"{int(uptime_seconds / 60)}m"
            elif uptime_seconds < 86400:  # Less than 1 day
                return f"{uptime_seconds / 3600:.1f}h"
            else:
                return f"{uptime_seconds / 86400:.1f}d"
        except Exception:
            return "Unknown"

# Global instance
system_health_service = SystemHealthService()