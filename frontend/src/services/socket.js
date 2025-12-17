import { io } from 'socket.io-client';
import { SOCKET_URL, ENABLE_SOCKET } from '../utils/constants';

class SocketService {
    constructor() {
        this.socket = null;
        this.listeners = new Map();
    }

    connect() {
        if (!ENABLE_SOCKET) {
            console.log('Socket.IO is disabled');
            return;
        }

        if (this.socket?.connected) {
            console.log('Socket already connected');
            return;
        }

        const token = localStorage.getItem('token');
        console.log('SocketService: Connecting to', SOCKET_URL, 'with token:', token ? 'present' : 'missing');

        this.socket = io(SOCKET_URL, {
            transports: ['polling', 'websocket'],
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: 5,
            timeout: 10000,
            forceNew: true
        });

        this.socket.on('connect', () => {
            console.log('✅ Socket.IO connected successfully! ID:', this.socket.id);
        });

        this.socket.on('disconnect', (reason) => {
            console.log('❌ Socket.IO disconnected. Reason:', reason);
        });

        this.socket.on('connect_error', (error) => {
            console.error('🚫 Socket.IO connection error:', error.message || error);
        });

        this.socket.on('error', (error) => {
            console.error('⚠️ Socket.IO error:', error);
        });

        this.socket.on('reconnect', (attemptNumber) => {
            console.log('🔄 Socket.IO reconnected after', attemptNumber, 'attempts');
        });

        this.socket.on('reconnect_attempt', (attemptNumber) => {
            console.log('🔄 Socket.IO reconnection attempt', attemptNumber);
        });

        this.socket.on('reconnect_error', (error) => {
            console.error('🚫 Socket.IO reconnection error:', error);
        });

        this.socket.on('reconnect_failed', () => {
            console.error('💥 Socket.IO reconnection failed - giving up');
        });
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
            this.listeners.clear();
        }
    }

    on(event, callback) {
        if (!this.socket) {
            console.warn('Socket not connected. Call connect() first.');
            return;
        }

        this.socket.on(event, callback);

        // Store listener for cleanup
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    off(event, callback) {
        if (!this.socket) return;

        if (callback) {
            this.socket.off(event, callback);

            // Remove from listeners map
            const eventListeners = this.listeners.get(event);
            if (eventListeners) {
                const index = eventListeners.indexOf(callback);
                if (index > -1) {
                    eventListeners.splice(index, 1);
                }
            }
        } else {
            this.socket.off(event);
            this.listeners.delete(event);
        }
    }

    emit(event, data) {
        if (!this.socket) {
            console.warn('Socket not connected. Call connect() first.');
            return;
        }

        this.socket.emit(event, data);
    }

    isConnected() {
        return this.socket?.connected || false;
    }
}

// Create singleton instance
const socketService = new SocketService();

export default socketService;
