"""
Mock Authentication Module
Replaces Keycloak integration for simplified development/testing.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Flexible security scheme that accepts any token (or none if we want to be very loose)
# usage of auto_error=False allows us to handle missing tokens gracefully if needed,
# though here we might just enforce presence for API consistency.
bearer_scheme = HTTPBearer(auto_error=False)

MOCK_ADMIN_USER = {
    "sub": "mock-admin-id",
    "name": "Mock Admin",
    "preferred_username": "admin",
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

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Mock implementation of get_current_user.
    Ignores the actual token content and returns a super-admin user.
    """
    # We still require a header to exist to simulate a realistic API call, 
    # but we don't validate the token signature.
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )

    # Accept any token in mock mode - just check that something was provided
    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )

    # Return the full-access mock user with proper structure
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
