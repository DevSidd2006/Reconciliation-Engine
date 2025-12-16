#!/usr/bin/env python3
"""
Token Testing Script
Tests generated tokens against the API endpoints
"""

import json
import requests
import sys
from pathlib import Path
from typing import Dict, Any, Optional


class TokenTester:
    """Tests API tokens and endpoints"""
    
    def __init__(self, tokens_file: str, api_base_url: str = "http://localhost:8000"):
        self.tokens_file = Path(tokens_file)
        self.api_base_url = api_base_url.rstrip('/')
        self.tokens = {}
        
    def load_tokens(self) -> bool:
        """Load tokens from JSON file"""
        if not self.tokens_file.exists():
            print(f"❌ Tokens file not found: {self.tokens_file}")
            return False
        
        try:
            with open(self.tokens_file, 'r') as f:
                data = json.load(f)
                self.tokens = data.get('tokens', {})
            
            if not self.tokens:
                print("❌ No tokens found in file")
                return False
            
            print(f"✅ Loaded {len(self.tokens)} tokens from {self.tokens_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading tokens: {e}")
            return False
    
    def test_endpoint(self, token: str, endpoint: str, method: str = "GET") -> Dict[str, Any]:
        """Test an API endpoint with a token"""
        url = f"{self.api_base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, timeout=10)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
            
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {e}"}
    
    def test_token_validity(self, token_name: str, token_data: Dict[str, Any]) -> None:
        """Test a single token against various endpoints"""
        if not token_data:
            print(f"❌ {token_name}: No token data")
            return
        
        access_token = token_data.get('access_token')
        if not access_token:
            print(f"❌ {token_name}: No access token")
            return
        
        role = token_data.get('role', 'unknown')
        username = token_data.get('username', 'unknown')
        
        print(f"\n🔍 Testing {token_name} ({role} - {username})")
        print("-" * 50)
        
        # Test endpoints
        endpoints = [
            ("/health", "GET", "Health check"),
            ("/", "GET", "Root endpoint"),
            ("/security/status", "GET", "Security status"),
        ]
        
        # Add role-specific endpoints
        if role in ['admin', 'auditor', 'operator']:
            endpoints.extend([
                ("/transactions", "GET", "List transactions"),
                ("/mismatches", "GET", "List mismatches"),
            ])
        
        if role == 'admin':
            endpoints.extend([
                ("/admin/users", "GET", "Admin users"),
                ("/admin/audit-logs", "GET", "Audit logs"),
            ])
        
        success_count = 0
        total_count = len(endpoints)
        
        for endpoint, method, description in endpoints:
            result = self.test_endpoint(access_token, endpoint, method)
            
            if result["success"]:
                print(f"  ✅ {description}: HTTP {result['status_code']}")
                success_count += 1
            else:
                status = result.get('status_code', 'N/A')
                error = result.get('error', 'Unknown error')
                print(f"  ❌ {description}: HTTP {status} - {error}")
        
        # Summary
        success_rate = (success_count / total_count) * 100
        if success_rate >= 80:
            print(f"  🎉 Token working: {success_count}/{total_count} endpoints ({success_rate:.0f}%)")
        elif success_rate >= 50:
            print(f"  ⚠️  Token partial: {success_count}/{total_count} endpoints ({success_rate:.0f}%)")
        else:
            print(f"  💥 Token failing: {success_count}/{total_count} endpoints ({success_rate:.0f}%)")
    
    def test_api_health(self) -> bool:
        """Test if API is responding"""
        print("🏥 Testing API health...")
        
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API is healthy and responding")
                return True
            else:
                print(f"❌ API health check failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API is not accessible: {e}")
            return False
    
    def run_tests(self) -> bool:
        """Run all token tests"""
        print("🧪 Token Testing Suite")
        print("=" * 60)
        
        # Load tokens
        if not self.load_tokens():
            return False
        
        # Test API health first
        if not self.test_api_health():
            print("\n❌ API is not accessible. Make sure the security stack is running.")
            print("Run: python scripts/start_security_stack.py")
            return False
        
        # Test each token
        all_working = True
        for token_name, token_data in self.tokens.items():
            try:
                self.test_token_validity(token_name, token_data)
            except Exception as e:
                print(f"❌ Error testing {token_name}: {e}")
                all_working = False
        
        # Final summary
        print("\n" + "=" * 60)
        if all_working:
            print("🎉 All tokens tested successfully!")
            print("\nYou can now use these tokens to access the API:")
            print(f"  Authorization: Bearer <token>")
            print(f"  API Base URL: {self.api_base_url}")
        else:
            print("⚠️  Some tokens had issues. Check the output above.")
        
        print(f"\nTokens file: {self.tokens_file}")
        print("=" * 60)
        
        return all_working


def main():
    """Main function"""
    # Determine tokens file path
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    tokens_file = project_root / "tmp" / "tokens.json"
    
    # Parse command line arguments
    api_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        if sys.argv[1].startswith("http"):
            api_url = sys.argv[1]
        else:
            tokens_file = Path(sys.argv[1])
    
    if len(sys.argv) > 2:
        api_url = sys.argv[2]
    
    print(f"Testing tokens from: {tokens_file}")
    print(f"Against API: {api_url}")
    
    # Run tests
    tester = TokenTester(str(tokens_file), api_url)
    success = tester.run_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()