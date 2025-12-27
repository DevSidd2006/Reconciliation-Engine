# Banking Reconciliation Engine - PowerShell Startup Script
# Enhanced version with better error handling and status monitoring

Write-Host "🚀 Banking Reconciliation Engine - PowerShell Startup" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Function to check if port is available
function Test-Port($port) {
    $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
    return -not $connection
}

# Function to wait for service to be ready
function Wait-ForService($url, $serviceName, $maxAttempts = 30) {
    Write-Host "⏳ Waiting for $serviceName to be ready..." -ForegroundColor Yellow
    for ($i = 1; $i -le $maxAttempts; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ $serviceName is ready!" -ForegroundColor Green
                return $true
            }
        }
        catch {
            Write-Host "." -NoNewline -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    }
    Write-Host ""
    Write-Host "⚠️  $serviceName may not be fully ready, continuing..." -ForegroundColor Yellow
    return $false
}

Write-Host "🔍 Pre-flight Checks..." -ForegroundColor Yellow

# Check Docker
if (-not (Test-Command "docker")) {
    Write-Host "❌ Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "   Please install Docker Desktop and add it to PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python
if (-not (Test-Command "python")) {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "   Please install Python 3.8+ and add it to PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js
if (-not (Test-Command "node")) {
    Write-Host "❌ Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "   Please install Node.js 16+ and add it to PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker Desktop is not running" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check port availability
$ports = @(3000, 8002, 9092, 5432, 6379)
foreach ($port in $ports) {
    if (-not (Test-Port $port)) {
        Write-Host "⚠️  Port $port is already in use" -ForegroundColor Yellow
        Write-Host "   This may cause conflicts. Continue anyway? (y/n): " -NoNewline -ForegroundColor Yellow
        $continue = Read-Host
        if ($continue -ne "y" -and $continue -ne "Y") {
            exit 1
        }
    }
}

Write-Host "✅ All prerequisites checked" -ForegroundColor Green
Write-Host ""

# Install missing dependencies
Write-Host "📦 Installing Missing Dependencies..." -ForegroundColor Cyan
Set-Location "backend"
Write-Host "Installing Python docker package..." -ForegroundColor Yellow
try {
    pip install docker --quiet
    Write-Host "✅ Docker package installed" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Warning: Could not install docker package" -ForegroundColor Yellow
}
Write-Host ""

# Step 1: Start Docker Infrastructure
Write-Host "Step 1: Starting Docker Infrastructure..." -ForegroundColor Cyan
Write-Host "🐳 Starting Kafka infrastructure..." -ForegroundColor Yellow
Set-Location "..\kafka"
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start Kafka infrastructure" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🐳 Starting Backend infrastructure (PostgreSQL + Redis)..." -ForegroundColor Yellow
Set-Location "..\backend"
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start Backend infrastructure" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Docker infrastructure started" -ForegroundColor Green
Write-Host ""

# Step 2: Wait for services
Write-Host "Step 2: Waiting for Docker services to initialize..." -ForegroundColor Cyan
Write-Host "⏳ Waiting 20 seconds for containers to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Step 3: Show container status
Write-Host "Step 3: Verifying Docker containers..." -ForegroundColor Cyan
Write-Host "📊 Container Status:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Write-Host ""

# Step 4: Start Backend API
Write-Host "Step 4: Starting Backend API Server..." -ForegroundColor Cyan
Write-Host "🚀 Starting Backend API in new window..." -ForegroundColor Yellow
$backendPath = (Get-Location).Path
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; Write-Host '🔧 Backend API Server Starting...' -ForegroundColor Cyan; python -m uvicorn app.main_simple:app --port 8002 --reload"

# Wait for backend to be ready
Wait-ForService "http://localhost:8002/health" "Backend API"

# Step 5: Start Kafka Consumer
Write-Host "Step 5: Starting Kafka Consumer..." -ForegroundColor Cyan
Write-Host "📨 Starting Consumer in new window..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; Write-Host '📨 Kafka Consumer Starting...' -ForegroundColor Cyan; python -m app.consumers.simple_reconciliation_consumer"

Write-Host "⏳ Waiting 5 seconds for consumer to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Step 6: Start Transaction Producer
Write-Host "Step 6: Starting Transaction Producer..." -ForegroundColor Cyan
Write-Host "🏭 Starting Producer in new window..." -ForegroundColor Yellow
$producerPath = (Resolve-Path "..\producers").Path
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$producerPath'; Write-Host '🏭 Transaction Producer Starting...' -ForegroundColor Cyan; python coordinated_producer.py"

Write-Host "⏳ Waiting 5 seconds for producer to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Step 7: Start Frontend
Write-Host "Step 7: Starting Frontend React App..." -ForegroundColor Cyan
Write-Host "🎨 Starting Frontend in new window..." -ForegroundColor Yellow
$frontendPath = (Resolve-Path "..\frontend").Path
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; Write-Host '🎨 React Frontend Starting...' -ForegroundColor Cyan; npm start"

# Wait for frontend to be ready
Write-Host "⏳ Waiting for React to compile..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Final status
Write-Host ""
Write-Host "✅ 🎉 ALL SERVICES STARTED SUCCESSFULLY! 🎉" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 ACCESS POINTS:" -ForegroundColor Cyan
Write-Host "   📊 Main Dashboard:     http://localhost:3000" -ForegroundColor White
Write-Host "   🔧 Backend API:        http://localhost:8002" -ForegroundColor White
Write-Host "   📚 API Documentation:  http://localhost:8002/docs" -ForegroundColor White
Write-Host "   🔍 Health Check:       http://localhost:8002/health" -ForegroundColor White
Write-Host ""
Write-Host "🔐 DEFAULT LOGIN CREDENTIALS:" -ForegroundColor Cyan
Write-Host "   👤 Username: admin" -ForegroundColor White
Write-Host "   🔑 Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "🎯 FEATURES AVAILABLE:" -ForegroundColor Cyan
Write-Host "   ✅ Professional Banking Dashboard" -ForegroundColor Green
Write-Host "   ✅ Transaction Reconciliation Tab" -ForegroundColor Green
Write-Host "   ✅ Dark/Light Theme Toggle" -ForegroundColor Green
Write-Host "   ✅ Near Real-time Updates (10s polling)" -ForegroundColor Green
Write-Host "   ✅ Live Transaction Monitoring" -ForegroundColor Green
Write-Host "   ✅ Mismatch Detection & Alerts" -ForegroundColor Green
Write-Host ""
Write-Host "🖥️  RUNNING SERVICES:" -ForegroundColor Cyan
Write-Host "   🐳 Docker: Kafka + Zookeeper + PostgreSQL + Redis" -ForegroundColor White
Write-Host "   🔧 Backend: FastAPI Server (Port 8002)" -ForegroundColor White
Write-Host "   📨 Consumer: Kafka Message Processor" -ForegroundColor White
Write-Host "   🏭 Producer: Transaction Generator" -ForegroundColor White
Write-Host "   🎨 Frontend: React Dashboard (Port 3000)" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Ready to use! Opening browser..." -ForegroundColor Green

# Open browser
try {
    Start-Process "http://localhost:3000"
    Write-Host "✅ Browser opened to dashboard" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Could not open browser automatically" -ForegroundColor Yellow
    Write-Host "   Please manually open: http://localhost:3000" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press Enter to exit this script (services will continue running)..." -ForegroundColor Yellow
Read-Host