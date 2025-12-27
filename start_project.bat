@echo off
echo 🚀 Banking Reconciliation Engine - Enhanced Automated Startup
echo ==========================================================

echo.
echo 🔍 Pre-flight Checks...

REM Check if Docker is running
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not running
    echo    Please install Docker Desktop and make sure it's running
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo    Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    echo    Please install Node.js 16+ and add it to PATH
    pause
    exit /b 1
)

echo ✅ All prerequisites found

echo.
echo 📦 Installing Missing Dependencies...
cd backend
echo Installing Python docker package...
pip install docker >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Warning: Could not install docker package, continuing anyway...
)

echo.
echo Step 1: Starting Docker Infrastructure...
echo 🐳 Starting Kafka infrastructure...
cd ..\kafka
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Failed to start Kafka infrastructure
    echo    Make sure Docker Desktop is running and try again
    pause
    exit /b 1
)

echo 🐳 Starting Backend infrastructure (PostgreSQL + Redis)...
cd ..\backend
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Failed to start Backend infrastructure
    echo    Check Docker Desktop and try again
    pause
    exit /b 1
)

echo ✅ Docker infrastructure started

echo.
echo Step 2: Waiting for services to initialize...
echo ⏳ Waiting 15 seconds for containers to be ready...
timeout /t 15 /nobreak

echo.
echo Step 3: Verifying Docker containers...
echo 📊 Container Status:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

echo Step 4: Starting Backend API Server...
echo 🚀 Starting Backend API in new window...
start "🔧 Backend API (Port 8002)" cmd /k "cd /d %cd% && echo 🚀 Starting Backend API Server... && python -m uvicorn app.main_simple:app --port 8002 --reload"

echo.
echo Step 5: Waiting for Backend API to start...
echo ⏳ Waiting 8 seconds for API server...
timeout /t 8 /nobreak

echo.
echo Step 6: Starting Kafka Consumer...
echo 📨 Starting Consumer in new window...
start "📨 Kafka Consumer" cmd /k "cd /d %cd% && echo 📨 Starting Kafka Consumer... && python -m app.consumers.simple_reconciliation_consumer"

echo.
echo Step 7: Waiting for Consumer to initialize...
echo ⏳ Waiting 5 seconds for consumer...
timeout /t 5 /nobreak

echo.
echo Step 8: Starting Transaction Producer...
echo 🏭 Starting Producer in new window...
cd ..\producers
start "🏭 Transaction Producer" cmd /k "cd /d %cd% && echo 🏭 Starting Transaction Producer... && python coordinated_producer.py"

echo.
echo Step 9: Starting Frontend React App...
echo 🎨 Starting Frontend in new window...
cd ..\frontend
start "🎨 Frontend Dashboard (Port 3000)" cmd /k "cd /d %cd% && echo 🎨 Starting React Frontend... && npm start"

echo.
echo Step 10: Final initialization wait...
echo ⏳ Waiting 15 seconds for all services to be ready...
timeout /t 15 /nobreak

echo.
echo ✅ 🎉 ALL SERVICES STARTED SUCCESSFULLY! 🎉
echo ================================================
echo.
echo 🌐 ACCESS POINTS:
echo    📊 Main Dashboard:     http://localhost:3000
echo    🔧 Backend API:        http://localhost:8002  
echo    📚 API Documentation:  http://localhost:8002/docs
echo    🔍 Health Check:       http://localhost:8002/health
echo.
echo 🔐 DEFAULT LOGIN CREDENTIALS:
echo    👤 Username: admin
echo    🔑 Password: admin123
echo.
echo 🎯 FEATURES AVAILABLE:
echo    ✅ Professional Banking Dashboard
echo    ✅ Transaction Reconciliation Tab
echo    ✅ Dark/Light Theme Toggle
echo    ✅ Near Real-time Updates (10s polling)
echo    ✅ Live Transaction Monitoring
echo    ✅ Mismatch Detection & Alerts
echo.
echo 🖥️  RUNNING SERVICES:
echo    🐳 Docker: Kafka + Zookeeper + PostgreSQL + Redis
echo    🔧 Backend: FastAPI Server (Port 8002)
echo    📨 Consumer: Kafka Message Processor
echo    🏭 Producer: Transaction Generator
echo    🎨 Frontend: React Dashboard (Port 3000)
echo.
echo ⚠️  TROUBLESHOOTING:
echo    - If services fail to start, check the individual terminal windows
echo    - Refer to STARTUP_GUIDE.md for detailed instructions
echo    - Check Docker Desktop is running and has enough resources
echo    - Ensure ports 3000, 8002, 9092, 5432, 6379 are available
echo.
echo 🚀 Ready to use! Open http://localhost:3000 in your browser
echo.
pause