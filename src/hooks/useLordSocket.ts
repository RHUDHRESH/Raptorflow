import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';

export type SocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface LordMessage {
  type: string;
  data: any;
  timestamp: string;
  lord?: string;
}

export const useLordSocket = (lord: string) => {
  const { session } = useAuth();
  const [status, setStatus] = useState<SocketStatus>('disconnected');
  const [messages, setMessages] = useState<LordMessage[]>([]);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    if (!session?.access_token) return;

    const wsUrl = (import.meta as any).env.VITE_WS_URL || 'ws://localhost:8000';
    const socketUrl = `${wsUrl}/ws/lords/${lord}?token=${session.access_token}`;

    try {
      setStatus('connecting');
      const ws = new WebSocket(socketUrl);

      ws.onopen = () => {
        setStatus('connected');
        console.log(`[${lord}Socket] Connected`);
        // Subscribe to updates
        ws.send('subscribe');
      };

      ws.onmessage = (event) => {
        try {
          const message: LordMessage = JSON.parse(event.data);
          setMessages((prev) => [...prev, message]);
        } catch (e) {
          console.error(`[${lord}Socket] Failed to parse message`, e);
        }
      };

      ws.onclose = () => {
        setStatus('disconnected');
        console.log(`[${lord}Socket] Disconnected`);
        // Attempt reconnect
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      };

      ws.onerror = (error) => {
        console.error(`[${lord}Socket] Error:`, error);
        setStatus('error');
        ws.close();
      };

      socketRef.current = ws;
    } catch (error) {
      console.error(`[${lord}Socket] Connection failed:`, error);
      setStatus('error');
    }
  }, [session, lord]);

  useEffect(() => {
    if (session) {
      connect();
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [session, connect]);

  const sendMessage = useCallback((message: string) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(message);
    } else {
      console.warn(`[${lord}Socket] Socket not connected`);
    }
  }, [lord]);

  return {
    status,
    messages,
    sendMessage
  };
};

export default useLordSocket;
