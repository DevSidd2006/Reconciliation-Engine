#!/usr/bin/env python3
"""
HTTPS Testing Script
Tests HTTPS connectivity with self-signed certificates
"""

import sys
import requests
import time
from urllib3.exceptions import InsecureRequestWarning


def test_https():
    """Test HTTPS endpoints"""
    
    # Disable SSL warnings for self-signed certificates
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    print("🔐 Testing HTTPS Connectivity")
    print("=" * 50)
    
    test_endpoints = [
        ("API Health", "https://localhost/api/health"),
        ("API Root", "https://localhost/api/"),
        ("Traefik Dashboard", "https://localhost/dashboard/"),

    ]
    
    success_count = 0
    total_count = len(test_endpoints)
    
    for name, url in test_endpoints:
        try:
            print(f"Testing {name}...", end=" ")
            response = requests.get(url, verify=False, timeout=10)
            
            if response.status_code < 400:
                print(f"✅ HTTP {response.status_code}")
                success_count += 1
            else:
                print(f"⚠️  HTTP {response.status_code}")
                success_count += 1  # Still counts as working HTTPS
                
        except requests.exceptions.SSLError as e:
            print(f"❌ SSL Error: {e}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection refused (service not running)")
        except requests.exceptions.Timeout:
            print(f"❌ Timeout")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print(f"HTTPS Test Results: {success_count}/{total_count} endpoints working")
    
    if success_count > 0:
        print("✅ HTTPS is working with self-signed certificates!")
        print("\n📋 Access URLs:")
        print("   • API: https://localhost/api/health")
        print("   • Dashboard: https://localhost/dashboard/")

        print("\n⚠️  Browser Warning:")
        print("   Your browser will show a security warning.")
        print("   Click 'Advanced' → 'Proceed to localhost (unsafe)'")
        return True
    else:
        print("❌ HTTPS is not working. Check:")
        print("   1. Traefik is running: docker ps | grep traefik")
        print("   2. Certificates exist: ls backend/traefik/")
        print("   3. Services are up: docker-compose ps")
        return False


def test_certificate_info():
    """Display certificate information"""
    print("\n🔍 Certificate Information")
    print("-" * 30)
    
    try:
        import ssl
        import socket
        
        # Get certificate info
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection(('localhost', 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname='localhost') as ssock:
                cert = ssock.getpeercert()
                
                print(f"Subject: {dict(x[0] for x in cert['subject'])}")
                print(f"Issuer: {dict(x[0] for x in cert['issuer'])}")
                print(f"Valid from: {cert['notBefore']}")
                print(f"Valid until: {cert['notAfter']}")
                
                if 'subjectAltName' in cert:
                    alt_names = [name[1] for name in cert['subjectAltName']]
                    print(f"Alt names: {', '.join(alt_names)}")
                
    except Exception as e:
        print(f"Could not retrieve certificate info: {e}")


def main():
    """Main function"""
    print("HTTPS Test Suite for Self-Signed Certificates")
    print("=" * 60)
    
    # Wait a moment for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(5)
    
    # Test HTTPS connectivity
    https_working = test_https()
    
    # Show certificate info if HTTPS is working
    if https_working:
        test_certificate_info()
    
    print("\n" + "=" * 60)
    
    if https_working:
        print("🎉 HTTPS testing completed successfully!")
        return True
    else:
        print("💥 HTTPS testing failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)