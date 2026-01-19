"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/* ══════════════════════════════════════════════════════════════════════════════
   COHORTS REDIRECT — Now part of Foundation
   Redirects to Foundation page ICP section
   ══════════════════════════════════════════════════════════════════════════════ */

export default function CohortsPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/foundation#icp");
  }, [router]);

  return (
    <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center">
      <div className="text-center">
        <p className="text-sm text-[var(--muted)]">Redirecting to Foundation...</p>
      </div>
    </div>
  );
}
