/**
 * Context Store
 * 
 * Manages Business Context Manifest (BCM) state and freshness indicators.
 */
import { create } from 'zustand'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

type ContextState = {
  freshness: Record<string, string> // workspace_id -> last updated timestamp
  isLoading: boolean
  error: string | null
}

type ContextActions = {
  checkFreshness: (workspaceId: string) => Promise<void>
  triggerRebuild: (workspaceId: string) => Promise<void>
}

export const useContextStore = create<ContextState & ContextActions>()((set, get) => ({
  freshness: {},
  isLoading: false,
  error: null,

  async checkFreshness(workspaceId: string) {
    set({ isLoading: true, error: null })
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/context/manifest?workspace_id=${workspaceId}`
      )
      const data = await response.json()
      set({
        freshness: {
          ...get().freshness,
          [workspaceId]: data.updated_at
        },
        isLoading: false
      })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      set({ error: message, isLoading: false })
    }
  },

  async triggerRebuild(workspaceId: string) {
    set({ isLoading: true, error: null })
    try {
      await fetch(`${API_BASE_URL}/api/v1/context/rebuild`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace_id: workspaceId })
      })
      await get().checkFreshness(workspaceId)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      set({ error: message, isLoading: false })
    }
  }
}))
