import { useEffect, useState, useCallback, useRef } from 'react';
import socketService from '../services/socket';

export const useSocket = () => {
  const [isConnected, setIsConnected] = useState(socketService.isConnected());

  // Connect on mount
  useEffect(() => {
    console.log('useSocket: Initializing Socket.IO connection...');
    socketService.connect();

    const onConnect = () => {
      console.log('useSocket: Socket.IO connected!');
      setIsConnected(true);
    };
    
    const onDisconnect = (reason) => {
      console.log('useSocket: Socket.IO disconnected:', reason);
      setIsConnected(false);
    };

    socketService.on('connect', onConnect);
    socketService.on('disconnect', onDisconnect);

    // Check connection status periodically
    const checkConnection = () => {
      const connected = socketService.isConnected();
      console.log('useSocket: Connection check:', connected);
      setIsConnected(connected);
    };

    const interval = setInterval(checkConnection, 2000);

    return () => {
      clearInterval(interval);
      socketService.off('connect', onConnect);
      socketService.off('disconnect', onDisconnect);
      // We usually don't disconnect the singleton here as other components might use it
    };
  }, []);

  const subscribe = useCallback((event, callback) => {
    socketService.on(event, callback);
  }, []);

  const unsubscribe = useCallback((event, callback) => {
    socketService.off(event, callback);
  }, []);

  const emit = useCallback((event, data) => {
    socketService.emit(event, data);
  }, []);

  return {
    isConnected, // Return state
    subscribe,
    unsubscribe,
    emit
  };
};