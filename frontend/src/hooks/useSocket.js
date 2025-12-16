import { useEffect, useRef, useCallback } from 'react';
import { SOCKET_URL } from '../utils/constants';

export const useSocket = () => {
  const socketRef = useRef(null);
  const listenersRef = useRef(new Map());

  useEffect(() => {
    // Initialize WebSocket connection
    const connectWebSocket = () => {
      try {
        const wsUrl = SOCKET_URL.replace('http', 'ws') + '/ws';
        socketRef.current = new WebSocket(wsUrl);

        socketRef.current.onopen = () => {
          console.log('WebSocket connected');
        };

        socketRef.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            const { type, payload } = data;

            // Call all listeners for this event type
            const listeners = listenersRef.current.get(type) || [];
            listeners.forEach(callback => callback(payload));
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        socketRef.current.onclose = () => {
          console.log('WebSocket disconnected');
          // Attempt to reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };

        socketRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        // Retry connection after 5 seconds
        setTimeout(connectWebSocket, 5000);
      }
    };

    connectWebSocket();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  const subscribe = useCallback((eventType, callback) => {
    const listeners = listenersRef.current.get(eventType) || [];
    listeners.push(callback);
    listenersRef.current.set(eventType, listeners);
  }, []);

  const unsubscribe = useCallback((eventType, callback) => {
    const listeners = listenersRef.current.get(eventType) || [];
    const filteredListeners = listeners.filter(listener => listener !== callback);
    
    if (filteredListeners.length === 0) {
      listenersRef.current.delete(eventType);
    } else {
      listenersRef.current.set(eventType, filteredListeners);
    }
  }, []);

  const emit = useCallback((eventType, data) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: eventType,
        payload: data
      }));
    }
  }, []);

  return {
    subscribe,
    unsubscribe,
    emit,
    isConnected: socketRef.current?.readyState === WebSocket.OPEN
  };
};