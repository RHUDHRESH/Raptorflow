import { publicEnv } from "./env";
import { useOfficeStore } from "@/state/office-store";
import type { OfficeEventMessage } from "@raptorflow/contracts";

export type OfficeSocketStatus = "connecting" | "connected" | "disconnected" | "error";

type StatusListener = (status: OfficeSocketStatus) => void;

export class OfficeSocket {
  private ws: WebSocket | null = null;
  private _orgId: string;
  private status: OfficeSocketStatus = "disconnected";
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectDelay = 1000;
  private maxReconnectDelay = 30_000;
  private shouldReconnect = true;
  private statusListeners = new Set<StatusListener>();

  constructor(orgId: string) {
    this._orgId = orgId;
  }

  get orgId(): string {
    return this._orgId;
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    if (this.ws?.readyState === WebSocket.CONNECTING) return;
    this.shouldReconnect = true;
    this.doConnect();
  }

  disconnect(): void {
    this.shouldReconnect = false;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close(1000, "Client disconnect");
      this.ws = null;
    }
    this.setStatus("disconnected");
  }

  send(event: Omit<OfficeEventMessage, "orgId">): void {
    if (this.ws?.readyState !== WebSocket.OPEN) return;
    const message: OfficeEventMessage = {
      ...event,
      orgId: this._orgId,
    } as OfficeEventMessage;
    this.ws.send(JSON.stringify(message));
  }

  getStatus(): OfficeSocketStatus {
    return this.status;
  }

  addStatusListener(listener: StatusListener): () => void {
    this.statusListeners.add(listener);
    return () => this.statusListeners.delete(listener);
  }

  private doConnect(): void {
    this.setStatus("connecting");

    let url: string;
    if (publicEnv.offlineMode) {
      const wsBase = `ws://localhost:3001`;
      url = `${wsBase}/ws/office?org_id=${encodeURIComponent(this._orgId)}`;
    } else {
      const apiHost = publicEnv.apiBaseUrl.replace(/^https?:\/\//, "");
      url = `wss://${apiHost}/ws/office?org_id=${encodeURIComponent(this._orgId)}`;
    }

    try {
      this.ws = new WebSocket(url);
    } catch {
      this.scheduleReconnect();
      return;
    }

    this.ws.onopen = () => {
      this.setStatus("connected");
      this.reconnectDelay = 1000;
    };

    this.ws.onmessage = (evt) => {
      try {
        const event: OfficeEventMessage = JSON.parse(evt.data as string);
        this.dispatchEvent(event);
      } catch {
        // Ignore malformed messages silently
      }
    };

    this.ws.onerror = () => {
      this.setStatus("error");
    };

    this.ws.onclose = (evt) => {
      if (evt.code === 1000) {
        this.setStatus("disconnected");
        return;
      }
      this.setStatus("disconnected");
      if (this.shouldReconnect) {
        this.scheduleReconnect();
      }
    };
  }

  private scheduleReconnect(): void {
    if (!this.shouldReconnect || this.reconnectTimer) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
      this.doConnect();
    }, this.reconnectDelay);
  }

  private setStatus(status: OfficeSocketStatus): void {
    this.status = status;
    this.statusListeners.forEach((listener) => listener(status));
  }

  private dispatchEvent(event: OfficeEventMessage): void {
    const store = useOfficeStore.getState();
    store.pushEvent(event);

    switch (event.eventType) {
      case "morning_meeting_start":
        store.setMode("active");
        store.focusZone("conference-room");
        break;
      case "conference_break":
        store.setMode("passive");
        break;
      case "debate_agent_speaking":
      case "debate_agent_reacting":
        store.setMode("active");
        break;
      case "agent_walk_start":
        if (event.payload.destination && typeof event.payload.destination === "string") {
          store.focusZone(event.payload.destination);
        }
        break;
      case "snark_refresh":
        store.setSurface("snark");
        break;
    }
  }
}

const socketMap = new Map<string, OfficeSocket>();

export function getOfficeSocket(orgId: string): OfficeSocket {
  if (!socketMap.has(orgId)) {
    socketMap.set(orgId, new OfficeSocket(orgId));
  }
  return socketMap.get(orgId)!;
}

export function useOfficeSocket(orgId: string) {
  const socket = getOfficeSocket(orgId);
  return {
    socket,
    connect: () => socket.connect(),
    disconnect: () => socket.disconnect(),
    send: (event: Omit<OfficeEventMessage, "orgId">) => socket.send(event),
    getStatus: () => socket.getStatus(),
    addStatusListener: (listener: StatusListener) => socket.addStatusListener(listener),
  };
}
