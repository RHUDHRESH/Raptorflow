"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Compass, ArrowRight } from 'lucide-react';
import dynamic from 'next/dynamic';
import { BlueprintCard } from '@/components/ui/BlueprintCard';

const BlueprintButton = dynamic(() => import('@/components/ui/BlueprintButton').then(mod => ({ default: mod.BlueprintButton })), { ssr: false });

export const runtime = 'edge';

export default function SignupPage() {
    const router = useRouter();

    useEffect(() => {
        // Auto-redirect to dashboard (bypass mode)
        const timer = setTimeout(() => {
            router.push('/dashboard');
        }, 1000);

        return () => clearTimeout(timer);
    }, [router]);

    return (
        <div className="min-h-screen bg-[var(--canvas)] relative overflow-hidden flex items-center justify-center p-4">
            <div className="fixed inset-0 blueprint-grid-major pointer-events-none opacity-30" />

            <div className="relative z-10 w-full max-w-md">
                <BlueprintCard figure="FIG. 01" code="AUTH-BYPASS" showCorners variant="elevated" padding="lg">
                    <div className="text-center mb-8">
                        <div className="flex justify-center mb-4">
                            <div className="h-12 w-12 rounded-[var(--radius-sm)] bg-[var(--ink)] text-[var(--paper)] flex items-center justify-center ink-bleed-md">
                                <Compass size={24} strokeWidth={1.5} />
                            </div>
                        </div>
                        <h1 className="font-serif text-3xl text-[var(--ink)] mb-2">Create Account</h1>
                        <p className="text-sm text-[var(--ink-secondary)] font-technical">Auto-setting up your workspace...</p>
                    </div>

                    <div className="mb-4 p-3 bg-[var(--success-light)] border border-[var(--success)] rounded-[var(--radius-sm)]">
                        <p className="text-sm text-[var(--success)] font-technical">Account created automatically - Redirecting to dashboard</p>
                    </div>

                    <div className="text-center">
                        <p className="text-xs text-[var(--ink-muted)] font-technical mb-4">
                            Demo Mode: No signup required
                        </p>

                        <Link href="/dashboard" className="inline-block">
                            <BlueprintButton
                                className="w-full"
                                size="lg"
                            >
                                <ArrowRight size={16} strokeWidth={1.5} />
                                Go to Dashboard
                            </BlueprintButton>
                        </Link>
                    </div>
                </BlueprintCard>
            </div>
        </div>
    );
}
