
import { useState, useEffect, useCallback, useRef } from 'react';

export interface AgentEvent {
  id: string;
  event_type: 'thought' | 'action' | 'plan' | 'result' | 'error' | 'system';
  payload: any;
  correlation_id: string;
  timestamp: string;
}

export const useAgentStream = () => {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    // Adjust URL based on environment
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/agent_stream';
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('🧠 Connected to Agent Brain Stream');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        // If it's a pong or system message, handle separately if needed
        if (data.type === 'pong') return;

        // If it matches our Event structure
        if (data.event_type) {
          setEvents((prev) => [...prev, data as AgentEvent]);
        }
      } catch (err) {
        console.error('Error parsing agent event', err);
      }
    };

    ws.onclose = () => {
      console.log('Disconnected from Agent Brain Stream');
      setIsConnected(false);
      // Auto-reconnect logic could go here
    };

    wsRef.current = ws;
  }, []);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { events, isConnected };
};
