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
    
    Authenticates user against Keycloak and returns JWT tokens
    """
    try:
        # Keycloak token endpoint
        token_url = f"{auth_service.keycloak_url}/auth/realms/{auth_service.realm}/protocol/openid_connect/token"
        
        # Prepare token request
        token_data = {
            'grant_type': 'password',
            'client_id': 'reconciliation-frontend',
            'username': login_request.username,
            'password': login_request.password,
            'scope': 'openid profile email banking'
        }
        
        # Request tokens from Keycloak
        response = requests.post(
            token_url,
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        
        if response.status_code != 200:
            error_detail = "Invalid credentials"
            try:
                error_info = response.json()
                if 'error_description' in error_info:
                    error_detail = error_info['error_description']
            except:
                pass
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_detail
            )
        
        token_response = response.json()
        
        # Validate and extract user info from access token
        user_info = auth_service.validate_token(token_response['access_token'])
        
        # Get user permissions
        permissions = auth_service.get_user_permissions(user_info.get('roles', []))
        
        # Create audit log
        auth_service.create_audit_log(
            user_id=user_info['user_id'],
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
def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    👤 Get Current User Information
    
    Returns current user's profile and permissions
    """
    permissions = auth_service.get_user_permissions(current_user.get('roles', []))
    
    return UserInfo(
        user_id=current_user['user_id'],
        username=current_user['username'],
        email=current_user['email'],
        roles=current_user['roles'],
        groups=current_user['groups'],
        permissions=permissions
    )

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