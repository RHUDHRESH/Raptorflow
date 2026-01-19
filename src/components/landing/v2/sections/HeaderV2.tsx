"use client";

import React from "react";
import Link from "next/link";
import { RaptorLogo } from "@/components/ui/CompassLogo";

// ═══════════════════════════════════════════════════════════════
// HeaderV2 - Fixed navigation header
// ═══════════════════════════════════════════════════════════════

export function HeaderV2() {
    return (
        <header className="fixed top-0 left-0 right-0 z-50 bg-[var(--canvas)]/90 backdrop-blur-md border-b border-[var(--border)]">
            <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-3">
                    <RaptorLogo size={28} className="text-[var(--ink)]" />
                    <span className="font-editorial text-xl font-bold tracking-tight text-[var(--ink)]">
                        RaptorFlow
                    </span>
                </Link>

                {/* Navigation */}
                <nav className="hidden md:flex items-center gap-8">
                    <Link
                        href="#system"
                        className="text-sm text-[var(--secondary)] hover:text-[var(--ink)] transition-colors"
                    >
                        System
                    </Link>
                    <Link
                        href="#how"
                        className="text-sm text-[var(--secondary)] hover:text-[var(--ink)] transition-colors"
                    >
                        How it works
                    </Link>
                    <Link
                        href="#pricing"
                        className="text-sm text-[var(--secondary)] hover:text-[var(--ink)] transition-colors"
                    >
                        Pricing
                    </Link>
                    <Link
                        href="/login"
                        className="text-sm text-[var(--ink)]"
                    >
                        Log in
                    </Link>
                    <Link
                        href="/signup"
                        className="text-sm px-5 py-2.5 bg-[var(--ink)] text-[var(--canvas)] rounded-lg font-medium hover:opacity-90 transition-opacity"
                    >
                        Start free
                    </Link>
                </nav>

                {/* Mobile Menu Button - TODO: Implement mobile menu */}
                <button className="md:hidden p-2 text-[var(--ink)]">
                    <svg
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                    >
                        <line x1="3" y1="6" x2="21" y2="6" />
                        <line x1="3" y1="12" x2="21" y2="12" />
                        <line x1="3" y1="18" x2="21" y2="18" />
                    </svg>
                </button>
            </div>
        </header>
    );
}
