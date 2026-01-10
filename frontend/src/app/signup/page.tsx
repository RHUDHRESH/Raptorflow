"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Compass, Mail, Lock, User, ArrowRight } from 'lucide-react';
import dynamic from 'next/dynamic';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintInput } from '@/components/ui/BlueprintInput';
import { signUp } from '@/lib/auth';

const BlueprintButton = dynamic(() => import('@/components/ui/BlueprintButton').then(mod => ({ default: mod.BlueprintButton })), { ssr: false });

export const runtime = 'edge';

export default function SignupPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        const formData = new FormData(e.currentTarget);
        const email = formData.get('email') as string;
        const password = formData.get('password') as string;
        const fullName = formData.get('fullName') as string;

        try {
            // Create user account
            const user = signUp(email, fullName);

            // Redirect to dashboard after successful signup
            setTimeout(() => {
                router.push('/dashboard');
            }, 1000);

        } catch (error) {
            setError('Failed to create account. Please try again.');
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[var(--canvas)] relative overflow-hidden flex items-center justify-center p-4">
            <div className="fixed inset-0 blueprint-grid-major pointer-events-none opacity-30" />

            <div className="relative z-10 w-full max-w-md">
                <BlueprintCard figure="FIG. 01" code="AUTH-NEW" showCorners variant="elevated" padding="lg">
                    <div className="text-center mb-8">
                        <div className="flex justify-center mb-4">
                            <div className="h-12 w-12 rounded-[var(--radius-sm)] bg-[var(--ink)] text-[var(--paper)] flex items-center justify-center ink-bleed-md">
                                <Compass size={24} strokeWidth={1.5} />
                            </div>
                        </div>
                        <h1 className="font-serif text-3xl text-[var(--ink)] mb-2">Initialize Account</h1>
                        <p className="text-sm text-[var(--ink-secondary)] font-technical">Create your founder operating system.</p>
                    </div>

                    {error && (
                        <div className="mb-4 p-3 bg-[var(--error-light)] border border-[var(--error)] rounded-[var(--radius-sm)]">
                            <p className="text-sm text-[var(--error)] font-technical">{error}</p>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <BlueprintInput
                            label="Full Name"
                            type="text"
                            name="fullName"
                            placeholder="Jane Doe"
                            startIcon={<User size={16} />}
                            required
                        />

                        <BlueprintInput
                            label="Email Address"
                            type="email"
                            name="email"
                            placeholder="jane@start.up"
                            startIcon={<Mail size={16} />}
                            required
                        />

                        <BlueprintInput
                            label="Password"
                            type="password"
                            name="password"
                            placeholder="Min. 8 characters"
                            startIcon={<Lock size={16} />}
                            required
                        />

                        <BlueprintButton
                            type="submit"
                            className="w-full"
                            size="lg"
                        >
                            {loading ? 'Creating Account...' : 'Initialize Workspace'}
                        </BlueprintButton>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-sm text-[var(--ink-muted)] font-technical">
                            Already have an account?{' '}
                            <Link
                                href="/login"
                                className="text-[var(--blueprint)] hover:text-[var(--blueprint-dark)] transition-colors font-medium"
                            >
                                Sign In
                            </Link>
                        </p>
                    </div>

                    <div className="mt-4 text-center">
                        <p className="text-xs text-[var(--ink-ghost)] font-technical">
                            Demo: Use any email/password to signup
                        </p>
                    </div>
                </BlueprintCard>
            </div>
        </div>
    );
}
