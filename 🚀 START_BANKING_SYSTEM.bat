@echo off
REM ===================================================================
REM 🏦 Banking Reconciliation Engine - One-Click Startup
REM ===================================================================
REM This script starts the complete banking reconciliation system
REM Just double-click this file to launch everything!
REM ===================================================================

title 🏦 Banking Reconciliation Engine Launcher

REM Check if we're in the right directory
if not exist "backend" (
    echo ❌ Error: This script must be run from the project root directory
    echo    Make sure you're in the Reconciliation-Engine folder
    pause
    exit /b 1
)

REM Try PowerShell version first (better features)
where powershell >nul 2>&1
if %errorlevel% equ 0 (
    echo 🚀 Launching enhanced PowerShell startup...
    powershell -ExecutionPolicy Bypass -File "start_project.ps1"
) else (
    echo 🚀 Launching batch startup...
    call start_project.bat
)

REM Keep window open if there were any issues
if %errorlevel% neq 0 (
    echo.
    echo ❌ Startup encountered issues. Check the error messages above.
    pause
)