"use client";

import Link from "next/link";
import { FileQuestion, Home, ArrowLeft } from "lucide-react";

export const runtime = 'edge';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--paper)] relative overflow-hidden">
      <div className="fixed inset-0 pointer-events-none z-0" style={{ backgroundImage: "url('/textures/paper-grain.png')", backgroundRepeat: "repeat", backgroundSize: "256px 256px", opacity: 0.04, mixBlendMode: "multiply" }} />
      <div className="fixed inset-0 blueprint-grid pointer-events-none z-0 opacity-30" />

      <div className="relative z-10 max-w-md w-full p-8 text-center">
        <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-[var(--canvas)] border border-[var(--border)] flex items-center justify-center">
          <FileQuestion size={32} strokeWidth={1.5} className="text-[var(--muted)]" />
        </div>

        <div className="flex items-center justify-center gap-3 mb-4">
          <span className="font-technical text-[var(--error)]">ERR_404</span>
          <div className="h-px w-8 bg-[var(--border)]" />
          <span className="font-technical text-[var(--muted)]">NOT_FOUND</span>
        </div>

        <h1 className="font-serif text-4xl text-[var(--ink)] mb-4">File Missing</h1>
        <p className="text-[var(--secondary)] mb-8">
          The document or page you are looking for has been moved, archived, or does not exist in the system.
        </p>

        <div className="flex flex-col gap-3">
          <Link href="/dashboard" className="flex items-center justify-center gap-2 h-10 px-4 rounded-[var(--radius-sm)] bg-[var(--ink)] text-[var(--paper)] font-medium hover:opacity-90 transition-opacity">
            <Home size={16} /> Return to Dashboard
          </Link>
          <button onClick={() => window.history.back()} className="flex items-center justify-center gap-2 h-10 px-4 rounded-[var(--radius-sm)] border border-[var(--border)] text-[var(--ink)] font-medium hover:border-[var(--blueprint)] transition-colors">
            <ArrowLeft size={16} /> Go Back
          </button>
        </div>
      </div>
    </div>
  );
}
