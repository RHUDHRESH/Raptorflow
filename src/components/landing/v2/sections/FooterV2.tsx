"use client";

import React from "react";
import Link from "next/link";
import { RaptorLogo } from "@/components/ui/CompassLogo";

// ═══════════════════════════════════════════════════════════════
// FooterV2 - Premium footer
// ═══════════════════════════════════════════════════════════════

export function FooterV2() {
    return (
        <footer className="py-16 border-t border-[var(--border)] bg-[var(--canvas)]">
            <div className="max-w-7xl mx-auto px-6">
                {/* Main Footer Content */}
                <div className="flex flex-col md:flex-row justify-between items-start gap-12 mb-12">
                    {/* Brand */}
                    <div>
                        <div className="flex items-center gap-3 mb-4">
                            <RaptorLogo size={28} className="text-[var(--ink)]" />
                            <span className="font-editorial font-bold text-xl text-[var(--ink)]">
                                RaptorFlow
                            </span>
                        </div>
                        <p className="text-[var(--secondary)] max-w-xs">
                            The operating system for founder-led marketing.
                        </p>
                    </div>

                    {/* Links */}
                    <div className="flex gap-16">
                        {/* Product */}
                        <div>
                            <h4 className="text-sm font-semibold uppercase tracking-wider text-[var(--muted)] mb-4">
                                Product
                            </h4>
                            <ul className="space-y-2 text-sm">
                                <li>
                                    <Link
                                        href="#system"
                                        className="text-[var(--secondary)] hover:text-[var(--ink)] transition-colors"
                                    >
                                        Features
                                    </Link>
                                </li>
                                <li>
                                    <Link
                                        href="#pricing"
                                        className="text-[var(--secondary)] hover:text-[var(--ink)] transition-colors"
                                    >
                                        Pricing
                                    </Link>
                                </li>
                                <li>
                                    <Link
                                        href="/login"
                                        className="text-[var(--secondary)] hover:text-[var(--ink)] transition-colors"
                                    >
                                        Log in
                                    </Link>
                                </li>
                            </ul>
                        </div>

                        {/* Legal */}
                        <div>
                            <h4 className="text-sm font-semibold uppercase tracking-wider text-[var(--muted)] mb-4">
                                Legal
                            </h4>
                            <ul className="space-y-2 text-sm">
                                <li>
                                    <Link
                                        href="/legal/privacy"
                                        className="text-[var(--secondary)] hover:text-[var(--ink)] transition-colors"
                                    >
                                        Privacy
                                    </Link>
                                </li>
                                <li>
                                    <Link
                                        href="/legal/terms"
                                        className="text-[var(--secondary)] hover:text-[var(--ink)] transition-colors"
                                    >
                                        Terms
                                    </Link>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div className="pt-8 border-t border-[var(--border)] flex flex-col md:flex-row justify-between text-sm text-[var(--muted)] gap-4">
                    <p>© {new Date().getFullYear()} RaptorFlow Inc.</p>
                    <p className="italic">Marketing. Finally under control.</p>
                </div>
            </div>
        </footer>
    );
}
