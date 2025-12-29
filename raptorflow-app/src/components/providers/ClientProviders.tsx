'use client';

import { ReactNode } from 'react';
import { FoundationProvider } from '@/context/FoundationProvider';
import { TypingExperienceProvider } from '@/components/ui/typing/TypingExperienceProvider';
import { SmoothScrollProvider } from '@/components/providers/SmoothScrollProvider';

/**
 * Client-side providers wrapper
 * Groups all context providers that require 'use client'
 */
export function ClientProviders({ children }: { children: ReactNode }) {
  return (
    <SmoothScrollProvider>
      <FoundationProvider>
        <TypingExperienceProvider>{children}</TypingExperienceProvider>
      </FoundationProvider>
    </SmoothScrollProvider>
  );
}
