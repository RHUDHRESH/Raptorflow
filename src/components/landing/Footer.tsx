"use client";

import React from "react";
import Link from "next/link";
import { CompassLogo } from "@/components/ui/CompassLogo";

export function Footer() {
    return (
        <footer className="bg-[var(--canvas)] border-t border-[var(--border)] py-12">
            <div className="max-w-7xl mx-auto px-6">

                <div className="flex flex-col md:flex-row justify-between items-start gap-8">
                    {/* Brand */}
                    <div className="space-y-3">
                        <Link href="/" className="flex items-center gap-2">
                            <CompassLogo size={24} className="text-[var(--ink)]" />
                            <span className="font-editorial font-bold text-lg text-[var(--ink)]">RaptorFlow</span>
                        </Link>
                        <p className="text-sm text-[var(--secondary)] max-w-xs">
                            The operating system for founder-led marketing.
                        </p>
                    </div>

                    {/* Links */}
                    <div className="flex gap-12">
                        <div className="space-y-3">
                            <h4 className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">Product</h4>
                            <ul className="space-y-2 text-sm text-[var(--secondary)]">
                                <li><Link href="#features" className="hover:text-[var(--ink)]">Features</Link></li>
                                <li><Link href="#pricing" className="hover:text-[var(--ink)]">Pricing</Link></li>
                                <li><Link href="/signin" className="hover:text-[var(--ink)]">Log In</Link></li>
                            </ul>
                        </div>
                        <div className="space-y-3">
                            <h4 className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">Legal</h4>
                            <ul className="space-y-2 text-sm text-[var(--secondary)]">
                                <li><Link href="/legal/privacy" className="hover:text-[var(--ink)]">Privacy</Link></li>
                                <li><Link href="/legal/terms" className="hover:text-[var(--ink)]">Terms</Link></li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div className="mt-12 pt-6 border-t border-[var(--border)] flex justify-between text-xs text-[var(--muted)]">
                    <p>© {new Date().getFullYear()} RaptorFlow</p>
                </div>
            </div>
        </footer>
    );
}
