#!/usr/bin/env python3
"""
HTTPS Setup Script for Local Development
Sets up self-signed certificates and configures Traefik for HTTPS
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any


class HTTPSSetup:
    """Sets up HTTPS with self-signed certificates for local development"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_dir = project_root / "backend"
        
    def log(self, message: str) -> None:
        """Log info message"""
        print(f"🔐 {message}")
    
    def success(self, message: str) -> None:
        """Log success message"""
        print(f"✅ {message}")
    
    def error(self, message: str) -> None:
        """Log error message"""
        print(f"❌ {message}")
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        print(f"⚠️  {message}")
    
    def generate_certificates(self) -> bool:
        """Generate SSL certificates"""
        self.log("Generating SSL certificates...")
        
        # Try Python-based generator first (no OpenSSL required)
        python_cert_script = self.backend_dir / "scripts" / "generate_ssl_certs_python.py"
        openssl_cert_script = self.backend_dir / "scripts" / "generate_ssl_certs.py"
        
        cert_script = python_cert_script if python_cert_script.exists() else openssl_cert_script
        
        if not cert_script.exists():
            self.error(f"Certificate generation script not found: {cert_script}")
            return False
        
        try:
            result = subprocess.run([sys.executable, str(cert_script)], 
                                  cwd=self.backend_dir, timeout=120)
            
            if result.returncode == 0:
                self.success("SSL certificates generated successfully")
                return True
            else:
                self.error("Certificate generation failed")
                return False
                
        except subprocess.TimeoutExpired:
            self.error("Certificate generation timed out")
            return False
        except Exception as e:
            self.error(f"Certificate generation error: {e}")
            return False
    
    def check_certificates(self) -> bool:
        """Check if certificates exist"""
        traefik_dir = self.backend_dir / "traefik"
        cert_file = traefik_dir / "localhost.crt"
        key_file = traefik_dir / "localhost.key"
        config_file = traefik_dir / "tls.yml"
        
        if cert_file.exists() and key_file.exists() and config_file.exists():
            self.success("SSL certificates found")
            return True
        else:
            self.log("SSL certificates not found, generating...")
            return False
    
    def restart_traefik(self) -> bool:
        """Restart Traefik to pick up new certificates"""
        self.log("Restarting Traefik to load certificates...")
        
        try:
            # Stop Traefik
            result = subprocess.run([
                'docker-compose', '-f', 'docker-compose.traefik.yml', 
                'stop', 'traefik'
            ], cwd=self.backend_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.warning(f"Failed to stop Traefik: {result.stderr}")
            
            # Remove Traefik container to force recreation
            subprocess.run(['docker', 'rm', 'reconciliation_traefik'], 
                         capture_output=True)
            
            # Start Traefik
            result = subprocess.run([
                'docker-compose', '-f', 'docker-compose.traefik.yml', 
                'up', '-d', 'traefik'
            ], cwd=self.backend_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.success("Traefik restarted successfully")
                return True
            else:
                self.error(f"Failed to start Traefik: {result.stderr}")
                return False
                
        except Exception as e:
            self.error(f"Error restarting Traefik: {e}")
            return False
    
    def test_https(self) -> bool:
        """Test HTTPS connectivity"""
        self.log("Testing HTTPS connectivity...")
        
        import time
        import requests
        from urllib3.exceptions import InsecureRequestWarning
        
        # Disable SSL warnings for self-signed certificates
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        
        # Wait for Traefik to start
        time.sleep(10)
        
        test_urls = [
            "https://localhost/dashboard/",
            "https://localhost/api/health",
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url, verify=False, timeout=10)
                if response.status_code < 400:
                    self.success(f"HTTPS working: {url} (HTTP {response.status_code})")
                else:
                    self.warning(f"HTTPS response: {url} (HTTP {response.status_code})")
            except requests.exceptions.ConnectionError:
                self.warning(f"HTTPS not ready: {url} (connection refused)")
            except Exception as e:
                self.warning(f"HTTPS test error: {url} - {e}")
        
        return True
    
    def print_access_urls(self) -> None:
        """Print access URLs for HTTPS services"""
        print("\n" + "=" * 60)
        print("🌐 HTTPS SETUP COMPLETE")
        print("=" * 60)
        print("Your services are now available via HTTPS:")
        print()
        print("🔒 HTTPS URLs (Self-Signed Certificates):")
        print("   • API: https://localhost/api/")
        print("   • API Health: https://localhost/api/health")
        print("   • Traefik Dashboard: https://localhost/dashboard/")
        print("   • Keycloak: https://localhost/auth/")
        print()
        print("🔓 HTTP URLs (Development):")
        print("   • API: http://localhost:8000/")
        print("   • Keycloak: http://localhost:8082/")
        print("   • Traefik Dashboard: http://localhost:8081/")
        print()
        print("⚠️  Browser Security Warning:")
        print("   Your browser will show a security warning for self-signed certificates.")
        print("   Click 'Advanced' → 'Proceed to localhost (unsafe)' to continue.")
        print()
        print("🔧 To avoid warnings, install the CA certificate:")
        print("   File: backend/ssl-certs/ca-cert.pem")
        print("   See installation instructions in the certificate generation output.")
        print("=" * 60)
    
    def setup_https(self) -> bool:
        """Set up HTTPS with self-signed certificates"""
        print("🔐 HTTPS Setup for Local Development")
        print("=" * 60)
        
        try:
            # Check if certificates exist
            if not self.check_certificates():
                # Generate certificates
                if not self.generate_certificates():
                    return False
            
            # Restart Traefik to load certificates
            if not self.restart_traefik():
                return False
            
            # Test HTTPS
            self.test_https()
            
            # Print access URLs
            self.print_access_urls()
            
            self.success("HTTPS setup completed successfully!")
            return True
            
        except KeyboardInterrupt:
            self.error("HTTPS setup cancelled by user")
            return False
        except Exception as e:
            self.error(f"HTTPS setup failed: {e}")
            return False


def main():
    """Main function"""
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent  # Go up from backend/scripts to project root
    
    print(f"Project root: {project_root}")
    print(f"Backend dir: {project_root / 'backend'}")
    
    # Set up HTTPS
    setup = HTTPSSetup(project_root)
    success = setup.setup_https()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()