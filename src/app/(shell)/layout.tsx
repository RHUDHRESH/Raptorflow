"use client";

import { WorkspaceProvider } from "@/components/workspace/WorkspaceProvider";
import { AnimationProvider } from "@/components/providers/AnimationProvider";

/**
 * Shell Layout
 * 
 * Provides workspace context and animation context to all shell pages.
 * Individual pages use the Raptor Layout component for their UI.
 * 
 * AnimationProvider enables:
 * - Page transition animations (slide + fade)
 * - Scroll-triggered reveals
 * - Stagger animations
 * - Reduced motion support
 */
export default function ShellLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <WorkspaceProvider>
      <AnimationProvider>
        {children}
      </AnimationProvider>
    </WorkspaceProvider>
  );
}
