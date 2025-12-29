'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { Button } from '@/components/ui/button';
import { FadeIn, Stagger } from '@/components/ui/motion';
import { toast } from 'sonner';
import Link from 'next/link';

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleGoogleAuth = async () => {
    setLoading(true);
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      });
      if (error) {
        throw error;
      }
    } catch (error: any) {
      toast.error('Authentication error', {
        description: error.message || 'Unable to start Google login.',
      });
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
                  Welcome back
                </h1>
                <p className="text-muted-foreground text-lg">
                  Sign in with Google to continue.
                </p>
              </div>
            </div>
          </FadeIn>

          <FadeIn delay={1}>
            <div className="bg-card border border-border rounded-2xl p-8 shadow-sm">
              <Button
                type="button"
                onClick={handleGoogleAuth}
                disabled={loading}
                className="w-full h-14 text-lg rounded-xl font-medium shadow-md shadow-foreground/5"
              >
                {loading ? 'Redirecting...' : 'Continue with Google'}
              </Button>
            </div>
          </FadeIn>

          <FadeIn delay={2}>
            <p className="text-center text-muted-foreground">
              Questions?{' '}
              <Link
                href="/contact"
                className="text-foreground font-semibold hover:underline underline-offset-4"
              >
                Contact support
              </Link>
            </p>
          </FadeIn>
        </Stagger>
      </div>
    </div>
  );
}
