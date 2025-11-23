import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

type AppContextValue = {
  workspaceId?: string;
  activeIcpId?: string;
  setWorkspaceId: (id?: string) => void;
  setActiveIcpId: (id?: string) => void;
  reset: () => void;
};

const AppContext = createContext<AppContextValue | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [workspaceId, setWorkspaceId] = useState<string | undefined>(undefined);
  const [activeIcpId, setActiveIcpId] = useState<string | undefined>(undefined);

  const value = useMemo<AppContextValue>(
    () => ({
      workspaceId,
      activeIcpId,
      setWorkspaceId,
      setActiveIcpId,
      reset: () => {
        setWorkspaceId(undefined);
        setActiveIcpId(undefined);
      },
    }),
    [workspaceId, activeIcpId],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) {
    throw new Error("useAppContext must be used within an AppProvider");
  }
  return ctx;
}
