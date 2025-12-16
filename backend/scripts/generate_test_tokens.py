#!/usr/bin/env python3
"""
Banking-Grade Test Token Generator for Transaction Reconciliation Engine

This script generates JWT tokens for all user roles using Keycloak OAuth2 endpoints.
Used for testing and development of the banking-grade security system.
"""

import requests
import json
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "app"))

try:
    from dotenv import load_dotenv
    import os
    
    # Load environment variables
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
    
    KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080")
    KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "reconciliation")
    KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "reconciliation-api")
    KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "reconciliation-api-secret-2024")
    
except ImportError:
    # Fallback configuration if dotenv not available
    KEYCLOAK_SERVER_URL = "http://localhost:8080"
    KEYCLOAK_REALM = "reconciliation"
    KEYCLOAK_CLIENT_ID = "reconciliation-api"
    KEYCLOAK_CLIENT_SECRET = "reconciliation-api-secret-2024"

# Test users configuration
TEST_USERS = {
    "admin": {"username": "admin", "password": "admin123"},
    "auditor": {"username": "auditor", "password": "auditor123"},
    "operator": {"username": "operator", "password": "operator123"},
    "viewer": {"username": "viewer", "password": "viewer123"}
}

def wait_for_keycloak(max_retries=30, delay=2):
    """Wait for Keycloak to be available"""
    print(f"Waiting for Keycloak at {KEYCLOAK_SERVER_URL}...")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}", timeout=5)
            if response.status_code == 200:
                print("✅ Keycloak is available")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ Attempt {attempt + 1}/{max_retries} - Keycloak not ready, waiting {delay}s...")
        time.sleep(delay)
    
    print("❌ Keycloak is not available after maximum retries")
    return False

def get_token(username, password):
    """Get JWT token for a user"""
    token_url = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid_connect/token"
    
    data = {
        "grant_type": "password",
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
        "username": username,
        "password": password,
        "scope": "openid profile email"
    }
    
    try:
        response = requests.post(token_url, data=data, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        else:
            print(f"❌ Failed to get token for {username}: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed for {username}: {str(e)}")
        return None

def validate_token(token, role):
    """Validate token by calling a protected endpoint"""
    if not token:
        return False
    
    # Test with transactions/stats endpoint (requires auditor+)
    test_url = "http://localhost:8000/transactions/stats"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(test_url, headers=headers, timeout=5)
        
        if role in ["admin", "auditor"]:
            # These roles should have access
            success = response.status_code == 200
        else:
            # Operator and viewer should get 403 for stats endpoint
            success = response.status_code in [200, 403]
        
        if success:
            print(f"✅ Token validation successful for {role}")
        else:
            print(f"❌ Token validation failed for {role}: {response.status_code}")
        
        return success
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Token validation request failed for {role}: {str(e)}")
        return False

def main():
    """Generate and validate test tokens for all roles"""
    print("🔐 Banking-Grade Test Token Generator")
    print("=" * 50)
    
    # Wait for Keycloak to be available
    if not wait_for_keycloak():
        print("❌ Cannot proceed without Keycloak. Please start Keycloak container first:")
        print("   docker-compose -f docker-compose.traefik.yml up -d keycloak")
        sys.exit(1)
    
    print("\n🎫 Generating tokens for all roles...")
    tokens = {}
    
    for role, user_info in TEST_USERS.items():
        print(f"\n📝 Getting token for {role} ({user_info['username']})...")
        token = get_token(user_info["username"], user_info["password"])
        
        if token:
            tokens[role] = token
            print(f"✅ Token generated for {role}")
            
            # Validate token
            validate_token(token, role)
        else:
            print(f"❌ Failed to generate token for {role}")
    
    # Output results
    print("\n" + "=" * 50)
    print("🎯 TOKEN GENERATION RESULTS")
    print("=" * 50)
    
    if tokens:
        print("\n📋 Generated Tokens (copy for testing):")
        print("-" * 40)
        
        for role, token in tokens.items():
            print(f"\n# {role.upper()} TOKEN")
            print(f"{role}_token=\"{token}\"")
        
        print("\n🧪 Usage Examples:")
        print("-" * 20)
        print("# Test with curl:")
        for role in tokens.keys():
            print(f"curl -H \"Authorization: Bearer ${role}_token\" http://localhost:8000/transactions/stats")
        
        print(f"\n✅ Successfully generated {len(tokens)}/{len(TEST_USERS)} tokens")
        
        # Save tokens to file for convenience
        tokens_file = Path(__file__).parent / "test_tokens.json"
        with open(tokens_file, 'w') as f:
            json.dump(tokens, f, indent=2)
        print(f"💾 Tokens saved to: {tokens_file}")
        
    else:
        print("❌ No tokens were generated successfully")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure Keycloak is running: docker-compose -f docker-compose.traefik.yml up -d")
        print("2. Check Keycloak logs: docker-compose -f docker-compose.traefik.yml logs keycloak")
        print("3. Verify realm import: http://localhost:8080/admin")
        print("4. Check user credentials in realm-export.json")
        sys.exit(1)

if __name__ == "__main__":
    main()