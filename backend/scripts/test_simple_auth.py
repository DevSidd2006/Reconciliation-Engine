#!/usr/bin/env python3
"""
Simple Authentication Test
"""

import requests
import json
from pathlib import Path

def test_simple_auth():
    """Test simple authentication scenarios"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Simple Authentication Test")
    print("=" * 50)
    
    # Test 1: Anonymous access to protected endpoint
    print("Test 1: Anonymous access to /mismatches")
    try:
        response = requests.get(f"{base_url}/mismatches", timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  ❌ FAIL: Should require authentication")
        elif response.status_code == 401:
            print("  ✅ PASS: Correctly requires authentication")
        else:
            print(f"  ⚠️  Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 2: Anonymous access to /transactions
    print("\nTest 2: Anonymous access to /transactions")
    try:
        response = requests.get(f"{base_url}/transactions", timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  ❌ FAIL: Should require authentication")
        elif response.status_code == 401:
            print("  ✅ PASS: Correctly requires authentication")
        else:
            print(f"  ⚠️  Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 3: Load token and test authenticated access
    print("\nTest 3: Authenticated access with valid token")
    token_file = Path(__file__).parent.parent / "tmp" / "tokens.json"
    if token_file.exists():
        with open(token_file, 'r') as f:
            data = json.load(f)
            admin_token = data.get("tokens", {}).get("TOKEN_ADMIN", {}).get("access_token")
            
        if admin_token:
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            # Test transactions with token
            try:
                response = requests.get(f"{base_url}/transactions/stats", headers=headers, timeout=10)
                print(f"  /transactions/stats with admin token: {response.status_code}")
                if response.status_code == 200:
                    print("  ✅ PASS: Admin can access transactions")
                else:
                    print(f"  ❌ FAIL: Expected 200, got {response.status_code}")
                    if response.status_code == 401:
                        print("    Token validation failed")
                    try:
                        error_detail = response.json()
                        print(f"    Error: {error_detail}")
                    except:
                        pass
            except Exception as e:
                print(f"  ❌ Error: {e}")
            
            # Test mismatches with token
            try:
                response = requests.get(f"{base_url}/mismatches", headers=headers, timeout=10)
                print(f"  /mismatches with admin token: {response.status_code}")
                if response.status_code == 200:
                    print("  ✅ PASS: Admin can access mismatches")
                else:
                    print(f"  ❌ FAIL: Expected 200, got {response.status_code}")
                    try:
                        error_detail = response.json()
                        print(f"    Error: {error_detail}")
                    except:
                        pass
            except Exception as e:
                print(f"  ❌ Error: {e}")
        else:
            print("  ❌ No admin token found")
    else:
        print("  ❌ No token file found")

if __name__ == "__main__":
    test_simple_auth()