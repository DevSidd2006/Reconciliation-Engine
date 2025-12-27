# Backend Setup with Virtual Environment

## Initial Setup (One-time)

### 1. Create Virtual Environment
```bash
cd backend
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```bash
.\venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Backend

### Start the Server (with virtual environment)

**Option 1: Activate first, then run**
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start server
uvicorn app.main:app --reload --port 8000
```

**Option 2: Run directly with venv Python**
```bash
# From backend directory
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

**Option 3: Use full path to uvicorn**
```bash
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

## Verify Installation

Check if virtual environment is activated:
```bash
# Should show path to venv
where python
```

Check installed packages:
```bash
pip list
```

## Deactivate Virtual Environment

When you're done:
```bash
deactivate
```

## Quick Start Commands

**Start Backend (from project root):**
```bash
cd backend
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

**Start Frontend (from project root):**
```bash
cd frontend
npm run dev
```

## Troubleshooting

### Virtual environment not found
- Make sure you're in the `backend` directory
- Run `python -m venv venv` to create it

### Module not found errors
- Activate virtual environment
- Run `pip install -r requirements.txt`

### Port already in use
- Kill the process using port 8000
- Or use a different port: `--port 8001`

### PowerShell execution policy error
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Environment Structure

```
backend/
├── venv/                    # Virtual environment (gitignored)
│   ├── Scripts/            # Windows executables
│   ├── Lib/                # Python packages
│   └── ...
├── app/                     # Application code
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Adding New Dependencies

1. Activate virtual environment
2. Install package: `pip install package-name`
3. Update requirements: `pip freeze > requirements.txt`

## Security Stack Automation

### Automated Full Stack Startup

The project includes automated scripts to start the complete security stack with:
- Keycloak (Identity Provider)
- Traefik (HTTPS Reverse Proxy)
- Backend API
- Redis Cache
- PostgreSQL Database
- Automatic realm import
- Dynamic token generation

### Quick Start - Security Stack

**Windows (Recommended):**
```bash
# From backend directory
scripts\start_security_stack.bat
```

**Cross-Platform Python:**
```bash
# From backend directory
python scripts/start_security_stack.py
```

**PowerShell (Windows):**
```bash
# From backend directory
powershell -ExecutionPolicy Bypass -File scripts/start_security_stack.ps1
```

**Interactive Token Generation:**
```bash
python scripts/start_security_stack.py --interactive
```

### What the Script Does

1. ✅ **Loads environment variables** from `.env`
2. ✅ **Checks Docker availability**
3. ✅ **Starts all services** via docker-compose
4. ✅ **Waits for services** to be healthy
5. ✅ **Imports Keycloak realm** automatically
6. ✅ **Runs database migrations**
7. ✅ **Generates test tokens** for all roles
8. ✅ **Validates all services** are working

### After Startup

Once the script completes, you'll have:

- **Keycloak Admin**: http://localhost:8080
- **API Endpoint**: http://localhost:8000
- **Traefik Dashboard**: http://localhost:8081
- **HTTPS** (if configured): https://your-domain.com
- **Test Tokens**: `tmp/tokens.json`

### Test Users & Roles

The system includes pre-configured test users:

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| admin | admin123 | admin | Full system access |
| auditor | auditor123 | auditor | Read-only audit access |
| operator | operator123 | operator | Transaction operations |
| viewer | viewer123 | viewer | Basic read access |

### Manual Token Generation

Generate tokens separately:
```bash
python scripts/generate_tokens.py
```

Interactive mode:
```bash
python scripts/generate_tokens.py --interactive
```

### Environment Configuration

Ensure your `.env` file contains all required variables:
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `KEYCLOAK_ADMIN_PASSWORD`
- `KEYCLOAK_SERVER_URL`
- `KEYCLOAK_REALM`
- `KEYCLOAK_CLIENT_ID`
- `KEYCLOAK_CLIENT_SECRET`
- `TRAEFIK_DOMAIN`
- `TRAEFIK_EMAIL`

### Troubleshooting

**Docker not running:**
```bash
# Start Docker Desktop or Docker service
```

**Port conflicts:**
```bash
# Stop conflicting services
docker-compose down
```

**Permission errors (Windows):**
```bash
# Run as Administrator or use:
powershell -ExecutionPolicy Bypass -File scripts/start_security_stack.ps1
```

**Keycloak realm import fails:**
- Check `keycloak/realm-export.json` exists
- Verify Keycloak admin credentials in `.env`

## Current Status

✅ Virtual environment created at `backend/venv/`
✅ Security stack automation scripts ready
✅ Cross-platform startup support (Windows/Linux/Mac)
✅ Automated Keycloak realm import
✅ Dynamic token generation
✅ Health checks and validation

### Development Workflow

**Start everything:**
```bash
scripts\start_security_stack.bat
```

**Development mode (API only):**
```bash
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```
