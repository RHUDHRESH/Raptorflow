import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface PersonaBrief {
  audience: string;
  voice: string;
  goals: string[];
  guidelines?: string;
}

interface PersonaStoreState {
  brief: PersonaBrief | null;
  setBrief: (brief: PersonaBrief) => void;
  updateBrief: (updates: Partial<PersonaBrief>) => void;
  clearBrief: () => void;
}

export const usePersonaStore = create<PersonaStoreState>()(
  persist(
    (set, get) => ({
      brief: null,

      setBrief: (brief: PersonaBrief) => set({ brief }),

      updateBrief: (updates: Partial<PersonaBrief>) => set((state) => ({
        brief: state.brief ? { ...state.brief, ...updates } : null
      })),

      clearBrief: () => set({ brief: null }),
    }),
    {
      name: "persona-brief-storage",
    }
  )
);
