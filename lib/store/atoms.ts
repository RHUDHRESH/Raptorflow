import { atom } from "jotai";
import { Campaign, Move, Toast, User } from "@/lib/types";

export type DrawerType = "none" | "muse" | "move" | "campaign" | "strategy";

export const userAtom = atom<User | null>(null);
export const isAuthenticatedAtom = atom((get) => get(userAtom) !== null);

export const activeSidebarAtom = atom<"home" | "campaigns" | "moves" | "settings">("home");
export const sidebarCollapsedAtom = atom<boolean>(false);

export const openDrawerAtom = atom<DrawerType>("none");
export const drawerDataAtom = atom<Record<string, any>>({});

export const currentCampaignAtom = atom<Campaign | null>(null);
export const activeMoveAtom = atom<Move | null>(null);
export const todaysMovesAtom = atom<Move[]>([]);

export const museQuotaUsedAtom = atom<number>(0);
export const museQuotaLimitAtom = atom<number>(120);
export const museQuotaPercentAtom = atom((get) => {
  const used = get(museQuotaUsedAtom);
  const limit = get(museQuotaLimitAtom);
  return Math.round((used / limit) * 100);
});

export const darkModeAtom = atom<boolean>(false);
export const toastStackAtom = atom<Toast[]>([]);

export const loadingAtom = atom<boolean>(false);
