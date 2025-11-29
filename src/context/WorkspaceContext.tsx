import React, { createContext, useContext, useState, useEffect } from 'react';
import type { User } from '@supabase/supabase-js';
import { supabase, isSupabaseConfigured } from '../lib/supabase';
import { workspaceService, type Workspace } from '../services/workspaceService';
import { useAuth } from './AuthContext';

/**
 * Workspace Context Value
 * 
 * The shape of the context value provided by WorkspaceProvider.
 */
export interface WorkspaceContextValue {
    // State
    status: 'idle' | 'loading' | 'ready' | 'error';
    currentWorkspace: Workspace | null;
    currentWorkspaceId: string | null;
    workspaces: Workspace[];
    loading: boolean;
    user: User | null;
    error: string | null;

    // Actions
    selectWorkspace: (workspace: Workspace) => void;
    setCurrentWorkspaceId: (id: string) => void;
    addWorkspace: (workspace: Workspace) => void;
    createNewWorkspace: (name: string, description?: string) => Promise<{ success: boolean; error?: string; workspace?: Workspace }>;
    refreshWorkspaces: () => Promise<void>;
}

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

/**
 * useWorkspace Hook
 * 
 * Custom hook to access workspace context. Must be used within a WorkspaceProvider.
 * 
 * @throws Error if used outside of WorkspaceProvider
 */
export const useWorkspace = (): WorkspaceContextValue => {
    const context = useContext(WorkspaceContext);
    if (!context) {
        throw new Error('useWorkspace must be used within a WorkspaceProvider');
    }
    return context;
};

interface WorkspaceProviderProps {
    children: React.ReactNode;
}

/**
 * Workspace Provider
 * 
 * Provides workspace state and methods to the entire application.
 * Handles workspace fetching, selection, and management.
 * 
 * Features:
 * - Auto-loads workspaces for authenticated users
 * - Persists workspace selection in localStorage
 * - Auto-selects single workspace
 * - Restores last-used workspace
 */
export const WorkspaceProvider: React.FC<WorkspaceProviderProps> = ({ children }) => {
    const { user } = useAuth();
    const [status, setStatus] = useState<'idle' | 'loading' | 'ready' | 'error'>('idle');
    const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);
    const [currentWorkspaceId, setCurrentWorkspaceId] = useState<string | null>(null);
    const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Initialize workspace state when user changes
    useEffect(() => {
        const initializeWorkspace = async () => {
            if (!user) {
                setStatus('idle');
                setCurrentWorkspace(null);
                setCurrentWorkspaceId(null);
                setWorkspaces([]);
                setLoading(false);
                return;
            }

            // DEV BYPASS CHECK: If user is dev user (from AuthContext bypass), inject mock workspace
            if (user.id === 'dev-user-123' || user.id === 'demo-user') {
                console.log('[WorkspaceProvider] Dev/Demo user detected, injecting mock workspace');
                
                const mockWorkspace: Workspace = {
                    id: 'demo-workspace-1',
                    name: 'Demo Workspace',
                    slug: 'demo-workspace',
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString(),
                    owner_id: user.id
                };

                setWorkspaces([mockWorkspace]);
                setCurrentWorkspace(mockWorkspace);
                setCurrentWorkspaceId(mockWorkspace.id);
                setStatus('ready');
                setLoading(false);
                return;
            }

            // Regular Supabase flow
            if (!isSupabaseConfigured() || !supabase) {
                // Should normally not happen if user is real, but fallback to demo if something is wrong
                console.warn('[WorkspaceProvider] Supabase not configured but user present. Injecting mock workspace.');
                const mockWorkspace: Workspace = {
                    id: 'demo-workspace-1',
                    name: 'Demo Workspace',
                    slug: 'demo-workspace',
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString(),
                    owner_id: user.id
                };
                setWorkspaces([mockWorkspace]);
                setCurrentWorkspace(mockWorkspace);
                setCurrentWorkspaceId(mockWorkspace.id);
                setStatus('ready');
                setLoading(false);
                return;
            }

            try {
                setStatus('loading');
                setLoading(true);

                // Fetch workspaces from DB (RLS filters automatically)
                const { data: userWorkspaces, error: fetchError } = await workspaceService.getWorkspaces();

                if (fetchError) {
                    console.error('[WorkspaceProvider] Error fetching workspaces:', fetchError);
                    setStatus('error');
                    setError(fetchError.message || 'Failed to load workspaces');
                    setLoading(false);
                    return;
                }

                setWorkspaces(userWorkspaces || []);

                // Workspace selection logic with userId-scoped localStorage
                if (userWorkspaces && userWorkspaces.length > 0) {
                    const storageKey = `rf_active_workspace_${user.id}`;
                    const lastWorkspaceId = localStorage.getItem(storageKey);

                    if (userWorkspaces.length === 1) {
                        // Auto-select the only workspace
                        const workspace = userWorkspaces[0];
                        setCurrentWorkspace(workspace);
                        setCurrentWorkspaceId(workspace.id);
                        localStorage.setItem(storageKey, workspace.id);
                    } else if (lastWorkspaceId) {
                        // Try to restore last-used workspace
                        const workspace = userWorkspaces.find((w) => w.id === lastWorkspaceId);
                        if (workspace) {
                            setCurrentWorkspace(workspace);
                            setCurrentWorkspaceId(workspace.id);
                        } else {
                            // Fallback to first
                            const workspace = userWorkspaces[0];
                            setCurrentWorkspace(workspace);
                            setCurrentWorkspaceId(workspace.id);
                        }
                    } else {
                         // Fallback to first
                         const workspace = userWorkspaces[0];
                         setCurrentWorkspace(workspace);
                         setCurrentWorkspaceId(workspace.id);
                    }
                }

                setStatus('ready');
                setLoading(false);
            } catch (error) {
                console.error('[WorkspaceProvider] Error initializing workspace:', error);
                setStatus('error');
                setError(error instanceof Error ? error.message : 'Unknown error');
                setLoading(false);
            }
        };

        initializeWorkspace();
    }, [user]);

    /**
     * Select a workspace and persist the choice
     */
    const selectWorkspace = (workspace: Workspace) => {
        setCurrentWorkspace(workspace);
        setCurrentWorkspaceId(workspace.id);
        if (user) {
            const storageKey = `rf_active_workspace_${user.id}`;
            localStorage.setItem(storageKey, workspace.id);
        }
    };

    /**
     * Set current workspace by ID
     */
    const setCurrentWorkspaceIdHandler = (id: string) => {
        const workspace = workspaces.find(w => w.id === id);
        if (workspace) {
            selectWorkspace(workspace);
        }
    };

    /**
     * Add a newly created workspace and auto-select it
     */
    const addWorkspace = (workspace: Workspace) => {
        const updatedWorkspaces = [...workspaces, workspace];
        setWorkspaces(updatedWorkspaces);
        // Auto-select newly created workspace
        selectWorkspace(workspace);
    };

    /**
     * Create a new workspace
     */
    const createNewWorkspace = async (
        name: string,
        description?: string
    ): Promise<{ success: boolean; error?: string; workspace?: Workspace }> => {
        if (!user) {
            return { success: false, error: 'No user authenticated' };
        }

        try {
            const { data: workspace, error: createError } = await workspaceService.createWorkspace({
                name,
                description,
            });

            if (createError || !workspace) {
                return {
                    success: false,
                    error: createError?.message || 'Failed to create workspace',
                };
            }

            // Add to local state and select
            addWorkspace(workspace);

            return { success: true, workspace };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
            };
        }
    };

    /**
     * Refresh workspaces from the database
     */
    const refreshWorkspaces = async () => {
        if (!supabase || !user) return;

        try {
            setStatus('loading');
            const { data: userWorkspaces, error: fetchError } = await workspaceService.getWorkspaces();

            if (!fetchError && userWorkspaces) {
                setWorkspaces(userWorkspaces);
                setStatus('ready');
            } else {
                setStatus('error');
                setError(fetchError?.message || 'Failed to refresh workspaces');
            }
        } catch (error) {
            console.error('[WorkspaceProvider] Error refreshing workspaces:', error);
            setStatus('error');
            setError(error instanceof Error ? error.message : 'Unknown error');
        }
    };

    const value: WorkspaceContextValue = {
        status,
        currentWorkspace,
        currentWorkspaceId,
        workspaces,
        loading,
        user,
        error,
        selectWorkspace,
        setCurrentWorkspaceId: setCurrentWorkspaceIdHandler,
        addWorkspace,
        createNewWorkspace,
        refreshWorkspaces,
    };

    return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
};

export default WorkspaceContext;
