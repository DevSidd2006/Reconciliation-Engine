#!/usr/bin/env python3
"""
Test Token Validation - Debug token validation issues
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "app"))

from security.keycloak_config import keycloak_config

def test_token_validation():
    """Test token validation with actual tokens"""
    
    # Load tokens
    token_file = Path(__file__).parent.parent / "tmp" / "tokens.json"
    if not token_file.exists():
        print("❌ Token file not found")
        return
    
    with open(token_file, 'r') as f:
        data = json.load(f)
        tokens = data.get("tokens", {})
    
    print("🔍 Testing Token Validation")
    print("=" * 50)
    print(f"Keycloak Config:")
    print(f"  Public Issuer: {keycloak_config.public_issuer}")
    print(f"  JWKS URL: {keycloak_config.jwks_url}")
    print(f"  Audience: {keycloak_config.audience}")
    print(f"  Algorithm: {keycloak_config.algorithm}")
    print()
    
    for token_name, token_data in tokens.items():
        print(f"Testing {token_name}:")
        access_token = token_data.get("access_token")
        if access_token:
            try:
                # Test token validation
                payload = keycloak_config.validate_token(access_token)
                print(f"  ✅ Token validation successful")
                print(f"     Username: {payload.get('preferred_username')}")
                print(f"     Roles: {payload.get('roles', [])}")
                
                # Test user info extraction
                user_info = keycloak_config.extract_user_info(payload)
                print(f"     User ID: {user_info.get('user_id')}")
                print(f"     Email: {user_info.get('email')}")
                
            except Exception as e:
                print(f"  ❌ Token validation failed: {e}")
                print(f"     Error type: {type(e).__name__}")
        else:
            print("  ❌ No access token found")
        print()

if __name__ == "__main__":
    test_token_validation()