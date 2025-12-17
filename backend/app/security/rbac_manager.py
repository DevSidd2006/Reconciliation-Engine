"""
RBAC Manager - Role Hierarchy and Permission Dependencies

This module provides:
- Role hierarchy: admin > auditor > operator > viewer
- Consistent permission mapping
- Clean RBAC dependencies for routers
- Proper role inheritance logic
"""

from fastapi import Depends, HTTPException, status
from security import get_current_user

ROLE_HIERARCHY = {
    "admin": ["auditor", "operator", "viewer"],
    "auditor": ["operator", "viewer"],
    "operator": ["viewer"],
    "viewer": []
}

def has_role(user_roles, required_role):
    """
    Check if user has required role based on hierarchy.
    Example: admin automatically satisfies auditor/operator/viewer.
    
    Args:
        user_roles: List of user's roles
        required_role: Required role string
        
    Returns:
        bool: True if user has required role (direct or inherited)
    """
    for role in user_roles:
        if role == required_role:
            return True
        if role in ROLE_HIERARCHY and required_role in ROLE_HIERARCHY[role]:
            return True
    return False

def require_role(required_role):
    """
    Create a dependency that requires a specific role.
    
    Args:
        required_role: Role required for access
        
    Returns:
        FastAPI dependency function
    """
    def dependency(current_user = Depends(get_current_user)):
        if not current_user or "roles" not in current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        if not has_role(current_user["roles"], required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required role: {required_role}"
            )

        return current_user
    return dependency

# PUBLIC RBAC DEPENDENCIES USED BY ROUTERS
require_admin = require_role("admin")
require_auditor = require_role("auditor")
require_operator = require_role("operator")
require_viewer = require_role("viewer")