"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { Compass, Mail, Lock, User, ArrowRight, Eye, EyeOff } from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintInput } from '@/components/ui/BlueprintInput';

const BlueprintButton = dynamic(() => import('@/components/ui/BlueprintButton').then(mod => ({ default: mod.BlueprintButton })), { ssr: false });

export const runtime = 'edge';

export default function LoginPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        const formData = new FormData(e.currentTarget);
        const email = formData.get('email') as string;
        const password = formData.get('password') as string;

        try {
            // Try to login with the bypass system
            const userStr = localStorage.getItem('raptorflow_user');
            const sessionStr = localStorage.getItem('raptorflow_session');

            if (userStr && sessionStr) {
                const user = JSON.parse(userStr);
                const session = JSON.parse(sessionStr);

                // Check if email matches stored user
                if (user.email === email) {
                    // Update session with new timestamp
                    const updatedSession = {
                        ...session,
                        expires_at: new Date(Date.now() + 3600000).toISOString()
                    };
                    localStorage.setItem('raptorflow_session', JSON.stringify(updatedSession));

                    // Redirect to dashboard
                    router.push('/dashboard');
                    return;
                }
            }

            // If no matching user, try to create one (signup flow)
            const mockUserId = `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

            const mockUser = {
                id: mockUserId,
                email: email,
                fullName: email.split('@')[0],
                subscriptionPlan: 'soar',
                subscriptionStatus: 'active',
                createdAt: new Date().toISOString()
            };

            localStorage.setItem('raptorflow_user', JSON.stringify(mockUser));
            localStorage.setItem('raptorflow_session', JSON.stringify({
                access_token: 'bypass-access-token',
                user: mockUser,
                expires_at: new Date(Date.now() + 3600000).toISOString()
            }));

            router.push('/dashboard');

        } catch (error) {
            setError('Authentication failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[var(--canvas)] relative overflow-hidden flex items-center justify-center p-4">
            <div className="fixed inset-0 blueprint-grid-major pointer-events-none opacity-30" />

            <div className="relative z-10 w-full max-w-md">
                <BlueprintCard figure="FIG. 01" code="AUTH-LOGIN" showCorners variant="elevated" padding="lg">
                    <div className="text-center mb-8">
                        <div className="flex justify-center mb-4">
                            <div className="h-12 w-12 rounded-[var(--radius-sm)] bg-[var(--ink)] text-[var(--paper)] flex items-center justify-center ink-bleed-md">
                                <Compass size={24} strokeWidth={1.5} />
                            </div>
                        </div>
                        <h1 className="font-serif text-3xl text-[var(--ink)] mb-2">Welcome Back</h1>
                        <p className="text-sm text-[var(--ink-secondary)] font-technical">Access your founder operating system.</p>
                    </div>

                    {error && (
                        <div className="mb-4 p-3 bg-[var(--error-light)] border border-[var(--error)] rounded-[var(--radius-sm)]">
                            <p className="text-sm text-[var(--error)] font-technical">{error}</p>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <BlueprintInput
                            label="Email Address"
                            type="email"
                            name="email"
                            placeholder="Enter your email"
                            startIcon={<Mail size={16} />}
                            required
                        />

                        <BlueprintInput
                            label="Password"
                            type={showPassword ? "text" : "password"}
                            name="password"
                            placeholder="Enter your password"
                            startIcon={<Lock size={16} />}
                            endIcon={
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="text-[var(--ink-muted)] hover:text-[var(--ink)] transition-colors"
                                >
                                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                                </button>
                            }
                            required
                        />

                        <BlueprintButton
                            type="submit"
                            className="w-full"
                            size="lg"
                        >
                            {loading ? 'Authenticating...' : 'Sign In'}
                        </BlueprintButton>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-sm text-[var(--ink-muted)] font-technical">
                            Don't have an account?{' '}
                            <Link
                                href="/signup"
                                className="text-[var(--blueprint)] hover:text-[var(--blueprint-dark)] transition-colors font-medium"
                            >
                                Sign up
                            </Link>
                        </p>
                    </div>

                    <div className="mt-4 text-center">
                        <p className="text-xs text-[var(--ink-ghost)] font-technical">
                            Demo: Use any email/password to login
                        </p>
                    </div>
                </BlueprintCard>
            </div>
        </div>
    );
}
