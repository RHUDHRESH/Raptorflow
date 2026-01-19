"use client";

import React from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import {
    UserIcon,
    Settings03Icon,
    PaintBoardIcon,
    Notification03Icon,
    SecurityCheckIcon,
    CreditCardIcon,
} from "hugeicons-react";
import { cn } from "@/lib/utils";

// ═══════════════════════════════════════════════════════════════
// SettingsNav - Left sidebar navigation
// ═══════════════════════════════════════════════════════════════

interface NavItem {
    id: string;
    label: string;
    href: string;
    icon: any;
}

const NAV_ITEMS: NavItem[] = [
    { id: "profile", label: "Profile", href: "/settings", icon: UserIcon },
    { id: "workspace", label: "Workspace", href: "/settings/workspace", icon: Settings03Icon },
    { id: "appearance", label: "Appearance", href: "/settings/appearance", icon: PaintBoardIcon },
    { id: "notifications", label: "Notifications", href: "/settings/notifications", icon: Notification03Icon },
    { id: "security", label: "Security", href: "/settings/security", icon: SecurityCheckIcon },
    { id: "billing", label: "Billing", href: "/settings/billing", icon: CreditCardIcon },
];

export function SettingsNav() {
    const pathname = usePathname();

    const isActive = (href: string) => {
        if (href === "/settings") {
            return pathname === "/settings";
        }
        return pathname === href;
    };

    return (
        <nav className="w-52 shrink-0">
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-xl font-semibold text-[var(--ink)]">Settings</h1>
                <p className="text-sm text-[var(--muted)] mt-1">
                    Manage your account
                </p>
            </div>

            {/* Nav Items */}
            <ul className="space-y-1">
                {NAV_ITEMS.map((item) => {
                    const active = isActive(item.href);
                    const Icon = item.icon;

                    return (
                        <li key={item.id}>
                            <Link
                                href={item.href}
                                className={cn(
                                    "flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-150",
                                    active
                                        ? "bg-[var(--ink)] text-[var(--canvas)]"
                                        : "text-[var(--muted)] hover:bg-[var(--surface)] hover:text-[var(--ink)]"
                                )}
                            >
                                {React.createElement(Icon as any, {
                                    className: "w-4 h-4",
                                    strokeWidth: 1.5,
                                })}
                                {item.label}
                            </Link>
                        </li>
                    );
                })}
            </ul>
        </nav>
    );
}
