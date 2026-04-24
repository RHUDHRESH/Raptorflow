import React from "react";
import { FoundationChrome } from "@/components/foundation/foundation-chrome";

/**
 * FoundationLayout
 * Wraps all 21 foundation screens in a full-screen immersive container.
 * Replaces the default app shell.
 */
export default function FoundationLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[#1a1a1a] text-white selection:bg-[#f59e0b]/30 selection:text-[#f59e0b]">
      {/* Interactive Chrome Layer (Client) */}
      <FoundationChrome />

      {/* 5. CONTENT AREA (Server/Client) */}
      <main className="relative z-10 pt-6 min-h-screen">
        {children}
      </main>
    </div>
  );
}
