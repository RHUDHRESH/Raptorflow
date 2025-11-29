import React from 'react';
import { Navigate, useLocation, Outlet } from 'react-router-dom';
import { useWorkspace } from '../context/WorkspaceContext';
import { Loader2 } from 'lucide-react';

/**
 * WorkspaceGuard Component
 * 
 * Protects routes that require an active workspace.
 * Redirects to workspace creation if no workspace exists.
 */
export const WorkspaceGuard: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
    const { status, currentWorkspace, workspaces } = useWorkspace();
    const location = useLocation();

    if (status === 'loading' || status === 'idle') {
         return (
            <div className="flex items-center justify-center min-h-screen bg-white">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 animate-spin text-neutral-900 mx-auto mb-4" />
                    <p className="text-neutral-600">Loading workspace...</p>
                </div>
            </div>
        );
    }

    // If no workspaces at all, redirect to create
    if (workspaces.length === 0) {
        // Prevent infinite redirect if already on create page
        if (location.pathname === '/workspace/create') {
             return <>{children || <Outlet />}</>;
        }
        return <Navigate to="/workspace/create" state={{ from: location }} replace />;
    }

    // If workspaces exist but none selected (shouldn't happen due to auto-select, but just in case)
    if (!currentWorkspace) {
        // Redirect to the first available workspace or a selector
        // For now, let's trust the context to auto-select, or redirect to first one
         return (
            <div className="flex items-center justify-center min-h-screen bg-white">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 animate-spin text-neutral-900 mx-auto mb-4" />
                    <p className="text-neutral-600">Selecting workspace...</p>
                </div>
            </div>
        );
    }

    return <>{children || <Outlet />}</>;
};

export default WorkspaceGuard;
