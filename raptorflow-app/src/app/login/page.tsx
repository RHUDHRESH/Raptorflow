'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FadeIn, Stagger } from '@/components/ui/motion';
import { toast } from 'sonner';
import Link from 'next/link';

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [isSignUp, setIsSignUp] = useState(false);
    const router = useRouter();

    const handleAuth = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            if (isSignUp) {
                const { error } = await supabase.auth.signUp({
                    email,
                    password,
                    options: {
                        emailRedirectTo: `${window.location.origin}/auth/callback`,
                    },
                });
                if (error) throw error;
                toast.success('Registration successful!', {
                    description: 'Please check your email to verify your account.',
                });
            } else {
                const { error } = await supabase.auth.signInWithPassword({
                    email,
                    password,
                });
                if (error) throw error;
                toast.success('Welcome back!', {
                    description: 'Redirecting to your dashboard...',
                });
                router.push('/dashboard');
            }
        } catch (error: any) {
            toast.error('Authentication error', {
                description: error.message || 'Check your credentials and try again.',
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-canvas px-6 py-12">
            <div className="absolute inset-0 -z-10 overflow-hidden">
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 h-[800px] w-[800px] rounded-full bg-gradient-to-br from-foreground/5 to-transparent blur-3xl opacity-50" />
            </div>

            <div className="w-full max-w-md">
                <Stagger className="space-y-12">
                    <FadeIn>
                        <div className="text-center space-y-6">
                            <Link href="/" className="inline-block group">
                                <span className="font-display text-3xl font-semibold tracking-tighter text-foreground group-hover:text-muted-foreground transition-colors">
                                    RAPTORFLOW
                                </span>
                            </Link>
                            <div className="space-y-2">
                                <h1 className="font-display text-4xl font-medium tracking-tight text-foreground">
                                    {isSignUp ? 'Create your account' : 'Welcome back'}
                                </h1>
                                <p className="text-muted-foreground text-lg">
                                    {isSignUp
                                        ? 'Start your 14-day free trial today.'
                                        : 'Marketing. Finally under control.'}
                                </p>
                            </div>
                        </div>
                    </FadeIn>

                    <FadeIn delay={1}>
                        <div className="bg-card border border-border rounded-2xl p-8 shadow-sm">
                            <form onSubmit={handleAuth} className="space-y-6">
                                <div className="space-y-2">
                                    <Label htmlFor="email">Email Address</Label>
                                    <Input
                                        id="email"
                                        type="email"
                                        placeholder="founder@company.com"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        className="h-12 rounded-xl"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <div className="flex items-center justify-between">
                                        <Label htmlFor="password">Password</Label>
                                        {!isSignUp && (
                                            <button type="button" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
                                                Forgot password?
                                            </button>
                                        )}
                                    </div>
                                    <Input
                                        id="password"
                                        type="password"
                                        placeholder="••••••••"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                        className="h-12 rounded-xl"
                                    />
                                </div>

                                <Button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full h-14 text-lg rounded-xl font-medium shadow-md shadow-foreground/5"
                                >
                                    {loading ? 'Processing...' : (isSignUp ? 'Sign up' : 'Sign in')}
                                </Button>
                            </form>
                        </div>
                    </FadeIn>

                    <FadeIn delay={2}>
                        <p className="text-center text-muted-foreground">
                            {isSignUp ? 'Already have an account?' : "Don't have an account?"}{' '}
                            <button
                                onClick={() => setIsSignUp(!isSignUp)}
                                className="text-foreground font-semibold hover:underline underline-offset-4"
                            >
                                {isSignUp ? 'Sign in' : 'Create one for free'}
                            </button>
                        </p>
                    </FadeIn>
                </Stagger>
            </div>
        </div>
    );
}
