import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useWorkspace } from '../context/WorkspaceContext';
import { workspaceService, type Workspace } from '../services/workspaceService';
import { Sparkles, Plus, ArrowRight, Building2, Users, Loader2, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Workspace Page
 * 
 * Workspace selection and creation page.
 * Users can select an existing workspace or create a new one.
 * 
 * Flow:
 * - If user has no workspaces: Show create form
 * - If user has one workspace: Auto-select and redirect
 * - If user has multiple workspaces: Show selector
 */
export default function WorkspacePage() {
    const { user, logout } = useAuth();
    const { workspaces, currentWorkspace, selectWorkspace, addWorkspace, loading: workspaceLoading } = useWorkspace();
    const navigate = useNavigate();

    // Local state
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [workspaceName, setWorkspaceName] = useState('');
    const [workspaceDescription, setWorkspaceDescription] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [createError, setCreateError] = useState<string | null>(null);

    // Auto-redirect if workspace is already selected
    useEffect(() => {
        if (currentWorkspace && !workspaceLoading) {
            // Workspace is selected, redirect to dashboard
            navigate('/dashboard', { replace: true });
        }
    }, [currentWorkspace, workspaceLoading, navigate]);

    // Auto-show create form if no workspaces
    useEffect(() => {
        if (!workspaceLoading && workspaces.length === 0) {
            setShowCreateForm(true);
        }
    }, [workspaceLoading, workspaces]);

    // Handle workspace selection
    const handleSelectWorkspace = (workspace: Workspace) => {
        selectWorkspace(workspace);
        // Redirect will happen via useEffect
    };

    // Handle workspace creation
    const handleCreateWorkspace = async (e: React.FormEvent) => {
        e.preventDefault();
        setCreateError(null);

        // Validation
        if (!workspaceName.trim()) {
            setCreateError('Workspace name is required');
            return;
        }

        setIsCreating(true);

        try {
            const { data: newWorkspace, error } = await workspaceService.createWorkspace({
                name: workspaceName.trim(),
                description: workspaceDescription.trim() || undefined,
            });

            if (error) {
                setCreateError(error.message || 'Failed to create workspace');
                setIsCreating(false);
                return;
            }

            if (newWorkspace) {
                // Add to context and auto-select
                addWorkspace(newWorkspace);
                // Redirect will happen via useEffect
            }
        } catch (error) {
            setCreateError('An unexpected error occurred');
            setIsCreating(false);
        }
    };

    const handleLogout = async () => {
        await logout();
    };

    // Show loading state
    if (workspaceLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-white">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 animate-spin text-neutral-900 mx-auto mb-4" />
                    <p className="text-neutral-600">Loading workspaces...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-neutral-50">
            {/* Header */}
            <header className="bg-white border-b border-neutral-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        {/* Logo */}
                        <div className="flex items-center gap-2">
                            <div className="h-8 w-8 rounded-full bg-neutral-900 flex items-center justify-center">
                                <Sparkles className="w-4 h-4 text-white" />
                            </div>
                            <span className="text-xl font-bold tracking-widest uppercase font-serif">
                                RaptorFlow
                            </span>
                        </div>

                        {/* User Menu */}
                        <div className="flex items-center gap-4">
                            <div className="text-right hidden sm:block">
                                <p className="text-sm font-medium text-neutral-900">
                                    {user?.user_metadata?.full_name || user?.email}
                                </p>
                            </div>
                            <button
                                onClick={handleLogout}
                                className="text-sm text-neutral-600 hover:text-neutral-900 transition-colors"
                            >
                                Sign Out
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-12"
                >
                    <h1 className="text-4xl font-bold text-neutral-900 mb-4">
                        {workspaces.length === 0 ? 'Create your workspace' : 'Select a workspace'}
                    </h1>
                    <p className="text-lg text-neutral-600">
                        {workspaces.length === 0
                            ? 'Get started by creating your first workspace'
                            : 'Choose a workspace to continue'}
                    </p>
                </motion.div>

                {/* Workspace List */}
                {workspaces.length > 0 && !showCreateForm && (
                    <div className="space-y-4 mb-8">
                        <AnimatePresence>
                            {workspaces.map((workspace, index) => (
                                <motion.button
                                    key={workspace.id}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                    onClick={() => handleSelectWorkspace(workspace)}
                                    className="w-full bg-white border border-neutral-200 rounded-xl p-6 hover:border-neutral-900 hover:shadow-lg transition-all group text-left"
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-4">
                                            <div className="h-12 w-12 rounded-lg bg-neutral-100 flex items-center justify-center group-hover:bg-neutral-900 transition-colors">
                                                <Building2 className="h-6 w-6 text-neutral-600 group-hover:text-white transition-colors" />
                                            </div>
                                            <div>
                                                <h3 className="text-lg font-semibold text-neutral-900 mb-1">
                                                    {workspace.name}
                                                </h3>
                                                {workspace.description && (
                                                    <p className="text-sm text-neutral-500">{workspace.description}</p>
                                                )}
                                                <div className="flex items-center gap-2 mt-2">
                                                    <span className="text-xs text-neutral-400 capitalize">
                                                        {workspace.plan || 'Free'} Plan
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <ArrowRight className="h-5 w-5 text-neutral-400 group-hover:text-neutral-900 transition-colors" />
                                    </div>
                                </motion.button>
                            ))}
                        </AnimatePresence>
                    </div>
                )}

                {/* Create New Workspace Button */}
                {workspaces.length > 0 && !showCreateForm && (
                    <div className="text-center">
                        <button
                            onClick={() => setShowCreateForm(true)}
                            className="inline-flex items-center gap-2 px-6 py-3 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 transition-colors"
                        >
                            <Plus className="h-5 w-5" />
                            <span>Create New Workspace</span>
                        </button>
                    </div>
                )}

                {/* Create Workspace Form */}
                {showCreateForm && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-white rounded-xl border border-neutral-200 p-8 max-w-2xl mx-auto"
                    >
                        <div className="text-center mb-6">
                            <div className="h-16 w-16 rounded-full bg-neutral-100 flex items-center justify-center mx-auto mb-4">
                                <Building2 className="h-8 w-8 text-neutral-600" />
                            </div>
                            <h2 className="text-2xl font-bold text-neutral-900 mb-2">Create Workspace</h2>
                            <p className="text-neutral-600">
                                Set up a new workspace for your team or project
                            </p>
                        </div>

                        <form onSubmit={handleCreateWorkspace} className="space-y-5">
                            {/* Workspace Name */}
                            <div>
                                <label htmlFor="name" className="block text-sm font-medium text-neutral-700 mb-2">
                                    Workspace Name *
                                </label>
                                <input
                                    id="name"
                                    type="text"
                                    required
                                    value={workspaceName}
                                    onChange={(e) => setWorkspaceName(e.target.value)}
                                    className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-transparent transition-all"
                                    placeholder="Acme Inc."
                                    disabled={isCreating}
                                />
                            </div>

                            {/* Workspace Description */}
                            <div>
                                <label
                                    htmlFor="description"
                                    className="block text-sm font-medium text-neutral-700 mb-2"
                                >
                                    Description (Optional)
                                </label>
                                <textarea
                                    id="description"
                                    value={workspaceDescription}
                                    onChange={(e) => setWorkspaceDescription(e.target.value)}
                                    className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-transparent transition-all resize-none"
                                    placeholder="A brief description of your workspace..."
                                    rows={3}
                                    disabled={isCreating}
                                />
                            </div>

                            {/* Error Message */}
                            <AnimatePresence>
                                {createError && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: 'auto' }}
                                        exit={{ opacity: 0, height: 0 }}
                                        className="p-3 rounded-lg bg-red-50 border border-red-100 text-sm text-red-600"
                                    >
                                        {createError}
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            {/* Buttons */}
                            <div className="flex gap-3">
                                {workspaces.length > 0 && (
                                    <button
                                        type="button"
                                        onClick={() => setShowCreateForm(false)}
                                        disabled={isCreating}
                                        className="flex-1 px-4 py-3 border border-neutral-200 text-neutral-700 rounded-lg hover:bg-neutral-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        Cancel
                                    </button>
                                )}
                                <button
                                    type="submit"
                                    disabled={isCreating}
                                    className="flex-1 bg-neutral-900 text-white py-3 px-4 rounded-lg font-medium hover:bg-neutral-800 focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                                >
                                    {isCreating ? (
                                        <>
                                            <Loader2 className="h-5 w-5 animate-spin" />
                                            <span>Creating...</span>
                                        </>
                                    ) : (
                                        <>
                                            <CheckCircle2 className="h-5 w-5" />
                                            <span>Create Workspace</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>
                    </motion.div>
                )}
            </main>
        </div>
    );
}
