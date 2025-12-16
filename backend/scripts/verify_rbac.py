#!/usr/bin/env python3
"""
Comprehensive RBAC Verification Script for Banking-Grade Transaction Reconciliation Engine

This script performs complete verification of Role-Based Access Control including:
- Token validation with different roles
- API endpoint protection testing
- Role hierarchy verification
- Permission-based access control
- Unauthorized access behavior (401/403 responses)
"""

import json
import requests
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import time

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class RBACVerifier:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.tokens = self.load_tokens()
        self.test_results = []
        
    def load_tokens(self) -> Dict:
        """Load test tokens from tokens.json"""
        token_file = Path(__file__).parent.parent / "tmp" / "tokens.json"
        if not token_file.exists():
            print("❌ Token file not found. Run generate_tokens.py first.")
            sys.exit(1)
            
        with open(token_file, 'r') as f:
            data = json.load(f)
            return data.get("tokens", {})
    
    def make_request(self, method: str, endpoint: str, token: Optional[str] = None, 
                    data: Optional[Dict] = None) -> Tuple[int, Dict]:
        """Make HTTP request with optional authentication"""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                headers["Content-Type"] = "application/json"
                response = requests.post(url, headers=headers, json=data or {}, timeout=10)
            elif method.upper() == "PUT":
                headers["Content-Type"] = "application/json"
                response = requests.put(url, headers=headers, json=data or {}, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return 400, {"error": "Unsupported method"}
            
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, {"text": response.text}
                
        except requests.exceptions.RequestException as e:
            return 0, {"error": str(e)}
    
    def test_endpoint_access(self, role: str, method: str, endpoint: str, 
                           expected_status: int, description: str) -> bool:
        """Test access to specific endpoint with given role"""
        token_key = f"TOKEN_{role.upper()}"
        token = None
        
        if role != "anonymous":
            if token_key not in self.tokens:
                print(f"❌ Token not found for role: {role}")
                return False
            token = self.tokens[token_key]["access_token"]
        
        status_code, response = self.make_request(method, endpoint, token)
        
        success = status_code == expected_status
        status_icon = "✅" if success else "❌"
        
        print(f"{status_icon} {role.upper():8} {method:6} {endpoint:25} -> {status_code:3} (expected {expected_status:3}) - {description}")
        
        if not success:
            print(f"   Response: {response}")
        
        self.test_results.append({
            "role": role,
            "method": method,
            "endpoint": endpoint,
            "expected_status": expected_status,
            "actual_status": status_code,
            "success": success,
            "description": description,
            "response": response
        })
        
        return success
    
    def verify_health_endpoint(self):
        """Verify health endpoint is publicly accessible"""
        print("\n🔍 Testing Health Endpoint (Public Access)")
        print("=" * 80)
        
        # Health endpoint should be accessible without authentication
        self.test_endpoint_access("anonymous", "GET", "/", 200, "Public health check")
        self.test_endpoint_access("anonymous", "GET", "/health", 200, "Public health endpoint")
    
    def verify_authentication_required(self):
        """Verify that protected endpoints require authentication"""
        print("\n🔍 Testing Authentication Requirements (401 Unauthorized)")
        print("=" * 80)
        
        protected_endpoints = [
            ("GET", "/transactions", "Transaction list requires auth"),
            ("GET", "/transactions/stats", "Transaction stats require auth"),
            ("GET", "/mismatches", "Mismatch list requires auth"),
            ("GET", "/mismatches/stats", "Mismatch stats require auth"),
            ("GET", "/admin", "Admin dashboard requires auth"),
        ]
        
        for method, endpoint, description in protected_endpoints:
            self.test_endpoint_access("anonymous", method, endpoint, 401, description)
    
    def verify_role_based_access(self):
        """Verify role-based access control for different endpoints"""
        print("\n🔍 Testing Role-Based Access Control")
        print("=" * 80)
        
        # Test cases: (role, method, endpoint, expected_status, description)
        test_cases = [
            # Transaction endpoints - Auditor can read
            ("auditor", "GET", "/transactions", 200, "Auditor can read transactions"),
            ("auditor", "GET", "/transactions/stats", 200, "Auditor can read transaction stats"),
            
            # Operator can read and write transactions
            ("operator", "GET", "/transactions", 200, "Operator can read transactions"),
            ("operator", "POST", "/transactions", 200, "Operator can create transactions"),
            
            # Viewer has limited access
            ("viewer", "GET", "/transactions", 403, "Viewer cannot read transactions (needs auditor+)"),
            
            # Mismatch endpoints - Operator can read and write
            ("operator", "GET", "/mismatches", 200, "Operator can read mismatches"),
            ("operator", "POST", "/mismatches/resolve", 200, "Operator can resolve mismatches"),
            
            # Auditor can read mismatches
            ("auditor", "GET", "/mismatches/stats", 200, "Auditor can read mismatch stats"),
            
            # Admin endpoints - Admin only
            ("admin", "GET", "/admin", 200, "Admin can access admin dashboard"),
            ("admin", "GET", "/admin/audit-logs", 200, "Admin can access audit logs"),
            ("admin", "GET", "/admin/system-health", 200, "Admin can check system health"),
            
            # Non-admin roles cannot access admin endpoints
            ("auditor", "GET", "/admin", 403, "Auditor cannot access admin dashboard"),
            ("operator", "GET", "/admin", 403, "Operator cannot access admin dashboard"),
            ("viewer", "GET", "/admin", 403, "Viewer cannot access admin dashboard"),
            
            # Delete operations - Admin only
            ("admin", "DELETE", "/transactions/test-123", 200, "Admin can delete transactions"),
            ("operator", "DELETE", "/transactions/test-123", 403, "Operator cannot delete transactions"),
            ("auditor", "DELETE", "/transactions/test-123", 403, "Auditor cannot delete transactions"),
        ]
        
        for role, method, endpoint, expected_status, description in test_cases:
            self.test_endpoint_access(role, method, endpoint, expected_status, description)
    
    def verify_token_validation(self):
        """Verify token validation logic"""
        print("\n🔍 Testing Token Validation")
        print("=" * 80)
        
        # Test with invalid token
        invalid_token = "invalid.jwt.token"
        headers = {"Authorization": f"Bearer {invalid_token}"}
        
        try:
            response = requests.get(f"{self.base_url}/transactions", headers=headers, timeout=10)
            success = response.status_code == 401
            status_icon = "✅" if success else "❌"
            print(f"{status_icon} Invalid token -> {response.status_code} (expected 401) - Invalid token rejected")
            
            if not success:
                print(f"   Response: {response.json()}")
                
        except Exception as e:
            print(f"❌ Error testing invalid token: {e}")
    
    def verify_role_hierarchy(self):
        """Verify role hierarchy and permission inheritance"""
        print("\n🔍 Testing Role Hierarchy")
        print("=" * 80)
        
        # Admin should have access to everything
        admin_endpoints = [
            ("GET", "/transactions", "Admin inherits transaction read"),
            ("GET", "/mismatches", "Admin inherits mismatch read"),
            ("GET", "/admin", "Admin has admin access"),
        ]
        
        for method, endpoint, description in admin_endpoints:
            self.test_endpoint_access("admin", method, endpoint, 200, description)
    
    def verify_audit_logging(self):
        """Verify that RBAC actions are properly logged"""
        print("\n🔍 Testing Audit Logging")
        print("=" * 80)
        
        # Make some authenticated requests to generate audit logs
        admin_token = self.tokens.get("TOKEN_ADMIN", {}).get("access_token")
        if admin_token:
            # Access some endpoints to generate logs
            self.make_request("GET", "/transactions/stats", admin_token)
            self.make_request("GET", "/admin/system-health", admin_token)
            
            # Check if audit logs are accessible
            status_code, response = self.make_request("GET", "/admin/audit-logs", admin_token)
            success = status_code == 200
            status_icon = "✅" if success else "❌"
            print(f"{status_icon} Audit logs accessible -> {status_code} (expected 200) - Audit logging functional")
            
            if success and isinstance(response, dict) and "data" in response:
                log_count = len(response["data"]) if isinstance(response["data"], list) else 0
                print(f"   Found {log_count} audit log entries")
        else:
            print("❌ Admin token not available for audit log testing")
    
    def run_verification(self):
        """Run complete RBAC verification"""
        print("🔐 Banking-Grade RBAC Verification")
        print("=" * 80)
        print(f"API Base URL: {self.base_url}")
        print(f"Available tokens: {list(self.tokens.keys())}")
        print()
        
        # Wait for API to be ready
        print("⏳ Waiting for API to be ready...")
        for i in range(30):
            try:
                response = requests.get(f"{self.base_url}/", timeout=5)
                if response.status_code == 200:
                    print("✅ API is ready")
                    break
            except:
                pass
            time.sleep(1)
        else:
            print("❌ API not responding. Make sure the backend is running.")
            return False
        
        # Run all verification tests
        self.verify_health_endpoint()
        self.verify_authentication_required()
        self.verify_token_validation()
        self.verify_role_based_access()
        self.verify_role_hierarchy()
        self.verify_audit_logging()
        
        # Summary
        self.print_summary()
        
        return self.get_overall_success()
    
    def print_summary(self):
        """Print verification summary"""
        print("\n📊 RBAC Verification Summary")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   {result['role']} {result['method']} {result['endpoint']} - {result['description']}")
                    print(f"      Expected: {result['expected_status']}, Got: {result['actual_status']}")
    
    def get_overall_success(self) -> bool:
        """Check if all tests passed"""
        return all(result["success"] for result in self.test_results)

def main():
    """Main verification function"""
    verifier = RBACVerifier()
    success = verifier.run_verification()
    
    if success:
        print("\n🎉 All RBAC verification tests passed!")
        print("✅ Banking-grade security is properly implemented")
        sys.exit(0)
    else:
        print("\n⚠️  Some RBAC verification tests failed")
        print("❌ Review the failed tests and fix security issues")
        sys.exit(1)

if __name__ == "__main__":
    main()