@echo off
echo ========================================
echo Banking Reconciliation System Launcher
echo Build Script for Windows
echo ========================================
echo.

echo [1/4] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo ✅ Node.js is installed

echo.
echo [2/4] Installing Electron dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed

echo.
echo [3/4] Building Windows executable...
call npm run build-win
if %errorlevel% neq 0 (
    echo ERROR: Failed to build executable
    pause
    exit /b 1
)
echo ✅ Executable built successfully

echo.
echo [4/4] Build completed!
echo.
echo 📁 Output location: dist\
echo 🚀 Installer: Banking Reconciliation Launcher Setup.exe
echo.
echo The installer is ready for distribution to client machines.
echo Clients only need Docker Desktop installed - no Node.js required!
echo.
pause