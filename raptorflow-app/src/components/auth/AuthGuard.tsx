'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';

interface AuthGuardProps {
  children: React.ReactNode;
}

export function AuthGuard({ children }: AuthGuardProps) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [hasAccess, setHasAccess] = useState<boolean | null>(null);
  const router = useRouter();

  useEffect(() => {
    async function checkAuth() {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        setIsAuthenticated(false);
        router.push('/login');
      } else {
        setIsAuthenticated(true);
        setHasAccess(true);
      }
    }

    checkAuth();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!session) {
        setIsAuthenticated(false);
        setHasAccess(false);
        router.push('/login');
      } else {
        setIsAuthenticated(true);
        setHasAccess(true);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [router]);

  if (isAuthenticated === null || hasAccess === null) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-canvas">
        <div className="animate-pulse text-muted-foreground font-mono">
          Authenticating...
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !hasAccess) {
    return null;
  }

  return <>{children}</>;
}
