#!/usr/bin/env python3
"""
Debug Token Script - Decode JWT tokens to check issuer and claims
"""

import json
import jwt
import sys
from pathlib import Path

def decode_token_without_verification(token: str):
    """Decode JWT token without signature verification to inspect claims"""
    try:
        # Decode without verification to see the payload
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None

def main():
    # Load tokens
    token_file = Path(__file__).parent.parent / "tmp" / "tokens.json"
    if not token_file.exists():
        print("❌ Token file not found")
        return
    
    with open(token_file, 'r') as f:
        data = json.load(f)
        tokens = data.get("tokens", {})
    
    print("🔍 Token Analysis")
    print("=" * 50)
    
    for token_name, token_data in tokens.items():
        print(f"\n{token_name}:")
        access_token = token_data.get("access_token")
        if access_token:
            decoded = decode_token_without_verification(access_token)
            if decoded:
                print(f"  Issuer: {decoded.get('iss')}")
                print(f"  Subject: {decoded.get('sub')}")
                print(f"  Username: {decoded.get('preferred_username')}")
                print(f"  Roles: {decoded.get('roles', [])}")
                print(f"  Audience: {decoded.get('aud')}")
                print(f"  Expires: {decoded.get('exp')}")
            else:
                print("  ❌ Failed to decode token")
        else:
            print("  ❌ No access token found")

if __name__ == "__main__":
    main()