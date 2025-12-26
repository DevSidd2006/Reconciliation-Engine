# 🚀 Banking Reconciliation Engine - Startup Options

## 📋 **Available Startup Methods**

### 🎯 **Method 1: One-Click Launcher (Easiest)**
**File**: `🚀 START_BANKING_SYSTEM.bat`
- ✅ **Just double-click** to start everything
- ✅ Automatically detects PowerShell support
- ✅ Falls back to batch if needed
- ✅ Best for beginners

### 🔧 **Method 2: Enhanced PowerShell (Recommended)**
**File**: `start_project.ps1`
- ✅ Advanced error checking
- ✅ Port availability checks
- ✅ Service health monitoring
- ✅ Colored output and progress indicators
- ✅ Automatic browser opening
- ✅ Better dependency management

**Usage**:
```powershell
powershell -ExecutionPolicy Bypass -File start_project.ps1
```

### 📦 **Method 3: Standard Batch Script**
**File**: `start_project.bat`
- ✅ Works on all Windows systems
- ✅ No PowerShell required
- ✅ Enhanced error handling
- ✅ Dependency installation
- ✅ Comprehensive status reporting

**Usage**:
```cmd
start_project.bat
```

### 🛑 **System Shutdown**
**File**: `🛑 STOP_BANKING_SYSTEM.bat`
- ✅ Stops all Docker containers
- ✅ Kills all related processes
- ✅ Clean system shutdown
- ✅ Safe to run anytime

## 🔍 **What Each Startup Method Does**

### **Pre-flight Checks**
- ✅ Verifies Docker is installed and running
- ✅ Checks Python availability
- ✅ Checks Node.js availability
- ✅ Tests port availability (3000, 8002, 9092, 5432, 6379)
- ✅ Installs missing Python dependencies

### **Infrastructure Startup**
1. **Kafka Infrastructure** (docker-compose)
   - Kafka broker
   - Zookeeper
   - Schema Registry

2. **Backend Infrastructure** (docker-compose)
   - PostgreSQL database
   - Redis cache

### **Application Services**
3. **Backend API Server** (Port 8002)
   - FastAPI application
   - Health checks enabled
   - Auto-reload for development

4. **Kafka Consumer**
   - Processes transactions from 3 topics
   - Real-time reconciliation
   - Database storage

5. **Transaction Producer**
   - Generates coordinated transactions
   - Multiple source simulation
   - Configurable mismatch rates

6. **Frontend Dashboard** (Port 3000)
   - React application
   - Professional banking UI
   - Real-time updates

## 🌐 **Access Points After Startup**

| Service | URL | Description |
|---------|-----|-------------|
| **Main Dashboard** | http://localhost:3000 | Professional banking interface |
| **Backend API** | http://localhost:8002 | REST API endpoints |
| **API Documentation** | http://localhost:8002/docs | Interactive Swagger docs |
| **Health Check** | http://localhost:8002/health | System health status |

## 🔐 **Default Credentials**

```
Username: admin
Password: admin123
```

## 🎯 **Features Available**

- ✅ **Professional Banking Dashboard**
- ✅ **Transaction Reconciliation Tab**
- ✅ **Dark/Light Theme Toggle**
- ✅ **Near Real-time Updates** (10-second polling)
- ✅ **Live Transaction Monitoring**
- ✅ **Mismatch Detection & Alerts**
- ✅ **Indian Rupee Currency Formatting**
- ✅ **Professional Sidebar Navigation**

## 🛠️ **Troubleshooting**

### **Common Issues**

1. **Docker not running**
   - Start Docker Desktop
   - Wait for it to fully initialize

2. **Port conflicts**
   - Check if ports are already in use
   - Stop conflicting services
   - Use `🛑 STOP_BANKING_SYSTEM.bat` first

3. **Python dependencies missing**
   - Scripts auto-install missing packages
   - Manually run: `pip install docker`

4. **Node.js issues**
   - Ensure Node.js 16+ is installed
   - Run `npm install` in frontend folder

### **Manual Cleanup**
If automated scripts fail:
```cmd
# Stop Docker containers
cd backend && docker-compose down
cd ../kafka && docker-compose down

# Kill processes
taskkill /f /im python.exe
taskkill /f /im node.exe
```

## 📊 **System Requirements**

### **Minimum Requirements**
- Windows 10/11
- Docker Desktop
- Python 3.8+
- Node.js 16+
- 4GB RAM
- 2GB free disk space

### **Recommended Requirements**
- Windows 11
- Docker Desktop with 4GB RAM allocation
- Python 3.11+
- Node.js 18+
- 8GB RAM
- 5GB free disk space
- SSD storage for better performance

## 🚀 **Quick Commands**

```cmd
# Start everything (one-click)
🚀 START_BANKING_SYSTEM.bat

# Stop everything
🛑 STOP_BANKING_SYSTEM.bat

# Clean restart
clean_restart.bat

# Check system status
docker ps
```

---

**💡 Tip**: For the best experience, use the one-click launcher `🚀 START_BANKING_SYSTEM.bat` - it handles everything automatically!