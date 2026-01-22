"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export const runtime = 'edge';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--canvas)] relative overflow-hidden p-6">
      {/* Background Texture */}
      <div className="fixed inset-0 pointer-events-none z-0 opacity-[0.03]"
        style={{ backgroundImage: "url('/textures/paper-grain.png')", backgroundRepeat: "repeat" }} />

      <div className="relative z-10 max-w-lg w-full">
        {/* Minimal "Quiet Luxury" Card */}
        <div className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-12 md:p-16 text-center shadow-[var(--shadow-sm)]">

          <div className="mb-8">
            <span className="font-technical text-[var(--ink-muted)] text-xs tracking-widest uppercase mb-4 block">
              Error 404
            </span>
            <h1 className="font-serif text-4xl md:text-5xl text-[var(--ink)] mb-4 tracking-tight">
              Page Not Found
            </h1>
            <div className="w-12 h-px bg-[var(--border)] mx-auto my-6" />
            <p className="text-[var(--ink-secondary)] text-lg leading-relaxed max-w-sm mx-auto">
              The page you are looking for has been moved, deleted, or possibly never existed.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="w-full sm:w-auto px-8 py-3 rounded-[var(--radius-md)] bg-[var(--ink)] text-[var(--paper)] font-medium hover:opacity-90 transition-all flex items-center justify-center gap-2 group"
            >
              Return Home
            </Link>
            <button
              onClick={() => window.history.back()}
              className="w-full sm:w-auto px-8 py-3 rounded-[var(--radius-md)] border border-[var(--border)] text-[var(--ink)] font-medium hover:bg-[var(--surface)] transition-all flex items-center justify-center gap-2"
            >
              <ArrowLeft size={16} /> Go Back
            </button>
          </div>
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
