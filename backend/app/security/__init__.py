"""
Banking-Grade Security Package for Transaction Reconciliation Engine

This package provides comprehensive security features including:
- Keycloak OAuth2/OpenID Connect integration
- Role-Based Access Control (RBAC)
- Comprehensive audit logging
- Security middleware and headers
- Threat detection and monitoring
"""

from .auth import get_current_user
from .rbac_manager import require_admin, require_auditor, require_operator, require_viewer, has_role
from .audit_logger import audit_logger, BankingAuditLogger, AuditLog
from .security_middleware import (
    SecurityHeadersMiddleware, RequestValidationMiddleware, 
    SecurityMonitoringMiddleware, get_cors_config
)

__all__ = [
    # Authentication (Mock only)
    'get_current_user',
    
    # RBAC System
    'require_admin',
    'require_auditor',
    'require_operator',
    'require_viewer',
    'has_role',
    
    # Audit Logging
    'audit_logger',
    'BankingAuditLogger',
    'AuditLog',
    
    # Security Middleware
    'SecurityHeadersMiddleware',
    'RequestValidationMiddleware',
    'SecurityMonitoringMiddleware',
    'get_cors_config',
]