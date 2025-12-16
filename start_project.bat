@echo off
echo 🚀 Banking Reconciliation Engine - Automated Startup
echo ================================================

echo.
echo Step 1: Starting Docker Infrastructure...
cd kafka
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Failed to start Kafka infrastructure
    pause
    exit /b 1
)

cd ..\backend
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Failed to start Backend infrastructure
    pause
    exit /b 1
)

echo ✅ Docker infrastructure started

echo.
echo Step 2: Waiting for services to initialize...
timeout /t 10 /nobreak

echo.
echo Step 3: Checking Docker containers...
docker ps
echo.

echo Step 4: Starting Backend API...
echo ⚠️  Starting Backend API in new window...
start "Backend API" cmd /k "cd /d %cd% && python -m uvicorn app.main_simple:app --port 8002 --reload"

echo.
echo Step 5: Waiting for Backend to start...
timeout /t 5 /nobreak

echo.
echo Step 6: Starting Frontend...
echo ⚠️  Starting Frontend in new window...
cd ..\frontend
start "Frontend" cmd /k "cd /d %cd% && npm start"

echo.
echo Step 7: Waiting for Frontend to start...
timeout /t 10 /nobreak

echo.
echo Step 8: Starting Consumer...
echo ⚠️  Starting Consumer in new window...
cd ..\backend
start "Consumer" cmd /k "cd /d %cd% && python -m app.consumers.simple_reconciliation_consumer"

echo.
echo Step 9: Waiting for Consumer to start...
timeout /t 5 /nobreak

echo.
echo Step 10: Starting Producer...
echo ⚠️  Starting Producer in new window...
cd ..\producers
start "Producer" cmd /k "cd /d %cd% && python coordinated_producer.py"

echo.
echo ✅ All services started!
echo.
echo 🌐 Access Points:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8002
echo    API Docs: http://localhost:8002/docs
echo.
echo 🔐 Login Credentials:
echo    Username: admin
echo    Password: admin123
echo.
echo ⚠️  If you see any errors, check the individual terminal windows
echo    and refer to STARTUP_GUIDE.md for troubleshooting
echo.
pause