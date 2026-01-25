"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
    LayoutDashboard,
    Target,
    Users,
    Zap,
    BarChart2,
    Lightbulb,
    Trophy,
    Layers,
    Box,
    Search,
    ChevronDown,
    Settings,
    HelpCircle,
    LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/components/auth/AuthProvider";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Sidebar Navigation
   Architectural blueprint aesthetic matching Dashboard/Blackbox/Analytics
   ══════════════════════════════════════════════════════════════════════════════ */

const navItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard, code: "DASH" },
    { name: "Foundation", href: "/foundation", icon: Target, code: "FNDN" },
    { name: "Moves", href: "/moves", icon: Zap, code: "MOVE" },
    { name: "Campaigns", href: "/campaigns", icon: BarChart2, code: "CAMP" },
    { name: "Muse", href: "/muse", icon: Lightbulb, code: "MUSE", badge: "AI" },
    { name: "Daily Wins", href: "/daily-wins", icon: Trophy, code: "WINS" },
    { name: "Analytics", href: "/analytics", icon: Layers, code: "ANLT" },
    { name: "Blackbox", href: "/blackbox", icon: Box, code: "BBOX" },
];

const secondaryItems = [
    { name: "Settings", href: "/settings", icon: Settings },
    { name: "Help", href: "/help", icon: HelpCircle },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, profile, logout } = useAuth();
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  // Extract user info for display
  const displayName = user?.email ? 
    user.email!.split('@')[0].charAt(0).toUpperCase() + user.email!.split('@')[0].slice(1) : 
    "User";
  const initials = displayName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

  return (
    <aside className="fixed left-0 top-0 hidden lg:flex flex-col h-screen w-64 bg-[var(--paper)] border-r border-[var(--structure)] z-50 overflow-y-auto">
        {/* Paper texture overlay removed - handled globally */}

        {/* Blueprint accent line */}
        <div className="absolute top-0 right-0 h-full w-px bg-[var(--blueprint-line)]" />

        {/* Brand Header */}
        <div className="relative z-10 p-6 pb-4 border-b border-[var(--structure-subtle)]">
            <Link href="/dashboard" className="flex items-center gap-3 group">
                <div className="w-9 h-9 rounded-[var(--radius-lg)] bg-[var(--ink)] flex items-center justify-center text-[var(--paper)] font-serif font-bold text-sm">
                    RF
                </div>
                <div className="flex flex-col">
                    <span className="font-serif font-semibold text-lg tracking-tight text-[var(--ink)] group-hover:text-[var(--ink-secondary)] transition-colors">
                        RaptorFlow
                    </span>
                    <span className="font-technical text-[9px] tracking-widest text-[var(--ink-muted)] uppercase">
                        Marketing OS
                    </span>
                </div>
            </Link>
        </div>

        {/* Navigation - Main Modules */}
        <nav className="relative z-10 flex-1 overflow-y-auto px-4 py-6 space-y-1">
            {navItems.map((item) => {
                const isActive = pathname?.startsWith(item.href);
                const Icon = item.icon;

                return (
                    <Link
                        key={item.href}
                        href={item.href}
                        className={cn(
                            "group flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all relative overflow-hidden",
                            isActive
                                ? "bg-[var(--surface)] text-[var(--ink)] shadow-sm ring-1 ring-black/5"
                                : "text-[var(--ink-secondary)] hover:bg-[var(--surface-hover)] hover:text-[var(--ink)]"
                        )}
                    >
                        {/* Active Accent Line */}
                        {isActive && (
                            <motion.div 
                                layoutId="active-nav-accent"
                                className="absolute left-0 top-2 bottom-2 w-1 bg-[var(--blueprint)] rounded-r-full"
                                initial={{ opacity: 0, x: -5 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                            />
                        )}
                        
                        <Icon
                            size={18}
                            strokeWidth={isActive ? 2 : 1.5}
                            className={cn(
                                "transition-colors relative z-10",
                                isActive ? "text-[var(--blueprint)]" : "text-[var(--ink-muted)] group-hover:text-[var(--ink)]"
                            )}
                        />
                        <span className="flex-1 relative z-10">{item.name}</span>

                        {/* AI Badge for Muse */}
                        {item.badge && (
                            <span className="font-technical text-[9px] px-1.5 py-0.5 rounded-full bg-[var(--ink)] text-[var(--paper)]">
                                {item.badge}
                            </span>
                        )}
                    </Link>
                );
            })}
        </nav>

        {/* Secondary Navigation */}
        <div className="relative z-10 px-4 py-4 border-t border-[var(--structure-subtle)] mb-4">
            {secondaryItems.map((item) => {
                const Icon = item.icon;
                return (
                    <Link
                        key={item.href}
                        href={item.href}
                        className="group flex items-center gap-3 px-3 py-2 text-sm text-[var(--ink-secondary)] hover:text-[var(--ink)] hover:bg-[var(--surface-hover)] rounded-lg transition-colors"
                    >
                        <Icon size={18} strokeWidth={1.5} className="text-[var(--ink-muted)] group-hover:text-[var(--ink)]" />
                        <span>{item.name}</span>
                    </Link>
                );
            })}
        </div>

        {/* User Profile - Minimal */}
        <div className="relative z-10 px-4 pb-6">
            <button
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                className="flex items-center gap-3 w-full p-2 rounded-lg hover:bg-[var(--surface-hover)] transition-colors text-left group border border-transparent hover:border-[var(--border-subtle)]"
            >
                {/* Avatar */}
                {user?.id && profile?.avatar_url ? (
                    <div className="w-8 h-8 rounded-md bg-[var(--ink)] overflow-hidden">
                        <img src={profile.avatar_url} alt="Profile" className="w-full h-full object-cover" />
                    </div>
                ) : (
                    <div className="w-8 h-8 rounded-md bg-[var(--ink)] flex items-center justify-center text-[var(--paper)] font-medium text-xs">
                        {initials}
                    </div>
                )}

                <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-[var(--ink)] truncate">
                        {profile?.full_name || displayName}
                    </div>
                    <div className="text-xs text-[var(--ink-muted)] truncate">
                        {user?.email || "Signed In"}
                    </div>
                </div>

                <ChevronDown
                    size={14}
                    strokeWidth={1.5}
                    className={cn(
                        "text-[var(--ink-muted)] transition-transform",
                        isProfileOpen && "rotate-180"
                    )}
                />
            </button>

            {/* Dropdown Menu */}
            {isProfileOpen && (
                <div className="absolute bottom-full left-4 right-4 mb-2 p-1 bg-[var(--paper)] border border-[var(--border)] rounded-lg shadow-[var(--shadow-card)] ring-1 ring-black/5 z-50">
                    <Link
                        href="/settings"
                        className="flex items-center gap-2 px-3 py-2 text-sm text-[var(--ink-secondary)] hover:text-[var(--ink)] hover:bg-[var(--surface-hover)] rounded-md transition-colors"
                    >
                        <Settings size={14} strokeWidth={1.5} />
                        <span>Settings</span>
                    </Link>
                    <button
                        onClick={logout}
                        className="flex items-center gap-2 w-full px-3 py-2 text-sm text-[var(--error)] hover:bg-[var(--error-bg)] rounded-md transition-colors"
                    >
                        <LogOut size={14} strokeWidth={1.5} />
                        <span>Sign Out</span>
                    </button>
                </div>
            )}
        </div>
    </aside>
);
}
