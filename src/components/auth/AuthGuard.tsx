"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { clientAuth } from '@/lib/auth-service';
import { BlueprintLoader } from '@/components/ui/BlueprintLoader';

interface AuthGuardProps {
  children: React.ReactNode;
  redirectTo?: string;
}

export function AuthGuard({ children, redirectTo = '/signin' }: AuthGuardProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [isUserAuthenticated, setIsUserAuthenticated] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const authenticated = await clientAuth.isAuthenticated()
        setIsUserAuthenticated(authenticated)

        if (!authenticated) {
          router.push(redirectTo);
        }
      } catch (error) {
        console.error('Error checking auth:', error)
        setIsUserAuthenticated(false)
        router.push(redirectTo)
      }

      setIsLoading(false);
    };

    checkAuth();
  }, [router, redirectTo]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center">
        <BlueprintLoader size="lg" />
      </div>
    );
  }

  if (!isUserAuthenticated) {
    return (
      <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center">
        <BlueprintLoader size="lg" />
      </div>
    );
  }

  return <>{children}</>;
}

export function AuthenticatedContent({ children }: { children: React.ReactNode }) {
  const [isUserAuthenticated, setIsUserAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      const supabase = createClient()
      if (!supabase) {
        setIsLoading(false)
        return
      }

      try {
        const { data: { session } } = await supabase.auth.getSession()
        const authenticated = !!session
        setIsUserAuthenticated(authenticated);

        if (!authenticated) {
          router.push('/signin');
        }
      } catch (error) {
        console.error('Error checking auth:', error)
        setIsUserAuthenticated(false)
        router.push('/signin')
      }
      setIsLoading(false);
    };

    checkAuth();
  }, [router]);

  if (isLoading || !isUserAuthenticated) {
    return (
      <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center">
        <BlueprintLoader size="lg" />
      </div>
    );
  }

  return <>{children}</>;
}
