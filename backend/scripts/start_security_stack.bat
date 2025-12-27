@echo off
REM =============================================================================
REM Windows Batch Wrapper for Security Stack Startup
REM =============================================================================

echo Starting Security Stack...
echo.

REM Check if PowerShell is available
powershell -Command "Get-Host" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PowerShell is not available
    echo Please install PowerShell or run the Python script directly
    pause
    exit /b 1
)

REM Get script directory
set SCRIPT_DIR=%~dp0
set PS_SCRIPT=%SCRIPT_DIR%start_security_stack.ps1

REM Check if PowerShell script exists
if not exist "%PS_SCRIPT%" (
    echo ERROR: PowerShell script not found: %PS_SCRIPT%
    pause
    exit /b 1
)

REM Run PowerShell script with execution policy bypass
echo Running PowerShell script...
powershell -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %*

REM Check exit code
if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: Security stack started successfully!
) else (
    echo.
    echo ERROR: Security stack startup failed
)

echo.
echo Press any key to continue...
pause >nul