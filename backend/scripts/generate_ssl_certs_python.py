#!/usr/bin/env python3
"""
Python-based SSL Certificate Generator (No OpenSSL Required)
Generates self-signed certificates using Python cryptography library
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import ipaddress

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
except ImportError:
    print("❌ cryptography library not found. Installing...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'cryptography'])
        from cryptography import x509
        from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        print("✅ cryptography library installed successfully")
    except Exception as e:
        print(f"❌ Failed to install cryptography library: {e}")
        sys.exit(1)


class PythonSSLGenerator:
    """Generate SSL certificates using Python cryptography library"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.certs_dir = project_root / "ssl-certs"
        self.traefik_dir = project_root / "traefik"
        
    def create_directories(self) -> None:
        """Create necessary directories"""
        self.certs_dir.mkdir(exist_ok=True)
        self.traefik_dir.mkdir(exist_ok=True)
        print("✅ Created certificate directories")
    
    def generate_ca_certificate(self) -> tuple:
        """Generate Certificate Authority certificate and key"""
        print("🔐 Generating Certificate Authority (CA)...")
        
        # Generate CA private key
        ca_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
        )
        
        # Create CA certificate
        ca_name = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Development"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Banking Reconciliation"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Development"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Local Development CA"),
        ])
        
        ca_cert = x509.CertificateBuilder().subject_name(
            ca_name
        ).issuer_name(
            ca_name
        ).public_key(
            ca_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                key_cert_sign=True,
                crl_sign=True,
                digital_signature=False,
                key_encipherment=False,
                key_agreement=False,
                content_commitment=False,
                data_encipherment=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).sign(ca_key, hashes.SHA256())
        
        # Save CA certificate and key
        ca_cert_path = self.certs_dir / "ca-cert.pem"
        ca_key_path = self.certs_dir / "ca-key.pem"
        
        with open(ca_cert_path, "wb") as f:
            f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
        
        with open(ca_key_path, "wb") as f:
            f.write(ca_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print(f"✅ CA certificate created: {ca_cert_path}")
        return ca_cert, ca_key
    
    def generate_server_certificate(self, ca_cert, ca_key) -> tuple:
        """Generate server certificate signed by CA"""
        print("🌐 Generating server certificate for localhost...")
        
        # Generate server private key
        server_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create server certificate
        server_name = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Development"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Banking Reconciliation"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "API"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        # Subject Alternative Names
        san_list = [
            x509.DNSName("localhost"),
            x509.DNSName("*.localhost"),
            x509.DNSName("api.localhost"),
            x509.DNSName("auth.localhost"),
            x509.DNSName("traefik.localhost"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            x509.IPAddress(ipaddress.IPv6Address("::1")),
        ]
        
        server_cert = x509.CertificateBuilder().subject_name(
            server_name
        ).issuer_name(
            ca_cert.subject
        ).public_key(
            server_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False,
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                key_cert_sign=False,
                crl_sign=False,
                digital_signature=True,
                key_encipherment=True,
                key_agreement=False,
                content_commitment=True,
                data_encipherment=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([
                ExtendedKeyUsageOID.SERVER_AUTH,
                ExtendedKeyUsageOID.CLIENT_AUTH,
            ]),
            critical=True,
        ).sign(ca_key, hashes.SHA256())
        
        # Save server certificate and key
        server_cert_path = self.certs_dir / "server-cert.pem"
        server_key_path = self.certs_dir / "server-key.pem"
        
        with open(server_cert_path, "wb") as f:
            f.write(server_cert.public_bytes(serialization.Encoding.PEM))
        
        with open(server_key_path, "wb") as f:
            f.write(server_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print(f"✅ Server certificate created: {server_cert_path}")
        return server_cert, server_key
    
    def create_traefik_files(self) -> bool:
        """Create Traefik certificate files and configuration"""
        print("🚛 Creating Traefik certificate files...")
        
        server_cert_path = self.certs_dir / "server-cert.pem"
        server_key_path = self.certs_dir / "server-key.pem"
        
        # Copy to Traefik directory
        traefik_cert = self.traefik_dir / "localhost.crt"
        traefik_key = self.traefik_dir / "localhost.key"
        
        with open(server_cert_path, 'r') as src, open(traefik_cert, 'w') as dst:
            dst.write(src.read())
        
        with open(server_key_path, 'r') as src, open(traefik_key, 'w') as dst:
            dst.write(src.read())
        
        # Create Traefik TLS configuration
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
        
        print(f"✅ Traefik files created:")
        print(f"   Certificate: {traefik_cert}")
        print(f"   Private Key: {traefik_key}")
        print(f"   TLS Config: {traefik_config}")
        
        return True
    
    def print_certificate_info(self, cert) -> None:
        """Print certificate information"""
        print("\n🔍 Certificate Information:")
        print("-" * 40)
        
        # Subject
        subject_attrs = {}
        for attr in cert.subject:
            subject_attrs[attr.oid._name] = attr.value
        print(f"Subject: {subject_attrs}")
        
        # Issuer
        issuer_attrs = {}
        for attr in cert.issuer:
            issuer_attrs[attr.oid._name] = attr.value
        print(f"Issuer: {issuer_attrs}")
        
        # Validity
        print(f"Valid from: {cert.not_valid_before}")
        print(f"Valid until: {cert.not_valid_after}")
        
        # Subject Alternative Names
        try:
            san_ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            san_names = []
            for name in san_ext.value:
                if hasattr(name, 'value'):
                    san_names.append(str(name.value))
                else:
                    san_names.append(str(name))
            print(f"Alt names: {', '.join(san_names)}")
        except x509.ExtensionNotFound:
            pass
    
    def print_installation_instructions(self) -> None:
        """Print CA certificate installation instructions"""
        ca_cert_path = self.certs_dir / "ca-cert.pem"
        
        print(f"\n📋 CERTIFICATE INSTALLATION INSTRUCTIONS")
        print("=" * 60)
        print(f"To avoid browser security warnings, install the CA certificate:")
        print(f"CA Certificate: {ca_cert_path.absolute()}")
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
        print("🔐 Python SSL Certificate Generator")
        print("=" * 60)
        
        try:
            # Create directories
            self.create_directories()
            
            # Generate CA certificate
            ca_cert, ca_key = self.generate_ca_certificate()
            
            # Generate server certificate
            server_cert, server_key = self.generate_server_certificate(ca_cert, ca_key)
            
            # Create Traefik files
            self.create_traefik_files()
            
            # Print certificate info
            self.print_certificate_info(server_cert)
            
            # Success message
            print(f"\n🎉 SUCCESS: SSL certificates generated successfully!")
            print(f"📁 Certificates location: {self.certs_dir.absolute()}")
            print(f"📁 Traefik config: {self.traefik_dir.absolute()}")
            
            # Installation instructions
            self.print_installation_instructions()
            
            return True
            
        except Exception as e:
            print(f"\n💥 Certificate generation failed: {e}")
            return False


def main():
    """Main function"""
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print(f"Project root: {project_root}")
    
    # Generate certificates
    generator = PythonSSLGenerator(project_root)
    success = generator.generate_certificates()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()