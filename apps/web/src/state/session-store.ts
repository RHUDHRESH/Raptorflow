import { create } from "zustand";

interface SessionState {
  activeOrgId?: string;
  activeSessionId?: string;
  setSession: (payload: { activeOrgId?: string; activeSessionId?: string }) => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  activeOrgId: undefined,
  activeSessionId: undefined,
  setSession: (payload) => set(payload),
}));
