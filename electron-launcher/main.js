const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const { spawn, exec } = require('child_process');
const path = require('path');
const axios = require('axios');

class BankingSystemLauncher {
  constructor() {
    this.mainWindow = null;
    this.dockerProcesses = new Map();
    this.isSystemRunning = false;
    this.healthCheckInterval = null;
  }

  createWindow() {
    this.mainWindow = new BrowserWindow({
      width: 800,
      height: 600,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js')
      },
      icon: path.join(__dirname, 'assets', 'icon.png'),
      resizable: false,
      maximizable: false,
      title: 'Banking Reconciliation System Launcher'
    });

    this.mainWindow.loadFile('index.html');
    
    // Remove menu bar
    this.mainWindow.setMenuBarVisibility(false);

    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
      this.cleanup();
    });
  }

  async checkDockerInstallation() {
    return new Promise((resolve) => {
      exec('docker --version', (error, stdout, stderr) => {
        if (error) {
          resolve({
            installed: false,
            error: 'Docker is not installed or not in PATH'
          });
        } else {
          resolve({
            installed: true,
            version: stdout.trim()
          });
        }
      });
    });
  }

  async checkDockerDaemon() {
    return new Promise((resolve) => {
      exec('docker info', (error, stdout, stderr) => {
        if (error) {
          resolve({
            running: false,
            error: 'Docker daemon is not running'
          });
        } else {
          resolve({
            running: true,
            info: 'Docker daemon is running'
          });
        }
      });
    });
  }

  async checkDockerCompose() {
    return new Promise((resolve) => {
      exec('docker compose version', (error, stdout, stderr) => {
        if (error) {
          // Try legacy docker-compose
          exec('docker-compose --version', (error2, stdout2, stderr2) => {
            if (error2) {
              resolve({
                available: false,
                error: 'docker-compose is not available'
              });
            } else {
              resolve({
                available: true,
                version: stdout2.trim(),
                command: 'docker-compose'
              });
            }
          });
        } else {
          resolve({
            available: true,
            version: stdout.trim(),
            command: 'docker compose'
          });
        }
      });
    });
  }

  getResourcesRoot() {
    return app.isPackaged 
      ? process.resourcesPath 
      : path.resolve(__dirname, '..');
  }

  async startDockerServices() {
    const projectRoot = this.getResourcesRoot();
    const composePath = path.join(projectRoot, 'docker-compose.yml');
    
    return new Promise((resolve, reject) => {
      this.sendStatusUpdate('system', 'Starting complete Banking Reconciliation System...');
      this.sendStatusUpdate('system', `Using compose file: ${composePath}`);
      
      const systemProcess = spawn(
        'docker',
        ['compose', '-f', composePath, 'up', '-d', '--build'],
        {
          cwd: projectRoot,
          stdio: 'pipe',
          windowsHide: true
        }
      );

      let output = '';

      systemProcess.stdout.on('data', d => {
        output += d.toString();
        this.sendStatusUpdate('system', d.toString().trim());
      });

      systemProcess.stderr.on('data', d => {
        output += d.toString();
        this.sendStatusUpdate('system', `System: ${d.toString().trim()}`);
      });

      systemProcess.on('close', code => {
        if (code === 0) {
          this.sendStatusUpdate('system', 'All services started successfully');
          this.isSystemRunning = true;
          resolve({ success: true });
        } else {
          reject(new Error(`docker compose failed with code ${code}`));
        }
      });

      this.dockerProcesses.set('system', systemProcess);
    });
  }

  async stopDockerServices() {
    const projectRoot = this.getResourcesRoot();
    const composePath = path.join(projectRoot, 'docker-compose.yml');
    
    return new Promise((resolve) => {
      this.sendStatusUpdate('system', 'Stopping Banking Reconciliation System...');
      
      const systemProcess = spawn(
        'docker',
        ['compose', '-f', composePath, 'down'],
        { cwd: projectRoot }
      );

      systemProcess.on('close', () => {
        this.sendStatusUpdate('system', 'All services stopped successfully');
        this.isSystemRunning = false;
        resolve({ success: true });
      });
    });
  }

  async checkBackendHealth() {
    try {
      const response = await axios.get('http://localhost:8002/health', { timeout: 5000 });
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }

  async waitForBackendHealth(maxAttempts = 60) {
    this.sendStatusUpdate('health', 'Waiting for backend to be ready...');
    
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      const isHealthy = await this.checkBackendHealth();
      
      if (isHealthy) {
        this.sendStatusUpdate('health', 'Backend is ready!');
        return true;
      }
      
      this.sendStatusUpdate('health', `Checking backend health (${attempt}/${maxAttempts})...`);
      await new Promise(resolve => setTimeout(resolve, 3000));
    }
    
    this.sendStatusUpdate('health', 'Backend health check timed out');
    return false;
  }

  sendStatusUpdate(component, message) {
    if (this.mainWindow) {
      this.mainWindow.webContents.send('status-update', { component, message });
    }
  }

  openFrontendWindow() {
    const frontendWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true
      },
      title: 'Banking Reconciliation Dashboard'
    });

    frontendWindow.loadURL('http://localhost:3000');
    
    frontendWindow.webContents.on('did-fail-load', () => {
      dialog.showErrorBox('Frontend Error', 'Failed to load the frontend application. Please ensure the React development server is running on port 3000.');
    });
  }

  cleanup() {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
    
    // Kill any running Docker processes
    this.dockerProcesses.forEach((process) => {
      if (!process.killed) {
        process.kill();
      }
    });
  }

  setupIpcHandlers() {
    ipcMain.handle('check-docker', async () => {
      const dockerCheck = await this.checkDockerInstallation();
      if (!dockerCheck.installed) {
        return { success: false, error: dockerCheck.error };
      }

      const daemonCheck = await this.checkDockerDaemon();
      if (!daemonCheck.running) {
        return { success: false, error: daemonCheck.error };
      }

      const composeCheck = await this.checkDockerCompose();
      if (!composeCheck.available) {
        return { success: false, error: composeCheck.error };
      }

      return {
        success: true,
        docker: dockerCheck,
        daemon: daemonCheck,
        compose: composeCheck
      };
    });

    ipcMain.handle('start-system', async () => {
      try {
        this.sendStatusUpdate('system', 'Starting Banking Reconciliation System...');
        
        const result = await this.startDockerServices();
        
        if (result.success) {
          const isHealthy = await this.waitForBackendHealth();
          
          if (isHealthy) {
            this.sendStatusUpdate('system', 'System started successfully!');
            return { success: true };
          } else {
            this.sendStatusUpdate('system', 'System started but backend health check failed');
            return { success: false, error: 'Backend health check failed' };
          }
        }
        
        return result;
      } catch (error) {
        this.sendStatusUpdate('system', `Failed to start system: ${error.error || error.message}`);
        return { success: false, error: error.error || error.message };
      }
    });

    ipcMain.handle('stop-system', async () => {
      try {
        this.sendStatusUpdate('system', 'Stopping Banking Reconciliation System...');
        const result = await this.stopDockerServices();
        this.sendStatusUpdate('system', 'System stopped successfully');
        return result;
      } catch (error) {
        this.sendStatusUpdate('system', `Failed to stop system: ${error.message}`);
        return { success: false, error: error.message };
      }
    });

    ipcMain.handle('open-frontend', () => {
      this.openFrontendWindow();
    });

    ipcMain.handle('open-docker-desktop', () => {
      shell.openExternal('https://www.docker.com/products/docker-desktop/');
    });

    ipcMain.handle('get-system-status', () => {
      return { isRunning: this.isSystemRunning };
    });
  }
}

// Application lifecycle
const launcher = new BankingSystemLauncher();

app.whenReady().then(() => {
  launcher.createWindow();
  launcher.setupIpcHandlers();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      launcher.createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    launcher.cleanup();
    app.quit();
  }
});

app.on('before-quit', () => {
  launcher.cleanup();
});