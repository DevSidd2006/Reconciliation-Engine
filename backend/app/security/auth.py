"""
Authentication Module - Token Extractor, Validation, and User Injection

This module provides:
- JWT token extraction from Authorization header
- Token validation using Keycloak
- User information extraction with roles
- Fixes ALL 500 validation errors
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from security.keycloak_config import keycloak_config

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Extract, validate JWT and return user object with roles.
    
    This function:
    1. Extracts JWT token from Authorization header
    2. Validates token using Keycloak
    3. Extracts user information and roles
    4. Returns complete user object for RBAC
    
    Returns:
        dict: User object with roles, username, user_id, etc.
        
    Raises:
        HTTPException: 401 if token missing or invalid
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )

    token = credentials.credentials
    payload = keycloak_config.validate_token(token)
    user = keycloak_config.extract_user_info(payload)

    # ---------------------------
    # ROLE EXTRACTION USING OPTION B
    # resource_access.reconciliation-api.roles
    # ---------------------------
    client_id = keycloak_config.client_id
    
    # Extract roles from resource_access.<client>.roles
    roles = payload.get("resource_access", {}) \
                  .get(client_id, {}) \
                  .get("roles", [])
    
    # Fallback to top-level roles claim if resource_access is empty
    if not roles and "roles" in payload:
        roles = payload["roles"]
    
    user["roles"] = roles

    return user