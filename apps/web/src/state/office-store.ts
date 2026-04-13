import { create } from "zustand";
import type { OfficeEventMessage } from "@raptorflow/contracts";
import {
  officeDebugSurfaces,
  officeFloorPlan,
  officeRoster,
  officeSeedEvents,
  officeSnarkLines,
  type OfficeAgent,
  type OfficeDebugSurface,
  type OfficeMode,
  type OfficeSnarkLine,
  type OfficeSurface,
  type OfficeZone,
} from "./office-types";

interface OfficeState {
  mode: OfficeMode;
  surface: OfficeSurface;
  zoomLevel: number;
  focusedZoneId: string;
  floorPlan: OfficeZone[];
  roster: OfficeAgent[];
  snarkLines: OfficeSnarkLine[];
  debugSurfaces: OfficeDebugSurface[];
  eventLog: OfficeEventMessage[];
  connectionStatus: "disconnected" | "connecting" | "connected";
  setMode: (mode: OfficeMode) => void;
  setSurface: (surface: OfficeSurface) => void;
  setZoomLevel: (zoomLevel: number) => void;
  focusZone: (zoneId: string) => void;
  zoomIn: () => void;
  zoomOut: () => void;
  pushEvent: (event: OfficeEventMessage) => void;
  clearEvents: () => void;
  setConnectionStatus: (status: "disconnected" | "connecting" | "connected") => void;
}

export const useOfficeStore = create<OfficeState>((set) => ({
  mode: "passive",
  surface: "floor_plan",
  zoomLevel: 1,
  focusedZoneId: "conference-room",
  floorPlan: officeFloorPlan,
  roster: officeRoster,
  snarkLines: officeSnarkLines,
  debugSurfaces: officeDebugSurfaces,
  eventLog: officeSeedEvents,
  connectionStatus: "disconnected",
  setMode: (mode) => set({ mode }),
  setSurface: (surface) => set({ surface }),
  setZoomLevel: (zoomLevel) => set({ zoomLevel: Math.min(1.5, Math.max(0.4, zoomLevel)) }),
  focusZone: (focusedZoneId) => set({ focusedZoneId }),
  zoomIn: () => set((state) => ({ zoomLevel: Math.min(1.5, state.zoomLevel + 0.1) })),
  zoomOut: () => set((state) => ({ zoomLevel: Math.max(0.4, state.zoomLevel - 0.1) })),
  pushEvent: (event) =>
    set((state) => ({
      eventLog: [...state.eventLog.slice(-499), event],
    })),
  clearEvents: () => set({ eventLog: [] }),
  setConnectionStatus: (connectionStatus) => set({ connectionStatus }),
}));
