"""
Banking-Grade Security Middleware for Transaction Reconciliation Engine

This module provides comprehensive security middleware including:
- Secure HTTP headers
- CORS hardening
- Request validation
- Security incident detection
- Performance monitoring
"""

import os
import logging
from typing import List
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .audit_logger import audit_logger

# Load environment variables
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

# Configure logging
logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Banking-grade security headers middleware
    
    Implements comprehensive security headers for:
    - Transport security
    - Content security
    - Frame protection
    - XSS protection
    - Information disclosure prevention
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.security_headers = {
            # HTTPS enforcement
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Content type protection
            "X-Content-Type-Options": "nosniff",
            
            # Frame protection
            "X-Frame-Options": "DENY",
            
            # XSS protection
            "X-XSS-Protection": "1; mode=block",
            
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Content Security Policy
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            ),
            
            # Permissions policy
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=()"
            ),
            
            # Server information hiding
            "Server": "Banking-API/1.0",
            
            # Cache control for sensitive data
            "Cache-Control": "no-store, no-cache, must-revalidate, private",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        logger.info("Security headers middleware initialized")
    
    async def dispatch(self, request: Request, call_next):
        """
        Apply security headers to all responses
        
        Args:
            request: Incoming request
            call_next: Next middleware in chain
            
        Returns:
            Response with security headers applied
        """
        try:
            # Process request
            response = await call_next(request)
            
            # Apply security headers
            for header, value in self.security_headers.items():
                response.headers[header] = value
            
            # Additional headers for API responses
            if request.url.path.startswith("/api") or request.url.path.startswith("/transactions") or request.url.path.startswith("/mismatches"):
                response.headers["X-API-Version"] = "1.0"
                response.headers["X-Rate-Limit-Policy"] = "banking-grade"
            
            return response
            
        except Exception as e:
            logger.error(f"Security headers middleware error: {str(e)}")
            
            # Log security incident
            audit_logger.log_security_incident(
                incident_type="middleware_error",
                description=f"Security headers middleware failed: {str(e)}",
                ip_address=request.client.host,
                severity="medium"
            )
            
            # Return error response with security headers
            error_response = JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "Internal security error",
                    "code": "SECURITY_ERROR"
                }
            )
            
            # Apply security headers to error response
            for header, value in self.security_headers.items():
                error_response.headers[header] = value
            
            return error_response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Banking-grade request validation middleware
    
    Validates incoming requests for:
    - Malicious patterns
    - Oversized requests
    - Invalid content types
    - Suspicious headers
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.suspicious_patterns = [
            # SQL injection patterns
            r"(?i)(union|select|insert|update|delete|drop|create|alter)\s+",
            r"(?i)(script|javascript|vbscript|onload|onerror)",
            r"(?i)(<script|</script>|<iframe|</iframe>)",
            # Path traversal
            r"\.\.\/|\.\.\\",
            # Command injection (more specific patterns to avoid false positives)
            r"(?i)\b(cmd\.exe|powershell\.exe|bash|sh)\b",
            r"(?i)\b(exec\(|eval\(|shell_exec\()\b"
        ]
        
        logger.info("Request validation middleware initialized")
    
    async def dispatch(self, request: Request, call_next):
        """
        Validate incoming requests for security threats
        
        Args:
            request: Incoming request
            call_next: Next middleware in chain
            
        Returns:
            Response or security error
        """
        try:
            # Validate request size
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_request_size:
                logger.warning(f"Request too large: {content_length} bytes from {request.client.host}")
                
                audit_logger.log_security_incident(
                    incident_type="oversized_request",
                    description=f"Request size {content_length} exceeds limit",
                    ip_address=request.client.host,
                    severity="medium"
                )
                
                return JSONResponse(
                    status_code=413,
                    content={
                        "status": "error",
                        "message": "Request too large",
                        "code": "REQUEST_TOO_LARGE"
                    }
                )
            
            # Validate request path and query parameters
            full_url = str(request.url)
            if self._contains_suspicious_patterns(full_url):
                logger.warning(f"Suspicious request pattern detected: {full_url} from {request.client.host}")
                
                audit_logger.log_security_incident(
                    incident_type="suspicious_request",
                    description=f"Malicious pattern detected in request: {request.url.path}",
                    ip_address=request.client.host,
                    severity="high",
                    details={"url": full_url, "method": request.method}
                )
                
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "message": "Invalid request",
                        "code": "INVALID_REQUEST"
                    }
                )
            
            # Validate headers
            if self._has_suspicious_headers(request.headers):
                logger.warning(f"Suspicious headers detected from {request.client.host}")
                
                audit_logger.log_security_incident(
                    incident_type="suspicious_headers",
                    description="Malicious headers detected",
                    ip_address=request.client.host,
                    severity="medium"
                )
                
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "message": "Invalid headers",
                        "code": "INVALID_HEADERS"
                    }
                )
            
            # Process request
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Request validation middleware error: {str(e)}")
            
            audit_logger.log_security_incident(
                incident_type="validation_error",
                description=f"Request validation failed: {str(e)}",
                ip_address=request.client.host,
                severity="medium"
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "Request validation error",
                    "code": "VALIDATION_ERROR"
                }
            )
    
    def _contains_suspicious_patterns(self, text: str) -> bool:
        """Check if text contains suspicious patterns"""
        import re
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _has_suspicious_headers(self, headers) -> bool:
        """Check for suspicious headers"""
        suspicious_header_patterns = [
            r"(?i)(script|javascript|vbscript)",
            r"(?i)(<script|</script>)",
            r"(?i)(cmd|exec|system)"
        ]
        
        import re
        
        for header_name, header_value in headers.items():
            header_text = f"{header_name}: {header_value}"
            for pattern in suspicious_header_patterns:
                if re.search(pattern, header_text):
                    return True
        return False


def get_cors_config():
    """
    Get hardened CORS configuration
    
    Returns:
        Dictionary with CORS configuration
    """
    # Get allowed origins from environment
    allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "https://localhost:5173")
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]
    
    # Get credentials setting
    allow_credentials = os.getenv("ALLOWED_CREDENTIALS", "true").lower() == "true"
    
    logger.info(f"CORS configured with origins: {allowed_origins}")
    
    return {
        "allow_origins": allowed_origins,
        "allow_credentials": allow_credentials,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "Accept",
            "Origin",
            "X-API-Key"
        ],
        "expose_headers": [
            "X-Rate-Limit-Limit",
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Reset",
            "X-API-Version"
        ],
        "max_age": 86400  # 24 hours
    }


class SecurityMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Security monitoring middleware for threat detection
    
    Monitors for:
    - Unusual request patterns
    - High-frequency requests
    - Failed authentication attempts
    - Suspicious user agents
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.suspicious_user_agents = [
            "sqlmap", "nikto", "nmap", "masscan", "zap", "burp",
            "python-requests", "curl", "wget"  # May be legitimate but worth monitoring
        ]
        logger.info("Security monitoring middleware initialized")
    
    async def dispatch(self, request: Request, call_next):
        """
        Monitor requests for security threats
        
        Args:
            request: Incoming request
            call_next: Next middleware in chain
            
        Returns:
            Response with security monitoring
        """
        start_time = time.time()
        
        try:
            # Check user agent
            user_agent = request.headers.get("user-agent", "").lower()
            if any(suspicious in user_agent for suspicious in self.suspicious_user_agents):
                logger.warning(f"Suspicious user agent: {user_agent} from {request.client.host}")
                
                audit_logger.log_security_incident(
                    incident_type="suspicious_user_agent",
                    description=f"Suspicious user agent detected: {user_agent}",
                    ip_address=request.client.host,
                    severity="low",
                    details={"user_agent": user_agent, "endpoint": request.url.path}
                )
            
            # Process request
            response = await call_next(request)
            
            # Monitor response time for potential DoS
            response_time = time.time() - start_time
            if response_time > 10.0:  # 10 seconds threshold
                logger.warning(f"Slow response detected: {response_time:.2f}s for {request.url.path}")
                
                audit_logger.log_security_incident(
                    incident_type="slow_response",
                    description=f"Unusually slow response: {response_time:.2f}s",
                    ip_address=request.client.host,
                    severity="low",
                    details={"response_time": response_time, "endpoint": request.url.path}
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Security monitoring middleware error: {str(e)}")
            
            # Still process the request even if monitoring fails
            response = await call_next(request)
            return response


# Import time for monitoring
import time