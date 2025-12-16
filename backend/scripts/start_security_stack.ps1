# =============================================================================
# AUTOMATED SECURITY STACK STARTUP SCRIPT (Windows PowerShell)
# =============================================================================
# This script starts the complete security stack with:
# - Keycloak (Identity Provider)
# - Traefik (HTTPS Reverse Proxy)
# - Backend API
# - Redis Cache
# - PostgreSQL Database
# - Automatic realm import
# - Dynamic token generation
# =============================================================================

param(
    [switch]$Interactive,
    [string]$EnvFile = ".env"
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"

# Script paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$TokensDir = Join-Path $ProjectRoot "tmp"

# Logging functions
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Blue
}

function Write-Error-Log {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning-Log {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

# Load environment variables
function Load-Environment {
    $envPath = Join-Path $ProjectRoot $EnvFile
    
    if (-not (Test-Path $envPath)) {
        Write-Error-Log "Environment file not found: $envPath"
        exit 1
    }
    
    Write-Log "Loading environment variables from $envPath"
    
    # Read and parse .env file
    Get-Content $envPath | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            # Remove quotes if present
            $value = $value -replace '^["'']|["'']$', ''
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
    
    # Validate required variables
    $requiredVars = @(
        "POSTGRES_PASSWORD",
        "REDIS_PASSWORD", 
        "KEYCLOAK_ADMIN_PASSWORD",
        "KEYCLOAK_SERVER_URL",
        "KEYCLOAK_REALM",
        "KEYCLOAK_CLIENT_ID",
        "KEYCLOAK_CLIENT_SECRET",
        "TRAEFIK_DOMAIN",
        "TRAEFIK_EMAIL"
    )
    
    foreach ($var in $requiredVars) {
        if (-not [Environment]::GetEnvironmentVariable($var)) {
            Write-Error-Log "Required environment variable not set: $var"
            exit 1
        }
    }
    
    Write-Success "Environment variables loaded successfully"
}

# Check if Docker is running
function Test-Docker {
    Write-Log "Checking Docker availability..."
    
    try {
        $null = docker info 2>$null
        Write-Success "Docker is running"
        return $true
    }
    catch {
        Write-Error-Log "Docker is not running or not accessible"
        return $false
    }
}

# Get container status
function Get-ContainerStatus {
    param([string]$ContainerName)
    
    $running = docker ps -q -f "name=$ContainerName" 2>$null
    if ($running) {
        return "running"
    }
    
    $exists = docker ps -aq -f "name=$ContainerName" 2>$null
    if ($exists) {
        return "stopped"
    }
    
    return "not_exists"
}

# Wait for service to be ready
function Wait-ForService {
    param(
        [string]$ServiceName,
        [string]$Url,
        [int]$MaxAttempts = 30,
        [int]$SleepTime = 5
    )
    
    Write-Log "Waiting for $ServiceName to be ready at $Url..."
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Success "$ServiceName is ready!"
                return $true
            }
        }
        catch {
            # Service not ready yet
        }
        
        if ($i -eq $MaxAttempts) {
            Write-Error-Log "$ServiceName failed to start after $($MaxAttempts * $SleepTime) seconds"
            return $false
        }
        
        Write-Log "Attempt $i/$MaxAttempts`: $ServiceName not ready yet, waiting ${SleepTime}s..."
        Start-Sleep -Seconds $SleepTime
    }
    
    return $false
}

# Wait for database to be ready
function Wait-ForDatabase {
    Write-Log "Waiting for PostgreSQL to be ready..."
    
    for ($i = 1; $i -le 30; $i++) {
        try {
            $result = docker exec reconciliation_postgres pg_isready -U postgres 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "PostgreSQL is ready!"
                return $true
            }
        }
        catch {
            # Database not ready yet
        }
        
        if ($i -eq 30) {
            Write-Error-Log "PostgreSQL failed to start after 60 seconds"
            return $false
        }
        
        Write-Log "Attempt $i/30: PostgreSQL not ready yet, waiting 2s..."
        Start-Sleep -Seconds 2
    }
    
    return $false
}

# Create necessary directories
function New-Directories {
    Write-Log "Creating necessary directories..."
    
    if (-not (Test-Path $TokensDir)) {
        New-Item -ItemType Directory -Path $TokensDir -Force | Out-Null
    }
    
    $letsencryptDir = Join-Path $ProjectRoot "letsencrypt"
    if (-not (Test-Path $letsencryptDir)) {
        New-Item -ItemType Directory -Path $letsencryptDir -Force | Out-Null
    }
    
    Write-Success "Directories created"
}

# Start Docker Compose services
function Start-Services {
    Write-Log "Starting Docker Compose services..."
    
    Set-Location $ProjectRoot
    
    # Check if services are already running
    $containers = @("reconciliation_postgres", "reconciliation_redis", "reconciliation_keycloak", "reconciliation_traefik", "reconciliation_api")
    $servicesRunning = $true
    
    foreach ($container in $containers) {
        $status = Get-ContainerStatus $container
        if ($status -ne "running") {
            $servicesRunning = $false
            break
        }
    }
    
    if ($servicesRunning) {
        Write-Warning-Log "All services are already running, skipping Docker Compose start"
    }
    else {
        Write-Log "Starting services with docker-compose..."
        docker-compose -f docker-compose.traefik.yml up -d
        if ($LASTEXITCODE -ne 0) {
            Write-Error-Log "Failed to start Docker Compose services"
            exit 1
        }
        Write-Success "Docker Compose services started"
    }
}

# Run database migrations
function Invoke-Migrations {
    Write-Log "Running database migrations..."
    
    $apiStatus = Get-ContainerStatus "reconciliation_api"
    if ($apiStatus -ne "running") {
        Write-Error-Log "API container is not running, cannot run migrations"
        return $false
    }
    
    try {
        docker exec reconciliation_api alembic upgrade head
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Database migrations completed successfully"
            return $true
        }
        else {
            Write-Warning-Log "Migration command failed or no migrations to run"
            return $true  # Don't fail the entire process
        }
    }
    catch {
        Write-Warning-Log "Migration command failed: $_"
        return $true  # Don't fail the entire process
    }
}

# Check if Keycloak realm exists
function Test-RealmExists {
    param(
        [string]$KeycloakUrl,
        [string]$Realm
    )
    
    Write-Log "Checking if realm '$Realm' exists..."
    
    try {
        # Get admin token
        $tokenBody = @{
            username = [Environment]::GetEnvironmentVariable("KEYCLOAK_ADMIN")
            password = [Environment]::GetEnvironmentVariable("KEYCLOAK_ADMIN_PASSWORD")
            grant_type = "password"
            client_id = "admin-cli"
        }
        
        $tokenResponse = Invoke-RestMethod -Uri "$KeycloakUrl/realms/master/protocol/openid-connect/token" -Method Post -Body $tokenBody -ContentType "application/x-www-form-urlencoded" -TimeoutSec 10
        $adminToken = $tokenResponse.access_token
        
        if (-not $adminToken) {
            Write-Error-Log "Failed to get admin token from Keycloak"
            return $false
        }
        
        # Check if realm exists
        $headers = @{ Authorization = "Bearer $adminToken" }
        $response = Invoke-WebRequest -Uri "$KeycloakUrl/admin/realms/$Realm" -Method Get -Headers $headers -TimeoutSec 10 -UseBasicParsing -ErrorAction SilentlyContinue
        
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

# Import Keycloak realm
function Import-Realm {
    $keycloakUrl = [Environment]::GetEnvironmentVariable("KEYCLOAK_SERVER_URL")
    $realm = [Environment]::GetEnvironmentVariable("KEYCLOAK_REALM")
    
    if (Test-RealmExists $keycloakUrl $realm) {
        Write-Success "Realm '$realm' already exists, skipping import"
        return $true
    }
    
    Write-Log "Importing Keycloak realm '$realm'..."
    
    try {
        # Get admin token
        $tokenBody = @{
            username = [Environment]::GetEnvironmentVariable("KEYCLOAK_ADMIN")
            password = [Environment]::GetEnvironmentVariable("KEYCLOAK_ADMIN_PASSWORD")
            grant_type = "password"
            client_id = "admin-cli"
        }
        
        $tokenResponse = Invoke-RestMethod -Uri "$keycloakUrl/realms/master/protocol/openid-connect/token" -Method Post -Body $tokenBody -ContentType "application/x-www-form-urlencoded" -TimeoutSec 10
        $adminToken = $tokenResponse.access_token
        
        if (-not $adminToken) {
            Write-Error-Log "Failed to get admin token for realm import"
            return $false
        }
        
        # Import realm from JSON file
        $realmFile = Join-Path $ProjectRoot "keycloak\realm-export.json"
        if (-not (Test-Path $realmFile)) {
            Write-Error-Log "Realm export file not found: $realmFile"
            return $false
        }
        
        $realmJson = Get-Content $realmFile -Raw
        $headers = @{
            Authorization = "Bearer $adminToken"
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-WebRequest -Uri "$keycloakUrl/admin/realms" -Method Post -Headers $headers -Body $realmJson -TimeoutSec 30 -UseBasicParsing -ErrorAction SilentlyContinue
        
        if ($response.StatusCode -eq 201) {
            Write-Success "Realm '$realm' imported successfully"
            return $true
        }
        else {
            Write-Error-Log "Failed to import realm (HTTP $($response.StatusCode))"
            return $false
        }
    }
    catch {
        Write-Error-Log "Failed to import realm: $_"
        return $false
    }
}

# Generate test tokens
function New-TestTokens {
    Write-Log "Generating test access tokens..."
    
    $pythonScript = Join-Path $ScriptDir "generate_tokens.py"
    if (-not (Test-Path $pythonScript)) {
        Write-Error-Log "Token generation script not found: $pythonScript"
        return $false
    }
    
    try {
        if ($Interactive) {
            python $pythonScript --interactive
        }
        else {
            python $pythonScript
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Test tokens generated successfully"
            return $true
        }
        else {
            Write-Error-Log "Failed to generate test tokens"
            return $false
        }
    }
    catch {
        Write-Error-Log "Failed to run token generation script: $_"
        return $false
    }
}

# Validate services
function Test-Services {
    Write-Log "Validating all services..."
    
    $keycloakUrl = [Environment]::GetEnvironmentVariable("KEYCLOAK_SERVER_URL")
    $realm = [Environment]::GetEnvironmentVariable("KEYCLOAK_REALM")
    $domain = [Environment]::GetEnvironmentVariable("TRAEFIK_DOMAIN")
    if (-not $domain) { $domain = "localhost" }
    
    # Check Keycloak
    if (-not (Wait-ForService "Keycloak" "$keycloakUrl/realms/$realm" 10 3)) {
        Write-Error-Log "Keycloak validation failed"
        return $false
    }
    
    # Check if HTTPS is enabled
    $enableHttps = [Environment]::GetEnvironmentVariable("ENABLE_HTTPS")
    if ($enableHttps -eq "true") {
        Write-Log "Validating HTTPS configuration..."
        try {
            $response = Invoke-WebRequest -Uri "https://$domain" -Method Get -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Success "HTTPS is active"
            }
            else {
                Write-Warning-Log "HTTPS validation failed - this is normal for local development"
            }
        }
        catch {
            Write-Warning-Log "HTTPS validation failed - this is normal for local development"
        }
    }
    
    # Check API endpoint
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Success "API endpoint is responding"
        }
        else {
            Write-Warning-Log "API health check failed"
        }
    }
    catch {
        Write-Warning-Log "API health check failed"
    }
    
    Write-Success "Service validation completed"
    return $true
}

# Print final status
function Show-Status {
    $domain = [Environment]::GetEnvironmentVariable("TRAEFIK_DOMAIN")
    if (-not $domain) { $domain = "localhost" }
    
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor $Green
    Write-Host "SECURE STACK READY" -ForegroundColor $Green
    Write-Host "============================================================================" -ForegroundColor $Green
    
    $enableHttps = [Environment]::GetEnvironmentVariable("ENABLE_HTTPS")
    if ($enableHttps -eq "true") {
        Write-Host "HTTPS active at: " -NoNewline
        Write-Host "https://$domain" -ForegroundColor $Blue
    }
    else {
        Write-Host "HTTP active at: " -NoNewline  
        Write-Host "http://$domain" -ForegroundColor $Blue
    }
    
    Write-Host "Keycloak admin: " -NoNewline
    Write-Host "http://localhost:8080" -ForegroundColor $Blue
    
    Write-Host "API endpoint: " -NoNewline
    Write-Host "http://localhost:8000" -ForegroundColor $Blue
    
    Write-Host "Traefik dashboard: " -NoNewline
    Write-Host "http://localhost:8081" -ForegroundColor $Blue
    
    Write-Host "Tokens stored at: " -NoNewline
    Write-Host "$TokensDir\tokens.json" -ForegroundColor $Blue
    
    Write-Host ""
    Write-Host "Services running:"
    Write-Host "  - PostgreSQL (internal)"
    Write-Host "  - Redis (internal)"
    Write-Host "  - Keycloak (port 8080)"
    Write-Host "  - Traefik (ports 80, 443, 8081)"
    Write-Host "  - Backend API (port 8000)"
    Write-Host "============================================================================" -ForegroundColor $Green
}

# Main execution
function Main {
    Write-Log "Starting automated security stack deployment..."
    
    try {
        # Pre-flight checks
        Load-Environment
        if (-not (Test-Docker)) { exit 1 }
        New-Directories
        
        # Start services
        Start-Services
        
        # Wait for core services
        if (-not (Wait-ForDatabase)) { exit 1 }
        # Redis might not respond to HTTP, so we skip the check
        if (-not (Wait-ForService "Keycloak" ([Environment]::GetEnvironmentVariable("KEYCLOAK_SERVER_URL")) 30 5)) { exit 1 }
        
        # Configure Keycloak
        if (-not (Import-Realm)) { exit 1 }
        
        # Start API and run migrations
        if (-not (Wait-ForService "API" "http://localhost:8000/health" 20 3)) { exit 1 }
        Invoke-Migrations | Out-Null
        
        # Generate tokens
        if (-not (New-TestTokens)) { exit 1 }
        
        # Final validation
        if (-not (Test-Services)) { exit 1 }
        
        # Print status
        Show-Status
        
        Write-Success "Security stack startup completed successfully!"
    }
    catch {
        Write-Error-Log "Script failed: $_"
        exit 1
    }
}

# Run main function
Main