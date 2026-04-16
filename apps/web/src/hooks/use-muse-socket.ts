"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth } from "@clerk/nextjs";

/**
 * RaptorFlow Muse Message Type
 */
export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  isStreaming: boolean;
  agentKey?: string;
  agentName?: string;
  timestamp: number;
};

interface MuseSocketState {
  messages: Message[];
  isConnected: boolean;
  isStreaming: boolean;
  sessionId: string | null;
  sendMessage: (text: string, context?: { current_route: string; campaign_id?: string }) => void;
  setSessionId: (id: string | null) => void;
  setMessages: (msgs: Message[]) => void;
}

/**
 * useMuseSocket Hook
 * 
 * Manages the live conversational session with the RaptorFlow Muse.
 * Handles streaming tokens, agent attribution, and automatic reconnection.
 */
export function useMuseSocket(): MuseSocketState {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const maxRetries = 5;

  // ─── WebSocket Logic ─────────────────────────────────────────

  const connect = useCallback(async () => {
    if (socketRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const token = await getToken();
      // Derive WS URL from API URL if WS_URL not explicitly set
      const baseUrl = process.env.NEXT_PUBLIC_WS_URL || 
                      process.env.NEXT_PUBLIC_API_URL?.replace(/^http/, "ws");
      
      const wsUrl = `${baseUrl}/api/v1/ws?token=${token}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log("Muse WebSocket Connected");
        setIsConnected(true);
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        switch (data.type) {
          case "muse.token":
            setIsStreaming(true);
            setMessages((prev) => {
              const last = prev[prev.length - 1];
              if (last && last.role === "assistant" && last.isStreaming) {
                return [
                  ...prev.slice(0, -1),
                  { ...last, content: last.content + data.token },
                ];
              }
              return prev;
            });
            break;

          case "muse.done":
            setIsStreaming(false);
            setMessages((prev) => {
              const last = prev[prev.length - 1];
              if (last && last.role === "assistant") {
                return [
                  ...prev.slice(0, -1),
                  { 
                    ...last, 
                    isStreaming: false, 
                    agentKey: data.agent_key, 
                    agentName: data.agent_name 
                  },
                ];
              }
              return prev;
            });
            break;

          case "muse.error":
            console.error("Muse Socket Error:", data.message);
            setIsStreaming(false);
            break;

          case "nudge.new":
            // Global event handler - can be bridged to an EventBus or Zustand
            break;

          case "office.event":
            // Global office animation handler
            break;
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        setIsStreaming(false);
        if (reconnectAttempts.current < maxRetries) {
          const delay = Math.pow(2, reconnectAttempts.current) * 1000;
          reconnectAttempts.current += 1;
          setTimeout(connect, delay);
        }
      };

      socketRef.current = ws;
    } catch (err) {
      console.error("Failed to connect to Muse WebSocket:", err);
    }
  }, [getToken]);

  useEffect(() => {
    connect();
    return () => {
      socketRef.current?.close();
    };
  }, [connect]);

  // ─── Actions ─────────────────────────────────────────────────

  const sendMessage = useCallback((text: string, context?: { current_route: string; campaign_id?: string }) => {
    if (!socketRef.current || !sessionId) return;

    // 1. Optimistic User Message
    const userMsg: Message = {
      id: Math.random().toString(36).substring(7),
      role: "user",
      content: text,
      isStreaming: false,
      timestamp: Date.now(),
    };

    // 2. Prep Empty Assistant Message
    const assistantMsg: Message = {
      id: Math.random().toString(36).substring(7),
      role: "assistant",
      content: "",
      isStreaming: true,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);

    // 3. Send over Wire
    socketRef.current.send(JSON.stringify({
      type: "muse.send",
      message: text,
      session_id: sessionId,
      context: context || { current_route: window.location.pathname }
    }));
  }, [sessionId]);

  return {
    messages,
    setMessages,
    isConnected,
    isStreaming,
    sessionId,
    setSessionId,
    sendMessage,
  };
}
