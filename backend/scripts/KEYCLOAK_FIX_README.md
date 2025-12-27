# 🔧 Keycloak Token Validation Fix

## 🚨 The Problem

**Docker Network vs Host Network Mismatch:**

- **Inside Docker**: Backend container sees Keycloak as `http://keycloak:8080`
- **Outside Docker**: Your PowerShell/browser sees Keycloak as `http://localhost:8080`
- **Token Issuer**: Tokens contain `iss: http://localhost:8080/realms/reconciliation`
- **Backend Validation**: Was trying to validate against `http://keycloak:8080/realms/reconciliation`

**Result**: `issuer mismatch` → 401 Unauthorized

## ✅ The Solution

### 1. Environment Variables (.env)

```bash
# Internal Docker URL (container-to-container)
KEYCLOAK_SERVER_URL=http://keycloak:8080

# Public URLs (for token validation - MUST match token issuer)
KEYCLOAK_PUBLIC_ISSUER=http://localhost:8080/realms/reconciliation
KEYCLOAK_PUBLIC_JWKS_URL=http://localhost:8080/realms/reconciliation/protocol/openid-connect/certs

KEYCLOAK_REALM=reconciliation
KEYCLOAK_CLIENT_ID=reconciliation-api
KEYCLOAK_CLIENT_SECRET=reconciliation-api-secret-2024
JWT_ALGORITHM=RS256
JWT_AUDIENCE=reconciliation-api
```

### 2. Updated KeycloakConfig

The `backend/app/security/keycloak_config.py` now:

- ✅ Uses **public JWKS URL** for token signature validation
- ✅ Uses **public issuer** for token issuer validation  
- ✅ Handles both internal and external URLs correctly
- ✅ Provides better error messages

### 3. Updated Scripts

All startup scripts now:

- ✅ Set default public URLs if not provided
- ✅ Use localhost for token generation
- ✅ Handle Docker network differences automatically

## 🧪 Testing the Fix

### Quick Test
```bash
python backend/scripts/test_keycloak_fix.py
```

### Manual Test
```bash
# 1. Get token
curl -X POST "http://localhost:8080/realms/reconciliation/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=reconciliation-api" \
  -d "client_secret=reconciliation-api-secret-2024" \
  -d "username=auditor" \
  -d "password=auditor123"

# 2. Use token (replace <TOKEN> with actual token)
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/health
```

### PowerShell Test
```powershell
# Get token
$resp = Invoke-RestMethod -Uri "http://localhost:8080/realms/reconciliation/protocol/openid-connect/token" `
  -Method Post `
  -ContentType "application/x-www-form-urlencoded" `
  -Body @{
    client_id     = "reconciliation-api"
    client_secret = "reconciliation-api-secret-2024"
    username      = "auditor"
    password      = "auditor123"
    grant_type    = "password"
  }

$token = $resp.access_token

# Test API
Invoke-RestMethod -Uri "http://localhost:8000/health" -Headers @{ "Authorization" = "Bearer $token" }
```

## 🔄 Applying the Fix

### If API is Already Running

```bash
# 1. Rebuild API container with new config
cd backend
docker-compose -f docker-compose.traefik.yml build api

# 2. Restart API container
docker-compose -f docker-compose.traefik.yml restart api

# 3. Test the fix
python scripts/test_keycloak_fix.py
```

### Fresh Start

```bash
# 1. Stop everything
docker-compose -f docker-compose.traefik.yml down

# 2. Start with new config
python scripts/start_security_stack.py

# 3. Test tokens
python scripts/test_tokens.py
```

## 📋 Verification Checklist

- [ ] ✅ Environment variables include public URLs
- [ ] ✅ KeycloakConfig uses public JWKS URL
- [ ] ✅ Token generation works from localhost
- [ ] ✅ API accepts tokens without issuer mismatch
- [ ] ✅ All roles (admin, auditor, operator) work
- [ ] ✅ Error messages are clear and helpful

## 🎯 Expected Results

**Before Fix:**
```json
{
  "status": "error",
  "message": "Token validation error",
  "code": "VALIDATION_ERROR"
}
```

**After Fix:**
```json
{
  "status": "healthy",
  "service": "Banking-Grade Transaction Reconciliation API",
  "version": "1.0.0",
  "timestamp": "2024-12-16T10:30:00Z",
  "security": {...}
}
```

## 🚀 Next Steps

1. **Test all endpoints** with different roles
2. **Verify HTTPS** works in production
3. **Check audit logging** captures token validation
4. **Monitor performance** of JWKS client
5. **Set up token refresh** for long-running sessions

The fix ensures that tokens generated from `localhost:8080` are properly validated by the backend API, resolving the Docker network vs host network mismatch issue.