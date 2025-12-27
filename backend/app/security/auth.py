"""
Authentication Module - Simplified Mock Authentication

This module provides:
- Mock JWT token validation for development
- User information with predefined roles
- Simplified authentication for testing
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Mock authentication that accepts any token and returns admin user.
    
    Returns:
        dict: User object with roles, username, user_id, etc.
        
    Raises:
        HTTPException: 401 if token missing
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )

    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )

    # Return mock admin user with all roles
    return {
        "user_id": "mock-admin-id",
        "username": "admin", 
        "name": "Mock Admin",
        "email": "admin@example.com",
        "roles": ["admin", "operator", "auditor", "viewer"],
        "realm_access": {
            "roles": ["admin", "operator", "auditor", "viewer"]
        },
        "resource_access": {
            "reconciliation-api": {
                "roles": ["admin", "operator", "auditor", "viewer"]
            }
        }
    }