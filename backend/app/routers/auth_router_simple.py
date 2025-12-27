"""
Simple Authentication Router for Development
Bypasses Keycloak for easy testing
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any, List
import jwt
from datetime import datetime, timedelta

router = APIRouter()
security = HTTPBearer()

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

# Demo users for development
DEMO_USERS = {
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

JWT_SECRET = 'dev-secret-key-banking-reconciliation'

def create_token(user_data: dict) -> str:
    """Create JWT token for user"""
    payload = {
        'user_id': user_data['user_id'],
        'username': user_data['username'],
        'roles': user_data['roles'],
        'permissions': user_data['permissions'],
        'exp': datetime.utcnow() + timedelta(hours=8),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return user data"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login", response_model=TokenResponse)
def login(login_request: LoginRequest):
    """
    🔐 Simple Development Login
    
    Username/Password combinations:
    - admin/admin123 (Full access)
    - auditor/auditor123 (Read-only)
    - operator/operator123 (Limited access)
    """
    # Validate credentials
    if login_request.username not in DEMO_USERS:
        raise HTTPException(status_code=401, detail="Invalid username")
    
    user_data = DEMO_USERS[login_request.username]
    if login_request.password != user_data['password']:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Create token
    token = create_token(user_data)
    
    return TokenResponse(
        access_token=token,
        refresh_token=token,  # Same for simplicity
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

@router.get("/me", response_model=UserInfo)
def get_current_user(user_data: dict = Depends(verify_token)):
    """Get current user information"""
    username = user_data['username']
    user_info = DEMO_USERS[username]
    
    return UserInfo(
        user_id=user_data['user_id'],
        username=user_data['username'],
        email=user_info['email'],
        roles=user_data['roles'],
        groups=user_info['groups'],
        permissions=user_data['permissions']
    )

@router.post("/logout")
def logout():
    """Simple logout (client should remove token)"""
    return {"message": "Logged out successfully"}

@router.get("/health")
def auth_health():
    """Authentication service health check"""
    return {
        "status": "healthy",
        "mode": "development",
        "available_users": list(DEMO_USERS.keys())
    }