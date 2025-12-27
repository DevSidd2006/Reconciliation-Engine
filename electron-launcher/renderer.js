// Banking Reconciliation System Launcher - Renderer Process

class LauncherUI {
    constructor() {
        this.isSystemRunning = false;
        this.dockerStatus = null;
        
        this.initializeElements();
        this.setupEventListeners();
        this.checkInitialStatus();
    }

    initializeElements() {
        // Status elements
        this.dockerIndicator = document.getElementById('docker-indicator');
        this.dockerText = document.getElementById('docker-text');
        this.dockerStatus = document.getElementById('docker-status');
        
        this.systemIndicator = document.getElementById('system-indicator');
        this.systemText = document.getElementById('system-text');
        this.systemStatus = document.getElementById('system-status');
        
        // Log elements
        this.activityLog = document.getElementById('activity-log');
        
        // Button elements
        this.startBtn = document.getElementById('start-btn');
        this.stopBtn = document.getElementById('stop-btn');
        this.frontendBtn = document.getElementById('frontend-btn');
        this.retryBtn = document.getElementById('retry-btn');
        
        // Error elements
        this.errorSection = document.getElementById('error-section');
        this.errorMessage = document.getElementById('error-message');
        this.installDockerBtn = document.getElementById('install-docker-btn');
        this.dismissErrorBtn = document.getElementById('dismiss-error-btn');
    }

    setupEventListeners() {
        // Button event listeners
        this.startBtn.addEventListener('click', () => this.startSystem());
        this.stopBtn.addEventListener('click', () => this.stopSystem());
        this.frontendBtn.addEventListener('click', () => this.openFrontend());
        this.retryBtn.addEventListener('click', () => this.checkDockerStatus());
        this.installDockerBtn.addEventListener('click', () => this.openDockerDesktop());
        this.dismissErrorBtn.addEventListener('click', () => this.dismissError());

        // Listen for status updates from main process
        window.electron.onStatusUpdate((data) => {
            this.handleStatusUpdate(data);
        });
    }

    async checkInitialStatus() {
        await this.checkDockerStatus();
        await this.checkSystemStatus();
    }

    async checkDockerStatus() {
        this.updateDockerStatus('checking', 'Checking Docker installation...');
        this.addLogEntry('Checking Docker installation and daemon status...');

        try {
            const result = await window.electron.checkDocker();
            
            if (result.success) {
                this.updateDockerStatus('success', 
                    `Docker is ready (${result.docker.version.split(' ')[2]})`);
                this.addLogEntry('✅ Docker is installed and running', 'success');
                this.enableSystemControls();
                this.dismissError();
            } else {
                this.updateDockerStatus('error', result.error);
                this.addLogEntry(`❌ Docker check failed: ${result.error}`, 'error');
                this.showDockerError(result.error);
                this.disableSystemControls();
            }
        } catch (error) {
            this.updateDockerStatus('error', 'Failed to check Docker status');
            this.addLogEntry(`❌ Error checking Docker: ${error.message}`, 'error');
            this.showDockerError(error.message);
            this.disableSystemControls();
        }
    }

    async checkSystemStatus() {
        try {
            const status = await window.electron.getSystemStatus();
            this.isSystemRunning = status.isRunning;
            this.updateSystemControls();
        } catch (error) {
            this.addLogEntry(`⚠️ Could not check system status: ${error.message}`, 'warning');
        }
    }

    async startSystem() {
        this.startBtn.disabled = true;
        this.updateSystemStatus('starting', 'Starting system...');
        this.addLogEntry('🚀 Starting Banking Reconciliation System...');

        try {
            const result = await window.electron.startSystem();
            
            if (result.success) {
                this.isSystemRunning = true;
                this.updateSystemStatus('success', 'System is running');
                this.addLogEntry('✅ Banking Reconciliation System started successfully!', 'success');
                this.updateSystemControls();
            } else {
                this.updateSystemStatus('error', `Failed to start: ${result.error}`);
                this.addLogEntry(`❌ Failed to start system: ${result.error}`, 'error');
                this.startBtn.disabled = false;
            }
        } catch (error) {
            this.updateSystemStatus('error', 'Start failed');
            this.addLogEntry(`❌ Error starting system: ${error.message}`, 'error');
            this.startBtn.disabled = false;
        }
    }

    async stopSystem() {
        this.stopBtn.disabled = true;
        this.updateSystemStatus('stopping', 'Stopping system...');
        this.addLogEntry('🛑 Stopping Banking Reconciliation System...');

        try {
            const result = await window.electron.stopSystem();
            
            if (result.success) {
                this.isSystemRunning = false;
                this.updateSystemStatus('stopped', 'System stopped');
                this.addLogEntry('✅ Banking Reconciliation System stopped successfully', 'success');
                this.updateSystemControls();
            } else {
                this.addLogEntry(`❌ Failed to stop system: ${result.error}`, 'error');
                this.stopBtn.disabled = false;
            }
        } catch (error) {
            this.addLogEntry(`❌ Error stopping system: ${error.message}`, 'error');
            this.stopBtn.disabled = false;
        }
    }

    async openFrontend() {
        this.addLogEntry('🌐 Opening Banking Dashboard...');
        try {
            await window.electron.openFrontend();
            this.addLogEntry('✅ Dashboard opened in new window', 'success');
        } catch (error) {
            this.addLogEntry(`❌ Failed to open dashboard: ${error.message}`, 'error');
        }
    }

    async openDockerDesktop() {
        this.addLogEntry('📥 Opening Docker Desktop download page...');
        try {
            await window.electron.openDockerDesktop();
        } catch (error) {
            this.addLogEntry(`❌ Failed to open Docker Desktop page: ${error.message}`, 'error');
        }
    }

    updateDockerStatus(type, message) {
        this.dockerText.textContent = message;
        this.dockerStatus.className = 'status-card';
        this.dockerIndicator.className = 'status-indicator';

        switch (type) {
            case 'checking':
                this.dockerStatus.classList.add('warning');
                this.dockerIndicator.classList.add('loading');
                this.dockerIndicator.textContent = '⏳';
                break;
            case 'success':
                this.dockerStatus.classList.add('success');
                this.dockerIndicator.textContent = '✅';
                break;
            case 'error':
                this.dockerStatus.classList.add('error');
                this.dockerIndicator.textContent = '❌';
                break;
        }
    }

    updateSystemStatus(type, message) {
        this.systemText.textContent = message;
        this.systemStatus.className = 'status-card';
        this.systemIndicator.className = 'status-indicator';

        switch (type) {
            case 'starting':
            case 'stopping':
                this.systemStatus.classList.add('warning');
                this.systemIndicator.classList.add('loading');
                this.systemIndicator.textContent = '⏳';
                break;
            case 'success':
                this.systemStatus.classList.add('success');
                this.systemIndicator.textContent = '✅';
                break;
            case 'stopped':
                this.systemIndicator.textContent = '⭕';
                break;
            case 'error':
                this.systemStatus.classList.add('error');
                this.systemIndicator.textContent = '❌';
                break;
        }
    }

    enableSystemControls() {
        this.startBtn.disabled = false;
        this.updateSystemControls();
    }

    disableSystemControls() {
        this.startBtn.disabled = true;
        this.stopBtn.disabled = true;
        this.frontendBtn.disabled = true;
    }

    updateSystemControls() {
        if (this.isSystemRunning) {
            this.startBtn.disabled = true;
            this.stopBtn.disabled = false;
            this.frontendBtn.disabled = false;
        } else {
            this.startBtn.disabled = false;
            this.stopBtn.disabled = true;
            this.frontendBtn.disabled = true;
        }
    }

    showDockerError(error) {
        this.errorMessage.textContent = error;
        this.errorSection.style.display = 'block';
        
        // Show install button if Docker is not installed
        if (error.includes('not installed') || error.includes('not in PATH')) {
            this.installDockerBtn.style.display = 'inline-block';
        } else {
            this.installDockerBtn.style.display = 'none';
        }
    }

    dismissError() {
        this.errorSection.style.display = 'none';
    }

    addLogEntry(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        logEntry.textContent = `[${timestamp}] ${message}`;
        
        this.activityLog.appendChild(logEntry);
        this.activityLog.scrollTop = this.activityLog.scrollHeight;

        // Keep only last 50 log entries
        while (this.activityLog.children.length > 50) {
            this.activityLog.removeChild(this.activityLog.firstChild);
        }
    }

    handleStatusUpdate(data) {
        const { component, message } = data;
        
        // Add to activity log
        let logType = 'info';
        if (message.includes('successfully') || message.includes('ready')) {
            logType = 'success';
        } else if (message.includes('failed') || message.includes('error')) {
            logType = 'error';
        } else if (message.includes('starting') || message.includes('waiting')) {
            logType = 'warning';
        }
        
        this.addLogEntry(`[${component.toUpperCase()}] ${message}`, logType);
    }
}

// Initialize the launcher UI when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LauncherUI();
});