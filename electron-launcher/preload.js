const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electron', {
  checkDocker: () => ipcRenderer.invoke('check-docker'),
  startSystem: () => ipcRenderer.invoke('start-system'),
  stopSystem: () => ipcRenderer.invoke('stop-system'),
  openFrontend: () => ipcRenderer.invoke('open-frontend'),
  openDockerDesktop: () => ipcRenderer.invoke('open-docker-desktop'),
  getSystemStatus: () => ipcRenderer.invoke('get-system-status'),
  
  // Listen for status updates
  onStatusUpdate: (callback) => {
    ipcRenderer.on('status-update', (event, data) => callback(data));
  },
  
  // Remove listeners
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});