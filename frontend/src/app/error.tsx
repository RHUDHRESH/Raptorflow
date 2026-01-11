"use client";

import { useEffect } from "react";
import { AlertCircle, RotateCcw } from "lucide-react";

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
    <div className="min-h-screen flex items-center justify-center bg-[var(--paper)] relative overflow-hidden">
      <div className="fixed inset-0 pointer-events-none z-0" style={{ backgroundImage: "url('/textures/paper-grain.png')", opacity: 0.05, mixBlendMode: "multiply" }} />
      <div className="fixed inset-0 blueprint-grid pointer-events-none z-0 opacity-10" />

      <div className="relative z-10 max-w-md w-full p-8 text-center">
        <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-[var(--error-light)] border border-[var(--error)] flex items-center justify-center">
          <AlertCircle size={32} strokeWidth={1.5} className="text-[var(--error)]" />
        </div>

        <div className="flex items-center justify-center gap-3 mb-4">
          <span className="font-technical text-[var(--error)]">ERR_500</span>
          <div className="h-px w-8 bg-[var(--error)]" />
          <span className="font-technical text-[var(--muted)]">SYSTEM_FAILURE</span>
        </div>

        <h1 className="font-serif text-3xl text-[var(--ink)] mb-4">Critical Alignment Error</h1>
        <p className="text-[var(--secondary)] mb-8">
          The system encountered an unexpected structural failure. Our engineers have been dispatched.
        </p>

        <button
          onClick={reset}
          className="flex items-center justify-center gap-2 h-10 px-6 mx-auto rounded-[var(--radius-sm)] bg-[var(--ink)] text-[var(--paper)] font-medium hover:opacity-90 transition-opacity"
        >
          <RotateCcw size={16} /> Attempt Re-Initialization
        </button>

        {error.digest && (
          <p className="mt-8 text-xs font-mono text-[var(--muted)]">Reference: {error.digest}</p>
        )}
      </div>
    </div>
  );
}
