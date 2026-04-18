import { getAuthToken, getWsBaseUrl } from "./api";
import { useOfficeStore } from "@/state/office-store";
export type OfficeSocketStatus = "connecting" | "connected" | "disconnected" | "error";

type OfficeEventMessage = {
  event_type: string;
  org_id: string;
  payload: Record<string, unknown>;
  timestamp: string;
};

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

  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    if (this.ws?.readyState === WebSocket.CONNECTING) return;
    this.shouldReconnect = true;
    await this.doConnect();
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

  getStatus(): OfficeSocketStatus {
    return this.status;
  }

  addStatusListener(listener: StatusListener): () => void {
    this.statusListeners.add(listener);
    return () => this.statusListeners.delete(listener);
  }

  private async doConnect(): Promise<void> {
    this.setStatus("connecting");
    useOfficeStore.getState().setConnectionStatus("connecting");

    const token = await getAuthToken();
    if (!token) {
      this.setStatus("error");
      useOfficeStore.getState().setConnectionStatus("disconnected");
      return;
    }

    const url = `${getWsBaseUrl()}/api/v1/office/ws?token=${encodeURIComponent(token)}`;

    try {
      this.ws = new WebSocket(url);
    } catch {
      this.scheduleReconnect();
      return;
    }

    this.ws.onopen = () => {
      this.setStatus("connected");
      useOfficeStore.getState().setConnectionStatus("connected");
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
      useOfficeStore.getState().setConnectionStatus("disconnected");
    };

    this.ws.onclose = (evt) => {
      if (evt.code === 1000) {
        this.setStatus("disconnected");
        useOfficeStore.getState().setConnectionStatus("disconnected");
        return;
      }
      this.setStatus("disconnected");
      useOfficeStore.getState().setConnectionStatus("disconnected");
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
      void this.doConnect();
    }, this.reconnectDelay);
  }

  private setStatus(status: OfficeSocketStatus): void {
    this.status = status;
    this.statusListeners.forEach((listener) => listener(status));
  }

  private dispatchEvent(event: OfficeEventMessage): void {
    const store = useOfficeStore.getState();
    const payload = event.payload ?? {};
    const agentKey = (payload.agent_key || payload.agentKey) as any;
    store.logEvent({ type: event.event_type, agentKey });
    
    switch (event.event_type) {
      case "morning_meeting_start":
        store.setMode("active");
        store.setFocusedZone("conference-room");
        break;
      case "conference_break":
        store.setMode("passive");
        break;
      case "debate_agent_speaking":
      case "debate_agent_reacting":
        store.setMode("active");
        break;
      case "agent_walk_start":
        if (payload.destination && typeof payload.destination === "string") {
          store.setFocusedZone(payload.destination);
        }
        break;
      case "snark_refresh":
        store.toggleNudgePanel(true);
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
    getStatus: () => socket.getStatus(),
    addStatusListener: (listener: StatusListener) => socket.addStatusListener(listener),
  };
}
