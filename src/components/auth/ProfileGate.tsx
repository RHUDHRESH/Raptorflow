"use client";

import React, { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/components/auth/AuthProvider";
import { BlueprintLoader } from "@/components/ui/BlueprintLoader";

const PUBLIC_PATH_PREFIXES = [
  "/",
  "/signin",
  "/signup",
  "/auth/callback",
  "/test-auth.html",
];

function isPublicPath(pathname: string | null): boolean {
  if (!pathname) return true;
  return PUBLIC_PATH_PREFIXES.some((prefix) =>
    prefix === "/"
      ? pathname === "/"
      : pathname === prefix || pathname.startsWith(`${prefix}/`)
  );
}

export function ProfileGate({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const {
    isAuthenticated,
    isLoading,
    profileStatus,
    isCheckingProfile,
  } = useAuth();

  // State to prevent endless redirects
  const [redirectAttempted, setRedirectAttempted] = useState<string>("");
  const [showError, setShowError] = useState<string>("");
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    // Reset state when user changes or path changes
    if (!isAuthenticated || isPublicPath(pathname)) {
      setRedirectAttempted("");
      setShowError("");
      setRetryCount(0);
      return;
    }

    // Don't redirect if already checking profile
    if (isCheckingProfile) {
      return;
    }

    // Handle profile verification errors
    if (profileStatus.error && retryCount < 3) {
      // Retry verification after a delay
      const timer = setTimeout(() => {
        setRetryCount(prev => prev + 1);
        setShowError("");
      }, 2000);
      return () => clearTimeout(timer);
    } else if (profileStatus.error && retryCount >= 3) {
      setShowError(profileStatus.error);
      return;
    }

    // Smart redirect logic with state tracking
    const hasActiveSubscription = profileStatus.subscriptionStatus === 'active';
    const redirectKey = `${profileStatus.profileExists}-${profileStatus.workspaceExists}-${profileStatus.needsPayment}-${hasActiveSubscription}`;

    if (!profileStatus.profileExists && redirectAttempted !== "no-profile") {
      setRedirectAttempted("no-profile");
      router.replace(hasActiveSubscription ? "/onboarding/start" : "/onboarding/plans");
      return;
    }

    if (!profileStatus.workspaceExists && redirectAttempted !== "no-workspace") {
      setRedirectAttempted("no-workspace");
      router.replace(hasActiveSubscription ? "/onboarding/start" : "/onboarding/plans");
      return;
    }

    if ((profileStatus.needsPayment || !hasActiveSubscription) && redirectAttempted !== "needs-payment") {
      setRedirectAttempted("needs-payment");
      router.replace("/onboarding/plans");
      return;
    }

    // Clear redirect state when profile is ready
    if (profileStatus.isReady) {
      setRedirectAttempted("");
      setShowError("");
      setRetryCount(0);
    }
  }, [
    isAuthenticated,
    pathname,
    profileStatus,
    isCheckingProfile,
    redirectAttempted,
    retryCount,
    router,
  ]);

  if (!isAuthenticated || isPublicPath(pathname)) {
    return <>{children}</>;
  }

  // Show error UI after multiple failed attempts
  if (showError) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-6 bg-[var(--paper)] p-8">
        <div className="text-center max-w-md">
          <div className="mb-4">
            <div className="w-16 h-16 mx-auto bg-red-100 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <h2 className="text-xl font-semibold mb-2">Profile Verification Failed</h2>
          <p className="text-[var(--muted)] mb-6">
            We're having trouble verifying your profile. This might be due to a temporary issue.
          </p>
          <div className="space-y-3">
            <button
              onClick={() => window.location.reload()}
              className="w-full px-4 py-2 bg-[var(--ink)] text-[var(--paper)] rounded-lg hover:opacity-90 transition-opacity"
            >
              Refresh Page
            </button>
            <button
              onClick={() => {
                setRetryCount(0);
                setShowError("");
                setRedirectAttempted("");
              }}
              className="w-full px-4 py-2 border border-[var(--border)] rounded-lg hover:bg-[var(--muted)] transition-colors"
            >
              Try Again
            </button>
          </div>
          <p className="text-xs text-[var(--muted)] mt-4">
            Error: {showError}
          </p>
        </div>
      </div>
    );
  }

  // Show loading state
  if (isLoading || isCheckingProfile || !profileStatus.isReady) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-[var(--paper)]">
        <BlueprintLoader size="lg" />
        <p className="font-mono text-xs text-[var(--muted)] tracking-[0.2em]">
          VERIFYING WORKSPACE & PAYMENT STATUS…
        </p>
        {retryCount > 0 && (
          <p className="font-mono text-xs text-[var(--muted)] opacity-60">
            Retry attempt {retryCount}/3
          </p>
        )}
      </div>
    );
  }

  return <>{children}</>;
}
