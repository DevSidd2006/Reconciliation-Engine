import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any
from datetime import datetime, timedelta
import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, status

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)

class KeycloakConfig:

    def __init__(self):

        # Internal Docker URL (for container-to-container communication)
        self.internal_url = os.getenv("KEYCLOAK_SERVER_URL", "http://keycloak:8080")
        
        # Public URLs (for token validation - must match token issuer)
        self.public_issuer = os.getenv("KEYCLOAK_PUBLIC_ISSUER")
        self.public_jwks_url = os.getenv("KEYCLOAK_PUBLIC_JWKS_URL")

        self.realm = os.getenv("KEYCLOAK_REALM", "reconciliation")
        self.client_id = os.getenv("KEYCLOAK_CLIENT_ID")
        self.client_secret = os.getenv("KEYCLOAK_CLIENT_SECRET")
        self.algorithm = os.getenv("JWT_ALGORITHM", "RS256")
        self.audience = os.getenv("JWT_AUDIENCE", self.client_id)

        # Use public JWKS URL for token validation (not internal Docker URL)
        self.jwks_url = self.public_jwks_url or f"http://localhost:8080/realms/{self.realm}/protocol/openid-connect/certs"
        
        # Fallback public issuer if not set
        if not self.public_issuer:
            self.public_issuer = f"http://localhost:8080/realms/{self.realm}"

        try:
            self.jwks_client = PyJWKClient(self.jwks_url)
            logger.info(f"✅ JWKS Client initialized at: {self.jwks_url}")
            logger.info(f"✅ Using public issuer: {self.public_issuer}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize JWKS: {e}")
            self.jwks_client = None

    def validate_token(self, token: str) -> Dict[str, Any]:

        try:
            if not self.jwks_client:
                self.jwks_client = PyJWKClient(self.jwks_url)

            signing_key = self.jwks_client.get_signing_key_from_jwt(token)

            # Validate using PUBLIC issuer with proper configuration
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.public_issuer,
                options={"verify_aud": False}  # Skip audience validation since tokens don't have aud claim
            )

            self._validate_claims(payload)
            return payload

        except jwt.InvalidTokenError as e:
            logger.error(f"Token validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "status": "error",
                    "message": "Token validation error",
                    "code": "INVALID_TOKEN",
                    "details": str(e)
                }
            )
        except Exception as e:
            logger.error(f"Unexpected token validation error: {e}")
            # Log more details for debugging
            logger.error(f"Token validation system error details: {type(e).__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,  # Changed from 500 to 401
                detail={
                    "status": "error",
                    "message": "Token validation system error",
                    "code": "VALIDATION_SYSTEM_ERROR",
                    "info": str(e)  # Add error details for debugging
                }
            )

    def _validate_claims(self, payload: Dict[str, Any]):
        required = ["sub", "iat", "exp", "preferred_username"]
        for claim in required:
            if claim not in payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Missing claim: {claim}"
                )

        issued_at = datetime.fromtimestamp(payload["iat"])
        if datetime.now() - issued_at > timedelta(hours=24):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token too old"
            )

    def extract_user_info(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract user information from validated JWT payload
        
        Args:
            payload: Validated JWT payload
            
        Returns:
            Dictionary containing user information for RBAC
        """
        # Extract roles using Option B: resource_access.<client>.roles
        roles = payload.get("resource_access", {}) \
                      .get(self.client_id, {}) \
                      .get("roles", [])
        
        # Fallback to top-level roles claim if resource_access is empty
        if not roles and "roles" in payload:
            roles = payload["roles"]
        
        return {
            "user_id": payload.get("sub"),
            "username": payload.get("preferred_username"),
            "email": payload.get("email"),
            "name": payload.get("name"),
            "given_name": payload.get("given_name"),
            "family_name": payload.get("family_name"),
            "roles": roles,  # Using Option B role extraction
            "realm_access": payload.get("realm_access", {}),
            "resource_access": payload.get("resource_access", {}),
            "session_id": payload.get("sid"),
            "issued_at": payload.get("iat"),
            "expires_at": payload.get("exp")
        }


keycloak_config = KeycloakConfig()
