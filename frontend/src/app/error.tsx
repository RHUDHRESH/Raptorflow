"use client";

import { useEffect } from "react";
import { RotateCcw } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to monitoring service
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--canvas)] relative overflow-hidden p-6">
      {/* Background Texture */}
      <div className="fixed inset-0 pointer-events-none z-0 opacity-[0.03]"
        style={{ backgroundImage: "url('/textures/paper-grain.png')", backgroundRepeat: "repeat" }} />

      <div className="relative z-10 max-w-lg w-full">
        {/* Minimal "Quiet Luxury" Card - Error Variant */}
        <div className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-12 md:p-16 text-center shadow-[var(--shadow-sm)]">

          <div className="mb-8">
            <span className="font-technical text-[var(--error)] text-xs tracking-widest uppercase mb-4 block">
              System Error
            </span>
            <h1 className="font-serif text-4xl md:text-5xl text-[var(--ink)] mb-4 tracking-tight">
              Critical Failure
            </h1>
            <div className="w-12 h-px bg-[var(--error)] opacity-30 mx-auto my-6" />
            <p className="text-[var(--ink-secondary)] text-lg leading-relaxed max-w-sm mx-auto">
              We encountered an unexpected issue. Our engineers have been notified.
            </p>
          </div>

          <button
            onClick={reset}
            className="w-full sm:w-auto px-8 py-3 mx-auto rounded-[var(--radius-md)] bg-[var(--ink)] text-[var(--paper)] font-medium hover:opacity-90 transition-all flex items-center justify-center gap-2"
          >
            <RotateCcw size={16} /> Attempt Recovery
          </button>

          {error.digest && (
            <p className="mt-8 text-[10px] font-technical text-[var(--ink-muted)]">
              REF: {error.digest}
            </p>
          )}
        </div>
        {/* Footer Meta */}
        <div className="mt-8 text-center">
          <p className="font-technical text-[var(--ink-muted)] text-[10px] tracking-widest">
            RAPTORFLOW SYSTEM OVERSEER
          </p>
        </div>
      </div>
    </div>
  );
}
