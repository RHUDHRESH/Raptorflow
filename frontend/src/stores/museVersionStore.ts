import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface AssetVersion {
  id: string;
  assetId: string;
  content: string;
  title: string;
  tags: string[];
  type: string;
  metadata?: Record<string, any>;
  createdAt: string;
  changeDescription?: string;
}

export interface AssetVersionCreate {
  content: string;
  title: string;
  tags: string[];
  type: string;
  metadata?: Record<string, any>;
  changeDescription?: string;
}

export interface MuseAssetWithVersions extends MuseAsset {
  versions: AssetVersion[];
}

export interface VersionDiff {
  added: string[];
  removed: string[];
  unchanged: string[];
}

interface MuseVersionStoreState {
  versions: Record<string, AssetVersion[]>; // assetId -> versions
  addVersion: (assetId: string, version: AssetVersionCreate) => void;
  getVersions: (assetId: string) => AssetVersion[];
  getDiff: (assetId: string, fromVersionId: string, toVersionId: string) => VersionDiff | null;
  deleteVersions: (assetId: string) => void;
}

const generateId = () => Math.random().toString(36).substr(2, 9);

export const useMuseVersionStore = create<MuseVersionStoreState>()(
  persist(
    (set, get) => ({
      versions: {},

      addVersion: (assetId, version) => {
        set((state) => ({
          versions: {
            ...state.versions,
            [assetId]: [
              ...(state.versions[assetId] || []),
              {
                ...version,
                id: generateId(),
                createdAt: new Date().toISOString(),
                assetId,
              },
            ],
          },
        }));
      },

      getVersions: (assetId) => {
        return get().versions[assetId] || [];
      },

      getDiff: (assetId, fromVersionId, toVersionId) => {
        const versions = get().versions[assetId] || [];
        const from = versions.find(v => v.id === fromVersionId);
        const to = versions.find(v => v.id === toVersionId);
        if (!from || !to) return null;

        const fromLines = from.content.split('\n');
        const toLines = to.content.split('\n');
        const added: string[] = [];
        const removed: string[] = [];
        const unchanged: string[] = [];

        // Simple line-by-line diff
        const maxLines = Math.max(fromLines.length, toLines.length);
        for (let i = 0; i < maxLines; i++) {
          const fromLine = fromLines[i] || '';
          const toLine = toLines[i] || '';
          if (fromLine === toLine) {
            unchanged.push(fromLine);
          } else {
            if (fromLine) removed.push(fromLine);
            if (toLine) added.push(toLine);
          }
        }

        return { added, removed, unchanged };
      },

      deleteVersions: (assetId) => {
        set((state) => {
          const next = { ...state.versions };
          delete next[assetId];
          return { versions: next };
        });
      },
    }),
    {
      name: "muse-versions-storage",
    }
  )
);
