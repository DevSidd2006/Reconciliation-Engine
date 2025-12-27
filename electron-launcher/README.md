# Banking Reconciliation System - Desktop Launcher

## Overview

This Electron-based desktop application serves as a launcher and orchestrator for the Banking Reconciliation System. It provides a clean GUI interface to manage Docker services without requiring manual command-line operations.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Electron Launcher                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Docker Check  │  │  Service Start  │  │  Health Mon  │ │
│  │   • Installation│  │  • Kafka        │  │  • Backend   │ │
│  │   • Daemon      │  │  • PostgreSQL   │  │  • Frontend  │ │
│  │   • Compose     │  │  • Redis        │  │  • Endpoints │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Docker Environment                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │     Kafka       │  │    Backend      │  │   Frontend   │ │
│  │  • Zookeeper    │  │  • FastAPI      │  │  • React     │ │
│  │  • Kafka Broker │  │  • PostgreSQL   │  │  • Dashboard │ │
│  │  • Schema Reg   │  │  • Redis        │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 🐳 Docker Orchestration
- **Pre-flight Checks**: Validates Docker installation and daemon status
- **Service Management**: Starts/stops all services using existing docker-compose files
- **Health Monitoring**: Waits for backend API to be ready before declaring success

### 🖥️ Clean User Interface
- **Status Dashboard**: Real-time status of Docker and system components
- **Activity Log**: Detailed logging of all operations with timestamps
- **Error Handling**: Clear error messages with actionable solutions
- **Control Buttons**: Start/Stop system, Open Dashboard, Retry operations

### 🔒 Enterprise-Grade Design
- **No Code Modifications**: Uses existing backend/frontend without changes
- **Dependency Isolation**: All dependencies run inside Docker containers
- **Graceful Error Handling**: Comprehensive error scenarios covered
- **Resource Management**: Proper cleanup of processes and resources

## Prerequisites

### Required (Must be installed on client machine)
- **Docker Desktop**: Must be installed and running
- **Windows 10/11**: Target platform for .exe distribution

### Not Required (Handled by Docker)
- ❌ Python/pip - Runs inside backend container
- ❌ Node.js/npm - Runs inside frontend container  
- ❌ Kafka/Zookeeper - Runs inside Kafka container
- ❌ PostgreSQL/Redis - Runs inside database containers

## Installation & Usage

### Development Setup
```bash
cd electron-launcher
npm install
npm start
```

### Building Windows Executable
```bash
npm run build-win
```
This creates a distributable .exe file in the `dist/` directory.

### End User Workflow
1. **Install**: Run the .exe installer
2. **Launch**: Start "Banking Reconciliation Launcher" from desktop/start menu
3. **Check**: Application automatically checks Docker status
4. **Start**: Click "Start System" to launch all services
5. **Access**: Click "Open Dashboard" to access the banking interface

## Error Scenarios & Solutions

### Docker Not Installed
```
❌ Error: Docker is not installed or not in PATH
💡 Solution: Download and install Docker Desktop
🔗 Action: "Download Docker Desktop" button opens official download page
```

### Docker Daemon Not Running
```
❌ Error: Docker daemon is not running  
💡 Solution: Start Docker Desktop application
🔄 Action: "Retry Docker Check" button to re-validate
```

### Port Conflicts
```
❌ Error: Port 5432 already in use
💡 Solution: Stop conflicting services or change ports in docker-compose.yml
```

### Service Startup Failures
```
❌ Error: Backend services failed to start (exit code: 1)
💡 Solution: Check Docker logs, ensure sufficient resources
```

## File Structure

```
electron-launcher/
├── main.js              # Main Electron process (Docker orchestration)
├── preload.js           # Secure IPC bridge
├── renderer.js          # UI logic and event handling
├── index.html           # Main application interface
├── styles.css           # Professional UI styling
├── package.json         # Electron dependencies and build config
├── README.md           # This documentation
└── assets/             # Application icons and resources
    └── icon.ico        # Windows application icon
```

## Technical Implementation

### Docker Service Orchestration
```javascript
// Sequential startup: Kafka → Backend → Health Check
async startDockerServices() {
  // 1. Start Kafka infrastructure
  await this.startKafkaServices();
  
  // 2. Start backend services  
  await this.startBackendServices();
  
  // 3. Wait for backend health endpoint
  await this.waitForBackendHealth();
}
```

### Health Check Implementation
```javascript
// Polls backend /health endpoint until ready
async waitForBackendHealth(maxAttempts = 30) {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const isHealthy = await this.checkBackendHealth();
    if (isHealthy) return true;
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  return false;
}
```

### Security Model
- **Context Isolation**: Renderer process cannot access Node.js APIs directly
- **Preload Script**: Secure IPC bridge with limited, validated API surface
- **No Shell Injection**: All Docker commands use spawn() with argument arrays

## Build Configuration

### Electron Builder Settings
```json
{
  "build": {
    "appId": "com.banking.reconciliation.launcher",
    "productName": "Banking Reconciliation Launcher",
    "win": {
      "target": "nsis",
      "icon": "assets/icon.ico"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  }
}
```

## Deployment Strategy

### Distribution Package
- **Single .exe installer**: Contains all Electron dependencies
- **No additional downloads**: Self-contained application
- **Standard Windows installer**: NSIS-based with user-friendly options
- **Desktop integration**: Start menu and desktop shortcuts

### Client Requirements
- Windows 10/11 (64-bit)
- Docker Desktop installed and running
- 4GB+ RAM (for Docker containers)
- 10GB+ disk space (for Docker images)

## Maintenance & Updates

### Version Updates
- Update `package.json` version
- Rebuild with `npm run build-win`
- Distribute new .exe to clients

### Docker Image Updates
- No launcher changes needed
- Docker will pull latest images automatically
- Backend/frontend updates are transparent to launcher

## Troubleshooting

### Common Issues

**Launcher won't start**
- Check Windows compatibility (Win10/11 required)
- Run as administrator if needed
- Check antivirus software blocking

**Docker check fails**
- Ensure Docker Desktop is installed and running
- Check Windows Docker integration is enabled
- Verify Docker is in system PATH

**Services fail to start**
- Check available system resources (RAM/CPU)
- Ensure ports 3000, 5432, 6379, 8000, 9092 are available
- Review Docker Desktop logs for detailed errors

**Frontend won't open**
- Wait for full system startup (health check completion)
- Check if port 3000 is accessible
- Verify React development server started successfully

## Support

For technical support:
1. Check the Activity Log in the launcher for detailed error messages
2. Review Docker Desktop logs for container-specific issues
3. Ensure all prerequisites are met (Docker Desktop running)
4. Try the "Retry Docker Check" button after resolving issues