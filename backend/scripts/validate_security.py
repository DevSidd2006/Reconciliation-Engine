#!/usr/bin/env python3
"""
Banking-Grade Security Validation Script for Transaction Reconciliation Engine

This script automatically validates all security features:
- HTTPS/TLS configuration
- Mock authentication
- RBAC authorization
- Audit logging
- Rate limiting
"""

import requests
import json
import sys
import time
import subprocess
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8000"
# Keycloak removed - using mock authentication
TRAEFIK_DASHBOARD_URL = "http://localhost:8081"

class SecurityValidator:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
    
    def log_test(self, test_name, success, message=""):
        """Log test result"""
        status = "PASS" if success else "FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    def test_service_availability(self):
        """Test if all services are running"""
        print("\nTesting Service Availability")
        print("-" * 40)
        
        services = [
            ("API Server", API_BASE_URL),

            ("Traefik Dashboard", TRAEFIK_DASHBOARD_URL)
        ]
        
        for service_name, url in services:
            try:
                response = requests.get(url, timeout=5)
                success = response.status_code in [200, 404]  # 404 is OK for some endpoints
                self.log_test(f"{service_name} Available", success, f"Status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.log_test(f"{service_name} Available", False, f"Error: {str(e)}")
    
    def test_public_endpoints(self):
        """Test public endpoints work without authentication"""
        print("\n🌐 Testing Public Endpoints")
        print("-" * 40)
        
        public_endpoints = [
            ("/", "Health Check"),
            ("/security/status", "Security Status")
        ]
        
        for endpoint, description in public_endpoints:
            try:
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
                success = response.status_code == 200
                self.log_test(f"Public {description}", success, f"Status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.log_test(f"Public {description}", False, f"Error: {str(e)}")
    
    def test_protected_endpoints_without_auth(self):
        """Test protected endpoints return 401 without authentication"""
        print("\n🔒 Testing Protected Endpoints (No Auth)")
        print("-" * 40)
        
        protected_endpoints = [
            ("/transactions/stats", "Transaction Stats"),
            ("/mismatches/stats", "Mismatch Stats"),
            ("/admin/system-health", "Admin Health")
        ]
        
        for endpoint, description in protected_endpoints:
            try:
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
                success = response.status_code == 401
                self.log_test(f"Protected {description} (401)", success, f"Status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.log_test(f"Protected {description} (401)", False, f"Error: {str(e)}")
    
    def load_test_tokens(self):
        """Load test tokens from file or generate them"""
        print("\n🎫 Loading Test Tokens")
        print("-" * 40)
        
        tokens_file = Path(__file__).parent / "test_tokens.json"
        
        if tokens_file.exists():
            try:
                with open(tokens_file, 'r') as f:
                    self.tokens = json.load(f)
                self.log_test("Load Existing Tokens", True, f"Loaded {len(self.tokens)} tokens")
            except Exception as e:
                self.log_test("Load Existing Tokens", False, f"Error: {str(e)}")
        
        if not self.tokens:
            print("🔄 Generating new tokens...")
            try:
                # Run token generation script
                result = subprocess.run([
                    sys.executable, 
                    str(Path(__file__).parent / "generate_test_tokens.py")
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    # Try to load tokens again
                    if tokens_file.exists():
                        with open(tokens_file, 'r') as f:
                            self.tokens = json.load(f)
                    self.log_test("Generate New Tokens", True, f"Generated {len(self.tokens)} tokens")
                else:
                    self.log_test("Generate New Tokens", False, f"Script failed: {result.stderr}")
            except Exception as e:
                self.log_test("Generate New Tokens", False, f"Error: {str(e)}")
    
    def test_rbac_authorization(self):
        """Test role-based access control"""
        print("\n👥 Testing RBAC Authorization")
        print("-" * 40)
        
        if not self.tokens:
            self.log_test("RBAC Tests", False, "No tokens available")
            return
        
        # Test cases: (endpoint, required_role, expected_status_for_roles)
        test_cases = [
            ("/transactions/stats", "auditor", {
                "admin": 200, "auditor": 200, "operator": 403, "viewer": 403
            }),
            ("/admin/system-health", "admin", {
                "admin": 200, "auditor": 403, "operator": 403, "viewer": 403
            })
        ]
        
        for endpoint, required_role, expected_statuses in test_cases:
            for role, token in self.tokens.items():
                if not token:
                    continue
                
                try:
                    headers = {"Authorization": f"Bearer {token}"}
                    response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers, timeout=10)
                    
                    expected_status = expected_statuses.get(role, 403)
                    success = response.status_code == expected_status
                    
                    self.log_test(
                        f"RBAC {role} → {endpoint}",
                        success,
                        f"Expected: {expected_status}, Got: {response.status_code}"
                    )
                except requests.exceptions.RequestException as e:
                    self.log_test(f"RBAC {role} → {endpoint}", False, f"Error: {str(e)}")
    
    def test_security_headers(self):
        """Test security headers are present"""
        print("\n🛡️  Testing Security Headers")
        print("-" * 40)
        
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Referrer-Policy"
        ]
        
        try:
            response = requests.get(f"{API_BASE_URL}/", timeout=5)
            
            for header in required_headers:
                present = header in response.headers
                self.log_test(f"Security Header: {header}", present, 
                            f"Value: {response.headers.get(header, 'Missing')}")
        except requests.exceptions.RequestException as e:
            self.log_test("Security Headers", False, f"Error: {str(e)}")
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        print("\n⚡ Testing Rate Limiting")
        print("-" * 40)
        
        # Make rapid requests to trigger rate limiting
        endpoint = f"{API_BASE_URL}/"
        rate_limited = False
        
        try:
            for i in range(25):  # Exceed typical rate limits
                response = requests.get(endpoint, timeout=2)
                if response.status_code == 429:
                    rate_limited = True
                    break
            
            self.log_test("Rate Limiting Active", rate_limited, 
                        "Rate limiting triggered" if rate_limited else "No rate limiting detected")
        except requests.exceptions.RequestException as e:
            self.log_test("Rate Limiting Active", False, f"Error: {str(e)}")
    
    def test_audit_logging(self):
        """Test audit logging functionality"""
        print("\n📝 Testing Audit Logging")
        print("-" * 40)
        
        if "admin" not in self.tokens:
            self.log_test("Audit Logging", False, "No admin token available")
            return
        
        try:
            # Access admin endpoint to generate audit log
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            response = requests.get(f"{API_BASE_URL}/admin/audit-logs?limit=1", headers=headers, timeout=10)
            
            success = response.status_code == 200
            self.log_test("Audit Logs Accessible", success, f"Status: {response.status_code}")
            
            if success:
                data = response.json()
                has_logs = len(data.get("data", [])) > 0
                self.log_test("Audit Logs Present", has_logs, 
                            f"Found {len(data.get('data', []))} audit entries")
        except requests.exceptions.RequestException as e:
            self.log_test("Audit Logging", False, f"Error: {str(e)}")
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "=" * 60)
        print("🎯 BANKING-GRADE SECURITY VALIDATION REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        print(f"\n🏆 Overall Status: {'PASS' if failed_tests == 0 else 'FAIL'}")
        
        if failed_tests == 0:
            print("\n🎉 All security features are working correctly!")
            print("   The banking-grade security implementation is complete.")
        else:
            print(f"\n🔧 Please fix the {failed_tests} failed test(s) above.")
        
        return failed_tests == 0

def main():
    """Run complete security validation"""
    print("Banking-Grade Security Validation")
    print("=" * 60)
    print("This script validates all Phase 4 security features")
    print("=" * 60)
    
    validator = SecurityValidator()
    
    # Run all validation tests
    validator.test_service_availability()
    validator.test_public_endpoints()
    validator.test_protected_endpoints_without_auth()
    validator.load_test_tokens()
    validator.test_rbac_authorization()
    validator.test_security_headers()
    validator.test_rate_limiting()
    validator.test_audit_logging()
    
    # Generate final report
    success = validator.generate_report()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()