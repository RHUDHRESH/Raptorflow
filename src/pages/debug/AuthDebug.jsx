import React from 'react';
import { useAuth } from '../../context/AuthContext.tsx';
import { isSupabaseConfigured } from '../../lib/supabase';

/**
 * Auth Debug Page
 * 
 * Development-only page for debugging authentication state and configuration.
 * Shows current auth status, user info, session details, and environment config.
 */
export default function AuthDebug() {
    const { status, user, session, subscription, error } = useAuth();
    const [signOutLoading, setSignOutLoading] = React.useState(false);
    const auth = useAuth();

    const handleSignOut = async () => {
        setSignOutLoading(true);
        try {
            await auth.signOut();
        } catch (err) {
            console.error('Sign out error:', err);
        } finally {
            setSignOutLoading(false);
        }
    };

    // Check environment configuration
    const envConfig = {
        supabaseConfigured: isSupabaseConfigured(),
        supabaseUrl: import.meta.env.VITE_SUPABASE_URL || '(not set)',
        hasAnonKey: !!import.meta.env.VITE_SUPABASE_ANON_KEY,
        environment: import.meta.env.VITE_ENVIRONMENT || 'development',
    };

    return (
        <div className="min-h-screen bg-obsidian p-8">
            <div className="max-w-4xl mx-auto space-y-6">
                {/* Header */}
                <div className="border-b border-glass-border pb-4">
                    <h1 className="text-3xl font-display font-bold text-white">
                        🔍 Auth Debug
                    </h1>
                    <p className="text-obsidian-500 mt-2">
                        Development-only authentication state inspector
                    </p>
                </div>

                {/* Environment Config */}
                <div className="bg-obsidian-100 border border-glass-border rounded-lg p-6">
                    <h2 className="text-xl font-semibold text-white mb-4">
                        Environment Configuration
                    </h2>
                    <dl className="grid grid-cols-2 gap-4">
                        <div>
                            <dt className="text-sm text-obsidian-500">Supabase Configured</dt>
                            <dd className={`text-lg font-mono ${envConfig.supabaseConfigured ? 'text-neon-green' : 'text-neon-red'}`}>
                                {envConfig.supabaseConfigured ? '✅ Yes' : '❌ No'}
                            </dd>
                        </div>
                        <div>
                            <dt className="text-sm text-obsidian-500">Environment</dt>
                            <dd className="text-lg font-mono text-white">{envConfig.environment}</dd>
                        </div>
                        <div className="col-span-2">
                            <dt className="text-sm text-obsidian-500">Supabase URL</dt>
                            <dd className="text-sm font-mono text-white break-all">{envConfig.supabaseUrl}</dd>
                        </div>
                        <div>
                            <dt className="text-sm text-obsidian-500">Anon Key Present</dt>
                            <dd className={`text-lg font-mono ${envConfig.hasAnonKey ? 'text-neon-green' : 'text-neon-red'}`}>
                                {envConfig.hasAnonKey ? '✅ Yes' : '❌ No'}
                            </dd>
                        </div>
                    </dl>
                </div>

                {/* Auth Status */}
                <div className="bg-obsidian-100 border border-glass-border rounded-lg p-6">
                    <h2 className="text-xl font-semibold text-white mb-4">Auth Status</h2>
                    <dl className="space-y-3">
                        <div>
                            <dt className="text-sm text-obsidian-500">Status</dt>
                            <dd className="flex items-center gap-2 mt-1">
                                <span className={`inline-block w-3 h-3 rounded-full ${status === 'authenticated' ? 'bg-neon-green' :
                                        status === 'loading' ? 'bg-neon-blue animate-pulse' :
                                            'bg-obsidian-400'
                                    }`}></span>
                                <span className="text-lg font-mono text-white">{status}</span>
                            </dd>
                        </div>
                        {error && (
                            <div>
                                <dt className="text-sm text-neon-red">Error</dt>
                                <dd className="text-sm font-mono text-neon-red bg-neon-red/10 p-3 rounded mt-1">
                                    {error}
                                </dd>
                            </div>
                        )}
                    </dl>
                </div>

                {/* User Info */}
                {user ? (
                    <div className="bg-obsidian-100 border border-glass-border rounded-lg p-6">
                        <h2 className="text-xl font-semibold text-white mb-4">User Info</h2>
                        <dl className="space-y-3">
                            <div>
                                <dt className="text-sm text-obsidian-500">ID</dt>
                                <dd className="text-sm font-mono text-white break-all">{user.id}</dd>
                            </div>
                            <div>
                                <dt className="text-sm text-obsidian-500">Email</dt>
                                <dd className="text-lg font-mono text-white">{user.email || '(no email)'}</dd>
                            </div>
                            {user.user_metadata?.full_name && (
                                <div>
                                    <dt className="text-sm text-obsidian-500">Full Name</dt>
                                    <dd className="text-lg text-white">{user.user_metadata.full_name}</dd>
                                </div>
                            )}
                            <div>
                                <dt className="text-sm text-obsidian-500">Created At</dt>
                                <dd className="text-sm text-white">
                                    {user.created_at ? new Date(user.created_at).toLocaleString() : 'N/A'}
                                </dd>
                            </div>
                            <div>
                                <dt className="text-sm text-obsidian-500">User Metadata</dt>
                                <dd className="text-xs font-mono text-obsidian-400 bg-obsidian-900 p-3 rounded mt-1 overflow-auto max-h-40">
                                    <pre>{JSON.stringify(user.user_metadata, null, 2)}</pre>
                                </dd>
                            </div>
                        </dl>
                    </div>
                ) : (
                    <div className="bg-obsidian-100 border border-glass-border rounded-lg p-6">
                        <h2 className="text-xl font-semibold text-white mb-2">User Info</h2>
                        <p className="text-obsidian-400">No user authenticated</p>
                    </div>
                )}

                {/* Session Info */}
                {session ? (
                    <div className="bg-obsidian-100 border border-glass-border rounded-lg p-6">
                        <h2 className="text-xl font-semibold text-white mb-4">Session Info</h2>
                        <dl className="space-y-3">
                            <div>
                                <dt className="text-sm text-obsidian-500">Access Token (first 50 chars)</dt>
                                <dd className="text-xs font-mono text-white break-all">
                                    {session.access_token.substring(0, 50)}...
                                </dd>
                            </div>
                            <div>
                                <dt className="text-sm text-obsidian-500">Expires At</dt>
                                <dd className="text-sm text-white">
                                    {session.expires_at ? new Date(session.expires_at * 1000).toLocaleString() : 'N/A'}
                                </dd>
                            </div>
                            <div>
                                <dt className="text-sm text-obsidian-500">Full Session Object</dt>
                                <dd className="text-xs font-mono text-obsidian-400 bg-obsidian-900 p-3 rounded mt-1 overflow-auto max-h-60">
                                    <pre>{JSON.stringify(session, null, 2)}</pre>
                                </dd>
                            </div>
                        </dl>
                    </div>
                ) : null}

                {/* Subscription Info */}
                {subscription && (
                    <div className="bg-obsidian-100 border border-glass-border rounded-lg p-6">
                        <h2 className="text-xl font-semibold text-white mb-4">Subscription Info</h2>
                        <dl className="space-y-3">
                            <div>
                                <dt className="text-sm text-obsidian-500">Plan</dt>
                                <dd className="text-lg font-mono text-white capitalize">{subscription.plan}</dd>
                            </div>
                            <div>
                                <dt className="text-sm text-obsidian-500">Status</dt>
                                <dd className={`text-lg font-mono ${subscription.status === 'active' ? 'text-neon-green' : 'text-obsidian-400'}`}>
                                    {subscription.status}
                                </dd>
                            </div>
                            {subscription.billing_period && (
                                <div>
                                    <dt className="text-sm text-obsidian-500">Billing Period</dt>
                                    <dd className="text-lg text-white capitalize">{subscription.billing_period}</dd>
                                </div>
                            )}
                        </dl>
                    </div>
                )}

                {/* Actions */}
                <div className="flex gap-4">
                    {user && (
                        <button
                            onClick={handleSignOut}
                            disabled={signOutLoading}
                            className="px-6 py-3 bg-neon-red/20 hover:bg-neon-red/30 border border-neon-red text-neon-red rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {signOutLoading ? 'Signing out...' : 'Sign Out'}
                        </button>
                    )}
                    <a
                        href="/auth"
                        className="px-6 py-3 bg-glass hover:bg-glass-hover border border-glass-border text-white rounded-lg transition-all text-center"
                    >
                        Go to Auth Page
                    </a>
                    <a
                        href="/"
                        className="px-6 py-3 bg-glass hover:bg-glass-hover border border-glass-border text-white rounded-lg transition-all text-center"
                    >
                        Go to Landing
                    </a>
                </div>

                {/* Dev Note */}
                <div className="bg-neon-purple/10 border border-neon-purple/30 rounded-lg p-4">
                    <p className="text-sm text-neon-purple">
                        <strong>Note:</strong> This page is for development purposes only.
                        Remove or protect it in production builds.
                    </p>
                </div>
            </div>
        </div>
    );
}
