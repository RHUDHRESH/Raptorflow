"use client";

import { OnboardingShell } from "@/components/onboarding/OnboardingShell";

export default function OnboardingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="h-screen">
      {children}
    </div>
  );
}
