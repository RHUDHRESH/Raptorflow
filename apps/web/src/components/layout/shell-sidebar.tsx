"use client";

import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Bell,
  BellRing,
  BriefcaseBusiness,
  Building2,
  CreditCard,
  LayoutDashboard,
  type LucideIcon,
  MessageSquareMore,
  Radar,
  UploadCloud,
  Settings,
  Sparkles,
  UsersRound
} from "lucide-react";
import { cn } from "@/lib/cn";

const navigation = [
  { href: "/app", label: "Dashboard", icon: LayoutDashboard },
  { href: "/foundation", label: "Foundation", icon: Building2 },
  { href: "/campaigns", label: "Campaigns", icon: BriefcaseBusiness },
  { href: "/intel", label: "Intel", icon: Radar },
  { href: "/nudges", label: "Nudges", icon: BellRing },
  { href: "/uploads", label: "Uploads", icon: UploadCloud },
  { href: "/office", label: "Office", icon: Sparkles },
  { href: "/muse", label: "Muse", icon: MessageSquareMore },
  { href: "/council", label: "Council", icon: UsersRound },
  { href: "/daily-wins", label: "Daily Wins", icon: Bell },
  { href: "/billing", label: "Billing", icon: CreditCard },
  { href: "/settings", label: "Settings", icon: Settings }
] as const satisfies ReadonlyArray<{ href: Route; label: string; icon: LucideIcon }>;

export function ShellSidebar({
  identity
}: {
  identity: { userId: string; orgId: string };
}): React.ReactElement {
  const pathname = usePathname();

  return (
    <aside className="border-r border-[var(--border)] bg-white/65 px-4 py-6 backdrop-blur">
      <div className="mb-8 space-y-2 px-3">
        <p className="text-xs uppercase tracking-[0.26em] text-[var(--muted-foreground)]">
          RaptorFlow
        </p>
        <p className="font-[family-name:var(--font-display)] text-2xl">Office Shell</p>
        <p className="text-xs text-[var(--muted-foreground)]">Org: {identity.orgId}</p>
      </div>
      <nav className="space-y-1">
        {navigation.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-2xl px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
                  : "text-[var(--muted-foreground)] hover:bg-white"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
