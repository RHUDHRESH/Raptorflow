"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated as checkIsAuthenticated, getCurrentUser } from '@/lib/auth';
import { BlueprintLoader } from '@/components/ui/BlueprintLoader';

interface AuthGuardProps {
  children: React.ReactNode;
  redirectTo?: string;
}

export function AuthGuard({ children, redirectTo = '/login' }: AuthGuardProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [isUserAuthenticated, setIsUserAuthenticated] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      const authenticated = await checkIsAuthenticated();
      setIsUserAuthenticated(authenticated);

      if (!authenticated) {
        router.push(redirectTo);
      }

      setIsLoading(false);
    };

    checkAuth();
  }, [router, redirectTo]);

  useEffect(() => {
    const handleStorageChange = async () => {
      const authenticated = await checkIsAuthenticated();
      setIsUserAuthenticated(authenticated);

      if (!authenticated) {
        router.push(redirectTo);
      }
    };

    // Listen for storage changes (for logout)
    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
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
      const authenticated = await checkIsAuthenticated();
      setIsUserAuthenticated(authenticated);

      if (!authenticated) {
        router.push('/login');
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
