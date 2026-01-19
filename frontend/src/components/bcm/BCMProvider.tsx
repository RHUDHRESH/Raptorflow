"use client";

import { useEffect, ReactNode } from "react";
import { useBCMStore } from "@/stores/bcmStore";
import { useBCMUpdates } from "@/hooks/useBCMUpdates";

interface BCMProviderProps {
  children: ReactNode;
}

/**
 * BCM Provider - Ensures BCM data is available and up-to-date across the application
 * This component should wrap the main application to provide BCM context to all features
 */
export function BCMProvider({ children }: BCMProviderProps) {
  const { bcm, isLoading } = useBCMStore();
  
  // Enable automatic BCM updates based on completed tasks
  useBCMUpdates({ enabled: true });

  // Log BCM state changes for debugging
  useEffect(() => {
    if (bcm) {
      console.log('BCM Provider: BCM data available', {
        version: bcm.meta.version,
        company: bcm.foundation.company,
        icps: bcm.icps.length,
        lastUpdated: bcm.meta.updated_at
      });
    }
  }, [bcm]);

  // Initialize BCM from localStorage if needed
  useEffect(() => {
    if (!isLoading && !bcm) {
      console.log('BCM Provider: No BCM data found - user should complete onboarding');
    }
  }, [bcm, isLoading]);

  return <>{children}</>;
}

/**
 * Hook to check if BCM is available and provide helpful messaging
 */
export function useBCMAvailability() {
  const { bcm, isLoading } = useBCMStore();

  const isAvailable = !isLoading && !!bcm;
  const needsOnboarding = !isLoading && !bcm;
  
  const getBCMStatusMessage = () => {
    if (isLoading) return "Loading business context...";
    if (needsOnboarding) return "Complete onboarding to generate your business context";
    if (bcm) return `Business context v${bcm.meta.version} loaded`;
    return "Business context unavailable";
  };

  return {
    isAvailable,
    needsOnboarding,
    isLoading,
    statusMessage: getBCMStatusMessage(),
    bcm
  };
}
