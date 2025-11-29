import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

/**
 * Auth Debug Page
 * 
 * Development-only page for testing authentication functionality.
 * Displays current auth state and provides simple controls for testing.
 */
export default function AuthDebug() {
    const { status, user, session, subscription, onboardingCompleted, login, logout } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setMessage('');
        setIsLoading(true);

        try {
            const result = await login(email, password);
            if (result.success) {
                setMessage('✅ Login successful!');
                setEmail('');
                setPassword('');
            } else {
                setMessage(`❌ Login failed: ${result.error}`);
            }
        } catch (error) {
            setMessage(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
            setIsLoading(false);
        }
    };

    const handleLogout = async () => {
        setMessage('');
        setIsLoading(true);

        try {
            await logout();
            setMessage('✅ Logged out successfully!');
        } catch (error) {
            setMessage(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            backgroundColor: '#0a0a0a',
            color: '#ffffff',
            padding: '2rem',
            fontFamily: 'Inter, system-ui, sans-serif',
        }}>
            <div style={{
                maxWidth: '800px',
                margin: '0 auto',
            }}>
                {/* Header */}
                <div style={{
                    marginBottom: '2rem',
                    borderBottom: '1px solid #333',
                    paddingBottom: '1rem',
                }}>
                    <h1 style={{
                        fontSize: '2rem',
                        fontWeight: '700',
                        marginBottom: '0.5rem',
                    }}>
                        🔐 Auth Debug Console
                    </h1>
                    <p style={{
                        color: '#888',
                        fontSize: '0.875rem',
                    }}>
                        Development-only page for testing authentication
                    </p>
                </div>

                {/* Status Section */}
                <section style={{
                    backgroundColor: '#111',
                    border: '1px solid #333',
                    borderRadius: '8px',
                    padding: '1.5rem',
                    marginBottom: '1.5rem',
                }}>
                    <h2 style={{
                        fontSize: '1.25rem',
                        fontWeight: '600',
                        marginBottom: '1rem',
                        color: '#fff',
                    }}>
                        Current Status
                    </h2>

                    <div style={{ display: 'grid', gap: '0.75rem' }}>
                        <StatusRow
                            label="Auth Status"
                            value={status}
                            color={status === 'authenticated' ? '#10b981' : status === 'loading' ? '#f59e0b' : '#ef4444'}
                        />
                        <StatusRow
                            label="User ID"
                            value={user?.id || 'N/A'}
                        />
                        <StatusRow
                            label="Email"
                            value={user?.email || 'N/A'}
                        />
                        <StatusRow
                            label="Name"
                            value={user?.user_metadata?.full_name || 'N/A'}
                        />
                        <StatusRow
                            label="Session Active"
                            value={session ? 'Yes' : 'No'}
                            color={session ? '#10b981' : '#ef4444'}
                        />
                        <StatusRow
                            label="Subscription Plan"
                            value={subscription?.plan || 'N/A'}
                        />
                        <StatusRow
                            label="Onboarding Complete"
                            value={onboardingCompleted ? 'Yes' : 'No'}
                            color={onboardingCompleted ? '#10b981' : '#f59e0b'}
                        />
                    </div>
                </section>

                {/* Session Details */}
                {session && (
                    <section style={{
                        backgroundColor: '#111',
                        border: '1px solid #333',
                        borderRadius: '8px',
                        padding: '1.5rem',
                        marginBottom: '1.5rem',
                    }}>
                        <h2 style={{
                            fontSize: '1.25rem',
                            fontWeight: '600',
                            marginBottom: '1rem',
                            color: '#fff',
                        }}>
                            Session Details
                        </h2>

                        <pre style={{
                            backgroundColor: '#0a0a0a',
                            border: '1px solid #333',
                            borderRadius: '4px',
                            padding: '1rem',
                            overflow: 'auto',
                            fontSize: '0.75rem',
                            color: '#10b981',
                        }}>
                            {JSON.stringify(session, null, 2)}
                        </pre>
                    </section>
                )}

                {/* Actions Section */}
                <section style={{
                    backgroundColor: '#111',
                    border: '1px solid #333',
                    borderRadius: '8px',
                    padding: '1.5rem',
                    marginBottom: '1.5rem',
                }}>
                    <h2 style={{
                        fontSize: '1.25rem',
                        fontWeight: '600',
                        marginBottom: '1rem',
                        color: '#fff',
                    }}>
                        Actions
                    </h2>

                    {status === 'authenticated' ? (
                        <div>
                            <button
                                onClick={handleLogout}
                                disabled={isLoading}
                                style={{
                                    backgroundColor: '#ef4444',
                                    color: '#fff',
                                    padding: '0.75rem 1.5rem',
                                    borderRadius: '6px',
                                    border: 'none',
                                    fontSize: '0.875rem',
                                    fontWeight: '600',
                                    cursor: isLoading ? 'not-allowed' : 'pointer',
                                    opacity: isLoading ? 0.5 : 1,
                                    transition: 'all 0.2s',
                                }}
                                onMouseEnter={(e) => {
                                    if (!isLoading) {
                                        e.currentTarget.style.backgroundColor = '#dc2626';
                                    }
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.backgroundColor = '#ef4444';
                                }}
                            >
                                {isLoading ? 'Signing out...' : 'Sign Out'}
                            </button>
                        </div>
                    ) : (
                        <form onSubmit={handleLogin} style={{ display: 'grid', gap: '1rem' }}>
                            <div>
                                <label style={{
                                    display: 'block',
                                    fontSize: '0.875rem',
                                    fontWeight: '500',
                                    marginBottom: '0.5rem',
                                    color: '#ccc',
                                }}>
                                    Email
                                </label>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    style={{
                                        width: '100%',
                                        backgroundColor: '#0a0a0a',
                                        border: '1px solid #333',
                                        borderRadius: '6px',
                                        padding: '0.75rem',
                                        color: '#fff',
                                        fontSize: '0.875rem',
                                    }}
                                    placeholder="dev@raptorflow.local"
                                />
                            </div>

                            <div>
                                <label style={{
                                    display: 'block',
                                    fontSize: '0.875rem',
                                    fontWeight: '500',
                                    marginBottom: '0.5rem',
                                    color: '#ccc',
                                }}>
                                    Password
                                </label>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    style={{
                                        width: '100%',
                                        backgroundColor: '#0a0a0a',
                                        border: '1px solid #333',
                                        borderRadius: '6px',
                                        padding: '0.75rem',
                                        color: '#fff',
                                        fontSize: '0.875rem',
                                    }}
                                    placeholder="••••••••"
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={isLoading}
                                style={{
                                    backgroundColor: '#10b981',
                                    color: '#fff',
                                    padding: '0.75rem 1.5rem',
                                    borderRadius: '6px',
                                    border: 'none',
                                    fontSize: '0.875rem',
                                    fontWeight: '600',
                                    cursor: isLoading ? 'not-allowed' : 'pointer',
                                    opacity: isLoading ? 0.5 : 1,
                                    transition: 'all 0.2s',
                                }}
                                onMouseEnter={(e) => {
                                    if (!isLoading) {
                                        e.currentTarget.style.backgroundColor = '#059669';
                                    }
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.backgroundColor = '#10b981';
                                }}
                            >
                                {isLoading ? 'Signing in...' : 'Sign In'}
                            </button>
                        </form>
                    )}

                    {message && (
                        <div style={{
                            marginTop: '1rem',
                            padding: '0.75rem',
                            backgroundColor: message.startsWith('✅') ? '#10b98120' : '#ef444420',
                            border: `1px solid ${message.startsWith('✅') ? '#10b981' : '#ef4444'}`,
                            borderRadius: '6px',
                            fontSize: '0.875rem',
                            color: message.startsWith('✅') ? '#10b981' : '#ef4444',
                        }}>
                            {message}
                        </div>
                    )}
                </section>

                {/* Info Section */}
                <section style={{
                    backgroundColor: '#111',
                    border: '1px solid #333',
                    borderRadius: '8px',
                    padding: '1.5rem',
                }}>
                    <h2 style={{
                        fontSize: '1.25rem',
                        fontWeight: '600',
                        marginBottom: '1rem',
                        color: '#fff',
                    }}>
                        ℹ️ Info
                    </h2>

                    <ul style={{
                        listStyle: 'none',
                        padding: 0,
                        margin: 0,
                        fontSize: '0.875rem',
                        color: '#888',
                        lineHeight: '1.75',
                    }}>
                        <li>• This page is for development and testing only</li>
                        <li>• Auth state is managed by AuthContext</li>
                        <li>• All auth operations go through authService</li>
                        <li>• Session persists across page reloads</li>
                        <li>• Check browser console for detailed logs</li>
                    </ul>
                </section>
            </div>
        </div>
    );
}

// Helper component for status rows
function StatusRow({ label, value, color }: { label: string; value: string; color?: string }) {
    return (
        <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '0.5rem 0',
            borderBottom: '1px solid #222',
        }}>
            <span style={{ color: '#888', fontSize: '0.875rem' }}>{label}</span>
            <span style={{
                color: color || '#fff',
                fontSize: '0.875rem',
                fontWeight: '600',
                fontFamily: 'JetBrains Mono, monospace',
            }}>
                {value}
            </span>
        </div>
    );
}
