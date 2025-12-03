import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { logger } from '../developer-toolkit/logger';
import { api } from '../services/api';

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
    const [isListening, setIsListening] = useState(false);
    const [wsConnected, setWsConnected] = useState(false);
    const wsRef = useRef(null);

    useEffect(() => {
        const connectWs = () => {
            if (wsRef.current?.readyState === WebSocket.OPEN) return;

            logger.info('Attempting to connect to WebSocket...');
            const ws = new WebSocket('ws://localhost:8765/ws');
            wsRef.current = ws;

            ws.onopen = () => {
                setWsConnected(true);
                logger.info('WebSocket Connected');
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'status') {
                        setIsListening(data.listening);
                        logger.info(`Voice status updated: ${data.listening}`);
                    }
                } catch (e) {
                    logger.error("Failed to parse WS message", e.message);
                }
            };

            ws.onclose = (event) => {
                logger.warn(`WebSocket Disconnected: Code ${event.code}`, event.reason);
                setWsConnected(false);
                wsRef.current = null;
                // Reconnect after 3 seconds
                setTimeout(connectWs, 3000);
            };

            ws.onerror = (error) => {
                logger.error('WebSocket Error', error.message || 'Unknown error');
                ws.close();
            };
        };

        connectWs();

        // Listen for Electron global shortcut
        if (window.electronAPI) {
            window.electronAPI.onTriggerVoice(() => {
                toggleListening();
            });
        }

        return () => {
            if (wsRef.current) {
                wsRef.current.onclose = null;
                wsRef.current.close();
                wsRef.current = null;
            }
        };
    }, []);

    const toggleListening = async () => {
        try {
            if (isListening) {
                return await api.stopVoice();
            } else {
                return await api.startVoice();
            }
        } catch (e) {
            console.error("Failed to toggle voice", e);
            throw e;
        }
    };

    return (
        <WebSocketContext.Provider value={{ isListening, wsConnected, toggleListening }}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocketContext = () => {
    const context = useContext(WebSocketContext);
    if (!context) {
        throw new Error('useWebSocketContext must be used within a WebSocketProvider');
    }
    return context;
};
