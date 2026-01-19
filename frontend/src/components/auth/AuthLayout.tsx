"use client";

import React from 'react';
import { Compass } from 'lucide-react';

interface AuthLayoutProps {
    children: React.ReactNode;
    /** Title displayed in the left brand panel */
    title: React.ReactNode;
    /** Subtext/Body displayed in the left brand panel */
    subtitle: React.ReactNode;
    /** System version code for the footer */
    sysCode?: string;
    /** Optional override for the icon */
    icon?: React.ReactNode;
}

export default function AuthLayout({
    children,
    title,
    subtitle,
    sysCode = "SYS.V.2.0.4",
    icon
}: AuthLayoutProps) {
    return (
        <div className="min-h-screen bg-[var(--canvas)] flex relative overflow-hidden">
            {/* Left Panel - Brand / Art (Hidden on Mobile) */}
            <div className="hidden lg:flex w-1/2 bg-[var(--ink)] relative flex-col justify-between p-16 text-[var(--paper)] overflow-hidden">
                {/* Texture - Subtle & Expensive */}
                <div className="absolute inset-0 opacity-[0.05]"
                    style={{
                        backgroundImage: "url('/textures/paper-grain.png')",
                        backgroundRepeat: "repeat",
                    }}
                />

                {/* Brand Logo Area */}
                <div className="relative z-10 flex items-center gap-4">
                    <div className="w-12 h-12 bg-[var(--paper)] rounded-[var(--radius-md)] flex items-center justify-center text-[var(--ink)] shadow-md">
                        {icon || <Compass size={28} strokeWidth={1.5} />}
                    </div>
                    <span className="font-serif text-2xl tracking-tight font-semibold">RaptorFlow</span>
                </div>

                {/* Art / Message - BOLD & VISIBLE */}
                <div className="relative z-10 max-w-xl">
                    <h1 className="font-serif text-6xl leading-[1.1] mb-8 font-medium">
                        {title}
                    </h1>
                    <div className="w-16 h-1 bg-[var(--accent-amber)] mb-8 opacity-80" />
                    <div className="text-[var(--structure-subtle)] font-light text-xl leading-relaxed opacity-90">
                        {subtitle}
                    </div>
                </div>

                {/* Footer */}
                <div className="relative z-10 flex items-center gap-8 text-xs text-[var(--structure)] font-technical tracking-widest uppercase opacity-70">
                    <span>{sysCode}</span>
                    <span>//</span>
                    <span>SECURE_CONNECTION</span>
                </div>
            </div>

            {/* Right Panel - Content form */}
            <div className="w-full lg:w-1/2 flex items-center justify-center p-6 md:p-12 relative bg-[var(--paper)]">
                <div className="w-full max-w-md">
                    {/* Mobile Logo (Visible only on small screens) */}
                    <div className="lg:hidden mb-12 flex items-center justify-center gap-3">
                        <div className="w-10 h-10 bg-[var(--ink)] rounded-[var(--radius-sm)] flex items-center justify-center text-[var(--paper)]">
                            {icon || <Compass size={24} strokeWidth={1.5} />}
                        </div>
                        <span className="font-serif text-2xl text-[var(--ink)]">RaptorFlow</span>
                    </div>

                    {children}

                    {/* Legal Links Footer */}
                    <div className="mt-8 pt-8 border-t border-[var(--border)] flex justify-center gap-6 text-xs text-[var(--ink-muted)]">
                        <a href="/legal/terms" className="hover:text-[var(--ink)] transition-colors">Terms</a>
                        <a href="/legal/privacy" className="hover:text-[var(--ink)] transition-colors">Privacy</a>
                        <a href="/support" className="hover:text-[var(--ink)] transition-colors">Help</a>
                    </div>
                </div>
            </div>
        </div>
    );
}
