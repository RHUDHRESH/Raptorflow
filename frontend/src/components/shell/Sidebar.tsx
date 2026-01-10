"use client";

import { useRef, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import gsap from "gsap";
import {
    LayoutDashboard,
    Target,
    Users,
    Zap,
    Send,
    Wand2,
    BarChart3,
    Box,
    Settings,
    HelpCircle,
    ChevronDown,
    Compass,
} from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Sidebar Navigation
   Features:
   - Paper texture visible
   - Blueprint-style section dividers
   - Technical navigation codes
   - Measurement ticks along the edge
   - Registration marks on active items
   ══════════════════════════════════════════════════════════════════════════════ */

const mainNav = [
    { id: "dashboard", label: "Dashboard", code: "DASH", icon: LayoutDashboard, href: "/dashboard" },
    { id: "foundation", label: "Foundation", code: "FND", icon: Target, href: "/foundation" },
    { id: "cohorts", label: "Cohorts", code: "COH", icon: Users, href: "/foundation#icp" },
    { id: "moves", label: "Moves", code: "MOV", icon: Zap, href: "/moves" },
    { id: "campaigns", label: "Campaigns", code: "CMP", icon: Send, href: "/campaigns", badge: "3" },
    { id: "muse", label: "Muse", code: "MUS", icon: Wand2, href: "/muse" },
    { id: "daily-wins", label: "Daily Wins", code: "WIN", icon: Compass, href: "/daily-wins" },
    { id: "analytics", label: "Analytics", code: "ANL", icon: BarChart3, href: "/analytics" },
    { id: "blackbox", label: "Blackbox", code: "BLK", icon: Box, href: "/blackbox" },
];

const secondaryNav = [
    { id: "settings", label: "Settings", code: "SET", icon: Settings, href: "/settings" },
    { id: "help", label: "Help", code: "HLP", icon: HelpCircle, href: "/help" },
];

export function Sidebar() {
    const pathname = usePathname();
    const sidebarRef = useRef<HTMLElement>(null);
    const navItemsRef = useRef<(HTMLAnchorElement | null)[]>([]);

    const isActive = (href: string) => {
        if (href === "/dashboard") return pathname === "/dashboard" || pathname === "/";
        return pathname.startsWith(href);
    };

    // GSAP entrance animation
    useEffect(() => {
        if (!sidebarRef.current) return;

        const ctx = gsap.context(() => {
            // Logo animation
            const logo = sidebarRef.current?.querySelector("[data-logo]");
            if (logo) {
                gsap.fromTo(
                    logo,
                    { opacity: 0, x: -20 },
                    { opacity: 1, x: 0, duration: 0.5, ease: "power2.out" }
                );
            }

            // Nav items stagger
            const navItems = sidebarRef.current?.querySelectorAll("[data-nav-item]");
            if (navItems && navItems.length > 0) {
                gsap.fromTo(
                    navItems,
                    { opacity: 0, x: -16 },
                    {
                        opacity: 1,
                        x: 0,
                        duration: 0.4,
                        stagger: 0.04,
                        delay: 0.2,
                        ease: "power2.out"
                    }
                );
            }

            // User profile animation
            const profile = sidebarRef.current?.querySelector("[data-profile]");
            if (profile) {
                gsap.fromTo(
                    profile,
                    { opacity: 0, y: 20 },
                    { opacity: 1, y: 0, duration: 0.5, delay: 0.5, ease: "back.out(1.2)" }
                );
            }
        }, sidebarRef);

        return () => ctx.revert();
    }, []);

    // Hover animation for nav items
    const handleNavHover = (e: React.MouseEvent<HTMLAnchorElement>, entering: boolean) => {
        const target = e.currentTarget;
        const icon = target.querySelector("[data-icon]");

        if (entering) {
            gsap.to(target, { x: 4, duration: 0.2, ease: "power2.out" });
            if (icon) {
                gsap.to(icon, { scale: 1.1, duration: 0.2, ease: "back.out(2)" });
            }
        } else {
            gsap.to(target, { x: 0, duration: 0.2, ease: "power2.out" });
            if (icon) {
                gsap.to(icon, { scale: 1, duration: 0.2, ease: "power2.out" });
            }
        }
    };

    return (
        <aside
            ref={sidebarRef}
            className="relative w-64 bg-[var(--paper)] border-r border-[var(--border)] flex flex-col ink-bleed-sm overflow-hidden"
        >
            {/* Paper texture overlay */}
            <div
                className="absolute inset-0 pointer-events-none z-0"
                style={{
                    backgroundImage: "url('/textures/paper-grain.png')",
                    backgroundRepeat: "repeat",
                    backgroundSize: "256px 256px",
                    opacity: 0.05,
                    mixBlendMode: "multiply",
                }}
            />

            {/* Blueprint edge measurement ticks */}
            <div className="absolute top-0 right-0 bottom-0 w-px bg-[var(--blueprint-line)] z-10" />
            <div className="absolute top-0 right-0 bottom-0 flex flex-col pointer-events-none z-10">
                {[...Array(20)].map((_, i) => (
                    <div key={i} className="flex-1 flex items-end justify-end">
                        <div className={`h-px ${i % 4 === 0 ? 'w-3 bg-[var(--blueprint)]' : 'w-1.5 bg-[var(--blueprint-line)]'}`} />
                    </div>
                ))}
            </div>

            {/* ═══════════════════════════════════════════════════════════════════
          LOGO — Technical brand mark
          ═══════════════════════════════════════════════════════════════════ */}
            <div
                data-logo
                className="relative z-10 h-18 py-6 px-5 flex items-center border-b border-[var(--border)]"
                style={{ opacity: 0 }}
            >
                <div className="flex items-center gap-4">
                    {/* Logo with registration marks */}
                    <div className="relative">
                        <div className="w-10 h-10 bg-[var(--ink)] rounded-[var(--radius-sm)] flex items-center justify-center ink-bleed-sm">
                            <Compass size={20} className="text-[var(--paper)]" strokeWidth={1.5} />
                        </div>
                        {/* Registration corner */}
                        <div className="absolute -top-1 -left-1 w-2 h-2 border-t border-l border-[var(--blueprint)]" />
                    </div>

                    <div className="flex flex-col">
                        <span className="font-serif text-lg font-semibold tracking-tight text-[var(--ink)] leading-none">
                            RaptorFlow
                        </span>
                        <span className="font-technical text-[var(--blueprint)]">
                            MKT-OS v2.0
                        </span>
                    </div>
                </div>
            </div>

            {/* ═══════════════════════════════════════════════════════════════════
          MAIN NAVIGATION — Technical list style
          ═══════════════════════════════════════════════════════════════════ */}
            <nav className="flex-1 px-3 py-5 overflow-y-auto relative z-10">
                {/* Section header */}
                <div className="flex items-center gap-2 px-3 mb-4">
                    <span className="font-technical text-[var(--blueprint)]">MODULES</span>
                    <div className="flex-1 h-px bg-[var(--blueprint-line)]" />
                    <span className="font-technical text-[var(--muted)]">09</span>
                </div>

                <div className="space-y-1">
                    {mainNav.map((item, index) => {
                        const active = isActive(item.href);
                        const Icon = item.icon;

                        return (
                            <Link
                                key={item.id}
                                href={item.href}
                                data-nav-item
                                ref={(el) => { navItemsRef.current[index] = el; }}
                                onMouseEnter={(e) => handleNavHover(e, true)}
                                onMouseLeave={(e) => handleNavHover(e, false)}
                                className={`group flex items-center gap-3 px-3 py-2.5 rounded-[var(--radius-sm)] text-sm font-medium transition-all duration-200 relative ${active
                                    ? "bg-[var(--blueprint-light)] text-[var(--ink)] border border-[var(--blueprint-line)]"
                                    : "text-[var(--secondary)] hover:bg-[var(--surface)] border border-transparent"
                                    }`}
                                style={{ opacity: 0 }}
                            >
                                {/* Active indicator - blueprint style */}
                                {active && (
                                    <>
                                        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-6 bg-[var(--blueprint)]" />
                                        {/* Registration marks */}
                                        <div className="absolute -top-0.5 -left-0.5 w-2 h-2 border-t border-l border-[var(--blueprint)]" />
                                        <div className="absolute -bottom-0.5 -right-0.5 w-2 h-2 border-b border-r border-[var(--blueprint)]" />
                                    </>
                                )}

                                {/* Icon */}
                                <div data-icon className="flex-shrink-0">
                                    <Icon
                                        size={18}
                                        strokeWidth={1.5}
                                        className={active ? "text-[var(--blueprint)]" : "text-[var(--muted)] group-hover:text-[var(--secondary)]"}
                                    />
                                </div>

                                {/* Label */}
                                <span className="flex-1">{item.label}</span>

                                {/* Technical code */}
                                <span className={`font-technical ${active ? 'text-[var(--blueprint)]' : 'text-[var(--muted)] opacity-0 group-hover:opacity-100'} transition-opacity`}>
                                    {item.code}
                                </span>

                                {/* Badge */}
                                {item.badge && (
                                    <span className="min-w-[18px] h-[18px] flex items-center justify-center font-technical text-[10px] bg-[var(--blueprint)] text-[var(--paper)] rounded-[var(--radius-xs)]">
                                        {item.badge}
                                    </span>
                                )}
                            </Link>
                        );
                    })}
                </div>
            </nav>

            {/* ═══════════════════════════════════════════════════════════════════
          DIVIDER — Blueprint style
          ═══════════════════════════════════════════════════════════════════ */}
            <div className="px-6 relative z-10">
                <div className="relative h-px bg-[var(--border)]">
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-2 h-2 border-l border-t border-[var(--blueprint-line)] rotate-45" />
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 border-r border-b border-[var(--blueprint-line)] rotate-45" />
                </div>
            </div>

            {/* ═══════════════════════════════════════════════════════════════════
          SECONDARY NAVIGATION
          ═══════════════════════════════════════════════════════════════════ */}
            <div className="px-3 py-4 relative z-10">
                <div className="flex items-center gap-2 px-3 mb-3">
                    <span className="font-technical text-[var(--muted)]">SUPPORT</span>
                    <div className="flex-1 h-px bg-[var(--blueprint-line)]" />
                </div>

                <div className="space-y-1">
                    {secondaryNav.map((item) => {
                        const active = isActive(item.href);
                        const Icon = item.icon;

                        return (
                            <Link
                                key={item.id}
                                href={item.href}
                                data-nav-item
                                onMouseEnter={(e) => handleNavHover(e, true)}
                                onMouseLeave={(e) => handleNavHover(e, false)}
                                className={`group flex items-center gap-3 px-3 py-2 rounded-[var(--radius-sm)] text-sm font-medium transition-all duration-200 relative ${active
                                    ? "bg-[var(--blueprint-light)] text-[var(--ink)]"
                                    : "text-[var(--secondary)] hover:bg-[var(--canvas)]"
                                    }`}
                                style={{ opacity: 0 }}
                            >
                                <div data-icon>
                                    <Icon
                                        size={16}
                                        strokeWidth={1.5}
                                        className={active ? "text-[var(--blueprint)]" : "text-[var(--muted)] group-hover:text-[var(--secondary)]"}
                                    />
                                </div>
                                <span>{item.label}</span>
                                <span className="font-technical text-[var(--muted)] opacity-0 group-hover:opacity-100 transition-opacity ml-auto">
                                    {item.code}
                                </span>
                            </Link>
                        );
                    })}
                </div>
            </div>

            {/* ═══════════════════════════════════════════════════════════════════
          USER PROFILE — Architectural style
          ═══════════════════════════════════════════════════════════════════ */}
            <div
                data-profile
                className="p-4 border-t border-[var(--border)] relative z-10"
                style={{ opacity: 0 }}
            >
                <Link href="/settings">
                    <div className="flex items-center gap-3 p-2.5 rounded-[var(--radius-sm)] hover:bg-[var(--canvas)] cursor-pointer transition-all duration-200 group">
                        {/* Avatar with registration mark */}
                        <div className="relative">
                            <div className="w-10 h-10 rounded-[var(--radius-xs)] bg-[var(--ink)] flex items-center justify-center text-[var(--paper)] text-sm font-semibold ink-bleed-sm">
                                BM
                            </div>
                            <div className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 border-t border-r border-[var(--blueprint)]" />
                        </div>

                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-[var(--ink)] truncate">Bossman</p>
                            <p className="font-technical text-[var(--muted)]">ADMIN</p>
                        </div>

                        <ChevronDown
                            size={14}
                            strokeWidth={1.5}
                            className="text-[var(--muted)] group-hover:text-[var(--secondary)] group-hover:rotate-180 transition-all duration-300"
                        />
                    </div>
                </Link>
            </div>

            {/* Document info at bottom */}
            <div className="px-4 py-2 border-t border-[var(--border)] relative z-10">
                <span className="font-technical text-[8px] text-[var(--muted)]">
                    NAV-PANEL v2.0
                </span>
            </div>
        </aside>
    );
}
