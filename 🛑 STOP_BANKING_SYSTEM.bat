@echo off
title 🛑 Banking Reconciliation Engine - Shutdown

echo 🛑 Banking Reconciliation Engine - System Shutdown
echo ================================================
echo.

echo 🔍 Stopping all services...
echo.

REM Stop Docker containers
echo 📦 Stopping Docker containers...
cd backend
docker-compose down
cd ..\kafka  
docker-compose down
cd ..

echo.
echo 🔄 Killing any remaining processes...

REM Kill Python processes (Backend, Consumer, Producer)
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im uvicorn.exe >nul 2>&1

REM Kill Node.js processes (Frontend)
taskkill /f /im node.exe >nul 2>&1

REM Kill any remaining cmd windows with our services
for /f "tokens=2" %%i in ('tasklist /fi "windowtitle eq 🔧 Backend API*" /fo csv ^| find /c /v ""') do if %%i gtr 1 taskkill /f /fi "windowtitle eq 🔧 Backend API*"
for /f "tokens=2" %%i in ('tasklist /fi "windowtitle eq 📨 Kafka Consumer*" /fo csv ^| find /c /v ""') do if %%i gtr 1 taskkill /f /fi "windowtitle eq 📨 Kafka Consumer*"
for /f "tokens=2" %%i in ('tasklist /fi "windowtitle eq 🏭 Transaction Producer*" /fo csv ^| find /c /v ""') do if %%i gtr 1 taskkill /f /fi "windowtitle eq 🏭 Transaction Producer*"
for /f "tokens=2" %%i in ('tasklist /fi "windowtitle eq 🎨 Frontend Dashboard*" /fo csv ^| find /c /v ""') do if %%i gtr 1 taskkill /f /fi "windowtitle eq 🎨 Frontend Dashboard*"

echo.
echo ✅ System shutdown complete!
echo.
echo 📊 What was stopped:
echo    🐳 Docker containers (Kafka, PostgreSQL, Redis)
echo    🔧 Backend API server
echo    📨 Kafka consumer
echo    🏭 Transaction producer  
echo    🎨 React frontend
echo.
echo 💡 To restart the system, run: 🚀 START_BANKING_SYSTEM.bat
echo.
pause