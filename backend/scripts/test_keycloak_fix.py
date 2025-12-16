#!/usr/bin/env python3
"""
Test script to verify Keycloak token validation fix
"""

import os
import sys
import requests
import json
from pathlib import Path


def test_keycloak_fix():
    """Test the Keycloak issuer/JWKS fix"""
    
    print("🔧 Testing Keycloak Token Validation Fix")
    print("=" * 50)
    
    # Load environment
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    env_file = project_root / ".env"
    
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    # Parse .env file
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    # Check required variables
    required = [
        'KEYCLOAK_PUBLIC_ISSUER',
        'KEYCLOAK_PUBLIC_JWKS_URL',
        'KEYCLOAK_CLIENT_ID',
        'KEYCLOAK_CLIENT_SECRET'
    ]
    
    print("📋 Checking environment variables:")
    for var in required:
        if var in env_vars:
            print(f"  ✅ {var}: {env_vars[var]}")
        else:
            print(f"  ❌ {var}: Missing")
            return False
    
    # Test token generation
    print("\n🎫 Testing token generation:")
    
    # Use the public issuer URL to construct token endpoint
    public_issuer = env_vars.get('KEYCLOAK_PUBLIC_ISSUER', 'http://localhost:8082/realms/reconciliation')
    keycloak_base = public_issuer.replace('/realms/reconciliation', '')
    token_url = f"{keycloak_base}/realms/reconciliation/protocol/openid-connect/token"
    token_data = {
        'grant_type': 'password',
        'client_id': env_vars['KEYCLOAK_CLIENT_ID'],
        'client_secret': env_vars['KEYCLOAK_CLIENT_SECRET'],
        'username': 'auditor',
        'password': 'auditor123'
    }
    
    try:
        response = requests.post(token_url, data=token_data, timeout=10)
        if response.status_code == 200:
            token_response = response.json()
            access_token = token_response.get('access_token')
            print(f"  ✅ Token generated successfully")
            print(f"  📝 Token length: {len(access_token)} characters")
            
            # Decode token to check issuer (without verification)
            import jwt
            try:
                # Decode without verification to check issuer
                unverified = jwt.decode(access_token, options={"verify_signature": False})
                token_issuer = unverified.get('iss')
                expected_issuer = env_vars['KEYCLOAK_PUBLIC_ISSUER']
                
                print(f"  🔍 Token issuer: {token_issuer}")
                print(f"  🔍 Expected issuer: {expected_issuer}")
                
                if token_issuer == expected_issuer:
                    print(f"  ✅ Issuer matches!")
                else:
                    print(f"  ❌ Issuer mismatch!")
                    return False
                    
            except Exception as e:
                print(f"  ⚠️  Could not decode token: {e}")
            
        else:
            print(f"  ❌ Token generation failed: HTTP {response.status_code}")
            print(f"     Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ Token generation error: {e}")
        return False
    
    # Test API endpoint
    print("\n🌐 Testing API endpoint:")
    
    api_url = "http://localhost:8000/health"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        print(f"  📡 API Response: HTTP {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✅ API accepts token successfully!")
            api_response = response.json()
            print(f"  📊 API Status: {api_response.get('status', 'unknown')}")
            return True
        elif response.status_code == 401:
            print(f"  ❌ API rejected token (401 Unauthorized)")
            try:
                error_detail = response.json()
                print(f"     Error: {error_detail}")
            except:
                print(f"     Raw response: {response.text}")
            return False
        else:
            print(f"  ⚠️  Unexpected API response: {response.status_code}")
            print(f"     Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  ❌ API is not running (connection refused)")
        print(f"     Make sure to start the API first:")
        print(f"     python backend/scripts/start_security_stack.py")
        return False
    except Exception as e:
        print(f"  ❌ API test error: {e}")
        return False


def main():
    """Main function"""
    print("Keycloak Token Validation Fix Test")
    print("This script tests if the issuer/JWKS mismatch is resolved")
    print()
    
    success = test_keycloak_fix()
    
    if success:
        print("\n🎉 SUCCESS: Keycloak token validation is working!")
        print("The issuer/JWKS mismatch has been resolved.")
    else:
        print("\n💥 FAILURE: Token validation is still not working")
        print("Check the errors above and ensure:")
        print("1. Keycloak is running (http://localhost:8080)")
        print("2. API is running (http://localhost:8000)")
        print("3. Environment variables are correct")
        print("4. Docker containers are rebuilt after config changes")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)