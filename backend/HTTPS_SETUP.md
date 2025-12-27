# 🔐 HTTPS Setup with Self-Signed Certificates

This guide explains how to enable HTTPS for local development using self-signed certificates.

## 🚀 Quick Start

### Automatic Setup (Recommended)

```bash
# From backend directory
python scripts/setup_https.py
```

This will:
- ✅ Generate self-signed SSL certificates
- ✅ Configure Traefik for HTTPS
- ✅ Restart services to load certificates
- ✅ Test HTTPS connectivity

### Manual Setup

```bash
# 1. Generate certificates
python scripts/generate_ssl_certs.py

# 2. Restart Traefik
docker-compose -f docker-compose.traefik.yml restart traefik

# 3. Test HTTPS
python scripts/test_https.py
```

## 🌐 Access URLs

After HTTPS setup, your services will be available at:

### HTTPS URLs (Self-Signed)
- **API**: https://localhost/api/
- **API Health**: https://localhost/api/health
- **Traefik Dashboard**: https://localhost/dashboard/
- **Keycloak**: https://localhost/auth/

### HTTP URLs (Development)
- **API**: http://localhost:8000/
- **Keycloak**: http://localhost:8082/
- **Traefik Dashboard**: http://localhost:8081/

## 🔧 Configuration

### Environment Variables

```bash
# Enable HTTPS
ENABLE_HTTPS=true
TRAEFIK_DOMAIN=localhost
TRAEFIK_EMAIL=admin@localhost
```

### Generated Files

```
backend/
├── ssl-certs/           # SSL certificates
│   ├── ca-cert.pem     # Certificate Authority (install this)
│   ├── ca-key.pem      # CA private key
│   ├── server-cert.pem # Server certificate
│   └── server-key.pem  # Server private key
├── traefik/            # Traefik configuration
│   ├── localhost.crt   # Certificate for Traefik
│   ├── localhost.key   # Private key for Traefik
│   └── tls.yml         # TLS configuration
```

## 🛡️ Security Features

### Certificate Details
- **Algorithm**: RSA 2048-bit
- **Validity**: 365 days
- **Subject**: CN=localhost
- **SAN**: localhost, 127.0.0.1, *.localhost

### TLS Configuration
- **Protocols**: TLS 1.2, TLS 1.3
- **Cipher Suites**: Strong encryption only
- **HSTS**: Enabled
- **Security Headers**: Comprehensive set

## 🔍 Browser Setup

### Avoiding Security Warnings

Your browser will show security warnings for self-signed certificates. You have two options:

#### Option 1: Accept Warning (Quick)
1. Navigate to https://localhost/api/health
2. Click "Advanced" or "Show Details"
3. Click "Proceed to localhost (unsafe)"

#### Option 2: Install CA Certificate (Recommended)
Install the CA certificate to avoid warnings:

**Windows:**
1. Double-click `backend/ssl-certs/ca-cert.pem`
2. Click "Install Certificate"
3. Choose "Local Machine" → Next
4. Select "Place all certificates in the following store"
5. Browse → "Trusted Root Certification Authorities" → OK
6. Next → Finish

**macOS:**
1. Double-click `backend/ssl-certs/ca-cert.pem`
2. Add to "System" keychain
3. Open Keychain Access
4. Find "Local Development CA" → Double-click
5. Expand "Trust" → Set to "Always Trust"

**Linux:**
```bash
sudo cp backend/ssl-certs/ca-cert.pem /usr/local/share/ca-certificates/local-dev-ca.crt
sudo update-ca-certificates
```

## 🧪 Testing

### Test HTTPS Connectivity
```bash
python scripts/test_https.py
```

### Test with curl
```bash
# With certificate verification (after installing CA)
curl https://localhost/api/health

# Skip certificate verification
curl -k https://localhost/api/health
```

### Test with Browser
1. Navigate to https://localhost/api/health
2. Should see JSON response with API health status

## 🔄 Traefik Configuration

### Docker Compose Changes

The `docker-compose.traefik.yml` has been updated to:

1. **Remove Let's Encrypt**: No longer uses ACME/Let's Encrypt
2. **Add File Provider**: Loads TLS config from `traefik/tls.yml`
3. **Mount Certificates**: Certificates available in `/etc/traefik/certs/`
4. **Localhost Routing**: Routes configured for `localhost` domain

### TLS Configuration

The `traefik/tls.yml` file configures:

```yaml
tls:
  certificates:
    - certFile: /etc/traefik/certs/localhost.crt
      keyFile: /etc/traefik/certs/localhost.key
  options:
    default:
      sslProtocols: ["TLSv1.2", "TLSv1.3"]
      minVersion: "VersionTLS12"
```

## 🚨 Troubleshooting

### Certificate Generation Fails

**Problem**: OpenSSL not found
```bash
# Windows
winget install OpenSSL.Light
# Or download from: https://slproweb.com/products/Win32OpenSSL.html

# macOS
brew install openssl

# Linux
sudo apt-get install openssl
```

### HTTPS Not Working

**Check Traefik Status:**
```bash
docker logs reconciliation_traefik
```

**Check Certificate Files:**
```bash
ls -la backend/traefik/
# Should see: localhost.crt, localhost.key, tls.yml
```

**Restart Services:**
```bash
docker-compose -f docker-compose.traefik.yml restart traefik
```

### Browser Still Shows Warnings

1. **Clear Browser Cache**: Hard refresh (Ctrl+F5)
2. **Check CA Installation**: Verify CA certificate is installed
3. **Try Incognito Mode**: Test in private browsing
4. **Check Certificate**: Use browser dev tools → Security tab

### Port Conflicts

If port 443 is in use:
```bash
# Check what's using port 443
netstat -ano | findstr :443

# Stop conflicting service or change Traefik port
```

## 📋 Integration with API

### Token Authentication with HTTPS

```bash
# Get token
TOKEN=$(curl -k -X POST "https://localhost/auth/realms/reconciliation/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&client_id=reconciliation-api&client_secret=reconciliation-api-secret-2024&username=admin&password=admin123" \
  | jq -r '.access_token')

# Use token with HTTPS API
curl -k -H "Authorization: Bearer $TOKEN" https://localhost/api/health
```

### Update Client Applications

Update your frontend or client applications to use HTTPS URLs:

```javascript
// Before
const API_BASE = 'http://localhost:8000';

// After
const API_BASE = 'https://localhost/api';
```

## 🎯 Production Considerations

⚠️ **This setup is for development only!**

For production:
1. Use real SSL certificates (Let's Encrypt, commercial CA)
2. Use proper domain names (not localhost)
3. Enable certificate validation
4. Use production-grade TLS configuration
5. Implement proper certificate rotation

## 📚 Additional Resources

- [Traefik TLS Documentation](https://doc.traefik.io/traefik/https/tls/)
- [OpenSSL Certificate Guide](https://www.openssl.org/docs/man1.1.1/man1/openssl-req.html)
- [Self-Signed Certificate Best Practices](https://security.stackexchange.com/questions/8110/what-are-the-differences-between-ssl-tls-certificates)

---

🎉 **Your banking reconciliation system now supports HTTPS for secure local development!**