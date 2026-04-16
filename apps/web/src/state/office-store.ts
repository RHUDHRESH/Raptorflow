import { create } from 'zustand';
import type { AgentKey } from '@/lib/office-constants';

interface AgentStatus {
  status: 'idle' | 'working' | 'speaking' | 'walking' | 'in_meeting';
  currentZone: string;
  lastEvent: string | null;
}

interface SnarkMessage {
  agentKey: AgentKey;
  text: string;
  timestamp: number;
  id: string;
}

interface OfficeEvent {
  type: string;
  agentKey?: AgentKey;
  timestamp: number;
  processed: boolean;
}

interface OfficeState {
  canvasReady: boolean;
  mode: 'passive' | 'active';
  zoom: number;
  focusedZone: string | null;
  focusedAgent: AgentKey | null;
  nudgePanelOpen: boolean;
  agentStatuses: Record<AgentKey, AgentStatus>;
  snarkFeed: SnarkMessage[];
  eventLog: OfficeEvent[];

  // Actions
  setCanvasReady: (ready: boolean) => void;
  setMode: (mode: 'passive' | 'active') => void;
  setZoom: (zoom: number) => void;
  setFocusedZone: (zoneId: string | null) => void;
  setFocusedAgent: (agentKey: AgentKey | null) => void;
  toggleNudgePanel: (open?: boolean) => void;
  updateAgentStatus: (key: AgentKey, status: Partial<AgentStatus>) => void;
  addSnarkLine: (agentKey: AgentKey, text: string) => void;
  logEvent: (event: Omit<OfficeEvent, 'timestamp' | 'processed'>) => void;
  clearEventLog: () => void;
}

/**
 * Zustand Store for the Office UI Chrome
 * 
 * Note: PixiJS manages its own internal rendering state; this store is for 
 * React-layer synchronization (HUD, Sidebar, Nudge Panel).
 */
export const useOfficeStore = create<OfficeState>((set) => ({
  canvasReady: false,
  mode: 'active',
  zoom: 1.0,
  focusedZone: null,
  focusedAgent: null,
  nudgePanelOpen: true,
  agentStatuses: {} as Record<AgentKey, AgentStatus>,
  snarkFeed: [],
  eventLog: [],

  setCanvasReady: (ready) => set({ canvasReady: ready }),
  setMode: (mode) => set({ mode }),
  setZoom: (zoom) => set({ zoom }),
  setFocusedZone: (zoneId) => set({ focusedZone: zoneId }),
  setFocusedAgent: (agentKey) => set({ focusedAgent: agentKey }),
  toggleNudgePanel: (open) => set((state) => ({ 
    nudgePanelOpen: open !== undefined ? open : !state.nudgePanelOpen 
  })),

  updateAgentStatus: (key, statusUpdate) => set((state) => ({
    agentStatuses: {
      ...state.agentStatuses,
      [key]: {
        ...(state.agentStatuses[key] || { status: 'idle', currentZone: 'reception', lastEvent: null }),
        ...statusUpdate
      }
    }
  })),

  addSnarkLine: (agentKey, text) => set((state) => ({
    snarkFeed: [
      { agentKey, text, timestamp: Date.now(), id: Math.random().toString(36).substring(7) },
      ...state.snarkFeed
    ].slice(0, 50) // Keep last 50
  })),

  logEvent: (event) => set((state) => ({
    eventLog: [
      ...state.eventLog,
      { ...event, timestamp: Date.now(), processed: false }
    ]
  })),

  clearEventLog: () => set({ eventLog: [] }),
}));
