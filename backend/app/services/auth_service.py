"""
Banking-Grade Authentication Service
Handles Keycloak integration, JWT validation, and role-based access control
"""
import jwt
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from functools import wraps
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

class BankingAuthService:
    def __init__(self):
        # Keycloak configuration
        self.keycloak_url = "http://localhost:8080"
        self.realm = "banking-reconciliation"
        self.client_id = "reconciliation-backend"
        self.client_secret = "reconciliation-backend-secret"
        
        # JWT configuration
        self.algorithm = "RS256"
        self.public_key = None
        self.public_key_cache_time = None
        self.public_key_cache_duration = 3600  # 1 hour
        
        # Role hierarchy for banking operations
        self.role_hierarchy = {
            'admin': ['admin', 'auditor', 'operator'],
            'auditor': ['auditor', 'operator'],
            'operator': ['operator']
        }
        
        # Permission mapping for banking operations
        self.permissions = {
            'admin': [
                'read:transactions',
                'write:transactions',
                'delete:transactions',
                'read:mismatches',
                'write:mismatches',
                'read:stats',
                'read:redis',
                'write:redis',
                'read:system',
                'write:system',
                'read:audit',
                'write:audit'
            ],
            'auditor': [
                'read:transactions',
                'read:mismatches',
                'read:stats',
                'read:redis',
                'read:system',
                'read:audit'
            ],
            'operator': [
                'read:transactions',
                'read:mismatches',
                'read:stats'
            ]
        }
    
    def get_keycloak_public_key(self) -> str:
        """Get Keycloak public key for JWT validation"""
        try:
            # Check cache
            if (self.public_key and self.public_key_cache_time and 
                datetime.now() - self.public_key_cache_time < timedelta(seconds=self.public_key_cache_duration)):
                return self.public_key
            
            # Fetch from Keycloak
            url = f"{self.keycloak_url}/auth/realms/{self.realm}/protocol/openid_connect/certs"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            keys = response.json()['keys']
            if not keys:
                raise Exception("No keys found in Keycloak response")
            
            # Get the first key (in production, you'd match by kid)
            key_data = keys[0]
            
            # Convert to PEM format
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            import base64
            
            # Decode the key components
            n = base64.urlsafe_b64decode(key_data['n'] + '==')
            e = base64.urlsafe_b64decode(key_data['e'] + '==')
            
            # Create RSA public key
            public_numbers = rsa.RSAPublicNumbers(
                int.from_bytes(e, 'big'),
                int.from_bytes(n, 'big')
            )
            public_key = public_numbers.public_key()
            
            # Convert to PEM
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            self.public_key = pem.decode('utf-8')
            self.public_key_cache_time = datetime.now()
            
            return self.public_key
            
        except Exception as e:
            logger.error(f"Failed to get Keycloak public key: {e}")
            # Fallback to a default key for development
            return self._get_development_key()
    
    def _get_development_key(self) -> str:
        """Development fallback key"""
        return """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4f5wg5l2hKsTeNem/V41
fGnJm6gOdrj8ym3rFkEjWT2btf+FxKlaXzjTBhc0QhOIIaOhqhqk3xvJq8k6cOO4
w5s6+5h1v4rxe5ovQYWSsZhcXcc0ciePiE+hBYkuTnW7uqzABfUT2cbXXPpag+XC
cQqbODlpni43lcE6Gc5QjuiXsHFcOGWn0nxeT4h9QoQQQoQQQoQQQoQQQoQQQoQQ
QoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQ
QoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQQoQQ
QIDAQAB
-----END PUBLIC KEY-----"""
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and extract user information"""
        try:
            # Get public key
            public_key = self.get_keycloak_public_key()
            
            # Decode and validate token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=[self.algorithm],
                audience=self.client_id,
                options={"verify_exp": True, "verify_aud": True}
            )
            
            return {
                'user_id': payload.get('sub'),
                'username': payload.get('preferred_username'),
                'email': payload.get('email'),
                'roles': payload.get('realm_access', {}).get('roles', []),
                'groups': payload.get('groups', []),
                'exp': payload.get('exp'),
                'iat': payload.get('iat'),
                'iss': payload.get('iss')
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token validation failed"
            )
    
    def get_user_permissions(self, roles: List[str]) -> List[str]:
        """Get user permissions based on roles"""
        permissions = set()
        
        for role in roles:
            if role in self.permissions:
                permissions.update(self.permissions[role])
        
        return list(permissions)
    
    def has_permission(self, user_roles: List[str], required_permission: str) -> bool:
        """Check if user has required permission"""
        user_permissions = self.get_user_permissions(user_roles)
        return required_permission in user_permissions
    
    def has_role(self, user_roles: List[str], required_role: str) -> bool:
        """Check if user has required role (with hierarchy)"""
        for user_role in user_roles:
            if user_role in self.role_hierarchy:
                if required_role in self.role_hierarchy[user_role]:
                    return True
        return False
    
    def create_audit_log(self, user_id: str, action: str, resource: str, 
                        details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create audit log entry for banking compliance"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'details': details or {},
            'ip_address': None,  # Will be filled by middleware
            'user_agent': None,  # Will be filled by middleware
            'session_id': None   # Will be filled by middleware
        }
        
        # In production, this would be sent to a secure audit service
        logger.info(f"AUDIT: {json.dumps(audit_entry)}")
        
        return audit_entry

# Global auth service instance
auth_service = BankingAuthService()

# FastAPI security scheme
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """FastAPI dependency to get current authenticated user"""
    token = credentials.credentials
    user_info = auth_service.validate_token(token)
    return user_info

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from kwargs (injected by FastAPI)
            user = None
            for key, value in kwargs.items():
                if isinstance(value, dict) and 'user_id' in value:
                    user = value
                    break
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not auth_service.has_permission(user.get('roles', []), permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role: str):
    """Decorator to require specific role"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from kwargs (injected by FastAPI)
            user = None
            for key, value in kwargs.items():
                if isinstance(value, dict) and 'user_id' in value:
                    user = value
                    break
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not auth_service.has_role(user.get('roles', []), role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{role}' required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Banking-specific permission checks
def require_admin():
    """Require admin role"""
    return require_role('admin')

def require_auditor():
    """Require auditor role or higher"""
    return require_role('auditor')

def require_operator():
    """Require operator role or higher"""
    return require_role('operator')

# Permission-based decorators
def require_read_transactions():
    return require_permission('read:transactions')

def require_write_transactions():
    return require_permission('write:transactions')

def require_read_mismatches():
    return require_permission('read:mismatches')

def require_read_stats():
    return require_permission('read:stats')

def require_read_redis():
    return require_permission('read:redis')

def require_read_system():
    return require_permission('read:system')