import { useState, useEffect } from 'react';
import socketService from '../services/socket';

export const useSocket = () => {
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        socketService.connect();

        const checkConnection = () => {
            setIsConnected(socketService.isConnected());
        };

        // Check connection status periodically
        const interval = setInterval(checkConnection, 1000);
        checkConnection();

        return () => {
            clearInterval(interval);
        };
    }, []);

    const subscribe = (event, callback) => {
        socketService.on(event, callback);
    };

    const unsubscribe = (event, callback) => {
        socketService.off(event, callback);
    };

    const emit = (event, data) => {
        socketService.emit(event, data);
    };

    return {
        isConnected,
        subscribe,
        unsubscribe,
        emit,
    };
};
