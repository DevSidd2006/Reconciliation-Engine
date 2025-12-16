#!/usr/bin/env python3
"""
Self-Signed SSL Certificate Generator for Local Development
Generates TLS certificates for HTTPS testing without requiring real domains
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import ipaddress


class SSLCertificateGenerator:
    """Generates self-signed SSL certificates for local development"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.certs_dir = project_root / "ssl-certs"
        self.traefik_dir = project_root / "traefik"
        
    def create_directories(self) -> None:
        """Create necessary directories for certificates"""
        self.certs_dir.mkdir(exist_ok=True)
        self.traefik_dir.mkdir(exist_ok=True)
        print(f"✅ Created certificate directories")
    
    def check_openssl(self) -> bool:
        """Check if OpenSSL is available"""
        try:
            result = subprocess.run(['openssl', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ OpenSSL available: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ OpenSSL not working: {result.stderr}")
                return False
        except FileNotFoundError:
            print("❌ OpenSSL not found. Please install OpenSSL:")
            print("   Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
            print("   Or use: winget install OpenSSL.Light")
            return False
        except Exception as e:
            print(f"❌ Error checking OpenSSL: {e}")
            return False
    
    def create_ca_certificate(self) -> bool:
        """Create Certificate Authority (CA) certificate"""
        print("\n🔐 Creating Certificate Authority (CA)...")
        
        ca_key = self.certs_dir / "ca-key.pem"
        ca_cert = self.certs_dir / "ca-cert.pem"
        
        # Generate CA private key
        ca_key_cmd = [
            'openssl', 'genrsa', 
            '-out', str(ca_key),
            '4096'
        ]
        
        result = subprocess.run(ca_key_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to generate CA key: {result.stderr}")
            return False
        
        # Generate CA certificate
        ca_cert_cmd = [
            'openssl', 'req', '-new', '-x509',
            '-key', str(ca_key),
            '-out', str(ca_cert),
            '-days', '365',
            '-subj', '/C=US/ST=Development/L=Local/O=Banking Reconciliation/OU=Development/CN=Local Development CA'
        ]
        
        result = subprocess.run(ca_cert_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to generate CA certificate: {result.stderr}")
            return False
        
        print(f"✅ CA certificate created: {ca_cert}")
        return True
    
    def create_server_certificate(self) -> bool:
        """Create server certificate for localhost"""
        print("\n🌐 Creating server certificate for localhost...")
        
        server_key = self.certs_dir / "server-key.pem"
        server_csr = self.certs_dir / "server.csr"
        server_cert = self.certs_dir / "server-cert.pem"
        ca_key = self.certs_dir / "ca-key.pem"
        ca_cert = self.certs_dir / "ca-cert.pem"
        
        # Generate server private key
        server_key_cmd = [
            'openssl', 'genrsa',
            '-out', str(server_key),
            '2048'
        ]
        
        result = subprocess.run(server_key_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to generate server key: {result.stderr}")
            return False
        
        # Create certificate signing request (CSR)
        server_csr_cmd = [
            'openssl', 'req', '-new',
            '-key', str(server_key),
            '-out', str(server_csr),
            '-subj', '/C=US/ST=Development/L=Local/O=Banking Reconciliation/OU=API/CN=localhost'
        ]
        
        result = subprocess.run(server_csr_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to generate CSR: {result.stderr}")
            return False
        
        # Create extensions file for SAN (Subject Alternative Names)
        ext_file = self.certs_dir / "server.ext"
        ext_content = """authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
DNS.3 = 127.0.0.1
DNS.4 = api.localhost
DNS.5 = auth.localhost
DNS.6 = traefik.localhost
IP.1 = 127.0.0.1
IP.2 = ::1
"""
        
        with open(ext_file, 'w') as f:
            f.write(ext_content)
        
        # Sign the certificate with CA
        server_cert_cmd = [
            'openssl', 'x509', '-req',
            '-in', str(server_csr),
            '-CA', str(ca_cert),
            '-CAkey', str(ca_key),
            '-CAcreateserial',
            '-out', str(server_cert),
            '-days', '365',
            '-extensions', 'v3_req',
            '-extfile', str(ext_file)
        ]
        
        result = subprocess.run(server_cert_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to sign server certificate: {result.stderr}")
            return False
        
        print(f"✅ Server certificate created: {server_cert}")
        
        # Clean up temporary files
        server_csr.unlink(missing_ok=True)
        ext_file.unlink(missing_ok=True)
        
        return True
    
    def create_traefik_certificates(self) -> bool:
        """Create certificates in format expected by Traefik"""
        print("\n🚛 Creating Traefik certificate files...")
        
        server_key = self.certs_dir / "server-key.pem"
        server_cert = self.certs_dir / "server-cert.pem"
        
        # Copy certificates to traefik directory
        traefik_cert = self.traefik_dir / "localhost.crt"
        traefik_key = self.traefik_dir / "localhost.key"
        
        # Copy server certificate and key
        with open(server_cert, 'r') as src, open(traefik_cert, 'w') as dst:
            dst.write(src.read())
        
        with open(server_key, 'r') as src, open(traefik_key, 'w') as dst:
            dst.write(src.read())
        
        print(f"✅ Traefik certificates created:")
        print(f"   Certificate: {traefik_cert}")
        print(f"   Private Key: {traefik_key}")
        
        return True
    
    def create_traefik_config(self) -> bool:
        """Create Traefik dynamic configuration for TLS"""
        print("\n⚙️  Creating Traefik TLS configuration...")
        
        traefik_config = self.traefik_dir / "tls.yml"
        
        config_content = """# Traefik TLS Configuration for Self-Signed Certificates
tls:
  certificates:
    - certFile: /etc/traefik/certs/localhost.crt
      keyFile: /etc/traefik/certs/localhost.key
      stores:
        - default
  
  stores:
    default:
      defaultCertificate:
        certFile: /etc/traefik/certs/localhost.crt
        keyFile: /etc/traefik/certs/localhost.key

  options:
    default:
      sslProtocols:
        - "TLSv1.2"
        - "TLSv1.3"
      cipherSuites:
        - "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
        - "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305"
        - "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
      curvePreferences:
        - "CurveP521"
        - "CurveP384"
      minVersion: "VersionTLS12"
"""
        
        with open(traefik_config, 'w') as f:
            f.write(config_content)
        
        print(f"✅ Traefik TLS config created: {traefik_config}")
        return True
    
    def verify_certificates(self) -> bool:
        """Verify the generated certificates"""
        print("\n🔍 Verifying certificates...")
        
        server_cert = self.certs_dir / "server-cert.pem"
        
        # Verify certificate
        verify_cmd = [
            'openssl', 'x509', '-in', str(server_cert),
            '-text', '-noout'
        ]
        
        result = subprocess.run(verify_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Certificate verification failed: {result.stderr}")
            return False
        
        # Extract key information
        info_cmd = [
            'openssl', 'x509', '-in', str(server_cert),
            '-subject', '-issuer', '-dates', '-noout'
        ]
        
        result = subprocess.run(info_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Certificate verification successful:")
            for line in result.stdout.strip().split('\n'):
                print(f"   {line}")
        
        return True
    
    def print_installation_instructions(self) -> None:
        """Print instructions for installing the CA certificate"""
        ca_cert = self.certs_dir / "ca-cert.pem"
        
        print(f"\n📋 CERTIFICATE INSTALLATION INSTRUCTIONS")
        print("=" * 60)
        print(f"To avoid browser security warnings, install the CA certificate:")
        print(f"CA Certificate: {ca_cert.absolute()}")
        print()
        print("🪟 Windows:")
        print("1. Double-click ca-cert.pem")
        print("2. Click 'Install Certificate'")
        print("3. Choose 'Local Machine' → Next")
        print("4. Select 'Place all certificates in the following store'")
        print("5. Browse → 'Trusted Root Certification Authorities' → OK")
        print("6. Next → Finish")
        print()
        print("🍎 macOS:")
        print("1. Double-click ca-cert.pem")
        print("2. Add to 'System' keychain")
        print("3. Open Keychain Access")
        print("4. Find 'Local Development CA' → Double-click")
        print("5. Expand 'Trust' → Set to 'Always Trust'")
        print()
        print("🐧 Linux:")
        print("1. sudo cp ca-cert.pem /usr/local/share/ca-certificates/local-dev-ca.crt")
        print("2. sudo update-ca-certificates")
        print()
        print("🌐 Browser Testing:")
        print("After installation, test: https://localhost")
        print("You should see a green lock icon (no security warnings)")
    
    def generate_certificates(self) -> bool:
        """Generate all certificates"""
        print("🔐 SSL Certificate Generator for Local Development")
        print("=" * 60)
        
        try:
            # Check prerequisites
            if not self.check_openssl():
                return False
            
            # Create directories
            self.create_directories()
            
            # Generate certificates
            if not self.create_ca_certificate():
                return False
            
            if not self.create_server_certificate():
                return False
            
            if not self.create_traefik_certificates():
                return False
            
            if not self.create_traefik_config():
                return False
            
            if not self.verify_certificates():
                return False
            
            # Print success message
            print(f"\n🎉 SUCCESS: SSL certificates generated successfully!")
            print(f"📁 Certificates location: {self.certs_dir.absolute()}")
            print(f"📁 Traefik config: {self.traefik_dir.absolute()}")
            
            # Print installation instructions
            self.print_installation_instructions()
            
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️  Certificate generation cancelled by user")
            return False
        except Exception as e:
            print(f"\n💥 Unexpected error: {e}")
            return False


def main():
    """Main function"""
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print(f"Project root: {project_root}")
    
    # Generate certificates
    generator = SSLCertificateGenerator(project_root)
    success = generator.generate_certificates()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()