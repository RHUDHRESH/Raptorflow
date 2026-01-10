"use client";

import { ReactNode } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { motion } from "motion/react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

interface SettingsNavItem {
    id: string;
    label: string;
    href: string;
    icon?: ReactNode;
}

const settingsNav: SettingsNavItem[] = [
    { id: "account", label: "Account", href: "/settings" },
    { id: "workspace", label: "Workspace", href: "/settings/workspace" },
    { id: "appearance", label: "Appearance", href: "/settings/appearance" },
    { id: "notifications", label: "Notifications", href: "/settings/notifications" },
    { id: "security", label: "Security", href: "/settings/security" },
    { id: "billing", label: "Billing", href: "/settings/billing" },
];

interface SettingsLayoutProps {
    children: ReactNode;
    title?: string;
    description?: string;
}

export function SettingsLayout({
    children,
    title = "Settings",
    description = "Manage your account and preferences",
}: SettingsLayoutProps) {
    const pathname = usePathname();

    const isActive = (href: string) => {
        if (href === "/settings") {
            return pathname === "/settings";
        }
        return pathname === href;
    };

    return (
        <div className="flex h-full min-h-[calc(100vh-80px)]">
            {/* Settings Sub-Nav */}
            <div className="w-64 shrink-0 border-r border-border bg-card">
                <div className="px-6 py-8">
                    <h2 className="text-xl font-semibold text-foreground">{title}</h2>
                    <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{description}</p>
                </div>

                <nav className="px-3 pb-6">
                    <ul className="flex flex-col gap-1">
                        {settingsNav.map((item) => {
                            const active = isActive(item.href);

                            return (
                                <li key={item.id}>
                                    <Link
                                        href={item.href}
                                        className={cn(
                                            "flex items-center rounded-lg px-3 py-2 text-sm transition-colors",
                                            active
                                                ? "bg-[var(--blueprint)] text-[var(--paper)] font-medium shadow-sm"
                                                : "text-[var(--muted)] hover:bg-[var(--blueprint-light)] hover:text-[var(--blueprint)]"
                                        )}
                                        aria-current={active ? "page" : undefined}
                                    >
                                        {item.label}
                                    </Link>
                                </li>
                            );
                        })}
                    </ul>
                </nav>
            </div>

            {/* Settings Content */}
            <ScrollArea className="flex-1 bg-background">
                <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, ease: "easeOut" }}
                    className="px-10 py-10 max-w-4xl"
                >
                    {children}
                </motion.div>
            </ScrollArea>
        </div>
    );
}
