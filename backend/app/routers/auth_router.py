"""
Banking Authentication Router
Handles login, logout, token refresh, and user management
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Dict, Any, List
import requests
import json

from services.auth_service import auth_service, get_current_user

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: Dict[str, Any]

class UserInfo(BaseModel):
    user_id: str
    username: str
    email: str
    roles: List[str]
    groups: List[str]
    permissions: List[str]

@router.post("/login", response_model=TokenResponse)
def login(login_request: LoginRequest):
    """
    🔐 Banking User Authentication
    
    Development mode: Simple authentication bypass
    """
    try:
        # Development mode: Simple user validation
        demo_users = {
            'admin': {
                'password': 'admin123',
                'user_id': 'admin-user',
                'username': 'admin',
                'email': 'admin@banking.local',
                'roles': ['admin'],
                'groups': ['Banking Administrators'],
                'permissions': ['read:transactions', 'write:transactions', 'read:mismatches', 'write:mismatches', 'read:stats', 'write:system']
            },
            'auditor': {
                'password': 'auditor123',
                'user_id': 'auditor-user',
                'username': 'auditor',
                'email': 'auditor@banking.local',
                'roles': ['auditor'],
                'groups': ['Banking Auditors'],
                'permissions': ['read:transactions', 'read:mismatches', 'read:stats']
            },
            'operator': {
                'password': 'operator123',
                'user_id': 'operator-user',
                'username': 'operator',
                'email': 'operator@banking.local',
                'roles': ['operator'],
                'groups': ['Banking Operators'],
                'permissions': ['read:transactions', 'read:mismatches']
            }
        }
        
        # Validate user credentials
        if login_request.username not in demo_users:
            raise HTTPException(status_code=401, detail="Invalid username")
        
        user_data = demo_users[login_request.username]
        if login_request.password != user_data['password']:
            raise HTTPException(status_code=401, detail="Invalid password")
        
        # Create simple JWT token (development only)
        import jwt
        from datetime import datetime, timedelta
        
        payload = {
            'user_id': user_data['user_id'],
            'username': user_data['username'],
            'roles': user_data['roles'],
            'permissions': user_data['permissions'],
            'exp': datetime.utcnow() + timedelta(hours=8),
            'iat': datetime.utcnow()
        }
        
        # Simple secret for development (use proper key in production)
        token = jwt.encode(payload, 'dev-secret-key', algorithm='HS256')
        
        return TokenResponse(
            access_token=token,
            refresh_token=token,  # Same token for simplicity in dev
            expires_in=28800,  # 8 hours
            user_info={
                'user_id': user_data['user_id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'roles': user_data['roles'],
                'groups': user_data['groups'],
                'permissions': user_data['permissions']
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Authentication service error")
            action='LOGIN',
            resource='authentication',
            details={'username': login_request.username}
        )
        
        return TokenResponse(
            access_token=token_response['access_token'],
            refresh_token=token_response['refresh_token'],
            expires_in=token_response['expires_in'],
            user_info={
                'user_id': user_info['user_id'],
                'username': user_info['username'],
                'email': user_info['email'],
                'roles': user_info['roles'],
                'groups': user_info['groups'],
                'permissions': permissions
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

@router.post("/refresh")
def refresh_token(refresh_token: str):
    """
    🔄 Refresh JWT Token
    
    Refreshes access token using refresh token
    """
    try:
        token_url = f"{auth_service.keycloak_url}/auth/realms/{auth_service.realm}/protocol/openid_connect/token"
        
        token_data = {
            'grant_type': 'refresh_token',
            'client_id': 'reconciliation-frontend',
            'refresh_token': refresh_token
        }
        
        response = requests.post(
            token_url,
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        token_response = response.json()
        
        # Validate new access token
        user_info = auth_service.validate_token(token_response['access_token'])
        permissions = auth_service.get_user_permissions(user_info.get('roles', []))
        
        return TokenResponse(
            access_token=token_response['access_token'],
            refresh_token=token_response.get('refresh_token', refresh_token),
            expires_in=token_response['expires_in'],
            user_info={
                'user_id': user_info['user_id'],
                'username': user_info['username'],
                'email': user_info['email'],
                'roles': user_info['roles'],
                'groups': user_info['groups'],
                'permissions': permissions
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.post("/logout")
def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    🚪 User Logout
    
    Logs out user and invalidates tokens
    """
    try:
        # Create audit log
        auth_service.create_audit_log(
            user_id=current_user['user_id'],
            action='LOGOUT',
            resource='authentication',
            details={'username': current_user['username']}
        )
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )

@router.get("/me", response_model=UserInfo)
def get_current_user_info(authorization: str = Depends(HTTPBearer())):
    """
    👤 Get Current User Information
    
    Development mode: Simple JWT validation
    """
    try:
        import jwt
        
        # Extract token from authorization header
        token = authorization.credentials
        
        # Decode JWT token (development mode)
        payload = jwt.decode(token, 'dev-secret-key', algorithms=['HS256'])
        
        return UserInfo(
            user_id=payload['user_id'],
            username=payload['username'],
            email=f"{payload['username']}@banking.local",
            roles=payload['roles'],
            groups=[f"Banking {payload['roles'][0].title()}s"],
            permissions=payload['permissions']
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.get("/permissions")
def get_user_permissions(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    🔑 Get User Permissions
    
    Returns detailed permission information for current user
    """
    permissions = auth_service.get_user_permissions(current_user.get('roles', []))
    
    return {
        'user_id': current_user['user_id'],
        'username': current_user['username'],
        'roles': current_user['roles'],
        'permissions': permissions,
        'role_hierarchy': {
            role: auth_service.role_hierarchy.get(role, [])
            for role in current_user['roles']
        }
    }

@router.get("/roles")
def get_available_roles():
    """
    📋 Get Available Roles
    
    Returns all available roles and their permissions (public endpoint)
    """
    return {
        'roles': {
            'admin': {
                'description': 'Banking Administrator - Full system access',
                'permissions': auth_service.permissions['admin']
            },
            'auditor': {
                'description': 'Banking Auditor - Read-only access to all data',
                'permissions': auth_service.permissions['auditor']
            },
            'operator': {
                'description': 'Banking Operator - Limited operational access',
                'permissions': auth_service.permissions['operator']
            }
        },
        'hierarchy': auth_service.role_hierarchy
    }

@router.get("/health")
def auth_health_check():
    """
    ❤️ Authentication Service Health Check
    
    Checks Keycloak connectivity and service status
    """
    try:
        # Test Keycloak connectivity
        health_url = f"{auth_service.keycloak_url}/auth/realms/{auth_service.realm}"
        response = requests.get(health_url, timeout=5)
        
        keycloak_status = "healthy" if response.status_code == 200 else "unhealthy"
        
        return {
            'status': 'healthy',
            'keycloak': {
                'status': keycloak_status,
                'url': auth_service.keycloak_url,
                'realm': auth_service.realm
            },
            'jwt_validation': 'enabled',
            'role_based_access': 'enabled',
            'audit_logging': 'enabled'
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'keycloak': {
                'status': 'unreachable',
                'url': auth_service.keycloak_url,
                'realm': auth_service.realm
            }
        }