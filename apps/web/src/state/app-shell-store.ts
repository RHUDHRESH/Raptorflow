import { create } from "zustand";

interface AppShellState {
  sidebarOpen: boolean;
  commandPaletteOpen: boolean;
  toggleSidebar: () => void;
  setCommandPaletteOpen: (open: boolean) => void;
}

export const useAppShellStore = create<AppShellState>((set) => ({
  sidebarOpen: true,
  commandPaletteOpen: false,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
}));
