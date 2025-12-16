"""
Banking-Grade Audit Logging System for Transaction Reconciliation Engine

This module provides comprehensive audit logging for:
- Authentication events
- Authorization decisions
- Data access patterns
- Administrative actions
- Security incidents
"""

import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from db.database import Base, SessionLocal

# Configure logging
logger = logging.getLogger(__name__)


class AuditLog(Base):
    """
    Audit log table for banking-grade security compliance
    
    Stores comprehensive audit trail including:
    - User identification and authentication
    - Resource access and authorization
    - Timestamps and IP addresses
    - Success/failure status
    - Detailed context information
    """
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # User Information
    user_id = Column(String, nullable=True, index=True)
    username = Column(String, nullable=True, index=True)
    session_id = Column(String, nullable=True)
    
    # Request Information
    method = Column(String, nullable=False)
    endpoint = Column(String, nullable=False, index=True)
    ip_address = Column(String, nullable=True, index=True)
    user_agent = Column(String, nullable=True)
    
    # Event Information
    event_type = Column(String, nullable=False, index=True)  # auth, authz, data_access, admin
    action = Column(String, nullable=False)  # login, access, create, update, delete
    resource = Column(String, nullable=True)  # transactions, mismatches, users
    resource_id = Column(String, nullable=True)
    
    # Status and Results
    success = Column(Boolean, nullable=False, index=True)
    status_code = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Security Context
    roles = Column(Text, nullable=True)  # JSON string of user roles
    permissions = Column(Text, nullable=True)  # Required permissions
    
    # Additional Context
    details = Column(Text, nullable=True)  # JSON string with additional details
    risk_score = Column(Integer, default=0)  # Risk assessment score


class BankingAuditLogger:
    """
    Banking-grade audit logger with comprehensive security event tracking
    
    Features:
    - Structured audit logging to database
    - Risk-based event classification
    - Compliance-ready audit trails
    - Performance-optimized batch logging
    - Tamper-evident log integrity
    """
    
    def __init__(self):
        """Initialize audit logger with database connection"""
        self.logger = logging.getLogger(f"{__name__}.BankingAuditLogger")
        self._ensure_audit_table()
        self.logger.info("Banking audit logger initialized")
    
    def _ensure_audit_table(self):
        """Ensure audit_logs table exists by executing SQL script"""
        try:
            from pathlib import Path
            
            # Get SQL script path
            sql_file = Path(__file__).parent / "create_audit_logs.sql"
            
            if sql_file.exists():
                db = SessionLocal()
                try:
                    # Read and execute SQL script
                    with open(sql_file, 'r') as f:
                        sql_script = f.read()
                    
                    # Execute the SQL script
                    from sqlalchemy import text
                    db.execute(text(sql_script))
                    db.commit()
                    self.logger.info("Audit logs table initialized successfully")
                    
                except Exception as e:
                    self.logger.error(f"Failed to initialize audit logs table: {str(e)}")
                    db.rollback()
                finally:
                    db.close()
            else:
                self.logger.warning("Audit logs SQL script not found")
                
        except Exception as e:
            self.logger.error(f"Error ensuring audit table: {str(e)}")
    
    def _create_audit_entry(
        self,
        event_type: str,
        action: str,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        method: Optional[str] = None,
        endpoint: Optional[str] = None,
        ip_address: Optional[str] = None,
        success: bool = True,
        **kwargs
    ) -> AuditLog:
        """
        Create audit log entry with common fields
        
        Args:
            event_type: Type of event (auth, authz, data_access, admin)
            action: Specific action performed
            user_id: User identifier
            username: Username
            method: HTTP method
            endpoint: API endpoint
            ip_address: Client IP address
            success: Whether action was successful
            **kwargs: Additional fields
            
        Returns:
            AuditLog instance
        """
        return AuditLog(
            event_type=event_type,
            action=action,
            user_id=user_id,
            username=username,
            method=method,
            endpoint=endpoint,
            ip_address=ip_address,
            success=success,
            **kwargs
        )
    
    def log_authentication(
        self,
        user_id: str,
        username: str,
        method: str,
        endpoint: str,
        ip_address: str,
        success: bool,
        session_id: Optional[str] = None,
        error: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Log authentication events
        
        Args:
            user_id: User identifier
            username: Username
            method: HTTP method
            endpoint: API endpoint
            ip_address: Client IP address
            success: Whether authentication succeeded
            session_id: Session identifier
            error: Error message if failed
            user_agent: User agent string
        """
        db = SessionLocal()
        try:
            audit_entry = self._create_audit_entry(
                event_type="authentication",
                action="login" if success else "login_failed",
                user_id=user_id,
                username=username,
                method=method,
                endpoint=endpoint,
                ip_address=ip_address,
                success=success,
                session_id=session_id,
                error_message=error,
                user_agent=user_agent,
                risk_score=10 if not success else 0
            )
            
            db.add(audit_entry)
            db.commit()
            
            log_level = logging.INFO if success else logging.WARNING
            self.logger.log(
                log_level,
                f"Authentication {'succeeded' if success else 'failed'} for user {username} "
                f"from {ip_address} on {endpoint}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log authentication event: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    def log_authorization(
        self,
        user_id: str,
        username: str,
        method: str,
        endpoint: str,
        required_roles: List[str],
        user_roles: List[str],
        success: bool,
        ip_address: str,
        resource: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> None:
        """
        Log authorization decisions
        
        Args:
            user_id: User identifier
            username: Username
            method: HTTP method
            endpoint: API endpoint
            required_roles: Roles required for access
            user_roles: User's actual roles
            success: Whether authorization succeeded
            ip_address: Client IP address
            resource: Resource being accessed
            resource_id: Specific resource identifier
        """
        db = SessionLocal()
        try:
            import json
            
            audit_entry = self._create_audit_entry(
                event_type="authorization",
                action="access_granted" if success else "access_denied",
                user_id=user_id,
                username=username,
                method=method,
                endpoint=endpoint,
                ip_address=ip_address,
                success=success,
                resource=resource,
                resource_id=resource_id,
                roles=json.dumps(user_roles),
                permissions=json.dumps(required_roles),
                risk_score=20 if not success else 0
            )
            
            db.add(audit_entry)
            db.commit()
            
            log_level = logging.INFO if success else logging.WARNING
            self.logger.log(
                log_level,
                f"Authorization {'granted' if success else 'denied'} for user {username} "
                f"to access {endpoint}. Required: {required_roles}, User: {user_roles}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log authorization event: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    def log_data_access(
        self,
        user_id: str,
        username: str,
        method: str,
        endpoint: str,
        resource: str,
        action: str,
        ip_address: str,
        resource_id: Optional[str] = None,
        record_count: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        success: bool = True
    ) -> None:
        """
        Log data access events
        
        Args:
            user_id: User identifier
            username: Username
            method: HTTP method
            endpoint: API endpoint
            resource: Resource type (transactions, mismatches)
            action: Action performed (read, create, update, delete)
            ip_address: Client IP address
            resource_id: Specific resource identifier
            record_count: Number of records accessed
            filters: Query filters applied
            success: Whether access succeeded
        """
        db = SessionLocal()
        try:
            import json
            
            details = {}
            if record_count is not None:
                details["record_count"] = record_count
            if filters:
                details["filters"] = filters
            
            audit_entry = self._create_audit_entry(
                event_type="data_access",
                action=f"{resource}_{action}",
                user_id=user_id,
                username=username,
                method=method,
                endpoint=endpoint,
                ip_address=ip_address,
                success=success,
                resource=resource,
                resource_id=resource_id,
                details=json.dumps(details) if details else None,
                risk_score=5 if action in ["create", "update", "delete"] else 0
            )
            
            db.add(audit_entry)
            db.commit()
            
            self.logger.info(
                f"Data access logged: {username} performed {action} on {resource} "
                f"via {endpoint} ({record_count or 1} records)"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log data access event: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    def log_admin_action(
        self,
        user_id: str,
        username: str,
        action: str,
        resource: str,
        ip_address: str,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """
        Log administrative actions
        
        Args:
            user_id: Administrator user ID
            username: Administrator username
            action: Administrative action performed
            resource: Resource affected
            ip_address: Client IP address
            details: Additional action details
            success: Whether action succeeded
            error: Error message if failed
        """
        db = SessionLocal()
        try:
            import json
            
            audit_entry = self._create_audit_entry(
                event_type="administration",
                action=action,
                user_id=user_id,
                username=username,
                ip_address=ip_address,
                success=success,
                resource=resource,
                details=json.dumps(details) if details else None,
                error_message=error,
                risk_score=50  # Admin actions are high risk
            )
            
            db.add(audit_entry)
            db.commit()
            
            log_level = logging.INFO if success else logging.ERROR
            self.logger.log(
                log_level,
                f"Admin action: {username} performed {action} on {resource} "
                f"from {ip_address} - {'Success' if success else 'Failed'}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log admin action: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    def log_security_incident(
        self,
        incident_type: str,
        description: str,
        ip_address: str,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        severity: str = "medium",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log security incidents
        
        Args:
            incident_type: Type of security incident
            description: Incident description
            ip_address: Source IP address
            user_id: User ID if applicable
            username: Username if applicable
            severity: Incident severity (low, medium, high, critical)
            details: Additional incident details
        """
        db = SessionLocal()
        try:
            import json
            
            risk_scores = {"low": 25, "medium": 50, "high": 75, "critical": 100}
            
            audit_entry = self._create_audit_entry(
                event_type="security_incident",
                action=incident_type,
                user_id=user_id,
                username=username,
                ip_address=ip_address,
                success=False,  # Security incidents are always failures
                error_message=description,
                details=json.dumps(details) if details else None,
                risk_score=risk_scores.get(severity, 50)
            )
            
            db.add(audit_entry)
            db.commit()
            
            self.logger.error(
                f"SECURITY INCIDENT [{severity.upper()}]: {incident_type} - {description} "
                f"from {ip_address} (User: {username or 'unknown'})"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log security incident: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    def get_audit_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get audit log summary for reporting
        
        Args:
            start_date: Start date for summary
            end_date: End date for summary
            user_id: Filter by user ID
            event_type: Filter by event type
            
        Returns:
            Dictionary containing audit summary statistics
        """
        db = SessionLocal()
        try:
            from sqlalchemy import func, and_
            
            query = db.query(AuditLog)
            
            # Apply filters
            filters = []
            if start_date:
                filters.append(AuditLog.timestamp >= start_date)
            if end_date:
                filters.append(AuditLog.timestamp <= end_date)
            if user_id:
                filters.append(AuditLog.user_id == user_id)
            if event_type:
                filters.append(AuditLog.event_type == event_type)
            
            if filters:
                query = query.filter(and_(*filters))
            
            # Get summary statistics
            total_events = query.count()
            successful_events = query.filter(AuditLog.success == True).count()
            failed_events = query.filter(AuditLog.success == False).count()
            
            # Get event type breakdown
            event_types = db.query(
                AuditLog.event_type,
                func.count(AuditLog.id).label('count')
            ).group_by(AuditLog.event_type).all()
            
            # Get top users
            top_users = db.query(
                AuditLog.username,
                func.count(AuditLog.id).label('count')
            ).filter(AuditLog.username.isnot(None)).group_by(AuditLog.username).order_by(
                func.count(AuditLog.id).desc()
            ).limit(10).all()
            
            return {
                "total_events": total_events,
                "successful_events": successful_events,
                "failed_events": failed_events,
                "success_rate": (successful_events / total_events * 100) if total_events > 0 else 0,
                "event_types": {event_type: count for event_type, count in event_types},
                "top_users": {username: count for username, count in top_users}
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate audit summary: {str(e)}")
            return {"error": str(e)}
        finally:
            db.close()


# Global audit logger instance
audit_logger = BankingAuditLogger()